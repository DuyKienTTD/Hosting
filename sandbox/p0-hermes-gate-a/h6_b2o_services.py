"""B2-O synthetic adapter, receipt, writer and instrumentation for a local H6 route."""

from contextlib import closing, contextmanager
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from http.client import HTTPConnection, RemoteDisconnected
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
from io import BytesIO
import json
import os
from pathlib import Path
import socket
import sqlite3
import sys
import threading
import time
from uuid import uuid4

import bridge
import h6_provider
from h6_b2i_async_mock import CALLBACK_MAX_AGE, CALLBACK_SOCKET_TIMEOUT, HERMES_SDK_TIMEOUT_FIXTURE
from h6_b2k_services import signature
import h6_p0
import provider_mock


ROLE = sys.argv[1]
DB = Path("/fixture-data/state.sqlite")
PATH = "/webhook/b2o-integrated-fixture"
DELAYS = {"b2o-31": 31, "b2o-46": 46}
PORTS = {"bridge": 8080, "guard": 8081, "provider": 8082, "receipt": 8083, "writer": 8084,
         "n8n": 5678, "hermes": 8642}


def secret(name):
    return os.environ["B2O_" + name]


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(wire):
    return sha256(wire).hexdigest()


def emit(event, task=None, **fields):
    print("B2O_EVENT " + raw({"role": ROLE, "event": event, "task": task, "pid": os.getpid(),
                             "wall_utc": datetime.now(timezone.utc).isoformat(),
                             "mono_ns": time.monotonic_ns(), **fields}).decode(), flush=True)


@contextmanager
def tx(write=False):
    with closing(sqlite3.connect(DB, timeout=3)) as db, db:
        db.row_factory = sqlite3.Row
        db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
        yield db


def initialize(sql):
    with tx(write=True) as db:
        db.execute(sql)


def rpc(role, path, token=None, value=None, timeout=5):
    headers = {"Authorization": "Bearer " + token} if token else {}
    if value is not None:
        headers["Content-Type"] = "application/json"
    with closing(HTTPConnection(role, PORTS[role], timeout=timeout)) as conn:
        conn.request("GET" if value is None else "POST", path, None if value is None else raw(value), headers)
        with conn.getresponse() as response:
            payload = response.read(16385)
            if len(payload) > 16384:
                raise ValueError("fixture response too large")
            return response.status, json.loads(payload)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, status, value):
        data = raw(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def authorized(self, name):
        return hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + secret(name))

    def do_GET(self):  # noqa: N802
        if ROLE != "bridge" or not self.authorized("ADMIT"):
            return self.reply(404, {})
        if self.path == "/ready":
            try:
                code, _ = rpc("hermes", "/health")
            except OSError:
                code = 503
            return self.reply(code, {})
        if not self.path.startswith("/jobs/"):
            return self.reply(404, {})
        with tx() as db:
            row = db.execute("SELECT job,state,binding,outcome,receipt FROM jobs WHERE job=?",
                             (self.path.removeprefix("/jobs/"),)).fetchone()
        if row is None:
            return self.reply(404, {})
        self.reply(200, dict(row) | {"binding": json.loads(row["binding"]) if row["binding"] else None})

    def do_POST(self):  # noqa: N802
        auth = {"bridge": "ADMIT", "receipt": "BIND" if self.path == "/bind" else "RECEIVE",
                "writer": "WRITER"}[ROLE]
        if not self.authorized(auth):
            return self.reply(401, {})
        try:
            length = int(self.headers["Content-Length"])
            if not 1 <= length <= 4096:
                return self.reply(413, {})
            value = json.loads(self.rfile.read(length))
            if not isinstance(value, dict):
                return self.reply(422, {})
            status, body = {"bridge": admit_job, "receipt": receipt, "writer": writer}[ROLE](self.path, value)
        except (KeyError, OSError, ValueError, sqlite3.Error) as exc:
            emit("request_error", error=type(exc).__name__)
            status, body = 422, {}
        self.reply(status, body)


