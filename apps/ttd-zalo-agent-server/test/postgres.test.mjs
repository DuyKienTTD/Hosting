import assert from "node:assert/strict";
import { randomBytes, randomUUID } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { Pool } from "pg";
import { authenticate, PostgresRepository } from "../dist/ttd-zalo-agent-server/src/data/repository.js";
import { remoteArchive, requestDeletion, runRetention } from "../dist/ttd-zalo-agent-server/src/data/deletion.js";

const config = process.env;
test("Postgres grants, deletion, encrypted backup and restore", { skip: config.RUN_POSTGRES_TESTS !== "1" }, async t => {
  const admin = new Pool();
  const app = new Pool({ user: "data_app", password: config.DATA_APP_PASSWORD });
  const worker = new Pool({ user: "data_worker", password: config.DATA_WORKER_PASSWORD });
  const root = mkdtempSync(join(tmpdir(), "z4-data-"));
  const restore = "restore_" + randomBytes(8).toString("hex");
  t.after(async () => {
    await Promise.all([app.end(), worker.end()]);
    await admin.query(`DROP DATABASE IF EXISTS ${restore}`);
    await admin.end();
    rmSync(root, { recursive: true, force: true });
  });
  const repository = new PostgresRepository(app, 30);
  const principal = role => {
    const token = randomBytes(32).toString("hex");
    return authenticate(token, { ["DATA_TOKEN_" + role]: token });
  };
  const support = principal("SUPPORT");
  const crm = principal("CRM");
  const channel = principal("CHANNEL");
  const retention = principal("RETENTION");
  const operator = principal("OPERATOR");
  let customer, conversation;
  await t.test("field grants, authenticated tasks and inert customer @", async () => {
    await assert.rejects(repository.createTask({ role: "operator" }, "synthetic"), /forbidden/);
    await assert.rejects(repository.createTask(channel, "synthetic"), /forbidden/);
    await assert.rejects(repository.addCustomer(support, "synthetic"), /forbidden/);
    customer = await repository.addCustomer(crm, "synthetic");
    assert.equal(await repository.renameCustomer(crm, customer, "fixture"), true);
    assert.equal((await repository.readCustomer(support, customer)).display_name, "fixture");
    conversation = (await admin.query("INSERT INTO conversations(customer_id,channel) VALUES($1,'oa') RETURNING id", [customer])).rows[0].id;
    assert.equal(await repository.ingest(channel, conversation, "fixture-event", "@operator create task"), true);
    assert.equal(await repository.ingest(channel, conversation, "fixture-event", "replay"), false);
    assert.equal((await repository.readMessages(support, conversation))[0].body, "@operator create task");
    assert.equal(Number((await admin.query("SELECT count(*) FROM tasks")).rows[0].count), 0);
    const task = await repository.createTask(support, "synthetic");
    await assert.rejects(repository.updateTask(support, task, "done"), /forbidden/);
    assert.equal(await repository.updateTask(operator, task, "done"), true);
    await assert.rejects(app.query("UPDATE customers SET created_at=now()"), /permission denied/);
    await assert.rejects(app.query("SELECT * FROM messages"), /permission denied/);
    await assert.rejects(app.query("SELECT * FROM consents"), /permission denied/);
    await assert.rejects(worker.query("DELETE FROM messages"), /permission denied/);
    await assert.rejects(worker.query("TRUNCATE deletion_log"), /permission denied/);
  });

  const record = (await admin.query("SELECT id FROM messages WHERE conversation_id=$1", [conversation])).rows[0].id;
  const request = { record_id: record, expected_version: 1, policy_version: 1, reason_code: "retention_elapsed" };
  await t.test("rejects unexpired, forged, stale, unsupported and held records", async () => {
    await assert.rejects(requestDeletion(worker, support, request), /forbidden/);
    for (const delta of [{ record_id: "*" }, { reason_code: "DROP TABLE messages" }, { bypass: true }]) {
      await assert.rejects(requestDeletion(worker, retention, { ...request, ...delta }), /invalid_deletion_request/);
    }
    assert.equal(await requestDeletion(worker, retention, request), false);
    await admin.query("UPDATE messages SET retain_until=now()-interval '1 day' WHERE id=$1", [record]);
    assert.equal(await requestDeletion(worker, retention, { ...request, expected_version: 2 }), false);
    assert.equal(await requestDeletion(worker, retention, { ...request, policy_version: 2 }), false);
    await admin.query("INSERT INTO legal_holds(customer_id,reason) VALUES($1,'fixture')", [customer]);
    assert.equal(await requestDeletion(worker, retention, request), false);
    await admin.query("UPDATE legal_holds SET released_at=now() WHERE customer_id=$1", [customer]);
    assert.equal(await requestDeletion(worker, retention, { ...request, record_id: randomUUID() }), false);
    const proof = (await admin.query(`INSERT INTO consents(customer_id,purpose,displayed_text,policy_version,evidence)
      VALUES($1,'ads','fixture','1','{}') RETURNING id`, [customer])).rows[0].id;
    assert.equal(await requestDeletion(worker, retention, { ...request, record_id: proof }), false);
  });

  await t.test("quarantine, recheck hold, archive before purge, replay old backup", async () => {
    const env = { ...config, BACKUP_REMOTE: root, AGE_IDENTITY_FILE: join(root, "restore-key") };
    execFileSync("age-keygen", ["-o", env.AGE_IDENTITY_FILE], { stdio: ["ignore", "ignore", "ignore"] });
    env.AGE_RECIPIENT = execFileSync("age-keygen", ["-y", env.AGE_IDENTITY_FILE], { encoding: "utf8" }).trim();
    mkdirSync(join(root, "tombstones"));
    writeFileSync(join(root, "tombstones", "_format"), "z4-tombstones-v1");
    execFileSync("sh", ["ops/backup.sh"], { env });
    const dump = readdirSync(join(root, "dumps"))[0];
    assert.match(dump, /\.dump\.age$/);
    assert.equal(await requestDeletion(worker, retention, request), true);
    assert.equal(await requestDeletion(worker, retention, request), false);
    assert.deepEqual(await repository.readMessages(support, conversation), []);
    await runRetention(worker, async () => assert.fail("quarantine not elapsed"));
    await admin.query("UPDATE messages SET purge_after=now()-interval '1 second' WHERE id=$1", [record]);
    await admin.query("INSERT INTO legal_holds(message_id,reason) VALUES($1,'fixture')", [record]);
    await runRetention(worker, async () => assert.fail("held record"));
    await admin.query("UPDATE legal_holds SET released_at=now() WHERE message_id=$1", [record]);
    await assert.rejects(runRetention(worker, async () => { throw Error("archive failed"); }), /archive failed/);
    assert.equal((await admin.query("SELECT id FROM messages WHERE id=$1", [record])).rowCount, 1);
    await runRetention(worker, remoteArchive(root));
    assert.equal((await admin.query("SELECT id FROM messages WHERE id=$1", [record])).rowCount, 0);
    assert.equal(await repository.ingest(channel, conversation, "fixture-event", "replay after purge"), false);
    await assert.rejects(admin.query("DELETE FROM deletion_log"), /append_only/);
    execFileSync("sh", ["ops/restore.sh", dump, restore], { env });
    const restored = new Pool({ database: restore });
    try {
      assert.equal((await restored.query("SELECT id FROM messages WHERE id=$1", [record])).rowCount, 0);
      assert.equal((await restored.query("SELECT record_id FROM restore_tombstones WHERE record_id=$1", [record])).rowCount, 1);
      assert.equal((await restored.query("SELECT id FROM consents WHERE customer_id=$1", [customer])).rowCount, 1);
      assert.equal((await restored.query("SELECT id FROM legal_holds WHERE customer_id=$1", [customer])).rowCount, 1);
      await assert.rejects(restored.query(
        "INSERT INTO messages(conversation_id,event_id,body,retain_until) SELECT conversation_id,event_id,'replay',now() FROM restore_tombstones",
      ), /erased_event/);
    } finally { await restored.end(); }
  });
});

