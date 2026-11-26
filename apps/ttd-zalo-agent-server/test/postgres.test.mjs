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
