import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { createHmac } from "node:crypto";

import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { chromium } from "playwright";
import { Store } from "../dist/ttd-zalo-agent-server/src/store.js";
import { defaults } from "../dist/ttd-zalo-agent-server/src/config.js";
import { ChannelJournal } from "../dist/ttd-zalo-agent-server/src/adapters/common.js";
import { SubizAdapter } from "../dist/ttd-zalo-agent-server/src/adapters/subiz.js";
import { ZaloBotAdapter } from "../dist/ttd-zalo-agent-server/src/adapters/bot.js";
import { SubizUiAdapter } from "../dist/ttd-zalo-agent-server/src/adapters/ui.js";
import { CapabilityRouter, RuntimeChannel, command } from "../dist/ttd-zalo-agent-server/src/adapters/router.js";
import { webhookHandler } from "../dist/ttd-zalo-agent-server/src/adapters/setup.js";
import { smoke } from "../dist/ttd-zalo-agent-server/src/adapters/smoke.js";

function setup(t, path = ":memory:") {
  let now = 1795651200000;
  const clock = () => now;
  const store = new Store(path, "synthetic-index-key");
  t.after(() => store.db.close());
  const journal = new ChannelJournal(store, clock);
  return { store, journal, clock, advance: delta => { now += delta; } };
}
async function serve(t, handler) {
  const server = createServer((req, res) => { void handler(req, res).catch(() => res.writeHead(500).end()); });
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  t.after(() => { server.closeAllConnections(); server.close(); });
  return "http://127.0.0.1:" + server.address().port;
}
const adsTestConfig = { ...defaults, advertising: { ...defaults.advertising, enabled: true } };

const account = "synthetic-account";
const agent = "synthetic-agent";
const profile = "synthetic-profile";
const user = "synthetic-user";
const cid = "synthetic-cid";
const contact = "synthetic-contact";
const channel = "zalo";
const source = "synthetic-personal-source";
const commandFor = (key, operation, payload) => command(account, key, operation, payload);
const nonce = "TTD-SMOKE-fixture_nonce_42";
const writeEnv = (t, name, value) => {
  const previous = process.env[name];
  process.env[name] = value;
  t.after(() => { if (previous === undefined) delete process.env[name]; else process.env[name] = previous; });
};

function eventData(at, text = nonce) {
  return { id: "event-inbound", account_id: account, created: at, type: "message_sent",
    by: { type: "user", id: user }, data: { message: { conversation_id: cid, format: "plaintext", text } } };
}

async function subizFixture(t, f) {
  writeEnv(t, "SUBIZ_API_TOKEN", "synthetic-pat");
  writeEnv(t, "SUBIZ_WEBHOOK_SECRET", "synthetic-hook");
  const events = [eventData(f.clock())];
  const state = { writes: 0, reads: 0, mode: "normal" };
  const url = await serve(t, async (req, res) => {
    assert.equal(req.headers.authorization, "Bearer synthetic-pat");
    if (req.method === "GET") state.reads++;
    const json = payload => res.setHeader("Content-Type", "application/json").end(JSON.stringify(payload));
    if (req.url === "/4.1/me" && req.method === "GET") {
      if (state.mode === "auth") { res.statusCode = 400; json({ code: "access_deny,internal" }); return; }
      json({ account_id: account, id: agent }); return;
    }
    if (req.url === "/4.0/conversations/" + cid && req.method === "GET") {
      json({ id: cid, account_id: account, touchpoint: { channel, source: state.mode === "wrong-source" ? "other" : source, id: profile },
        members: [{ type: "user", id: user, membership: "active" }] }); return;
    }
    if (req.url === "/4.0/conversations/" + cid + "/messages?limit=100" && req.method === "GET") { json(events); return; }
    assert.equal(req.url, "/4.1/conversations/" + cid + "/messages");
    assert.equal(req.method, "POST");
    const body = JSON.parse(await Array.fromAsync(req).then(parts => Buffer.concat(parts).toString("utf8")));
    assert.deepEqual(body, { type: "message_sent", data: { message: { text: body.data.message.text, format: "plaintext" } } });
    state.writes++;
    if (state.mode === "rate") { res.writeHead(429, { "Retry-After": "7" }).end(); return; }
    if (state.mode === "lost") { req.socket.destroy(); return; }
    const item = { ...eventData(f.clock(), body.data.message.text), id: "provider-receipt-" + state.writes, by: { type: "agent", id: agent } };
    events.push(item);
    json(item);
  });
  const config = { accountId: account, agentId: agent, channel, source,
    direct: [{ contactId: contact, conversationId: cid, userId: user, profileId: profile, friendUntil: f.clock() + 172800000 }] };
  const providerFetch = (remote, opts) => {
    assert.equal(new URL(remote).origin, "https://api.subiz.com.vn");
    return fetch(url + new URL(remote).pathname + new URL(remote).search, opts);
  };
  return { config, adapter: new SubizAdapter(config, f.journal, providerFetch, f.clock), providerFetch, state, events };
}

