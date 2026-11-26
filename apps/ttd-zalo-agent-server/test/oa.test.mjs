import { latestSmokeUid, sendOaSmoke } from "../dist/ttd-zalo-agent-server/src/channels/oa/smoke-cli.js";
import assert from "node:assert/strict";
import { createHash, createHmac, randomBytes, randomUUID } from "node:crypto";
import { createServer } from "node:http";
import { request as httpsRequest } from "node:https";
import { execFile } from "node:child_process";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { promisify } from "node:util";
import { once } from "node:events";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import test from "node:test";
import { Pool } from "pg";
import { PostgresRuntimeDatabase } from "../dist/ttd-zalo-agent-server/src/data/runtime-database.js";
import { Store } from "../dist/ttd-zalo-agent-server/src/store.js";
import { Guard } from "../dist/ttd-zalo-agent-server/src/guard.js";
import { OaAiDrafts } from "../dist/ttd-zalo-agent-server/src/web/ai-drafts.js";
import { liveProvider, readLiveWiring } from "../dist/ttd-zalo-agent-server/src/live-wiring.js";
import { oaQuotes } from "../dist/ttd-zalo-agent-server/src/web/oa-quotes.js";
import { Runtime } from "../dist/ttd-zalo-agent-server/src/runtime.js";
import { FakeProvider } from "../dist/ttd-zalo-agent-server/src/provider.js";
import { defaults } from "../dist/ttd-zalo-agent-server/src/config.js";
import { Envelope } from "../dist/ttd-zalo-agent-server/src/channels/oa/crypto.js";
import { accountScope, createOaWebhookServer, OaInbox, oaTarget, oaWebhook, oaWebhookMaxSkewMs } from "../dist/ttd-zalo-agent-server/src/channels/oa/webhook.js";
import { OaTokens } from "../dist/ttd-zalo-agent-server/src/channels/oa/tokens.js";
import { OaAdapter, OaRuntimeChannel } from "../dist/ttd-zalo-agent-server/src/channels/oa/adapter.js";

const postgres = process.env.RUN_POSTGRES_TESTS === "1";
const hour = 3_600_000;
async function server(t, listener) {
  const running = createServer(listener).listen(0, "127.0.0.1");
  await once(running, "listening");
  t.after(() => new Promise(resolve => running.close(resolve)));
  return `http://127.0.0.1:${running.address().port}`;
}

