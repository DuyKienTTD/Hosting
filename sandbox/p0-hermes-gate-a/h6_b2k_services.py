"""B2-K synthetic-only loopback services. Each process opens one private database."""

from contextlib import closing, contextmanager
from hashlib import sha256
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import sqlite3
import time
from uuid import uuid4

from h6_b2i_async_mock import (
    CALLBACK_MAX_AGE, DIGEST, IDENTIFIER, JOB_ID, MAX_BODY, TERMINAL, decode, encode, matches,
)

IDENTITY = {"job_id", "task_id", "correlation_id", "request_sha256"}
BINDING = IDENTITY | {"run_id", "schema_version", "synthetic"}
SCHEMA = {
    "adapter": """CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY, task_id TEXT UNIQUE, correlation_id TEXT UNIQUE,
        request_sha256 TEXT, run_id TEXT UNIQUE, event BLOB,
        delivery TEXT DEFAULT 'none', attempts INTEGER DEFAULT 0)""",
    "hermes": """CREATE TABLE IF NOT EXISTS runs (
        job_id TEXT PRIMARY KEY, binding BLOB, run_id TEXT UNIQUE, state TEXT DEFAULT 'prepared',
        dispatches INTEGER DEFAULT 0, settlements INTEGER DEFAULT 0, reserve TEXT DEFAULT 'none')""",
    "receiver": """CREATE TABLE IF NOT EXISTS inbox (
        job_id TEXT PRIMARY KEY, binding BLOB, run_id TEXT UNIQUE, receipt BLOB)""",
}


def signature(key, role, timestamp, raw):
    prefix = b"ttd.h6.b2-k." + role + b".v1\n" + str(timestamp).encode() + b"\n"
    return hmac.digest(key, prefix + raw, "sha256").hex()


def valid_binding(value, fields):
    return (set(value) == fields and type(value["schema_version"]) is int
            and value["schema_version"] == 1 and value["synthetic"] is True
            and matches(JOB_ID, value["job_id"]) and matches(DIGEST, value["request_sha256"])
            and all(matches(IDENTIFIER, value[name]) for name in ("task_id", "correlation_id"))
            and ("run_id" not in fields or matches(JOB_ID, value["run_id"])))


def rpc(port, path, token=None, payload=None, headers=None, timeout=1):
    request_headers = dict(headers or {})
    if token is not None:
        request_headers["Authorization"] = "Bearer " + token
    with closing(HTTPConnection("127.0.0.1", port, timeout=timeout)) as client:
        client.request("GET" if payload is None else "POST", path,
                       None if payload is None else encode(payload), request_headers)
        with client.getresponse() as response:
            raw = response.read(MAX_BODY + 1)
            if len(raw) > MAX_BODY:
                raise ValueError("fixture response too large")
            return response.status, decode(raw)


