"""Network-internal provider recorder, receipt store and driver for B2-N."""

from contextlib import closing
from hashlib import sha256
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

import provider_mock

AUTH = os.environ["B2N_HTTP_BEARER"]
ENGINE = os.environ["B2N_ENGINE_BEARER"]
ROUTE = os.environ["B2N_RECEIPT_BEARER"]
UPSTREAM = os.environ["B2N_PROVIDER_BEARER"]
BASE_PATH = "/webhook/ttd-p0-fake-ads-audit-v1"
CANDIDATE_PATH = "/webhook/b2n-receipt-fixture"
DATA = Path("/fixture-data")
MODEL = "gpt-6-luna"
DELAYS = {"lost": 0.2, "medium": 31, "slow": 46}


def wire(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(value):
    return sha256(wire(value)).hexdigest()


def call(service, path, body=None, *, bearer=None, headers=None, timeout=5, abandon=False):
    hosts = {"hermes": 8642, "n8n": 5678, "provider": 8082, "receipt": 8083}
    with closing(HTTPConnection(service, hosts[service], timeout=timeout)) as client:
        hs = dict(headers or {})
        if bearer is not None:
            hs["Authorization"] = "Bearer " + bearer
        if body is not None:
            hs["Content-Type"] = "application/json"
        client.request("GET" if body is None else "POST", path,
                       None if body is None else wire(body), hs)
        if abandon:
            return
        with client.getresponse() as r:
            raw = r.read()
            try:
                body = json.loads(raw) if raw else {}
            except ValueError:
                body = {"non_json_response": True, "length": len(raw), "type": r.getheader("Content-Type")}
            return r.status, body, dict(r.getheaders())


def database():
    conn = sqlite3.connect(DATA / "state.sqlite", timeout=3)
    conn.row_factory = sqlite3.Row
    return conn


def initialize(sql):
    with closing(database()) as db, db:
        db.executescript(sql)


class Provider(provider_mock.Handler):
    def log_message(self, *args):
        pass

    def do_GET(self):  # noqa: N802
        if self.path == "/counts":
            with closing(database()) as db:
                self.send_json(200, {r["label"]: r["n"] for r in db.execute(
                    "SELECT label,count(*) AS n FROM dispatch GROUP BY label")})
        else:
            super().do_GET()

    def do_POST(self):  # noqa: N802
        if self.path != "/v1/responses" or not self.authorized():
            return super().do_POST()
        raw = self.rfile.read(int(self.headers["Content-Length"]))
        needles = [label for label in DELAYS if ("B2N_" + label.upper()).encode() in raw]
        if len(needles) != 1:
            self.send_json(422, {"error": "unrecognized_fixture_request"})
            return
        label = needles[0]
        with closing(database()) as db, db:
            db.execute("INSERT INTO dispatch VALUES (?,?)", (label, time.time()))
        time.sleep(DELAYS[label])
        self.rfile = BytesIO(raw)
        try:
            super().do_POST()
        except (BrokenPipeError, ConnectionResetError):
            pass


class Receipt(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, status, body):
        raw = wire(body)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):  # noqa: N802
        if self.path != "/state" or self.headers.get("Authorization") != "Bearer " + ROUTE:
            self.send_json(401, {})
            return
        with closing(database()) as db:
            rows = [dict(r) for r in db.execute("SELECT job,receipt,outcome FROM jobs ORDER BY job")]
        self.send_json(200, rows)

    def do_POST(self):  # noqa: N802
        expected = AUTH if self.path == "/v1/reason" else ROUTE
        if self.headers.get("Authorization") != "Bearer " + expected:
            self.send_json(401, {})
            return
        raw = self.rfile.read(int(self.headers["Content-Length"]))
        value = json.loads(raw)
        if self.path == "/v1/reason":
            self.send_json(202, {"accepted": True, "synthetic": True})
            return
        job = value.get("job_id")
        if self.path == "/bind":
            with closing(database()) as db, db:
                db.execute("INSERT INTO jobs(job,binding) VALUES (?,?)", (job, wire(value)))
            self.send_json(201, {})
            return
        if self.path != "/receipt":
            self.send_json(404, {})
            return
        code, reply = self.accept_event(job, value)
        if code == 200 and value.get("fixture_hold_ack") and not reply["replayed"]:
            time.sleep(2)
        self.send_json(code, reply)

    def accept_event(self, job, value):
        fields = {"job_id", "task_id", "correlation_id", "run_id", "request_sha256", "outcome",
                  "phase", "synthetic", "fixture_hold_ack"}
        outcome = value.get("outcome")
        if (set(value) != fields or value["phase"] != "callback" or value["synthetic"] is not True
                or outcome not in ("mock_succeeded", "outcome_unknown")):
            return 422, {}
        binding = wire({key: value[key] for key in ("job_id", "task_id", "correlation_id", "run_id", "request_sha256")})
        receipt = sha({key: val for key, val in value.items() if key != "fixture_hold_ack"})
        with closing(database()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT binding,receipt FROM jobs WHERE job=?", (job,)).fetchone()
            if not row or row["binding"] != binding or (row["receipt"] and row["receipt"] != receipt):
                return 409, {}
            db.execute("UPDATE jobs SET receipt=?,outcome=? WHERE job=? AND receipt IS NULL", (receipt, outcome, job))
            return 200, {"receipt": receipt, "replayed": row["receipt"] is not None}


def report(label, value):
    print("B2N_RUNTIME_" + label, json.dumps(value, sort_keys=True), flush=True)


def wait_for(check, timeout=45):
    stop = time.monotonic() + timeout
    while time.monotonic() < stop:
        try:
            value = check()
            if value:
                return value
        except OSError:
            pass
        time.sleep(0.25)
    raise TimeoutError("expected isolated fixture observation missing")


def submit(label, *, change=False, abandon=False):
    body = {"input": "B2N_" + label.upper() + " synthetic only" + (" conflict" if change else ""),
            "model": MODEL, "provider": "openai-api",
            "model_options": {"reasoning_effort": "none", "service_tier": "default"}}
    return call("hermes", "/v1/runs", body, bearer=ENGINE, headers={"Idempotency-Key": "b2n-" + label},
                abandon=abandon), sha(body)


def counts():
    return call("provider", "/counts")[1]


def get_run(run):
    return call("hermes", "/v1/runs/" + run, bearer=ENGINE)[1]


def callback(body, bearer=AUTH, timeout=5):
    return call("n8n", CANDIDATE_PATH, body, bearer=bearer, timeout=timeout)


def event_for(label, run, request_digest, outcome):
    binding = {"job_id": label, "task_id": "task-" + label, "correlation_id": "corr-" + label,
               "run_id": run, "request_sha256": request_digest}
    assert call("receipt", "/bind", binding, bearer=ROUTE)[0] == 201
    return binding | {"outcome": outcome, "phase": "callback", "synthetic": True, "fixture_hold_ack": False}


def baseline_callback():
    result = {"summary": "synthetic", "signals": [], "recommendations": []}
    body = {"phase": "callback", "task_id": "fake-baseline", "correlation_id": "fake-correlation",
            "status": "hermes_mock_succeeded", "result_hash": sha(result), "result": result,
            "inference": {"mode": "hermes_mock", "paid": False, "provider": "gate-a-provider-mock",
                          "model": MODEL, "hard_max_output_tokens": 600, "input_upper_bound_tokens": 100,
                          "tools_enabled": False, "physical_requests": 1, "runtime": {
                              "provider": "openai-api", "model": MODEL}}}
    reply = lambda auth: call("n8n", BASE_PATH, body, bearer=auth)
    def registered():
        status, response, _ = reply("fixture-wrong")
        if status == 404:
            return False
        assert status == 401, (status, response)
        return True
    wait_for(registered)
    for _ in range(2):
        result = reply(AUTH)
        assert result[1].get("ack") is True, result[:2]
    assert call("receipt", "/state", bearer=ROUTE)[1] == []
    report("BASELINE_CALLBACK", {"wrong_bearer": 401, "same_callback_accepted_twice": True, "fixture_receipts": 0})


def phase_one():
    wait_for(lambda: call("hermes", "/health")[0] == 200)
    wait_for(lambda: call("n8n", "/healthz/readiness")[0] == 200)
    baseline_callback()
    submit("lost", abandon=True)
    wait_for(lambda: counts().get("lost") == 1)
    (code, body, _), fingerprint = submit("lost")
    assert code == 202 and body.get("replayed") is True
    run = body["run_id"]
    status = wait_for(lambda: get_run(run) if get_run(run).get("status") in ("completed", "failed") else None)
    assert status["status"] == "completed", "Hermes fake result must complete"
    (DATA / "lost.json").write_bytes(wire({"run": run, "request_sha256": fingerprint}))
    report("LOST_ACK", {"run_id_sha256": sha(run), "request_sha256": fingerprint, "http": code,
                         "replayed_before_restart": True, "fake_dispatches": counts()["lost"]})


def phase_two():
    wait_for(lambda: call("hermes", "/health")[0] == 200)
    lost = json.loads((DATA / "lost.json").read_bytes())
    (code, body, _), fingerprint = submit("lost")
    assert code == 202 and body["replayed"] and body["run_id"] == lost["run"]
    assert fingerprint == lost["request_sha256"] and counts()["lost"] == 1
    assert submit("lost", change=True)[0][0] == 409
    report("RESTART", {"same_run_id": True, "http": code, "different_binding_http": 409, "fake_dispatches": 1})
    for label in ("medium", "slow"):
        (status, run_body, _), digest = submit(label)
        assert status == 202
        run_id = run_body["run_id"]
        wait_for(lambda: counts().get(label) == 1, timeout=8)
        start = time.monotonic()
        terminal = None
        while time.monotonic() - start < 45:
            state = get_run(run_id).get("status")
            if state in ("completed", "failed", "unknown", "interrupted"):
                terminal = state
                break
            time.sleep(0.20)
        elapsed = time.monotonic() - start
        assert (label == "medium" and terminal == "completed" and 30 < elapsed < 45) or +               (label == "slow" and terminal is None and 45 <= elapsed < 48), (label, terminal, elapsed)
        chosen = "mock_succeeded" if terminal else "outcome_unknown"
        value = event_for(label, run_id, digest, chosen)
        assert callback(value, bearer="fixture-wrong")[0] == 401
        assert callback(value | {"request_sha256": "0" * 64})[0] == 409
        if label == "medium":
            value["fixture_hold_ack"] = True
            try:
                callback(value, timeout=0.7)
            except TimeoutError:
                pass
            else:
                raise AssertionError("receipt ACK fault did not fire")
        else:
            assert callback(value)[0] == 200
        row = next(row for row in call("receipt", "/state", bearer=ROUTE)[1] if row["job"] == label)
        assert row["receipt"] and row["outcome"] == chosen and counts()[label] == 1
        (DATA / (label + ".json")).write_bytes(wire({"event": value, "receipt": row["receipt"]}))
        report("DEADLINE", {"case": label, "elapsed_since_recorder_seen_s": round(elapsed, 3),
                             "hermes_terminal_at_cutoff": terminal, "candidate_outcome": chosen,
                             "fake_dispatches": 1, "durable_receipts": 1, "wrong_auth_http": 401,
                             "wrong_binding_http": 409, "receipt_ack_lost": label == "medium"})


def phase_three():
    for label in ("medium", "slow"):
        saved = json.loads((DATA / (label + ".json")).read_bytes())
        status, body, _ = callback(saved["event"])
        assert status == 200 and body == {"replayed": True, "receipt": saved["receipt"]}
        changed = "outcome_unknown" if label == "medium" else "mock_succeeded"
        assert callback(saved["event"] | {"outcome": changed})[0] == 409
    rows = call("receipt", "/state", bearer=ROUTE)[1]
    assert len(rows) == 2 and all(r["receipt"] for r in rows) and counts() == {"lost": 1, "medium": 1, "slow": 1}
    report("RECEIPT_RESTART", {"matched_persisted_receipts": 2, "conflicting_replay_http": 409,
                               "fake_dispatch_counts": counts(), "duplicate_receipts": 0})


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "provider":
        provider_mock.token = lambda: UPSTREAM.encode()
        initialize("CREATE TABLE IF NOT EXISTS dispatch(label TEXT NOT NULL, time REAL NOT NULL);")
        ThreadingHTTPServer(("0.0.0.0", 8082), Provider).serve_forever()
    elif mode == "receipt":
        initialize("CREATE TABLE IF NOT EXISTS jobs(job TEXT PRIMARY KEY, binding BLOB, receipt TEXT, outcome TEXT);")
        ThreadingHTTPServer(("0.0.0.0", 8083), Receipt).serve_forever()
    else:
        {"one": phase_one, "two": phase_two, "three": phase_three}[mode]()