async function fixture(t, extraMigrations = []) {
  const schema = "oa_test_" + randomUUID().replaceAll("-", "");
  const root = new Pool();
  const admin = new Pool({ options: "-c search_path=" + schema });
  const runtime = { user: "data_runtime", password: process.env.DATA_RUNTIME_PASSWORD };
  const pool = new Pool({ ...runtime, options: "-c search_path=" + schema, statement_timeout: 1000 });
  const db = new PostgresRuntimeDatabase(runtime, schema);
  t.after(async () => {
    db.close();
    await Promise.all([pool.end(), admin.end()]);
    try { await root.query("DROP SCHEMA " + schema + " CASCADE"); }
    finally { await root.end(); }
  });
  await root.query("CREATE SCHEMA " + schema);
  for (const path of ["postgres/001.sql", "postgres/002-runtime.sql", "postgres/006-oa.sql", "postgres/007-oa-quota.sql"]) {
    await admin.query(await readFile(new URL("../" + path, import.meta.url), "utf8"));
  }
  const runtimeGrants = await readFile(new URL("../postgres/runtime-grants.sql", import.meta.url), "utf8");
  await admin.query(runtimeGrants.split("\n").filter(line => line.startsWith("GRANT ")).join("\n"));
  for (const file of extraMigrations) {
    await admin.query(await readFile(new URL("../postgres/" + file, import.meta.url), "utf8"));
  }
  await root.query("GRANT USAGE ON SCHEMA " + schema + " TO data_runtime");
  const identity = randomUUID();
  const store = new Store(db, identity);
  const secondStore = () => {
    const otherDb = new PostgresRuntimeDatabase(runtime, schema);
    t.after(() => otherDb.close());
    return new Store(otherDb, identity);
  };
  store.stop("global", false);
  const box = new Envelope(randomBytes(32));
  const account = { appId: "fixture_app", oaId: "fixture_oa", webhookSecret: randomUUID() };
  const scope = accountScope(account);
  const appSecret = randomUUID();
  const calls = { refresh: [], send: [] };
  const upstream = { sendError: 0, disconnect: false, refreshDisconnect: false };
  const mock = await server(t, async (req, res) => {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const body = Buffer.concat(chunks).toString();
    const url = new URL(req.url, "http://localhost");
    res.setHeader("content-type", "application/json");
    if (url.pathname === "/v4/oa/access_token") {
      calls.refresh.push({ header: req.headers.secret_key, form: new URLSearchParams(body) });
      if (upstream.refreshDisconnect) return res.destroy();
      const sequence = calls.refresh.length;
      return res.end(JSON.stringify({ access_token: "mock_access_" + sequence,
        refresh_token: "mock_refresh_" + sequence, expires_in: "90000" }));
    }
    if (url.pathname !== "/v3.0/oa/message/cs") return res.writeHead(404).end();
    const message = JSON.parse(body);
    calls.send.push({ token: req.headers.access_token, proof: req.headers.appsecret_proof, message });
    if (upstream.beforeSend) await upstream.beforeSend();
    if (upstream.disconnect) return res.destroy();
    res.end(JSON.stringify({ error: upstream.sendError, data: { message_id: "fixture_delivery", user_id: message.recipient.user_id } }));
  });
  let now = Date.now();
  const clock = () => now;
  const advance = ms => { now += ms; };
  const tokenManager = () => new OaTokens(pool, box, scope, account.appId, appSecret, mock + "/v4/oa/access_token", clock);
  const tokens = tokenManager();
  const makeChannel = (options = {}, channelStore = store, onSend) => new OaRuntimeChannel(new OaAdapter(channelStore, box, tokens, account,
    appSecret, { endpoint: mock + "/v3.0/oa/message/cs", clock, ...options }), onSend);
  const channel = makeChannel();
  const inbox = new OaInbox(pool, store, box, account, clock);
  const url = await server(t, oaWebhook(inbox));
  const uid = "fixture_uid";
  const target = oaTarget(account, uid);
  const hashed = store.hash(target);
  function signed(event, tamper = false) {
    const packet = { app_id: account.appId, timestamp: String(now), ...event };
    const body = JSON.stringify(packet, null, 1);
    const digest = createHash("sha256").update(account.appId + body + packet.timestamp + account.webhookSecret).digest("hex");
    return { body: tamper ? body + " " : body,
      headers: { "x-zevent-signature": "mac=" + digest, "content-type": "application/json" } };
  }
  function hook(event, { tamper = false } = {}) {
    return fetch(url + "/webhooks/zalo-oa", { method: "POST", ...signed(event, tamper) });
  }
  const message = (name = "fixture_message") => ({
    event_name: "user_send_text", sender: { id: uid }, recipient: { id: account.oaId },
    message: { msg_id: name, text: "Thông số mẫu thử?" },
  });
  const follow = event_name => ({ event_name, oa_id: account.oaId, follower: { id: uid } });
  const withdraw = () => hook({ event_name: "user_withdraw", oa_id: account.oaId, user_id: uid });
  const consent = () => store.consent(hashed, now + 10 * 24 * hour, true, true, true, true,
    { displayedText: "Fixture", policyVersion: "fixture-1", evidence: { source: "mock" } });
  const install = (issued = now) => tokens.install({ access: "mock_initial_access", refresh: "mock_initial_refresh", seconds: 90_000 }, issued);
  return { pool, store, target, hashed, account, appSecret, channel, makeChannel, secondStore, clock, advance, calls, upstream,
    tokens, tokenManager, hook, message, follow, withdraw, consent, install, inbox, signed };
}

test("OA OAuth rotates once across managers, encrypts pairs and invalidates only the matching generation", { skip: !postgres }, async t => {
  const f = await fixture(t);
  await f.install(f.clock() - 25 * hour);
  const row = (await f.pool.query("SELECT * FROM oa_oauth")).rows[0];
  assert.equal(+row.access_until - (f.clock() - 25 * hour), 25 * hour);
  assert.ok(+row.refresh_until > f.clock() + 85 * 24 * hour);
  assert.equal(row.access_cipher.includes("mock_initial_access"), false);
  assert.equal(row.refresh_cipher.includes("mock_initial_refresh"), false);
  const results = await Promise.all([f.tokens.current(), f.tokenManager().current(), f.tokenManager().current()]);
  assert.equal(f.calls.refresh.length, 1);
  assert.equal(f.calls.refresh[0].header, f.appSecret);
  assert.equal(f.calls.refresh[0].form.get("grant_type"), "refresh_token");
  assert.equal(f.calls.refresh[0].form.get("refresh_token"), "mock_initial_refresh");
  assert.equal(new Set(results.map(result => result.generation)).size, 1);
  await f.tokens.invalidate(row.generation);
  assert.equal((await f.tokens.current()).generation, results[0].generation);
  await f.tokens.invalidate(results[0].generation);
  assert.equal((await f.tokens.current()).value, "mock_access_2");
  assert.equal(f.calls.refresh[1].form.get("refresh_token"), "mock_refresh_1");
});

