"""Fail-closed, mock-testable admission on the existing P0 ledger format.

The caller must dispatch only after admit() returns 'admitted'. Never refund an
unknown outcome. The adapter and this module lock the same .json.lock inode.
"""

from __future__ import annotations

import fcntl
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

MODEL = "gpt-6-luna"
RESERVE_USD = 0.0035


def _durable_write(path: Path, value: dict) -> None:
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, sort_keys=True, separators=(",", ":"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def admit(path: Path, task_id: str, key_hash: str, fingerprint: str,
          now: datetime | None = None) -> str:
    """Consume a pre-created scoped permit and reserve in one ledger commit.

    Permit must already be stored in ledger['one_shot_permits'][task_id] with
    key_hash, fingerprint, model, expires_at (UTC ISO), state='ready'. This
    function never creates a permit or a ledger. The global switch stays ON.
    """
    now = now or datetime.now(timezone.utc)
    lock_path = path.with_suffix(path.suffix + ".lock")
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        os.fchmod(fd, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX)
        ledger = json.loads(path.read_text(encoding="utf-8"))
        if ledger.get("model") != MODEL or ledger.get("max_calls") != 5:
            raise RuntimeError("LEDGER_MISMATCH")
        if ledger.get("kill_switch") is not True:
            raise RuntimeError("KILL_SWITCH_NOT_ON")
        if ledger.get("caps_usd") != {"daily": 0.05, "total": 0.05, "job": 0.01}:
            raise RuntimeError("CAP_MISMATCH")
        permit = ledger.get("one_shot_permits", {}).get(task_id)
        if not permit or permit.get("state") != "ready":
            raise RuntimeError("PERMIT_UNAVAILABLE")
        if permit.get("key_hash") != key_hash or permit.get("fingerprint") != fingerprint or permit.get("model") != MODEL:
            raise RuntimeError("PERMIT_SCOPE_MISMATCH")
        expiry = datetime.fromisoformat(permit["expires_at"])
        if expiry.tzinfo is None or now >= expiry:
            raise RuntimeError("PERMIT_EXPIRED")
        if task_id in ledger["tasks"] or int(ledger["attempts"]) >= 5:
            raise RuntimeError("ATTEMPT_LIMIT")
        day = now.date().isoformat()
        day_state = ledger["days"].get(day, {"attempts": 0, "reserved_usd": 0.0, "actual_usd": 0.0})
        if RESERVE_USD > 0.01 or float(ledger["reserved_usd"]) + RESERVE_USD > 0.05 or float(day_state["reserved_usd"]) + RESERVE_USD > 0.05:
            raise RuntimeError("BUDGET_CAP")
        permit["state"] = "consumed"
        permit["consumed_at"] = now.isoformat()
        ledger["attempts"] += 1
        ledger["reserved_usd"] = round(float(ledger["reserved_usd"]) + RESERVE_USD, 8)
        day_state["attempts"] += 1
        day_state["reserved_usd"] = round(float(day_state["reserved_usd"]) + RESERVE_USD, 8)
        ledger["days"][day] = day_state
        ledger["tasks"][task_id] = {"fingerprint": fingerprint, "state": "inflight", "attempt": ledger["attempts"], "reserved_usd": RESERVE_USD, "day": day}
        _durable_write(path, ledger)
        return "admitted"
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
