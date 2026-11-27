"""Synthetic B2-G actors. CONNECT can relay only to the explicit fake TLS service."""

import hashlib
import http.client
import json
import os
import select
import socket
import socketserver
import ssl
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOSTS = {
    "ok": "ok.b2g.invalid", "chunked": "chunked.b2g.invalid", "wrong-ca": "wrong-ca.b2g.invalid",
    "wrong-host": "wrong-host.outside.invalid", "expired": "expired.b2g.invalid",
    "reject": "reject.b2g.invalid", "drop": "drop.b2g.invalid", "handshake": "handshake.b2g.invalid",
    "redirect": "redirect.b2g.invalid", "slow": "slow.b2g.invalid", "short": "short.b2g.invalid",
    "bad-sse": "bad-sse.b2g.invalid", "bad-chunk": "bad-chunk.b2g.invalid",
}
CASE_BY_HOST = {host: case for case, host in HOSTS.items()}
NO_POST = {"wrong-ca", "wrong-host", "expired", "reject", "drop", "handshake"}
SUCCESS = {"ok", "chunked"}
BLOCKED = "unapproved.b2g.invalid"
PROXY, BACKEND = "b2g-proxy", "b2g-provider"
PROXY_PORT, TLS_PORT = 8888, 8443
AUDIT = Path("/audit/events.jsonl")
LEDGER, SOCKETS = Path("/fake-ledger"), Path("/ipc")
KEYFILE = Path("/ipc-auth/ipc.key")
CREDENTIAL = "b2g-synthetic-provider-fixture"
TOKEN = "b2g-synthetic-guard-fixture"
BODY = {"model": "gpt-6-luna", "stream": True, "reasoning": {"effort": "none"},
        "input": [{"role": "user", "content": "task_id=b2g-fake; correlation_id=b2g; channel=ads; spend=1.00; clicks=1"}]}
