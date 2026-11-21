"""Linux process-death checks around the one-shot commit on ledger copies."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import one_shot
from one_shot_linux_test import NOW, attempt, fixture


def child_crash(path: Path, phase: str) -> None:
    pid = os.fork()
    if pid == 0:
        if phase == "before_replace":
            with patch.object(one_shot.os, "replace", side_effect=lambda *_: os._exit(31)):
                attempt(str(path))
        elif phase == "after_replace":
            original = one_shot.os.replace
            def replace_then_die(source, target):
                original(source, target)
                os._exit(32)
            with patch.object(one_shot.os, "replace", side_effect=replace_then_die):
                attempt(str(path))
        else:
            os._exit(33)
        os._exit(34)
    _, status = os.waitpid(pid, 0)
    assert os.WEXITSTATUS(status) in (31, 32), status


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "level2-budget.json"
        fixture(path)
        child_crash(path, "before_replace")
        assert json.loads(path.read_text(encoding="utf-8"))["attempts"] == 1
        assert attempt(str(path)) == "admitted"
        assert "PERMIT_UNAVAILABLE" in attempt(str(path))
        fixture(path)
        child_crash(path, "after_replace")
        state = json.loads(path.read_text(encoding="utf-8"))
        assert state["attempts"] == 2 and state["reserved_usd"] == 0.007
        assert state["one_shot_permits"]["gate-b"]["state"] == "consumed"
        assert "PERMIT_UNAVAILABLE" in attempt(str(path))
        print(json.dumps({"result": "PASS", "crash_points": ["before_replace", "after_replace"],
                          "post_commit_replay_rejected": True, "paid_calls": 0}))


if __name__ == "__main__":
    main()
