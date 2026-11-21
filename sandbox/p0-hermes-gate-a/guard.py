#!/usr/bin/env python3
"""Fail-closed pre-dispatch policy guard for the mock-only GATE A lane."""

from __future__ import annotations

import fcntl
import hashlib
import hmac
import json
import os
import tempfile
import urllib.error
import urllib.request
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator


HOST = "0.0.0.0"
PORT = 8081
MODEL = "gpt-6-luna"
HARD_OUTPUT_CAP = 600
STRICT_FULL_REQUEST_BYTE_BOUND = 4_000
MAX_BODY_BYTES = 64 * 1024
TOKEN_FILE = Path("/run/secrets/guard_service_token")
LEDGER_PATH = Path("/opt/ttd/ledger/level2-budget.json")
CAPTURE_DIR = Path("/opt/ttd/capture")
CAPTURE_INDEX = CAPTURE_DIR / "capture-index.json"
CAPTURE_LOCK = CAPTURE_DIR / "capture.lock"
MOCK_URL = "http://gate-a-provider-mock:8082/v1/responses"
FORBIDDEN_FIELDS = {"tools", "tool_choice", "parallel_tool_calls"}


def service_token() -> str:
    return TOKEN_FILE.read_text(encoding="utf-8").strip()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


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
def capture_lock() -> Iterator[None]:
    CAPTURE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(CAPTURE_LOCK, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def ledger_summary() -> dict[str, Any]:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    return {
        "attempts": ledger.get("attempts"),
        "reserved_usd": ledger.get("reserved_usd"),
        "actual_usd": ledger.get("actual_usd"),
        "kill_switch": ledger.get("kill_switch"),
        "sha256": hashlib.sha256(LEDGER_PATH.read_bytes()).hexdigest(),
    }


def record_capture(raw: dict[str, Any], forwarded: dict[str, Any]) -> dict[str, Any]:
    raw_bytes = canonical(raw)
    forwarded_bytes = canonical(forwarded)
    with capture_lock():
        if CAPTURE_INDEX.exists():
            index = json.loads(CAPTURE_INDEX.read_text(encoding="utf-8"))
        else:
            index = {"schema_version": 1, "physical_requests": 0, "entries": []}
        sequence = int(index["physical_requests"]) + 1
        raw_path = CAPTURE_DIR / f"request-{sequence:03d}-raw.json"
        forwarded_path = CAPTURE_DIR / f"request-{sequence:03d}-forwarded.json"
        atomic_write(raw_path, raw)
        atomic_write(forwarded_path, forwarded)
        entry = {
            "sequence": sequence,
            "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "forwarded_sha256": hashlib.sha256(forwarded_bytes).hexdigest(),
            "raw_full_request_bytes": len(raw_bytes),
            "forwarded_full_request_bytes": len(forwarded_bytes),
            "strict_input_token_upper_bound": len(forwarded_bytes),
            "model": forwarded.get("model"),
            "max_output_tokens": forwarded.get("max_output_tokens"),
            "tools_field_present": "tools" in forwarded,
            "stream": forwarded.get("stream") is True,
        }
        index["physical_requests"] = sequence
        index["entries"].append(entry)
        atomic_write(CAPTURE_INDEX, index)
        return entry


def enforce(body: dict[str, Any]) -> tuple[dict[str, Any], int]:
    if body.get("model") != MODEL:
        raise ValueError("MODEL_NOT_ALLOWED")
    if any(field in body for field in FORBIDDEN_FIELDS):
        raise ValueError("TOOLS_NOT_ALLOWED")
    requested_cap = body.get("max_output_tokens")
    if requested_cap is not None and (not isinstance(requested_cap, int) or requested_cap > HARD_OUTPUT_CAP):
        raise ValueError("OUTPUT_CAP_NOT_ALLOWED")
    ledger = ledger_summary()
    if ledger["kill_switch"] is not True:
        raise RuntimeError("KILL_SWITCH_NOT_ON")
    forwarded = dict(body)
    forwarded["model"] = MODEL
    forwarded["max_output_tokens"] = HARD_OUTPUT_CAP
    for field in FORBIDDEN_FIELDS:
        forwarded.pop(field, None)
    full_bytes = len(canonical(forwarded))
    if full_bytes > STRICT_FULL_REQUEST_BYTE_BOUND:
        raise ValueError("INPUT_BOUND_EXCEEDED")
    return forwarded, full_bytes


class Handler(BaseHTTPRequestHandler):
    server_version = "ttd-gate-a-inference-guard/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args: Any) -> None:
        print(json.dumps({"event": "guard_http", "path": self.path, "status": args[1]}), flush=True)

    def send_json(self, status: int, value: Any) -> None:
        payload = json.dumps(value, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def authorized(self) -> bool:
        expected = f"Bearer {service_token()}".encode()
        return hmac.compare_digest(self.headers.get("Authorization", "").encode(), expected)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            try:
                ledger = ledger_summary()
                status = 200 if ledger["kill_switch"] is True else 503
                self.send_json(status, {"status": "ok" if status == 200 else "blocked", "mode": "mock_only", "ledger": ledger})
            except Exception:
                self.send_json(503, {"status": "unhealthy", "error": "LEDGER_UNAVAILABLE"})
            return
        if self.path in ("/v1/models", "/v1/models/gpt-6-luna"):
            if not self.authorized():
                self.send_json(401, {"error": "GUARD_AUTH_REJECTED"})
                return
            model = {"id": MODEL, "object": "model", "owned_by": "ttd-gate-a-mock"}
            self.send_json(200, {"object": "list", "data": [model]} if self.path == "/v1/models" else model)
            return
        self.send_json(404, {"error": "PATH_NOT_ALLOWED"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/responses":
            self.send_json(404, {"error": "PATH_NOT_ALLOWED"})
            return
        if not self.authorized():
            self.send_json(401, {"error": "GUARD_AUTH_REJECTED"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 2 or length > MAX_BODY_BYTES:
            self.send_json(413, {"error": "BODY_SIZE"})
            return
        try:
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "INVALID_JSON"})
            return
        try:
            forwarded, _ = enforce(body)
        except ValueError as error:
            self.send_json(422, {"error": str(error)})
            return
        except RuntimeError as error:
            self.send_json(503, {"error": str(error)})
            return
        entry = record_capture(body, forwarded)
        request = urllib.request.Request(
            MOCK_URL,
            data=json.dumps(forwarded, separators=(",", ":")).encode(),
            method="POST",
            headers={
                "Authorization": f"Bearer {service_token()}",
                "Content-Type": "application/json",
                "User-Agent": "ttd-gate-a-guard/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                payload = response.read(256 * 1024)
                self.send_response(response.status)
                self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("x-ttd-capture-sequence", str(entry["sequence"]))
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as error:
            payload = error.read(64 * 1024)
            self.send_response(error.code)
            self.send_header("Content-Type", error.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except urllib.error.URLError:
            self.send_json(502, {"error": "MOCK_UNAVAILABLE"})


if __name__ == "__main__":
    if len(service_token()) < 32:
        raise SystemExit("guard service token missing")
    if ledger_summary()["kill_switch"] is not True:
        raise SystemExit("real P0 kill switch must remain ON")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
