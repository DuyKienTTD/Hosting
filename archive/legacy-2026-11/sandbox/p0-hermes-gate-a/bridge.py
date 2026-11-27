#!/usr/bin/env python3
"""Authenticated n8n bridge to a real Hermes auxiliary API server."""

from __future__ import annotations

import fcntl
import hashlib
import hmac
import json
import os
import re
import tempfile
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator


HOST = "0.0.0.0"
PORT = 8080
MODEL = "gpt-6-luna"
P0_TOKEN_FILE = Path("/run/secrets/existing_p0_token")
API_KEY_FILE = Path("/run/secrets/api_server_key")
STATE_PATH = Path("/opt/ttd/state/bridge-tasks.json")
LOCK_PATH = STATE_PATH.with_suffix(".lock")
HERMES_URL = "http://gate-a-hermes:8642"
CALLBACK_URL = "http://n8n-p0-sandbox:5678/webhook/ttd-p0-fake-ads-audit-v1"
ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{3,128}$")


def secret(path: Path) -> str:
    value = path.read_text(encoding="utf-8").strip()
    if len(value) < 32:
        raise RuntimeError("secret unavailable")
    return value


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def state_lock() -> Iterator[dict[str, Any]]:
    STATE_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(LOCK_PATH, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {"schema_version": 1, "tasks": {}}
        yield state
        atomic_write(STATE_PATH, state)
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def request_json(url: str, *, method: str = "GET", body: Any = None, headers: dict[str, str] | None = None, timeout: float = 10) -> tuple[int, dict[str, Any], dict[str, str]]:
    payload = None if body is None else json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()
    request = urllib.request.Request(url, data=payload, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(256 * 1024)
            return response.status, json.loads(raw), dict(response.headers)
    except urllib.error.HTTPError as error:
        raw = error.read(256 * 1024)
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"error": "HTTP_ERROR"}
        return error.code, parsed, dict(error.headers)


def bearer(path: Path) -> dict[str, str]:
    return {"Authorization": f"Bearer {secret(path)}", "Content-Type": "application/json"}


def run_hermes(task_id: str, correlation_id: str, input_data: dict[str, Any], simulate: str | None) -> dict[str, Any]:
    marker = ""
    if simulate == "provider_error":
        marker = " [SIMULATE_PROVIDER_ERROR]"
    elif simulate == "delay":
        marker = " [SIMULATE_DELAY]"
    prompt = (
        "This is a private GATE A provider-mock test using fictional advertising data only. "
        "Return only JSON with keys summary, signals, recommendations. Do not use tools, "
        "external data, accounts, memory, subagents, or additional model calls. "
        f"task_id={task_id}; correlation_id={correlation_id}; channel=ads; "
        f"spend={float(input_data['spend']):.2f}; clicks={input_data['clicks']}.{marker}"
    )
    body = {
        "input": prompt,
        "model": MODEL,
        "provider": "openai-api",
        "model_options": {"reasoning_effort": "none", "service_tier": "default"},
    }
    status, created, _ = request_json(
        HERMES_URL + "/v1/runs",
        method="POST",
        body=body,
        headers={**bearer(API_KEY_FILE), "Idempotency-Key": "gate-a-" + task_id},
        timeout=5,
    )
    if status not in (200, 202) or not isinstance(created.get("run_id"), str):
        raise RuntimeError(f"HERMES_ADMISSION_{status}")
    run_id = created["run_id"]
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        poll_status, run, _ = request_json(HERMES_URL + "/v1/runs/" + run_id, headers=bearer(API_KEY_FILE), timeout=5)
        if poll_status != 200:
            raise RuntimeError(f"HERMES_POLL_{poll_status}")
        state = run.get("status")
        if state == "completed":
            runtime = run.get("runtime") or {}
            requested = runtime.get("requested") or {}
            if requested.get("model") != MODEL or requested.get("provider") != "openai-api":
                raise RuntimeError("HERMES_RUNTIME_MISMATCH")
            if runtime.get("model") not in (None, "", MODEL) or runtime.get("provider") not in (None, "", "openai-api"):
                raise RuntimeError("HERMES_RUNTIME_MISMATCH")
            try:
                result = json.loads(run.get("output") or "")
            except json.JSONDecodeError as error:
                raise RuntimeError("HERMES_OUTPUT_SCHEMA") from error
            if set(result) != {"summary", "signals", "recommendations"}:
                raise RuntimeError("HERMES_OUTPUT_SCHEMA")
            return {
                "run_id_hash": hashlib.sha256(run_id.encode()).hexdigest(),
                "result": result,
                "usage": run.get("usage") or {},
                "runtime": {
                    "model": MODEL,
                    "provider": "openai-api",
                    "requested": requested,
                    "api_server_served_model": runtime.get("model") or None,
                    "api_server_served_provider": runtime.get("provider") or None,
                    "route_source": runtime.get("route_source"),
                    "guard_enforced": True,
                },
            }
        if state in {"failed", "cancelled", "interrupted"}:
            raise RuntimeError("HERMES_RUN_" + str(state).upper())
        time.sleep(0.15)
    raise RuntimeError("HERMES_RUN_TIMEOUT")


def callback(payload: dict[str, Any]) -> int:
    status, _, _ = request_json(CALLBACK_URL, method="POST", body=payload, headers=bearer(P0_TOKEN_FILE), timeout=5)
    return status


class Handler(BaseHTTPRequestHandler):
    server_version = "ttd-gate-a-bridge/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args: Any) -> None:
        print(json.dumps({"event": "bridge_http", "path": self.path, "status": args[1]}), flush=True)

    def send_json(self, status: int, value: Any) -> None:
        payload = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            # A client-side timeout must not turn an already committed run into a
            # failed task or make an exact replay create a second physical call.
            pass

    def authorized(self) -> bool:
        expected = f"Bearer {secret(P0_TOKEN_FILE)}".encode()
        return hmac.compare_digest(self.headers.get("Authorization", "").encode(), expected)

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/healthz":
            self.send_json(404, {"status": "not_found"})
            return
        try:
            status, health, _ = request_json(HERMES_URL + "/health", timeout=3)
            self.send_json(200 if status == 200 else 503, {"status": "ok" if status == 200 else "degraded", "hermes": health, "mode": "hermes_mock"})
        except Exception:
            self.send_json(503, {"status": "degraded", "error": "HERMES_UNAVAILABLE"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/reason":
            self.send_json(404, {"status": "not_found"})
            return
        if not self.authorized():
            self.send_json(401, {"status": "unauthorized", "error": "P0_AUTH_REJECTED"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"status": "invalid_request", "error": "INVALID_JSON"})
            return
        task_id = body.get("task_id")
        correlation_id = body.get("correlation_id")
        input_data = body.get("input")
        simulate = body.get("simulate")
        valid = (
            isinstance(task_id, str) and ID_PATTERN.fullmatch(task_id)
            and isinstance(correlation_id, str) and ID_PATTERN.fullmatch(correlation_id)
            and isinstance(input_data, dict) and input_data.get("channel") == "ads"
            and isinstance(input_data.get("spend"), (int, float)) and not isinstance(input_data.get("spend"), bool) and 0 <= input_data["spend"] <= 10000
            and isinstance(input_data.get("clicks"), int) and not isinstance(input_data.get("clicks"), bool) and 0 <= input_data["clicks"] <= 100000
            and simulate in (None, "provider_error", "delay")
        )
        if not valid:
            self.send_json(422, {"status": "invalid_request", "error": "P0_FAKE_ADS_SCHEMA"})
            return
        fingerprint = canonical_hash({"task_id": task_id, "input": input_data, "simulate": simulate})
        with state_lock() as state:
            prior = state["tasks"].get(task_id)
            if prior:
                if prior["fingerprint"] != fingerprint:
                    self.send_json(409, {"status": "conflict", "error": "P0_IDEMPOTENCY_CONFLICT"})
                    return
                if prior["state"] == "complete":
                    self.send_json(200, {**prior["response"], "replayed": True, "callback_repeated": False})
                    return
                if prior["state"] == "inflight":
                    self.send_json(202, {"accepted": True, "pending": True, "replayed": True, "callback_repeated": False})
                    return
                self.send_json(502, {"accepted": False, "replayed": True, "error": prior.get("error", "HERMES_RUN_FAILED")})
                return
            state["tasks"][task_id] = {"fingerprint": fingerprint, "state": "inflight"}

        try:
            hermes = run_hermes(task_id, correlation_id, input_data, simulate)
            result_hash = canonical_hash(hermes["result"])
            usage = hermes["usage"]
            inference = {
                "mode": "hermes_mock",
                "paid": False,
                "provider": "gate-a-provider-mock",
                "model": MODEL,
                "hard_max_output_tokens": 600,
                "input_upper_bound_tokens": int(usage.get("input_tokens", 0)),
                "tools_enabled": False,
                "physical_requests": 1,
                "runtime": hermes["runtime"],
                "run_id_hash": hermes["run_id_hash"],
            }
            callback_payload = {
                "phase": "callback",
                "task_id": task_id,
                "correlation_id": correlation_id,
                "status": "hermes_mock_succeeded",
                "result": hermes["result"],
                "result_hash": result_hash,
                "inference": inference,
                "error": None,
            }
            callback_status = callback(callback_payload)
            if callback_status != 200:
                raise RuntimeError(f"CALLBACK_{callback_status}")
            response = {
                "accepted": True,
                "task_id": task_id,
                "correlation_id": correlation_id,
                "callback_http_status": callback_status,
                "result_hash": result_hash,
                "replayed": False,
                "mode": "hermes_mock",
                "paid_inference": False,
                "provider": "gate-a-provider-mock",
                "model": MODEL,
                "usage": usage,
                "run_id_hash": hermes["run_id_hash"],
            }
            with state_lock() as state:
                state["tasks"][task_id].update(state="complete", response=response)
            self.send_json(200, response)
        except Exception as error:
            code = str(error) if isinstance(error, RuntimeError) else "HERMES_RUN_FAILED"
            with state_lock() as state:
                state["tasks"][task_id].update(state="failed", error=code)
            self.send_json(502, {"accepted": False, "task_id": task_id, "correlation_id": correlation_id, "error": code})


if __name__ == "__main__":
    secret(P0_TOKEN_FILE)
    secret(API_KEY_FILE)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
