"""Read-only P0 startup fixture. No admission handler, live paths, or provider imports."""

from contextlib import contextmanager
from datetime import datetime, timezone
import errno
import fcntl
import os
from pathlib import Path
import stat
import time

import h6_ipc_auth as ipc
import h6_p0 as p0
import h6_writer as writer
import one_shot


DOMAIN = b"ttd-h6-b2l-startup-fixture-v1\x00"
REQUEST = {"op": "health", "version": 1}
ENABLED = {"IDLE_NO_PERMIT", "STARTUP_ONLY", "RECONCILE_REQUIRED", "SETTLED"}
STATUSES = ENABLED | {"BLOCKED", "UNAVAILABLE"}
LOCK_WAIT = 0.20
MARKER = "h6_b2l_synthetic_fixture"
LEDGER = "level2-budget.json"
LOCK = LEDGER + ".lock"


def safe_entry(entry, kind, mode):
    if ((entry.st_mode, entry.st_uid, entry.st_gid) != (kind | mode, 0, 0)
            or (kind == stat.S_IFREG and entry.st_nlink != 1)):
        raise PermissionError("B2L_FIXTURE_LAYOUT")
    return entry.st_dev, entry.st_ino


def check_acl(fd, kind):
    names = ["system.posix_acl_access"]
    if kind == stat.S_IFDIR:
        names.append("system.posix_acl_default")
    for name in names:
        try:
            os.getxattr(fd, name)
        except OSError as exc:
            if exc.errno not in (errno.ENODATA, errno.ENOTSUP):
                raise
        else:
            raise PermissionError("B2L_FIXTURE_ACL")


@contextmanager
def entry(path, kind, mode, parent=None):
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_NOATIME
    if kind == stat.S_IFDIR:
        flags |= os.O_DIRECTORY
    fd = os.open(path, flags, dir_fd=parent)
    try:
        check_current(path, fd, kind, mode, parent)
        check_acl(fd, kind)
        yield fd
    finally:
        os.close(fd)


def check_current(path, fd, kind, mode, parent=None):
    opened = safe_entry(os.fstat(fd), kind, mode)
    named = safe_entry(os.stat(path, dir_fd=parent, follow_symlinks=False), kind, mode)
    if opened != named:
        raise PermissionError("B2L_FIXTURE_INODE_CHANGED")
    return opened


def acquire_shared(fd):
    deadline = time.monotonic() + LOCK_WAIT
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
            return
        except BlockingIOError:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("B2L_HEALTH_LOCK_BUSY") from None
            time.sleep(min(remaining, 0.01))


def classify(ledger):
    if ledger.get(MARKER) is not True:
        raise ValueError("B2L_SYNTHETIC_MARKER_REQUIRED")
    permits = ledger.get("one_shot_permits", {})
    shots = {task for task, row in ledger["tasks"].items() if row.get("one_shot") is True}
    if not permits and not shots:
        return "IDLE_NO_PERMIT"
    task_id, = permits
    permit = permits[task_id]
    if (not writer.TASK_ID.fullmatch(task_id) or permit["model"] != one_shot.MODEL
            or not writer.SHA256.fullmatch(permit["key_hash"])
            or not writer.SHA256.fullmatch(permit["fingerprint"])):
        raise ValueError("B2L_PERMIT_LAYOUT")
    quote = p0.checked_quote(permit)
    if permit["state"] == "ready" and not shots and task_id not in ledger["tasks"]:
        return "IDLE_NO_PERMIT" if p0.utc_date(quote["valid_until"]) <= datetime.now(timezone.utc) else "STARTUP_ONLY"
    if permit["state"] != "consumed" or shots != {task_id}:
        raise ValueError("B2L_PERMIT_RELATION")
    task = ledger["tasks"][task_id]
    day = ledger["days"][task["day"]]
    if (task["fingerprint"] != permit["fingerprint"] or task["key_hash"] != permit["key_hash"]
            or task["provider_scope"] != quote or type(task["attempt"]) is not int
            or not 1 <= task["attempt"] <= ledger["attempts"] or day["attempts"] < 1
            or one_shot.usd(task["reserved_usd"]) != one_shot.usd(one_shot.RESERVE_USD)
            or one_shot.usd(day["reserved_usd"]) < one_shot.usd(one_shot.RESERVE_USD)
            or p0.utc_date(permit["consumed_at"]) >= p0.utc_date(permit["expires_at"])):
        raise ValueError("B2L_TASK_RELATION")
    if task["state"] in ("inflight", "outcome_unknown"):
        return "RECONCILE_REQUIRED"
    if task["state"] == "usage_recorded":
        return "SETTLED"
    raise ValueError("B2L_TASK_STATE")


