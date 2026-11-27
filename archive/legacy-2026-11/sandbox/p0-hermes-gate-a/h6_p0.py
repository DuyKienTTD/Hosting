"""P0 v1 transactions for one narrowly scoped, pre-authorized provider request."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib

import h6_writer
import one_shot
from mock_contract import MAX_INPUT, MAX_OUTPUT

# Snapshot of the reviewed Standard candidate rates, not a pricing discovery API.
PRICING_ID = "h5-luna-standard-30m-v1"
QUOTE_FIELDS = {"approval_sha256", "counted_fingerprint", "input_tokens", "max_output_tokens",
                "pricing_id", "service_tier", "valid_until"}
SCOPE_FIELDS = {"task_id", "key_hash", "fingerprint"}
MAX_QUOTE_REMAINING = timedelta(minutes=15)


def check_unmarked(ledger):
    if "h6_stage_a_fixture" in ledger:
        raise ValueError("P0_PROVIDER_REQUIRES_UNMARKED_V1")


def utc_date(value):
    if not isinstance(value, str) or len(value) > 48:
        raise ValueError("P0_TIME_FORMAT")
    parsed = datetime.fromisoformat(value)
    if parsed.utcoffset() != timedelta(0):
        raise ValueError("P0_TIME_REQUIRES_UTC")
    return parsed


def checked_quote(permit, now=None):
    quote = permit["provider_scope"]
    if (not isinstance(quote, dict) or set(quote) != QUOTE_FIELDS or "mock_input_tokens" in permit
            or not h6_writer.SHA256.fullmatch(quote["approval_sha256"])
            or quote["counted_fingerprint"] != permit["fingerprint"]
            or quote["pricing_id"] != PRICING_ID or quote["service_tier"] != "default"
            or type(quote["max_output_tokens"]) is not int or quote["max_output_tokens"] != MAX_OUTPUT
            or type(quote["input_tokens"]) is not int or not 0 < quote["input_tokens"] <= MAX_INPUT):
        raise ValueError("P0_PROVIDER_SCOPE")
    expiry = utc_date(quote["valid_until"])
    if expiry > utc_date(permit["expires_at"]) or (
        now is not None and not now < expiry <= now + MAX_QUOTE_REMAINING
    ):
        raise RuntimeError("P0_PROVIDER_QUOTE_EXPIRED_OR_UNBOUNDED")
    # Upper bound for the approved count, all at 30m cache-write price, plus
    # maximum output and a 10% regional margin. Reserve remains the P0 constant.
    worst = (quote["input_tokens"] * Decimal("0.125") + MAX_OUTPUT * Decimal("0.50")) * Decimal("1.10") / 1_000_000
    if worst > one_shot.usd(one_shot.RESERVE_USD):
        raise RuntimeError("P0_PROVIDER_RESERVE_TOO_LOW")
    return quote


def authorize(ledger, permit, now):
    check_unmarked(ledger)
    return checked_quote(permit, now)


def snapshot(path):
    one_shot.require_root_layout(path)
    ledger, raw = one_shot.read_ledger(path)
    check_unmarked(ledger)
    return {key: ledger[key] for key in h6_writer.SUMMARY_FIELDS - {"sha256"}} | {
        "sha256": hashlib.sha256(raw).hexdigest()}


def require_ready(path):
    one_shot.require_root_layout(path)
    ledger, _ = one_shot.read_ledger(path)
    check_unmarked(ledger)
    task_id, = ledger.get("one_shot_permits", {})
    permit = ledger["one_shot_permits"][task_id]
    if (not h6_writer.TASK_ID.fullmatch(task_id) or permit["state"] != "ready"
            or permit["model"] != one_shot.MODEL or not h6_writer.SHA256.fullmatch(permit["key_hash"])
            or not h6_writer.SHA256.fullmatch(permit["fingerprint"]) or task_id in ledger["tasks"]
            or any(row.get("one_shot") is True for row in ledger["tasks"].values())
            or ledger["attempts"] >= one_shot.MAX_CALLS):
        raise RuntimeError("P0_PROVIDER_NOT_READY")
    checked_quote(permit, datetime.now(timezone.utc))


def settle(path, task_id, key_hash, fingerprint, outcome, usage):
    if outcome == "usage_recorded":
        h6_writer.validate_usage(usage)
    elif outcome != "outcome_unknown" or usage is not None:
        raise ValueError("P0_PROVIDER_OUTCOME")
    with one_shot.locked(path, existing_root=True) as ledger:
        check_unmarked(ledger)
        permit = ledger["one_shot_permits"][task_id]
        task = ledger["tasks"][task_id]
        quote = checked_quote(permit)
        if (permit["state"] != "consumed" or permit["model"] != one_shot.MODEL or task.get("one_shot") is not True
                or permit["fingerprint"] != fingerprint or task["fingerprint"] != fingerprint
                or permit["key_hash"] != key_hash or task["key_hash"] != key_hash or task["provider_scope"] != quote
                or one_shot.usd(task["reserved_usd"]) != one_shot.usd(one_shot.RESERVE_USD)
                or type(task["attempt"]) is not int or not 1 <= task["attempt"] <= ledger["attempts"]):
            raise ValueError("P0_PROVIDER_SETTLEMENT_SCOPE")
        day = ledger["days"][task["day"]]
        if not 1 <= day["attempts"] <= ledger["attempts"] or one_shot.usd(day["reserved_usd"]) < one_shot.usd(one_shot.RESERVE_USD):
            raise ValueError("P0_PROVIDER_RESERVATION_MISSING")
        if task["state"] != "inflight":
            if task["state"] == outcome and task["provider_usage"] == usage:
                return True
            raise RuntimeError("P0_PROVIDER_SETTLEMENT_CONFLICT")
        if usage is not None:
            if usage["input_tokens"] > quote["input_tokens"]:
                raise ValueError("P0_PROVIDER_USAGE_ABOVE_COUNT")
            estimate = Decimal(usage["estimated_cost_usd"])
            for bucket in (day, ledger):
                combined = one_shot.usd(bucket["actual_usd"]) + estimate
                if combined > one_shot.usd(bucket["reserved_usd"]):
                    raise RuntimeError("P0_PROVIDER_SETTLEMENT_CAP")
                bucket["actual_usd"] = float(combined)
            task["actual_cost_usd"] = float(estimate)
        task.update(state=outcome, provider_usage=usage, invoice_status="unreconciled")
        one_shot._durable_write(path, ledger)
        return True


def dispatch(path, request):
    op = request["op"]
    keys = set(request) - {"op"}
    if op == "snapshot" and not keys:
        return snapshot(path)
    allowed = {"admit": SCOPE_FIELDS, "settle": SCOPE_FIELDS | {"outcome", "usage"}}
    if op not in allowed or keys != allowed[op]:
        raise ValueError("P0_PROVIDER_OPERATION")
    task, key_hash, fingerprint = (request[name] for name in ("task_id", "key_hash", "fingerprint"))
    if not (h6_writer.TASK_ID.fullmatch(task) and h6_writer.SHA256.fullmatch(key_hash)
            and h6_writer.SHA256.fullmatch(fingerprint)):
        raise ValueError("P0_PROVIDER_REQUEST_SCOPE")
    if op == "admit":
        return one_shot.admit(path, task, key_hash, fingerprint, permit_check=authorize)
    return settle(path, task, key_hash, fingerprint, request["outcome"], request["usage"])
