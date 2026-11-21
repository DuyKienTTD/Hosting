"""Local Docker fixture for UID/ACL and authenticated Unix IPC. No live entry point."""

import fcntl
import hashlib
import hmac
import os
import socket
import stat
import struct
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import h6_writer as ipc
import one_shot
from h6_b2a_ledger_test import LEGACY, SCOPE, TASK, level2_adapter, seed
from mock_contract import encode

LEDGER = Path("/case/mock-ledger/level2-budget.json")
LOCK = LEDGER.with_suffix(".json.lock")
ADDRESS = Path("/case/ipc/writer.sock")
KEY = Path("/case/auth/fixture.key")
ACL = Path("/case/acl")
SOURCE = Path("/level2/adapter.py")
CONTENDED = LEDGER.parent / "fixture-contention"
ADMIT = dict(SCOPE, v=1, op="admit")
SNAPSHOT = {"v": 1, "op": "snapshot"}


def posture(uid=0, gid=0):
    assert (os.geteuid(), os.getegid()) == (uid, gid)
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines())
    assert all(int(status[name], 16) == 0 for name in ("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"))
    assert int(status["NoNewPrivs"]) == 1
    assert {path.name for path in Path("/sys/class/net").iterdir()} == {"lo"}
    assert os.statvfs("/").f_flag & os.ST_RDONLY
    assert not Path("/var/run/docker.sock").exists()
    assert not Path("/run/secrets").exists()


def assert_mode(path, mode, uid=0, gid=0):
    info = path.stat()
    assert (info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)) == (uid, gid, mode)


def acl(path, named_permissions, default=False):
    entries = [(1, 7 if path.is_dir() else 6, 0xffffffff),
               (2, named_permissions, 23062), (4, 0, 0xffffffff),
               (16, named_permissions, 0xffffffff), (32, 0, 0xffffffff)]
    attribute = "system.posix_acl_default" if default else "system.posix_acl_access"
    os.setxattr(path, attribute, struct.pack("<I", 2) + b"".join(
        struct.pack("<HHI", *entry) for entry in entries))


def init():
    posture()
    for directory in (LEDGER.parent, ADDRESS.parent, KEY.parent):
        directory.chmod(0o700)
    KEY.touch(mode=0o600, exist_ok=False)
    KEY.write_bytes(os.urandom(32))
    seed(SOURCE, LEDGER)
    for phase in ("pre-replace", "post-fsync"):
        case = LEDGER.parent / phase / "mock-ledger"
        case.mkdir(mode=0o700, parents=True)
        seed(SOURCE, case / LEDGER.name)
    assert_mode(LEDGER.parent, 0o700)
    for path in (LEDGER, LOCK, KEY):
        assert_mode(path, 0o600)
        assert not any(name.startswith("system.posix_acl_") for name in os.listxattr(path))
    assert not any(name.startswith("system.posix_acl_") for name in os.listxattr(LEDGER.parent))
    assert LOCK.stat().st_ino != LEDGER.stat().st_ino

    for name in ("denied", "existing-acl", "default-acl", "nonroot-replace"):
        case = ACL / name / "mock-ledger"
        case.mkdir(mode=0o700, parents=True)
        seed(SOURCE, case / LEDGER.name)
        if name != "denied":
            acl(case, 7)
            acl(case / LEDGER.name, 6)
            acl(case / LOCK.name, 6)
            assert_mode(case, 0o770)
            assert_mode(case / LEDGER.name, 0o660)
        if name == "default-acl":
            acl(case, 7, default=True)
    print("PASS fixture DAC baseline and scoped ACL setup")


def peer(conn):
    # Reuse the Stage A kernel credential check with the measured root GID.
    ipc.require_peer(conn, 0)


def mac(key, role, client_nonce, server_nonce, payload=b""):
    return hmac.new(key, b"h6-b2-c-fixture\0" + role + client_nonce + server_nonce + payload,
                    hashlib.sha256).hexdigest()


def nonce(text):
    raw = bytes.fromhex(text)
    assert len(raw) == 32
    return raw


