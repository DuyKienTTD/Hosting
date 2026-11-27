"""Disposable H3 mock rehearsal hooks. No provider credential or paid transport."""
import hashlib
import io
import json
import re
import sys
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from mock_contract import freeze

LEDGER = Path("/opt/ttd/mock-ledger/level2-budget.json")
CACHE_KEY = "h3-disposable-fixture"


def freeze_mock(body):
    return freeze(dict(body, prompt_cache_key=CACHE_KEY))


def stage(capture_directory, task, fixture):
    paths = sorted(Path(capture_directory).glob("request-*-raw.json"), reverse=True)
    for path in paths:
        raw = path.read_text()
        match = re.search(r"task_id=(e2e-success-[0-9]+);", raw)
        if match:
            body = json.loads(raw.replace(match[1], task))
            wire, digest = freeze_mock(body)
            Path(fixture).write_bytes(wire)
            print(json.dumps({"stage_sha256": digest, "bytes": len(wire)}))
            return
    raise SystemExit("no known synthetic success fixture")


def run_guard():
    import guard
    if guard.LEDGER_PATH != LEDGER or guard.MOCK_URL != "http://gate-a-provider-mock:8082/v1/responses":
        raise SystemExit("requires mock ledger and fixed mock upstream")
    if guard.ledger_summary()["kill_switch"] is not True:
        raise SystemExit("requires global kill switch on")
    guard.freeze = freeze_mock
    ThreadingHTTPServer((guard.HOST, guard.PORT), guard.Handler).serve_forever()


def run_provider():
    import provider_mock

    class ObservedMock(provider_mock.Handler):
        def do_POST(self):
            if not self.authorized() or self.path != "/v1/responses":
                return super().do_POST()
            if not 0 < int(self.headers.get("Content-Length", "0")) <= 4000:
                self.send_error(400)
                return
            wire = self.rfile.read(int(self.headers["Content-Length"]))
            digest = hashlib.sha256(wire).hexdigest()
            ledger = json.loads(LEDGER.read_bytes())
            tasks = ledger["tasks"]
            matches = [(key, permit) for key, permit in ledger["one_shot_permits"].items()
                       if permit["fingerprint"] == digest and permit["state"] == "consumed"]
            ready = (len(matches) == 1 and ledger["kill_switch"] is True
                     and tasks[matches[0][0]]["state"] == "inflight"
                     and tasks[matches[0][0]]["reserved_usd"] == 0.0035)
            print(json.dumps({"h3_received": True, "wire_sha256": digest,
                              "consumed_and_reserved_on_receipt": ready}), flush=True)
            if not ready:
                self.send_error(412)
                return
            source = self.rfile
            with io.BytesIO(wire) as buffered:
                self.rfile = buffered
                try:
                    super().do_POST()
                finally:
                    self.rfile = source

    ThreadingHTTPServer((provider_mock.HOST, provider_mock.PORT), ObservedMock).serve_forever()


def negatives(fixture, task):
    import guard
    wire = Path(fixture).read_bytes()
    body = json.loads(wire)
    checks = [
        (dict(body, model="incorrect"), guard.service_token(), 422),
        (body, "invalid-mock-service-auth", 401),
        (dict(body, instructions=body["instructions"] + " Changed."), guard.service_token(), 503),
        (json.loads(wire.replace(task.encode(), b"h3-wrong-task")), guard.service_token(), 503),
    ]
    for value, auth, expected in checks:
        request = urllib.request.Request("http://127.0.0.1:8081/v1/responses", data=json.dumps(value).encode(),
                                         headers={"Authorization": "Bearer " + auth})
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                status = response.status
        except urllib.error.HTTPError as error:
            status = error.code
            error.close()
        if status != expected:
            raise SystemExit(f"negative: expected {expected}, got {status}")
    print("h3_negative_statuses 422 401 503 503")


if __name__ == "__main__":
    modes = {"stage": stage, "guard": run_guard, "provider": run_provider, "negatives": negatives}
    modes[sys.argv[1]](*sys.argv[2:])
