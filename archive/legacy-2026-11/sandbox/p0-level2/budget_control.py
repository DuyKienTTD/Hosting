#!/usr/bin/env python3
"""One-way operational kill switch for new P0 paid inference tasks."""

from __future__ import annotations

import json
import sys

import adapter


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"status", "stop"}:
        raise SystemExit("usage: budget_control.py status|stop")
    with adapter.locked_ledger() as ledger:
        if sys.argv[1] == "stop":
            ledger["kill_switch"] = True
        safe = {
            "attempts": ledger["attempts"],
            "reserved_usd": ledger["reserved_usd"],
            "actual_usd": ledger["actual_usd"],
            "kill_switch": ledger.get("kill_switch", False),
        }
    print(json.dumps(safe, separators=(",", ":")))


if __name__ == "__main__":
    main()