def challenge(conn):
    peer(conn)
    client_nonce = nonce(ipc.receive(conn)["client"])
    server_nonce = os.urandom(32)
    key = KEY.read_bytes()
    ipc.send(conn, {"v": 1, "server": server_nonce.hex(),
                    "proof": mac(key, b"S", client_nonce, server_nonce)})
    envelope = ipc.receive(conn)
    assert set(envelope) == {"v", "request", "proof"}
    message = envelope["request"]
    assert hmac.compare_digest(envelope["proof"], mac(key, b"C", client_nonce, server_nonce, encode(message)))
    assert type(message["v"]) is int and message["v"] == 1
    return message


def observed_dispatch(path, message):
    if message["op"] != "admit":
        return ipc.dispatch(path, message)
    original_flock = fcntl.flock

    def observe_lock(fd, flags):
        if flags == fcntl.LOCK_EX:
            try:
                original_flock(fd, flags | fcntl.LOCK_NB)
            except BlockingIOError:
                identity = os.fstat(fd)
                marker = CONTENDED.with_suffix(".tmp")
                marker.write_text(f"{identity.st_dev} {identity.st_ino}")
                marker.replace(CONTENDED)
            else:
                return
        original_flock(fd, flags)

    with patch.object(fcntl, "flock", observe_lock):
        return ipc.dispatch(path, message)


