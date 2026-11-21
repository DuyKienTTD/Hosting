#!/usr/bin/env python3
"""Mock-only GATE A end-to-end and idempotency acceptance tests."""

from __future__ import annotations

import concurrent.futures
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


BRIDGE = "http://127.0.0.1:8080/v1/reason"
N8N = "http://n8n-p0-sandbox:5678/webhook/ttd-p0-fake-ads-audit-v1"
TOKEN = Path("/run/secrets/existing_p0_token").read_text(encoding="utf-8").strip()
CAPTURE_INDEX = Path("/opt/ttd/capture/capture-index.json")


def request(url: str, body: dict, token: str | None = TOKEN, timeout: float = 25) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(
        url,
        data=json.dumps(body, separators=(",", ":")).encode(),
        method="POST",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def count() -> int:
    if not CAPTURE_INDEX.exists():
        return 0
    return int(json.loads(CAPTURE_INDEX.read_text(encoding="utf-8"))["physical_requests"])


def payload(task_id: str, *, simulate: str | None = None, spend: int = 25) -> dict:
    value = {
        "task_id": task_id,
        "correlation_id": "corr-" + task_id,
        "input": {"channel": "ads", "spend": spend, "clicks": 7},
    }
    if simulate:
        value["simulate"] = simulate
    return value


stamp = str(int(time.time()))
results: dict[str, object] = {}

# n8n ingress authentication and schema gates.
results["n8n_missing_auth"] = request(N8N, payload("auth-missing-" + stamp), None)[0]
results["n8n_wrong_auth"] = request(N8N, payload("auth-wrong-" + stamp), "wrong-token")[0]
invalid = payload("schema-invalid-" + stamp)
invalid["input"]["channel"] = "production"
results["n8n_invalid_schema"] = request(N8N, invalid)[0]

# Full n8n -> bridge -> real Hermes -> guard -> mock -> callback path.
normal = payload("e2e-success-" + stamp)
before = count()
status, first = request(N8N, normal)
after_first = count()
replay_status, replay = request(N8N, normal)
after_replay = count()
results["e2e"] = {
    "status": status,
    "mode": first.get("mode"),
    "paid_inference": first.get("paid_inference"),
    "replay_status": replay_status,
    "replayed": replay.get("replayed"),
    "physical_delta": after_first - before,
    "replay_delta": after_replay - after_first,
}

# Same task id with changed input must fail closed and make no provider request.
conflict = payload(normal["task_id"], spend=26)
conflict_before = count()
results["idempotency_conflict"] = {
    "status": request(BRIDGE, conflict)[0],
    "physical_delta": count() - conflict_before,
}

# Synthetic provider error: one physical request, no retry.
error_case = payload("provider-error-" + stamp, simulate="provider_error")
error_before = count()
results["provider_error"] = {
    "status": request(BRIDGE, error_case)[0],
    "physical_delta": count() - error_before,
}

# A disconnected client must not cause another physical request on replay.
timeout_case = payload("client-timeout-" + stamp, simulate="delay")
timeout_before = count()
try:
    request(BRIDGE, timeout_case, timeout=0.2)
    timeout_observed = False
except (TimeoutError, urllib.error.URLError):
    timeout_observed = True
time.sleep(3)
timeout_status, timeout_replay = request(BRIDGE, timeout_case)
results["client_timeout"] = {
    "observed": timeout_observed,
    "replay_status": timeout_status,
    "replayed": timeout_replay.get("replayed"),
    "physical_delta": count() - timeout_before,
}

# Concurrent identical arrivals may return 200/202, but only one provider request is allowed.
concurrent_case = payload("concurrent-" + stamp, simulate="delay")
concurrent_before = count()
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    concurrent_statuses = list(pool.map(lambda _: request(BRIDGE, concurrent_case)[0], range(5)))
time.sleep(0.5)
final_status, final_replay = request(BRIDGE, concurrent_case)
results["concurrency"] = {
    "statuses": sorted(concurrent_statuses),
    "final_status": final_status,
    "replayed": final_replay.get("replayed"),
    "physical_delta": count() - concurrent_before,
}

assert results["n8n_missing_auth"] == 401, results
assert results["n8n_wrong_auth"] == 401, results
assert results["n8n_invalid_schema"] == 422, results
assert results["e2e"] == {
    "status": 200,
    "mode": "hermes_mock",
    "paid_inference": False,
    "replay_status": 200,
    "replayed": True,
    "physical_delta": 1,
    "replay_delta": 0,
}, results
assert results["idempotency_conflict"] == {"status": 409, "physical_delta": 0}, results
assert results["provider_error"] == {"status": 502, "physical_delta": 1}, results
assert results["client_timeout"] == {
    "observed": True,
    "replay_status": 200,
    "replayed": True,
    "physical_delta": 1,
}, results
assert results["concurrency"]["final_status"] == 200, results
assert results["concurrency"]["replayed"] is True, results
assert results["concurrency"]["physical_delta"] == 1, results
assert set(results["concurrency"]["statuses"]).issubset({200, 202}), results

print(json.dumps({"result": "PASS", "tests": results}, sort_keys=True))
