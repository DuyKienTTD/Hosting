"""Run with Linux, in a disposable container with --network none."""

import concurrent.futures
import fcntl
import hashlib
import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import bridge
import guard
import h6_writer
import one_shot
from mock_contract import encode
from one_shot_linux_test import fixture

BODY = {
    "model": "gpt-6-luna", "stream": True, "reasoning": {"effort": "none"},
    "instructions": "Return only fictional fixture data.",
    "input": [{"role": "user", "content": "task_id=gate-b; correlation_id=h6-callback; channel=ads; spend=25.00; clicks=7"}],
}
TOKEN = "synthetic-h6-guard-and-callback-fixture"


def state(path):
    return json.loads(path.read_bytes())


def make_fixture(path, digest):
    fixture(path)
    ledger = state(path)
    ledger["h6_stage_a_fixture"] = True
    scope = ledger["one_shot_permits"]["gate-b"]
    scope.update(key_hash=guard.mock_scope(BODY)[1], fingerprint=digest, mock_input_tokens=723)
    path.write_bytes(encode(ledger))
    os.chown(path, h6_writer.WRITER_UID, h6_writer.IPC_GID)
    path.chmod(0o600)


def command(action, *args):
    return [sys.executable, "-B", __file__, action, *map(str, args)]


@contextmanager
def child(action, uid, *args, pass_fds=()):
    process = subprocess.Popen(command(action, *args), user=uid, group=h6_writer.IPC_GID,
                               extra_groups=[], pass_fds=pass_fds)
    try:
        yield process
    finally:
        if process.poll() is None:
            process.terminate()
        process.wait(timeout=4)


def wait_until(check):
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        if check():
            return
        time.sleep(0.01)
    raise AssertionError("fixture startup timeout")


def http_call(port, path, body=None, authorized=True):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=4)
    try:
        headers = {"Content-Type": "application/json"}
        if authorized:
            headers["Authorization"] = "Bearer " + TOKEN
        conn.request("GET" if body is None else "POST", path, body, headers)
        response = conn.getresponse()
        return response.status, response.read()
    finally:
        conn.close()


@contextmanager
def guard_service(address, upstream):
    with ThreadingHTTPServer(("127.0.0.1", 0), guard.Handler) as server:
        fd = server.fileno()
        with child("guard", h6_writer.GUARD_UID, address, upstream, fd, pass_fds=(fd,)):
            yield server.server_port


def running_guard(address, upstream, fd):
    class QuietGuard(guard.Handler):
        def log_message(self, *_):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), QuietGuard, bind_and_activate=False) as server:
        server.socket.close()
        server.socket = socket.socket(fileno=int(fd))
        with patch.multiple(guard, H6_STAGE_A_SOCKET=address, MOCK_URL=upstream,
                            MOCK_TIMEOUT=0.5, service_token=lambda: TOKEN):
            server.serve_forever()


def running_writer(address, path, crash):
    if crash == "normal":
        h6_writer.serve(address, path)
    durable_write = one_shot._durable_write

    def injected(ledger_path, ledger):
        if crash == "before_commit":
            os._exit(31)
        durable_write(ledger_path, ledger)
        os._exit(32)

    with patch.object(one_shot, "_durable_write", injected):
        h6_writer.serve(address, path)


def check_peers(address):
    original = address.stat()
    assert (original.st_mode & 0o777, original.st_uid, original.st_gid) == (0o660, 23062, 23060)
    assert address.parent.stat().st_mode & 0o777 == 0o750
    # A different UID with the allowed GID can connect, but writer rejects its peer identity.
    subprocess.run(command("wrong_peer", address), user=23063, group=h6_writer.IPC_GID,
                   extra_groups=[], timeout=4, check=True)
    subprocess.run(command("wrong_permissions", address), user=23063, group=23063,
                   extra_groups=[], timeout=4, check=True)


