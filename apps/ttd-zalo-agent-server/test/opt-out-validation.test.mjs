import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { classifyOptOut } from "../dist/ttd-zalo-agent-server/src/opt-out.js";
import { defaults } from "../dist/ttd-zalo-agent-server/src/config.js";

test("preserved opt-out validation corpus blocks positive ads and avoids false permanent stops", async t => {
  const corpus = JSON.parse(await readFile(new URL("./fixtures/opt-out-validation.json", import.meta.url)));
  assert.equal(corpus.positive.length, 30);
  assert.equal(corpus.negative.length, 20);
  const missed = corpus.positive.filter(text => classifyOptOut(text, defaults.advertising) === "none");
  const falseStops = corpus.negative.filter(text => classifyOptOut(text, defaults.advertising) === "stop");
  const positives = 30 - missed.length;
  const negatives = 20 - falseStops.length;
  t.diagnostic(`positive=${positives}/30 negative=${negatives}/20`);
  assert.ok(positives >= 29, JSON.stringify(missed));
  assert.deepEqual(falseStops, []);
});
