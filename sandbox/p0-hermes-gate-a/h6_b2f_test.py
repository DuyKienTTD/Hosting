"""B2-F contract tests. Use only synthetic P0 v1 files and loopback stubs."""

import fcntl
import hashlib
import http.client
import json
import os
import select
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from unittest.mock import patch

import guard
import h6_b2d_mock_test as helpers
import h6_ipc_auth as ipc
import h6_p0 as p0
import h6_provider as provider
import h6_stage_a_test as stage_a
import h6_writer as writer
import one_shot
from mock_contract import encode, usage_from_response

TOKEN = stage_a.TOKEN
BODY = stage_a.BODY
WIRE, DIGEST = guard.freeze_stage_a(BODY)
TASK, KEY_HASH = guard.mock_scope(BODY)
SCOPE = {"task_id": TASK, "key_hash": KEY_HASH, "fingerprint": DIGEST}
ADMIT = {"op": "admit", **SCOPE}
ROOT = Path("/opt/ttd")


def fetch_case(directory, digest=DIGEST):
    directory.mkdir(mode=0o700)
    path = directory / "level2-budget.json"
    lock = path.with_suffix(".json.lock")
    lock.touch(mode=0o600)
    adapter = helpers.level2(path)
    ledger = adapter.new_ledger()
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    ledger.update(kill_switch=True, tasks={"previous": {"state": "complete"}}, b2f_extension=["preserve"])
    ledger["one_shot_permits"] = {TASK: dict(state="ready", model=one_shot.MODEL, key_hash=KEY_HASH,
        fingerprint=digest, expires_at=expiry, provider_scope={
            "approval_sha256": "a" * 64, "counted_fingerprint": digest, "input_tokens": 723,
            "max_output_tokens": 600, "pricing_id": p0.PRICING_ID, "service_tier": "default", "valid_until": expiry,
        })}
    adapter.atomic_write(path, ledger)
    return path, lock, adapter


def must_reject(action):
    helpers.denied(action, (OSError, ValueError, RuntimeError, TypeError, KeyError))


def disabled_and_preconditions(path):
    def trap(*_, **__):
        raise AssertionError("disabled entrypoint touched a resource")

    assert not provider.LIVE_ENABLED and guard.PROVIDER_LANE is None
    with patch.multiple(ipc, read_key=trap), patch.multiple(p0, require_ready=trap, snapshot=trap), \
            patch.object(http.client, "HTTPSConnection", trap), patch.object(os, "open", trap):
        for action in (provider.live_lane, provider.serve_live_writer, provider.provider_key, provider.connect_live):
            must_reject(action)
    for command, extras, expected in (
        (["guard.py"], {provider.PROVIDER_MODE_ENV: "real"}, b"H6_PROVIDER_BUILD_DISABLED"),
        (["guard.py"], {provider.PROVIDER_MODE_ENV: "real", "TTD_H6_B2_D_SOCKET": "/fake"}, b"invalid H6 provider mode"),
        (["guard.py"], {provider.PROVIDER_MODE_ENV: "mock"}, b"invalid H6 provider mode"),
        (["h6_writer.py", "--b2-f-real"], {}, b"H6_PROVIDER_BUILD_DISABLED"),
    ):
        result = subprocess.run([sys.executable, "-B", str(ROOT / command[0]), *command[1:]],
                                env=dict(os.environ, **extras), capture_output=True, timeout=5)
        assert result.returncode != 0 and expected in result.stderr
    # Exercise future preconditions with injected synthetic references only.
    with (patch.multiple(provider, LIVE_ENABLED=True, LIVE_IPC_KEY=path.parent / "absent-key",
                         LIVE_LEDGER=path.parent / "absent-ledger",
                         LEGACY_LEDGER=path.parent / "no-legacy-ledger"),
          patch.object(provider, "has_private_rw_mount", lambda directory: directory == path.parent),
          patch.object(writer, "listen", trap)):
        must_reject(provider.live_client)
        must_reject(provider.serve_live_writer)
        with patch.object(ipc, "read_key", lambda _: os.urandom(32)):
            must_reject(provider.serve_live_writer)
            data = json.loads(path.read_bytes())
            missing = dict(data, one_shot_permits={})
            path.write_bytes(encode(missing))
            try:
                with patch.object(provider, "LIVE_LEDGER", path):
                    must_reject(provider.serve_live_writer)
            finally:
                path.write_bytes(encode(data))
    with patch.object(provider, "LIVE_ENABLED", True), patch.object(http.client, "HTTPSConnection") as https:
        provider.connect_live()
        assert https.call_args.args == (provider.PROVIDER_PROXY, 8888)
        context = https.call_args.kwargs["context"]
        assert context.check_hostname and context.verify_mode == provider.ssl.CERT_REQUIRED
        https.return_value.set_tunnel.assert_called_once_with(provider.PROVIDER_HOST, 443)
        https.return_value.connect.assert_not_called()
    print("PASS hard lock/isolated references and CONNECT/TLS configuration (no network calls)")


