import assert from "node:assert/strict";
import { readFileSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { DatabaseSync } from "node:sqlite";
import { test } from "node:test";
import { Foundation } from "../dist/foundation.js";

const a = "customer-a";
const b = "customer-b";
const allow = { retain: true, respond: true, send: true };
function fixture(t) {
  const dir = mkdtempSync(join(tmpdir(), "ttd-mvp-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return join(dir, "db.sqlite");
}
function consent(db, target, scopes = allow, takeover = false) {
  db.setConsent(target, scopes, Date.now() + 60_000, takeover);
}
function receive(db, text = "Cho hỏi SKU MAU-01") { return db.receive(a, "msg-1", text); }
const doc = "SKU: MAU-01\nTên: Mẫu lan can A\nThông tin: Thép mạ kẽm";

test("fake DM -> sourced draft -> edited exact approval -> one fake send across reopen", async (t) => {
  const path = fixture(t);
  let db = new Foundation(path);
  db.setStopped(false);
  consent(db, a);
  db.importKnowledge(doc);
  const msg = receive(db);
  const draft = db.draft(a, msg.id);
  assert.equal(draft.source.id, "MAU-01");
  assert.match(draft.text, /Thép mạ kẽm/);
  assert.throws(() => db.draft(b, msg.id), /DRAFT_DENIED/);
  const original = db.approve(a, draft.text, msg.id);
  db.invalidateApprovals(a);
  await assert.rejects(db.send(original, a, draft.text), /APPROVAL_MISMATCH/);
  const edited = draft.text + ". Xin cảm ơn.";
  const grant = db.approve(a, edited, msg.id);
  await assert.rejects(db.send(grant, b, edited), /APPROVAL_MISMATCH/);
  assert.equal((await db.send(grant, a, edited)).status, "fake-sent");
  const repeated = db.approve(a, edited, msg.id);
  await assert.rejects(db.send(repeated, a, edited), /UNIQUE/);
  db.close();
  db = new Foundation(path);
  t.after(() => db.close());
  assert.equal(receive(db).state, "duplicate");
  assert.equal(db.status().fakeSends, 1);
  assert.throws(() => db.draft(a, msg.id), /DRAFT_DENIED/);
  assert.equal(db.activity().attempts.length, 1);
});

test("denied and response-only sentinels absent from SQLite; retained data stays scoped", (t) => {
  const path = fixture(t);
  let db = new Foundation(path);
  db.setStopped(false);
  assert.equal(db.receive(a, "denied", "RAW_DENIED_SENTINEL").state, "denied");
  consent(db, a, { retain: false, respond: true, send: false });
  const msg = db.receive(a, "ephemeral", "RAW_EPHEMERAL_SENTINEL");
  assert.equal(msg.state, "ephemeral");
  assert.equal(msg.canDraft, true);
  assert.deepEqual(db.conversation(a), []);
  assert.throws(() => db.remember(a, msg.id, "RAW_EPHEMERAL_SENTINEL"), /MEMORY_DENIED/);
  consent(db, a, { retain: true, respond: false, send: false });
  consent(db, b);
  const retained = db.receive(a, "keep", "Khách quan tâm mẫu A");
  assert.equal(retained.canDraft, false);
  assert.throws(() => db.draft(a, retained.id), /DRAFT_DENIED/);
  db.remember(a, retained.id, "mẫu A");
  assert.throws(() => db.remember(b, retained.id, "mẫu A"), /MEMORY_DENIED/);
  db.close();
  assert.equal(readFileSync(path).includes(Buffer.from("RAW_DENIED_SENTINEL")), false);
  assert.equal(readFileSync(path).includes(Buffer.from("RAW_EPHEMERAL_SENTINEL")), false);
  db = new Foundation(path);
  t.after(() => db.close());
  assert.equal(db.conversation(a).length, 1);
  assert.equal(db.profile(a)[0].source, retained.id);
  assert.deepEqual(db.conversation(b), []);
  assert.deepEqual(db.profile(b), []);
  consent(db, a, { retain: false, respond: false, send: false });
  assert.deepEqual(db.conversation(a), []);
  assert.deepEqual(db.profile(a), []);
});

test("document data is plain text and unknown price leads to clarification", (t) => {
  const db = new Foundation(fixture(t)); t.after(() => db.close());
  db.setStopped(false);
  consent(db, a);
  assert.throws(() => db.importKnowledge("<script>alert(1)</script>"), /INVALID_DOCUMENT/);
  assert.equal(db.importKnowledge(doc), "MAU-01");
  assert.throws(() => db.importKnowledge(doc), /UNIQUE/);
  assert.equal(db.knowledge("MAU-01")[0].id, "MAU-01");
  const msg = receive(db, "Giá SKU MAU-01 bao nhiêu?");
  const draft = db.draft(a, msg.id);
  assert.equal(draft.source, null);
  assert.match(draft.text, /xác nhận/);
});

test("revocation after reservation closes the attempt and blocks future retry", async (t) => {
  const path = fixture(t);
  const db = new Foundation(path);
  const peer = new Foundation(path);
  t.after(() => { db.close(); peer.close(); });
  db.setStopped(false);
  consent(db, a);
  const { id } = receive(db);
  const grant = db.approve(a, "Nội dung mẫu", id);
  await assert.rejects(db.send(grant, a, "Nội dung mẫu", async () => {
    consent(peer, a, allow, true);
  }), /SEND_REVOKED/);
  assert.equal(db.status().fakeSends, 0);
  assert.equal(db.activity().attempts[0].status, "closed");
  consent(peer, a);
  assert.equal(db.receive(a, "msg-1", "Tin lặp").state, "duplicate");
  assert.throws(() => db.approve(a, "Nội dung mẫu", id), /DRAFT_DENIED/);
});

test("migrates an M0 schema while preserving STOP, consent and old receipts", (t) => {
  const path = fixture(t);
  const v1 = new DatabaseSync(path);
  v1.exec(`
    CREATE TABLE state(id INTEGER PRIMARY KEY, stopped INTEGER NOT NULL, epoch INTEGER NOT NULL);
    INSERT INTO state VALUES(1,1,5);
    CREATE TABLE consent(target TEXT PRIMARY KEY, revision INTEGER NOT NULL, expires INTEGER NOT NULL,
      retain INTEGER NOT NULL, respond INTEGER NOT NULL, send INTEGER NOT NULL, takeover INTEGER NOT NULL);
    INSERT INTO consent VALUES('customer-a',7,1890000000000,1,1,1,0);
    CREATE TABLE attempt(id TEXT PRIMARY KEY, target TEXT NOT NULL, status TEXT NOT NULL);
    INSERT INTO attempt VALUES('legacy','customer-a','sent');
    CREATE TABLE receipt(id TEXT PRIMARY KEY REFERENCES attempt(id));
    INSERT INTO receipt VALUES('legacy');
    PRAGMA user_version=1;
  `);
  v1.close();
  const db = new Foundation(path); t.after(() => db.close());
  assert.equal(db.status().stopped, true);
  assert.equal(db.status().fakeSends, 1);
  assert.equal(db.policy(a).revision, 7);
  assert.deepEqual(db.conversation(a), []);
});
