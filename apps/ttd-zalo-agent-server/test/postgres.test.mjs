import assert from "node:assert/strict";
import { createHmac, randomBytes, randomUUID } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readdirSync, rmSync, utimesSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { Pool } from "pg";
import { authenticate, PostgresRepository } from "../dist/ttd-zalo-agent-server/src/data/repository.js";
import { cleanPendingPurges, requestDeletion, runRetention } from "../dist/ttd-zalo-agent-server/src/data/deletion.js";

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
    const ledger = join(root, "receipts");
    const originalLedger = process.env.PURGE_RECEIPT_REMOTE;
    process.env.PURGE_RECEIPT_REMOTE = ledger;
    t.after(() => {
      if (originalLedger === undefined) delete process.env.PURGE_RECEIPT_REMOTE;
      else process.env.PURGE_RECEIPT_REMOTE = originalLedger;
    });
    const env = { ...config, RESTORE_SOURCE_DATABASE: config.PGDATABASE, BACKUP_REMOTE: root,
      PURGE_RECEIPT_REMOTE: ledger, AGE_IDENTITY_FILE: join(root, "restore-key") };
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
    await runRetention(worker, join(root, "unavailable"));
    await admin.query("UPDATE messages SET purge_after=now()-interval '1 second' WHERE id=$1", [record]);
    await admin.query("INSERT INTO legal_holds(message_id,reason) VALUES($1,'fixture')", [record]);
    await runRetention(worker, join(root, "unavailable"));
    await admin.query("UPDATE legal_holds SET released_at=now() WHERE message_id=$1", [record]);
    const attempt = randomUUID();
    const runtimeRole = new Pool({ user: "data_runtime", password: config.DATA_RUNTIME_PASSWORD });
    try {
      for (const role of [worker, app, runtimeRole, admin]) {
        await assert.rejects(role.query("SELECT authorize_purge($1,1,1)", [record]), /does not exist/);
        await assert.rejects(role.query("DELETE FROM messages WHERE id=$1", [record]),
          /permission denied|purge_receipt_required/);
        await assert.rejects(role.query("SELECT purge_message($1,1,1,$2,$3)", [record, attempt, "0".repeat(64)]),
          /permission denied|purge_receipt_required/);
      }
      for (const role of [worker, app, runtimeRole]) {
        await assert.rejects(role.query("SELECT * FROM purge_private.signing_key"), /permission denied/);
        await assert.rejects(role.query("SELECT purge_private.replay_tombstone($1,$2,$3,$4,1,1,$5)",
          [attempt, record, conversation, "0".repeat(64), "0".repeat(64)]), /permission denied/);
      }
      const session = await worker.connect();
      try {
        const decoyKey = randomBytes(32);
        await session.query("CREATE TEMP TABLE signing_key(slot boolean,secret bytea)");
        await session.query("INSERT INTO signing_key VALUES(true,$1)", [decoyKey]);
        const eventKey = (await admin.query("SELECT event_id FROM messages WHERE id=$1", [record])).rows[0].event_id;
        const decoySignature = createHmac("sha256", decoyKey)
          .update(["z4-tombstone-v2", "pending", attempt, record, conversation, eventKey, 1, 1].join("|")).digest("hex");
        await assert.rejects(session.query("SELECT purge_message($1,1,1,$2,$3)", [record, attempt, decoySignature]),
          /purge_receipt_required/);
      } finally {
        await session.query("DROP TABLE IF EXISTS pg_temp.signing_key");
        session.release();
      }
      assert.equal((await worker.query("SELECT purge_message($1,1,1,$2,NULL) AS eligible", [record, attempt])).rows[0].eligible, true);
      assert.equal((await admin.query("SELECT id FROM messages WHERE id=$1", [record])).rowCount, 1);
      await assert.rejects(admin.query("TRUNCATE messages CASCADE"), /purge_receipt_required/);
    } finally { await runtimeRole.end(); }

    await assert.rejects(runRetention(worker, join(root, "unavailable")), /tombstone_archive_unavailable/);
    assert.equal((await admin.query("SELECT id FROM messages WHERE id=$1", [record])).rowCount, 1);
    assert.deepEqual(readdirSync(join(root, "tombstones")), ["_format"]);
    const beforeArchive = restore + "_denied";
    try {
      execFileSync("sh", ["ops/restore.sh", dump, beforeArchive], { env });
      const restored = new Pool({ database: beforeArchive });
      try {
        assert.equal((await restored.query("SELECT id FROM messages WHERE id=$1", [record])).rowCount, 1);
      } finally { await restored.end(); }
    } finally { await admin.query(`DROP DATABASE IF EXISTS ${beforeArchive}`); }

    await admin.query(`CREATE FUNCTION fixture_after_pending() RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN RAISE EXCEPTION 'fixture_after_pending'; END $$;
      CREATE TRIGGER fixture_after_pending BEFORE INSERT ON restore_tombstones
        FOR EACH ROW EXECUTE FUNCTION fixture_after_pending()`);
    try {
      await assert.rejects(runRetention(worker, root), /fixture_after_pending/);
    } finally {
      await admin.query("DROP TRIGGER fixture_after_pending ON restore_tombstones; DROP FUNCTION fixture_after_pending()");
    }
    const pending = join(root, "tombstones", "pending");
    assert.equal(readdirSync(pending).length, 1);
    assert.equal((await admin.query("SELECT count(*)::int AS count FROM purge_private.commits")).rows[0].count, 0);

    await admin.query(`CREATE FUNCTION fixture_purge_failure() RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN RAISE EXCEPTION 'fixture_purge_failed'; END $$;
      CREATE TRIGGER fixture_purge_failure AFTER DELETE ON messages
        FOR EACH ROW EXECUTE FUNCTION fixture_purge_failure()`);
    try {
      await assert.rejects(runRetention(worker, root), /fixture_purge_failed/);
    } finally {
      await admin.query("DROP TRIGGER fixture_purge_failure ON messages; DROP FUNCTION fixture_purge_failure()");
    }
    assert.equal((await admin.query("SELECT id FROM messages WHERE id=$1", [record])).rowCount, 1);
    assert.equal((await admin.query("SELECT record_id FROM restore_tombstones WHERE record_id=$1", [record])).rowCount, 0);
    assert.equal((await admin.query("SELECT record_id FROM deletion_log WHERE record_id=$1 AND action='purge'", [record])).rowCount, 0);
    assert.equal(readdirSync(pending).length, 2);
    assert.equal((await admin.query("SELECT count(*)::int AS count FROM purge_private.commits")).rows[0].count, 0);
    await admin.query("INSERT INTO legal_holds(message_id,reason) VALUES($1,'fixture rollback hold')", [record]);
    await new Promise(resolve => setTimeout(resolve, 1100));
    execFileSync("sh", ["ops/backup.sh"], { env });
    const heldDump = readdirSync(join(root, "dumps")).sort().at(-1);
    assert.notEqual(heldDump, dump);
    const probeRestore = async (backup, suffix, expectedAudit, remaining = 1, overrides = {}, check) => {
      const database = restore + suffix;
      try {
        execFileSync("sh", ["ops/restore.sh", backup, database], { env: { ...env, ...overrides } });
        const snapshot = new Pool({ database });
        try {
          assert.equal((await snapshot.query("SELECT id FROM messages WHERE id=$1", [record])).rowCount, remaining);
          if (expectedAudit) assert.ok((await snapshot.query("SELECT 1 FROM audit_log WHERE action=$1 AND record_id=$2",
            [expectedAudit, record])).rowCount);
          if (check) await check(snapshot, database);
        } finally { await snapshot.end(); }
      } finally { await admin.query(`DROP DATABASE IF EXISTS ${database}`); }
    };
    await probeRestore(heldDump, "_rollback", "pending_rollback_verified");
    await admin.query("UPDATE legal_holds SET released_at=now() WHERE message_id=$1", [record]);

    // A filesystem obstruction prevents publication after the database commits.
    const confirmed = join(root, "tombstones", "confirmed");
    writeFileSync(confirmed, "fixture");
    await admin.query(`CREATE FUNCTION fixture_check_commit() RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        IF EXISTS (SELECT 1 FROM committed_purges() AS receipt WHERE receipt.purge_id=NEW.purge_id)
          THEN RAISE EXCEPTION 'fixture_confirmation_before_commit'; END IF;
        RETURN NEW;
      END $$;
      CREATE TRIGGER fixture_check_commit AFTER INSERT ON purge_private.commits
        FOR EACH ROW EXECUTE FUNCTION fixture_check_commit()`);
    try {
      await assert.rejects(runRetention(worker, root),
        error => !String(error).includes("fixture_confirmation_before_commit"));
    } finally {
      await admin.query("DROP TRIGGER fixture_check_commit ON purge_private.commits; DROP FUNCTION fixture_check_commit()");
    }
    assert.equal((await admin.query("SELECT id FROM messages WHERE id=$1", [record])).rowCount, 0);
    assert.equal((await worker.query("SELECT * FROM committed_purges()")).rowCount, 1);
    rmSync(confirmed);
    await probeRestore(dump, "_source", null, 0, { PURGE_RECEIPT_REMOTE: join(root, "unavailable") });
    const ledgerCopy = join(root, "receipts-offsite");
    execFileSync("sh", ["ops/backup-purge-receipts.sh"], { env: { ...env, PURGE_RECEIPT_BACKUP_REMOTE: ledgerCopy } });
    await probeRestore(dump, "_ledger", null, 0, {
      RESTORE_SOURCE_DATABASE: "missing_fixture_source", PURGE_RECEIPT_REMOTE: ledgerCopy,
    });
    await probeRestore(dump, "_unknown", "purge_unverified", 1, {
      RESTORE_SOURCE_DATABASE: "missing_fixture_source", PURGE_RECEIPT_REMOTE: join(root, "unavailable"),
    }, async (snapshot, database) => {
      assert.equal((await snapshot.query("SELECT id FROM visible_messages WHERE id=$1", [record])).rowCount, 0);
      const serving = new Pool({ database, user: "data_runtime", password: config.DATA_RUNTIME_PASSWORD });
      try {
        await assert.rejects(serving.query("SELECT 1"), /permission denied/);
      } finally { await serving.end(); }
      await assert.rejects(snapshot.query("SELECT purge_private.promote_restore()"), /restore_promotion_blocked/);
      const unknown = (await snapshot.query("SELECT purge_id FROM purge_private.restore_unknown")).rows;
      for (const item of unknown) await snapshot.query("SELECT purge_private.resolve_restore($1,'restore')", [item.purge_id]);
      assert.equal((await snapshot.query("SELECT id FROM visible_messages WHERE id=$1", [record])).rowCount, 1);
      await snapshot.query("SELECT purge_private.promote_restore()");
      assert.ok((await snapshot.query("SELECT 1 FROM audit_log WHERE action='restore_owner_restore'")).rowCount);
    });
    await admin.query("INSERT INTO legal_holds(message_id,reason) VALUES($1,'fixture post-purge hold')", [record]);
    await probeRestore(dump, "_newer_hold", "purge_blocked", 1, {}, async snapshot => {
      assert.ok((await snapshot.query("SELECT 1 FROM legal_holds WHERE message_id=$1 AND released_at IS NULL",
        [record])).rowCount);
    });
    await admin.query("UPDATE legal_holds SET released_at=now() WHERE message_id=$1", [record]);
    assert.equal(readdirSync(pending).length, 3);
    const expired = new Date(Date.now() - 48 * 60 * 60 * 1000);
    for (const name of readdirSync(pending)) utimesSync(join(pending, name), expired, expired);
    await cleanPendingPurges(worker, root);
    assert.equal(readdirSync(pending).length, 1, "unpublished committed pending survives cleanup");
    await admin.query(`CREATE FUNCTION fixture_ack_failure() RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN RAISE EXCEPTION 'fixture_ack_failed'; END $$;
      CREATE TRIGGER fixture_ack_failure BEFORE UPDATE ON purge_private.commits
        FOR EACH ROW EXECUTE FUNCTION fixture_ack_failure()`);
    try {
      await assert.rejects(runRetention(worker, root), /fixture_ack_failed/);
      assert.equal(readdirSync(confirmed).length, 1);
      assert.equal((await worker.query("SELECT * FROM committed_purges()")).rowCount, 1);
    } finally {
      await admin.query("DROP TRIGGER fixture_ack_failure ON purge_private.commits; DROP FUNCTION fixture_ack_failure()");
    }
    await runRetention(worker, root);
    assert.equal(readdirSync(confirmed).length, 1);
    assert.equal((await worker.query("SELECT * FROM committed_purges()")).rowCount, 0);
    await cleanPendingPurges(worker, root);
    assert.equal(readdirSync(pending).length, 0);
    await probeRestore(heldDump, "_held", "purge_blocked");
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
