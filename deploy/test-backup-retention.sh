#!/bin/bash
set -eu
temp=$(mktemp -d)
trap 'rm -rf "$temp"' EXIT
export PATH="$temp:$PATH" BACKUP_REMOTE=fixture:root AGE_RECIPIENT=fixture BACKUP_RETENTION_COUNT=30
export FIXTURE_REMOVED="$temp/removed"
for tool in pg_dump age; do
  printf '#!/bin/sh\nexit 0\n' > "$temp/$tool"
done
cat > "$temp/rclone" <<'SH'
#!/bin/sh
case "$1" in
  copyto) exit 0 ;;
  lsf)
    for day in $(seq 1 31); do printf '202611%02dT023000Z.dump.age\n' "$day"; done
    printf 'unrelated.dump.age\n'
    ;;
  deletefile) printf '%s\n' "$2" >> "$FIXTURE_REMOVED" ;;
  *) exit 17 ;;
esac
SH
chmod +x "$temp/pg_dump" "$temp/age" "$temp/rclone"
sh apps/ttd-zalo-agent-server/ops/backup.sh
test "$(cat "$FIXTURE_REMOVED")" = fixture:root/dumps/20261101T023000Z.dump.age
