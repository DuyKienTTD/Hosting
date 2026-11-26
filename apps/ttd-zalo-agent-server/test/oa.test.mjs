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
import { Runtime } from "../dist/ttd-zalo-agent-server/src/runtime.js";
import { FakeProvider } from "../dist/ttd-zalo-agent-server/src/provider.js";
import { defaults } from "../dist/ttd-zalo-agent-server/src/config.js";
import { Envelope } from "../dist/ttd-zalo-agent-server/src/channels/oa/crypto.js";
import { accountScope, createOaWebhookServer, OaInbox, oaTarget, oaWebhook } from "../dist/ttd-zalo-agent-server/src/channels/oa/webhook.js";
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

async function fixture(t) {
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
  for (const path of ["postgres/001.sql", "postgres/002-runtime.sql", "src/channels/oa/schema.sql"]) {
    await admin.query(await readFile(new URL("../" + path, import.meta.url), "utf8"));
  }
  const runtimeGrants = await readFile(new URL("../postgres/runtime-grants.sql", import.meta.url), "utf8");
  await admin.query(runtimeGrants.split("\n").filter(line => line.startsWith("GRANT ")).join("\n"));
  await root.query("GRANT USAGE ON SCHEMA " + schema + " TO data_runtime");
  const store = new Store(db, randomUUID());
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
    if (upstream.disconnect) return res.destroy();
    res.end(JSON.stringify({ error: upstream.sendError, data: { message_id: "fixture_delivery", user_id: message.recipient.user_id } }));
  });
  let now = Date.now();
  const clock = () => now;
  const advance = ms => { now += ms; };
  const tokenManager = () => new OaTokens(pool, box, scope, account.appId, appSecret, mock + "/v4/oa/access_token", clock);
  const tokens = tokenManager();
  const makeChannel = (allowAfter48h = false) => new OaRuntimeChannel(new OaAdapter(store, box, tokens, account,
    appSecret, { endpoint: mock + "/v3.0/oa/message/cs", clock, allowAfter48h }));
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
  return { pool, store, target, hashed, account, appSecret, channel, makeChannel, clock, advance, calls, upstream,
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
  assert.equal((await f.hook(f.message(), { tamper: true })).status, 401);
  const responses = await Promise.all(Array.from({ length: 8 }, () => f.hook(f.message())));
  assert.ok(responses.every(response => response.status === 200));
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
  const extended = new Guard(f.store, f.makeChannel(true), config, f.clock);
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
