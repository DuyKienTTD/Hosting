"""Authenticated, opt-in Unix IPC for the H6 mock writer and Guard."""

import hashlib
import hmac
import json
import os
import socket
import stat
import struct
import time
from pathlib import Path

import h6_writer
from mock_contract import encode, no_duplicate_keys

SOCKET_PATH = Path("/opt/ttd/h6-b2d-ipc/writer.sock")
KEY_PATH = Path("/run/h6-b2d-auth/ipc.key")
PROVIDER_KEY_PATH = Path("/run/secrets/openai_provider_api_key")
VERSION = 2
TIMEOUT = 4
PROOF_BYTES = 32
DOMAIN = b"ttd-h6-b2d-mock-ipc-v2\x00"


def read_mock_key():
    """Check fixture-only identity and the permissions of the opened file."""
    if (os.geteuid(), os.getegid()) != (0, 0) or os.path.lexists(PROVIDER_KEY_PATH):
        raise PermissionError("H6_IPC_MOCK_ISOLATION")
    return read_key(KEY_PATH)


def read_key(path):
    directory = path.parent.lstat()
    if (not stat.S_ISDIR(directory.st_mode)
            or (directory.st_uid, directory.st_gid, stat.S_IMODE(directory.st_mode)) != (0, 0, 0o700)):
        raise PermissionError("H6_IPC_KEY_POLICY")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_gid != 0
                or stat.S_IMODE(info.st_mode) != 0o400 or info.st_nlink != 1
                or not os.fstatvfs(stream.fileno()).f_flag & os.ST_RDONLY):
            raise PermissionError("H6_IPC_KEY_POLICY")
        key = stream.read(PROOF_BYTES + 1)
    if len(key) != PROOF_BYTES:
        raise ValueError("H6_IPC_KEY_LENGTH")
    return key


def root_peer(conn):
    fmt = h6_writer.PEER_FORMAT
    _, uid, gid = struct.unpack(fmt, conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize(fmt)))
    if (uid, gid) != (0, 0):
        raise PermissionError("H6_IPC_PEER_REJECTED")


def reject_constant(_):
    raise ValueError("H6_IPC_PACKET")


def set_remaining(conn, deadline):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("H6_IPC_DEADLINE")
    conn.settimeout(remaining)


def receive(conn, deadline, *fields):
    set_remaining(conn, deadline)
    raw = conn.recv(h6_writer.MAX_PACKET + 1)
    if not raw or len(raw) > h6_writer.MAX_PACKET:
        raise ValueError("H6_IPC_MESSAGE_SIZE")
    try:
        message = json.loads(raw, object_pairs_hook=no_duplicate_keys, parse_constant=reject_constant)
        if (not isinstance(message, dict) or set(message) != {"v", *fields}
                or type(message["v"]) is not int or message["v"] != VERSION or encode(message) != raw):
            raise ValueError("H6_IPC_PACKET")
    except (RecursionError, OverflowError) as error:
        raise ValueError("H6_IPC_PACKET") from error
    return message


def send(conn, deadline, **fields):
    set_remaining(conn, deadline)
    h6_writer.send(conn, {"v": VERSION, **fields})


def proof_bytes(value):
    if not isinstance(value, str) or not h6_writer.SHA256.fullmatch(value):
        raise ValueError("H6_IPC_PROOF_FORMAT")
    return bytes.fromhex(value)


def proof(key, role, client, server, payload=b"", *, domain=DOMAIN):
    return hmac.digest(key, domain + role + client + server + payload, "sha256")


def verify(value, expected):
    if not hmac.compare_digest(proof_bytes(value), expected):
        raise PermissionError("H6_IPC_AUTH_REJECTED")


def call(operation, **fields):
    result = exchange(SOCKET_PATH, read_mock_key(), DOMAIN, {**fields, "op": operation})
    if operation == "snapshot":
        if not isinstance(result, dict) or set(result) != h6_writer.SUMMARY_FIELDS:
            raise RuntimeError("H6_WRITER_INVALID_SNAPSHOT")
    elif result is not True:
        raise RuntimeError("H6_WRITER_INVALID_ACK")
    return result


def exchange(address, key, domain, request):
    deadline = time.monotonic() + TIMEOUT
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
        set_remaining(conn, deadline)
        conn.connect(os.fspath(address))
        root_peer(conn)
        client = os.urandom(PROOF_BYTES)
        send(conn, deadline, client=client.hex())
        challenge = receive(conn, deadline, "server", "proof")
        server = proof_bytes(challenge["server"])
        verify(challenge["proof"], proof(key, b"S", client, server, domain=domain))
        wire = encode(request)
        send(conn, deadline, request=request, proof=proof(key, b"C", client, server, wire, domain=domain).hex())
        envelope = receive(conn, deadline, "reply", "proof")
        reply = envelope["reply"]
        signed = hashlib.sha256(wire).digest() + encode(reply)
        verify(envelope["proof"], proof(key, b"R", client, server, signed, domain=domain))
    if not isinstance(reply, dict) or set(reply) != {"result"}:
        raise RuntimeError("H6_WRITER_REJECTED")
    return reply["result"]


def handle(conn, path, key):
    handle_exchange(conn, path, key, DOMAIN, h6_writer.dispatch)


def handle_exchange(conn, path, key, domain, dispatch):
    deadline = time.monotonic() + TIMEOUT
    root_peer(conn)
    try:
        client = proof_bytes(receive(conn, deadline, "client")["client"])
        server = os.urandom(PROOF_BYTES)
        send(conn, deadline, server=server.hex(), proof=proof(key, b"S", client, server, domain=domain).hex())
        envelope = receive(conn, deadline, "request", "proof")
        request = envelope["request"]
        wire = encode(request)
        verify(envelope["proof"], proof(key, b"C", client, server, wire, domain=domain))
    except (ValueError, RecursionError) as error:
        raise PermissionError("H6_IPC_AUTH_REJECTED") from error
    set_remaining(conn, deadline)
    try:
        if not isinstance(request, dict) or "v" in request:
            raise ValueError("H6_IPC_REQUEST")
        reply = {"result": dispatch(path, request)}
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, AttributeError):
        reply = {"error": "H6_WRITER_REJECTED"}
    # Never publish a successful ACK before dispatch returns from the durable commit.
    signed = hashlib.sha256(wire).digest() + encode(reply)
    send(conn, deadline, reply=reply, proof=proof(key, b"R", client, server, signed, domain=domain).hex())


def serve_mock():
    key = read_mock_key()
    ledger = h6_writer.FIXTURE_PATH
    if ledger.resolve() != ledger:
        raise PermissionError("H6_IPC_MOCK_PATH")
    for path, mode, is_type in ((ledger.parent, 0o700, stat.S_ISDIR), (ledger, 0o600, stat.S_ISREG),
                                (ledger.with_suffix(".json.lock"), 0o600, stat.S_ISREG)):
        info = path.lstat()
        if (not is_type(info.st_mode) or (info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)) != (0, 0, mode)
                or (is_type is stat.S_ISREG and info.st_nlink != 1)):
            raise PermissionError("H6_IPC_MOCK_LEDGER_POLICY")
    h6_writer.serve_fixture(SOCKET_PATH, ledger, 0, 0, 0o700, 0o600,
                            lambda conn, path: handle(conn, path, key))
