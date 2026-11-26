"""Generate and validate the content-addressed deployment manifest."""
import hashlib
import json
import re
import sys
from pathlib import Path

REPOSITORY = "DuyKienTTD/Hosting"
IMAGES = {name: f"ghcr.io/duykienttd/ttd-cskh-{name}" for name in ("runtime", "postgres")}
MIGRATIONS = Path("apps/ttd-zalo-agent-server/postgres")
NAME = re.compile(r"[0-9]{3}(?:-[a-z0-9-]+)?\.sql\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def entries(root):
    files = sorted(path for path in (root / MIGRATIONS).glob("[0-9]*.sql") if NAME.fullmatch(path.name))
    for expected, path in enumerate(files, 1):
        if int(path.name[:3]) != expected:
            raise ValueError("migration numbers must be contiguous and unique")
    if not files:
        raise ValueError("migration list is empty")
    return [{"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]


def read(path):
    data = json.loads(Path(path).read_text())
    if data.get("version") != 1 or not re.fullmatch(r"[a-f0-9]{40}", data.get("commit", "")):
        raise ValueError("invalid manifest version or commit")
    for kind, prefix in IMAGES.items():
        if not re.fullmatch(re.escape(prefix) + r"@sha256:[a-f0-9]{64}", data["images"][kind]):
            raise ValueError("invalid image reference")
    for index, item in enumerate(data["migrations"], 1):
        if (not NAME.fullmatch(item["file"]) or int(item["file"][:3]) != index or not DIGEST.fullmatch(item["sha256"])):
            raise ValueError("invalid migration entry")
    if not data["migrations"]:
        raise ValueError("migration list is empty")
    return data


def plan(path, root, ledger, adopt, rollback):
    data = read(path)
    expected = data["migrations"]
    root = Path(root)
    if expected != entries(root):
        raise ValueError("migration content differs from release commit")
    applied = Path(ledger).read_text().splitlines()
    lines = [item["file"] + "|" + item["sha256"] for item in expected]
    if applied != lines[:len(applied)]:
        raise ValueError("database migration history is not an exact prefix of the target manifest")
    mark = 0
    if not applied:
        names = [item["file"] for item in expected]
        if adopt not in names or rollback:
            raise ValueError("untracked database: confirm its applied prefix with --adopt-through FILE")
        mark = names.index(adopt) + 1
    elif adopt:
        raise ValueError("database already has a migration ledger")
    if rollback and applied != lines:
        raise ValueError("rollback requires the same applied schema")
    for line in lines[:mark]:
        print("adopt|" + line)
    for line in lines[max(len(applied), mark):]:
        print("apply|" + line)


def sql(root, plan_file):
    print("BEGIN;")
    print("SELECT pg_advisory_xact_lock(76425160);")
    print("CREATE TABLE IF NOT EXISTS public.release_migrations "
          "(name text PRIMARY KEY, sha256 text NOT NULL, applied_at timestamptz NOT NULL DEFAULT now());")
    for line in Path(plan_file).read_text().splitlines():
        op, name, checksum = line.split("|")
        if op not in ("apply", "adopt") or not NAME.fullmatch(name) or not DIGEST.fullmatch(checksum):
            raise ValueError("invalid migration plan")
        if op == "apply":
            data = (Path(root) / MIGRATIONS / name).read_text().strip().splitlines()
            if data[0] != "BEGIN;" or data[-1] != "COMMIT;":
                raise ValueError("migration must have one outer transaction")
            body = data[1:-1]
            if any(re.match(r"(?i)^\s*(?:COMMIT\s*;|ROLLBACK\s*;|BEGIN\s*;|\\)", row) for row in body):
                raise ValueError("unexpected transaction or psql command inside migration")
            print("\n".join(body))
        print(f"INSERT INTO public.release_migrations(name,sha256) VALUES ('{name}','{checksum}');")
    print("COMMIT;")


def main():
    action, *args = sys.argv[1:]
    if action == "build":
        commit, runtime, postgres = args
        print(json.dumps({"version": 1, "commit": commit,
                          "images": {"runtime": IMAGES["runtime"] + "@" + runtime,
                                     "postgres": IMAGES["postgres"] + "@" + postgres},
                          "migrations": entries(Path.cwd())}, indent=2))
    elif action == "values":
        data = read(args[0])
        print(data["commit"], data["images"]["runtime"], data["images"]["postgres"], sep="\n")
    elif action == "plan":
        path, root, ledger, adopt, mode = args
        plan(path, root, ledger, adopt, mode == "rollback")
    elif action == "sql":
        sql(*args)
    else:
        raise ValueError("unknown manifest action")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        sys.exit("Release manifest: " + str(exc))
