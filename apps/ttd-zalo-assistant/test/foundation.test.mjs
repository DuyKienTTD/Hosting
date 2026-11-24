import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { spawnSync } from "node:child_process";
import { Foundation, customers } from "../dist/foundation.js";

const target = "customer-a";
const second = "customer-b";
const content = "Bản nháp giả lập";
const allow = { retain: false, respond: true, send: true };
function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), "ttd-m0-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  return join(root, "foundation.sqlite");
}
function configure(db, id = target) {
  db.setStopped(false);
  db.setConsent(id, allow, Date.now() + 60_000, false);
}

test("same-name IDs stay separate; independent consent defaults to deny", (t) => {
  const db = new Foundation(fixture(t));
  t.after(() => db.close());
  assert.equal(customers[0].name, customers[1].name);
  assert.notEqual(customers[0].thread, customers[1].thread);
  assert.throws(() => db.approve(target, content), /SEND_DENIED/);
  configure(db);
  assert.equal(db.policy(target).respond, true);
  assert.equal(db.policy(target).retain, false);
  assert.equal(db.policy(second).send, false);
  assert.throws(() => db.policy("group-1"), /INVALID_TARGET/);
});

test("exact approval rejects edits, wrong destination and repeat; reopen preserves one receipt", async (t) => {
  const file = fixture(t);
  let db = new Foundation(file);
  configure(db);
  const id = db.approve(target, content);
  await assert.rejects(db.send(id, second, content), /APPROVAL_MISMATCH/);
  await assert.rejects(db.send(id, target, content + "!"), /APPROVAL_MISMATCH/);
  assert.equal((await db.send(id, target, content)).status, "fake-sent");
  await assert.rejects(db.send(id, target, content), /APPROVAL_MISMATCH/);
  db.close();
  db = new Foundation(file);
  t.after(() => db.close());
  assert.equal(db.status().fakeSends, 1);
  await assert.rejects(db.send(id, target, content), /APPROVAL_MISMATCH/);
});

test("STOP from a second SQLite connection during deferred preparation prevents initiation", async (t) => {
  const file = fixture(t);
  const db = new Foundation(file);
  const control = new Foundation(file);
  t.after(() => { db.close(); control.close(); });
  configure(db);
  const approved = db.approve(target, content);
  const wait = Promise.withResolvers();
  const pending = db.send(approved, target, content, () => wait.promise);
  control.setStopped(true);
  control.setStopped(false);
  wait.resolve();
  await assert.rejects(pending, /SEND_REVOKED/);
  assert.equal(db.status().fakeSends, 0);
});

test("revocation, takeover and expiry deny dispatch", async (t) => {
  const db = new Foundation(fixture(t));
  t.after(() => db.close());
  for (const change of [
    () => db.setConsent(target, { ...allow, send: false }, Date.now() + 60_000, false),
    () => db.setConsent(target, allow, Date.now() + 60_000, true),
    () => db.setConsent(target, allow, Date.now() - 1, false),
  ]) {
    configure(db);
    const id = db.approve(target, content);
    await assert.rejects(db.send(id, target, content, async () => change()), /SEND_REVOKED/);
  }
  assert.equal(db.status().fakeSends, 0);
});

test("process death after reservation cannot replay an in-memory approval", async (t) => {
  const file = fixture(t);
  const module = new URL("../dist/foundation.js", import.meta.url).href;
  const result = spawnSync(process.execPath, ["--input-type=module", "-e", `
    import {Foundation} from ${JSON.stringify(module)};
    const d=new Foundation(process.argv[1]);
    d.setStopped(false);
    d.setConsent("customer-a",{retain:false,respond:true,send:true},Date.now()+60000,false);
    const id=d.approve("customer-a","fixture");
    await d.send(id,"customer-a","fixture",async()=>{process.stdout.write(id);process.exit(23)});
  `, file], { encoding: "utf8" });
  assert.equal(result.status, 23, result.stderr);
  const db = new Foundation(file);
  t.after(() => db.close());
  assert.equal(db.status().fakeSends, 0);
  await assert.rejects(db.send(result.stdout, target, "fixture"), /APPROVAL_MISMATCH/);
});
