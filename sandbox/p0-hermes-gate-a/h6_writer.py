"""Stage A Unix IPC on an explicitly marked, disposable mock ledger."""

import fcntl
import hashlib
import json
import os
import re
import socket
import stat
import struct
from pathlib import Path

from mock_contract import encode, no_duplicate_keys, usage_from_response
from one_shot import MODEL, admit, read_ledger, settle_mock

GUARD_UID = 23061
WRITER_UID = 23062
IPC_GID = 23060
SOCKET_PATH = Path("/opt/ttd/h6-ipc/writer.sock")
FIXTURE_PATH = Path("/opt/ttd/mock-ledger/level2-budget.json")
MAX_PACKET = 4096
IPC_TIMEOUT = 2
VERSION = 1
PEER_FORMAT = "3i"
TASK_ID = re.compile(r"[A-Za-z0-9._:-]{1,128}")
SHA256 = re.compile(r"[a-f0-9]{64}")
SUMMARY_FIELDS = {"attempts", "reserved_usd", "actual_usd", "kill_switch", "sha256"}


def require_peer(conn, uid):
    credentials = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize(PEER_FORMAT))
    _, actual_uid, gid = struct.unpack(PEER_FORMAT, credentials)
    if (actual_uid, gid) != (uid, IPC_GID):
        raise PermissionError("H6_IPC_PEER_REJECTED")


def receive(conn):
    raw = conn.recv(MAX_PACKET + 1)
    if not raw or len(raw) > MAX_PACKET:
        raise ValueError("H6_IPC_MESSAGE_SIZE")
    message = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    if not isinstance(message, dict) or type(message.get("v")) is not int or message["v"] != VERSION:
        raise ValueError("H6_IPC_VERSION")
    return message


def send(conn, message):
    packet = encode(message)
    if len(packet) > MAX_PACKET or conn.send(packet) != len(packet):
        raise OSError("H6_IPC_SEND_FAILED")


def call(path, operation, **fields):
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
        conn.settimeout(IPC_TIMEOUT)
        conn.connect(os.fspath(path))
        require_peer(conn, WRITER_UID)
        send(conn, dict(fields, v=VERSION, op=operation))
        reply = receive(conn)
    if set(reply) != {"v", "result"}:
        raise RuntimeError("H6_WRITER_REJECTED")
    result = reply["result"]
    if operation == "snapshot":
        if not isinstance(result, dict) or set(result) != SUMMARY_FIELDS:
            raise RuntimeError("H6_WRITER_INVALID_SNAPSHOT")
    elif result is not True:
        raise RuntimeError("H6_WRITER_INVALID_ACK")
    return result


def fixture_snapshot(path):
    # Open the pathname each time. Atomic replacement publishes a complete snapshot.
    ledger, raw = read_ledger(path)
    if ledger.get("h6_stage_a_fixture") is not True:
        raise ValueError("STAGE_A_FIXTURE_REQUIRED")
    summary = {key: ledger[key] for key in SUMMARY_FIELDS - {"sha256"}}
    summary["sha256"] = hashlib.sha256(raw).hexdigest()
    return summary


def validate_usage(usage):
    """Validate the bounded, normalized mock accounting before persisting it."""
    if not isinstance(usage, dict) or not SHA256.fullmatch(usage["response_id_hash"]):
        raise ValueError("H6_MOCK_USAGE")
    response = {
        "id": "stage-a-validation",
        "model": MODEL,
        "status": usage["response_status"],
        "service_tier": "default",
        "usage": {
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "total_tokens": usage["input_tokens"] + usage["output_tokens"],
            "input_tokens_details": {"cached_tokens": usage["cached_tokens"],
                                     "cache_write_tokens": usage["cache_write_tokens"]},
            "output_tokens_details": {"reasoning_tokens": usage["reasoning_tokens"]},
        },
    }
    checked = usage_from_response(encode(response), False)
    checked["response_id_hash"] = usage["response_id_hash"]
    if checked != usage:
        raise ValueError("H6_MOCK_USAGE")


def dispatch(path, message):
    operation = message["op"]
    keys = set(message) - {"v", "op"}
    snapshot = fixture_snapshot(path)
    if operation == "snapshot" and not keys:
        return snapshot
    if operation == "admit" and keys == {"task_id", "key_hash", "fingerprint"}:
        task_id, key_hash, fingerprint = (message[key] for key in ("task_id", "key_hash", "fingerprint"))
        if not (TASK_ID.fullmatch(task_id) and SHA256.fullmatch(key_hash) and SHA256.fullmatch(fingerprint)):
            raise ValueError("H6_IPC_SCOPE")
        return admit(path, task_id, key_hash, fingerprint, stage_a=True) == "admitted"
    if operation == "settle" and keys == {"task_id", "fingerprint", "outcome", "usage"}:
        task_id, fingerprint, outcome, usage = (message[key] for key in
                                                 ("task_id", "fingerprint", "outcome", "usage"))
        if not (TASK_ID.fullmatch(task_id) and SHA256.fullmatch(fingerprint)):
            raise ValueError("H6_IPC_SCOPE")
        if outcome == "usage_recorded":
            validate_usage(usage)
        elif outcome != "outcome_unknown" or usage is not None:
            raise ValueError("H6_IPC_OUTCOME")
        settle_mock(path, task_id, fingerprint, outcome, usage, stage_a=True)
        return True
    raise ValueError("H6_IPC_OPERATION")


def handle(conn, path):
    conn.settimeout(IPC_TIMEOUT)
    require_peer(conn, GUARD_UID)
    try:
        result = dispatch(path, receive(conn))
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, AttributeError):
        send(conn, {"v": VERSION, "error": "H6_WRITER_REJECTED"})
        return
    # No successful admission reply before one_shot has fsynced file and directory.
    send(conn, {"v": VERSION, "result": result})


def serve(address, path):
    if (os.geteuid(), os.getegid()) != (WRITER_UID, IPC_GID):
        raise PermissionError("H6_WRITER_IDENTITY")
    if path.name != FIXTURE_PATH.name or path.parent.resolve().name != "mock-ledger" or path.is_symlink():
        raise ValueError("STAGE_A_FIXTURE_REQUIRED")
    if fixture_snapshot(path)["kill_switch"] is not True:
        raise ValueError("KILL_SWITCH_NOT_ON")
    directory = address.parent.stat()
    if (directory.st_uid, directory.st_gid, stat.S_IMODE(directory.st_mode)) != (WRITER_UID, IPC_GID, 0o750):
        raise PermissionError("H6_IPC_DIRECTORY")
    os.umask(0o117)  # A socket starts with mode 0660 even before listen.
    lock_fd = os.open(address.parent / "writer.lock", os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(lock_fd, "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            previous = address.lstat()
        except FileNotFoundError:
            pass
        else:
            if not stat.S_ISSOCK(previous.st_mode) or previous.st_uid != WRITER_UID:
                raise PermissionError("H6_IPC_STALE_PATH")
            address.unlink()
        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
            listener.bind(os.fspath(address))
            listener.listen(16)
            while True:
                conn, _ = listener.accept()
                with conn:
                    try:
                        handle(conn, path)
                    except OSError:
                        # Includes rejected peer, timeout and lost acknowledgement.
                        continue


if __name__ == "__main__":
    serve(SOCKET_PATH, FIXTURE_PATH)
