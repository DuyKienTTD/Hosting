"""Exercise the actual B2-D Guard/writer on isolated, synthetic Linux fixtures."""

import fcntl
import hashlib
import http.client
import importlib.util
import json
import os
import select
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import guard
import h6_ipc_auth as auth
import h6_writer as writer
import one_shot
from mock_contract import encode

ROOT = Path("/opt/ttd")
BODY = {"model": one_shot.MODEL, "max_output_tokens": 600,
        "input": [{"role": "user", "content": "task_id=fixture; correlation_id=fake; channel=ads; spend=1.00; clicks=1"}]}
WIRE, FINGERPRINT = guard.freeze_stage_a(BODY)
TASK, KEY_HASH = guard.mock_scope(BODY)
ADMIT = {"op": "admit", "task_id": TASK, "key_hash": KEY_HASH, "fingerprint": FINGERPRINT}


def posture():
    assert (os.geteuid(), os.getegid()) == (0, 0)
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines())
    assert all(int(status[name], 16) == 0 for name in ("CapEff", "CapPrm", "CapInh", "CapBnd", "CapAmb"))
    assert int(status["NoNewPrivs"]) == 1
    assert os.statvfs("/").f_flag & os.ST_RDONLY
    assert {path.name for path in Path("/sys/class/net").iterdir()} == {"lo"}
    assert not Path("/var/run/docker.sock").exists()
    assert not auth.PROVIDER_KEY_PATH.exists()


def denied(operation, errors=(PermissionError, ValueError, RuntimeError, ConnectionError, FileNotFoundError)):
    try:
        operation()
    except errors:
        return
    raise AssertionError("unexpected success")


def key_file(path, length, mode=0o400):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode), "wb") as handle:
        handle.write(os.urandom(length))


