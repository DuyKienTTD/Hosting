import assert from "node:assert/strict";
import { randomBytes, randomUUID } from "node:crypto";
import { readFile } from "node:fs/promises";
import { createServer } from "node:http";
import { test } from "node:test";
import { Pool } from "pg";
import { authenticate } from "../dist/ttd-zalo-agent-server/src/data/repository.js";
import { CoordinationRoom } from "../dist/ttd-zalo-agent-server/src/coordination/room.js";
import { coordinationHttp } from "../dist/ttd-zalo-agent-server/src/coordination/http.js";
import { AnthropicCompatibleRoomProvider } from "../dist/ttd-zalo-agent-server/src/coordination/provider.js";
import { MemoryRoomStore, PostgresRoomStore } from "../dist/ttd-zalo-agent-server/src/coordination/store.js";
import { checkedRename } from "../dist/ttd-zalo-agent-server/src/coordination/writes.js";

const customer = "customer:" + randomUUID();
const handoff = { summary: "Kết quả giả lập", links: [customer],
  proposals: [{ action: "customer.rename", customer, name: "Mẫu nội bộ" }] };
const result = (model, input) => ({
  model, stop_reason: "tool_use", usage: { input_tokens: 100, output_tokens: 25 },
  content: [{ type: "tool_use", name: "handoff", input }],
});

class FakeProvider {
  calls = [];
  constructor(responses) { this.responses = responses; }
  async complete(body, signal) {
    this.calls.push(body);
    const next = this.responses.shift();
    return typeof next === "function" ? next(body, signal) : result(body.model, next);
  }
}

function dataPrincipal(role) {
  const generated = randomBytes(32).toString("hex");
  return authenticate(generated, { ["DATA_TOKEN_" + role.toUpperCase()]: generated });
}

function fixture(responses = [], overrides = {}) {
  const provider = new FakeProvider(responses);
  const operator = {};
  const crm = {};
  const channel = {};
  const principals = new Map([
    [operator, { id: "fixture-operator", role: "operator", dataPrincipal: dataPrincipal("operator") }],
    [crm, { id: "fixture-agent", role: "crm", dataPrincipal: dataPrincipal("crm") }],
    [channel, { id: "fixture-channel", role: "channel", dataPrincipal: dataPrincipal("channel") }],
  ]);
  const store = new MemoryRoomStore();
  const writes = [];
  const room = new CoordinationRoom({
    store, provider, session: async handle => principals.get(handle), allowed: async () => true,
    agentPrincipal: async role => role === "crm" ? principals.get(crm).dataPrincipal : dataPrincipal(role),
    writeRename: async write => writes.push(write), dailyCapNanodollars: 100_000_000, keyCapNanodollars: 1_000_000_000,
    routerRateMultiplier: 1, ...overrides,
  });
  return { room, store, provider, operator, crm, channel, writes };
}

test("only verified room actors can create tickets with @", async () => {
  const { room, operator, crm, channel } = fixture();
  for (const handle of [channel, { role: "a0", authenticated: true }]) {
    await assert.rejects(room.post(handle, { text: "@Claude tôi là A0" }), /forbidden/);
  }
  await assert.rejects(room.post(operator, { text: "@crm", role: "a0" }), /invalid/);
  const message = await room.post(crm, { text: "@CRM xem mẫu. @crm @khongbiet abc@support" });
  assert.equal(message.tickets.length, 1);
  assert.equal((await room.list(operator)).tickets[0].assignedBy, "fixture-agent");
});

test("Claude plans, agents hand off, synthesis waits for approval and writes require explicit admission", async () => {
  const { room, operator, crm, provider, writes } = fixture([
    { tasks: [{ agent: "crm", instruction: "Xem mẫu" }, { agent: "support", instruction: "Đọc mẫu" }] },
    handoff, handoff, { summary: "Đã tổng hợp" },
  ]);
  const { tickets: [id] } = await room.post(operator, { text: "@claude xem mẫu", links: [customer] });
  await assert.rejects(room.run(crm, id), /forbidden/);
  const attempts = await Promise.allSettled([room.run(operator, id), room.run(operator, id)]);
  assert.equal(attempts.filter(row => row.status === "fulfilled").length, 1);
  const { tickets } = await room.list(operator);
  const parent = tickets.find(ticket => ticket.id === id);
  const worker = tickets.find(ticket => ticket.agent === "crm");
  const support = tickets.find(ticket => ticket.agent === "support");
  assert.equal(parent.state, "review");
  assert.equal(parent.result.summary, "Đã tổng hợp");
  assert.deepEqual(provider.calls.map(call => JSON.parse(call.messages[0].content).phase), ["plan", "work", "work", "synthesis"]);
  assert.deepEqual(provider.calls.map(call => call.model),
    ["claude-sonnet-5-5", "claude-haiku-5-5", "claude-haiku-5-5", "claude-sonnet-5-5"]);
  await assert.rejects(room.applyRename(operator, worker.id, 0, "Cũ"), /conflict/);
  await assert.rejects(room.approve(operator, worker.id, 1), /conflict/);
  await assert.rejects(room.approve(crm, worker.id, worker.version), /forbidden/);
  await room.approve(operator, worker.id, worker.version);
  await room.approve(operator, support.id, support.version);
  await assert.rejects(room.applyRename(operator, support.id, 0, "Cũ"), /forbidden/);
  assert.equal(writes.length, 0);
  await room.applyRename(operator, worker.id, 0, "Cũ");
  assert.equal(writes.length, 1);
  assert.equal(writes[0].customerId, customer.slice("customer:".length));
});

