"""Executable ENG-01A-S1 contract and in-process, synthetic-only adapter."""

from contextlib import closing, contextmanager
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import stat
import tempfile


LIVE_ENABLED = False
PREFIX = "eng01a-s1-"
MARKER = b"ENG-01A-S1 synthetic fixture v1\n"
OUTCOMES = {"completed", "failed", "outcome_unknown"}
REQUEST_FIELDS = {"schema_version", "synthetic", "idempotency_key", "channel", "source",
                  "approval", "budget", "deadline_ms", "payload"}
CALLBACK_FIELDS = {"schema_version", "synthetic", "job_id", "request_sha256", "channel",
                   "source", "outcome", "sequence", "occurred_ms", "callback_id"}
MODES = {"success", "failure", "timeout"}


class InvalidContract(ValueError):
    http_status = 422


class Conflict(RuntimeError):
    http_status = 409


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def sha(value):
    return hashlib.sha256(wire(value)).hexdigest()


def valid_time(value):
    return type(value) is int and 0 <= value < 2 ** 53


def validate_request(request, now_ms):
    if type(request) is not dict or request.keys() != REQUEST_FIELDS or not valid_time(now_ms):
        raise InvalidContract("invalid request shape or clock")
    budget = request["budget"]
    key = request["idempotency_key"]
    if (type(request["schema_version"]) is not int or request["schema_version"] != 1
            or request["synthetic"] is not True or request["approval"] != "synthetic_approved"
            or request["channel"] != "fixture" or request["source"] != "synthetic"
            or type(key) is not str or not re.fullmatch(r"fake-[a-z0-9-]{1,48}", key)
            or not valid_time(request["deadline_ms"])
            or type(budget) is not dict or budget.keys() != {"max_dispatches", "max_units"}
            or type(budget["max_dispatches"]) is not int or budget["max_dispatches"] != 1
            or type(budget["max_units"]) is not int or not 1 <= budget["max_units"] <= 10
            or type(request["payload"]) is not dict or request["payload"].keys() != {"mode"}
            or not isinstance(request["payload"]["mode"], str) or request["payload"]["mode"] not in MODES):
        raise InvalidContract("request is outside the synthetic contract")


