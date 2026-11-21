"""Add one scoped permit to a disposable ledger COPY, never the real ledger."""
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def main() -> None:
    path = Path(sys.argv[1]).resolve()
    if "/mock-ledger/" not in str(path):
        raise SystemExit("refusing non-mock ledger path")
    task_id, correlation_id = sys.argv[2:4]
    spend, clicks = float(sys.argv[4]), int(sys.argv[5])
    marker = {"task_id": task_id, "correlation_id": correlation_id,
              "channel": "ads", "spend": f"{spend:.2f}", "clicks": clicks}
    canonical = json.dumps(marker, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("kill_switch") is not True or "one_shot_permits" in data:
        raise SystemExit("mock ledger not fresh or kill switch not ON")
    data["one_shot_permits"] = {task_id: {
        "state": "ready", "model": "gpt-6-luna",
        "key_hash": hashlib.sha256(("gate-a-" + task_id).encode()).hexdigest(),
        "fingerprint": hashlib.sha256(canonical).hexdigest(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()}}
    temporary = path.with_name(path.name + ".new")
    temporary.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)
    print(json.dumps({"prepared": True, "ledger": "mock_copy", "kill_switch": True,
                      "attempts": data["attempts"], "task_id_hash": hashlib.sha256(task_id.encode()).hexdigest()}))


if __name__ == "__main__":
    main()
