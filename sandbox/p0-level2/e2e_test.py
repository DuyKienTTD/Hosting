#!/usr/bin/env python3
"""Secret-safe Provider E2E tests; exactly one new task can reach OpenAI."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


WEBHOOK = "http://n8n-p0-sandbox:5678/webhook/ttd-p0-fake-ads-audit-v1"
REASONER = os.environ.get("P0_REASONER_URL", "http://reasoner-p0:8080/v1/reason")
TOKEN = os.environ["P0_TOKEN"]
LEDGER = Path(os.environ.get("P0_BUDGET_PATH", "/opt/ttd/state/level2-budget.json"))


def post(url: str, payload: dict, token: str | None, timeout: float = 40) -> tuple[int, dict, int]:
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=json.dumps(payload, separators=(",", ":")).encode(), headers=headers, method="POST")
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw, status = response.read(65536), response.status
    except urllib.error.HTTPError as error:
        raw, status = error.read(65536), error.code
    elapsed_ms = int((time.monotonic() - started) * 1000)
    try:
        return status, json.loads(raw), elapsed_ms
    except (json.JSONDecodeError, UnicodeDecodeError):
        return status, {"unparsed": True}, elapsed_ms


def record(cases: list[dict], name: str, passed: bool, **details: object) -> None:
    cases.append({"case": name, "pass": bool(passed), **details})
    if not passed:
        print(json.dumps({"suite": "p0_level2_provider_e2e", "pass": False, "failed_case": cases[-1]}, separators=(",", ":")))
        raise AssertionError(name)


def main() -> None:
    cases: list[dict] = []
    status, _, elapsed = post(WEBHOOK, {}, None)
    record(cases, "missing_auth_no_paid_call", status == 401, http=status, elapsed_ms=elapsed)
    status, _, elapsed = post(WEBHOOK, {}, "invalid")
    record(cases, "wrong_auth_no_paid_call", status == 401, http=status, elapsed_ms=elapsed)
    invalid = {"phase": "start", "task_id": "p0-l2-invalid", "correlation_id": "corr-p0-l2-invalid", "input": {"channel": "seo", "spend": 10, "clicks": 2}}
    status, _, elapsed = post(WEBHOOK, invalid, TOKEN)
    record(cases, "invalid_schema_no_paid_call", status == 422, http=status, elapsed_ms=elapsed)

    valid = {"phase": "start", "task_id": "p0-level2-provider-01", "correlation_id": "corr-p0-level2-provider-01", "input": {"channel": "ads", "spend": 125.5, "clicks": 25}}
    status, body, elapsed = post(WEBHOOK, valid, TOKEN)
    usage = body.get("usage") or {}
    provider_ok = (
        status == 200 and body.get("accepted") is True
        and isinstance(body.get("replayed"), bool) and body.get("mode") == "openai"
        and (body.get("callback_http_status") == 200 or body.get("replayed") is True)
        and (body.get("paid_inference") is True or body.get("replayed") is True)
        and body.get("provider") == "openai" and str(body.get("model", "")).startswith("gpt-6-luna")
        and 0 <= usage.get("input_tokens", -1) <= 4000 and 0 <= usage.get("output_tokens", -1) <= 2000
        and 0 <= body.get("actual_cost_usd", -1) <= 0.01 and len(body.get("result_hash", "")) == 64
    )
    record(cases, "provider_e2e_authenticated_callback", provider_ok, http=status, elapsed_ms=elapsed, replayed=body.get("replayed"), model=body.get("model"), usage=usage, actual_cost_usd=body.get("actual_cost_usd"), result_hash=body.get("result_hash"))

    status, replay, elapsed = post(WEBHOOK, valid, TOKEN)
    record(cases, "persistent_idempotent_replay", status == 200 and replay.get("replayed") is True and replay.get("callback_repeated") is False, http=status, elapsed_ms=elapsed)
    conflict = dict(valid)
    conflict["input"] = {"channel": "ads", "spend": 126.5, "clicks": 25}
    status, _, elapsed = post(REASONER, conflict, TOKEN)
    record(cases, "idempotency_conflict_no_paid_call", status == 409, http=status, elapsed_ms=elapsed)

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    record(cases, "atomic_budget_attempt_count", ledger.get("attempts") == 1, attempts=ledger.get("attempts"), reserved_usd=ledger.get("reserved_usd"), actual_usd=ledger.get("actual_usd"))
    safe_summary = {
        "suite": "p0_level2_provider_e2e",
        "pass": True,
        "provider_e2e": "PASS",
        "hermes_e2e": "NOT_TESTED_BY_THIS_SUITE",
        "attempts": ledger["attempts"],
        "reserved_usd": ledger["reserved_usd"],
        "actual_usd": ledger["actual_usd"],
        "cases": cases,
    }
    print(json.dumps(safe_summary, separators=(",", ":")))


if __name__ == "__main__":
    main()
