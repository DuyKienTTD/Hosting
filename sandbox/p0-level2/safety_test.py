#!/usr/bin/env python3
"""No-cost concurrency tests for the persistent admission controller."""

from __future__ import annotations

import concurrent.futures
import json
import os
import tempfile
from pathlib import Path


os.environ.setdefault("P0_MODE", "openai")
os.environ.setdefault("P0_TOKEN", "t" * 40)
os.environ.setdefault("OPENAI_API_KEY", "k" * 40)
os.environ.setdefault("P0_CALLBACK_URL", "http://n8n-p0-sandbox:5678/webhook/test")

import adapter  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="ttd-p0-level2-") as directory:
        adapter.BUDGET_PATH = Path(directory) / "ledger.json"
        adapter.LOCK_PATH = Path(directory) / "ledger.json.lock"

        def attempt(index: int) -> str:
            try:
                decision, _ = adapter.admit(f"task-{index}", f"fingerprint-{index}")
                return decision
            except RuntimeError as error:
                return str(error)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(attempt, range(10)))
        ledger = json.loads(adapter.BUDGET_PATH.read_text(encoding="utf-8"))
        assert results.count("admitted") == adapter.MAX_CALLS
        assert ledger["attempts"] == adapter.MAX_CALLS
        assert ledger["reserved_usd"] == round(adapter.MAX_CALLS * adapter.RESERVE_USD_PER_ATTEMPT, 8)
        assert ledger["reserved_usd"] < adapter.TOTAL_CAP_USD
        existing_id = next(iter(ledger["tasks"]))
        existing_index = existing_id.removeprefix("task-")
        decision, _ = adapter.admit(existing_id, f"fingerprint-{existing_index}")
        assert decision == "existing"
        with adapter.locked_ledger() as stopped:
            stopped["kill_switch"] = True
        try:
            adapter.admit("task-after-stop", "fingerprint-after-stop")
        except RuntimeError as error:
            assert str(error) == "P0_KILL_SWITCH"
        else:
            raise AssertionError("kill switch admitted a new task")
        print(json.dumps({"suite": "p0_level2_admission", "pass": True, "admitted": results.count("admitted"), "blocked": len(results) - results.count("admitted"), "attempts": ledger["attempts"], "reserved_usd": ledger["reserved_usd"]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