test("OA never presents a refresh token again following an ambiguous response", { skip: !postgres }, async t => {
  const f = await fixture(t);
  await f.install(f.clock() - 25 * hour);
  f.upstream.refreshDisconnect = true;
  await assert.rejects(f.tokens.current(), /OA_REAUTHORIZATION_REQUIRED/);
  await assert.rejects(f.tokenManager().current(), /OA_REAUTHORIZATION_REQUIRED/);
  assert.equal(f.calls.refresh.length, 1);
});

test("OA webhook authenticates raw bytes, persists before ACK, deduplicates, and applies ordered consent changes", { skip: !postgres }, async t => {
  const f = await fixture(t);
  f.consent();
  const started = performance.now();
  assert.equal((await f.hook(f.message())).status, 200);
  assert.ok(performance.now() - started < 2000);
  assert.equal((await f.pool.query("SELECT event_id FROM oa_inbox")).rowCount, 1);
  const rejected = await f.hook(f.message("tampered_unique"), { tamper: true });
  assert.equal(rejected.status, 200);
  assert.deepEqual(await rejected.json(), { error: 0 });
  const responses = await Promise.all(Array.from({ length: 8 }, () => f.hook(f.message())));
  assert.ok(responses.every(response => response.status === 200));
  for (const offset of [-300_001, 300_001]) {
    assert.equal((await f.hook({ ...f.message("fixture_skew"), timestamp: String(f.clock() + offset) })).status, 200);
  }
  assert.equal((await f.pool.query("SELECT event_id FROM oa_inbox")).rowCount, 1);
  const request = { key: "fixture_poll", target: "channel" };
  const first = await f.channel.receiveMessage(request);
  assert.equal(first.value.length, 1);
  assert.equal(first.value[0].channel, "oa");
  f.channel.acknowledge("message");
  assert.equal((await f.channel.receiveMessage(request)).value.length, 0);
  assert.equal((await f.makeChannel().receiveMessage(request)).value.length, 1);
  assert.equal((await f.hook(f.follow("follow"))).status, 200);
  assert.equal((await f.pool.query("SELECT following FROM oa_contacts")).rows[0].following, true);
  f.advance(10);
  assert.equal((await f.hook(f.follow("unfollow"))).status, 200);
  assert.equal(f.store.contact(f.hashed, f.clock()).ad_state, "opted_out");
  assert.ok(f.store.policy(f.hashed, "support", f.clock()).send);
  f.advance(10);
  assert.equal((await f.hook(f.follow("follow"))).status, 200);
  assert.equal(f.store.contact(f.hashed, f.clock()).ad_state, "opted_out");
  assert.equal((await f.withdraw()).status, 200);
  assert.equal(f.store.policy(f.hashed, "support", f.clock()).send, false);
  assert.equal((await f.makeChannel().receiveMessage(request)).value.length, 0);
  assert.equal((await f.hook(f.message("after_withdraw"))).status, 200);
  assert.equal((await f.pool.query("SELECT 1 FROM oa_inbox WHERE sealed IS NOT NULL")).rowCount, 0);
});

test("OA runtime consumes the queue and Guard records a provider ambiguity once with no replay", { skip: !postgres }, async t => {
  const f = await fixture(t);
  await f.install();
  f.consent();
  assert.equal((await f.hook(f.message())).status, 200);
  const config = structuredClone(defaults);
  const aiStages = [];
  const provider = new FakeProvider(task => {
    if (task.choices.includes("support")) aiStages.push("router");
    if (task.choices.includes("answer")) aiStages.push("support");
    return task.choices.find(choice => choice !== "none") ?? "none";
  });
  const runtime = new Runtime(f.store, f.channel, provider, config, f.clock);
  await runtime.tick();
  assert.ok(aiStages.includes("router") && aiStages.includes("support"));
  const [{ id: origin }] = f.store.db.prepare("SELECT id FROM inbound").all();
  assert.equal((await f.channel.sendMessage({ key: "unreserved", target: f.target, text: "Fixture" })).error, "policy_denied");
  const guard = new Guard(f.store, f.channel, config, f.clock);
  const reply = id => ({ agent: "support", kind: "reply", id, origin, target: f.target, thread: f.target,
    text: "Fixture", revision: f.store.policy(f.hashed, "support", f.clock()).revision, epoch: f.store.setting("epoch") });
  const before = f.calls.send.length;
  assert.equal(await guard.dispatch(reply("fixture_send")), "sent");
  const sent = f.calls.send.at(-1);
  assert.equal(sent.token, "mock_initial_access");
  assert.equal(sent.proof, createHmac("sha256", f.appSecret).update(sent.token).digest("hex"));
  assert.equal(sent.message.recipient.user_id, "fixture_uid");
  f.upstream.disconnect = true;
  assert.equal(await guard.dispatch(reply("fixture_unknown")), "unknown");
  assert.equal(f.store.db.prepare("SELECT state FROM send_log WHERE id=?").get(f.store.hash("fixture_unknown")).state,
    "unknown_delivery");
  assert.equal(await guard.dispatch(reply("fixture_unknown")), "duplicate");
  assert.equal(f.calls.send.length, before + 2);
  assert.equal(f.store.setting("ADS_ENABLED"), 0);
});