def admit_job(path, value):
    task = value["task_id"]
    if path != "/jobs" or task not in DELAYS or value != {
        "task_id": task, "correlation_id": "corr-" + task,
        "input": {"channel": "ads", "spend": 1.25, "clicks": 3}, "simulate": None,
    }:
        return 422, {}
    payload = raw(value)
    request_sha = digest(payload)
    with tx(write=True) as db:
        row = db.execute("SELECT job,request,state FROM jobs WHERE task=?", (task,)).fetchone()
        if row:
            if row["request"] != payload:
                return 409, {}
            return (200 if row["state"] == "delivered" else 202), {"job_id": row["job"], "request_sha256": request_sha}
        job = uuid4().hex
        db.execute("INSERT INTO jobs(job,task,request,state) VALUES(?,?,?,'queued')", (job, task, payload))
    emit("admission_committed", task, http=202, job=job, request_sha256=request_sha)
    return 202, {"job_id": job, "request_sha256": request_sha}


def complete_job(row):
    task, job = row["task"], row["job"]
    request = json.loads(row["request"])
    # The GATE A bridge's scope marker and key are preserved in this async admission.
    prompt = ("Use only fictional advertising data. Return only JSON with keys summary, signals, "
              "recommendations. No tools, memory, or further calls. "
              f"task_id={task}; correlation_id={request['correlation_id']}; channel=ads; spend=1.25; clicks=3.")
    body = {"input": prompt, "model": bridge.MODEL, "provider": "openai-api",
            "model_options": {"reasoning_effort": "none", "service_tier": "default"}}
    headers = {"Authorization": "Bearer " + secret("ENGINE"), "Idempotency-Key": "gate-a-" + task}
    endpoint = "http://hermes:8642/v1/runs"
    emit("hermes_admission_start", task, hermes_request_sha256=digest(raw(body)))
    code, admitted, _ = bridge.request_json(endpoint, method="POST", body=body, headers=headers, timeout=5)
    run = admitted.get("run_id")
    if code != 202 or not isinstance(run, str) or admitted.get("replayed") is True:
        raise RuntimeError("unexpected_fresh_hermes_admission")
    binding = {"job_id": job, "task_id": task, "correlation_id": request["correlation_id"],
               "run_id_sha256": digest(run.encode()), "request_sha256": digest(row["request"])}
    emit("hermes_admission", task, http=code, run_id_sha256=binding["run_id_sha256"])
    with tx(write=True) as db:
        db.execute("UPDATE jobs SET hermes_run=?,binding=? WHERE job=?", (run, raw(binding), job))
    if rpc("receipt", "/bind", secret("BIND"), binding)[0] != 201:
        raise RuntimeError("receipt_binding_failed")
    emit("binding_committed", task, **{key: val for key, val in binding.items() if key != "task_id"})
    deadline = time.monotonic() + HERMES_SDK_TIMEOUT_FIXTURE
    last = None
    outcome = "outcome_unknown"
    while time.monotonic() < deadline:
        code, result, _ = bridge.request_json(endpoint + "/" + run, headers=headers, timeout=5)
        if code != 200:
            raise RuntimeError("hermes_status_unavailable")
        state = result.get("status")
        if state != last:
            emit("hermes_status_observed", task, http=code, app_status=state)
            last = state
        if state == "completed":
            result_payload = json.loads(result["output"])
            if (not isinstance(result_payload, dict)
                    or set(result_payload) != {"summary", "signals", "recommendations"}):
                raise ValueError("unexpected_hermes_output_schema")
            outcome = "mock_succeeded"
            break
        if state in {"failed", "cancelled", "interrupted", "unknown"}:
            break
        time.sleep(0.15)
    else:
        emit("adapter_deadline", task)
    event = binding | {"outcome": outcome, "synthetic": True, "phase": "callback", "sequence": 1}
    with tx(write=True) as db:
        db.execute("UPDATE jobs SET outcome=?, state='sending' WHERE job=?", (outcome, job))
    emit("outcome_committed", task, outcome=outcome)
    stamp = int(time.time())
    proof = signature(secret("EVENT_KEY").encode(), b"event", stamp, raw(event))
    emit("callback_sent", task, event_sha256=digest(raw(event)))
    code, ack = rpc("n8n", PATH, secret("WEBHOOK"), event | {"stamp": stamp, "proof": proof}, CALLBACK_SOCKET_TIMEOUT)
    expected = {"job_id": job, "event_sha256": digest(raw(event)), "run_id_sha256": binding["run_id_sha256"]}
    if (code != 200 or ack.get("receipt") != expected or not hmac.compare_digest(
            ack.get("proof", ""), signature(secret("RECEIPT_KEY").encode(), b"receipt", stamp, raw(expected)))):
        raise RuntimeError("callback_receipt_unconfirmed")
    with tx(write=True) as db:
        db.execute("UPDATE jobs SET receipt=?,state='delivered' WHERE job=?", (digest(raw(expected)), job))
    emit("callback_ack", task, http=code, receipt_sha256=digest(raw(expected)))


