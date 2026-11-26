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
    values = f"'{record_id}','{conversation_id}','{event_id}',{revision},{policy}"
    print(f"INSERT INTO restore_tombstones VALUES ({values}) ON CONFLICT (record_id) DO NOTHING;")
    print(
        "INSERT INTO deletion_log(record_id,conversation_id,event_id,version,policy_version,reason_code,action) "
        f"VALUES ({values},'retention_elapsed','restore_tombstone') ON CONFLICT DO NOTHING;"
    )
    print(f"DELETE FROM messages WHERE id='{record_id}' OR (conversation_id='{conversation_id}' AND event_id='{event_id}');")
print("COMMIT;")
