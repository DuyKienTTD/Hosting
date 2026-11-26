#!/bin/sh
set -eu
umask 077
: "${BACKUP_REMOTE:?}" "${AGE_IDENTITY_FILE:?}" "${DATA_TOMBSTONE_KEY:?}"
[ "$#" -eq 2 ] || exit 2
name=$1
db=$2
case "$name" in *.dump.age) ;; *) exit 2 ;; esac
case "$name" in *[!a-zA-Z0-9.]* | .* ) exit 2 ;; esac
case "$db" in restore_* ) ;; * ) exit 2 ;; esac
case "$db" in *[!a-z0-9_]* ) exit 2 ;; esac
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
rclone copyto "$BACKUP_REMOTE/dumps/$name" "$tmp/dump.age"
# The marker must be provisioned independently and must not be in the dump.
rclone cat "$BACKUP_REMOTE/tombstones/_format" > "$tmp/format"
[ "$(cat "$tmp/format")" = z4-tombstones-v1 ]
rclone copy "$BACKUP_REMOTE/tombstones" "$tmp/tombstones"
age -d -i "$AGE_IDENTITY_FILE" -o "$tmp/dump" "$tmp/dump.age"
# Template is inaccessible to service roles throughout replay.
createdb -T template0 "$db"
psql -v ON_ERROR_STOP=1 -d "$db" -c 'REVOKE CONNECT ON DATABASE '"$db"' FROM PUBLIC'
pg_restore --exit-on-error --single-transaction -d "$db" "$tmp/dump"
script_dir=$(dirname "$0")
migrations="$script_dir/../postgres"
[ -f "$migrations/003-purge.sql" ] || migrations=/migrations
if [ "$(psql -X -A -t -v ON_ERROR_STOP=1 -d "$db" -c "SELECT to_regnamespace('purge_private') IS NULL")" = t ]; then
  psql -X -v ON_ERROR_STOP=1 -d "$db" -f "$migrations/003-purge.sql"
fi
psql -X -v ON_ERROR_STOP=1 -d "$db" -f "$migrations/purge-key.sql"
python3 "$script_dir/restore-tombstones.py" "$tmp/tombstones" > "$tmp/replay.sql"
psql -v ON_ERROR_STOP=1 -d "$db" -f "$tmp/replay.sql"