def work():
    while True:
        with tx(write=True) as db:
            row = db.execute("SELECT * FROM jobs WHERE state='queued' ORDER BY rowid LIMIT 1").fetchone()
            if row is not None:
                db.execute("UPDATE jobs SET state='working' WHERE job=?", (row["job"],))
        if row is None:
            time.sleep(0.1)
            continue
        try:
            complete_job(row)
        except (OSError, ValueError, RuntimeError, KeyError, sqlite3.Error) as exc:
            with tx(write=True) as db:
                db.execute("UPDATE jobs SET state='dead_letter' WHERE job=?", (row["job"],))
            emit("worker_stopped", row["task"], error=type(exc).__name__)


BINDING = {"job_id", "task_id", "correlation_id", "run_id_sha256", "request_sha256"}


def receipt(path, value):
    job, task = value["job_id"], value["task_id"]
    if path == "/bind" and value.keys() == BINDING and task in DELAYS:
        with tx(write=True) as db:
            db.execute("INSERT INTO inbox(job,binding) VALUES(?,?)", (job, raw(value)))
        return 201, {}
    if path != "/receipt" or value.keys() != BINDING | {"outcome", "synthetic", "phase", "sequence", "stamp", "proof"}:
        return 422, {}
    stamp, proof = value.pop("stamp"), value.pop("proof")
    if (type(stamp) is not int or not 0 <= int(time.time()) - stamp <= CALLBACK_MAX_AGE
            or not isinstance(proof, str) or not hmac.compare_digest(
                proof, signature(secret("EVENT_KEY").encode(), b"event", stamp, raw(value)))):
        return 401, {}
    if (value["synthetic"] is not True or value["phase"] != "callback"
            or type(value["sequence"]) is not int or value["sequence"] != 1
            or value["outcome"] not in ("mock_succeeded", "outcome_unknown")):
        return 422, {}
    binding = {key: value[key] for key in BINDING}
    ack = {"job_id": job, "event_sha256": digest(raw(value)), "run_id_sha256": binding["run_id_sha256"]}
    with tx(write=True) as db:
        row = db.execute("SELECT binding,receipt FROM inbox WHERE job=?", (job,)).fetchone()
        if row is None or row["binding"] != raw(binding) or (row["receipt"] and row["receipt"] != raw(ack)):
            return 409, {}
        db.execute("UPDATE inbox SET receipt=?,outcome=? WHERE job=? AND receipt IS NULL",
                   (raw(ack), value["outcome"], job))
    if row["receipt"] is None:
        emit("receipt_committed", task, outcome=value["outcome"], receipt_sha256=digest(raw(ack)))
    return 200, {"receipt": ack, "proof": signature(secret("RECEIPT_KEY").encode(), b"receipt", stamp, raw(ack))}