function signature(raw) { return "sha256=" + createHmac("sha256", "synthetic-hook").update(raw).digest("hex"); }

test("Subiz signed webhook raw bytes, batch filtering, cursor, replay and encrypted persistence", async t => {
  const f = setup(t);
  const { adapter } = await subizFixture(t, f);
  const hook = webhookHandler(adapter);
  const url = await serve(t, async (req, res) => { if (!await hook(req, res)) res.writeHead(404).end(); });
  const event = eventData(f.clock());
  const raw = Buffer.from(JSON.stringify({ events: [event,
    { ...event, id: "echo", by: { type: "agent", id: agent } },
    { ...event, id: "wrong-account", account_id: "other" },
    { ...event, id: "stale", created: f.clock() - 90_000_000 },
    { ...event, id: "internal", data: { message: { ...event.data.message, is_internal: true } } },
    { ...event, id: "wrong-source", touchpoint: { channel, source: "other", id: profile } }] }, null, 2));
  const send = (body, signed) => fetch(url + "/webhooks/subiz", { method: "POST", body, headers: {
    "Content-Type": "application/json", "X-Hub-Signature-256": signed, "X-Subiz-Delivery": "fixture" } });
  assert.equal((await send(Buffer.concat([raw, Buffer.from(" ")]), signature(raw))).status, 403);
  assert.equal((await send(raw, signature(raw) + "," + "0".repeat(64))).status, 204);
  assert.equal((await send(raw, signature(raw))).status, 204);
  const r = await adapter.receiveMessage(commandFor("read", "receiveMessage", {}));
  assert.deepEqual(r.value.items.map(e => [e.payload.senderId, e.payload.thread.conversationId]), [[contact, cid]]);
  assert.equal((await adapter.receiveMessage(commandFor("read", "receiveMessage", { cursor: r.value.nextCursor }))).value.items.length, 0);
  assert.doesNotMatch(JSON.stringify(f.store.db.prepare("SELECT * FROM adapter_inbox").all()), new RegExp(nonce));
  f.store.deleteCustomer(contact);
  assert.equal((await send(raw, signature(raw))).status, 204);
  assert.equal((await adapter.receiveMessage(commandFor("read", "receiveMessage", {}))).value.items.length, 0);
});

test("Subiz exact conversation POST, auth and source, accepted distinction, durable dedup and timeout", async t => {
  const directory = await mkdtemp(join(tmpdir(), "zalo-adapter-"));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const path = join(directory, "runtime.sqlite");
  const f = setup(t, path);
  const { adapter, config, providerFetch, state } = await subizFixture(t, f);
  const write = (key, text = "fixture reply") => commandFor(key, "sendMessage", { conversationId: cid, text });
  assert.equal((await adapter.authenticate()).ok, true);
  state.mode = "auth";
  assert.equal((await adapter.authenticate()).error.code, "auth");
  state.mode = "wrong-source";
  assert.equal((await adapter.getContact(commandFor("read", "getContact", { contactId: contact }))).error.code, "policy_denied");
  state.mode = "normal";
  assert.equal((await adapter.getContact(commandFor("read", "getContact", { contactId: contact }))).value.friendship, "accepted");
  const sent = await adapter.sendMessage(write("first"));
  assert.equal(sent.value.state, "accepted");
  assert.deepEqual(await adapter.sendMessage(write("first")), sent);
  assert.equal((await adapter.sendMessage(write("first", "changed"))).error.code, "invalid_input");
  state.mode = "lost";
  assert.equal((await adapter.sendMessage(write("unknown"))).error.code, "unknown_delivery");
  const reopened = new Store(path, "synthetic-index-key");
  t.after(() => reopened.db.close());
  const replay = new SubizAdapter(config, new ChannelJournal(reopened, f.clock), providerFetch, f.clock);
  assert.deepEqual(await replay.sendMessage(write("first")), sent);
  assert.equal((await replay.sendMessage(write("unknown"))).error.code, "unknown_delivery");
  assert.equal(state.writes, 2);
});

