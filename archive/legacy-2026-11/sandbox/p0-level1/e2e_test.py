#!/usr/bin/env python3
"""Secret-safe E2E checks for the private Level 1 sandbox."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


WEBHOOK = "http://n8n-p0-sandbox:5678/webhook/ttd-p0-fake-ads-audit-v1"
REASONER = "http://127.0.0.1:8080/v1/reason"
TOKEN = os.environ["P0_TOKEN"]


def post(url: str, payload: dict, token: str | None, timeout: float = 12) -> tuple[int, dict, float]:
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, separators=(",", ":")).encode(),
        headers=headers,
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(16384)
            status = response.status
    except urllib.error.HTTPError as error:
        raw = error.read(16384)
        status = error.code
    elapsed = time.monotonic() - started
    try:
        body = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        body = {"unparsed": True}
    return status, body, elapsed


def record(results: list[dict], name: str, condition: bool, **details: object) -> None:
    results.append({"case": name, "pass": bool(condition), **details})
    if not condition:
        raise AssertionError(name)


def main() -> None:
    results: list[dict] = []

    status, body, elapsed = post(WEBHOOK, {}, None)
    record(results, "missing_auth", status == 401, http=status, elapsed_ms=int(elapsed * 1000))

    status, body, elapsed = post(WEBHOOK, {}, "invalid")
    record(results, "wrong_auth", status == 401, http=status, elapsed_ms=int(elapsed * 1000))

    invalid = {
        "phase": "start",
        "task_id": "p0-invalid-schema",
        "correlation_id": "corr-invalid-schema",
        "input": {"channel": "seo", "spend": 10, "clicks": 2},
    }
    status, body, elapsed = post(WEBHOOK, invalid, TOKEN)
    record(results, "invalid_input_schema", status == 422, http=status, elapsed_ms=int(elapsed * 1000))

    valid = {
        "phase": "start",
        "task_id": "p0-e2e-valid-01",
        "correlation_id": "corr-p0-e2e-valid-01",
        "input": {"channel": "ads", "spend": 125.5, "clicks": 25},
    }
    status, body, elapsed = post(WEBHOOK, valid, TOKEN)
    valid_ok = (
        status == 200
        and body.get("accepted") is True
        and body.get("callback_http_status") == 200
        and body.get("replayed") is False
        and body.get("mode") == "mock"
        and body.get("paid_inference") is False
        and len(body.get("result_hash", "")) == 64
    )
    record(results, "valid_e2e_callback", valid_ok, http=status, elapsed_ms=int(elapsed * 1000))

    status, body, elapsed = post(WEBHOOK, valid, TOKEN)
    replay_ok = status == 200 and body.get("replayed") is True and body.get("callback_repeated") is False
    record(results, "idempotent_replay", replay_ok, http=status, elapsed_ms=int(elapsed * 1000))

    conflict = dict(valid)
    conflict["input"] = {"channel": "ads", "spend": 126.5, "clicks": 25}
    status, body, elapsed = post(REASONER, conflict, TOKEN)
    record(results, "idempotency_conflict", status == 409, http=status, elapsed_ms=int(elapsed * 1000))

    invalid_output = {
        "phase": "start",
        "task_id": "p0-e2e-invalid-output-01",
        "correlation_id": "corr-p0-e2e-invalid-output-01",
        "input": {"channel": "ads", "spend": 10, "clicks": 2},
        "simulate": "invalid_output",
    }
    status, body, elapsed = post(REASONER, invalid_output, TOKEN)
    record(results, "invalid_output_rejected", status == 502, http=status, elapsed_ms=int(elapsed * 1000))

    timeout = {
        "phase": "start",
        "task_id": "p0-e2e-timeout-01",
        "correlation_id": "corr-p0-e2e-timeout-01",
        "input": {"channel": "ads", "spend": 50, "clicks": 10},
        "simulate": "timeout",
    }
    status, body, elapsed = post(WEBHOOK, timeout, TOKEN)
    timeout_ok = status == 200 and body.get("accepted") is True and body.get("pending") is True
    record(results, "timeout_retry_deduplicated", timeout_ok, http=status, elapsed_ms=int(elapsed * 1000))

    time.sleep(2.5)
    status, body, elapsed = post(REASONER, timeout, TOKEN)
    timeout_complete_ok = (
        status == 200
        and body.get("replayed") is True
        and body.get("callback_repeated") is False
        and len(body.get("result_hash", "")) == 64
    )
    record(results, "timeout_callback_completed_once", timeout_complete_ok, http=status, elapsed_ms=int(elapsed * 1000))

    print(json.dumps({"suite": "p0_level1_e2e", "pass": True, "cases": results}, separators=(",", ":")))


if __name__ == "__main__":
    main()
