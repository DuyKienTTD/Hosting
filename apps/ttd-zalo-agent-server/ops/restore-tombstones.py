"""Generate SQL only from validated immutable tombstones."""
import json
import re
import sys
from pathlib import Path
from uuid import UUID


def uuid(value):
    return str(UUID(value))


def version(value):
    if type(value) is not int or not 1 <= value <= 2147483647:
        raise ValueError("invalid version")
    return value


root = Path(sys.argv[1])
print("BEGIN;")
for path in sorted(root.glob("*.json")):
    # Legacy intent files have no commit proof.
    print("DO $$ BEGIN RAISE WARNING 'legacy_tombstone_ignored'; END $$;")

for phase in ("confirmed", "pending"):
    for path in sorted((root / phase).glob("*.json")):
        item = json.loads(path.read_text())
        fields = {"purge_id", "id", "conversation_id", "event_id", "version", "policy_version"}
        if phase == "confirmed":
            fields.add("proof")
        if set(item) != fields:
            raise ValueError("invalid tombstone")
        attempt = uuid(item["purge_id"])
        record_id = uuid(item["id"])
        conversation_id = uuid(item["conversation_id"])
        event_id = item["event_id"]
        revision = version(item["version"])
        policy = version(item["policy_version"])
        if path.name != f"{attempt}.json" or not re.fullmatch("[a-f0-9]{64}", event_id):
            raise ValueError("invalid tombstone identity")
        if phase == "pending" and (root / "confirmed" / path.name).is_file():
            continue
        if phase == "pending":
            print(f"SELECT purge_private.reconcile_restore_pending('{attempt}','{record_id}',"
                  f"'{conversation_id}','{event_id}',{revision},{policy});")
            continue
        proof = item["proof"]
        if not re.fullmatch("[a-f0-9]{64}", proof):
            raise ValueError("invalid commit proof")
        print(f"SELECT purge_private.replay_tombstone('{attempt}','{record_id}','{conversation_id}',"
              f"'{event_id}',{revision},{policy},'{proof}');")
# An old snapshot cannot prove delivery of sends started after the snapshot.
print("DO $restore$ BEGIN IF to_regclass('settings') IS NOT NULL THEN")
print("UPDATE settings SET value=1 WHERE key='global';")
print("UPDATE settings SET value=0 WHERE key='ADS_ENABLED';")
print("INSERT INTO settings VALUES ('epoch',1) ON CONFLICT(key) DO UPDATE SET value=settings.value+1;")
print("END IF; END $restore$;")
print("COMMIT;")