def writer():
    posture()
    assert_mode(ADDRESS.parent, 0o700)
    assert_mode(KEY, 0o600)
    assert os.statvfs(KEY.parent).f_flag & os.ST_RDONLY
    assert ipc.fixture_snapshot(LEDGER)["kill_switch"] is True
    ipc.IPC_GID = 0
    os.umask(0o177)
    with (ADDRESS.parent / "writer.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if ADDRESS.exists():
            assert stat.S_ISSOCK(ADDRESS.lstat().st_mode)
            ADDRESS.unlink()
        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
            listener.bind(str(ADDRESS))
            listener.listen(16)
            while True:
                conn, _ = listener.accept()
                with conn:
                    conn.settimeout(8)
                    try:
                        message = challenge(conn)
                    except (AssertionError, OSError, ValueError, KeyError, TypeError):
                        continue
                    try:
                        reply = {"v": 1, "result": observed_dispatch(LEDGER, message)}
                    except (OSError, ValueError, RuntimeError, KeyError, TypeError, AttributeError):
                        reply = {"v": 1, "error": "H6_WRITER_REJECTED"}
                    try:
                        ipc.send(conn, reply)
                    except OSError:
                        continue


def connect():
    conn = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    conn.settimeout(12)
    try:
        conn.connect(str(ADDRESS))
    except OSError:
        conn.close()
        raise
    return conn


def hello(conn, client):
    ipc.send(conn, {"v": 1, "client": client.hex()})
    return ipc.receive(conn)


def request(message, key, previous=None):
    ipc.IPC_GID = 0
    with connect() as conn:
        peer(conn)
        client = os.urandom(32)
        answer = hello(conn, client)
        server = nonce(answer["server"])
        if not hmac.compare_digest(answer["proof"], mac(key, b"S", client, server)):
            raise PermissionError("fixture server proof rejected")
        packet = {"v": 1, "request": message, "proof": mac(key, b"C", client, server, encode(message))}
        ipc.send(conn, previous if previous is not None else packet)
        return ipc.receive(conn), packet


def expect(error, operation):
    try:
        operation()
    except error:
        return
    raise AssertionError(f"expected {error}")


def guard(mode):
    posture()
    assert not LEDGER.parent.exists()
    assert os.statvfs(ADDRESS.parent).f_flag & os.ST_RDONLY
    assert os.statvfs(KEY.parent).f_flag & os.ST_RDONLY
    assert_mode(ADDRESS, 0o600)
    key = KEY.read_bytes()
    if mode == "race":
        with ThreadPoolExecutor(4) as pool:
            results = list(pool.map(lambda _: request(ADMIT, key)[0], range(4)))
        assert results.count({"v": 1, "result": True}) == 1
        assert results.count({"v": 1, "error": "H6_WRITER_REJECTED"}) == 3
        print("PASS 1/4 root admissions ACK")
    elif mode == "restart":
        assert request(ADMIT, key)[0] == {"v": 1, "error": "H6_WRITER_REJECTED"}
        print("PASS writer restart rejects replay")
    else:
        before, packet = request(SNAPSHOT, key)
        assert before["result"]["kill_switch"] is True
        expect((ValueError, ConnectionResetError), lambda: request(SNAPSHOT, key, previous=packet))
        expect(PermissionError, lambda: request(SNAPSHOT, os.urandom(32)))
        for message in ({"v": 1, "op": "write", "path": "/fake", "data": {}},
                        dict(ADMIT, path="/fake"), dict(ADMIT, fingerprint="0" * 64)):
            assert request(message, key)[0] == {"v": 1, "error": "H6_WRITER_REJECTED"}
        assert request(SNAPSHOT, key)[0] == before
        print("PASS root Guard mutual proof, wrong writer proof, captured packet replay and scope rejection")


def wrong_client(gid):
    posture(gid=gid)
    with connect() as conn:
        client = os.urandom(32)
        if gid:
            assert KEY.exists()  # Correct key is insufficient for the wrong kernel peer.
            expect((ValueError, BrokenPipeError, ConnectionResetError), lambda: hello(conn, client))
        else:
            assert not KEY.exists()
            answer = hello(conn, client)  # SO_PEERCRED alone accepted this exact UID/GID.
            proof = mac(os.urandom(32), b"C", client, nonce(answer["server"]), encode(ADMIT))
            ipc.send(conn, {"v": 1, "request": ADMIT, "proof": proof})
            expect((ValueError, ConnectionResetError), lambda: ipc.receive(conn))
    print(f"PASS client GID {gid} with {'wrong credentials' if gid else 'matching credentials but no key'} denied")


def level2(mode):
    posture()
    assert not ADDRESS.parent.exists() and not KEY.parent.exists()
    adapter = level2_adapter(SOURCE, LEDGER)
    if mode == "verify":
        ledger, raw = one_shot.read_ledger(LEDGER)
        lock_inode, ledger_inode, digest = (LEDGER.parent / "fixture-rollback").read_text().split()
        assert (str(LOCK.stat().st_ino), str(LEDGER.stat().st_ino), hashlib.sha256(raw).hexdigest()) == (
            lock_inode, ledger_inode, digest)
        assert ledger["tasks"][LEGACY]["concurrent_level2"] is True
        assert ledger["tasks"][TASK]["state"] == "inflight"
        print("PASS rollback stop preserves committed bytes and inodes")
        return

    lock_inode, ledger_inode = LOCK.stat().st_ino, LEDGER.stat().st_ino
    atomic_write = adapter.atomic_write

    def wait_for_writer(path, value):
        print("LEVEL2_LOCK_HELD", flush=True)
        deadline = time.monotonic() + 20
        while not CONTENDED.exists():
            assert time.monotonic() < deadline, "writer did not observe Level 2 lock contention"
            time.sleep(0.02)
        held = LOCK.stat()
        assert CONTENDED.read_text() == f"{held.st_dev} {held.st_ino}"
        atomic_write(path, value)

    with LEDGER.open("rb") as old:
        old_raw = old.read()
        with patch.object(adapter, "atomic_write", wait_for_writer):
            adapter.update_task(LEGACY, {"concurrent_level2": True}, 0.00001)
        deadline = time.monotonic() + 15
        while True:
            value, raw = one_shot.read_ledger(LEDGER)
            if TASK in value["tasks"]:
                break
            assert time.monotonic() < deadline
            time.sleep(0.02)
        assert value["tasks"][LEGACY]["concurrent_level2"] is True
        assert value["attempts"] == 2 and value["one_shot_permits"][TASK]["state"] == "consumed"
        assert os.fstat(old.fileno()).st_ino == ledger_inode != LEDGER.stat().st_ino
        old.seek(0)
        assert old.read() == old_raw != raw
        assert LOCK.stat().st_ino == lock_inode
        assert_mode(LOCK, 0o600)
        assert_mode(LEDGER, 0o600)
        (LEDGER.parent / "fixture-rollback").write_text(
            f"{lock_inode} {LEDGER.stat().st_ino} {hashlib.sha256(raw).hexdigest()}")
    print("PASS separate Level 2 writer contended, both updates survived, stable lock and new ledger inode")


def acl_case(mode):
    for name in ("denied", "existing-acl", "default-acl", "nonroot-replace"):
        ledger = ACL / name / "mock-ledger" / LEDGER.name
        lock = ledger.with_suffix(".json.lock")
        if mode == "before":
            if name == "denied":
                expect(PermissionError, lambda: ledger.read_bytes())
                expect(PermissionError, lambda: lock.open("r+b"))
                expect(PermissionError, lambda: ledger.with_name("forbidden").touch())
            else:
                assert ipc.fixture_snapshot(ledger)["kill_switch"]
                lock.open("r+b").close()
                if name == "nonroot-replace":
                    lock_inode = lock.stat().st_ino
                    expect(PermissionError, lambda: ipc.dispatch(ledger, ADMIT))
                    assert lock.stat().st_ino == lock_inode and ledger.stat().st_uid == 0
                    print("PASS ACL permits open but writer fchmod on root-owned lock fails")
        elif name not in ("denied", "nonroot-replace"):
            expect(PermissionError, lambda: ledger.read_bytes())
            expect(PermissionError, lambda: lock.open("r+b"))
    print(f"PASS DAC/ACL checks {mode}")


def acl_level2():
    posture()
    for name in ("existing-acl", "default-acl", "nonroot-replace"):
        ledger = ACL / name / "mock-ledger" / LEDGER.name
        lock = ledger.with_suffix(".json.lock")
        lock_inode, ledger_inode = lock.stat().st_ino, ledger.stat().st_ino
        level2_adapter(SOURCE, ledger).update_task(LEGACY, {"acl_fixture": True}, 0)
        assert lock.stat().st_ino == lock_inode and ledger.stat().st_ino != ledger_inode
        assert_mode(lock, 0o600)
        assert_mode(ledger, 0o600)
    print("PASS Level 2 fchmod and replace remove effective ACL access, including default ACL")


def faults():
    posture()
    for phase in ("pre-replace", "post-fsync"):
        ledger = LEDGER.parent / phase / "mock-ledger" / LEDGER.name
        lock = ledger.with_suffix(".json.lock")
        base, lock_inode = ledger.read_bytes(), lock.stat().st_ino
        durable = one_shot._durable_write
        reader, writer_end = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        pid = os.fork()
        if pid == 0:
            reader.close()
            if phase == "pre-replace":
                with patch.object(os, "replace", lambda *_: os._exit(73)):
                    ipc.dispatch(ledger, ADMIT)
            else:
                def lose_ack(path, value):
                    durable(path, value)
                    os._exit(73)

                with patch.object(one_shot, "_durable_write", lose_ack):
                    ipc.dispatch(ledger, ADMIT)
            ipc.send(writer_end, {"v": 1, "result": True})
            os._exit(90)
        writer_end.close()
        with reader:
            reader.settimeout(5)
            assert reader.recv(4096) == b""
        assert os.waitstatus_to_exitcode(os.waitpid(pid, 0)[1]) == 73
        assert lock.stat().st_ino == lock_inode
        if phase == "pre-replace":
            assert ledger.read_bytes() == base
            assert ipc.dispatch(ledger, ADMIT) is True  # Explicit mock recovery check.
        else:
            state, raw = one_shot.read_ledger(ledger)
            assert raw != base and state["tasks"][TASK]["state"] == "inflight"
        committed = ledger.read_bytes()
        expect(RuntimeError, lambda: ipc.dispatch(ledger, ADMIT))
        assert ledger.read_bytes() == committed
        print(f"PASS {phase} injected process exit, no ACK, stable lock and replay rejection")


def main(role, mode="before"):
    if role == "ready":
        connect().close()
    elif role == "guard":
        guard(mode)
    elif role == "level2":
        level2(mode)
    elif role == "acl-nonroot":
        posture(23062, 23060)
        acl_case(mode)
    elif role == "same-uid":
        wrong_client(0)
    elif role == "wrong-gid":
        wrong_client(23060)
    elif role == "unmounted":
        posture()
        assert not KEY.parent.exists() and not LEDGER.parent.exists()
        expect(FileNotFoundError, connect)
        print("PASS no socket mount")
    else:
        {"init": init, "writer": writer, "acl-level2": acl_level2, "faults": faults}[role]()


if __name__ == "__main__":
    main(*sys.argv[1:])