test("live OA in mock channel mode drafts under global STOP without sending or retaining unconsented text",
  { skip: !postgres }, async t => {
    const f = await fixture(t, ["009-web-operator.sql", "012-ai-drafts.sql", "016-draft-consent-marker.sql"]);
    const config = structuredClone(defaults);
    const wiring = readLiveWiring({
      OA_MODE: "live", CHANNEL_SMOKE_ONLY: "0", AI_MODE: "live", CHANNEL_MODE: "mock",
      ZALO_APP_ID: f.account.appId, ZALO_OA_ID: f.account.oaId, ZALO_APP_SECRET: f.appSecret,
      ZALO_WEBHOOK_SECRET: f.account.webhookSecret, ZALO_OA_ENCRYPTION_KEY: randomBytes(32).toString("hex"),
      AI_ROUTER_API_KEY: randomUUID(), AI_MODEL_ALLOWLIST: config.budget.byAgent.support,
      AI_ROUTER_RATE_MULTIPLIER: "1", AI_ROUTER_DAILY_USD: "1", AI_DAILY_TOKENS: "50000", AI_MONTHLY_TOKENS: "500000",
    }, config, false, "mock");
    assert.equal(wiring.oaMode, "live");
    assert.equal(wiring.aiMode, "live");
    let calls = 0;
    const provider = liveProvider(wiring, config, async (_url, init) => {
      calls++;
      const request = JSON.parse(init.body);
      assert.equal(JSON.parse(request.messages[0].content).purpose, "classify_customer_intent");
      return Response.json({ model: request.model, stop_reason: "tool_use", usage: { input_tokens: 100, output_tokens: 20 },
        content: [{ type: "tool_use", name: "propose", input: { choice: "price" } }] });
    });
    const drafts = new OaAiDrafts(f.store, config, provider, true, f.clock);
    const runtime = new Runtime(f.store, f.channel, provider, config, f.clock, [], true, drafts);
    f.consent();
    f.store.stop("global", true);
    const event = f.message("budget_fixture");
    event.message.text = "Xin báo giá SKU UNKNOWN-01.";
    assert.equal((await f.hook(event)).status, 200);
    assert.equal((await f.hook(event)).status, 200);
    await runtime.tick();
    const { rows } = await f.pool.query("SELECT id,inbound_id,ai_state,ai_reason,ai_intent,ai_message_id FROM web_reply_drafts");
    assert.equal(rows.length, 1);
    assert.equal(rows[0].ai_state, "needs_human");
    assert.equal(rows[0].ai_reason, "no_knowledge");
    assert.equal(rows[0].ai_intent, "price");
    assert.ok(rows[0].ai_message_id);
    assert.equal(calls, 1);
    assert.equal((await f.pool.query("SELECT 1 FROM ledger WHERE state='settled'")).rowCount, 1);
    assert.equal(await runtime.guard.dispatch({ agent: "support", kind: "reply", id: "fixture_stopped", origin: rows[0].inbound_id,
      target: f.target, thread: f.target, text: "Fixture", revision: f.store.policy(f.hashed, "support", f.clock()).revision,
      epoch: f.store.setting("epoch") }), "stopped");

    const noConsent = f.message("without_consent");
    noConsent.sender.id = "fixture_no_consent";
    assert.equal((await f.hook(noConsent)).status, 200);
    await runtime.tick();
    const marker = (await f.pool.query("SELECT id,body,ai_state,ai_reason,ai_message_id FROM web_reply_drafts WHERE ai_reason='consent'")).rows[0];
    assert.deepEqual(marker && [marker.body, marker.ai_state, marker.ai_reason, marker.ai_message_id], ["", "needs_human", "consent", null]);
    assert.equal(drafts.get(marker.id).reason, "consent");
    assert.equal(await drafts.regenerate(marker.id, drafts.get(marker.id).version), undefined);
    assert.equal((await f.pool.query("SELECT id FROM visible_messages")).rowCount, 1);
    assert.equal(calls, 1);
    assert.equal((await f.pool.query("SELECT id FROM ledger")).rowCount, 1);

    drafts.setEnabled(false);
    assert.equal((await f.hook(f.message("drafts_disabled"))).status, 200);
    await runtime.tick();
    assert.equal((await f.pool.query("SELECT 1 FROM web_reply_drafts WHERE ai_reason='unavailable'")).rowCount, 1);
    assert.equal(calls, 1);
    assert.equal((await f.pool.query("SELECT id FROM send_log")).rowCount, 0);
    assert.equal(f.calls.send.length, 0);
  });