@contextmanager
def running_writer(address, path, key, crash="", contention=None):
    original_write, original_flock = one_shot._durable_write, fcntl.flock

    def durable(target, value):
        if crash == "before":
            with patch.object(os, "replace", lambda *_: os._exit(71)):
                original_write(target, value)
        original_write(target, value)
        if crash == "after":
            os._exit(72)

    def monitor(fd, flags):
        if contention is not None and flags == fcntl.LOCK_EX:
            try:
                original_flock(fd, flags | fcntl.LOCK_NB)
                return
            except BlockingIOError:
                info = os.fstat(fd)
                os.write(contention, f"{info.st_dev}:{info.st_ino}".encode())
        original_flock(fd, flags)

    pid = os.fork()
    if pid == 0:
        with patch.object(one_shot, "_durable_write", durable), patch.object(fcntl, "flock", monitor):
            writer.listen(address, path, 0, 0, 0o700, 0o600,
                          lambda conn, target: ipc.handle_exchange(conn, target, key, provider.LIVE_DOMAIN, p0.dispatch))
        os._exit(92)
    try:
        limit = time.monotonic() + 2
        while time.monotonic() < limit:
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as probe:
                    probe.connect(str(address))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                time.sleep(0.01)
        else:
            raise AssertionError("writer did not listen")
        yield pid
    finally:
        finished, code = os.waitpid(pid, os.WNOHANG)
        if not finished:
            os.kill(pid, signal.SIGTERM)
            _, code = os.waitpid(pid, 0)
        if crash:
            assert os.waitstatus_to_exitcode(code) == (71 if crash == "before" else 72)


def rejected_ledger_inputs(path, lock, rpc):
    assert rpc({"op": "snapshot"})["kill_switch"]
    valid = path.read_bytes()
    bad_edits = [
        lambda value: value.update(kill_switch=False),
        lambda value: value.update(h6_stage_a_fixture=True),
        lambda value: value.update(actual_usd=0.1),
        lambda value: value.update(reserved_usd=0.049),
        lambda value: value.update(attempts=5),
        lambda value: value["one_shot_permits"][TASK].update(key_hash="0" * 64),
        lambda value: value["one_shot_permits"][TASK].update(mock_input_tokens=723),
        lambda value: value["one_shot_permits"][TASK]["provider_scope"].update(counted_fingerprint="0" * 64),
        lambda value: value["one_shot_permits"][TASK]["provider_scope"].update(input_tokens=4001),
        lambda value: value["one_shot_permits"][TASK]["provider_scope"].update(pricing_id="unapproved"),
        lambda value: value["one_shot_permits"][TASK]["provider_scope"].update(valid_until="2020-01-01T00:00:00+00:00"),
    ]
    for edit in bad_edits:
        modified = json.loads(valid)
        edit(modified)
        bad = encode(modified)
        path.write_bytes(bad)
        must_reject(lambda: rpc(ADMIT))
        assert path.read_bytes() == bad
    path.write_bytes(valid)
    lock.chmod(0o644)
    must_reject(lambda: rpc(ADMIT))
    assert lock.stat().st_mode & 0o777 == 0o644
    lock.chmod(0o600)
    lock.rename(lock.with_suffix(".old"))
    try:
        must_reject(lambda: rpc(ADMIT))
        assert not lock.exists()
    finally:
        lock.with_suffix(".old").rename(lock)
    for request in (dict(ADMIT, path="/fake"), {"op": "reset"}, dict(ADMIT, fingerprint="0" * 64)):
        must_reject(lambda: rpc(request))
    assert path.read_bytes() == valid
    print("PASS rejected fixture marker, scope/count/pricing/expiry/caps, missing or unsafe lock and generic operations")


