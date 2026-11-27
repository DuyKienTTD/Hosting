"""Linux-only targeted B2-L tests. All ledgers and IPC keys are synthetic."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import errno
import fcntl
import json
import os
from pathlib import Path
import select
import signal
import socket
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

import h6_b2l_idle as idle
import h6_ipc_auth as ipc
import h6_p0 as p0
import h6_provider as provider
import h6_writer as writer
import one_shot
from mock_contract import encode, usage_from_response


SOURCE = Path(__file__).resolve().parent
SCOPE = {"task_id": "fake-b2l", "key_hash": "b" * 64, "fingerprint": "c" * 64}
ADMIT = {"op": "admit", **SCOPE}
USAGE = usage_from_response(encode({"id": "fake-response", "model": one_shot.MODEL,
    "status": "completed", "service_tier": "default", "usage": {
        "input_tokens": 100, "output_tokens": 30, "total_tokens": 130,
        "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
        "output_tokens_details": {"reasoning_tokens": 0}}}), False)
SETTLE = {"op": "settle", **SCOPE, "outcome": "usage_recorded", "usage": USAGE}
UNKNOWN = {**SETTLE, "outcome": "outcome_unknown", "usage": None}
REJECT = (OSError, RuntimeError, ValueError)


class Fixture:
    def __init__(self, root, permit=False, expiry_minutes=5):
        self.root = root
        self.directory = root / "mock-ledger"
        self.directory.mkdir(mode=0o700)
        (root / "ipc").mkdir(mode=0o700)
        self.address = root / "ipc" / "writer.sock"
        self.transport_trace = root / "fake-transport.trace"
        self.path = self.directory / idle.LEDGER
        self.lock = self.directory / idle.LOCK
        self.lock.touch(mode=0o600)
        self.key = os.urandom(ipc.PROOF_BYTES)
        self.key_path = root / "synthetic-ipc.key"
        self.key_path.write_bytes(self.key)
        self.key_path.chmod(0o400)
        today = datetime.now(timezone.utc)
        bucket = {"attempts": 1, "reserved_usd": 0.0035, "actual_usd": 0.0}
        ledger = {**bucket, "schema_version": 1, "model": one_shot.MODEL, "max_calls": one_shot.MAX_CALLS,
                  "caps_usd": one_shot.CAPS, "kill_switch": True, "tasks": {"historical": {"state": "complete"}},
                  "days": {today.date().isoformat(): bucket}, "one_shot_permits": {},
                  idle.MARKER: True, "fake_extension": ["preserve"]}
        if permit:
            expiry = (today + timedelta(minutes=expiry_minutes)).isoformat()
            ledger["one_shot_permits"][SCOPE["task_id"]] = {
                "state": "ready", "model": one_shot.MODEL, "key_hash": SCOPE["key_hash"],
                "fingerprint": SCOPE["fingerprint"], "expires_at": expiry, "provider_scope": {
                    "approval_sha256": "a" * 64, "counted_fingerprint": SCOPE["fingerprint"], "input_tokens": 723,
                    "max_output_tokens": 600, "pricing_id": p0.PRICING_ID, "service_tier": "default", "valid_until": expiry,
                },
            }
        one_shot._durable_write(self.path, ledger)

    def snapshot(self, *, include_atime=True):
        fd = os.open(self.path, os.O_RDONLY | os.O_NOATIME)
        with os.fdopen(fd, "rb") as stream:
            data = stream.read()
        def metadata(path):
            info = path.stat()
            return info.st_dev, info.st_ino, info.st_atime_ns if include_atime else None, info.st_mtime_ns, info.st_ctime_ns

        return data, (metadata(self.path), metadata(self.lock))

    def fake_post(self):
        ledger = json.loads(self.snapshot()[0])
        assert ledger["attempts"] == 2 and ledger["reserved_usd"] == 0.007
        assert ledger["one_shot_permits"][SCOPE["task_id"]]["state"] == "consumed"
        fd = os.open(self.transport_trace, os.O_CREAT | os.O_APPEND | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "ab") as stream:
            stream.write(b"P")
            stream.flush()
            os.fsync(stream.fileno())

    def posts(self):
        return self.transport_trace.read_bytes().count(b"P") if self.transport_trace.exists() else 0

    def ready(self, running):
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline and running():
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
                    conn.connect(str(self.address))
                return
            except (FileNotFoundError, ConnectionRefusedError):
                time.sleep(0.01)
        raise AssertionError("fixture writer did not listen")

    @contextmanager
    def startup(self):
        process = subprocess.Popen([sys.executable, "-B", str(SOURCE / "h6_writer.py"),
                                    "--b2-l-startup-fixture", str(self.root)])
        try:
            self.ready(lambda: process.poll() is None)
            yield
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=5)

    def health(self):
        return idle.call(self.address, self.key)

    def startup_rpc(self, request):
        return ipc.exchange(self.address, self.key, idle.DOMAIN, request)

    def mock_rpc(self, request):
        return ipc.exchange(self.address, self.key, provider.LIVE_DOMAIN, request)

    @contextmanager
    def admission(self, fault=None):
        """Separate test-only P0 signed admission. No CLI live branch is entered."""
        assert json.loads(self.snapshot()[0])[idle.MARKER] is True
        original_replace, original_sync = os.replace, os.fsync

        def replace(*args):
            if fault == "before_rename":
                os._exit(71)
            return original_replace(*args)

        def sync(fd):
            directory = stat.S_ISDIR(os.fstat(fd).st_mode)
            if directory and fault == "after_rename_before_fsync":
                os._exit(72)
            if directory and fault == "directory_fsync_failure":
                raise OSError(errno.EIO, "synthetic directory fsync error")
            original_sync(fd)
            if directory and fault == "after_fsync_before_ack":
                os._exit(73)

        def dispatch(path, request):
            result = p0.dispatch(path, request)
            if request["op"] == "settle" and fault == "after_settle_before_ack":
                os._exit(76)
            return result

        pid = os.fork()
        if not pid:
            with patch.object(os, "replace", replace), patch.object(os, "fsync", sync):
                writer.listen(self.address, self.path, 0, 0, 0o700, 0o600,
                              lambda conn, path: ipc.handle_exchange(conn, path, self.key, provider.LIVE_DOMAIN, dispatch))
            os._exit(90)
        expected = {"before_rename": 71, "after_rename_before_fsync": 72,
                    "after_fsync_before_ack": 73, "after_settle_before_ack": 76}
        try:
            self.ready(lambda: True)
            yield
        finally:
            exited, code = os.waitpid(pid, os.WNOHANG)
            if not exited and fault in expected:
                deadline = time.monotonic() + 1
                while not exited and time.monotonic() < deadline:
                    time.sleep(0.01)
                    exited, code = os.waitpid(pid, os.WNOHANG)
            if not exited:
                os.kill(pid, signal.SIGTERM)
                _, code = os.waitpid(pid, 0)
            if fault in expected and os.waitstatus_to_exitcode(code) != expected[fault]:
                raise AssertionError("expected exact writer crash boundary")

    def caller_crash(self, fake_post):
        read_fd, write_fd = os.pipe()
        pid = os.fork()
        if not pid:
            os.close(read_fd)
            self.mock_rpc(ADMIT)
            os.write(write_fd, b"A")
            if fake_post:
                self.fake_post()
                os.write(write_fd, b"P")
            os._exit(75 if fake_post else 74)
        os.close(write_fd)
        try:
            with os.fdopen(read_fd, "rb") as stream:
                if not select.select([stream], [], [], 5)[0]:
                    os.kill(pid, signal.SIGKILL)
                result = stream.read()
        finally:
            _, status = os.waitpid(pid, 0)
        return result, os.waitstatus_to_exitcode(status)


class StartupTests(unittest.TestCase):
    @contextmanager
    def fixture(self, **kwargs):
        with TemporaryDirectory(prefix="h6-b2l-", dir="/tmp") as root:
            yield Fixture(Path(root), **kwargs)

    def assert_health(self, fx, status, healthy=True):
        self.assertEqual(fx.health(), {"version": 1, "healthy": healthy, "status": status})

    def assert_read_only(self, fx, status):
        before = fx.snapshot()
        names = set(os.listdir(fx.directory))
        with fx.startup():
            self.assert_health(fx, status)
            for op in (ADMIT, SETTLE, {"op": "snapshot"}, {"op": "health", "version": True},
                       {"op": "health", "version": 1, "extra": False}):
                with self.assertRaises(REJECT):
                    fx.startup_rpc(op)
        self.assertEqual(fx.snapshot(), before)
        self.assertEqual(set(os.listdir(fx.directory)), names)

    def test_permitless_restart_and_twenty_immutable_health_calls(self):
        with self.fixture() as fx:
            before = fx.snapshot()
            for _ in range(2):
                with fx.startup():
                    for _ in range(10):
                        self.assert_health(fx, "IDLE_NO_PERMIT")
                    with self.assertRaises(REJECT):
                        fx.startup_rpc(ADMIT)
            self.assertEqual(fx.snapshot(), before)
            self.assertEqual(set(os.listdir(fx.directory)), {idle.LEDGER, idle.LOCK})
            ledger = json.loads(before[0])
            print("B2L_HEALTH", json.dumps({"calls": 20, "cold_starts": 2, "attempts": ledger["attempts"],
                  "reserved_usd": ledger["reserved_usd"], "actual_usd": ledger["actual_usd"],
                  "bytes_and_inode_metadata_equal": True, "new_ledger_files": 0,
                  "fixture_layout": "root:root 0700/0600", "mock_dispatches": fx.posts()}), flush=True)

    def test_startup_only_denies_valid_expired_and_wrong_scope_permits(self):
        with self.fixture(permit=True) as fx:
            self.assert_read_only(fx, "STARTUP_ONLY")
            original = fx.snapshot()
            with fx.startup():
                with self.assertRaises(REJECT):
                    fx.startup_rpc({**ADMIT, "fingerprint": "0" * 64})
            self.assertEqual(fx.snapshot(), original)
        with self.fixture(permit=True, expiry_minutes=-1) as fx:
            self.assert_read_only(fx, "IDLE_NO_PERMIT")

    def test_missing_malformed_wrong_mode_and_replaced_paths(self):
        for fault in ("missing_ledger", "missing_lock", "bad_json", "bad_mode", "symlink", "marker", "kill",
                      "replaced_lock"):
            with self.subTest(fault=fault), self.fixture() as fx:
                if fault == "missing_ledger":
                    fx.path.unlink()
                if fault == "missing_lock":
                    fx.lock.unlink()
                if fault == "bad_json":
                    fx.path.write_bytes(b"{")
                if fault == "bad_mode":
                    fx.lock.chmod(0o644)
                if fault == "symlink":
                    other = fx.directory / "untrusted"
                    fx.path.rename(other)
                    fx.path.symlink_to(other.name)
                if fault in ("marker", "kill"):
                    data = json.loads(fx.snapshot()[0])
                    data[idle.MARKER if fault == "marker" else "kill_switch"] = False
                    fx.path.write_bytes(encode(data))
                with fx.startup():
                    if fault == "replaced_lock":
                        self.assert_health(fx, "IDLE_NO_PERMIT")
                        fx.lock.rename(fx.directory / "replaced-inode")
                        fx.lock.touch(mode=0o600)
                    before = {p.name: p.lstat().st_ino for p in fx.directory.iterdir()}
                    self.assert_health(fx, "BLOCKED", False)
                    self.assertEqual({p.name: p.lstat().st_ino for p in fx.directory.iterdir()}, before)

    def test_lock_contention_bounded_and_recovers(self):
        with self.fixture() as fx, fx.startup():
            before = fx.snapshot()
            with fx.lock.open("rb") as stream:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                start = time.monotonic()
                self.assert_health(fx, "UNAVAILABLE", False)
                elapsed = time.monotonic() - start
                self.assertGreaterEqual(elapsed, idle.LOCK_WAIT)
                self.assertLess(elapsed, 2)
            self.assert_health(fx, "IDLE_NO_PERMIT")
            self.assertEqual(fx.snapshot(), before)
            print("B2L_LOCK", json.dumps({"held_lock_status": "UNAVAILABLE",
                  "elapsed_ms": round(elapsed * 1000, 2), "recovery": "IDLE_NO_PERMIT"}), flush=True)

    def test_auth_wrong_key_domain_replay_and_missing_key(self):
        with self.fixture() as fx, fx.startup():
            before = fx.snapshot()
            for key, domain in ((os.urandom(32), idle.DOMAIN), (fx.key, provider.LIVE_DOMAIN)):
                with self.assertRaises(REJECT):
                    ipc.exchange(fx.address, key, domain, idle.REQUEST)
            nonce = os.urandom(32)
            stale = None
            for _ in range(2):
                with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
                    deadline = time.monotonic() + 2
                    conn.connect(str(fx.address))
                    ipc.send(conn, deadline, client=nonce.hex())
                    challenge = ipc.receive(conn, deadline, "server", "proof")
                    server = bytes.fromhex(challenge["server"])
                    if stale is None:
                        stale = ipc.proof(fx.key, b"C", nonce, server, encode(idle.REQUEST), domain=idle.DOMAIN).hex()
                        ipc.send(conn, deadline, request=idle.REQUEST, proof=stale)
                        self.assertIn("result", ipc.receive(conn, deadline, "reply", "proof")["reply"])
                    else:
                        ipc.send(conn, deadline, request=idle.REQUEST, proof=stale)
                        self.assertEqual(conn.recv(4096), b"")
            self.assertEqual(fx.snapshot(), before)
        with self.fixture() as fx:
            fx.key_path.unlink()
            proc = subprocess.run([sys.executable, "-B", str(SOURCE / "h6_writer.py"),
                                   "--b2-l-startup-fixture", str(fx.root)], capture_output=True, timeout=5)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(fx.address.exists())

    def test_wrong_peer_uid_and_gid(self):
        with self.fixture() as fx, fx.startup():
            before = fx.snapshot()
            # Enable connect at the test socket so rejection is from SO_PEERCRED, not DAC.
            fx.root.chmod(0o711)
            fx.address.parent.chmod(0o711)
            fx.address.chmod(0o666)
            for uid, gid in ((65534, 0), (0, 65534)):
                pid = os.fork()
                if not pid:
                    try:
                        os.setgid(gid)
                        os.setuid(uid)
                        with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
                            conn.settimeout(2)
                            conn.connect(str(fx.address))
                            if conn.recv(4096) == b"":
                                os._exit(0)
                    finally:
                        os._exit(91)
                _, status = os.waitpid(pid, 0)
                self.assertEqual(os.waitstatus_to_exitcode(status), 0)
            fx.root.chmod(0o700)
            fx.address.parent.chmod(0o700)
            fx.address.chmod(0o600)
            self.assert_health(fx, "IDLE_NO_PERMIT")
            self.assertEqual(fx.snapshot(), before)

    def assert_state(self, fx, state, initial):
        current = fx.snapshot(include_atime=False)
        ledger = json.loads(current[0])
        base = json.loads(initial[0])
        self.assertTrue(ledger["kill_switch"])
        self.assertEqual(ledger["actual_usd"], float(USAGE["estimated_cost_usd"]) if state == "usage_recorded" else 0)
        self.assertEqual(ledger["attempts"], 2)
        self.assertEqual(ledger["reserved_usd"], 0.007)
        self.assertEqual(ledger["fake_extension"], base["fake_extension"])
        self.assertEqual(ledger["tasks"]["historical"], base["tasks"]["historical"])
        task = ledger["tasks"][SCOPE["task_id"]]
        self.assertEqual(task["state"], state)
        self.assertEqual(ledger["days"][task["day"]]["attempts"], 2)
        self.assertEqual(ledger["days"][task["day"]]["reserved_usd"], 0.007)
        self.assertEqual(ledger["one_shot_permits"][SCOPE["task_id"]]["state"], "consumed")
        self.assertNotEqual(current[1][0][0:2], initial[1][0][0:2])
        self.assertEqual(current[1][1], initial[1][1])

    def test_concurrent_signed_admission_single_fake_post_and_settlement_replay(self):
        with self.fixture(permit=True) as fx:
            initial = fx.snapshot(include_atime=False)
            with fx.admission():
                with self.assertRaises(REJECT):
                    fx.mock_rpc(ADMIT | {"fingerprint": "d" * 64})
                self.assertEqual(fx.snapshot(include_atime=False), initial)

                def attempt(_):
                    try:
                        result = fx.mock_rpc(ADMIT)
                    except REJECT:
                        return None
                    fx.fake_post()
                    return result

                with ThreadPoolExecutor(max_workers=4) as pool:
                    replies = list(pool.map(attempt, range(4)))
                self.assertEqual(sum(reply is not None for reply in replies), 1)
                self.assert_state(fx, "inflight", initial)  # Durable consume/reserve before fake POST.
                self.assertTrue(fx.mock_rpc(SETTLE))
                terminal = fx.snapshot(include_atime=False)
                self.assertTrue(fx.mock_rpc(SETTLE))
                with self.assertRaises(REJECT):
                    fx.mock_rpc(UNKNOWN)
                self.assertEqual(fx.posts(), 1)
                self.assertEqual(fx.snapshot(include_atime=False), terminal)
            self.assert_state(fx, "usage_recorded", initial)
            self.assert_read_only(fx, "SETTLED")

    def test_six_crash_windows_and_directory_fsync_failure(self):
        modes = (("before_rename", "ready", 0, 0), ("after_rename_before_fsync", "inflight", 0, 0),
                 ("after_fsync_before_ack", "inflight", 0, 0), ("after_ack_before_post", "inflight", 1, 0),
                 ("after_post_before_settle", "inflight", 1, 1), ("after_settle_before_ack", "usage_recorded", 1, 1),
                 ("directory_fsync_failure", "inflight", 0, 0))
        for stage, state, acks, posts in modes:
            with self.subTest(stage=stage), self.fixture(permit=True) as fx:
                initial = fx.snapshot(include_atime=False)
                writer_fault = None if stage in ("after_ack_before_post", "after_post_before_settle") else stage
                with fx.admission(writer_fault):
                    messages = b""
                    if stage in ("after_ack_before_post", "after_post_before_settle"):
                        messages, code = fx.caller_crash(stage == "after_post_before_settle")
                        self.assertEqual(code, 75 if stage == "after_post_before_settle" else 74)
                    elif stage == "after_settle_before_ack":
                        fx.mock_rpc(ADMIT)
                        self.assert_state(fx, "inflight", initial)
                        fx.fake_post()
                        messages = b"AP"
                        with self.assertRaises(REJECT):
                            fx.mock_rpc(SETTLE)
                    else:
                        with self.assertRaises(REJECT):
                            fx.mock_rpc(ADMIT)
                self.assertEqual((messages.count(b"A"), messages.count(b"P")), (acks, posts))
                self.assertEqual(fx.posts(), posts)
                if state == "ready":
                    self.assertEqual(fx.snapshot(include_atime=False), initial)
                    self.assert_read_only(fx, "STARTUP_ONLY")
                else:
                    self.assert_state(fx, state, initial)
                    committed = fx.snapshot(include_atime=False)
                    self.assert_read_only(fx, "SETTLED" if state == "usage_recorded" else "RECONCILE_REQUIRED")
                    with fx.admission():
                        with self.assertRaises(REJECT):
                            fx.mock_rpc(ADMIT)
                        if state == "usage_recorded":
                            self.assertTrue(fx.mock_rpc(SETTLE))
                    self.assertEqual(fx.snapshot(include_atime=False), committed)
                    if stage == "after_post_before_settle":
                        with fx.admission():
                            self.assertTrue(fx.mock_rpc(UNKNOWN))
                            with self.assertRaises(REJECT):
                                fx.mock_rpc(SETTLE)
                        self.assert_state(fx, "outcome_unknown", initial)
                        self.assert_read_only(fx, "RECONCILE_REQUIRED")
                ledger = json.loads(fx.snapshot()[0])
                self.assertEqual(fx.posts(), posts)
                print("B2L_CRASH", json.dumps({"stage": stage, "observed_after_crash": state,
                      "signed_admit_acks": acks, "fake_posts": posts, "new_posts_after_restart": 0,
                      "attempts": ledger["attempts"], "reserved_usd": ledger["reserved_usd"],
                      "actual_usd": ledger["actual_usd"], "stable_lock_inode_unchanged": True}), flush=True)

    def test_live_entrypoint_remains_locked(self):
        result = subprocess.run([sys.executable, "-B", str(SOURCE / "h6_writer.py"), "--b2-f-real"],
                                capture_output=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"H6_PROVIDER_BUILD_DISABLED", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