def writer(path, value):
    if path != "/ipc":
        return 404, {}
    task, op = value["task_id"], value["op"]
    fingerprint = value["fingerprint"]
    if (task not in DELAYS or value["key_hash"] != digest(("gate-a-" + task).encode())
            or len(fingerprint) != 64 or any(c not in "0123456789abcdef" for c in fingerprint)):
        return 422, {}
    if op == "admit":
        with tx(write=True) as db:
            if db.execute("SELECT 1 FROM reserves WHERE task=?", (task,)).fetchone():
                return 409, {}
            db.execute("INSERT INTO reserves(task,digest,state) VALUES(?,?,'held')", (task, fingerprint))
        emit("reserve_committed", task, wire_sha256=fingerprint)
        return 200, {"approval_sha256": digest(b"synthetic-b2o"), "counted_fingerprint": fingerprint,
                     "pricing_id": h6_p0.PRICING_ID, "service_tier": "default", "input_tokens": 4000,
                     "max_output_tokens": 600, "valid_until": (datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat()}
    if op != "settle" or value["outcome"] not in {"usage_recorded", "outcome_unknown"}:
        return 422, {}
    succeeded = value["outcome"] == "usage_recorded"
    if succeeded != isinstance(value["usage"], dict):
        return 422, {}
    with tx(write=True) as db:
        changed = db.execute("""UPDATE reserves SET state=?,outcome=?,success_count=?
            WHERE task=? AND digest=? AND outcome IS NULL""",
            ("settled" if succeeded else "held", value["outcome"], int(succeeded), task, fingerprint)).rowcount
        if changed != 1:
            return 409, {}
    emit("writer_outcome_committed", task, outcome=value["outcome"], success_count=int(succeeded))
    return 200, True


def run_guard():
    import guard

    assert not h6_provider.LIVE_ENABLED and guard.PROVIDER_LANE is None
    current = threading.local()
    context_by_socket = {}
    original_abort = h6_provider.abort

    class Connection(HTTPConnection):
        def connect(self):
            emit("transport_connect_start", current.task)
            super().connect()
            context_by_socket[self.sock] = current.task
            emit("transport_connected", current.task)

        def request(self, method, url, body=None, headers=None, *, encode_chunked=False):
            assert method == "POST" and url == h6_provider.RESPONSES_PATH and self.sock is not None
            emit("transport_post", current.task, wire_sha256=digest(body))
            return super().request(method, url, body, headers, encode_chunked=encode_chunked)

        def getresponse(self):
            try:
                if not self.sock.recv(1, socket.MSG_PEEK):
                    raise RemoteDisconnected("synthetic upstream closed before first byte")
            except OSError as exc:
                emit("transport_read_ended", current.task, error=type(exc).__name__)
                raise
            emit("transport_first_byte", current.task)
            return super().getresponse()

        def close(self):
            context_by_socket.pop(self.sock, None)
            super().close()

    def observed_abort(sock):
        emit("guard_response_timer_fired", context_by_socket.get(sock))
        original_abort(sock)

    def writer_rpc(message):
        code, reply = rpc("writer", "/ipc", secret("WRITER"), message, timeout=4)
        if code != 200:
            raise RuntimeError("synthetic_writer_denied")
        emit("writer_ack", message["task_id"], operation=message["op"], http=code)
        return reply

    class Lane(h6_provider.Lane):
        def run(self, body, freeze, scope):
            current.task, _ = scope(body)
            emit("guard_request", current.task)
            try:
                return super().run(body, freeze, scope)
            except h6_provider.UnknownOutcome as exc:
                emit("guard_outcome_unknown", current.task, cause=type(exc.__cause__).__name__)
                raise
            finally:
                del current.task

    class ObservedGuard(guard.Handler):
        def run_provider_one_shot(self, body):
            self.task, _ = guard.mock_scope(body)
            return super().run_provider_one_shot(body)

        def send_response(self, code, message=None):
            if hasattr(self, "task"):
                emit("guard_http_response", self.task, http=code)
            return super().send_response(code, message)

    guard.service_token = lambda: secret("GUARD")
    guard.PROVIDER_LANE = Lane(writer_rpc, lambda: Connection("provider", 8082, timeout=h6_provider.CONNECT_TIMEOUT),
                               lambda: secret("UPSTREAM"))
    h6_provider.abort = observed_abort
    serve(ObservedGuard)


class Provider(provider_mock.Handler):
    def log_message(self, *_):
        pass

    def do_POST(self):  # noqa: N802
        if self.path != "/v1/responses" or not self.authorized():
            return super().do_POST()
        wire = self.rfile.read(int(self.headers["Content-Length"]))
        matches = [task for task in DELAYS if ("task_id=" + task + ";").encode() in wire]
        if len(matches) != 1:
            return self.send_json(422, {"error": "unknown_synthetic_task"})
        task, = matches
        fingerprint = digest(wire)
        with tx(write=True) as db:
            db.execute("INSERT INTO posts VALUES(?,?)", (task, fingerprint))
        emit("provider_post_committed", task, wire_sha256=fingerprint)
        time.sleep(DELAYS[task])
        emit("provider_response_attempt", task)
        self.rfile = BytesIO(wire)
        try:
            super().do_POST()
            emit("provider_response_written", task)
        except (BrokenPipeError, ConnectionResetError):
            emit("provider_response_connection_closed", task)


def serve(handler):
    with ThreadingHTTPServer(("0.0.0.0", PORTS[ROLE]), handler) as server:
        server.serve_forever()


def snapshot():
    query = {"provider": "SELECT task,digest,count(*) AS dispatches FROM posts GROUP BY task,digest ORDER BY task",
             "writer": "SELECT * FROM reserves ORDER BY task",
             "receipt": "SELECT binding,receipt,outcome FROM inbox ORDER BY binding",
             "bridge": "SELECT job,task,state,hermes_run,binding,outcome,receipt FROM jobs ORDER BY task"}[ROLE]
    with tx() as db:
        rows = [dict(row) for row in db.execute(query)]
    for row in rows:
        if "hermes_run" in row:
            run = row.pop("hermes_run")
            row["stored_run_id_sha256"] = digest(run.encode()) if run else None
        for name in ("binding", "receipt"):
            if isinstance(row.get(name), bytes):
                row[name] = json.loads(row[name])
    print(raw(rows).decode())


def driver():
    from h6_b2n_runtime_fixture import wait_for

    wait_for(lambda: rpc("n8n", "/healthz/readiness")[0] == 200)
    wait_for(lambda: rpc("bridge", "/ready", secret("ADMIT"))[0] == 200)
    for task in DELAYS:
        request = {"phase": "start", "task_id": task, "correlation_id": "corr-" + task,
                   "input": {"channel": "ads", "spend": 1.25, "clicks": 3}}
        if task == "b2o-31":
            def registered():
                code, _ = rpc("n8n", PATH, "synthetic-wrong", request)
                if code == 404:
                    return False
                assert code == 401
                return True
            wait_for(registered)
        emit("n8n_submit", task)
        code, admitted = rpc("n8n", PATH, secret("WEBHOOK"), request, timeout=32)
        assert code == 202, code
        emit("n8n_admission", task, http=code, job=admitted["job_id"], request_sha256=admitted["request_sha256"])

        def terminal():
            code, job = rpc("bridge", "/jobs/" + admitted["job_id"], secret("ADMIT"))
            assert code == 200, code
            assert job["state"] != "dead_letter", job
            return job if job["state"] == "delivered" else None

        job = wait_for(terminal, timeout=75)
        emit("driver_observed_receipt", task, outcome=job["outcome"], receipt_sha256=job["receipt"])
    # Allow the 46 s response attempt to run after the 45 s transport cutoff.
    time.sleep(3)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[2] == "snapshot":
        snapshot()
    elif ROLE == "bridge":
        initialize("""CREATE TABLE IF NOT EXISTS jobs(job TEXT PRIMARY KEY,task TEXT UNIQUE,request BLOB NOT NULL,
                   state TEXT NOT NULL,hermes_run TEXT UNIQUE,binding BLOB,outcome TEXT,receipt TEXT)""")
        threading.Thread(target=work, daemon=True).start()
        serve(Handler)
    elif ROLE == "receipt":
        initialize("CREATE TABLE IF NOT EXISTS inbox(job TEXT PRIMARY KEY,binding BLOB NOT NULL,receipt BLOB,outcome TEXT)")
        serve(Handler)
    elif ROLE == "writer":
        initialize("""CREATE TABLE IF NOT EXISTS reserves(task TEXT PRIMARY KEY,digest TEXT NOT NULL,
                   state TEXT NOT NULL,outcome TEXT,success_count INTEGER DEFAULT 0)""")
        serve(Handler)
    elif ROLE == "provider":
        initialize("CREATE TABLE IF NOT EXISTS posts(task TEXT NOT NULL,digest TEXT NOT NULL)")
        provider_mock.token = lambda: secret("UPSTREAM").encode()
        serve(Provider)
    elif ROLE == "guard":
        run_guard()
    elif ROLE == "driver":
        driver()
    else:
        raise RuntimeError("unrecognized synthetic role")
