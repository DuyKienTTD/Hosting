#!/bin/sh
set -eu
umask 077
: "${BACKUP_REMOTE:?}" "${AGE_RECIPIENT:?}"
retention=${BACKUP_RETENTION_DAYS:-35}
case "$retention" in ''|*[!0-9]*) exit 2 ;; esac
[ "$retention" -ge 7 ]
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
name=$(date -u +%Y%m%dT%H%M%SZ).dump.age
pg_dump --format=custom --file "$tmp/dump"
age -r "$AGE_RECIPIENT" -o "$tmp/$name" "$tmp/dump"
rclone copyto "$tmp/$name" "$BACKUP_REMOTE/dumps/$name" --immutable
rclone delete "$BACKUP_REMOTE/dumps" --include '*.dump.age' --min-age "${retention}d"