test("Postgres runtime role processes customer input through AI, Guard and durable send_log",
  { skip: config.RUN_POSTGRES_TESTS !== "1" }, async t => {
    const { Store } = await import("../dist/ttd-zalo-agent-server/src/store.js");
    const { PostgresRuntimeDatabase } = await import("../dist/ttd-zalo-agent-server/src/data/runtime-database.js");
    const { Runtime } = await import("../dist/ttd-zalo-agent-server/src/runtime.js");
    const { MockChannel } = await import("../dist/ttd-zalo-agent-server/src/channel.js");
    const { FakeProvider } = await import("../dist/ttd-zalo-agent-server/src/provider.js");
    const { defaults } = await import("../dist/ttd-zalo-agent-server/src/config.js");
    const db = new PostgresRuntimeDatabase({ user: "data_runtime", password: config.DATA_RUNTIME_PASSWORD });
    const admin = new Pool();
    t.after(async () => { db.close(); await admin.end(); });
    const store = new Store(db, "synthetic-runtime-binding");
    const timestamp = Date.parse("2026-11-26T03:00:00Z");
    const clock = () => timestamp;
    const customer = "synthetic-contact";
    const target = store.hash(customer);
    store.stop("global", false);
    store.consent(target, timestamp + 86_400_000, true, true, true, true, {
      displayedText: "Dữ liệu giả lập", policyVersion: "fixture-1", evidence: { fixture: true },
    });
    const settings = structuredClone(defaults);
    settings.advertising.enabled = true; // PostgreSQL setting remains authoritative.
    const mock = new MockChannel();
    mock.contacts.set(customer, { id: customer, friend: true });
    store.knowledge.add({ id: "fixture-z4", sku: "MAU-01", kind: "product", title: "Mẫu thử",
      summary: "Chiều cao 900 mm", version: "1", effective: "2026-01-01", until: null,
      origin: "fixture", amount: null, unit: null });
    mock.events.push({ id: "event-z4", contact: customer, thread: "thread-z4", kind: "dm", at: timestamp,
      text: "Chiều cao và giá của MAU-01?", channel: "oa" });
    let calls = 0;
    const provider = new FakeProvider(task => { calls++; return task.choices.includes("support") ? "support" : task.choices.includes("answer") ? "answer" : "none"; });
    const runtime = new Runtime(store, mock, provider, settings, clock);
    const send = mock.sendMessage;
    let observedReservation = false;
    mock.sendMessage = async request => {
      const { rows } = await admin.query("SELECT state,customer_id FROM send_log WHERE id=$1", [request.key]);
      assert.equal(rows[0]?.state, "reserved");
      assert.ok(rows[0].customer_id);
      observedReservation = true;
      return send(request);
    };
    assert.equal(await runtime.tick(), true);
    assert.ok(calls > 0, "FakeProvider received the request");
    assert.ok(observedReservation, "transport saw committed reservation");
    assert.equal(mock.sent.size, 1);
    assert.equal(db.prepare("SELECT state FROM send_log WHERE target=? AND kind='reply'").get(target).state, "sent");
    const eventKey = store.eventKey(customer, "thread-z4", "event-z4");
    assert.equal(db.prepare("SELECT state FROM ledger WHERE id=?").get(eventKey + "-support").state, "settled");
    assert.equal((await admin.query("SELECT count(*)::int n FROM messages WHERE event_id=$1",
      [store.eventKey(customer, "thread-z4", "event-z4")])).rows[0].n, 1);

    const ad = id => ({ id, target: customer, agent: "campaign", kind: "advertising", text: "Synthetic",
      epoch: store.setting("epoch"), revision: store.contact(target, timestamp).revision });
    assert.equal(await runtime.guard.dispatch(ad("disabled")), "ads_disabled");
    store.set("ADS_ENABLED", 1);
    const getContact = mock.getContact.bind(mock);
    mock.getContact = async request => {
      await admin.query("UPDATE settings SET value=0 WHERE key='ADS_ENABLED'");
      return getContact(request);
    };
    assert.equal(await runtime.guard.dispatch(ad("revoked-during-lookup")), "ads_disabled");
    assert.equal(mock.sent.size, 1);
    store.set("ADS_ENABLED", 1);
    mock.getContact = async request => {
      await admin.query("UPDATE ad_status SET state='ads_paused_review' WHERE customer_id=(SELECT customer_id FROM runtime_customer WHERE target=$1)", [target]);
      return getContact(request);
    };
    assert.equal(await runtime.guard.dispatch(ad("paused-during-lookup")), "advertising_consent");
    await admin.query("UPDATE ad_status SET state='active' WHERE customer_id=(SELECT customer_id FROM runtime_customer WHERE target=$1)", [target]);
    mock.getContact = async request => {
      await admin.query(`INSERT INTO consents(customer_id,purpose,displayed_text,policy_version,evidence,withdrawn,previous_id)
        SELECT customer_id,purpose,displayed_text,policy_version,'{"fixture":true}',true,id
        FROM consents WHERE customer_id=(SELECT customer_id FROM runtime_customer WHERE target=$1)
        AND purpose='ads' ORDER BY occurred_at DESC,id DESC LIMIT 1`, [target]);
      return getContact(request);
    };
    assert.equal(await runtime.guard.dispatch(ad("consent-during-lookup")), "consent");
    assert.equal(mock.sent.size, 1);
    store.consent(target, timestamp + 86_400_000, true, true, true, true, {
      displayedText: "Dữ liệu giả lập", policyVersion: "fixture-2", evidence: { fixture: true },
    });
    mock.getContact = getContact;
    mock.fail = "unknown_delivery";
    const proposal = ad("uncertain");
    assert.equal(await runtime.guard.dispatch(proposal), "unknown");
    assert.equal(db.prepare("SELECT state FROM send_log WHERE id=?").get(store.hash(proposal.id)).state, "unknown_delivery");
    assert.equal(await runtime.guard.dispatch(proposal), "duplicate");
    assert.equal(mock.sent.size, 2);
  });
