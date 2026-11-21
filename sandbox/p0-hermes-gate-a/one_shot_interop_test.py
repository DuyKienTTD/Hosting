"""Linux shared-inode lock interoperability against the original Level 2 adapter."""
import importlib.util
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

from one_shot_linux_test import NOW, fixture
from one_shot import admit


def main(adapter_file: str) -> None:
    os.environ.update(P0_MODE="openai", P0_TOKEN="x" * 32,
                      OPENAI_API_KEY="x" * 32,
                      P0_CALLBACK_URL="http://n8n-p0-sandbox:5678/mock")
    spec = importlib.util.spec_from_file_location("level2_adapter_interop", adapter_file)
    adapter = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = adapter
    spec.loader.exec_module(adapter)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "level2-budget.json"
        fixture(path)
        adapter.BUDGET_PATH = path
        adapter.LOCK_PATH = path.with_suffix(path.suffix + ".lock")
        entered = threading.Event()

        def adapter_write() -> None:
            with adapter.locked_ledger() as state:
                state["interop_marker"] = "adapter_committed"
                entered.set()
                time.sleep(0.2)

        worker = threading.Thread(target=adapter_write)
        worker.start()
        assert entered.wait(2)
        result = admit(path, "gate-b", "key-hash", "request-hash", NOW)
        worker.join()
        state = json.loads(path.read_text(encoding="utf-8"))
        assert result == "admitted"
        assert state["interop_marker"] == "adapter_committed"
        assert state["attempts"] == 2 and state["reserved_usd"] == 0.007
        assert state["kill_switch"] is True
        print(json.dumps({"result": "PASS", "shared_lock_inode": True,
                          "adapter_update_preserved": True, "attempts": 2,
                          "reserved_usd": 0.007, "paid_calls": 0}))


if __name__ == "__main__":
    main(sys.argv[1])
