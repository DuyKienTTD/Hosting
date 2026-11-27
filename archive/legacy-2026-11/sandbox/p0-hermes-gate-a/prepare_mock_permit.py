"""Stage a disposable ledger permit from an already reviewed fake Hermes body."""
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from guard import mock_scope
from mock_contract import freeze, no_duplicate_keys
from one_shot import MODEL, _durable_write, locked


def main() -> None:
    ledger_path, reviewed_fixture = map(Path, sys.argv[1:])
    path = ledger_path.resolve(strict=True)
    if "mock-ledger" not in path.parts or path.suffix != ".json":
        raise SystemExit("refusing non-mock ledger path")
    body = json.loads(reviewed_fixture.read_bytes(), object_pairs_hook=no_duplicate_keys)
    task_id, key_hash = mock_scope(body)
    _, fingerprint = freeze(body)
    with locked(path) as data:
        if data.get("kill_switch") is not True or "one_shot_permits" in data:
            raise SystemExit("mock ledger not fresh or kill switch not ON")
        data["one_shot_permits"] = {task_id: {
            "state": "ready", "model": MODEL, "key_hash": key_hash, "fingerprint": fingerprint,
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()}}
        _durable_write(path, data)
    print(json.dumps({"prepared": True, "ledger": "mock_copy", "kill_switch": True,
                      "attempts": data["attempts"], "task_id_hash": hashlib.sha256(task_id.encode()).hexdigest(),
                      "forwarded_sha256": fingerprint}))


if __name__ == "__main__":
    main()
