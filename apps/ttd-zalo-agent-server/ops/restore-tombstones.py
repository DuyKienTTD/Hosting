"""Generate SQL only from validated immutable tombstones."""
import hmac
import json
import os
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


key = os.environ["DATA_TOMBSTONE_KEY"]
if not re.fullmatch("[a-f0-9]{64}", key):
    raise ValueError("invalid tombstone signing key")

print("BEGIN;")
for path in sorted(Path(sys.argv[1]).iterdir()):
    if path.name == "_format":
        continue
    item = json.loads(path.read_text())
    if set(item) != {"id", "conversation_id", "event_id", "version", "policy_version"}:
        raise ValueError("invalid tombstone")
    record_id = uuid(item["id"])
    conversation_id = uuid(item["conversation_id"])
    event_id = item["event_id"]
    revision = version(item["version"])
    policy = version(item["policy_version"])
    if path.name != f"{record_id}.json" or not re.fullmatch("[a-f0-9]{64}", event_id):
        raise ValueError("invalid tombstone identity")
    identity = f"z4-tombstone-v1|{record_id}|{conversation_id}|{event_id}|{revision}|{policy}"
    signature = hmac.digest(bytes.fromhex(key), identity.encode(), "sha256").hex()
    print(f"SELECT purge_private.replay_tombstone('{record_id}','{conversation_id}',"
          f"'{event_id}',{revision},{policy},'{signature}');")
# An old snapshot cannot prove delivery of sends started after the snapshot.
print("DO $restore$ BEGIN IF to_regclass('settings') IS NOT NULL THEN")
print("UPDATE settings SET value=1 WHERE key='global';")
print("UPDATE settings SET value=0 WHERE key='ADS_ENABLED';")
print("INSERT INTO settings VALUES ('epoch',1) ON CONFLICT(key) DO UPDATE SET value=settings.value+1;")
print("END IF; END $restore$;")
print("COMMIT;")
