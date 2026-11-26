#!/bin/sh
set -eu
: "${PURGE_RECEIPT_REMOTE:?}" "${PURGE_RECEIPT_BACKUP_REMOTE:?}"
[ "${PURGE_RECEIPT_REMOTE%/}" != "${PURGE_RECEIPT_BACKUP_REMOTE%/}" ]
rclone copy "${PURGE_RECEIPT_REMOTE}" "${PURGE_RECEIPT_BACKUP_REMOTE}" --immutable --include '/*.json'
