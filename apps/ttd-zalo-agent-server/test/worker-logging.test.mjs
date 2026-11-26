import assert from "node:assert/strict";
import { test } from "node:test";
import { workerFailureCode } from "../dist/ttd-zalo-agent-server/src/data/worker-logging.js";

test("worker logs only exact internal error codes", () => {
  assert.equal(workerFailureCode(new Error("tombstone_archive_unavailable")), "tombstone_archive_unavailable");
  assert.equal(workerFailureCode(new Error("invalid_tombstone_format")), "invalid_tombstone_format");
  assert.equal(workerFailureCode(new Error("invalid_tombstone_format: private value")), "unknown");
  assert.equal(workerFailureCode({ message: "invalid_tombstone_format" }), "unknown");
});
