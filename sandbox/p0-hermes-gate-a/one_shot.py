"""Fail-closed, mock-testable admission on the existing P0 ledger format.

The caller must dispatch only after admit() returns 'admitted'. Never refund an
unknown outcome. The adapter and this module lock the same .json.lock inode.
"""

from __future__ import annotations

import fcntl
import json
import math
import os
import stat
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

MODEL = "gpt-6-luna"
RESERVE_USD = 0.0035
CAPS = {"daily": 0.05, "total": 0.05, "job": 0.01}
MAX_CALLS = 5
MAX_LEDGER_BYTES = 1024 * 1024


def usd(value: int | float) -> Decimal:
    if type(value) not in (int, float):
        raise RuntimeError("LEDGER_AMOUNT_INVALID")
    amount = Decimal(str(value))
    if not amount.is_finite() or amount < 0:
        raise RuntimeError("LEDGER_AMOUNT_INVALID")
    return amount


def unique_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("LEDGER_DUPLICATE_KEY")
        value[key] = item
    return value


def reject_nonfinite(_):
    raise RuntimeError("LEDGER_AMOUNT_INVALID")


def finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        reject_nonfinite(text)
    return value


def read_ledger(path: Path) -> tuple[dict, bytes]:
    """Read one complete v1 record from the current pathname, rejecting ambiguous JSON."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("LEDGER_NOT_REGULAR")
        raw = stream.read(MAX_LEDGER_BYTES + 1)
    if len(raw) > MAX_LEDGER_BYTES:
        raise ValueError("LEDGER_TOO_LARGE")
    ledger = json.loads(raw, object_pairs_hook=unique_keys,
                        parse_constant=reject_nonfinite, parse_float=finite_float)
    if (not isinstance(ledger, dict) or type(ledger.get("schema_version")) is not int
            or ledger["schema_version"] != 1 or ledger.get("model") != MODEL
            or type(ledger.get("max_calls")) is not int or ledger["max_calls"] != MAX_CALLS):
        raise RuntimeError("LEDGER_MISMATCH")
    if ledger.get("caps_usd") != CAPS:
        raise RuntimeError("CAP_MISMATCH")
    if ledger.get("kill_switch") is not True:
        raise RuntimeError("KILL_SWITCH_NOT_ON")
    for key in ("tasks", "days"):
        if not isinstance(ledger.get(key), dict) or any(not isinstance(row, dict) for row in ledger[key].values()):
            raise RuntimeError("LEDGER_ROW_INVALID")
    if not isinstance(ledger.get("one_shot_permits", {}), dict):
        raise RuntimeError("LEDGER_PERMITS_INVALID")
    totals = validate_budget(ledger)
    for day in ledger["days"].values():
        if any(value > aggregate for value, aggregate in zip(validate_budget(day), totals, strict=True)):
            raise RuntimeError("LEDGER_DAY_TOTAL_MISMATCH")
    return ledger, raw


def validate_budget(row):
    attempts = row.get("attempts")
    if type(attempts) is not int or not 0 <= attempts <= MAX_CALLS:
        raise RuntimeError("ATTEMPT_LIMIT")
    reserved, actual = usd(row.get("reserved_usd")), usd(row.get("actual_usd"))
    if reserved > usd(CAPS["total"]) or actual > reserved:
        raise RuntimeError("BUDGET_CAP")
    return attempts, reserved, actual


@contextmanager
def locked(path: Path):
    lock_path = path.with_suffix(path.suffix + ".lock")
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("LEDGER_LOCK_NOT_REGULAR")
        os.fchmod(fd, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX)
        ledger, _ = read_ledger(path)
        yield ledger
    finally:
        os.close(fd)


def _durable_write(path: Path, value: dict) -> None:
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, sort_keys=True, separators=(",", ":"), allow_nan=False)
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
        permits = ledger.get("one_shot_permits", {})
        permit = permits.get(task_id)
        if not isinstance(permit, dict) or permit.get("state") != "ready":
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
        if task_id in ledger["tasks"] or ledger["attempts"] >= MAX_CALLS:
            raise RuntimeError("ATTEMPT_LIMIT")
        day = now.date().isoformat()
        day_state = ledger["days"].get(day, {"attempts": 0, "reserved_usd": 0.0, "actual_usd": 0.0})
        reserve = usd(RESERVE_USD)
        total = usd(ledger["reserved_usd"]) + reserve
        daily = usd(day_state["reserved_usd"]) + reserve
        if reserve > usd(CAPS["job"]) or total > usd(CAPS["total"]) or daily > usd(CAPS["daily"]):
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
    if not ((outcome == "usage_recorded" and isinstance(usage, dict))
            or (outcome == "outcome_unknown" and usage is None)):
        raise RuntimeError("MOCK_SETTLEMENT_OUTCOME")
    with locked(path) as ledger:
        if stage_a and ledger.get("h6_stage_a_fixture") is not True:
            raise RuntimeError("STAGE_A_FIXTURE_REQUIRED")
        permit = ledger["one_shot_permits"][task_id]
        task = ledger["tasks"][task_id]
        if (permit["state"] != "consumed" or permit["model"] != MODEL or task.get("one_shot") is not True
                or permit["fingerprint"] != fingerprint or task["fingerprint"] != fingerprint
                or usd(task["reserved_usd"]) != usd(RESERVE_USD)
                or type(task.get("attempt")) is not int or not 1 <= task["attempt"] <= ledger["attempts"]):
            raise RuntimeError("SETTLEMENT_SCOPE_MISMATCH")
        if usd(ledger["days"][task["day"]]["reserved_usd"]) < usd(RESERVE_USD):
            raise RuntimeError("SETTLEMENT_RESERVATION_MISSING")
        if task["state"] != "inflight":
            if task["state"] == outcome and task["mock_usage"] == usage:
                return
            raise RuntimeError("SETTLEMENT_ALREADY_RECORDED")
        task.update(state=outcome, mock_usage=usage)
        _durable_write(path, ledger)