test("OA checks the 48h and seven-day boundaries and invalidates provider-rejected access", { skip: !postgres }, async t => {
  const f = await fixture(t);
  f.consent();
  await f.install();
  assert.equal((await f.hook(f.message())).status, 200);
  const config = structuredClone(defaults);
  config.scheduling.maxInboundAgeMs = 7 * 24 * hour;
  const [{ id }] = (await f.channel.receiveMessage({ key: "poll", target: "channel" })).value;
  const origin = f.store.eventKey(f.target, f.target, id);
  f.store.db.prepare("INSERT INTO inbound VALUES(?,?,?)").run(origin, f.hashed, f.clock());
  const reply = id => ({ agent: "support", kind: "reply", id, origin, target: f.target,
    text: "Fixture", revision: f.store.policy(f.hashed, "support", f.clock()).revision, epoch: f.store.setting("epoch") });
  const guard = new Guard(f.store, f.channel, config, f.clock);
  f.upstream.sendError = -220;
  assert.equal(await guard.dispatch(reply("old_access")), "failed");
  f.upstream.sendError = 0;
  assert.equal(await guard.dispatch(reply("new_access")), "sent");
  assert.equal(f.calls.refresh.length, 1);
  assert.equal(f.calls.send.at(-1).token, "mock_access_1");
  f.advance(48 * hour);
  assert.equal(await guard.dispatch(reply("free_boundary")), "policy_denied");
  const extended = new Guard(f.store, f.makeChannel({ allowAfter48h: true }), config, f.clock);
  assert.equal(await extended.dispatch(reply("paid_boundary")), "sent");
  f.advance(5 * 24 * hour);
  assert.equal(await extended.dispatch(reply("week_boundary")), "policy_denied");
});

test("OA accepts signed events over HTTPS and returns a timely 503 under lock contention", { skip: !postgres }, async t => {
  const f = await fixture(t);
  const tlsDir = await mkdtemp(join(tmpdir(), "oa-tls-"));
  t.after(() => rm(tlsDir, { recursive: true, force: true }));
  const certPath = join(tlsDir, "cert.pem");
  const keyPath = join(tlsDir, "key.pem");
  await promisify(execFile)("openssl", ["req", "-x509", "-newkey", "rsa:2048", "-nodes",
    "-subj", "/CN=localhost", "-addext", "subjectAltName=IP:127.0.0.1",
    "-days", "1", "-keyout", keyPath, "-out", certPath]);
  const [cert, key] = await Promise.all([readFile(certPath), readFile(keyPath)]);
  const tlsServer = createOaWebhookServer({ cert, key }, f.inbox).listen(0, "127.0.0.1");
  await once(tlsServer, "listening");
  t.after(() => new Promise(resolve => tlsServer.close(resolve)));
  const { body, headers } = f.signed(f.message());
  const post = () => new Promise((resolve, reject) => {
    const req = httpsRequest({ host: "127.0.0.1", port: tlsServer.address().port,
      method: "POST", path: "/webhooks/zalo-oa", ca: cert, headers }, res => {
      res.resume();
      res.once("end", () => resolve(res.statusCode));
    });
    req.once("error", reject);
    req.end(body);
  });
  const locked = await f.pool.connect();
  try {
    await locked.query("SELECT pg_advisory_lock(76425161)");
    const started = performance.now();
    assert.equal(await post(), 503);
    assert.ok(performance.now() - started < 2000);
    assert.equal((await locked.query("SELECT 1 FROM oa_inbox")).rowCount, 0);
  } finally {
    await locked.query("SELECT pg_advisory_unlock(76425161)");
    locked.release();
  }
  assert.equal(await post(), 200);
  assert.equal((await f.pool.query("SELECT 1 FROM oa_inbox")).rowCount, 1);
});