def reject_cross_request_ack(address, key):
    def forbidden_connection():
        raise AssertionError("wrong ACK opened a provider connection")

    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
        listener.bind(str(address))
        listener.listen()
        listener.settimeout(2)
        rpc = lambda request: ipc.exchange(address, key, provider.LIVE_DOMAIN, request)
        lane = provider.Lane(rpc, forbidden_connection, lambda: "synthetic-stub-credential")
        with ThreadPoolExecutor(1) as pool:
            result = pool.submit(lane.run, BODY, guard.freeze_stage_a, guard.mock_scope)
            conn, _ = listener.accept()
            with conn:
                limit = time.monotonic() + 2
                client = bytes.fromhex(ipc.receive(conn, limit, "client")["client"])
                server = os.urandom(32)
                sign = lambda role, data=b"": ipc.proof(key, role, client, server, data, domain=provider.LIVE_DOMAIN).hex()
                ipc.send(conn, limit, server=server.hex(), proof=sign(b"S"))
                assert ipc.receive(conn, limit, "request", "proof")["request"] == ADMIT
                reply = {"result": True}
                unrelated = hashlib.sha256(encode({"op": "snapshot"})).digest() + encode(reply)
                ipc.send(conn, limit, reply=reply, proof=sign(b"R", unrelated))
            must_reject(lambda: result.result(timeout=3))
    address.unlink()


def reject_nonce_replay(address, key):
    client = os.urandom(32)
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as first:
        first.connect(str(address))
        limit, handshake = helpers.challenge(first, client)
        old = bytes.fromhex(handshake["server"])
        signed = ipc.proof(key, b"C", client, old, encode({"op": "snapshot"}), domain=provider.LIVE_DOMAIN)
        ipc.send(first, limit, request={"op": "snapshot"}, proof=signed.hex())
        assert ipc.receive(first, limit, "reply", "proof")["reply"]["result"]["kill_switch"]
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as fresh:
        fresh.connect(str(address))
        limit, handshake = helpers.challenge(fresh, client)
        assert bytes.fromhex(handshake["server"]) != old
        ipc.send(fresh, limit, request={"op": "snapshot"}, proof=signed.hex())
        helpers.closed(fresh)


def response_payload(mode):
    count = 724 if mode == "usage-above-count" else 723
    status = "incomplete" if mode == "incomplete" else "completed"
    response = {"id": "synthetic-only", "model": one_shot.MODEL, "service_tier": "default", "status": status,
                "usage": {"input_tokens": count, "output_tokens": 20, "total_tokens": count + 20,
                          "input_tokens_details": {"cached_tokens": 0},
                          "output_tokens_details": {"reasoning_tokens": 0}}}
    event = "response.created" if mode == "missing-terminal" else f"response.{status}"
    if mode == "json":
        return encode(response)
    return b"data: " + encode({"type": event, "response": response}) + b"\n\n"


