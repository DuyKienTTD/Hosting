#!/bin/sh
set -eu
umask 077
source_file=${RCLONE_CONFIG_SOURCE:-/run/rclone-source.conf}
export RCLONE_CONFIG="${RCLONE_CONFIG:-/run/rclone-live/rclone.conf}"
[ "$#" -gt 0 ] && [ -f "$source_file" ] && [ "$RCLONE_CONFIG" != "$source_file" ] || exit 2
# Redirection creates a file owned by this process, even when the source is 0400.
temporary=$(mktemp "${RCLONE_CONFIG}.XXXXXX")
trap 'rm -f "$temporary"' EXIT
cat "$source_file" > "$temporary"
chmod 0600 "$temporary"
mv -f "$temporary" "$RCLONE_CONFIG"
trap - EXIT
exec "$@"