async function consultationFixture(t, options = {}) {
  const f = await fixture(t);
  await f.install();
  f.consent();
  assert.equal((await f.hook(f.message())).status, 200);
  const config = structuredClone(defaults);
  config.scheduling.maxInboundAgeMs = 7 * 24 * hour;
  const [{ id }] = (await f.channel.receiveMessage({ key: "quota_poll", target: "channel" })).value;
  const origin = f.store.eventKey(f.target, f.target, id);
  f.store.db.prepare("INSERT INTO inbound VALUES(?,?,?)").run(origin, f.hashed, f.clock());
  const proposal = id => ({ agent: "support", kind: "reply", id, origin, target: f.target, thread: f.target,
    text: "Fixture", revision: f.store.policy(f.hashed, "support", f.clock()).revision, epoch: f.store.setting("epoch") });
  const guard = (overrides = {}, store = f.store) => new Guard(store,
    f.makeChannel({ allowAfter48h: true, ...options, ...overrides }, store), config, f.clock);
  const log = id => f.pool.query("SELECT state,message_type,send_window,quota_month,quota_bucket FROM send_log WHERE id=$1",
    [f.store.hash(id)]).then(result => result.rows[0]);
  return { ...f, proposal, guard, log };
}

test("OA logs consultation type and classifies 47h, 49h, 6d 23h and 7d 1h", { skip: !postgres }, async t => {
  const f = await consultationFixture(t);
  const guard = f.guard();
  let previous = 0;
  for (const [hours, window, bucket] of [
    [47, "within_48h", "free_window"], [49, "48h_to_7d", "monthly"], [167, "48h_to_7d", "monthly"],
  ]) {
    f.advance((hours - previous) * hour);
    previous = hours;
    const id = "quota_" + hours;
    assert.equal(await guard.dispatch(f.proposal(id)), "sent");
    const row = await f.log(id);
    assert.equal(row.message_type, "oa_consultation");
    assert.equal(row.send_window, window);
    assert.equal(row.quota_bucket, bucket);
    assert.equal(row.quota_month, bucket === "monthly"
      ? new Date(f.clock() + 7 * hour).toISOString().slice(0, 7) : null);
  }
  f.advance(2 * hour);
  assert.equal(await guard.dispatch(f.proposal("too_late")), "policy_denied");
  assert.equal(await f.log("too_late"), undefined);
  assert.equal(f.calls.send.length, 3);
});

test("OA releases a definite failure, keeps unknown delivery, and requires opt-in for paid overflow", { skip: !postgres }, async t => {
  const f = await consultationFixture(t, { monthlyQuota: 1 });
  f.advance(49 * hour);
  const guard = f.guard();
  f.upstream.sendError = -200;
  assert.equal(await guard.dispatch(f.proposal("definite_failure")), "failed");
  assert.equal((await f.log("definite_failure")).state, "failed");
  f.upstream.sendError = 0;
  f.upstream.disconnect = true;
  assert.equal(await guard.dispatch(f.proposal("ambiguous")), "unknown");
  assert.equal((await f.log("ambiguous")).state, "unknown_delivery");
  assert.equal(await guard.dispatch(f.proposal("ambiguous")), "duplicate");
  assert.equal(await guard.dispatch(f.proposal("blocked")), "quota_exhausted");
  assert.equal(await f.log("blocked"), undefined);
  assert.equal(f.calls.send.length, 2);
  f.upstream.disconnect = false;
  assert.equal(await f.guard({ allowPaidOverflow: true }).dispatch(f.proposal("paid")), "sent");
  assert.equal((await f.log("paid")).quota_bucket, "paid_overflow");
  assert.equal(f.calls.send.length, 3);
});

test("OA commits the last monthly slot before transport and blocks a competing Postgres session", { skip: !postgres }, async t => {
  const f = await consultationFixture(t, { monthlyQuota: 1 });
  f.advance(49 * hour);
  const other = f.secondStore();
  const transportStarted = Promise.withResolvers();
  const releaseTransport = Promise.withResolvers();
  f.upstream.beforeSend = () => {
    transportStarted.resolve();
    return releaseTransport.promise;
  };
  const first = f.guard().dispatch(f.proposal("first"));
  try {
    await Promise.race([transportStarted.promise, first.then(outcome => assert.fail(outcome))]);
    assert.equal((await f.log("first")).state, "reserved");
    assert.equal((await f.log("first")).quota_bucket, "monthly");
    assert.equal(await f.guard({}, other).dispatch(f.proposal("competing")), "quota_exhausted");
    assert.equal(await f.log("competing"), undefined);
    assert.equal(f.calls.send.length, 1);
  } finally { releaseTransport.resolve(); }
  assert.equal(await first, "sent");
  assert.equal((await f.log("first")).state, "sent");
});

