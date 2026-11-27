"""Offline concurrency and durable replay test on a disposable ledger copy."""
import concurrent.futures
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from one_shot import admit


def main() -> None:
    now = datetime.now(timezone.utc)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "level2-budget.json"
        initial = {"schema_version": 1, "model": "gpt-6-luna", "max_calls": 5,
                   "caps_usd": {"daily": 0.05, "total": 0.05, "job": 0.01},
                   "attempts": 1, "reserved_usd": 0.0035, "actual_usd": 0.0000496,
                   "kill_switch": True, "days": {}, "tasks": {"previous": {"state": "complete"}},
                   "one_shot_permits": {"gate-b": {"state": "ready", "key_hash": "key-hash",
                       "fingerprint": "request-hash", "model": "gpt-6-luna",
                       "expires_at": (now + timedelta(minutes=10)).isoformat()}}}
        path.write_text(json.dumps(initial), encoding="utf-8")

        def call(_: int) -> str:
            try:
                return admit(path, "gate-b", "key-hash", "request-hash", now)
            except RuntimeError as error:
                return str(error)

        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            outcomes = list(pool.map(call, range(20)))
        assert outcomes.count("admitted") == 1, outcomes
        assert outcomes.count("PERMIT_UNAVAILABLE") == 19, outcomes
        persisted = json.loads(path.read_text(encoding="utf-8"))
        assert persisted["attempts"] == 2
        assert persisted["reserved_usd"] == 0.007
        assert persisted["kill_switch"] is True
        assert persisted["one_shot_permits"]["gate-b"]["state"] == "consumed"
        assert call(99) == "PERMIT_UNAVAILABLE"  # new call after durable reload
        print(json.dumps({"result": "PASS", "concurrent": 20, "admitted": 1,
                          "rejected": 19, "persisted_attempts": 2,
                          "persisted_reserved_usd": 0.007, "kill_switch": True}))


if __name__ == "__main__":
    main()