@contextmanager
def guard_http(rpc, stub_port, *, timeout=1):
    lane = provider.Lane(rpc, lambda: http.client.HTTPConnection("127.0.0.1", stub_port, timeout=timeout),
                         lambda: "synthetic-stub-credential")
    with (patch.multiple(guard, PROVIDER_LANE=lane, service_token=lambda: TOKEN, MOCK_URL=f"http://127.0.0.1:{stub_port}/fallback"),
          helpers.http_server(guard.Handler) as port):
        yield port


def one_case(root, mode):
    body = dict(BODY, stream=False) if mode == "json" else BODY
    expected_wire, expected_digest = guard.freeze_stage_a(body)
    scope = dict(SCOPE, fingerprint=expected_digest)
    path, lock, adapter = fetch_case(root, expected_digest)
    original = path.read_bytes()
    held = lock.stat()
    key = os.urandom(32)
    address = root / "writer.sock"
    rpc = lambda request: ipc.exchange(address, key, provider.LIVE_DOMAIN, request)
    hits = []
    pid = None
    crash = {"crash-before": "before", "crash-after-reserve": "after"}.get(mode, "")
    notification, send_notification = os.pipe() if mode == "concurrent" else (None, None)

    class Stub(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_):
            pass

        def do_GET(self):
            hits.append((self.path, b""))
            self.send_error(405)

        def do_POST(self):
            wire = self.rfile.read(int(self.headers["Content-Length"]))
            hits.append((self.path, wire))
            data = json.loads(path.read_bytes())
            assert data["kill_switch"] is True and data["one_shot_permits"][TASK]["state"] == "consumed"
            assert data["tasks"][TASK]["state"] == "inflight" and data["reserved_usd"] == one_shot.RESERVE_USD
            assert data["tasks"][TASK]["fingerprint"] == hashlib.sha256(wire).hexdigest() == expected_digest
            assert self.headers["Authorization"] == "Bearer synthetic-stub-credential"
            if mode == "redirect":
                self.send_response(302)
                self.send_header("Location", "/redirect-target")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if mode == "http-error":
                self.send_error(429)
                return
            if mode == "writer-dies-after-post":
                os.kill(pid, signal.SIGTERM)
            if mode == "deadline":
                time.sleep(0.35)
                self.close_connection = True
                return
            payload = response_payload(mode)
            self.send_response(200)
            self.send_header("Content-Type", "application/json" if mode == "json" else "text/event-stream")
            if mode == "callback":
                self.send_header("Transfer-Encoding", "chunked")
            else:
                self.send_header("Content-Length", str(len(payload) + (9 if mode == "truncated" else 0)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True
            if mode == "callback":
                self.wfile.write(f"{len(payload):x}\r\n".encode() + payload + b"\r\n0\r\n\r\n")
            else:
                self.wfile.write(payload)

    def submit(port):
        return stage_a.http_call(port, "/v1/responses", encode(body))[0]

    try:
        if mode == "concurrent":
            reject_cross_request_ack(address, key)
        with (running_writer(address, path, key, crash, send_notification) as pid,
              helpers.http_server(Stub) as stub_port, guard_http(rpc, stub_port) as port):
            if mode == "concurrent":
                rejected_ledger_inputs(path, lock, rpc)
                must_reject(lambda: ipc.exchange(address, key, ipc.DOMAIN, ADMIT))
                must_reject(lambda: ipc.exchange(address, os.urandom(32), provider.LIVE_DOMAIN, ADMIT))
                reject_nonce_replay(address, key)
                print("PASS B2-F domain/key, replay and cross-request ACK rejected before transport")
                for bad in (dict(BODY, instructions="tampered"), dict(BODY, tools=[]), dict(BODY, max_output_tokens=601)):
                    assert stage_a.http_call(port, "/v1/responses", encode(bad))[0] == 503
                assert not hits and path.read_bytes() == original

                ready = threading.Event()
                original_atomic = adapter.atomic_write

                def wait(file, value):
                    ready.set()
                    assert select.select([notification], [], [], 2)[0]
                    assert os.read(notification, 512).decode() == f"{held.st_dev}:{held.st_ino}"
                    original_atomic(file, value)

                with patch.object(adapter, "atomic_write", wait), ThreadPoolExecutor(5) as pool:
                    prior = pool.submit(adapter.update_task, "previous", {"updated_by_level2": True})
                    assert ready.wait(2)
                    assert sorted(pool.map(lambda _: submit(port), range(4))) == [200, 503, 503, 503]
                    prior.result(timeout=3)
            elif mode == "callback":
                callback_test(port)
            elif mode == "json":
                assert submit(port) == 200
            elif mode == "deadline":
                with patch.object(provider, "RESPONSE_TIMEOUT", 0.15):
                    assert submit(port) == 503
            else:
                assert submit(port) == 503
            expected_hits = 0 if crash else 1
            assert hits == [(provider.RESPONSES_PATH, expected_wire)] * expected_hits
            usage_recorded = mode in ("concurrent", "callback", "json", "incomplete")
            state = json.loads(path.read_bytes())
            if mode == "crash-before":
                assert path.read_bytes() == original
            elif usage_recorded:
                usage = usage_from_response(response_payload(mode), mode != "json")
                assert state["actual_usd"] == float(usage["estimated_cost_usd"])
                assert state["tasks"][TASK]["invoice_status"] == "unreconciled" and state["tasks"][TASK]["state"] == "usage_recorded"
                cached = path.read_bytes()
                exact = {"op": "settle", **scope, "outcome": "usage_recorded", "usage": usage}
                assert rpc(exact) is True and path.read_bytes() == cached
                must_reject(lambda: rpc(dict(exact, usage=dict(usage, input_tokens=724))))
                must_reject(lambda: rpc(dict(exact, fingerprint="0" * 64)))
                assert path.read_bytes() == cached
                if mode == "concurrent":
                    assert state["tasks"]["previous"]["updated_by_level2"] and state["b2f_extension"] == ["preserve"]
            else:
                expected = "inflight" if mode in ("crash-after-reserve", "writer-dies-after-post") else "outcome_unknown"
                assert state["tasks"][TASK]["state"] == expected and state["actual_usd"] == 0
            if mode != "crash-before":
                assert state["attempts"] == 1 and state["reserved_usd"] == one_shot.RESERVE_USD
                assert state["one_shot_permits"][TASK]["state"] == "consumed" and state["kill_switch"] is True
        saved = path.read_bytes(), path.stat().st_ino, lock.stat().st_ino
        if mode != "crash-before":
            with running_writer(address, path, key):
                must_reject(lambda: rpc({"op": "admit", **scope}))
        assert (path.read_bytes(), path.stat().st_ino, lock.stat().st_ino) == saved and saved[2] == held.st_ino
    finally:
        if notification is not None:
            os.close(notification)
            os.close(send_notification)
    print(f"PASS {mode}: {len(hits)} loopback POST(s), stable lock and reserve/replay invariants")


def callback_test(guard_port):
    notifications = []

    class Callback(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            accepted = self.headers.get("Authorization") == f"Bearer {TOKEN}"
            if accepted:
                notifications.append((self.path, payload))
            self.send_response(200 if accepted else 401)
            self.end_headers()
            self.wfile.write(b"{}")

    with helpers.http_server(Callback) as callback_port:
        stage_a.check_callback(guard_port, callback_port, notifications)
    assert len(notifications) == 1


def main():
    helpers.posture()
    with tempfile.TemporaryDirectory(prefix="b2f-", dir="/tmp") as scratch:
        root = Path(scratch)
        path, _, _ = fetch_case(root / "config")
        disabled_and_preconditions(path)
        for mode in ("concurrent", "callback", "json", "crash-before", "crash-after-reserve", "writer-dies-after-post",
                     "redirect", "http-error", "deadline", "truncated", "missing-terminal", "usage-above-count", "incomplete"):
            one_case(root / mode, mode)
    print("B2_F_SOURCE_MOCK_PASS")


if __name__ == "__main__":
    main()
