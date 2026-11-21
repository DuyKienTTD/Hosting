"""One-shot Responses transport and a source-locked provider lane."""

import hashlib
import http.client
import os
import re
import socket
import ssl
import stat
import threading
from datetime import datetime, timezone
from pathlib import Path

import h6_ipc_auth as ipc
import h6_p0 as p0
import h6_writer
from mock_contract import MAX_INPUT, MAX_OUTPUT, MAX_RESPONSE_BYTES, usage_from_response

# Deliberately has no environment override. Changing it requires a new reviewed build.
LIVE_ENABLED = False
PROVIDER_MODE_ENV = "TTD_H6_PROVIDER_MODE"
LIVE_LEDGER = Path("/opt/ttd/p0-ledger/level2-budget.json")
LEGACY_LEDGER = Path("/opt/ttd/ledger/level2-budget.json")
LIVE_SOCKET = Path("/opt/ttd/h6-b2f-live-ipc/writer.sock")
LIVE_IPC_KEY = Path("/run/h6-b2f-live-auth/ipc.key")
LIVE_DOMAIN = b"ttd-h6-b2f-provider-ipc-v2\x00"
PROVIDER_HOST = "api.openai.com"
PROVIDER_PROXY = "provider-egress"
PROVIDER_PROXY_PORT = 8888
RESPONSES_PATH = "/v1/responses"
CONNECT_TIMEOUT = 5
RESPONSE_TIMEOUT = 45
FAILURES = (OSError, ValueError, RuntimeError, KeyError, TypeError, AttributeError, http.client.HTTPException)


class UnknownOutcome(RuntimeError):
    pass


def require_live_build():
    if LIVE_ENABLED is not True:
        raise RuntimeError("H6_PROVIDER_BUILD_DISABLED")
    if (os.geteuid(), os.getegid()) != (0, 0):
        raise PermissionError("H6_PROVIDER_IDENTITY")


def live_client():
    require_live_build()
    key = ipc.read_key(LIVE_IPC_KEY)
    return lambda request: ipc.exchange(LIVE_SOCKET, key, LIVE_DOMAIN, request)


def has_private_rw_mount(path):
    entries = [line.split(" - ", 1)[0].split() for line in Path("/proc/self/mountinfo").read_text().splitlines()]
    matches = [entry for entry in entries if entry[4] == str(path)]
    return (len(matches) == 1 and "rw" in matches[0][5].split(",")
            and not any(field.startswith(("shared:", "master:")) for field in matches[0][6:]))