MODELS_RESPONSE = {"id": "fixture-b2g-response", "model": "gpt-6-luna", "service_tier": "default", "status": "completed",
                   "usage": {"input_tokens": 723, "output_tokens": 20, "total_tokens": 743,
                             "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 0}}}


def audit(event, case, **fields):
    payload = json.dumps({"event": event, "case": case, **fields}, separators=(",", ":")).encode() + b"\n"
    fd = os.open(AUDIT, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        assert os.write(fd, payload) == len(payload)
    finally:
        os.close(fd)


def posture(role):
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines())
    assert (os.geteuid(), os.getegid()) == (0, 0)
    assert all(int(status[key], 16) == 0 for key in ("CapEff", "CapPrm", "CapInh", "CapBnd", "CapAmb"))
    assert int(status["NoNewPrivs"]) == 1 and os.statvfs("/").f_flag & os.ST_RDONLY
    assert not any(line.split()[1] == "00000000" for line in Path("/proc/net/route").read_text().splitlines()[1:])
    assert not any(os.path.lexists(path) for path in ("/run/docker.sock", "/var/run/docker.sock",
        "/opt/ttd/ledger/level2-budget.json", "/opt/ttd/p0-ledger", "/run/secrets/openai_provider_api_key"))
    assert LEDGER.exists() == (role == "writer")
    assert SOCKETS.exists() == (role in ("writer", "guard"))
    assert KEYFILE.exists() == (role in ("writer", "guard"))
    assert Path("/tls").exists() == (role == "provider")
    assert Path("/trust").exists() == (role == "guard")
    if role == "writer":
        assert {item.name for item in Path("/sys/class/net").iterdir()} == {"lo"}
    if role in ("guard", "writer"):
        assert os.statvfs(KEYFILE).f_flag & os.ST_RDONLY


class Proxy(socketserver.StreamRequestHandler):
    rbufsize = 0

    def handle(self):
        self.connection.settimeout(2)
        request = self.rfile.readline(256).decode("ascii").split()
        if len(request) != 3 or request[0] != "CONNECT" or request[2] not in ("HTTP/1.0", "HTTP/1.1"):
            return
        for _ in range(16):
            if self.rfile.readline(512) == b"\r\n":
                break
        else:
            return
        authority = request[1]
        host, separator, port = authority.rpartition(":")
        case = CASE_BY_HOST.get(host) if separator and port == "443" else None
        audit("connect", case or "blocked")
        if case is None or case == "reject":
            self.connection.sendall(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n")
            return
        if case == "drop":
            return
        if case == "handshake":
            self.connection.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
            time.sleep(2)
            return
        # Deliberately ignore hostname for routing. No generic forward-proxy path.
        with socket.create_connection((BACKEND, TLS_PORT), timeout=2) as upstream:
            self.connection.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
            relay(self.connection, upstream)


def relay(client, upstream):
    deadline = time.monotonic() + 6
    remaining_bytes = 1024 * 1024
    sockets = {client: upstream, upstream: client}
    try:
        while remaining_bytes > 0 and time.monotonic() < deadline:
            readable, _, _ = select.select(list(sockets), [], [], max(0, deadline - time.monotonic()))
            for source in readable:
                data = source.recv(min(16_384, remaining_bytes))
                if not data:
                    return
                remaining_bytes -= len(data)
                sockets[source].sendall(data)
    except OSError:
        return


class FakeTLS(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_):
        pass

    def do_GET(self):
        audit("unexpected_http", "unexpected")
        self.send_error(405)

    def do_POST(self):
        sni = self.connection.b2g_sni
        case = CASE_BY_HOST[sni]
        length = int(self.headers["Content-Length"])
        assert 0 < length <= 4096
        data = self.rfile.read(length)
        if (self.path != "/v1/responses" or self.headers.get("Host", "").split(":")[0] != sni
                or self.headers.get("Authorization") != f"Bearer {CREDENTIAL}"):
            audit("unexpected_http", case)
            self.send_error(400)
            return
        audit("post", case, digest=hashlib.sha256(data).hexdigest(), size=len(data),
              tls=self.connection.version())
        self.close_connection = True
        if case == "redirect":
            self.send_response(302)
            self.send_header("Location", "/should-not-follow")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        event = "response.created" if case == "bad-sse" else "response.completed"
        payload = b"data: " + json.dumps({"type": event, "response": MODELS_RESPONSE}).encode() + b"\n\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Connection", "close")
        if case in ("chunked", "bad-chunk"):
            self.send_header("Transfer-Encoding", "chunked")
        else:
            self.send_header("Content-Length", str(len(payload) + (5 if case == "short" else 0)))
        self.end_headers()
        try:
            if case == "slow":
                for char in payload[:24]:
                    self.wfile.write(bytes([char]))
                    audit("drip", case)
                    time.sleep(0.1)
            elif case == "bad-chunk":
                self.wfile.write(b"z\r\ninvalid\r\n")
            elif case == "chunked":
                self.wfile.write(f"{len(payload):x}\r\n".encode() + payload + b"\r\n0\r\n\r\n")
            else:
                self.wfile.write(payload)
        except OSError:
            return


def tls_server():
    def context(name):
        value = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        value.minimum_version = ssl.TLSVersion.TLSv1_2
        value.load_cert_chain(f"/tls/{name}.crt", f"/tls/{name}.key")
        return value

    primary, expired = context("valid"), context("expired")

    def select_cert(conn, name, _):
        if name not in CASE_BY_HOST:
            return ssl.ALERT_DESCRIPTION_UNRECOGNIZED_NAME
        conn.b2g_sni = name
        if name == HOSTS["expired"]:
            conn.context = expired

    primary.set_servername_callback(select_cert)
    with ThreadingHTTPServer(("0.0.0.0", TLS_PORT), FakeTLS) as server:
        server.socket = primary.wrap_socket(server.socket, server_side=True)
        server.serve_forever()


def writer():
    import guard
    import h6_ipc_auth as ipc
    import h6_p0 as p0
    import h6_provider as provider
    import h6_writer
    import one_shot

    assert not provider.LIVE_ENABLED
    key = ipc.read_key(KEYFILE)
    _, digest = guard.freeze_stage_a(BODY)
    task, key_hash = guard.mock_scope(BODY)
    expires = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    permit = {"state": "ready", "model": one_shot.MODEL, "key_hash": key_hash, "fingerprint": digest,
              "expires_at": expires, "provider_scope": {"approval_sha256": "a" * 64, "counted_fingerprint": digest,
              "input_tokens": 723, "max_output_tokens": 600, "service_tier": "default", "pricing_id": p0.PRICING_ID,
              "valid_until": expires}}
    for case in HOSTS:
        socket_directory = SOCKETS / case
        socket_directory.mkdir(mode=0o700)
        folder = LEDGER / case
        folder.mkdir(mode=0o700)
        path = folder / "level2-budget.json"
        path.with_suffix(".json.lock").touch(mode=0o600)
        one_shot._durable_write(path, {"schema_version": 1, "model": one_shot.MODEL, "max_calls": one_shot.MAX_CALLS,
            "caps_usd": one_shot.CAPS, "attempts": 0, "reserved_usd": 0.0, "actual_usd": 0.0, "kill_switch": True,
            "days": {}, "tasks": {}, "one_shot_permits": {task: permit}})
        p0.require_ready(path)
        if os.fork() == 0:
            h6_writer.listen(socket_directory / "w.sock", path, 0, 0, 0o700, 0o600,
                              lambda conn, target: ipc.handle_exchange(conn, target, key, provider.LIVE_DOMAIN, p0.dispatch))
            os._exit(1)
    dead, status = os.wait()
    raise RuntimeError(f"fixture writer exited: {dead}, {status}")


def guard_matrix(provider_ip, outside_ips):
    from ipaddress import ip_address
    from unittest.mock import patch
    import guard
    import h6_ipc_auth as ipc
    import h6_provider as provider

    assert not provider.LIVE_ENABLED
    key = ipc.read_key(KEYFILE)
    wire, digest = guard.freeze_stage_a(BODY)
    # No live DNS lookups. Probe only fixture addresses and a documentation-only address.
    for host, port in [(provider_ip, TLS_PORT), ("192.0.2.1", 443)] + [(ip, PROXY_PORT) for ip in outside_ips]:
        assert ip_address(host).version == 4
        try:
            with socket.create_connection((host, port), timeout=0.35):
                raise AssertionError("unexpected network path")
        except OSError:
            pass
    with socket.create_connection((PROXY, PROXY_PORT), timeout=1.5) as conn:
        conn.sendall(f"CONNECT {BLOCKED}:443 HTTP/1.1\r\nHost: {BLOCKED}:443\r\n\r\n".encode())
        assert conn.recv(512).startswith(b"HTTP/1.1 403")
    print(f"PASS NO_BYPASS direct fake TLS, reserved non-project address, {len(outside_ips)} baseline proxy IPs, unapproved authority", flush=True)

    def submit(port):
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=6)
        try:
            conn.request("POST", "/v1/responses", body=json.dumps(BODY).encode(), headers={
                "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
            with conn.getresponse() as response:
                return response.status, response.read()
        finally:
            conn.close()

    for case, hostname in HOSTS.items():
        address = SOCKETS / case / "w.sock"
        assert address.is_socket()
        rpc = lambda message: ipc.exchange(address, key, provider.LIVE_DOMAIN, message)
        trust = "wrong-ca.pem" if case == "wrong-ca" else "ca.pem"
        context = ssl.create_default_context(cafile=f"/trust/{trust}")
        assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname and context.cert_store_stats()["x509_ca"] == 1
        factory_calls, errors = [], []
        deadline_fired = threading.Event()
        abort = provider.abort

        def observe_deadline(sock):
            deadline_fired.set()
            abort(sock)

        def tunnel():
            factory_calls.append(case)
            summary = rpc({"op": "snapshot"})
            assert summary["kill_switch"] and summary["attempts"] == 1 and summary["reserved_usd"] == 0.0035
            conn = http.client.HTTPSConnection(PROXY, PROXY_PORT, context=context, timeout=0.65 if case == "handshake" else 2)
            conn.set_tunnel(hostname, 443)
            return conn

        class ObservedLane(provider.Lane):
            def run(self, *args):
                try:
                    return super().run(*args)
                except provider.UnknownOutcome as exc:
                    errors.append(exc.__cause__)
                    raise

        def forbid_mock(*_):
            raise AssertionError("provider lane fell back to legacy mock")

        lane = ObservedLane(rpc, tunnel, lambda: CREDENTIAL)
        with (patch.multiple(guard, PROVIDER_LANE=lane, service_token=lambda: TOKEN),
              patch.object(guard.Handler, "run_one_shot_mock", forbid_mock),
              patch.object(provider, "RESPONSE_TIMEOUT", 0.8 if case == "slow" else 4),
              patch.object(provider, "abort", observe_deadline),
              ThreadingHTTPServer(("127.0.0.1", 0), guard.Handler) as entry):
            thread = threading.Thread(target=entry.serve_forever, daemon=True)
            thread.start()
            try:
                started = time.monotonic()
                if case == "ok":
                    with ThreadPoolExecutor(4) as pool:
                        replies = list(pool.map(lambda _: submit(entry.server_port), range(4)))
                    assert sorted(status for status, _ in replies) == [200, 503, 503, 503]
                else:
                    status, _ = submit(entry.server_port)
                    assert status == (200 if case in SUCCESS else 503)
                elapsed = time.monotonic() - started
                assert submit(entry.server_port)[0] == 503 and factory_calls == [case]
            finally:
                entry.shutdown()
                thread.join()
        if case in SUCCESS:
            assert not errors
        else:
            error, = errors
            if case in ("wrong-ca", "wrong-host", "expired"):
                expected = {"wrong-ca": {20, 21}, "wrong-host": {62}, "expired": {10}}
                assert isinstance(error, ssl.SSLCertVerificationError) and error.verify_code in expected[case], repr(error)
            elif case == "handshake":
                assert isinstance(error, TimeoutError) and 0.50 <= elapsed < 1.75, (repr(error), elapsed)
            elif case == "slow":
                # A timer shutdown during a TLS read can surface as timeout,
                # truncation or an SSL write to the just-closed socket.
                assert deadline_fired.is_set() and 0.70 <= elapsed < 1.75, (repr(error), elapsed)
                assert isinstance(error, (OSError, http.client.IncompleteRead)), repr(error)
            elif case == "reject":
                assert isinstance(error, OSError) and "403" in str(error)
            elif case == "drop":
                assert isinstance(error, (http.client.RemoteDisconnected, EOFError)) or (
                    isinstance(error, OSError) and "EOF" in str(error).upper())
            else:
                assert isinstance(error, (ValueError, http.client.IncompleteRead)), repr(error)
            print(f"PASS {case}: {type(error).__name__}, {elapsed:.3f}s, replay blocked", flush=True)
    print(f"PASS B2G_GUARD wire_sha256={digest} bytes={len(wire)}", flush=True)


if __name__ == "__main__":
    role, *args = sys.argv[1:]
    posture(role)
    if role == "proxy":
        with socketserver.ThreadingTCPServer(("0.0.0.0", PROXY_PORT), Proxy) as server:
            server.serve_forever()
    elif role == "provider":
        tls_server()
    elif role == "writer":
        writer()
    elif role == "guard":
        guard_matrix(args[0], args[1:])
    else:
        raise SystemExit("unexpected fixture role")
