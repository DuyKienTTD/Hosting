"""B2-E ext4 and callback test adaptations for the pinned B2-D suite."""

import json
import tempfile
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import guard
import h6_b2d_mock_test as suite
import h6_stage_a_test as stage_a
from mock_contract import encode

EXT4_CASES = Path("/opt/ttd/b2e-cases")
FUTURE_FIELD = {"fixture_only": ["preserved", 2]}


def callback():
    hits, callbacks = [], []

    class Stub(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            assert self.headers["Authorization"] == f"Bearer {stage_a.TOKEN}"
            hits.append(body)
            response = {"id": "b2e-synthetic", "model": suite.one_shot.MODEL, "service_tier": "default",
                        "status": "completed", "usage": {"input_tokens": 723, "output_tokens": 20,
                        "total_tokens": 743, "input_tokens_details": {"cached_tokens": 0},
                        "output_tokens_details": {"reasoning_tokens": 0}}}
            payload = b"data: " + encode({"type": "response.completed", "response": response}) + b"\n\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    class N8n(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            authorized = self.headers["Authorization"] == f"Bearer {stage_a.TOKEN}"
            if authorized:
                callbacks.append((self.path, payload))
            self.send_response(200 if authorized else 401)
            self.end_headers()
            self.wfile.write(b"{}")

    wire, fingerprint = guard.freeze_stage_a(stage_a.BODY)
    task, key_hash = guard.mock_scope(stage_a.BODY)
    with (tempfile.TemporaryDirectory(dir=EXT4_CASES) as directory,
          patch.multiple(suite, TASK=task, KEY_HASH=key_hash, FINGERPRINT=fingerprint),
          suite.case(Path(directory), "callback") as (ledger, _),
          suite.running_writer(), suite.http_server(Stub) as stub, suite.http_server(N8n) as receiver,
          suite.http_server(guard.Handler) as port,
          patch.multiple(guard, MOCK_URL=f"http://127.0.0.1:{stub}/mock", service_token=lambda: stage_a.TOKEN)):
        stage_a.check_callback(port, receiver, callbacks)
        assert hits == [wire] and len(callbacks) == 1
        assert json.loads(ledger.read_bytes())["tasks"][task]["state"] == "usage_recorded"
    print("PASS B2E callback: actual bridge and B2-D Guard/writer, one mock dispatch and one authenticated webhook", flush=True)


def run():
    assert any(line.split()[4] == str(EXT4_CASES) and line.split(" - ")[1].split()[0] == "ext4"
               for line in Path("/proc/self/mountinfo").read_text().splitlines())
    original_seed, original_race = suite.seed, suite.concurrency

    def seed(path):
        original_seed(path)
        value = json.loads(path.read_bytes())
        value["future_b2e_fixture_extension"] = FUTURE_FIELD
        path.write_bytes(encode(value))

    def race(path, lock):
        original_race(path, lock)
        assert json.loads(path.read_bytes())["future_b2e_fixture_extension"] == FUTURE_FIELD
        print("PASS B2E ext4: unknown Level 2 ledger field preserved", flush=True)

    scratch = SimpleNamespace(TemporaryDirectory=lambda *, dir: tempfile.TemporaryDirectory(dir=EXT4_CASES))
    with patch.multiple(suite, tempfile=scratch, seed=seed, concurrency=race):
        suite.tests()
    callback()


if __name__ == "__main__":
    run()
