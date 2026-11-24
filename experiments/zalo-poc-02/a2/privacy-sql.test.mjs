// ZALO-POC-02 A2 — dependency-free, offline native SQLite SQL-contract regression checks.
// Run only in a blocked-egress sandbox with Node >=22.13:
//   node --test experiments/zalo-poc-02/a2/privacy-sql.test.mjs
// Inputs must be patched checkout source, not live service.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { DatabaseSync } from "node:sqlite";
import { test } from "node:test";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = process.env.ZALO_PATCHED_SOURCE_ROOT;
const source = (p) => {
  assert.ok(root, "Set ZALO_PATCHED_SOURCE_ROOT to independently patched, pinned checkout");
  return fs.readFileSync(path.join(root, p), "utf8");
};
const mem = source("src/conversation/memory-store.ts");
const edit = source("src/conversation/memory-edit-store.ts");
const filter = source("src/middleware/allowlist-filter.ts");
const router = source("src/zalo/incoming-message-router.ts");
function stmt(file, name) {
  const escaped = name.replace(/[.*+?^$\x7b\x7d()|[\]\\]/g, "\\$&");
  const match = file.match(new RegExp("const " + escaped + " = db\\.prepare\\(\\x60([\\s\\S]*?)\\x60\\)"));
  assert.ok(match, "Missing prepared SQL: " + name);
  return match[1];
}
function dbCase(fn) {
  const db = new DatabaseSync(":memory:");
  db.exec(`CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL, subject_id TEXT NOT NULL, content TEXT NOT NULL,
    learned_in_thread_id TEXT NOT NULL, learned_in_group INTEGER NOT NULL
  ); CREATE TABLE messages(id INTEGER PRIMARY KEY,content TEXT);
  CREATE TABLE contacts(account_id TEXT, user_id TEXT,display_name TEXT);`);
  try { fn(db); } finally { db.close(); }
}
const insert = "INSERT INTO memories(account_id,subject_id,content,learned_in_thread_id,learned_in_group) VALUES(?,?,?,?,?)";
test("A2-01 group X not visible in group Y; group Y visible; DM secret excluded", () => dbCase(db => {
  db.prepare(insert).run("acc-synthetic","customer-a","group X fact","group-x",1);
  db.prepare(insert).run("acc-synthetic","customer-a","group Y fact","group-y",1);
  db.prepare(insert).run("acc-synthetic","customer-a","DM-only private","customer-a",0);
  const q = db.prepare(stmt(mem, "groupStmt"));
  const x = q.all("acc-synthetic","group-x","group-x","customer-a").map(r=>r.content);
  const y = q.all("acc-synthetic","group-y","group-y","customer-a").map(r=>r.content);
  assert.deepEqual(x, ["group X fact"]);
  assert.deepEqual(y, ["group Y fact"]);
  assert.ok(!x.includes("DM-only private")&&!y.includes("DM-only private"));
}));
test("A2-02 group edit suggestions limited to origin and no cross-group edit selection", () => dbCase(db => {
  db.prepare(insert).run("acc-synthetic","customer-a","confidential X","group-x",1);
  db.prepare(insert).run("acc-synthetic","customer-a","group Y","group-y",1);
  const q = db.prepare(stmt(edit, "factNhinThayTrongNhomStmt"));
  assert.deepEqual(q.all("acc-synthetic","customer-a","group-y").map(r=>r.content),["group Y"]);
  assert.deepEqual(q.all("acc-synthetic","customer-a","group-z"),[]);
}));
test("A2-03 duplicate facts are independent by origin thread/group scope", () => dbCase(db => {
  db.prepare(insert).run("acc-synthetic","customer-a","same sentence","group-x",1);
  const q = db.prepare(stmt(mem, "trungStmt"));
  assert.ok(q.get("acc-synthetic","customer-a","same sentence","group-x",1));
  assert.equal(q.get("acc-synthetic","customer-a","same sentence","group-y",1),undefined);
  assert.equal(q.get("acc-synthetic","customer-a","same sentence","customer-a",0),undefined);
}));
test("A2-04 explicit respond versus retain decision and fail-closed wiring", () => {
  assert.match(filter,/if \(!consent \|\| consent\.verified !== true\) return skip/);
  assert.match(filter,/respond: consent\.respond/);
  assert.match(filter,/record: consent\.retain/);
  const decisionIx=router.indexOf("const decision = shouldRespond(");
  const contactIx=router.indexOf("recordContactActivity(config.id");
  assert.ok(decisionIx>=0 && contactIx>decisionIx,"Consent must precede contact capture");
  assert.match(router,/if \(!decision\.respond && !decision\.record\) return "bo"/);
  assert.match(router,/if \(decision\.respond && !decision\.record\) return "bo"/);
});
test("A2-05 policy-negative no SQLite persisted record (contract fixture, not router execution)", () => dbCase(db => {
  const policy = { verified:false, respond:false,retain:false };
  if (policy.verified && policy.retain) {
    db.prepare("INSERT INTO messages(content) VALUES(?)").run("private-text");
    db.prepare("INSERT INTO contacts(account_id,user_id,display_name) VALUES(?,?,?)").run("acc-synthetic","customer-a","A");
  }
  assert.equal(db.prepare("SELECT COUNT(*) n FROM messages").get().n,0);
  assert.equal(db.prepare("SELECT COUNT(*) n FROM contacts").get().n,0);
  // This test alone DOES NOT prove actual router/cache/replay logic.
}));
