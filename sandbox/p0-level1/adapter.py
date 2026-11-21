#!/usr/bin/env python3
"""Deterministic, no-cost P0 reasoning adapter.

This service deliberately does not call an LLM. It validates the private
transport, service authentication, callback contract, schema, timeout and
idempotency controls required before a paid provider is approved.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


HOST = "0.0.0.0"
PORT = int(os.environ.get("P0_PORT", "8080"))
MODE = os.environ.get("P0_MODE", "mock")
TOKEN = os.environ.get("P0_TOKEN", "")
CALLBACK_URL = os.environ.get("P0_CALLBACK_URL", "")
MAX_BODY_BYTES = 32 * 1024

if MODE != "mock":
    raise SystemExit("P0_MODE must remain mock until Level 2 approval")
if len(TOKEN) < 32:
    raise SystemExit("P0_TOKEN must contain at least 32 characters")
if not CALLBACK_URL.startswith("http://n8n-p0-sandbox:5678/"):
    raise SystemExit("P0_CALLBACK_URL must target the private n8n sandbox alias")


_cache: dict[str, dict[str, Any]] = {}
_cache_lock = threading.Lock()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def send_callback(payload: dict[str, Any]) -> tuple[int, str]:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        CALLBACK_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "ttd-p0-reasoner/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            response_body = response.read(4096)
            return response.status, hashlib.sha256(response_body).hexdigest()
    except urllib.error.HTTPError as error:
        response_body = error.read(4096)
        return error.code, hashlib.sha256(response_body).hexdigest()
    except urllib.error.URLError:
        return 0, hashlib.sha256(b"").hexdigest()


class Handler(BaseHTTPRequestHandler):
    server_version = "ttd-p0-reasoner/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args: Any) -> None:
        # Never log request bodies, authorization headers, callback URLs or tokens.
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
        received = self.headers.get("Authorization", "")
        expected = f"Bearer {TOKEN}"
        return hmac.compare_digest(received.encode("utf-8"), expected.encode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/healthz":
            self._json(404, {"status": "not_found"})
            return
        self._json(
            200,
            {
                "status": "ok",
                "mode": MODE,
                "paid_inference": False,
                "provider_configured": False,
            },
        )

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
            request_body = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"status": "invalid_request", "error": "P0_INVALID_JSON"})
            return

        task_id = request_body.get("task_id")
        correlation_id = request_body.get("correlation_id")
        input_data = request_body.get("input")
        simulate = request_body.get("simulate")
        if not isinstance(task_id, str) or not 3 <= len(task_id) <= 128:
            self._json(422, {"status": "invalid_request", "error": "P0_TASK_ID"})
            return
        if not isinstance(correlation_id, str) or not 3 <= len(correlation_id) <= 128:
            self._json(422, {"status": "invalid_request", "error": "P0_CORRELATION_ID"})
            return
        if not isinstance(input_data, dict):
            self._json(422, {"status": "invalid_request", "error": "P0_INPUT_OBJECT"})
            return
        channel = input_data.get("channel")
        spend = input_data.get("spend")
        clicks = input_data.get("clicks")
        if channel != "ads" or not isinstance(spend, (int, float)) or spend < 0:
            self._json(422, {"status": "invalid_request", "error": "P0_FAKE_ADS_SCHEMA"})
            return
        if not isinstance(clicks, int) or isinstance(clicks, bool) or clicks < 0:
            self._json(422, {"status": "invalid_request", "error": "P0_FAKE_ADS_SCHEMA"})
            return

        fingerprint = canonical_hash({"task_id": task_id, "input": input_data})
        with _cache_lock:
            cached = _cache.get(task_id)
        if cached:
            if cached["fingerprint"] != fingerprint:
                self._json(409, {"status": "conflict", "error": "P0_IDEMPOTENCY_CONFLICT"})
                return
            if cached["state"] == "inflight":
                self._json(
                    202,
                    {
                        "accepted": True,
                        "task_id": task_id,
                        "correlation_id": correlation_id,
                        "pending": True,
                        "replayed": True,
                        "callback_repeated": False,
                        "mode": MODE,
                    },
                )
                return
            self._json(
                200,
                {
                    "accepted": True,
                    "task_id": task_id,
                    "correlation_id": correlation_id,
                    "result_hash": cached["result_hash"],
                    "replayed": True,
                    "callback_repeated": False,
                    "mode": MODE,
                },
            )
            return

        with _cache_lock:
            # Register the task before any delay or callback so an n8n retry
            # cannot create a second callback while the first request is live.
            _cache[task_id] = {
                "fingerprint": fingerprint,
                "state": "inflight",
            }

        started = time.monotonic()
        if simulate == "timeout":
            time.sleep(4)

        cost_per_click = round(float(spend) / clicks, 4) if clicks else None
        result = {
            "summary": (
                "Mock reasoning only: observed "
                f"{clicks} clicks from spend {float(spend):.2f}; "
                "no model or paid provider was called."
            ),
            "signals": [
                f"channel={channel}",
                f"clicks={clicks}",
                f"cost_per_click={cost_per_click if cost_per_click is not None else 'undefined'}",
            ],
            "recommendations": [
                "Approve a Level 2 provider, model and cost cap before real inference.",
                "Keep business connectors read-only until real E2E acceptance passes.",
            ],
        }
        result_hash = canonical_hash(result)
        callback_payload: dict[str, Any] = {
            "phase": "callback",
            "task_id": task_id,
            "correlation_id": correlation_id,
            "status": "mock_succeeded",
            "timings_ms": {
                "total": int((time.monotonic() - started) * 1000),
                "reasoning": 0,
                "callback": 0,
            },
            "result": result,
            "result_hash": result_hash,
            "error": None,
            "inference": {"mode": MODE, "paid": False, "provider": None, "model": None},
        }
        if simulate == "invalid_output":
            callback_payload.pop("result_hash")

        callback_started = time.monotonic()
        callback_status, callback_body_hash = send_callback(callback_payload)
        callback_payload["timings_ms"]["callback"] = int((time.monotonic() - callback_started) * 1000)
        if not 200 <= callback_status < 300:
            with _cache_lock:
                _cache.pop(task_id, None)
            self._json(
                502,
                {
                    "accepted": False,
                    "task_id": task_id,
                    "correlation_id": correlation_id,
                    "callback_http_status": callback_status,
                    "callback_body_hash": callback_body_hash,
                    "error": "P0_CALLBACK_REJECTED",
                    "mode": MODE,
                },
            )
            return

        with _cache_lock:
            _cache[task_id] = {
                "fingerprint": fingerprint,
                "state": "complete",
                "result_hash": result_hash,
            }
        self._json(
            200,
            {
                "accepted": True,
                "task_id": task_id,
                "correlation_id": correlation_id,
                "callback_http_status": callback_status,
                "callback_body_hash": callback_body_hash,
                "result_hash": result_hash,
                "replayed": False,
                "mode": MODE,
                "paid_inference": False,
            },
        )


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
