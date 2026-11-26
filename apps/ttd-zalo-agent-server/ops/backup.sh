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
pg_dump --exclude-table-data=purge_private.signing_key --format=custom --file "$tmp/dump"
age -r "$AGE_RECIPIENT" -o "$tmp/$name" "$tmp/dump"
rclone copyto "$tmp/$name" "$BACKUP_REMOTE/dumps/$name" --immutable
if [ -n "${BACKUP_RETENTION_COUNT:-}" ]; then
  count=$BACKUP_RETENTION_COUNT
  case "$count" in ''|0*|*[!0-9]*) exit 2 ;; esac
  rclone lsf --files-only "$BACKUP_REMOTE/dumps" > "$tmp/files"
  LC_ALL=C sort -r "$tmp/files" > "$tmp/sorted"
  awk -v keep="$count" 'length($0)==25 && substr($0,1,8)~/^[0-9]+$/ && substr($0,9,1)=="T" && substr($0,10,6)~/^[0-9]+$/ && substr($0,16)=="Z.dump.age" && ++n>keep' "$tmp/sorted" > "$tmp/expired"
  while IFS= read -r expired; do
    rclone deletefile "$BACKUP_REMOTE/dumps/$expired"
  done < "$tmp/expired"
else
  rclone delete "$BACKUP_REMOTE/dumps" --include '*.dump.age' --min-age "${retention}d"
fi