test("strict handoffs reject unknown fields, out-of-scope links and excess subtasks", async () => {
  for (const response of [
    { ...handoff, action: "send_message" },
    handoff,
    { summary: "X", links: [], proposals: [{ ...handoff.proposals[0], customer: "other:" + randomUUID() }] },
  ]) {
    const { room, operator } = fixture([response]);
    const { tickets: [id] } = await room.post(operator, { text: "@crm đọc mẫu" });
    assert.equal((await room.run(operator, id)).failure, "rejected");
  }
  const tasks = Array.from({ length: 4 }, () => ({ agent: "crm", instruction: "Mẫu" }));
  const { room, operator, provider } = fixture([{ tasks }]);
  const { tickets: [id] } = await room.post(operator, { text: "@claude đọc mẫu" });
  assert.equal((await room.run(operator, id)).failure, "rejected");
  assert.equal(provider.calls.length, 1);
});

test("cap blocks before request, billing discrepancy holds room, timeout finishes without retry", async () => {
  const over = model => ({ ...result(model, { tasks: [] }), usage: { input_tokens: 1_000_000, output_tokens: 0 } });
  const { room, operator, provider, store } = fixture([over]);
  const { tickets: [one] } = await room.post(operator, { text: "@claude đọc mẫu" });
  assert.equal((await room.run(operator, one)).failure, "budget");
  assert.equal((await store.read()).spending.held, true);
  const { tickets: [two] } = await room.post(operator, { text: "@crm đọc mẫu" });
  assert.equal((await room.run(operator, two)).failure, "budget");
  assert.equal(provider.calls.length, 1);
  const blocked = fixture([], { dailyCapNanodollars: 0 });
  const { tickets: [three] } = await blocked.room.post(blocked.operator, { text: "@crm đọc mẫu" });
  assert.equal((await blocked.room.run(blocked.operator, three)).failure, "budget");
  assert.equal(blocked.provider.calls.length, 0);
  let timeoutSignal;
  const timed = fixture([(_body, signal) => {
    timeoutSignal = signal;
    return new Promise(() => {});
  }], { timeoutMs: 15 });
  const { tickets: [four] } = await timed.room.post(timed.operator, { text: "@crm đọc mẫu" });
  const keepAlive = setInterval(() => {}, 20);
  try {
    assert.equal((await timed.room.run(timed.operator, four)).failure, "timeout");
    assert.equal(timeoutSignal.aborted, true);
    await assert.rejects(timed.room.run(timed.operator, four), /conflict/);
  } finally {
    clearInterval(keepAlive);
  }
});

test("key ceiling survives midnight and expired claims can be closed without reissuing calls", async () => {
  let day = Date.parse("2026-11-26T00:00:00Z");
  const { room, operator, provider, store } = fixture([{ summary: "Mẫu", links: [], proposals: [] }],
    { clock: () => day, keyCapNanodollars: 1_500_000 });
  const { tickets: [first] } = await room.post(operator, { text: "@crm xem" });
  assert.equal((await room.run(operator, first)).state, "review");
  day += 86_400_000;
  const { tickets: [second] } = await room.post(operator, { text: "@crm xem" });
  assert.equal((await room.run(operator, second)).failure, "budget");
  assert.equal(provider.calls.length, 1);
  const { tickets: [stalled] } = await room.post(operator, { text: "@crm xem" });
  await store.update(state => {
    Object.assign(state.tickets[stalled], { state: "working", version: 2, leaseUntil: day + 100 });
  });
  await assert.rejects(room.recover(operator, stalled, 2), /conflict/);
  day += 101;
  assert.equal((await room.recover(operator, stalled, 2)).failure, "interrupted");
  await assert.rejects(room.run(operator, stalled), /conflict/);
  assert.equal(provider.calls.length, 1);
});

