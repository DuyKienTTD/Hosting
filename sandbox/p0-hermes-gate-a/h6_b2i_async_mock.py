"""Offline B2-I contract. No live configuration, runtime imports, or provider client."""

from contextlib import closing, contextmanager
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import re
import sqlite3
from uuid import uuid4


MAX_BODY = 4096
IPC_TIMEOUT = 4
GUARD_CONNECT_TIMEOUT = 5
GUARD_RESPONSE_TIMEOUT = 45
HERMES_SDK_TIMEOUT_FIXTURE = 60
CALLBACK_SOCKET_TIMEOUT = 5
CALLBACK_MAX_AGE = 10
MAX_DELIVERY_ATTEMPTS = 2
IDENTIFIER = re.compile(r"[a-zA-Z0-9_-]{1,80}")
JOB_ID = re.compile(r"[0-9a-f]{32}")
DIGEST = re.compile(r"[0-9a-f]{64}")
TIMESTAMP = re.compile(r"[0-9]{1,12}")
CONTENT_LENGTH = re.compile(r"[0-9]{1,4}")
TERMINAL = {"mock_succeeded", "paid_succeeded", "failed", "outcome_unknown"}
SUBMISSION_FIELDS = {"schema_version", "synthetic", "task_id", "correlation_id",
                     "intent", "duration_seconds", "fault"}
CALLBACK_FIELDS = {"schema_version", "synthetic", "task_id", "correlation_id", "job_id",
                   "request_sha256", "sequence", "outcome"}


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def unique_fields(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON field")
    return result


def decode(raw):
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_fields)
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def matches(pattern, value):
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def envelope(value, fields):
    return (value.keys() == fields and type(value["schema_version"]) is int
            and value["schema_version"] == 1 and value["synthetic"] is True)


def callback_signature(key, timestamp, raw):
    message = b"ttd.h6.b2-i.callback.v1\n" + timestamp.encode("ascii") + b"\n" + raw
    return hmac.new(key, message, sha256).hexdigest()