test("Subiz 429 honors Retry-After across write keys and never schedules a retry", async t => {
  const f = setup(t);
  const { adapter, state } = await subizFixture(t, f);
  const write = key => commandFor(key, "sendMessage", { conversationId: cid, text: "fixture reply" });
  await adapter.getContact(commandFor("route", "getContact", { contactId: contact }));
  state.mode = "rate";
  assert.deepEqual((await adapter.sendMessage(write("one"))).error, { code: "rate_limited", retryAfterSeconds: 7 });
  f.advance(6000);
  assert.deepEqual((await adapter.sendMessage(write("two"))).error, { code: "rate_limited", retryAfterSeconds: 1 });
  assert.equal(state.writes, 1);
  f.advance(1000);
  state.mode = "normal";
  assert.equal((await adapter.sendMessage(write("one"))).ok, true);
  assert.equal(state.writes, 2);
});

test("router routes one configured capability; no fallback on unknown delivery", async t => {
  const f = setup(t);
  const { adapter, state } = await subizFixture(t, f);
  const router = new CapabilityRouter({ sendMessage: "api" }, { api: { adapter, operations: ["sendMessage"] } });
  assert.throws(() => new CapabilityRouter({ sendMessage: "bot" }, { api: { adapter, operations: ["sendMessage"] } }));
  assert.equal((await router.run(commandFor("missing", "postToGroup", { groupId: cid, text: "fixture" }))).error.code, "not_supported");
  await adapter.getContact(commandFor("route", "getContact", { contactId: contact }));
  state.mode = "lost";
  const bridge = new RuntimeChannel(router, account, new Map([[contact, cid]]), []);
  assert.equal((await bridge.sendMessage({ key: "bad-thread", target: contact, thread: "other", text: "fixture" })).error, "policy_denied");
  assert.equal((await bridge.sendMessage({ key: "send", target: contact, thread: cid, text: "fixture" })).error, "unknown_delivery");
  assert.equal(state.writes, 1);
});

test("smoke rejects a wrong contact and sends once through Guard for matching signed nonce", async t => {
  const f = setup(t);
  const { adapter, config, state, events } = await subizFixture(t, f);
  const routes = { subiz: config, capabilities: { sendMessage: "api", getContact: "api" } };
  const bridge = new RuntimeChannel(new CapabilityRouter(routes.capabilities, { api: { adapter, operations: ["sendMessage", "getContact"] } }),
    account, new Map([[contact, cid]]), []);
  const active = { subiz: adapter, channel: bridge };
  f.store.stop("global", false);
  f.store.consent(f.store.hash(contact), f.clock() + 50000, false, true, true, false);
  const raw = Buffer.from(JSON.stringify({ events }));
  assert.equal(await adapter.webhook(raw, signature(raw)), 204);
  assert.equal((await smoke(f.store, defaults, routes, active, "another", nonce, f.clock)).status, "FAIL");
  for (let i = 0; i < 2; i++) assert.equal((await smoke(f.store, defaults, routes, active, contact, nonce, f.clock)).status, "PASS");
  assert.equal(state.writes, 1);
});

test("Zalo Bot requires group entitlement, authenticates webhook and posts only to allowlisted groups", async t => {
  const f = setup(t);
  writeEnv(t, "ZALO_BOT_TOKEN", "synthetic-bot");
  writeEnv(t, "ZALO_BOT_WEBHOOK_SECRET", "synthetic-bot-hook");
  let entitled = false;
  let writes = 0;
  const bot = new ZaloBotAdapter({ accountId: account, botId: "fixture-bot", groups: ["fixture-group"] }, f.journal,
    async (url, init) => {
      if (url.endsWith("/getMe")) return Response.json({ ok: true, result: { id: "fixture-bot", can_join_groups: entitled } });
      assert.deepEqual(JSON.parse(init.body), { chat_id: "fixture-group", text: "fixture" });
      writes++;
      return Response.json({ ok: true, result: { message_id: "bot-receipt" } });
    });
  const post = g => commandFor("write", "postToGroup", { groupId: g, text: "fixture" });
  assert.equal((await bot.authenticate()).error.code, "not_supported");
  entitled = true;
  assert.equal((await bot.authenticate()).ok, true);
  const raw = Buffer.from(JSON.stringify({ event_name: "message.text.received", message: { message_id: "fixture-event",
    message_type: "CHAT_TEXT", date: f.clock(), from: { id: "fixture-user", is_bot: false },
    chat: { chat_type: "GROUP", id: "fixture-group" }, text: "fixture" } }));
  assert.equal(bot.webhook(raw, "wrong"), 403);
  assert.equal(bot.webhook(raw, "synthetic-bot-hook"), 204);
  assert.equal(bot.webhook(raw, "synthetic-bot-hook"), 204);
  assert.equal((await bot.readGroupMessages(commandFor("read", "readGroupMessages", { groupId: "fixture-group" }))).value.items.length, 1);
  assert.equal((await bot.postToGroup(post("unlisted"))).error.code, "policy_denied");
  assert.equal((await bot.postToGroup(post("fixture-group"))).value.state, "accepted");
  assert.equal((await bot.moderateGroup(commandFor("mod", "moderateGroup", { action: "delete_message", groupId: "fixture-group", messageId: "id" }))).error.code, "not_supported");
  assert.equal(writes, 1);
});

