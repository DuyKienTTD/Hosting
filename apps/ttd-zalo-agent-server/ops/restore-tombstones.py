"""Reconcile independent evidence into a closed staging database."""
import hmac
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from uuid import UUID


def uuid(value):
    return str(UUID(value))


def version(value):
    if type(value) is not int or not 1 <= value <= 2147483647:
        raise ValueError("invalid version")
    return value


def command(args, env=None):
    try:
        result = subprocess.run(args, env=env, capture_output=True, text=True, timeout=8)
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def identity(item):
    event_id = item["event_id"]
    if not re.fullmatch("[a-f0-9]{64}", event_id):
        raise ValueError("invalid event ID")
    return (uuid(item["purge_id"]), uuid(item["id"]), uuid(item["conversation_id"]),
            event_id, version(item["version"]), version(item["policy_version"]))


def args_for(item):
    return ",".join(f"'{value}'" if isinstance(value, str) else str(value) for value in item)


def verify(item, status, proof):
    message = "|".join(map(str, ("z4-tombstone-v2", status, *item)))
    expected = hmac.digest(key, message.encode(), "sha256").hex()
    return isinstance(proof, str) and hmac.compare_digest(expected, proof)


def source(query):
    database = os.environ.get("RESTORE_SOURCE_DATABASE", os.environ.get("PGDATABASE", ""))
    if not database or database == os.environ["RESTORE_STAGING_DATABASE"]:
        return None
    env = dict(os.environ, PGDATABASE=database, PGCONNECT_TIMEOUT="4")
    for field in ("HOST", "PORT", "USER", "PASSWORD"):
        if "RESTORE_SOURCE_" + field in os.environ:
            env["PG" + field] = os.environ["RESTORE_SOURCE_" + field]
    return command(["psql", "-XAtq", "-v", "ON_ERROR_STOP=1", "-c", query], env)


def independent_evidence(item, pending):
    origin, xid, intent = (pending.get(field, "") for field in ("origin", "xid", "intent"))
    if not (isinstance(origin, str) and re.fullmatch(r"[0-9]{1,20}:[0-9]{1,10}", origin)
            and isinstance(xid, str) and re.fullmatch("[0-9]{1,20}", xid)
            and isinstance(intent, str) and verify(item, f"intent:{origin}:{xid}", intent)):
        origin = xid = intent = ""
    answer = source("SELECT status||' '||proof FROM public.purge_recovery_evidence("
                    + args_for((*item, origin, xid, intent)) + ")")
    if answer:
        status, _, proof = answer.partition(" ")
        if status in ("confirmed", "rolled_back") and verify(item, status, proof):
            return status, proof
    remote = os.environ.get("PURGE_RECEIPT_REMOTE", "").rstrip("/")
    if remote:
        raw = command(["rclone", "cat", remote + "/" + item[0] + ".json"])
        if raw:
            try:
                ledger = json.loads(raw)
                status, proof = ledger["status"], ledger["proof"]
                if identity(ledger) == item and status in ("confirmed", "rolled_back") and verify(item, status, proof):
                    return status, proof
            except (ValueError, TypeError, KeyError):
                pass
    return None


key = bytes.fromhex(os.environ["DATA_TOMBSTONE_KEY"])
root = Path(sys.argv[1])
pending_files = {path.name: path for path in (root / "pending").glob("*.json")}
confirmed_files = {path.name: path for path in (root / "confirmed").glob("*.json")}
print("BEGIN;")
for path in sorted(root.glob("*.json")):
    # Old flat artifacts have no evidence of commit and no purge UUID.
    record = uuid(path.stem)
    item = json.loads(path.read_text())
    if uuid(item["id"]) != record:
        raise ValueError("invalid legacy tombstone")
    print(f"SELECT purge_private.quarantine_restore('{record}','{record}',"
          f"{version(item['version'])},{version(item['policy_version'])});")

for name in sorted(pending_files.keys() | confirmed_files.keys()):
    pending = json.loads(pending_files[name].read_text()) if name in pending_files else {}
    confirmed = json.loads(confirmed_files[name].read_text()) if name in confirmed_files else {}
    item = identity(pending or confirmed)
    if name != item[0] + ".json" or (confirmed and identity(confirmed) != item):
        raise ValueError("invalid tombstone identity")
    evidence = independent_evidence(item, pending)
    if not evidence and verify(item, "confirmed", confirmed.get("proof")):
        evidence = "confirmed", confirmed["proof"]
    attempt, record, thread, _, revision, policy = item
    if not evidence:
        print(f"SELECT purge_private.quarantine_restore('{attempt}','{record}',{revision},{policy});")
    elif evidence[0] == "rolled_back":
        print("INSERT INTO audit_log(actor,action,record_id)"
              f" VALUES('restore','pending_rollback_verified','{record}');")
    elif source(f"SELECT public.purge_restore_held('{record}','{thread}')") == "t":
        print(f"INSERT INTO legal_holds(message_id,reason) SELECT '{record}','restore_source_hold'"
              f" WHERE NOT EXISTS (SELECT 1 FROM legal_holds WHERE message_id='{record}' AND released_at IS NULL);")
        print("INSERT INTO audit_log(actor,action,record_id)"
              f" VALUES('restore','purge_blocked','{record}');")
        print("DO $$ BEGIN RAISE WARNING 'restore_tombstone_blocked_by_source_hold'; END $$;")
    else:
        print(f"SELECT purge_private.replay_tombstone({args_for((*item, evidence[1]))});")

print("DO $$ BEGIN IF to_regclass('settings') IS NOT NULL THEN")
print("UPDATE settings SET value=1 WHERE key='global';")
print("UPDATE settings SET value=0 WHERE key='ADS_ENABLED';")
print("INSERT INTO settings VALUES ('epoch',1) ON CONFLICT(key) DO UPDATE SET value=settings.value+1;")
print("END IF; END $$;")
print("UPDATE purge_private.restore_gate SET reconciled=true WHERE slot;")
print("COMMIT;")
