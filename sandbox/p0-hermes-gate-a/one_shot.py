"""Fail-closed, mock-testable admission on the existing P0 ledger format.

The caller must dispatch only after admit() returns 'admitted'. Never refund an
unknown outcome. The adapter and this module lock the same .json.lock inode.
"""

from __future__ import annotations

import fcntl
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

MODEL = "gpt-6-luna"
RESERVE_USD = 0.0035


def usd(value: int | float) -> Decimal:
    if type(value) not in (int, float):
        raise RuntimeError("LEDGER_AMOUNT_INVALID")
    amount = Decimal(str(value))
    if not amount.is_finite() or amount < 0:
        raise RuntimeError("LEDGER_AMOUNT_INVALID")
    return amount


@contextmanager
def locked(path: Path):
    lock_path = path.with_suffix(path.suffix + ".lock")
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        os.fchmod(fd, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield json.loads(path.read_text(encoding="utf-8"))
    finally:
        os.close(fd)


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
          now: datetime | None = None, *, stage_a: bool = False) -> str:
    """Consume a pre-created scoped permit and reserve in one ledger commit.

    Permit must already be stored in ledger['one_shot_permits'][task_id] with
    key_hash, fingerprint, model, expires_at (UTC ISO), state='ready'. This
    function never creates a permit or a ledger. The global switch stays ON.
    """
    with locked(path) as ledger:
        if stage_a and ledger.get("h6_stage_a_fixture") is not True:
            raise RuntimeError("STAGE_A_FIXTURE_REQUIRED")
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        if ledger.get("model") != MODEL or ledger.get("max_calls") != 5:
            raise RuntimeError("LEDGER_MISMATCH")
        if ledger.get("kill_switch") is not True:
            raise RuntimeError("KILL_SWITCH_NOT_ON")
        if ledger.get("caps_usd") != {"daily": 0.05, "total": 0.05, "job": 0.01}:
            raise RuntimeError("CAP_MISMATCH")
        permits = ledger.get("one_shot_permits", {})
        permit = permits.get(task_id)
        if not permit or permit.get("state") != "ready":
            raise RuntimeError("PERMIT_UNAVAILABLE")
        if len(permits) != 1 or any(row.get("one_shot") is True for row in ledger["tasks"].values()):
            raise RuntimeError("ONE_SHOT_LIMIT")
        if permit.get("key_hash") != key_hash or permit.get("fingerprint") != fingerprint or permit.get("model") != MODEL:
            raise RuntimeError("PERMIT_SCOPE_MISMATCH")
        if stage_a:
            count = permit.get("mock_input_tokens")
            if type(count) is not int or not 0 < count <= 4_000:
                raise RuntimeError("MOCK_INPUT_COUNT_INVALID")
        expiry = datetime.fromisoformat(permit["expires_at"])
        if expiry.tzinfo is None or now >= expiry:
            raise RuntimeError("PERMIT_EXPIRED")
        attempts = ledger["attempts"]
        if task_id in ledger["tasks"] or type(attempts) is not int or not 0 <= attempts < 5:
            raise RuntimeError("ATTEMPT_LIMIT")
        day = now.date().isoformat()
        day_state = ledger["days"].get(day, {"attempts": 0, "reserved_usd": 0.0, "actual_usd": 0.0})
        reserve = usd(RESERVE_USD)
        total = usd(ledger["reserved_usd"]) + reserve
        daily = usd(day_state["reserved_usd"]) + reserve
        if (reserve > Decimal("0.01") or max(total, daily) > Decimal("0.05")
                or usd(ledger["actual_usd"]) > usd(ledger["reserved_usd"])
                or usd(day_state["actual_usd"]) > usd(day_state["reserved_usd"])):
            raise RuntimeError("BUDGET_CAP")
        permit["state"] = "consumed"
        permit["consumed_at"] = now.isoformat()
        ledger["attempts"] += 1
        ledger["reserved_usd"] = float(total)
        day_state["attempts"] += 1
        day_state["reserved_usd"] = float(daily)
        ledger["days"][day] = day_state
        ledger["tasks"][task_id] = {"fingerprint": fingerprint, "state": "inflight", "one_shot": True,
                                     "attempt": ledger["attempts"], "reserved_usd": RESERVE_USD, "day": day}
        _durable_write(path, ledger)
        return "admitted"


def settle_mock(path: Path, task_id: str, fingerprint: str, outcome: str,
                usage: dict | None = None, *, stage_a: bool = False) -> None:
    """Persist terminal mock evidence without counting it as provider spend."""
    if "mock-ledger" not in path.resolve().parts:
        raise RuntimeError("MOCK_LEDGER_REQUIRED")
    with locked(path) as ledger:
        if stage_a and ledger.get("h6_stage_a_fixture") is not True:
            raise RuntimeError("STAGE_A_FIXTURE_REQUIRED")
        permit = ledger["one_shot_permits"][task_id]
        task = ledger["tasks"][task_id]
        if (ledger["kill_switch"] is not True or permit["state"] != "consumed"
                or permit["fingerprint"] != fingerprint or task["fingerprint"] != fingerprint):
            raise RuntimeError("SETTLEMENT_SCOPE_MISMATCH")
        if task["state"] != "inflight":
            if task["state"] == outcome and task["mock_usage"] == usage:
                return
            raise RuntimeError("SETTLEMENT_ALREADY_RECORDED")
        task.update(state=outcome, mock_usage=usage)
        _durable_write(path, ledger)