test("Playwright fixture creates and posts, reads members, requests friendship, detects acceptance and stops on drift", async t => {
  const f = setup(t);
  const folder = await mkdtemp(join(tmpdir(), "zalo-ui-"));
  t.after(() => rm(folder, { recursive: true, force: true }));
  const url = await serve(t, async (_req, res) => {
    res.setHeader("Content-Type", "text/html").end(`<!doctype html><div id="workspace" data-key="synthetic-workspace">Fixture</div>
      <section class="root" data-key="createGroup"><span class="target" data-key="new">New</span>
        <input class="input"><input class="member" data-key="fixture-friend" type="checkbox">
        <button>Submit</button><p class="receipt">Pending</p></section>
      <section class="root" data-key="postToGroup"><span class="target" data-key="fixture-group">Group</span>
        <textarea class="input"></textarea><button>Submit</button><p class="receipt">Pending</p></section>
      <section class="root" data-key="listMembers"><span class="target" data-key="fixture-group">Group</span>
        <p class="row" data-key="fixture-friend">Member</p></section>
      <section class="root" data-key="sendFriendRequest"><span class="target" data-key="fixture-friend">Friend</span>
        <button>Submit</button><p class="receipt">Pending</p></section>
      <section class="root" data-key="onFriendAccepted"><p class="accepted" data-key="fixture-friend"
        data-evidence="fixture-evidence" data-at="${f.clock()}">Accepted</p></section>
      <script>window.clicks=0; for(const b of document.querySelectorAll("button"))b.onclick=()=>{
        window.clicks++; b.parentElement.querySelector(".receipt").dataset.receipt="fixture-receipt-"+window.clicks;
      };</script>`);
  });
  // Only the loopback HTML fixture uses the system browser with sandbox disabled.

  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_TEST_EXECUTABLE, headless: true });
  t.after(() => browser.close());
  const page = await browser.newPage();
  await page.goto(url);
  const screenshot = join(folder, "diagnostic.png");
  const uiConfig = { accountId: account, workspaceId: "synthetic-workspace", origin: url, groups: ["fixture-group"],
    contacts: ["fixture-friend"], groupNames: ["Fixture group"], selectors: {
      workspace: "#workspace", challenge: "#challenge", root: ".root", target: ".target", targetAttribute: "data-key",
      input: ".input", member: ".member", submit: "button", receipt: ".receipt", receiptAttribute: "data-receipt",
      memberRows: ".row", acceptanceRows: ".accepted", evidenceAttribute: "data-evidence", timestampAttribute: "data-at",
    } };
  const ui = new SubizUiAdapter(uiConfig, page, f.journal, screenshot);
  assert.equal((await ui.createGroup(commandFor("create", "createGroup", { name: "Fixture group", memberIds: ["fixture-friend"] }))).ok, true);
  const post = key => commandFor(key, "postToGroup", { groupId: "fixture-group", text: "fixture" });
  assert.equal((await ui.postToGroup(post("post"))).ok, true);
  assert.deepEqual((await ui.listMembers(account, "fixture-group")).value, ["fixture-friend"]);
  assert.equal((await ui.sendFriendRequest(commandFor("invite", "sendFriendRequest", { contactId: "fixture-friend" }))).ok, true);
  assert.equal((await ui.onFriendAccepted(commandFor("accepted", "onFriendAccepted", {}))).value.items[0].payload.evidenceId, "fixture-evidence");
  await page.locator('section[data-key=postToGroup] button').evaluate(el => el.remove());
  assert.equal((await ui.postToGroup(post("drift"))).error.code, "unknown_delivery");
  assert.equal((await ui.postToGroup(post("after-drift"))).error.code, "not_supported");
  const restarted = new SubizUiAdapter(uiConfig, page, f.journal);
  assert.equal((await restarted.postToGroup(post("after-restart"))).error.code, "not_supported");
  assert.equal(await page.evaluate(() => window.clicks), 3);
  assert.equal((await readFile(screenshot)).subarray(1, 4).toString(), "PNG");
});

