#!/usr/bin/env python3
"""Private OpenAI Responses-compatible fixture for GATE A. No egress."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


HOST = "0.0.0.0"
PORT = 8082
TOKEN_FILE = Path("/run/secrets/guard_service_token")
MODEL = "gpt-6-luna"


def token() -> bytes:
    return TOKEN_FILE.read_text(encoding="utf-8").strip().encode()


def json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def input_surface(body: dict[str, Any]) -> bytes:
    return json.dumps(
        {"instructions": body.get("instructions"), "input": body.get("input")},
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def contains_marker(value: Any, marker: str) -> bool:
    return marker in json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class Handler(BaseHTTPRequestHandler):
    server_version = "ttd-gate-a-provider-mock/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args: Any) -> None:
        print(json.dumps({"event": "mock_http", "path": self.path, "status": args[1]}), flush=True)

    def send_json(self, status: int, value: Any) -> None:
        payload = json_bytes(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def authorized(self) -> bool:
        expected = b"Bearer " + token()
        return hmac.compare_digest(self.headers.get("Authorization", "").encode(), expected)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self.send_json(200, {"status": "ok", "mode": "mock", "egress": False})
        else:
            self.send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/responses":
            self.send_json(404, {"error": "not_found"})
            return
        if not self.authorized():
            self.send_json(401, {"error": "mock_auth_rejected"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "invalid_json"})
            return
        if contains_marker(body.get("input"), "[SIMULATE_PROVIDER_ERROR]"):
            self.send_json(503, {"error": {"message": "synthetic mock failure", "type": "server_error"}})
            return
        if contains_marker(body.get("input"), "[SIMULATE_DELAY]"):
            time.sleep(2.0)

        result = {
            "summary": "Synthetic GATE A result from a private provider mock.",
            "signals": ["fake_spend_reviewed", "fake_clicks_reviewed"],
            "recommendations": ["Keep production unchanged."],
        }
        text = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
        bound = len(input_surface(body))
        response = {
            "id": "resp_mock_" + hashlib.sha256(json_bytes(body)).hexdigest()[:16],
            "object": "response",
            "created_at": int(time.time()),
            "status": "completed",
            "model": MODEL,
            "output": [
                {
                    "id": "msg_mock",
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": text, "annotations": []}],
                }
            ],
            "usage": {
                "input_tokens": bound,
                "output_tokens": 32,
                "total_tokens": bound + 32,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens_details": {"reasoning_tokens": 0},
            },
        }
        if body.get("stream") is True:
            created = dict(response)
            created.update(status="in_progress", output=[])
            events = [
                {"type": "response.created", "response": created, "sequence_number": 0},
                {
                    "type": "response.output_item.done",
                    "item": response["output"][0],
                    "output_index": 0,
                    "sequence_number": 1,
                },
                {"type": "response.completed", "response": response, "sequence_number": 2},
            ]
            payload = "".join("data: " + json.dumps(event, separators=(",", ":")) + "\n\n" for event in events).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("x-request-id", response["id"])
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_json(200, response)


if __name__ == "__main__":
    if len(token()) < 32:
        raise SystemExit("guard service token missing")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
