"""Linux disposable-ledger multiprocess and fault tests; zero network calls."""
import concurrent.futures
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import one_shot

NOW = datetime.now(timezone.utc)


def fixture(path):
    value = {"schema_version": 1, "model": "gpt-6-luna", "max_calls": 5,
             "caps_usd": {"daily": 0.05, "total": 0.05, "job": 0.01},
             "attempts": 1, "reserved_usd": 0.0035, "actual_usd": 0.0000496,
             "kill_switch": True, "days": {}, "tasks": {"previous": {"state": "complete"}},
             "one_shot_permits": {"gate-b": {"state": "ready", "key_hash": "key-hash",
                 "fingerprint": "request-hash", "model": "gpt-6-luna",
                 "expires_at": (NOW + timedelta(minutes=10)).isoformat()}}}
    path.write_text(json.dumps(value), encoding="utf-8")


def attempt(path_string):
    try:
        return one_shot.admit(Path(path_string), "gate-b", "key-hash", "request-hash", NOW)
    except (RuntimeError, OSError, ValueError, KeyError, TypeError) as error:
        return type(error).__name__ + ":" + str(error)


def main():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "level2-budget.json"
        fixture(path)
        with concurrent.futures.ProcessPoolExecutor(max_workers=12) as pool:
            outcomes = list(pool.map(attempt, [str(path)] * 20))
        assert outcomes.count("admitted") == 1, outcomes
        assert sum("PERMIT_UNAVAILABLE" in item for item in outcomes) == 19, outcomes
        persisted = json.loads(path.read_text(encoding="utf-8"))
        assert (persisted["attempts"], persisted["reserved_usd"], persisted["kill_switch"]) == (2, 0.007, True)
        assert persisted["one_shot_permits"]["gate-b"]["state"] == "consumed"
        assert "PERMIT_UNAVAILABLE" in attempt(str(path))

        for field, value, expected in (("kill_switch", False, "KILL_SWITCH_NOT_ON"),
                                       ("reserved_usd", 0.049, "BUDGET_CAP"),
                                       ("attempts", 5, "ATTEMPT_LIMIT")):
            fixture(path)
            state = json.loads(path.read_text(encoding="utf-8"))
            state[field] = value
            path.write_text(json.dumps(state), encoding="utf-8")
            assert expected in attempt(str(path))
        fixture(path)
        with patch.object(one_shot.os, "replace", side_effect=OSError("replace failure")):
            assert "replace failure" in attempt(str(path))
        assert json.loads(path.read_text(encoding="utf-8"))["attempts"] == 1
        fixture(path)
        with patch.object(one_shot.os, "fsync", side_effect=OSError("fsync failure")):
            assert "fsync failure" in attempt(str(path))
        assert json.loads(path.read_text(encoding="utf-8"))["attempts"] == 1
        fixture(path)
        path.write_text("{bad", encoding="utf-8")
        assert "JSONDecodeError" in attempt(str(path))
        for argument, expected in (("wrong-task", "PERMIT_UNAVAILABLE"),
                                   ("wrong-key", "PERMIT_SCOPE_MISMATCH"),
                                   ("wrong-fingerprint", "PERMIT_SCOPE_MISMATCH")):
            fixture(path)
            try:
                one_shot.admit(path,
                               "wrong-task" if argument == "wrong-task" else "gate-b",
                               "wrong-key" if argument == "wrong-key" else "key-hash",
                               "wrong-fingerprint" if argument == "wrong-fingerprint" else "request-hash", NOW)
                raise AssertionError(argument)
            except RuntimeError as error:
                assert str(error) == expected
            assert json.loads(path.read_text(encoding="utf-8"))["attempts"] == 1
        fixture(path)
        stale = json.loads(path.read_text(encoding="utf-8"))
        stale["one_shot_permits"]["gate-b"]["expires_at"] = (NOW - timedelta(seconds=1)).isoformat()
        path.write_text(json.dumps(stale), encoding="utf-8")
        assert "PERMIT_EXPIRED" in attempt(str(path))
        fixture(path)
        wrong_model = json.loads(path.read_text(encoding="utf-8"))
        wrong_model["model"] = "other-model"
        path.write_text(json.dumps(wrong_model), encoding="utf-8")
        assert "LEDGER_MISMATCH" in attempt(str(path))
        fixture(path)
        with patch.object(one_shot.fcntl, "flock", side_effect=OSError("lock failure")):
            assert "lock failure" in attempt(str(path))
        assert json.loads(path.read_text(encoding="utf-8"))["attempts"] == 1
        fixture(path)
        with patch.object(one_shot.os, "open", side_effect=PermissionError("read-only lock")):
            assert "read-only lock" in attempt(str(path))
        assert json.loads(path.read_text(encoding="utf-8"))["attempts"] == 1
        fixture(path)
        original_fsync = one_shot.os.fsync
        fsync_count = 0
        def fail_directory_fsync(fd):
            nonlocal fsync_count
            fsync_count += 1
            if fsync_count == 2:
                raise OSError("directory fsync failure")
            return original_fsync(fd)
        with patch.object(one_shot.os, "fsync", side_effect=fail_directory_fsync):
            assert "directory fsync failure" in attempt(str(path))
        assert "PERMIT_UNAVAILABLE" in attempt(str(path))
        print(json.dumps({"result": "PASS", "kernel": os.uname().release,
                          "multiprocess_contenders": 20, "admitted": 1,
                          "rejected": 19, "replay_rejected": True,
                          "fault_cases": 14, "paid_calls": 0}))


if __name__ == "__main__":
    main()
