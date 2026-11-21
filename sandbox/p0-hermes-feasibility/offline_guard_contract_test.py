#!/usr/bin/env python3
"""Offline contract rehearsal for the proposed Hermes P0 inference guard.

This test performs no network access and contains no provider credential.  It
models the admission controls that must run before every provider request.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any


EXACT_MODEL = "gpt-6-luna"
HARD_OUTPUT_CAP = 600
APPROVED_OUTPUT_CAP = 2_000
CONSERVATIVE_INPUT_BYTES = 4_000
MAX_ATTEMPTS = 5
MAX_TOTAL_USD = Decimal("0.05")
WORST_CASE_USD = Decimal("0.0035")


class Rejected(RuntimeError):
    """A request rejected before budget reservation/provider dispatch."""


@dataclass(frozen=True)
class Admission:
    replay: bool
    upstream_body: dict[str, Any]


class ExclusiveCreateLock:
    """Small cross-platform lock based on atomic exclusive file creation."""

    def __init__(self, path: Path, timeout_seconds: float = 5.0) -> None:
        self.path = path
        self.timeout_seconds = timeout_seconds
        self.fd: int | None = None

    def __enter__(self) -> "ExclusiveCreateLock":
        deadline = time.monotonic() + self.timeout_seconds
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                os.write(self.fd, b"offline-contract-test\n")
                return self
            except (FileExistsError, PermissionError):
                # Windows can surface a sharing violation as PermissionError
                # while another thread owns the exclusively-created lock file.
                if time.monotonic() >= deadline:
                    raise TimeoutError("ledger lock timeout")
                time.sleep(0.005)

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.fd is not None:
            os.close(self.fd)
        self.path.unlink(missing_ok=True)


class OfflineGuard:
    def __init__(self, ledger_path: Path) -> None:
        self.ledger_path = ledger_path
        self.lock_path = ledger_path.with_suffix(".lock")

    @staticmethod
    def _canonical(value: Any) -> bytes:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")

    @classmethod
    def _request_hash(cls, body: dict[str, Any]) -> str:
        return hashlib.sha256(cls._canonical(body)).hexdigest()

    @staticmethod
    def _validate_and_build(path: str, body: dict[str, Any]) -> dict[str, Any]:
        if path != "/v1/responses":
            raise Rejected("PATH_NOT_ALLOWED")
        if body.get("model") != EXACT_MODEL:
            raise Rejected("MODEL_NOT_ALLOWED")
        if any(key in body for key in ("tools", "tool_choice", "parallel_tool_calls")):
            raise Rejected("TOOLS_NOT_ALLOWED")
        requested_cap = body.get("max_output_tokens")
        if requested_cap is not None and (
            not isinstance(requested_cap, int) or requested_cap > APPROVED_OUTPUT_CAP
        ):
            raise Rejected("OUTPUT_CAP_NOT_ALLOWED")

        encoded = OfflineGuard._canonical(body)
        if len(encoded) > CONSERVATIVE_INPUT_BYTES:
            raise Rejected("INPUT_ENVELOPE_EXCEEDED")

        upstream = dict(body)
        upstream["model"] = EXACT_MODEL
        upstream["max_output_tokens"] = HARD_OUTPUT_CAP
        upstream.pop("tools", None)
        upstream.pop("tool_choice", None)
        upstream.pop("parallel_tool_calls", None)
        return upstream

    def admit(self, *, task_id: str, path: str, body: dict[str, Any]) -> Admission:
        upstream = self._validate_and_build(path, body)
        request_hash = self._request_hash(upstream)

        with ExclusiveCreateLock(self.lock_path):
            ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
            prior = ledger.setdefault("reservations", {}).get(task_id)
            if prior is not None:
                if prior["request_hash"] != request_hash:
                    raise Rejected("IDEMPOTENCY_CONFLICT")
                return Admission(replay=True, upstream_body=upstream)

            if ledger["kill_switch"]:
                raise Rejected("P0_KILL_SWITCH")
            if ledger["attempts"] >= MAX_ATTEMPTS:
                raise Rejected("ATTEMPT_CAP")
            next_reserved = Decimal(str(ledger["reserved_usd"])) + WORST_CASE_USD
            if next_reserved > MAX_TOTAL_USD:
                raise Rejected("BUDGET_CAP")

            ledger["attempts"] += 1
            ledger["reserved_usd"] = float(next_reserved)
            ledger["reservations"][task_id] = {"request_hash": request_hash}
            temporary = self.ledger_path.with_suffix(f".{threading.get_ident()}.tmp")
            temporary.write_text(json.dumps(ledger, sort_keys=True), encoding="utf-8")
            os.replace(temporary, self.ledger_path)

        return Admission(replay=False, upstream_body=upstream)


def initial_ledger(*, kill_switch: bool) -> dict[str, Any]:
    return {
        "attempts": 1,
        "reserved_usd": 0.0035,
        "actual_usd": 0.0000496,
        "kill_switch": kill_switch,
        "reservations": {},
    }


def write_ledger(path: Path, *, kill_switch: bool) -> None:
    path.write_text(json.dumps(initial_ledger(kill_switch=kill_switch)), encoding="utf-8")


def expect_rejection(guard: OfflineGuard, code: str, **request: Any) -> None:
    before = guard.ledger_path.read_bytes()
    try:
        guard.admit(**request)
    except Rejected as exc:
        assert str(exc) == code, (str(exc), code)
    else:
        raise AssertionError(f"expected {code}")
    assert guard.ledger_path.read_bytes() == before, f"{code} mutated ledger"


def run() -> dict[str, Any]:
    base_body = {"model": EXACT_MODEL, "input": "Return fake-data JSON only."}
    with tempfile.TemporaryDirectory(prefix="ttd-hermes-offline-") as directory:
        root = Path(directory)

        killed_path = root / "killed-ledger.json"
        write_ledger(killed_path, kill_switch=True)
        killed_guard = OfflineGuard(killed_path)
        expect_rejection(
            killed_guard,
            "P0_KILL_SWITCH",
            task_id="killed-task",
            path="/v1/responses",
            body=base_body,
        )

        validation_path = root / "validation-ledger.json"
        write_ledger(validation_path, kill_switch=False)
        validation_guard = OfflineGuard(validation_path)
        invalid_cases = [
            ("MODEL_NOT_ALLOWED", "/v1/responses", {**base_body, "model": "other-model"}),
            ("TOOLS_NOT_ALLOWED", "/v1/responses", {**base_body, "tools": []}),
            ("OUTPUT_CAP_NOT_ALLOWED", "/v1/responses", {**base_body, "max_output_tokens": 2001}),
            ("PATH_NOT_ALLOWED", "/v1/chat/completions", base_body),
            ("INPUT_ENVELOPE_EXCEEDED", "/v1/responses", {**base_body, "input": "x" * 4_001}),
        ]
        for code, path, body in invalid_cases:
            expect_rejection(
                validation_guard,
                code,
                task_id=f"invalid-{code.lower()}",
                path=path,
                body=body,
            )

        first = validation_guard.admit(
            task_id="idempotent-task", path="/v1/responses", body=base_body
        )
        replay = validation_guard.admit(
            task_id="idempotent-task", path="/v1/responses", body=base_body
        )
        assert not first.replay and replay.replay
        assert first.upstream_body["model"] == EXACT_MODEL
        assert first.upstream_body["max_output_tokens"] == HARD_OUTPUT_CAP
        assert "tools" not in first.upstream_body
        expect_rejection(
            validation_guard,
            "IDEMPOTENCY_CONFLICT",
            task_id="idempotent-task",
            path="/v1/responses",
            body={**base_body, "input": "different fake input"},
        )

        concurrent_path = root / "concurrent-ledger.json"
        write_ledger(concurrent_path, kill_switch=False)
        concurrent_guard = OfflineGuard(concurrent_path)
        outcomes: list[str] = []
        outcomes_lock = threading.Lock()

        def worker(index: int) -> None:
            try:
                concurrent_guard.admit(
                    task_id=f"concurrent-{index}", path="/v1/responses", body=base_body
                )
                result = "admitted"
            except Rejected as exc:
                result = str(exc)
            with outcomes_lock:
                outcomes.append(result)

        threads = [threading.Thread(target=worker, args=(index,)) for index in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        final_ledger = json.loads(concurrent_path.read_text(encoding="utf-8"))
        assert outcomes.count("admitted") == 4, outcomes
        assert outcomes.count("ATTEMPT_CAP") == 6, outcomes
        assert final_ledger["attempts"] == 5
        assert Decimal(str(final_ledger["reserved_usd"])) == Decimal("0.0175")

    return {
        "result": "PASS",
        "network_calls": 0,
        "paid_calls": 0,
        "kill_switch_blocks_without_mutation": True,
        "invalid_requests_block_before_reservation": len(invalid_cases),
        "exact_model": EXACT_MODEL,
        "hard_max_output_tokens": HARD_OUTPUT_CAP,
        "tools_field_present_upstream": False,
        "idempotent_replay_reservations": 1,
        "concurrency": {
            "requests": 10,
            "starting_attempts": 1,
            "admitted": outcomes.count("admitted"),
            "blocked": outcomes.count("ATTEMPT_CAP"),
            "final_attempts": final_ledger["attempts"],
            "final_reserved_usd": final_ledger["reserved_usd"],
        },
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
