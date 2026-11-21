#!/usr/bin/env python3
"""Cost-gated GPT-6 Luna adapter for the isolated P0 provider E2E test."""

from __future__ import annotations

import fcntl
import hashlib
import hmac
import json
import os
import re
import tempfile
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator


HOST = "0.0.0.0"
PORT = int(os.environ.get("P0_PORT", "8080"))
MODE = os.environ.get("P0_MODE", "openai")
TOKEN = os.environ.get("P0_TOKEN", "")
CALLBACK_URL = os.environ.get("P0_CALLBACK_URL", "")
API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = "gpt-6-luna"
PROVIDER_URL = "https://api.openai.com/v1/responses"
BUDGET_PATH = Path(os.environ.get("P0_BUDGET_PATH", "/opt/ttd/state/level2-budget.json"))
LOCK_PATH = BUDGET_PATH.with_suffix(BUDGET_PATH.suffix + ".lock")

MAX_BODY_BYTES = 8 * 1024
MAX_CALLS = 5
MAX_INPUT_TOKENS = 4000
MAX_OUTPUT_TOKENS = 2000
LIVE_MAX_OUTPUT_TOKENS = 600
TOTAL_CAP_USD = 0.05
DAILY_CAP_USD = 0.05
JOB_CAP_USD = 0.01
# Standard worst case is USD 0.0014 for 4K input + 2K output. The reservation
# adds 2.5x headroom for regional/Fast/cache-write variance and still leaves the
# five-call P0 far below both approved USD 0.05 caps.
RESERVE_USD_PER_ATTEMPT = 0.0035
MAX_PROVIDER_INPUT_SURFACE_BYTES = 2500
ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{3,128}$")

if MODE != "openai":
    raise SystemExit("P0_MODE must be openai for the Level 2 adapter")
if len(TOKEN) < 32 or len(API_KEY) < 20:
    raise SystemExit("sandbox credentials are missing")
if not CALLBACK_URL.startswith("http://n8n-p0-sandbox:5678/"):
    raise SystemExit("callback must target the private n8n sandbox alias")