async function quoteEndpoint(t, f, store = f.store) {
  const approved = { customerId: "fixture-customer", productId: "fixture-product", priceList: "fixture-price" };
  const route = oaQuotes({
    store, config: defaults, channel: f.makeChannel({ allowAfter48h: true, monthlyQuota: 1 }, store), clock: f.clock,
    authenticate: async req => {
      const role = new Map([["fixture-owner", "owner"], ["fixture-sales", "sales"], ["fixture-support", "support"], ["fixture-a0", "a0"]])
        .get(req.headers.authorization);
      return role ? { id: role, label: role, role } : undefined;
    },
    resolve: async selection => {
      assert.equal("lastInteractionAt" in selection, false);
      if (!Object.entries(approved).every(([key, value]) => selection[key] === value)) return;
      return { target: f.target, origin: f.proposal("preview").origin,
        totalMillimetres: selection.quantity * 2500, totalVnd: selection.quantity * 300000 };
    },
  });
  const url = await server(t, (req, res) => {
    void route.handle(req, res).then(handled => { if (!handled) res.writeHead(404).end(); },
      () => res.writeHead(500).end());
  });
  return {
    block: () => route.block(f.target),
    send: (quantity, role = "owner") => fetch(url + "/api/v1/quotes/oa-send", {
      method: "POST", headers: { authorization: "fixture-" + role, "content-type": "application/json" },
      body: JSON.stringify({ ...approved, confirmed: true, unit: "bar", quantity, lastInteractionAt: f.clock() }),
    }),
  };
}

test("quote HTTP sends through Postgres Guard at 47h and 49h, expires at 168h", { skip: !postgres }, async t => {
  const f = await consultationFixture(t);
  const api = await quoteEndpoint(t, f);
  f.advance(47 * hour);
  const reply = await api.send(1);
  assert.equal(reply.status, 201);
  const result = await reply.json();
  assert.equal(result.delivery, "sent");
  assert.equal((await f.log(result.id)).quota_bucket, "free_window");
  assert.equal((await f.log(result.id)).quota_month, null);

  f.advance(2 * hour);
  const monthly = await api.send(2, "sales");
  assert.equal(monthly.status, 201);
  assert.equal((await f.log((await monthly.json()).id)).quota_bucket, "monthly");
  assert.equal(api.block(), "quota_exhausted");
  const exhausted = await api.send(3);
  assert.equal(exhausted.status, 409);
  assert.equal((await exhausted.json()).code, "quota_exhausted");

  f.advance(119 * hour);
  for (const role of ["owner", "sales"]) {
    const expired = await api.send(4, role);
    assert.equal(expired.status, 409);
    assert.equal((await expired.json()).code, "oa_window_expired");
  }
  assert.equal(api.block(), "oa_window_expired");
  assert.equal(f.calls.send.length, 2);
});

test("quote HTTP at 6d 23h, roles and opt-out use the live Guard", { skip: !postgres }, async t => {
  const f = await consultationFixture(t);
  const api = await quoteEndpoint(t, f);
  f.advance(167 * hour);
  for (const role of ["support", "a0"]) assert.equal((await api.send(1, role)).status, 403);
  const response = await api.send(1);
  assert.equal(response.status, 201);
  assert.equal((await f.log((await response.json()).id)).send_window, "48h_to_7d");
  f.store.optOut(f.hashed);
  const denied = await api.send(2, "sales");
  assert.equal(denied.status, 409);
  assert.equal((await denied.json()).code, "oa_policy_denied");
  assert.equal(f.calls.send.length, 1);
});

test("two quote HTTP sessions contend for one Postgres quota slot", { skip: !postgres }, async t => {
  const f = await consultationFixture(t);
  f.advance(49 * hour);
  const primary = await quoteEndpoint(t, f);
  const other = await quoteEndpoint(t, f, f.secondStore());
  const started = Promise.withResolvers();
  const release = Promise.withResolvers();
  f.upstream.beforeSend = () => { started.resolve(); return release.promise; };
  const first = primary.send(1);
  try {
    await Promise.race([started.promise, first.then(res => assert.fail("Transport not started: " + res.status))]);
    const denied = await other.send(2, "sales");
    assert.equal(denied.status, 409);
    assert.equal((await denied.json()).code, "quota_exhausted");
    assert.equal((await f.pool.query("SELECT 1 FROM send_log WHERE quota_bucket='monthly'")).rowCount, 1);
    assert.equal(f.calls.send.length, 1);
  } finally { release.resolve(); }
  assert.equal((await first).status, 201);
});

