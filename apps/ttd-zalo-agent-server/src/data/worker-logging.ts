const safeCodes = new Set([
  "tombstone_archive_unavailable",
  "invalid_tombstone_format",
  "tombstone_archive_mismatch",
  "invalid_tombstone_archive",
  "invalid_tombstone_key",
  "invalid_purge_receipt_remote",
  "invalid_pending_identity",
  "purge_rejected",
]);

export function workerFailureCode(error: unknown): string {
  return error instanceof Error && safeCodes.has(error.message) ? error.message : "unknown";
}