def check_file(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise InvalidContract("fixture files must be unlinked from other paths")


@contextmanager
def temporary_sandbox():
    with tempfile.TemporaryDirectory(prefix=PREFIX) as directory:
        root = Path(directory).resolve()
        (root / "fixture.marker").write_bytes(MARKER)
        with closing(sqlite3.connect(root / "worker-lock.sqlite")):
            pass
        with closing(sqlite3.connect(root / "state.sqlite")) as db:
            db.executescript("""
                CREATE TABLE jobs (
                    job_id TEXT PRIMARY KEY, idempotency_key TEXT NOT NULL UNIQUE,
                    request BLOB NOT NULL, request_sha256 TEXT NOT NULL,
                    admitted_ms INTEGER NOT NULL, state TEXT NOT NULL,
                    outcome TEXT, event BLOB
                );
                CREATE TABLE dispatches (
                    job_id TEXT PRIMARY KEY REFERENCES jobs(job_id), units INTEGER NOT NULL
                );
                CREATE TABLE receipts (
                    job_id TEXT PRIMARY KEY REFERENCES jobs(job_id), receipt BLOB NOT NULL
                );
                CREATE TABLE audit (
                    sequence INTEGER PRIMARY KEY, job_id TEXT NOT NULL REFERENCES jobs(job_id),
                    event TEXT NOT NULL, observed_ms INTEGER NOT NULL, UNIQUE(job_id, event)
                );
            """)
        yield OfflineAdapter(root)


class OfflineAdapter:
    def __init__(self, root, *, endpoint=None, credentials=None):
        if LIVE_ENABLED is not False or endpoint is not None or credentials is not None:
            raise InvalidContract("network endpoints and credentials are disabled")
        root = Path(root)
        if (root.is_symlink() or root.resolve().parent != Path(tempfile.gettempdir()).resolve()
                or not root.name.startswith(PREFIX)):
            raise InvalidContract("a dedicated temporary sandbox is required")
        marker = root / "fixture.marker"
        check_file(marker)
        if marker.read_bytes() != MARKER:
            raise InvalidContract("unknown sandbox ownership")
        self.root = root.resolve()
        self.state = self.root / "state.sqlite"
        self.worker_lock = self.root / "worker-lock.sqlite"
        check_file(self.state)
        check_file(self.worker_lock)

    @contextmanager
    def tx(self):
        with closing(sqlite3.connect(self.state)) as db, db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys = ON")
            db.execute("PRAGMA synchronous = FULL")
            db.execute("BEGIN IMMEDIATE")
            yield db

    @contextmanager
    def worker(self):
        # A separate SQLite lock serializes workers while leaving state transactions
        # independently committable. The OS releases it on abrupt process exit.
        with closing(sqlite3.connect(self.worker_lock, timeout=0)) as db:
            try:
                db.execute("BEGIN IMMEDIATE")
            except sqlite3.OperationalError as exc:
                if exc.sqlite_errorcode == sqlite3.SQLITE_BUSY:
                    raise Conflict("another worker still owns the sandbox") from exc
                raise
            yield

    @staticmethod
    def _job(db, job_id):
        row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            raise InvalidContract("unknown job")
        return row

    @staticmethod
    def _audit(db, job_id, event, now_ms):
        latest = db.execute("SELECT max(observed_ms) FROM audit WHERE job_id=?", (job_id,)).fetchone()[0]
        if not valid_time(now_ms) or (latest is not None and now_ms < latest):
            raise InvalidContract("invalid or reversed fixture clock")
        db.execute("INSERT INTO audit(job_id,event,observed_ms) VALUES(?,?,?)", (job_id, event, now_ms))

    def admit(self, request, now_ms):
        validate_request(request, now_ms)
        request_sha = sha(request)
        key = request["idempotency_key"]
        job_id = "job-" + request_sha
        with self.tx() as db:
            row = db.execute("SELECT job_id, request_sha256 FROM jobs WHERE idempotency_key=?", (key,)).fetchone()
            if row:
                if row["request_sha256"] != request_sha:
                    raise Conflict("idempotency key already bound to a different request")
                return {"http": 200, "job_id": row["job_id"], "request_sha256": request_sha, "replayed": True}
            if not 0 < request["deadline_ms"] - now_ms <= 60_000:
                raise InvalidContract("deadline outside the admission window")
            db.execute("""INSERT INTO jobs(job_id,idempotency_key,request,request_sha256,admitted_ms,state)
                VALUES(?,?,?,?,?,'pending')""", (job_id, key, wire(request), request_sha, now_ms))
            self._audit(db, job_id, "admitted", now_ms)
        return {"http": 202, "job_id": job_id, "request_sha256": request_sha, "replayed": False}

    def snapshot(self, job_id):
        with self.tx() as db:
            row = self._job(db, job_id)
            request = json.loads(row["request"])
            receipt = db.execute("SELECT receipt FROM receipts WHERE job_id=?", (job_id,)).fetchone()
            dispatch = db.execute("SELECT units FROM dispatches WHERE job_id=?", (job_id,)).fetchone()
            audit = db.execute("SELECT sequence,event,observed_ms FROM audit WHERE job_id=? ORDER BY sequence",
                               (job_id,)).fetchall()
        return {**{key: row[key] for key in ("job_id", "request_sha256", "state", "outcome", "admitted_ms")},
                **{key: request[key] for key in ("idempotency_key", "channel", "source", "approval", "budget",
                                                 "deadline_ms")},
                "fake_dispatches": int(dispatch is not None), "fake_units": dispatch["units"] if dispatch else 0,
                "callback": json.loads(row["event"]) if row["event"] else None,
                "receipt": json.loads(receipt["receipt"]) if receipt else None,
                "audit": [dict(entry) for entry in audit]}

    def _begin(self, job_id, now_ms):
        with self.tx() as db:
            row = self._job(db, job_id)
            prior = row["state"]
            request = json.loads(row["request"])
            if prior == "pending":
                db.execute("UPDATE jobs SET state='working' WHERE job_id=?", (job_id,))
                self._audit(db, job_id, "working", now_ms)
            return prior, request, row["request_sha256"]

    def _dispatch(self, job_id, now_ms):
        with self.tx() as db:
            row = self._job(db, job_id)
            request = json.loads(row["request"])
            if row["state"] != "working" or now_ms >= request["deadline_ms"] or request["budget"]["max_units"] < 1:
                raise Conflict("fake dispatch is not admitted")
            db.execute("INSERT INTO dispatches VALUES(?,1)", (job_id,))
            self._audit(db, job_id, "fake_dispatch", now_ms)

    def settle(self, job_id, request_sha256, outcome, now_ms):
        if type(outcome) is not str or outcome not in OUTCOMES or not valid_time(now_ms):
            raise InvalidContract("invalid fake result")
        with self.tx() as db:
            row = self._job(db, job_id)
            if row["state"] != "working" or row["request_sha256"] != request_sha256:
                raise Conflict("result does not match an unsettled job")
            request = json.loads(row["request"])
            if now_ms >= request["deadline_ms"]:
                outcome = "outcome_unknown"
            if outcome != "outcome_unknown" and not db.execute(
                    "SELECT 1 FROM dispatches WHERE job_id=?", (job_id,)).fetchone():
                raise Conflict("known outcome has no fake dispatch")
            binding = {"schema_version": 1, "synthetic": True, "job_id": job_id, "request_sha256": request_sha256,
                       "channel": request["channel"], "source": request["source"], "outcome": outcome,
                       "sequence": 1, "occurred_ms": now_ms}
            event = binding | {"callback_id": "callback-" + sha(binding)}
            db.execute("UPDATE jobs SET state='sending', outcome=?, event=? WHERE job_id=?",
                       (outcome, wire(event), job_id))
            self._audit(db, job_id, "sending", now_ms)

    def receive_callback(self, event, now_ms):
        if (type(event) is not dict or event.keys() != CALLBACK_FIELDS or not isinstance(event.get("job_id"), str)
                or not isinstance(event.get("callback_id"), str) or not valid_time(now_ms)):
            raise InvalidContract("callback identity is required")
        try:
            offered = wire(event)
        except (TypeError, ValueError) as exc:
            raise InvalidContract("callback must be canonical JSON") from exc
        job_id = event["job_id"]
        with self.tx() as db:
            row = self._job(db, job_id)
            if row["event"] is None or offered != row["event"]:
                raise Conflict("callback does not match the durable outbox event")
            persisted = db.execute("SELECT receipt FROM receipts WHERE job_id=?", (job_id,)).fetchone()
            if persisted:
                return json.loads(persisted["receipt"])
            identity = {"job_id": job_id, "callback_id": event["callback_id"], "request_sha256": row["request_sha256"],
                        "event_sha256": sha(event), "outcome": row["outcome"], "committed_ms": now_ms}
            receipt = identity | {"receipt_id": "receipt-" + sha(identity)}
            db.execute("INSERT INTO receipts VALUES(?,?)", (job_id, wire(receipt)))
            self._audit(db, job_id, "receipt_committed", now_ms)
            return receipt

    def _ack(self, job_id, receipt, now_ms):
        with self.tx() as db:
            row = self._job(db, job_id)
            committed = db.execute("SELECT receipt FROM receipts WHERE job_id=?", (job_id,)).fetchone()
            if row["state"] != "sending" or committed is None or committed["receipt"] != wire(receipt):
                raise Conflict("receipt ACK does not match the committed receipt")
            db.execute("UPDATE jobs SET state=outcome WHERE job_id=?", (job_id,))
            self._audit(db, job_id, "receipt_ack", now_ms)

    def process(self, job_id, now_ms, checkpoint=lambda _: None):
        with self.worker():
            prior, request, request_sha = self._begin(job_id, now_ms)
            if prior in OUTCOMES:
                return self.snapshot(job_id)
            if prior == "working":
                self.settle(job_id, request_sha, "outcome_unknown", now_ms)
            elif prior == "pending":
                checkpoint("working_before_dispatch")
                deadline = request["deadline_ms"]
                outcome = "outcome_unknown"
                if now_ms < deadline:
                    self._dispatch(job_id, now_ms)
                    checkpoint("working_after_dispatch")
                    mode = request["payload"]["mode"]
                    if mode == "timeout":
                        now_ms = deadline
                    else:
                        outcome = "completed" if mode == "success" else "failed"
                self.settle(job_id, request_sha, outcome, now_ms)
            event = self.snapshot(job_id)["callback"]
            checkpoint("sending_before_receipt")
            receipt = self.receive_callback(event, now_ms)
            checkpoint("sending_after_receipt")
            self._ack(job_id, receipt, now_ms)
            return self.snapshot(job_id)