def probe_peer(address):
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
        conn.settimeout(2)
        conn.connect(address)
        try:
            h6_writer.send(conn, {"v": 1, "op": "snapshot"})
            assert conn.recv(4096) == b""
        except (BrokenPipeError, ConnectionResetError):
            pass


def probe_permissions(address):
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
        try:
            conn.connect(address)
        except PermissionError:
            return
        raise AssertionError("socket permissions admitted another group")


def check_protocol(address):
    subprocess.run(command("bad_packets", address), user=h6_writer.GUARD_UID, group=h6_writer.IPC_GID,
                   extra_groups=[], timeout=4, check=True)


def probe_protocol(address):
    bad_packets = (b"x" * 4097, b'{"v":1,"v":1,"op":"snapshot"}', b'{"v":2,"op":"snapshot"}',
                   b'{"v":1,"op":"reset"}', b'{"v":1,"op":"snapshot","path":"unexpected"}')
    for packet in bad_packets:
        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
            conn.settimeout(2)
            conn.connect(address)
            conn.sendall(packet)
            assert json.loads(conn.recv(4096)) == {"v": 1, "error": "H6_WRITER_REJECTED"}


def check_impostor(root):
    address = root / "impostor.sock"
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
        listener.bind(str(address))
        address.chmod(0o666)
        listener.listen(1)
        try:
            h6_writer.call(address, "snapshot")
        except PermissionError as error:
            assert str(error) == "H6_IPC_PEER_REJECTED"
        else:
            raise AssertionError("client trusted wrong writer UID")
        with listener.accept()[0] as conn:
            assert conn.recv(4096) == b"", "client transmitted before authenticating writer"