class Service:
    def __init__(self, role, db_path, tokens, callback_key, receipt_key, clock, ports):
        self.role, self.db_path, self.tokens = role, db_path, tokens
        self.callback_key, self.receipt_key, self.clock, self.ports = callback_key, receipt_key, clock, ports
        with self.tx() as db:
            db.execute(SCHEMA[role])
            if role == "adapter":
                # The fixture supervisor starts a replacement only after joining the old process.
                db.execute("UPDATE jobs SET delivery='dead_letter' WHERE delivery='sending'")

    @contextmanager
    def tx(self, write=True):
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.row_factory = sqlite3.Row
            db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield db

    def call(self, role, path, body=None, headers=None):
        return rpc(self.ports[role], path, self.tokens[role], body, headers)

    def signed_callback(self, job, body, fault):
        at = self.clock.value
        code, response = rpc(self.ports["receiver"], "/callback", payload=body, headers={
            "X-Callback-Time": str(at), "X-Callback-Proof": signature(self.callback_key, b"event", at, encode(body)),
            **({"X-Fixture-" + fault: "1"} if fault else {}),
        })
        expected = {"job_id": job, "run_id": body["run_id"], "event_sha256": sha256(encode(body)).hexdigest()}
        return (code in (200, 409) and response.keys() == {"receipt", "proof"}
                and response["receipt"] == expected and isinstance(response["proof"], str)
                and hmac.compare_digest(signature(self.receipt_key, b"receipt", at, encode(expected)), response["proof"]))

    def adapter(self, path, body):
        if path == "/jobs" and body is not None:
            fields = {"schema_version", "synthetic", "task_id", "correlation_id", "input"}
            if (body.keys() != fields or not isinstance(body["input"], str)
                    or not 0 < len(body["input"]) <= 128):
                return 422, {}
            job = {k: v for k, v in body.items() if k != "input"}
            job.update(job_id=uuid4().hex, request_sha256=sha256(encode(body)).hexdigest())
            if not valid_binding(job, BINDING - {"run_id"}):
                return 422, {}
            with self.tx() as db:
                row = db.execute("SELECT * FROM jobs WHERE task_id=? OR correlation_id=?",
                                 (job["task_id"], job["correlation_id"])).fetchone()
                if row:
                    if row["request_sha256"] != job["request_sha256"]:
                        return 409, {}
                    job["job_id"] = row["job_id"]
                else:
                    db.execute("INSERT INTO jobs(job_id,task_id,correlation_id,request_sha256) VALUES(?,?,?,?)",
                               tuple(job[k] for k in ("job_id", "task_id", "correlation_id", "request_sha256")))
                return (200 if row and row["event"] else 202), job
        parts = path.split("/")
        if len(parts) not in (3, 4) or parts[1] != "jobs" or not matches(JOB_ID, parts[2]):
            return 404, {}
        job_id = parts[2]
        with self.tx(write=False) as db:
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if not row:
            return 404, {}
        binding = {**{key: row[key] for key in IDENTITY}, "schema_version": 1, "synthetic": True}
        if len(parts) == 3 and body is None:
            return 200, {**binding, "run_id": row["run_id"], "delivery": row["delivery"],
                         "outcome": decode(row["event"])["outcome"] if row["event"] else None}
        if len(parts) != 4 or body is None or set(body) - {"drop_ack", "corrupt_receipt"}:
            return 404, {}
        action = parts[3]
        if action == "sync":
            code, run = self.call("hermes", "/runs", binding,
                                  {"X-Fixture-Drop-Ack": "1"} if body.get("drop_ack") else None)
            run_id = run.get("run_id")
            if code not in (200, 202) or not matches(JOB_ID, run_id):
                return 502, {}
            with self.tx() as db:
                db.execute("UPDATE jobs SET run_id=? WHERE job_id=? AND (run_id IS NULL OR run_id=?)",
                           (run_id, job_id, run_id))
                if db.execute("SELECT run_id FROM jobs WHERE job_id=?", (job_id,)).fetchone()[0] != run_id:
                    return 409, {}
            return self.call("receiver", "/bindings", {**binding, "run_id": run_id})
        if not row["run_id"]:
            return 409, {}
        binding["run_id"] = row["run_id"]
        if action == "collect":
            code, event = self.call("hermes", "/runs/" + row["run_id"])
            if code != 200 or not valid_binding(event, BINDING | {"outcome", "sequence"}):
                return 409, {}
            if (any(binding[key] != event[key] for key in BINDING)
                    or not isinstance(event["outcome"], str) or event["outcome"] not in TERMINAL
                    or type(event["sequence"]) is not int or event["sequence"] != 1):
                return 409, {}
            wire = encode(event)
            with self.tx() as db:
                previous = db.execute("SELECT event FROM jobs WHERE job_id=?", (job_id,)).fetchone()[0]
                if previous is None:
                    db.execute("UPDATE jobs SET event=?,delivery='pending' WHERE job_id=?", (wire, job_id))
                elif previous != wire:
                    return 409, {}
            return 200, event
        if action == "deliver":
            # No worker retry. Keep the delivery claim durable before I/O and recover explicitly.
            with self.tx() as db:
                claimed = db.execute("""UPDATE jobs SET delivery='sending',attempts=attempts+1
                    WHERE job_id=? AND delivery IN ('pending','dead_letter') AND attempts<2""", (job_id,)).rowcount
                if not claimed:
                    return 409, {}
                event = decode(db.execute("SELECT event FROM jobs WHERE job_id=?", (job_id,)).fetchone()[0])
            try:
                fault = "Drop-Ack" if body.get("drop_ack") else "Corrupt-Receipt" if body.get("corrupt_receipt") else None
                delivered = self.signed_callback(job_id, event, fault)
            except (OSError, ValueError):
                delivered = False
            with self.tx() as db:
                db.execute("UPDATE jobs SET delivery=? WHERE job_id=?",
                           ("delivered" if delivered else "dead_letter", job_id))
            return (200 if delivered else 502), {}
        return 404, {}

    def hermes(self, path, body):
        if path == "/runs" and body is not None and valid_binding(body, BINDING - {"run_id"}):
            with self.tx() as db:
                row = db.execute("SELECT * FROM runs WHERE job_id=?", (body["job_id"],)).fetchone()
                wire = encode(body)
                if row:
                    return (200, {"run_id": row["run_id"]}) if row["binding"] == wire else (409, {})
                run_id = uuid4().hex
                db.execute("INSERT INTO runs(job_id,binding,run_id) VALUES(?,?,?)", (body["job_id"], wire, run_id))
                return 202, {"run_id": run_id}
        parts = path.split("/")
        if len(parts) not in (3, 4) or parts[1] != "runs" or not matches(JOB_ID, parts[2]):
            return 404, {}
        with self.tx(write=body is not None) as db:
            row = db.execute("SELECT * FROM runs WHERE run_id=?", (parts[2],)).fetchone()
            if not row:
                return 404, {}
            if len(parts) == 3 and body is None:
                if row["state"] not in TERMINAL:
                    return 202, {"state": row["state"]}
                return 200, {**decode(row["binding"]), "run_id": row["run_id"], "sequence": 1, "outcome": row["state"]}
            if len(parts) != 4 or body is None:
                return 404, {}
            if parts[3] == "start" and body == {} and row["state"] == "prepared":
                db.execute("UPDATE runs SET state='running',reserve='held',dispatches=1 WHERE run_id=?", (parts[2],))
                return 202, {}
            if (parts[3] == "finish" and body.keys() == {"outcome"} and isinstance(body["outcome"], str)
                    and body["outcome"] in TERMINAL and row["state"] == "running"):
                known = body["outcome"] != "outcome_unknown"
                db.execute("UPDATE runs SET state=?,settlements=?,reserve=? WHERE run_id=?",
                           (body["outcome"], int(known), "settled" if known else "held", parts[2]))
                return 200, {}
            return 409, {}

    def receiver(self, path, body, headers):
        if path == "/bindings" and body is not None and valid_binding(body, BINDING):
            wire = encode(body)
            with self.tx() as db:
                row = db.execute("SELECT binding FROM inbox WHERE job_id=? OR run_id=?",
                                 (body["job_id"], body["run_id"])).fetchone()
                if row:
                    return (200 if row["binding"] == wire else 409), {}
                db.execute("INSERT INTO inbox(job_id,binding,run_id) VALUES(?,?,?)",
                           (body["job_id"], wire, body["run_id"]))
                return 201, {}
        if path != "/callback" or body is None:
            return 404, {}
        at, proof = headers.get("X-Callback-Time", ""), headers.get("X-Callback-Proof", "")
        if (not at.isascii() or not at.isdigit() or len(at) > 12
                or not 0 <= self.clock.value - int(at) <= CALLBACK_MAX_AGE or not matches(DIGEST, proof)
                or not hmac.compare_digest(signature(self.callback_key, b"event", at, encode(body)), proof)):
            return 401, {}
        if (not valid_binding(body, BINDING | {"outcome", "sequence"}) or type(body["sequence"]) is not int
                or body["sequence"] != 1 or not isinstance(body["outcome"], str) or body["outcome"] not in TERMINAL):
            return 422, {}
        with self.tx() as db:
            row = db.execute("SELECT * FROM inbox WHERE job_id=?", (body["job_id"],)).fetchone()
            if not row or decode(row["binding"]) != {key: body[key] for key in BINDING}:
                return 409, {}
            receipt = {"job_id": body["job_id"], "run_id": body["run_id"], "event_sha256": sha256(encode(body)).hexdigest()}
            wire = encode(receipt)
            if row["receipt"] and row["receipt"] != wire:
                return 409, {}
            if row["receipt"] is None:
                db.execute("UPDATE inbox SET receipt=? WHERE job_id=?", (wire, body["job_id"]))
            return (409 if row["receipt"] else 200), {
                "receipt": receipt, "proof": signature(self.receipt_key, b"receipt", at, wire),
            }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.handle_rpc(False)

    def do_POST(self):
        self.handle_rpc(True)

    def handle_rpc(self, post):
        self.connection.settimeout(2)
        service = self.server.service
        try:
            if not (service.role == "receiver" and self.path == "/callback") and not hmac.compare_digest(
                self.headers.get("Authorization", "").encode(), ("Bearer " + service.tokens[service.role]).encode()
            ):
                code, result = 401, {}
            else:
                body = None
                if post:
                    lengths = self.headers.get_all("Content-Length", [])
                    size = int(lengths[0]) if len(lengths) == 1 else 0
                    if not 0 < size <= MAX_BODY or "Transfer-Encoding" in self.headers:
                        raise ValueError("invalid body size")
                    raw = self.rfile.read(size)
                    body = decode(raw)
                    if len(raw) != size or encode(body) != raw:
                        raise ValueError("non-canonical fixture request")
                if service.role == "receiver":
                    code, result = service.receiver(self.path, body, self.headers)
                else:
                    code, result = getattr(service, service.role)(self.path, body)
            if code in (200, 202) and self.headers.get("X-Fixture-Drop-Ack") == "1":
                return
            if service.role == "receiver" and "proof" in result and self.headers.get("X-Fixture-Corrupt-Receipt") == "1":
                result["proof"] = "0" * 64
            if code == 202 and self.path == "/jobs" and self.headers.get("X-Fixture-Hold-Ack") == "1":
                time.sleep(0.25)
        except (OSError, ValueError, sqlite3.IntegrityError):
            code, result = 502, {}
        raw = encode(result)
        try:
            self.send_response(code)
            self.send_header("Content-Length", str(len(raw)))
            if code == 202 and self.path == "/jobs":
                self.send_header("Location", "/jobs/" + result["job_id"])
            self.end_headers()
            self.wfile.write(raw)
        except OSError:
            pass


def run_service(role, db_path, tokens, callback_key, receipt_key, clock, ports, ready, port=0):
    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as server:
        server.service = Service(role, db_path, tokens, callback_key, receipt_key, clock, ports)
        ready.send(server.server_port)
        ready.close()
        server.serve_forever()
