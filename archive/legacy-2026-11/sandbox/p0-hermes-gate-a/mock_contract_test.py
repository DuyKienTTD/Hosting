"""Exercise the real guard over loopback with disposable state and fake usage."""

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import guard
from mock_contract import freeze
from one_shot_linux_test import fixture

TASK_ID = "gate-b"
BODY = {"stream": True, "model": "gpt-6-luna", "instructions": "Reviewed fake instructions",
        "input": [{"role": "user", "content": "task_id=gate-b; correlation_id=fake; channel=ads; spend=25.00; clicks=7"}]}


@contextmanager
def server(handler):
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as instance:
        worker = threading.Thread(target=instance.serve_forever, daemon=True)
        worker.start()
        try:
            yield f"http://127.0.0.1:{instance.server_port}/v1/responses"
        finally:
            instance.shutdown()
            worker.join()


def exercise(root, mode):
    path = root / "level2-budget.json"
    fixture(path)
    data = json.loads(path.read_bytes())
    del data["one_shot_permits"]
    path.write_text(json.dumps(data))
    reviewed = root / "reviewed-fixture.json"
    reviewed.write_text(json.dumps(BODY))
    preparation = subprocess.run([sys.executable, str(Path(__file__).with_name("prepare_mock_permit.py")),
                                  str(path), str(reviewed)], check=True, capture_output=True, text=True)
    expected_wire, digest = freeze(BODY)
    assert json.loads(preparation.stdout)["forwarded_sha256"] == digest
    received = []

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            wire = self.rfile.read(int(self.headers["Content-Length"]))
            ledger = json.loads(path.read_bytes())
            received.append((wire, ledger["attempts"], ledger["reserved_usd"],
                             ledger["one_shot_permits"][TASK_ID]["state"], ledger["tasks"][TASK_ID]["state"]))
            if mode == "timeout":
                time.sleep(0.55)
                return
            response = {"model": "gpt-6-luna", "status": "completed", "service_tier": "default",
                        "id": "resp_mock_fixture", "usage": {"input_tokens": 200, "output_tokens": 20,
                        "total_tokens": 220, "input_tokens_details": {"cached_tokens": 60, "cache_write_tokens": 40},
                        "output_tokens_details": {"reasoning_tokens": 8}}}
            event_type = "response.created" if mode == "truncated" else "response.completed"
            payload = f'data: {json.dumps({"type": event_type, "response": response})}\n\n'.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def submit(url, value):
        req = urllib.request.Request(url, data=json.dumps(value).encode(),
                                     headers={"Authorization": "Bearer fixture-value", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=3) as response:
                return response.status
        except urllib.error.HTTPError as error:
            error.close()
            return error.code

    with server(Provider) as endpoint:
        with patch.multiple(guard, LEDGER_PATH=path, MOCK_ONE_SHOT_LEDGER=str(path),
                            MOCK_URL=endpoint, MOCK_TIMEOUT=0.25, CAPTURE_DIR=root,
                            CAPTURE_LOCK=root / "capture.lock", CAPTURE_INDEX=root / "capture-index.json",
                            service_token=lambda: "fixture-value"):
            with server(guard.Handler) as url:
                tampered = copy.deepcopy(BODY)
                tampered["instructions"] += " with an extra field value"
                assert submit(url, tampered) == 503 and received == []
                assert json.loads(path.read_bytes())["one_shot_permits"][TASK_ID]["state"] == "ready"
                assert submit(url, BODY) == (200 if mode == "complete" else 502)
                assert submit(url, BODY) == 503
    assert received == [(expected_wire, 2, 0.007, "consumed", "inflight")]
    ledger = json.loads(path.read_bytes())
    task = ledger["tasks"][TASK_ID]
    assert task["fingerprint"] == hashlib.sha256(received[0][0]).hexdigest()
    assert ledger["attempts"] == 2 and ledger["reserved_usd"] == 0.007
    assert ledger["kill_switch"] is True and ledger["actual_usd"] == data["actual_usd"]
    if mode == "complete":
        assert task["state"] == "usage_recorded"
        assert task["mock_usage"]["estimated_cost_usd"] == "0.0000256"
        assert task["mock_usage"]["reasoning_tokens"] == 8
    else:
        assert task["state"] == "outcome_unknown" and task["mock_usage"] is None
    return {"mode": mode, "physical_mock_requests": len(received), "ledger_state": task["state"],
            "exact_wire_digest_match": True, "pre_dispatch_consume_observed": True,
            "tamper_dispatched": False, "replay_dispatched": False}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temp:
        results = []
        for mode in ("complete", "timeout", "truncated"):
            root = Path(temp) / mode / "mock-ledger"
            root.mkdir(mode=0o700, parents=True)
            results.append(exercise(root, mode))
        print(json.dumps({"result": "PASS", "cases": results, "paid_calls": 0}))
