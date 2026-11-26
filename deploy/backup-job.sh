#!/bin/sh
set -eu
case "${1:-}" in
  postgres) sh /ops/backup.sh ;;
  receipts) sh /ops/backup-purge-receipts.sh ;;
  *) exit 2 ;;
esac
printf 'backup_success job=%s at=%s\n' "$1" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