if RESERVE_USD_PER_ATTEMPT > JOB_CAP_USD:
    raise SystemExit("per-attempt reservation exceeds the approved job cap")


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def utc_day() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def new_ledger() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "model": MODEL,
        "max_calls": MAX_CALLS,
        "caps_usd": {"daily": DAILY_CAP_USD, "total": TOTAL_CAP_USD, "job": JOB_CAP_USD},
        "attempts": 0,
        "reserved_usd": 0.0,
        "actual_usd": 0.0,
        "days": {},
        "tasks": {},
    }


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def locked_ledger() -> Iterator[dict[str, Any]]:
    BUDGET_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = os.open(LOCK_PATH, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        os.fchmod(lock, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        if BUDGET_PATH.exists():
            with BUDGET_PATH.open("r", encoding="utf-8") as handle:
                ledger = json.load(handle)
        else:
            ledger = new_ledger()
        if ledger.get("model") != MODEL or ledger.get("max_calls") != MAX_CALLS:
            raise RuntimeError("P0_LEDGER_CONFIG_MISMATCH")
        yield ledger
        atomic_write(BUDGET_PATH, ledger)
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        os.close(lock)


def admit(task_id: str, fingerprint: str) -> tuple[str, dict[str, Any]]:
    with locked_ledger() as ledger:
        task = ledger["tasks"].get(task_id)
        if task:
            if task.get("fingerprint") != fingerprint:
                return "conflict", task
            return "existing", task
        day = utc_day()
        day_state = ledger["days"].setdefault(day, {"attempts": 0, "reserved_usd": 0.0, "actual_usd": 0.0})
        projected_total = float(ledger["reserved_usd"]) + RESERVE_USD_PER_ATTEMPT
        projected_day = float(day_state["reserved_usd"]) + RESERVE_USD_PER_ATTEMPT
        if int(ledger["attempts"]) >= MAX_CALLS:
            raise RuntimeError("P0_MAX_CALLS")
        if projected_total > TOTAL_CAP_USD or projected_day > DAILY_CAP_USD:
            raise RuntimeError("P0_BUDGET_CAP")
        task = {
            "fingerprint": fingerprint,
            "state": "inflight",
            "attempt": int(ledger["attempts"]) + 1,
            "reserved_usd": RESERVE_USD_PER_ATTEMPT,
            "day": day,
        }
        ledger["attempts"] = int(ledger["attempts"]) + 1
        ledger["reserved_usd"] = round(projected_total, 8)
        day_state["attempts"] = int(day_state["attempts"]) + 1
        day_state["reserved_usd"] = round(projected_day, 8)
        ledger["tasks"][task_id] = task
        return "admitted", dict(task)


def update_task(task_id: str, values: dict[str, Any], actual_usd: float = 0.0) -> dict[str, Any]:
    with locked_ledger() as ledger:
        task = ledger["tasks"][task_id]
        task.update(values)
        if actual_usd:
            day_state = ledger["days"][task["day"]]
            ledger["actual_usd"] = round(float(ledger["actual_usd"]) + actual_usd, 8)
            day_state["actual_usd"] = round(float(day_state["actual_usd"]) + actual_usd, 8)
        return dict(task)


def provider_request(task_id: str, correlation_id: str, input_data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], float, str, str]:
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "signals": {"type": "array", "items": {"type": "string"}},
            "recommendations": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["summary", "signals", "recommendations"],
        "additionalProperties": False,
    }
    prompt = (
        "This is a sandbox test with fictional advertising data only. "
        "Analyze the numbers briefly and return the required JSON. Do not use tools, "
        "external data, real accounts, or personal data. "
        f"task_id={task_id}; correlation_id={correlation_id}; "
        f"channel=ads; spend={float(input_data['spend']):.2f}; clicks={input_data['clicks']}."
    )
    body = {
        "model": MODEL,
        "input": prompt,
        "max_output_tokens": LIVE_MAX_OUTPUT_TOKENS,
        "reasoning": {"effort": "none"},
        "text": {"format": {"type": "json_schema", "name": "ttd_fake_ads_audit", "strict": True, "schema": schema}},
        "store": False,
        "service_tier": "default",
    }
    input_surface = json.dumps({"input": prompt, "text": body["text"]}, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    if len(input_surface) > MAX_PROVIDER_INPUT_SURFACE_BYTES:
        raise RuntimeError("P0_INPUT_BOUND")
    encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        PROVIDER_URL,
        data=encoded,
        method="POST",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "ttd-p0-provider-adapter/2.0",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(512 * 1024)
    payload = json.loads(raw)
    actual_model = str(payload.get("model", ""))
    if actual_model != MODEL and not actual_model.startswith(MODEL + "-"):
        raise RuntimeError("P0_MODEL_MISMATCH")
    output_text = payload.get("output_text")
    if not isinstance(output_text, str):
        parts: list[str] = []
        for item in payload.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                    parts.append(content["text"])
        output_text = "".join(parts)
    result = json.loads(output_text)
    if set(result) != {"summary", "signals", "recommendations"}:
        raise RuntimeError("P0_OUTPUT_SCHEMA")
    if not isinstance(result["summary"], str) or not all(isinstance(x, str) for x in result["signals"] + result["recommendations"]):
        raise RuntimeError("P0_OUTPUT_SCHEMA")
    usage_raw = payload.get("usage") or {}
    input_tokens = int(usage_raw.get("input_tokens", -1))
    output_tokens = int(usage_raw.get("output_tokens", -1))
    input_details = usage_raw.get("input_tokens_details") or {}
    output_details = usage_raw.get("output_tokens_details") or {}
    cached_tokens = int(input_details.get("cached_tokens", 0) or 0)
    reasoning_tokens = int(output_details.get("reasoning_tokens", 0) or 0)
    if not 0 <= input_tokens <= MAX_INPUT_TOKENS or not 0 <= output_tokens <= MAX_OUTPUT_TOKENS:
        raise RuntimeError("P0_TOKEN_CAP")
    uncached_tokens = max(0, input_tokens - cached_tokens)
    actual_usd = (uncached_tokens * 0.10 + cached_tokens * 0.01 + output_tokens * 0.50) / 1_000_000
    usage = {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_tokens,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
    }
    response_id_hash = hashlib.sha256(str(payload.get("id", "")).encode()).hexdigest()
    return result, usage, round(actual_usd, 8), actual_model, response_id_hash


def send_callback(payload: dict[str, Any]) -> tuple[int, str]:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        CALLBACK_URL,
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "ttd-p0-provider-adapter/2.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            response_body = response.read(8192)
            return response.status, hashlib.sha256(response_body).hexdigest()
    except urllib.error.HTTPError as error:
        return error.code, hashlib.sha256(error.read(8192)).hexdigest()
    except urllib.error.URLError:
        return 0, hashlib.sha256(b"").hexdigest()


class Handler(BaseHTTPRequestHandler):
    server_version = "ttd-p0-provider-adapter/2.0"
    sys_version = ""

    def log_message(self, fmt: str, *args: Any) -> None:
        print(json.dumps({"event": "http", "path": self.path, "status": args[1]}), flush=True)

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _authorized(self) -> bool:
        return hmac.compare_digest(self.headers.get("Authorization", "").encode(), f"Bearer {TOKEN}".encode())

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/healthz":
            self._json(404, {"status": "not_found"})
            return
        try:
            with locked_ledger() as ledger:
                summary = {"attempts": ledger["attempts"], "reserved_usd": ledger["reserved_usd"], "actual_usd": ledger["actual_usd"]}
            self._json(200, {"status": "ok", "mode": MODE, "paid_inference": True, "provider_configured": True, "model": MODEL, "budget": summary})
        except Exception:
            self._json(503, {"status": "unhealthy", "error": "P0_LEDGER_UNAVAILABLE"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/reason":
            self._json(404, {"status": "not_found"})
            return
        if not self._authorized():
            self._json(401, {"status": "unauthorized", "error": "P0_AUTH_REJECTED"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 2 or length > MAX_BODY_BYTES:
            self._json(413, {"status": "invalid_request", "error": "P0_BODY_SIZE"})
            return
        try:
            body = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"status": "invalid_request", "error": "P0_INVALID_JSON"})
            return
        task_id = body.get("task_id")
        correlation_id = body.get("correlation_id")
        input_data = body.get("input")
        valid = (
            isinstance(task_id, str) and ID_PATTERN.fullmatch(task_id)
            and isinstance(correlation_id, str) and ID_PATTERN.fullmatch(correlation_id)
            and isinstance(input_data, dict) and input_data.get("channel") == "ads"
            and isinstance(input_data.get("spend"), (int, float)) and not isinstance(input_data.get("spend"), bool) and 0 <= input_data["spend"] <= 10000
            and isinstance(input_data.get("clicks"), int) and not isinstance(input_data.get("clicks"), bool) and 0 <= input_data["clicks"] <= 100000
        )
        if not valid:
            self._json(422, {"status": "invalid_request", "error": "P0_FAKE_ADS_SCHEMA"})
            return
        fingerprint = canonical_hash({"task_id": task_id, "input": input_data})
        try:
            decision, task = admit(task_id, fingerprint)
        except RuntimeError as error:
            self._json(429, {"status": "blocked", "error": str(error)})
            return
        if decision == "conflict":
            self._json(409, {"status": "conflict", "error": "P0_IDEMPOTENCY_CONFLICT"})
            return
        if decision == "existing":
            if task.get("state") == "complete":
                self._json(200, {"accepted": True, "task_id": task_id, "correlation_id": correlation_id, "result_hash": task["result_hash"], "replayed": True, "callback_repeated": False, "mode": MODE, "provider": "openai", "model": task["model"], "usage": task["usage"], "actual_cost_usd": task["actual_cost_usd"]})
            elif task.get("state") == "inflight":
                self._json(202, {"accepted": True, "task_id": task_id, "correlation_id": correlation_id, "pending": True, "replayed": True, "callback_repeated": False, "mode": MODE})
            else:
                self._json(502, {"accepted": False, "task_id": task_id, "correlation_id": correlation_id, "replayed": True, "error": task.get("error", "P0_PROVIDER_FAILED")})
            return

        started = time.monotonic()
        try:
            result, usage, actual_cost, actual_model, response_id_hash = provider_request(task_id, correlation_id, input_data)
            result_hash = canonical_hash(result)
            update_task(task_id, {"state": "complete", "result_hash": result_hash, "model": actual_model, "usage": usage, "actual_cost_usd": actual_cost, "response_id_hash": response_id_hash}, actual_cost)
        except Exception as error:
            error_code = str(error) if isinstance(error, RuntimeError) else "P0_PROVIDER_FAILED"
            update_task(task_id, {"state": "failed", "error": error_code})
            self._json(502, {"accepted": False, "task_id": task_id, "correlation_id": correlation_id, "error": error_code, "provider_attempted": True})
            return
        callback_payload = {
            "phase": "callback",
            "task_id": task_id,
            "correlation_id": correlation_id,
            "status": "provider_succeeded",
            "timings_ms": {"total": int((time.monotonic() - started) * 1000)},
            "result": result,
            "result_hash": result_hash,
            "error": None,
            "inference": {"mode": MODE, "paid": True, "provider": "openai", "model": actual_model, "usage": usage, "actual_cost_usd": actual_cost},
        }
        callback_status, callback_body_hash = send_callback(callback_payload)
        if not 200 <= callback_status < 300:
            self._json(502, {"accepted": False, "task_id": task_id, "correlation_id": correlation_id, "provider_succeeded": True, "callback_http_status": callback_status, "callback_body_hash": callback_body_hash, "result_hash": result_hash, "error": "P0_CALLBACK_REJECTED"})
            return
        self._json(200, {"accepted": True, "task_id": task_id, "correlation_id": correlation_id, "callback_http_status": callback_status, "callback_body_hash": callback_body_hash, "result_hash": result_hash, "replayed": False, "mode": MODE, "paid_inference": True, "provider": "openai", "model": actual_model, "usage": usage, "actual_cost_usd": actual_cost})


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