test("signed stale or future events fail before any database access", async () => {
  const account = { appId: "fixture_app", oaId: "fixture_oa", webhookSecret: randomUUID() };
  const now = Date.now();
  const maxSkewMs = oaWebhookMaxSkewMs("60");
  assert.equal(oaWebhookMaxSkewMs(), 300_000);
  assert.throws(() => oaWebhookMaxSkewMs("0"), /INVALID_OA_WEBHOOK_MAX_SKEW_SECONDS/);
  let queries = 0;
  const pool = { query: async () => { queries++; } };
  const inbox = new OaInbox(pool, { hash: value => value }, new Envelope(randomBytes(32)), account, () => now, maxSkewMs);
  for (const [offset, status] of [[-60_001, 401], [60_001, 401], [-60_000, 200], [60_000, 200]]) {
    const timestamp = String(now + offset);
    const raw = Buffer.from(JSON.stringify({ app_id: account.appId, timestamp, event_name: "user_send_text",
      sender: { id: "fixture_uid" }, recipient: { id: account.oaId }, message: { msg_id: "fixture_id", text: "Fixture" } }));
    const signature = createHash("sha256").update(account.appId).update(raw).update(timestamp).update(account.webhookSecret).digest("hex");
    const before = queries;
    assert.equal(await inbox.accept(raw, "mac=" + signature, AbortSignal.timeout(1000)), status);
    assert.equal(queries - before, status === 200 ? 1 : 0);
  }
});

test("OA smoke command uses signed inbox evidence, scoped consent, Guard and the provider receipt", { skip: !postgres }, async t => {
  const f = await fixture(t);
  await f.install(f.clock() - 25 * hour);
  const uid = "fixture_uid";
  const modes = { oaMode: "live", smokeOnly: true, smokeAllowlist: new Set([uid]) };
  const cfg = structuredClone(defaults);
  let receipt;
  const channel = f.makeChannel({ allowedUids: modes.smokeAllowlist }, f.store, result => { receipt = result; });
  const oa = { channel, account: f.account };
  const send = (target = uid, options = modes, approve = false) => {
    receipt = undefined;
    return sendOaSmoke(f.store, cfg, oa, options, target, "Tin thử fixture", approve, () => receipt, f.clock);
  };
  assert.equal((await f.hook(f.message())).status, 200);
  assert.equal(latestSmokeUid(oa), uid);
  assert.equal((await send(uid, { ...modes, oaMode: "mock" }, true)).error, "oa_live_required");
  assert.equal((await send(uid, { ...modes, smokeOnly: false }, true)).error, "oa_smoke_only_required");
  assert.equal((await send("another_uid", modes, true)).error, "oa_uid_not_allowlisted");
  f.store.stop("global", true);
  assert.equal((await send(uid, modes, true)).error, "stopped");
  f.store.stop("global", false);
  assert.equal((await send()).error, "consent");
  assert.equal((await f.pool.query("SELECT 1 FROM consents")).rowCount, 0);
  assert.equal(f.calls.send.length, 0);
  assert.equal(f.calls.refresh.length, 0);

  assert.deepEqual(await send(uid, modes, true), { ok: true, message_id: "fixture_delivery" });
  assert.equal(f.calls.refresh.length, 1);
  const request = f.calls.send[0];
  assert.equal(request.message.recipient.user_id, uid);
  assert.equal(request.proof, createHmac("sha256", f.appSecret).update(request.token).digest("hex"));
  assert.equal((await f.pool.query("SELECT state FROM send_log")).rows[0].state, "sent");
  const consents = (await f.pool.query("SELECT purpose,evidence FROM consents ORDER BY purpose")).rows;
  assert.deepEqual(consents.map(row => row.purpose), ["respond", "send"]);
  assert.ok(consents.every(row => row.evidence.source === "smoke_test_owner_approved" && row.evidence.inbound));

  f.upstream.sendError = -200;
  assert.deepEqual(await send(), { ok: false, error: "failed", channel_error: "policy_denied", zalo_error: -200 });
  f.upstream.disconnect = true;
  assert.deepEqual(await send(), { ok: false, error: "unknown_delivery", channel_error: "unknown_delivery" });
  assert.equal(f.calls.send.length, 3);
  assert.equal((await f.pool.query("SELECT 1 FROM send_log WHERE state='unknown_delivery'")).rowCount, 1);

  await f.withdraw();
  assert.equal((await send(uid, modes, true)).ok, false);
  assert.equal(f.calls.send.length, 3);
});