class MockJobs:
    def __init__(self, scratch, clock, callback_key):
        if len(callback_key) != 32:
            raise ValueError("expected a synthetic 32-byte callback key")
        self.db = scratch / "h6-b2i-synthetic.sqlite3"
        self.clock = clock
        self.callback_key = callback_key
        with closing(sqlite3.connect(self.db)) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY, task_id TEXT UNIQUE NOT NULL,
                    correlation_id TEXT UNIQUE NOT NULL, request_sha256 TEXT NOT NULL,
                    intent TEXT NOT NULL, duration INTEGER NOT NULL, fault TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'accepted', run_started INTEGER, phase_started INTEGER,
                    dispatches INTEGER NOT NULL DEFAULT 0 CHECK (dispatches IN (0,1)),
                    reserve TEXT NOT NULL DEFAULT 'none',
                    settlements INTEGER NOT NULL DEFAULT 0 CHECK (settlements IN (0,1)),
                    outbox BLOB, delivery TEXT NOT NULL DEFAULT 'none',
                    delivery_attempts INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS receipts (
                    job_id TEXT PRIMARY KEY, body_sha256 TEXT NOT NULL
                );
            """)

    @contextmanager
    def transaction(self, write=False):
        with closing(sqlite3.connect(self.db)) as db, db:
            db.row_factory = sqlite3.Row
            db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield db

    def view(self, row):
        fields = ("job_id", "task_id", "correlation_id", "request_sha256", "state", "delivery")
        return {**{field: row[field] for field in fields}, "schema_version": 1, "synthetic": True}

    def admit(self, value):
        if (not envelope(value, SUBMISSION_FIELDS)
                or not all(matches(IDENTIFIER, value[name]) for name in ("task_id", "correlation_id"))
                or value["intent"] not in ("mock", "synthetic_paid")
                or type(value["duration_seconds"]) is not int
                or not 0 <= value["duration_seconds"] <= 120
                or value["fault"] not in ("none", "known_failure", "ipc_timeout", "connect_timeout",
                                          "transport_timeout", "settlement_ack_lost")):
            return 422, {"error": "submission_schema"}
        digest = sha256(encode(value)).hexdigest()
        with self.transaction(write=True) as db:
            row = db.execute("SELECT * FROM jobs WHERE task_id=? OR correlation_id=?",
                             (value["task_id"], value["correlation_id"])).fetchone()
            if row:
                if row["request_sha256"] != digest:
                    return 409, {"error": "idempotency_conflict"}
                return (200 if row["state"] in TERMINAL else 202), self.view(row)
            job_id = uuid4().hex
            db.execute("""INSERT INTO jobs
                (job_id, task_id, correlation_id, request_sha256, intent, duration, fault)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                       (job_id, value["task_id"], value["correlation_id"], digest,
                        value["intent"], value["duration_seconds"], value["fault"]))
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            return 202, self.view(row)

    def status(self, job_id):
        with self.transaction() as db:
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            return (200, self.view(row)) if row else (404, {"error": "not_found"})

    def advance(self, job_id):
        """Run one fake-state transition. The test clock drives the worker independently of HTTP."""
        with self.transaction(write=True) as db:
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if row["state"] in TERMINAL:
                return
            now = self.clock()
            if row["state"] == "accepted":
                db.execute("""UPDATE jobs SET state='reserved', reserve='held', run_started=?, phase_started=?
                              WHERE job_id=?""", (now, now, job_id))
                return
            if row["state"] == "reserved":
                if now - row["run_started"] >= HERMES_SDK_TIMEOUT_FIXTURE:
                    self.finish(db, row, "outcome_unknown")
                    return
                if row["fault"] in ("ipc_timeout", "connect_timeout"):
                    timeout = IPC_TIMEOUT if row["fault"] == "ipc_timeout" else GUARD_CONNECT_TIMEOUT
                    if now - row["phase_started"] >= timeout:
                        self.finish(db, row, "outcome_unknown")
                    return
                db.execute("UPDATE jobs SET state='running', dispatches=1, phase_started=? WHERE job_id=?",
                           (now, job_id))
                return
            remaining_sdk = HERMES_SDK_TIMEOUT_FIXTURE - (row["phase_started"] - row["run_started"])
            response_budget = min(GUARD_RESPONSE_TIMEOUT, remaining_sdk)
            elapsed = now - row["phase_started"]
            if (elapsed >= response_budget
                    and (row["duration"] >= response_budget or row["fault"] == "transport_timeout")):
                self.finish(db, row, "outcome_unknown")
            elif elapsed >= row["duration"] and row["fault"] != "transport_timeout":
                outcome = {"known_failure": "failed", "settlement_ack_lost": "outcome_unknown"}.get(row["fault"])
                if outcome is None:
                    outcome = "mock_succeeded" if row["intent"] == "mock" else "paid_succeeded"
                self.finish(db, row, outcome)

    def abandon(self, job_id):
        """Fixture recovery for an abandoned reservation or dispatch. No redispatch or refund."""
        with self.transaction(write=True) as db:
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if row["state"] in ("reserved", "running"):
                self.finish(db, row, "outcome_unknown")

    def finish(self, db, row, outcome):
        body = {name: row[name] for name in ("job_id", "task_id", "correlation_id", "request_sha256")}
        body.update(schema_version=1, synthetic=True, sequence=1, outcome=outcome)
        reserve = "held" if outcome == "outcome_unknown" else "settled"
        db.execute("""UPDATE jobs SET state=?, reserve=?, settlements=?, outbox=?, delivery='pending'
                      WHERE job_id=?""",
                   (outcome, reserve, int(reserve == "settled"), encode(body), row["job_id"]))

    def callback(self, timestamp, signature, raw):
        if (not matches(TIMESTAMP, timestamp) or not matches(DIGEST, signature)
                or not 0 <= self.clock() - int(timestamp) <= CALLBACK_MAX_AGE
                or not hmac.compare_digest(callback_signature(self.callback_key, timestamp, raw), signature)):
            return 401, {"error": "callback_auth"}
        value = decode(raw)
        if (not envelope(value, CALLBACK_FIELDS) or not matches(JOB_ID, value["job_id"])
                or not matches(DIGEST, value["request_sha256"])
                or not all(matches(IDENTIFIER, value[name]) for name in ("task_id", "correlation_id"))
                or type(value["sequence"]) is not int or value["sequence"] != 1
                or not isinstance(value["outcome"], str) or value["outcome"] not in TERMINAL):
            return 422, {"error": "callback_schema"}
        job_id = value["job_id"]
        with self.transaction(write=True) as db:
            row = db.execute("SELECT outbox FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if row is None or row["outbox"] != raw:
                return 409, {"error": "callback_binding"}
            body_sha256 = sha256(raw).hexdigest()
            receipt = {"job_id": job_id, "body_sha256": body_sha256}
            if db.execute("SELECT 1 FROM receipts WHERE job_id=?", (job_id,)).fetchone():
                return 409, {"receipt": receipt, "error": "callback_replay"}
            db.execute("INSERT INTO receipts VALUES (?, ?)", (job_id, body_sha256))
            return 200, {"receipt": receipt}

    def deliver(self, job_id, send):
        """Attempt only callback delivery. Explicit reconciliation may resend the same event once."""
        with self.transaction(write=True) as db:
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if (row["delivery"] not in ("pending", "dead_letter")
                    or row["delivery_attempts"] >= MAX_DELIVERY_ATTEMPTS):
                return
            db.execute("""UPDATE jobs SET delivery='sending', delivery_attempts=delivery_attempts+1
                          WHERE job_id=?""", (job_id,))
        raw = row["outbox"]
        timestamp = str(self.clock())
        signature = callback_signature(self.callback_key, timestamp, raw)
        delivered = False
        try:
            code, reply = send(raw, timestamp, signature, CALLBACK_SOCKET_TIMEOUT)
            receipt = {"job_id": job_id, "body_sha256": sha256(raw).hexdigest()}
            delivered = ((code == 200 and reply == {"receipt": receipt})
                         or (code == 409 and reply == {"receipt": receipt, "error": "callback_replay"}))
        except OSError:
            pass
        finally:
            with self.transaction(write=True) as db:
                db.execute("UPDATE jobs SET delivery=? WHERE job_id=?",
                           ("delivered" if delivered else "dead_letter", job_id))

    def recover_delivery(self, job_id):
        """Fixture operator calls after proving the previous sender has stopped."""
        with self.transaction(write=True) as db:
            db.execute("UPDATE jobs SET delivery='dead_letter' WHERE job_id=? AND delivery='sending'", (job_id,))


class MockHttpHandler(BaseHTTPRequestHandler):
    def setup(self):
        self.request.settimeout(CALLBACK_SOCKET_TIMEOUT)
        super().setup()

    def log_message(self, *args):
        pass

    def reply(self, code, value):
        raw = encode(value)
        self.send_response(code)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        if code == 202:
            self.send_header("Location", "/jobs/" + value["job_id"])
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def route(self, method):
        try:
            self.reply(*self.handle_request(method))
        except OSError:
            # The durable job or callback receipt can outlive a disconnected client.
            pass

    def handle_request(self, method):
        callback = method == "POST" and self.path == "/callback"
        if not callback:
            auth = self.headers.get_all("Authorization", [])
            if len(auth) != 1 or not hmac.compare_digest(auth[0].encode(), self.server.bearer):
                return 401, {"error": "job_auth"}
        if method == "GET" and self.path.startswith("/jobs/") and matches(JOB_ID, self.path[6:]):
            return self.server.jobs.status(self.path[6:])
        if method != "POST" or self.path not in ("/jobs", "/callback"):
            return 404, {"error": "not_found"}
        try:
            lengths = self.headers.get_all("Content-Length", [])
            if (len(lengths) != 1 or not matches(CONTENT_LENGTH, lengths[0])
                    or not 0 < int(lengths[0]) <= MAX_BODY or "Transfer-Encoding" in self.headers):
                raise ValueError("invalid framing")
            raw = self.rfile.read(int(lengths[0]))
            if len(raw) != int(lengths[0]):
                raise ValueError("incomplete body")
            if callback:
                timestamps = self.headers.get_all("X-Callback-Timestamp", [])
                signatures = self.headers.get_all("X-Callback-Signature", [])
                if len(timestamps) != 1 or len(signatures) != 1:
                    return 401, {"error": "callback_auth"}
                return self.server.jobs.callback(timestamps[0], signatures[0], raw)
            return self.server.jobs.admit(decode(raw))
        except ValueError:
            return 400, {"error": "invalid_request"}


def loopback_fixture(jobs, access_token, handler=MockHttpHandler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.jobs = jobs
    server.bearer = b"Bearer " + access_token
    return server
