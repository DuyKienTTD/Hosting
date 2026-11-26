#!/bin/sh
set -eu
umask 077
if [ "${1:-}" = --dry-run ]; then
  printf '%s\n' 'Plan: install/check rclone; headless gdrive scope drive.file; initialize backup and receipt paths.'
  exit 0
fi
[ "$#" -eq 0 ] && [ "$(id -u)" -eq 0 ] && [ -t 0 ] || exit 2
if ! command -v rclone >/dev/null 2>&1; then
  apt-get update
  apt-get install -y rclone
fi
dir=${SECRETS_DIR:?set the private configuration directory}
config=$dir/rclone.conf
remote=${RCLONE_REMOTE:-gdrive}
prefix=${BACKUP_PREFIX:?set the target prefix}
uid=${RCLONE_CONFIG_UID:-1000}
gid=${RCLONE_CONFIG_GID:-1000}
install -d -m 0700 "$dir"
if [ -e "$config" ] || [ -L "$config" ] || [ -e "$dir/rclone-worker.conf" ] || [ -L "$dir/rclone-worker.conf" ]; then
  printf '%s\n' 'Config already exists. Preserve it and review the migration in RUNBOOK.' >&2
  exit 1
fi
tmp=$(mktemp -d "$dir/.gdrive.XXXXXX")
trap 'rm -rf "$tmp"' EXIT
script_dir=$(dirname "$0")
python3 "$script_dir/rclone-oauth.py" "$tmp" "$remote"
for path in dumps receipts receipts-backup tombstones; do
  rclone --config "$tmp/rclone.conf" mkdir "$remote:$prefix/$path"
done
printf 'z4-tombstones-v1\n' > "$tmp/format"
rclone --config "$tmp/rclone.conf" copyto "$tmp/format" "$remote:$prefix/tombstones/_format" --immutable
# Keep the administrative copy separate from the worker bind mount.
install -o 0 -g 0 -m 0600 "$tmp/rclone.conf" "$config"
install -o "$uid" -g "$gid" -m 0400 "$tmp/rclone.conf" "$dir/rclone-worker.conf"
printf '%s\n' "Configured $config"