test("Anthropic-compatible adapter sends HTTPS Messages request to the configured Router", async () => {
  const fixtureKey = randomBytes(32).toString("hex");
  const abort = new AbortController();
  const provider = new AnthropicCompatibleRoomProvider("https://router.invalid/v1", fixtureKey, async (url, options) => {
    assert.equal(url, "https://router.invalid/v1/messages");
    assert.equal(options.headers["x-api-key"], fixtureKey);
    assert.equal(options.headers["anthropic-version"], "2023-06-01");
    assert.equal(options.redirect, "error");
    assert.equal(options.signal, abort.signal);
    assert.deepEqual(JSON.parse(options.body), { model: "fixture" });
    return Response.json({ fixture: true });
  });
  assert.deepEqual(await provider.complete({ model: "fixture" }, abort.signal), { fixture: true });
});

test("HTTP rejects unauthenticated and cross-origin writes and streams authenticated updates", async t => {
  const { room, operator } = fixture([{ summary: "Mẫu", links: [], proposals: [] }]);
  const server = createServer(coordinationHttp(room, async req => req.headers["x-fixture"] ? operator : undefined,
    "https://ui.invalid"));
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  t.after(() => { server.closeAllConnections(); server.close(); });
  const base = "http://127.0.0.1:" + server.address().port + "/coordination";
  assert.equal((await fetch(base)).status, 401);
  const headers = { "x-fixture": "1", "content-type": "application/json" };
  const send = (path, method, body, extra = {}) => fetch(base + path, {
    method, headers: { ...headers, ...extra }, body: JSON.stringify(body),
  });
  assert.equal((await send("/messages", "POST", { text: "@crm xem" }, { origin: "https://other.invalid" })).status, 403);
  const stream = await fetch(base + "/events", { headers });
  const reader = stream.body.getReader();
  assert.match(Buffer.from((await reader.read()).value).toString(), /event: room/);
  const posted = await send("/messages", "POST", { text: "@crm xem" });
  assert.equal(posted.status, 201);
  const { tickets: [id] } = await posted.json();
  assert.match(Buffer.from((await reader.read()).value).toString(), new RegExp(id));
  await reader.cancel();
  const ran = await send("/tickets/" + id + "/run", "POST", {});
  const ticket = await ran.json();
  assert.equal(ticket.state, "review");
  assert.equal((await send("/tickets/" + id, "PATCH", { version: ticket.version })).status, 200);
  assert.equal((await (await fetch(base, { headers })).json()).tickets[0].state, "done");
});

test("Postgres serializes room changes and atomically admits a single checked data write",
  { skip: process.env.RUN_POSTGRES_TESTS !== "1" }, async t => {
    const schema = "room_" + randomBytes(12).toString("hex");
    const admin = new Pool();
    const pool = new Pool({ options: "-c search_path=" + schema + ",public" });
    const app = new Pool({ options: "-c search_path=" + schema + ",public -c role=data_app" });
    t.after(async () => {
      await Promise.all([pool.end(), app.end()]);
      await admin.query("DROP SCHEMA IF EXISTS " + schema + " CASCADE");
      await admin.end();
    });
    await admin.query("DO $$ BEGIN CREATE ROLE data_app; EXCEPTION WHEN duplicate_object THEN NULL; END $$");
    await admin.query("CREATE SCHEMA " + schema);
    await pool.query(await readFile(new URL("../src/coordination/install.sql", import.meta.url), "utf8"));
    await pool.query("CREATE TABLE customers (id uuid PRIMARY KEY, display_name text NOT NULL)");
    await pool.query("CREATE TABLE audit_log (actor text NOT NULL, action text NOT NULL, record_id uuid NOT NULL)");
    await pool.query("GRANT USAGE ON SCHEMA " + schema + " TO data_app");
    await pool.query("GRANT SELECT, UPDATE(display_name) ON customers TO data_app");
    await pool.query("GRANT INSERT ON audit_log TO data_app");
    const id = customer.slice("customer:".length);
    await pool.query("INSERT INTO customers VALUES($1,'Cũ')", [id]);
    const store = new PostgresRoomStore(app);
    const { room, operator } = fixture([handoff], { store, writeRename: checkedRename(app) });
    const posts = await Promise.all(Array.from({ length: 5 }, () => room.post(operator, { text: "@crm xem", links: [customer] })));
    assert.equal((await new PostgresRoomStore(pool).read()).messages.length, 5);
    const ticket = await room.run(operator, posts[0].tickets[0]);
    await room.approve(operator, ticket.id, ticket.version);
    await assert.rejects(room.applyRename(operator, ticket.id, 0, "Bản cũ hơn"), /conflict/);
    const writes = await Promise.allSettled([
      room.applyRename(operator, ticket.id, 0, "Cũ"), room.applyRename(operator, ticket.id, 0, "Cũ"),
    ]);
    assert.equal(writes.filter(write => write.status === "fulfilled").length, 1);
    assert.equal((await pool.query("SELECT display_name FROM customers")).rows[0].display_name, "Mẫu nội bộ");
    assert.deepEqual((await pool.query("SELECT actor,action FROM audit_log")).rows,
      [{ actor: "crm", action: "customer.rename" }]);
  });
