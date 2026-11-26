import assert from "node:assert/strict";
import { randomBytes } from "node:crypto";
import { test } from "node:test";
import { nickPairing } from "../dist/ttd-zalo-agent-server/src/adapters/nick-pairing.js";
import { PostgresRuntimeDatabase } from "../dist/ttd-zalo-agent-server/src/data/runtime-database.js";
import { Store } from "../dist/ttd-zalo-agent-server/src/store.js";

test("nick enrollment is one-use, rotates credentials, and persists STOP", {
  skip: process.env.RUN_POSTGRES_TESTS !== "1",
}, t => {
  const options = { user: "data_runtime", password: process.env.DATA_RUNTIME_PASSWORD };
  const identity = randomBytes(32).toString("hex");
  // Reuse the Store transaction and digest operations without altering runtime identity binding.
  function connect() {
    const db = new PostgresRuntimeDatabase(options);
    t.after(() => db.close());
    return Object.assign(Object.create(Store.prototype), { db, identityKey: identity });
  }
  const store = connect();
  const first = nickPairing(store);
  first.revoke();
  const offer = first.issue();
  assert.equal(first.exchange("invalid"), undefined);
  const enrolled = first.exchange(offer.code);
  assert.ok(enrolled?.credential);
  assert.equal(first.exchange(offer.code), undefined);
  const restarted = nickPairing(connect());
  assert.equal(restarted.accepts(enrolled.credential), true);
  const replacement = restarted.exchange(restarted.issue().code);
  assert.equal(first.accepts(enrolled.credential), false);
  assert.equal(first.accepts(replacement.credential), true);
  first.revoke();
  assert.equal(first.accepts(replacement.credential), false);
  assert.equal(store.setting("nick"), 1);
});