class Health:
    def __init__(self, root):
        self.root = root
        self.lock_id = None
        try:
            with entry(root, stat.S_IFDIR, 0o700) as base:
                with entry("mock-ledger", stat.S_IFDIR, 0o700, base) as directory:
                    with entry(LOCK, stat.S_IFREG, 0o600, directory) as lock:
                        self.lock_id = safe_entry(os.fstat(lock), stat.S_IFREG, 0o600)
        except OSError:
            # Still bind the authenticated endpoint to report an opaque blocked state.
            pass

    def read(self):
        with entry(self.root, stat.S_IFDIR, 0o700) as base:
            with entry("mock-ledger", stat.S_IFDIR, 0o700, base) as directory:
                with entry(LOCK, stat.S_IFREG, 0o600, directory) as lock:
                    if self.lock_id != check_current(LOCK, lock, stat.S_IFREG, 0o600, directory):
                        raise PermissionError("B2L_STABLE_LOCK_CHANGED")
                    acquire_shared(lock)
                    with entry(LEDGER, stat.S_IFREG, 0o600, directory) as ledger:
                        if os.fstat(ledger).st_dev != self.lock_id[0]:
                            raise PermissionError("B2L_FIXTURE_DEVICE")
                        with os.fdopen(os.dup(ledger), "rb") as stream:
                            value = one_shot.decode_ledger(stream.read(one_shot.MAX_LEDGER_BYTES + 1))
                        result = classify(value)
                        check_current(LEDGER, ledger, stat.S_IFREG, 0o600, directory)
                    check_current(LOCK, lock, stat.S_IFREG, 0o600, directory)
                    check_current("mock-ledger", directory, stat.S_IFDIR, 0o700, base)
                check_current(self.root, base, stat.S_IFDIR, 0o700)
        return result

    def dispatch(self, _, request):
        if request.keys() != REQUEST.keys() or request != REQUEST or type(request["version"]) is not int:
            raise ValueError("B2L_HEALTH_ONLY")
        try:
            status = self.read()
        except TimeoutError:
            status = "UNAVAILABLE"
        except (OSError, ValueError, RuntimeError, TypeError, KeyError, AttributeError, OverflowError):
            status = "BLOCKED"
        return {"version": 1, "healthy": status in ENABLED, "status": status}


def read_fixture_key(root):
    with entry(root, stat.S_IFDIR, 0o700) as base:
        with entry("synthetic-ipc.key", stat.S_IFREG, 0o400, base) as key_fd:
            key = os.read(key_fd, ipc.PROOF_BYTES + 1)
    if len(key) != ipc.PROOF_BYTES:
        raise ValueError("B2L_FIXTURE_KEY_LENGTH")
    return key


def serve(root):
    if (root.parent != Path("/tmp") or not root.name.startswith("h6-b2l-") or root.resolve() != root
            or (os.geteuid(), os.getegid()) != (0, 0)):
        raise PermissionError("B2L_LOCAL_ROOT_FIXTURE_ONLY")
    key = read_fixture_key(root)
    health = Health(root)
    writer.listen(root / "ipc" / "writer.sock", root / "mock-ledger" / LEDGER, 0, 0, 0o700, 0o600,
                  lambda conn, path: ipc.handle_exchange(conn, path, key, DOMAIN, health.dispatch))


def call(address, key):
    status = ipc.exchange(address, key, DOMAIN, REQUEST)
    if (not isinstance(status, dict) or status.keys() != {"version", "healthy", "status"}
            or type(status["version"]) is not int or status["version"] != 1
            or not isinstance(status["status"], str) or status["status"] not in STATUSES
            or status["healthy"] is not (status["status"] in ENABLED)):
        raise ValueError("B2L_HEALTH_RESPONSE")
    return status