def seed(path):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    value = {"schema_version": 1, "model": one_shot.MODEL, "max_calls": one_shot.MAX_CALLS,
             "caps_usd": one_shot.CAPS, "attempts": 1, "reserved_usd": 0.0035, "actual_usd": 0,
             "kill_switch": True, "days": {}, "tasks": {"legacy": {"state": "complete"}},
             "h6_stage_a_fixture": True, "one_shot_permits": {TASK: {
                 "state": "ready", "key_hash": KEY_HASH, "fingerprint": FINGERPRINT, "model": one_shot.MODEL,
                 "mock_input_tokens": 723, "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}}}
    path.write_bytes(encode(value))
    path.chmod(0o600)
    path.with_suffix(".json.lock").touch(mode=0o600, exist_ok=False)


def init():
    posture()
    seed(writer.FIXTURE_PATH)
    auth.SOCKET_PATH.parent.chmod(0o700)
    test_auth = Path("/run/h6-b2d-test-auth")
    for directory in (auth.KEY_PATH.parent, test_auth):
        directory.chmod(0o700)
        key_file(directory / "ipc.key", 32)
    for name, size, mode in (("short", 31, 0o400), ("long", 33, 0o400), ("bad-mode", 32, 0o644)):
        key_file(test_auth / name, size, mode)
    (test_auth / "symlink").symlink_to("ipc.key")
    key_file(guard.TOKEN_FILE, 32)
    guard.TOKEN_FILE.chmod(0o600)
    # Guard expects a textual service token. Keep it distinct from both IPC keys.
    guard.TOKEN_FILE.write_text(os.urandom(32).hex())
    print("PASS initialized fake ledger and separate ephemeral IPC keys")


def connect():
    conn = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    conn.settimeout(2)
    conn.connect(str(auth.SOCKET_PATH))
    return conn


def closed(conn):
    try:
        assert conn.recv(4097) == b""
    except ConnectionResetError:
        return


def wait_ready(pid):
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        try:
            with connect():
                return
        except (FileNotFoundError, ConnectionRefusedError):
            assert not os.waitid(os.P_PID, pid, os.WEXITED | os.WNOHANG | os.WNOWAIT), "mock writer exited at startup"
            time.sleep(0.01)
    raise AssertionError("mock writer did not listen")


@contextmanager
def running_writer(crash="", contention_fd=None):
    durable_write = one_shot._durable_write
    original_flock = fcntl.flock

    def observe_flock(fd, flags):
        if flags == fcntl.LOCK_EX:
            try:
                original_flock(fd, flags | fcntl.LOCK_NB)
                return
            except BlockingIOError:
                info = os.fstat(fd)
                os.write(contention_fd, f"{info.st_dev}:{info.st_ino}".encode())
        original_flock(fd, flags)

    def lose_ack(path, value):
        durable_write(path, value)
        os._exit(72)

    pid = os.fork()
    if pid == 0:
        try:
            if crash == "before":
                with patch.object(os, "replace", lambda *_: os._exit(71)):
                    auth.serve_mock()
            elif crash == "after":
                with patch.object(one_shot, "_durable_write", lose_ack):
                    auth.serve_mock()
            elif contention_fd is not None:
                with patch.object(fcntl, "flock", observe_flock):
                    auth.serve_mock()
            else:
                auth.serve_mock()
        except Exception as error:
            print(f"fixture writer startup failed: {type(error).__name__}", flush=True)
        os._exit(90)
    try:
        wait_ready(pid)
        yield pid
    finally:
        finished, code = os.waitpid(pid, os.WNOHANG)
        if not finished:
            os.kill(pid, signal.SIGTERM)
            _, code = os.waitpid(pid, 0)
        if crash:
            assert os.waitstatus_to_exitcode(code) == (71 if crash == "before" else 72)


@contextmanager
def case(root, name):
    directory = root / name
    ledger = directory / "mock-ledger" / "level2-budget.json"
    seed(ledger)
    ipc = directory / "ipc"
    ipc.mkdir(mode=0o700)
    with (patch.object(auth, "SOCKET_PATH", ipc / "writer.sock"),
          patch.object(writer, "FIXTURE_PATH", ledger),
          patch.object(guard, "H6_B2_D_SOCKET", str(ipc / "writer.sock"))):
        yield ledger, ledger.with_suffix(".json.lock")


def challenge(conn, client):
    deadline = time.monotonic() + 2
    auth.send(conn, deadline, client=client.hex())
    return deadline, auth.receive(conn, deadline, "server", "proof")


def invalid_packets(path):
    key = auth.read_mock_key()
    initial = path.read_bytes()
    for raw in (b"x" * 4097, b'{"client":"x","v":2,"v":2}', b'{"op":"snapshot","v":1}',
                b'{"client":NaN,"v":2}', b'{"client":' + b"[" * 1500 + b"0" + b"]" * 1500 + b',"v":2}'):
        with connect() as conn:
            conn.send(raw)
            closed(conn)

    client = os.urandom(32)
    with connect() as conn:
        deadline, hello = challenge(conn, client)
        server = bytes.fromhex(hello["server"])
        valid = auth.proof(key, b"C", client, server, encode(ADMIT)).hex()
        auth.send(conn, deadline, request=dict(ADMIT, fingerprint="0" * 64), proof=valid)
        closed(conn)

    for variant in ("wrong-key", "reflected-role", "stale", "nested-duplicate"):
        with connect() as conn:
            deadline, hello = challenge(conn, client)
            fresh = bytes.fromhex(hello["server"])
            assert fresh != server
            if variant == "nested-duplicate":
                conn.send(b'{"proof":"x","request":{"op":"admit","op":"snapshot"},"v":2}')
            else:
                proof = {"wrong-key": auth.proof(os.urandom(32), b"C", client, fresh, encode(ADMIT)).hex(),
                         "reflected-role": hello["proof"], "stale": valid}[variant]
                auth.send(conn, deadline, request=ADMIT, proof=proof)
            closed(conn)

    denied(lambda: auth.call("write", path="/fake", data={}))
    denied(lambda: auth.call("admit", **{**ADMIT_FIELDS, "path": "/fake"}))
    assert auth.call("snapshot")["kill_switch"] and path.read_bytes() == initial
    print("PASS bad version, size, duplicate/nonfinite/recursive JSON, wrong MAC, role reflection, stale packet and request tamper")


def idle_challenge():
    with connect() as conn:
        started = time.monotonic()
        challenge(conn, os.urandom(32))
        conn.settimeout(auth.TIMEOUT + 2)
        closed(conn)
        assert auth.TIMEOUT - 0.25 <= time.monotonic() - started <= auth.TIMEOUT + 2
    assert guard.ledger_summary()["kill_switch"]
    print("PASS idle challenge expires within the exchange deadline")


ADMIT_FIELDS = {key: val for key, val in ADMIT.items() if key != "op"}


def client_rejections():
    key = auth.read_mock_key()
    for scenario in ("wrong-server", "legacy-reply", "missing-proof", "tampered-reply", "other-request-reply"):
        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as server:
            server.bind(str(auth.SOCKET_PATH))
            server.settimeout(2)
            server.listen()
            with ThreadPoolExecutor(1) as pool:
                result = pool.submit(guard.writer_call, "admit", **ADMIT_FIELDS)
                conn, _ = server.accept()
                with conn:
                    deadline = time.monotonic() + 2
                    client = bytes.fromhex(auth.receive(conn, deadline, "client")["client"])
                    nonce = os.urandom(32)
                    signing_key = os.urandom(32) if scenario == "wrong-server" else key
                    auth.send(conn, deadline, server=nonce.hex(), proof=auth.proof(signing_key, b"S", client, nonce).hex())
                    if scenario == "wrong-server":
                        closed(conn)
                    else:
                        packet = auth.receive(conn, deadline, "request", "proof")
                        reply = {"result": True}
                        bound_request = {} if scenario == "other-request-reply" else packet["request"]
                        bound_reply = {"result": False} if scenario == "tampered-reply" else reply
                        payload = hashlib.sha256(encode(bound_request)).digest() + encode(bound_reply)
                        if scenario == "legacy-reply":
                            writer.send(conn, {"v": 1, "result": True})
                        elif scenario == "missing-proof":
                            auth.send(conn, deadline, reply=reply)
                        else:
                            auth.send(conn, deadline, reply=reply, proof=auth.proof(key, b"R", client, nonce, payload).hex())
                denied(lambda: result.result(timeout=3), (RuntimeError,))
        auth.SOCKET_PATH.unlink()
    print("PASS actual Guard rejects wrong server proof and unsigned, legacy, tampered or different-request ACK")


def key_rejections():
    for name in ("absent", "short", "long", "bad-mode", "symlink"):
        with patch.object(auth, "KEY_PATH", auth.KEY_PATH.with_name(name)):
            denied(lambda: guard.writer_call("snapshot"), (RuntimeError,))
            denied(auth.serve_mock, (OSError, ValueError))
    writable = Path("/tmp/writable")
    key_file(writable, 32)
    with patch.object(auth, "KEY_PATH", writable):
        denied(auth.read_mock_key)
    with patch.object(auth, "PROVIDER_KEY_PATH", writable):
        denied(auth.read_mock_key)
    assert not auth.SOCKET_PATH.exists()
    denied(lambda: guard.writer_call("snapshot"))
    env = {**os.environ, "TTD_H6_B2_D_SOCKET": "/opt/ttd/h6-b2d-ipc/writer.sock",
           "TTD_H6_STAGE_A_SOCKET": "/opt/ttd/h6-ipc/writer.sock"}
    completed = subprocess.run([sys.executable, "-B", str(ROOT / "guard.py")], env=env,
                               capture_output=True, timeout=4)
    assert completed.returncode != 0 and b"invalid H6 B2-D mock socket configuration" in completed.stderr
    print("PASS isolated-key policy, missing socket, provider-key sentinel and conflicting fallback config")


def ledger_rejections(path, lock):
    initial = path.read_bytes()
    path.write_bytes(encode({key: value for key, value in json.loads(initial).items() if key != "h6_stage_a_fixture"}))
    denied(auth.serve_mock)
    path.write_bytes(initial)
    lock.chmod(0o644)
    denied(auth.serve_mock)
    lock.chmod(0o600)
    assert not auth.SOCKET_PATH.exists() and path.read_bytes() == initial
    print("PASS writer requires fixture marker and pre-existing root-only lock")


def level2(path):
    spec = importlib.util.spec_from_file_location("level2_fixture", ROOT / "level2-adapter.py")
    adapter = importlib.util.module_from_spec(spec)
    env = {"P0_MODE": "openai", "P0_TOKEN": "fixture-placeholder" * 2, "OPENAI_API_KEY": "fixture-placeholder-only",
           "P0_BUDGET_PATH": str(path), "P0_CALLBACK_URL": "http://n8n-p0-sandbox:5678/fake"}
    with patch.dict(os.environ, env):
        spec.loader.exec_module(adapter)

    def blocked(*_):
        raise AssertionError("test allowed only fake ledger operations")

    adapter.provider_request = blocked
    adapter.send_callback = blocked
    return adapter


def concurrency(path, lock):
    original_lock = lock.stat()
    old = path.open("rb")
    adapter = level2(path)
    actual = adapter.atomic_write
    ready = threading.Event()
    reader, notifier = os.pipe()

    def hold_lock(file, value):
        ready.set()
        assert select.select([reader], [], [], 3)[0], "H6 did not contend on Level 2 lock"
        assert os.read(reader, 256).decode() == f"{original_lock.st_dev}:{original_lock.st_ino}"
        actual(file, value)

    def admit(_):
        try:
            return guard.writer_call("admit", **ADMIT_FIELDS)
        except RuntimeError:
            return False

    try:
        with running_writer(contention_fd=notifier):
            with patch.object(adapter, "atomic_write", hold_lock), ThreadPoolExecutor(5) as pool:
                update = pool.submit(adapter.update_task, "legacy", {"concurrent_level2": True})
                assert ready.wait(2)
                assert list(pool.map(admit, range(4))).count(True) == 1
                update.result(timeout=3)
            summary = guard.ledger_summary()
            saved = path.read_bytes()
            state = json.loads(saved)
            assert summary["attempts"] == 2 and state["tasks"]["legacy"]["concurrent_level2"]
            assert state["tasks"][TASK]["state"] == "inflight"
            assert os.fstat(old.fileno()).st_ino != path.stat().st_ino
            assert json.load(old)["attempts"] == 1 and lock.stat().st_ino == original_lock.st_ino
        saved_inode = path.stat().st_ino
        with running_writer():
            denied(lambda: guard.writer_call("admit", **ADMIT_FIELDS))
        assert (path.read_bytes(), path.stat().st_ino, lock.stat().st_ino) == (saved, saved_inode, original_lock.st_ino)
    finally:
        old.close()
        os.close(reader)
        os.close(notifier)
    print("PASS Level 2 lock device/inode contention, 1/4 signed ACKs, replace, restart replay and rollback")


def http_request(port, path, body=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=6)
    try:
        conn.request("GET" if body is None else "POST", path, body, {
            "Authorization": "Bearer synthetic-guard-token", "Content-Type": "application/json"})
        response = conn.getresponse()
        return response.status, response.read()
    finally:
        conn.close()


@contextmanager
def http_server(handler):
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            yield server.server_port
        finally:
            server.shutdown()
            thread.join()


def guard_transaction(path, lock, phase=""):
    initial = path.read_bytes()
    stable = lock.stat().st_ino
    mock_hits = []

    class SilentGuard(guard.Handler):
        def log_message(self, *_):
            pass

    class Stub(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            current = json.loads(path.read_bytes())
            mock_hits.append((self.rfile.read(int(self.headers["Content-Length"])), current["tasks"][TASK]["state"]))
            payload = encode({"id": "synthetic-response", "model": one_shot.MODEL, "service_tier": "default",
                              "status": "completed", "usage": {"input_tokens": 723, "output_tokens": 20,
                              "total_tokens": 743, "input_tokens_details": {"cached_tokens": 0},
                              "output_tokens_details": {"reasoning_tokens": 0}}})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    with running_writer(phase):
        with (http_server(Stub) as upstream, http_server(SilentGuard) as port,
              patch.multiple(guard, MOCK_URL=f"http://127.0.0.1:{upstream}/fixture",
                             service_token=lambda: "synthetic-guard-token")):
            assert http_request(port, "/healthz")[0] == 200
            status, _ = http_request(port, "/v1/responses", encode(BODY))
            assert status == (503 if phase else 200), status
    assert lock.stat().st_ino == stable
    if phase == "before":
        assert path.read_bytes() == initial and not mock_hits
    elif phase == "after":
        assert not mock_hits and json.loads(path.read_bytes())["tasks"][TASK]["state"] == "inflight"
        saved = path.read_bytes()
        with running_writer():
            denied(lambda: guard.writer_call("admit", **ADMIT_FIELDS))
        assert path.read_bytes() == saved
    else:
        assert mock_hits == [(WIRE, "inflight")]
        assert json.loads(path.read_bytes())["tasks"][TASK]["state"] == "usage_recorded"
    print(f"PASS Guard HTTP {phase or 'success'}: {'zero dispatches, no ACK' if phase else 'one loopback mock dispatch and signed settlement'}")


def tests():
    posture()
    assert (guard.H6_B2_D_SOCKET, guard.H6_STAGE_A_SOCKET) == ("", "")
    key_rejections()
    with tempfile.TemporaryDirectory(dir="/tmp") as isolated:
        root = Path(isolated)
        with case(root, "auth") as (path, lock):
            ledger_rejections(path, lock)
            client_rejections()
            with running_writer():
                assert stat.S_IMODE(auth.SOCKET_PATH.stat().st_mode) == 0o600
                invalid_packets(path)
                idle_challenge()
        with case(root, "concurrent") as (path, lock):
            concurrency(path, lock)
        for phase in ("", "before", "after"):
            with case(root, phase or "success") as (path, lock):
                guard_transaction(path, lock, phase)


if __name__ == "__main__":
    {"init": init, "tests": tests}[sys.argv[1]]()