def serve_live_writer():
    require_live_build()
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines())
    if (os.path.lexists(ipc.PROVIDER_KEY_PATH) or os.path.lexists(LEGACY_LEDGER)
            or os.path.lexists("/run/docker.sock") or os.path.lexists("/var/run/docker.sock")
            or set(os.listdir("/sys/class/net")) != {"lo"}
            or not os.statvfs("/").f_flag & os.ST_RDONLY
            or any(int(status[cap], 16) for cap in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"))
            or int(status["NoNewPrivs"]) != 1):
        raise PermissionError("H6_PROVIDER_WRITER_ISOLATION")
    key = ipc.read_key(LIVE_IPC_KEY)
    if not has_private_rw_mount(LIVE_LEDGER.parent):
        raise PermissionError("H6_PROVIDER_LEDGER_BIND_REQUIRED")
    p0.require_ready(LIVE_LEDGER)
    h6_writer.listen(LIVE_SOCKET, LIVE_LEDGER, 0, 0, 0o700, 0o600,
                     lambda conn, path: ipc.handle_exchange(conn, path, key, LIVE_DOMAIN, p0.dispatch))


def provider_key():
    require_live_build()
    fd = os.open(ipc.PROVIDER_KEY_PATH, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if ((info.st_mode, info.st_uid, info.st_gid, info.st_nlink) != (stat.S_IFREG | 0o600, 0, 0, 1)
                or not os.fstatvfs(stream.fileno()).f_flag & os.ST_RDONLY):
            raise PermissionError("H6_PROVIDER_KEY_POLICY")
        raw = stream.read(514)
    key = raw.removesuffix(b"\n")
    if not re.fullmatch(rb"[!-~]{20,512}", key):
        raise ValueError("H6_PROVIDER_KEY_FORMAT")
    return key.decode("ascii")


def connect_live():
    require_live_build()
    connection = http.client.HTTPSConnection(PROVIDER_PROXY, PROVIDER_PROXY_PORT, timeout=CONNECT_TIMEOUT,
                                            context=ssl.create_default_context())
    connection.set_tunnel(PROVIDER_HOST, 443)
    return connection


def abort(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass


def post_once(connection, key, wire, streaming, send_by):
    """One explicit connect and POST. Accept only a complete bounded HTTP 200."""
    timer = None
    try:
        connection.connect()
        if datetime.now(timezone.utc) >= send_by:
            raise TimeoutError("H6_PROVIDER_QUOTE_EXPIRED")
        # A TCP timeout alone resets on progress. Interrupt a slow-drip response too.
        connection.sock.settimeout(RESPONSE_TIMEOUT)
        timer = threading.Timer(RESPONSE_TIMEOUT, abort, (connection.sock,))
        timer.daemon = True
        timer.start()
        connection.request("POST", RESPONSES_PATH, body=wire, headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json",
            "Accept-Encoding": "identity", "Connection": "close",
        })
        with connection.getresponse() as response:
            headers = response.headers
            content_type = "text/event-stream" if streaming else "application/json"
            if (response.status != 200 or headers.get_content_type() != content_type
                    or len(headers.get_all("Content-Type", [])) != 1
                    or headers.get("Content-Encoding", "identity") != "identity"):
                raise ValueError("H6_PROVIDER_HTTP_RESPONSE")
            lengths = headers.get_all("Content-Length", [])
            transfers = headers.get_all("Transfer-Encoding", [])
            if response.chunked and len(transfers) == 1 and transfers[0].lower() == "chunked" and not lengths:
                length = None
            elif not transfers and len(lengths) == 1 and re.fullmatch(r"[0-9]{1,9}", lengths[0]):
                length = int(lengths[0])
                if not 0 < length <= MAX_RESPONSE_BYTES:
                    raise ValueError("H6_PROVIDER_BODY_SIZE")
            else:
                raise ValueError("H6_PROVIDER_BODY_FRAMING")
            payload = response.read(MAX_RESPONSE_BYTES + 1)
            if not payload or len(payload) > MAX_RESPONSE_BYTES or (length is not None and len(payload) != length):
                raise ValueError("H6_PROVIDER_BODY_SIZE_OR_TRUNCATION")
            return content_type, payload
    finally:
        if timer is not None:
            timer.cancel()
        connection.close()


class Lane:
    """No default transport. Tests supply only a synthetic loopback connection."""

    def __init__(self, writer, connection_factory, credential):
        self.writer = writer
        self.connection_factory = connection_factory
        self.credential = credential

    def snapshot(self):
        result = self.writer({"op": "snapshot"})
        if not isinstance(result, dict) or set(result) != h6_writer.SUMMARY_FIELDS or result["kill_switch"] is not True:
            raise RuntimeError("H6_PROVIDER_SNAPSHOT")
        return result

    def run(self, body, freeze, scope):
        cap = body.get("max_output_tokens", MAX_OUTPUT)
        streaming = body.get("stream", False)
        if (type(cap) is not int or not 1 <= cap <= MAX_OUTPUT or type(streaming) is not bool
                or ("instructions" in body and not isinstance(body["instructions"], str))):
            raise ValueError("H6_PROVIDER_REQUEST_LIMIT")
        final_body = dict(body, reasoning=body.get("reasoning", {"effort": "none"}), stream=streaming)
        wire, _ = freeze(final_body)
        digest = hashlib.sha256(wire).hexdigest()
        task, key_hash = scope(body)
        fields = {"task_id": task, "key_hash": key_hash, "fingerprint": digest}
        key = self.credential()
        # Any missing, unauthenticated or late ACK stops before opening the connection.
        quote = self.writer({"op": "admit", **fields})
        if (not isinstance(quote, dict) or set(quote) != p0.QUOTE_FIELDS
                or quote["counted_fingerprint"] != digest or quote["pricing_id"] != p0.PRICING_ID
                or quote["service_tier"] != "default" or quote["max_output_tokens"] != MAX_OUTPUT
                or type(quote["input_tokens"]) is not int or not 0 < quote["input_tokens"] <= MAX_INPUT):
            raise RuntimeError("H6_PROVIDER_INVALID_ACK")
        try:
            until = p0.utc_date(quote["valid_until"])
            if datetime.now(timezone.utc) >= until:
                raise TimeoutError("H6_PROVIDER_QUOTE_EXPIRED")
            content_type, payload = post_once(self.connection_factory(), key, wire, streaming, until)
            usage = usage_from_response(payload, streaming)
            if usage["input_tokens"] > quote["input_tokens"]:
                raise ValueError("H6_PROVIDER_USAGE_ABOVE_APPROVED_COUNT")
        except FAILURES as error:
            try:
                self.writer({"op": "settle", **fields, "outcome": "outcome_unknown", "usage": None})
            except FAILURES:
                # A dead writer leaves inflight with its reserve and consumed permit.
                pass
            raise UnknownOutcome("H6_PROVIDER_OUTCOME_UNKNOWN") from error
        try:
            settled = self.writer({"op": "settle", **fields, "outcome": "usage_recorded", "usage": usage})
            if settled is not True:
                raise ValueError("H6_PROVIDER_INVALID_SETTLEMENT_ACK")
        except FAILURES as error:
            raise UnknownOutcome("H6_PROVIDER_SETTLEMENT_UNCONFIRMED") from error
        if usage["response_status"] != "completed":
            raise RuntimeError("H6_PROVIDER_RESPONSE_NOT_COMPLETED")
        return content_type, payload


def live_lane():
    client = live_client()
    if os.path.lexists(LEGACY_LEDGER) or os.path.lexists(LIVE_LEDGER.parent):
        raise PermissionError("H6_PROVIDER_GUARD_LEDGER_MOUNT")
    lane = Lane(client, connect_live, provider_key)
    lane.credential()
    lane.snapshot()
    return lane