test("signed Subiz opt-out during contact preflight prevents any provider send", async t => {
  const f = setup(t);
  const { adapter, state } = await subizFixture(t, f);
  const { Runtime } = await import("../dist/ttd-zalo-agent-server/src/runtime.js");
  const { FakeProvider } = await import("../dist/ttd-zalo-agent-server/src/provider.js");
  const router = new CapabilityRouter({ sendMessage: "api", getContact: "api" },
    { api: { adapter, operations: ["sendMessage", "getContact"] } });
  const bridge = new RuntimeChannel(router, account, new Map([[contact, cid]]), []);
  const runtime = new Runtime(f.store, bridge, new FakeProvider(), adsTestConfig, f.clock);
  const hook = webhookHandler(adapter, undefined, event => runtime.ingest(event));
  const url = await serve(t, async (req, res) => { if (!await hook(req, res)) res.writeHead(404).end(); });
  f.store.stop("global", false);
  const target = f.store.hash(contact);
  f.store.consent(target, f.clock() + 50000, false, true, true, true);
  const original = bridge.getContact.bind(bridge);
  bridge.getContact = async req => {
    const verified = await original(req);
    const raw = Buffer.from(JSON.stringify({ events: [eventData(f.clock(), "DỪNG NHẬN TIN")] }));
    const response = await fetch(url + "/webhooks/subiz", { method: "POST", body: raw,
      headers: { "Content-Type": "application/json", "X-Hub-Signature-256": signature(raw) } });
    assert.equal(response.status, 204);
    return verified;
  };
  const result = await runtime.guard.dispatch({ agent: "campaign", kind: "advertising", id: "fixture-offer",
    target: contact, text: "Ưu đãi fixture", revision: f.store.contact(target).revision, epoch: f.store.setting("epoch") });
  assert.equal(result, "consent");
  assert.equal(f.store.contact(target).opted_out, 1);
  assert.equal(state.writes, 0);
});

for (const reason of ["not_friend", "hours", "allowed"]) {
  test(`Subiz advertising preflight ${reason} counts GET and POST separately`, async t => {
    const f = setup(t);
    const at = Date.parse(reason === "hours" ? "2026-11-26T15:30:00Z" : "2026-11-26T03:00:00Z");
    f.advance(at - f.clock());
    const { adapter, config, state, providerFetch } = await subizFixture(t, f);
    if (reason === "not_friend") config.direct[0].friendUntil = f.clock() - 1;
    const sourceAdapter = reason === "not_friend" ? new SubizAdapter(config, f.journal, providerFetch, f.clock) : adapter;
    const router = new CapabilityRouter({ sendMessage: "api", getContact: "api" },
      { api: { adapter: sourceAdapter, operations: ["sendMessage", "getContact"] } });
    const bridge = new RuntimeChannel(router, account, new Map([[contact, cid]]), []);
    const { Guard } = await import("../dist/ttd-zalo-agent-server/src/guard.js");
    f.store.stop("global", false);
    const target = f.store.hash(contact);
    f.store.consent(target, f.clock() + 50000, false, true, true, true);
    const result = await new Guard(f.store, bridge, adsTestConfig, f.clock).dispatch({
      agent: "campaign", kind: "advertising", id: "preflight-offer", target: contact, thread: cid,
      text: "Ưu đãi fixture", revision: f.store.contact(target).revision, epoch: f.store.setting("epoch"),
    });
    assert.equal(result, reason === "allowed" ? "sent" : reason);
    assert.deepEqual([state.reads, state.writes], reason === "allowed" ? [1, 1] : [0, 0]);
  });
}

test("128-character idempotency key passes dispatch; 129 fails before any provider request", async t => {
  const f = setup(t);
  const { adapter, state } = await subizFixture(t, f);
  const router = new CapabilityRouter({ sendMessage: "api", getContact: "api" },
    { api: { adapter, operations: ["sendMessage", "getContact"] } });
  const bridge = new RuntimeChannel(router, account, new Map([[contact, cid]]), []);
  const send = key => bridge.sendMessage({ key, target: contact, thread: cid, text: "fixture reply" });
  const longKey = "x".repeat(129);
  assert.equal((await bridge.getContact({ key: longKey, target: contact })).error, "invalid_input");
  assert.equal((await send(longKey)).error, "invalid_input");
  assert.deepEqual([state.reads, state.writes], [0, 0]);
  const key = "x".repeat(128);
  assert.equal((await bridge.getContact({ key, target: contact })).ok, true);
  assert.equal((await send(key)).ok, true);
  assert.equal((await adapter.sendMessage(commandFor(longKey, "sendMessage", { conversationId: cid, text: "fixture reply" }))).error.code, "invalid_input");
  assert.deepEqual([state.reads, state.writes], [1, 1]);
});