def exercise(root, mode, wire, digest):
    root.mkdir(mode=0o755)
    ipc = root / "ipc"
    ipc.mkdir(mode=0o750)
    os.chown(ipc, h6_writer.WRITER_UID, h6_writer.IPC_GID)
    directory = root / "mock-ledger"
    directory.mkdir(mode=0o700)
    os.chown(directory, h6_writer.WRITER_UID, h6_writer.IPC_GID)
    path = directory / "level2-budget.json"
    address = ipc / "writer.sock"
    make_fixture(path, digest)
    lock_path = path.with_suffix(".json.lock")
    lock_path.touch(mode=0o600)
    os.chown(lock_path, h6_writer.WRITER_UID, h6_writer.IPC_GID)
    stable_lock_inode = lock_path.stat().st_ino
    hits, callbacks = [], []

    class Mock(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            hits.append(("unexpected_redirect", self.path))
            self.send_error(405)

        def do_POST(self):
            assert self.headers.get("Authorization") == "Bearer " + TOKEN
            item = self.rfile.read(int(self.headers["Content-Length"]))
            ledger = state(path)
            hits.append((self.path, item, ledger["one_shot_permits"]["gate-b"]["state"],
                         ledger["tasks"]["gate-b"]["state"], ledger["reserved_usd"]))
            if mode == "redirect":
                self.send_response(302)
                self.send_header("Location", "/redirect-target")
                self.end_headers()
                return
            if mode == "timeout":
                time.sleep(0.8)
                return
            response = {"id": "resp_h6_fake", "model": "gpt-6-luna", "service_tier": "default", "status": "completed",
                        "usage": {"input_tokens": 723, "output_tokens": 20, "total_tokens": 743,
                                  "input_tokens_details": {"cached_tokens": 0},
                                  "output_tokens_details": {"reasoning_tokens": 0}}}
            event = "response.created" if mode == "truncated" else "response.completed"
            payload = b"data: " + encode({"type": event, "response": response}) + b"\n\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(payload) + (10 if mode == "short_body" else 0)))
            self.end_headers()
            self.wfile.write(payload)

    class N8nFixture(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            auth = self.headers.get("Authorization") == "Bearer " + TOKEN
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if auth:
                callbacks.append((self.path, payload))
            self.send_response(200 if auth else 401)
            self.end_headers()
            self.wfile.write(b"{}")

    with ThreadingHTTPServer(("127.0.0.1", 0), Mock) as mock, \
            ThreadingHTTPServer(("127.0.0.1", 0), N8nFixture) as n8n, \
            path.open("rb") as old_inode:
        upstream = f"http://127.0.0.1:{mock.server_port}/v1/responses"
        with guard_service(address, upstream) as port:
            mock_threads = [threading.Thread(target=server.serve_forever, daemon=True) for server in (mock, n8n)]
            for thread in mock_threads:
                thread.start()
            try:
                assert http_call(port, "/healthz")[0] == 503
                run_case(mode, address, path, port, n8n.server_port, hits, callbacks)
            finally:
                for server in (mock, n8n):
                    server.shutdown()
                for thread in mock_threads:
                    thread.join()
        expected_hits = [] if mode in {"before_commit", "after_commit"} else [
            ("/v1/responses", wire, "consumed", "inflight", 0.007)]
        assert hits == expected_hits
        assert lock_path.stat().st_ino == stable_lock_inode
        assert json.load(old_inode)["attempts"] == 1
        final = state(path)
        assert final["kill_switch"] is True and final["actual_usd"] == 0.0000496
        if mode == "before_commit":
            assert final["attempts"] == 1 and not hits
        else:
            assert final["attempts"] == 2 and final["reserved_usd"] == 0.007
            assert path.stat().st_ino != os.fstat(old_inode.fileno()).st_ino
            expected = {"ok": "usage_recorded", "callback": "usage_recorded",
                        "after_commit": "inflight"}.get(mode, "outcome_unknown")
            assert final["tasks"]["gate-b"]["state"] == expected
            assert final["one_shot_permits"]["gate-b"]["state"] == "consumed"
        return {"mode": mode, "mock_dispatches": len(hits), "callbacks": len(callbacks),
                "attempts": final["attempts"]}


def run_case(mode, address, path, port, callback_port, hits, callbacks):
    crash = mode if mode in {"before_commit", "after_commit"} else "normal"
    submit = lambda body: http_call(port, "/v1/responses", encode(body))[0]
    with child("writer", h6_writer.WRITER_UID, address, path, crash) as writer:
        wait_until(lambda: http_call(port, "/healthz")[0] == 200)
        if mode == "ok":
            check_peers(address)
            check_protocol(address)
            assert http_call(port, "/v1/responses", encode(BODY), authorized=False)[0] == 401
            assert submit(dict(BODY, instructions="tampered")) == 503
            assert submit(dict(BODY, tools=[])) == 422
            assert submit(dict(BODY, input=BODY["input"] * 2)) == 422
            assert submit(dict(BODY, input=[{"type": "function_call_output", "output": "fake"}])) == 422
            baseline = path.read_bytes()
            invalid = json.loads(baseline)
            invalid["one_shot_permits"]["gate-b"]["mock_input_tokens"] = 4001
            path.write_bytes(encode(invalid))
            assert submit(BODY) == 503
            assert state(path)["one_shot_permits"]["gate-b"]["state"] == "ready"
            invalid.pop("h6_stage_a_fixture")
            path.write_bytes(encode(invalid))
            assert submit(BODY) == 503
            path.write_bytes(baseline)
            assert not hits and state(path)["attempts"] == 1
            # Emulate the pre-existing Level 2 writer holding the shared lock.
            with path.with_suffix(".json.lock").open("r+") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                    requests = [pool.submit(submit, dict(BODY, prompt_cache_key=f"transient-{i}"))
                                for i in range(8)]
                    time.sleep(0.10)
                    assert not hits and state(path)["attempts"] == 1
                    fcntl.flock(lock, fcntl.LOCK_UN)
                    assert sorted(item.result() for item in requests) == [200] + [503] * 7
        elif mode == "callback":
            check_callback(port, callback_port, callbacks)
        else:
            assert submit(BODY) == (502 if crash == "normal" else 503)
        if crash != "normal":
            assert writer.wait(timeout=4) == (31 if crash == "before_commit" else 32)
        else:
            assert submit(BODY) == 503
            status, raw = http_call(port, "/healthz")
            assert status == 200
            snapshot = json.loads(raw)["ledger"]
            assert snapshot["attempts"] == 2 and snapshot["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert http_call(port, "/healthz")[0] == 503
    if mode != "before_commit":
        before = path.read_bytes()
        with child("writer", h6_writer.WRITER_UID, address, path, "normal"):
            wait_until(lambda: http_call(port, "/healthz")[0] == 200)
            assert submit(BODY) == 503
        assert path.read_bytes() == before, "rollback restarted writer without changing committed ledger"


def check_callback(guard_port, callback_port, callbacks):
    def fake_hermes(task_id, correlation_id, _input, simulate):
        assert (task_id, correlation_id, simulate) == ("gate-b", "h6-callback", None)
        status, raw = http_call(guard_port, "/v1/responses", encode(BODY))
        assert status == 200
        usage = json.loads(raw.removeprefix(b"data: "))["response"]["usage"]
        return {"result": {"summary": "fake", "signals": [], "recommendations": []},
                "usage": usage, "runtime": {"guard_enforced": True}, "run_id_hash": "synthetic"}

    inbound = encode({"task_id": "gate-b", "correlation_id": "h6-callback",
                      "input": {"channel": "ads", "spend": 25, "clicks": 7}})
    with tempfile.TemporaryDirectory() as directory:
        credential = Path(directory) / "fixture"
        credential.write_text(TOKEN, encoding="utf-8")
        endpoint = f"http://127.0.0.1:{callback_port}/webhook/fake-n8n"
        flags = {"CALLBACK_URL": endpoint, "P0_TOKEN_FILE": credential, "run_hermes": fake_hermes,
                 "STATE_PATH": Path(directory) / "bridge.json", "LOCK_PATH": Path(directory) / "bridge.lock"}
        with patch.multiple(bridge, **flags), ThreadingHTTPServer(("127.0.0.1", 0), bridge.Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                status, result = http_call(server.server_port, "/v1/reason", inbound)
                assert status == 200 and json.loads(result)["callback_http_status"] == 200
                status, replayed = http_call(server.server_port, "/v1/reason", inbound)
                assert status == 200 and json.loads(replayed)["callback_repeated"] is False
            finally:
                server.shutdown()
                thread.join()
    assert http_call(callback_port, "/webhook/fake-n8n", b"{}", authorized=False)[0] == 401
    assert len(callbacks) == 1
    assert callbacks[0][0] == "/webhook/fake-n8n"
    assert callbacks[0][1]["correlation_id"] == "h6-callback"


def main():
    assert os.geteuid() == 0 and set(os.listdir("/sys/class/net")) == {"lo"}
    assert not Path("/run/secrets/openai_provider_api_key").exists()
    wire, digest = guard.freeze_stage_a(BODY)
    assert guard.freeze_stage_a(dict(BODY, prompt_cache_key="different")) == (wire, digest)
    with tempfile.TemporaryDirectory(prefix="h6-") as temp:
        root = Path(temp)
        root.chmod(0o755)
        check_impostor(root)
        results = [exercise(root / mode, mode, wire, digest) for mode in
                   ("ok", "callback", "before_commit", "after_commit", "truncated",
                    "short_body", "timeout", "redirect")]
    print(json.dumps({"result": "PASS", "cases": results, "concurrent_requests": 8,
                      "exact_wire_sha256": digest, "provider_operations": 0, "paid_calls": 0}))


if __name__ == "__main__":
    actions = {
        "guard": running_guard,
        "writer": lambda address, path, crash: running_writer(Path(address), Path(path), crash),
        "wrong_peer": probe_peer,
        "wrong_permissions": probe_permissions,
        "bad_packets": probe_protocol,
    }
    if len(sys.argv) > 1:
        actions[sys.argv[1]](*sys.argv[2:])
    else:
        main()
