import assert from "node:assert/strict";
import { randomBytes, randomUUID } from "node:crypto";
import { once } from "node:events";
import { mkdtempSync, rmSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { Pool } from "pg";
import WebSocket from "ws";
import { attachNickAudit } from "../dist/ttd-zalo-agent-server/src/adapters/nick-audit.js";
import { PostgresRuntimeDatabase } from "../dist/ttd-zalo-agent-server/src/data/runtime-database.js";
import { Journal } from "../../ttd-zalo-nick-worker/src/journal.js";
import { Worker } from "../../ttd-zalo-nick-worker/src/worker.js";

test("nick outbox replays after server outage into Postgres exactly once", {
  skip: process.env.RUN_POSTGRES_TESTS !== "1", timeout: 15_000,
}, async t => {
  const admin = new Pool();
  const db = new PostgresRuntimeDatabase({ user: "data_runtime", password: process.env.DATA_RUNTIME_PASSWORD });
  const dir = mkdtempSync(join(tmpdir(), "nick-audit-"));
  const credential = randomBytes(32).toString("hex");
  const job = randomUUID();
  const nonce = randomUUID();
  const path = join(dir, "outbox");
  let journal = new Journal(path);
  let socket;
  let endpoint;
  t.after(async () => {
    socket?.terminate();
    await endpoint?.close();
    db.close();
    journal.close();
    await admin.query("DELETE FROM notices WHERE key=$1", [`nick:committed_before_revoke:${job}`]);
    await admin.query("DELETE FROM send_log WHERE id=$1", [job]);
    await admin.end();
    rmSync(dir, { recursive: true, force: true });
  });

  async function serve(port = 0) {
    const server = createServer();
    const detach = attachNickAudit(server, db, credential);
    server.listen(port, "127.0.0.1");
    await once(server, "listening");
    return { port: server.address().port, close: () => new Promise(resolve => {
      detach();
      server.close(resolve);
    }) };
  }
  async function connect(port) {
    const client = new WebSocket(`ws://127.0.0.1:${port}/internal/nick-worker`, {
      headers: { Authorization: `Bearer ${credential}` },
    });
    await once(client, "open");
    return client;
  }

  await admin.query("INSERT INTO send_log(id,agent,kind,state) VALUES($1,'nick-worker','reply','reserved')", [job]);
  endpoint = await serve();
  const port = endpoint.port;
  socket = await connect(port);
  const first = new Worker({ invalidatePermit: async revoked => revoked?.nonce === nonce ? { id: job, nonce } : undefined }, journal);
  await first.attach(socket).then(async () => {
    // Initial attachment cannot have a committed permit. Simulate loss after admission instead.
    assert.equal(journal.audits.size, 0);
  });
  const closed = once(socket, "close");
  await endpoint.close();
  endpoint = undefined;
  await closed;
  await first.detach(socket);
  await first.invalidatePermit({ id: job, nonce });
  assert.equal(journal.audits.size, 1);
  assert.equal((await admin.query("SELECT state FROM send_log WHERE id=$1", [job])).rows[0].state, "reserved");
  journal.close();
  journal = new Journal(path);

  endpoint = await serve(port);
  socket = await connect(port);
  const worker = new Worker({ invalidatePermit: async () => {}, snapshot: async () => ({}), scan: async () => ({}) }, journal);
  await worker.attach(socket);
  const event = journal.audits.get(job);
  const ack = new Promise(resolve => socket.on("message", raw => {
    const message = JSON.parse(raw.toString());
    if (message.type === "audit_ack") resolve(message);
  }));
  await worker.tick(socket);
  const received = await ack;
  assert.equal(received.idempotencyKey, event.idempotencyKey);
  assert.equal((await admin.query("SELECT state FROM send_log WHERE id=$1", [job])).rows[0].state, "committed_before_revoke");
  const duplicateAck = new Promise(resolve => socket.on("message", raw => {
    const message = JSON.parse(raw.toString());
    if (message.type === "audit_ack") resolve(message);
  }));
  socket.send(JSON.stringify(event));
  await duplicateAck;
  assert.equal((await admin.query("SELECT count(*)::int AS count FROM notices WHERE key=$1", [event.idempotencyKey])).rows[0].count, 1);
  await worker.receive(socket, received);
  assert.equal(journal.audits.size, 0);
});
