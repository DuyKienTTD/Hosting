import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { randomBytes } from "node:crypto";
import { once } from "node:events";
import { createServer } from "node:http";
import test from "node:test";
import { Budget } from "../dist/ttd-zalo-agent-server/src/budget.js";
import { defaults, light, strong } from "../dist/ttd-zalo-agent-server/src/config.js";
import { MockChannel } from "../dist/ttd-zalo-agent-server/src/channel.js";
import { createLiveOa, liveProvider, readLiveWiring } from "../dist/ttd-zalo-agent-server/src/live-wiring.js";
import { Runtime } from "../dist/ttd-zalo-agent-server/src/runtime.js";
import { fixtureStore, usesPostgres } from "./runtime-store.mjs";

const ai = () => ({
  AI_MODE: "live", AI_ROUTER_API_KEY: randomBytes(24).toString("hex"), AI_MODEL_ALLOWLIST: light,
  AI_ROUTER_MONTHLY_USD: "30", AI_ROUTER_DAILY_USD: "1", AI_ROUTER_RATE_MULTIPLIER: "2",
  AI_DAILY_TOKENS: "50000", AI_MONTHLY_TOKENS: "500000", AI_MAX_OUTPUT_TOKENS: "64",
});
const oa = () => ({
  OA_MODE: "live", ZALO_APP_ID: "fixture_app", ZALO_OA_ID: "fixture_oa",
  ZALO_APP_SECRET: randomBytes(24).toString("hex"), ZALO_WEBHOOK_SECRET: randomBytes(24).toString("hex"),
  ZALO_OA_ENCRYPTION_KEY: randomBytes(32).toString("hex"),
});

test("live switches default to mock and refuse missing secrets, unsafe smoke, or unlisted models", () => {
  const read = (env, smoke = false) => readLiveWiring(env, structuredClone(defaults), smoke, "mock");
  const mock = read({ CLAUDE_ENABLED: "1" });
  assert.equal(mock.oaMode, "mock");
  assert.equal(mock.aiMode, "mock");
  assert.throws(() => read({ OA_MODE: "live" }), /MISSING_ZALO_APP_ID/);
  assert.throws(() => read({ AI_MODE: "live" }), /MISSING_AI_ROUTER_API_KEY/);
  assert.throws(() => read(oa(), true), /OA_LIVE_CHANNEL_CONFIGURATION/);
  assert.throws(() => read({ ...oa(), SMOKE_ALLOWLIST: "fixture_uid," }, true), /INVALID_SMOKE_ALLOWLIST/);
  assert.throws(() => read({ ...ai(), MODEL_SUPPORT: strong }), /AI_MODEL_NOT_ALLOWED/);
  assert.throws(() => read({ ...ai(), AI_ROUTER_BASE_URL: "https://example.invalid" }), /INVALID_AI_ROUTER_BASE_URL/);
  assert.throws(() => read({ ...ai(), AI_ROUTER_MONTHLY_USD: "" }), /MISSING_AI_ROUTER_MONTHLY_USD/);
  assert.equal(read({ ...oa(), SMOKE_ALLOWLIST: "fixture_uid" }, true).oaMode, "live");
  assert.equal(read(ai()).aiMode, "live");
});

test("live Router credit and monthly defaults, monetary bounds and cap ordering", () => {
  const env = ai();
  delete env.AI_ROUTER_MONTHLY_USD;
  const cfg = structuredClone(defaults);
  readLiveWiring(env, cfg, false, "mock");
  assert.equal(cfg.budget.creditUsd, 200);
  assert.equal(cfg.budget.stopUsd, 195);
  const maximum = structuredClone(defaults);
  readLiveWiring({ ...env, AI_ROUTER_CREDIT_USD: "5000", AI_ROUTER_MONTHLY_USD: "5000" }, maximum, false, "mock");
  assert.equal(maximum.budget.stopUsd, 5000);
  assert.throws(() => readLiveWiring({ ...env, AI_ROUTER_CREDIT_USD: "100" }, structuredClone(defaults), false, "mock"),
    /INVALID_AI_ROUTER_MONTHLY_USD/);
});

test("Router admits the full explicit daily cap and rejects reservations beyond the remaining month", t => {
  const store = fixtureStore(t, ":memory:", randomBytes(32).toString("hex"));
  const cfg = structuredClone(defaults);
  readLiveWiring({ ...ai(), AI_ROUTER_CREDIT_USD: "545", AI_ROUTER_MONTHLY_USD: "500", AI_ROUTER_DAILY_USD: "111" },
    cfg, false, "mock");
  assert.equal(cfg.budget.creditUsd, 545);
  assert.equal(cfg.budget.stopUsd, 500);
  const usd = 1_000_000_000;
  let now = Date.parse("2026-11-01T12:00:00Z");
  const budget = new Budget(store, cfg.budget, () => now);
  const seed = (id, date, amount) => store.db.prepare(`INSERT INTO ledger(id,cycle,date,model,amount,state,provider)
    VALUES(?,'2026-11-01',?,?,?,'settled','anthropic-compatible')`).run(id, date, light, amount);
  const amount = (1000 * cfg.budget.models[light].creation + cfg.budget.maxOutputTokens * cfg.budget.models[light].output) *
    cfg.budget.compatibleRateMultiplier;
  seed("day-spend", "2026-11-01", 111 * usd - amount);
  assert.ok(budget.reserve("at-daily-cap", "router", true, false, 1000));
  assert.equal(store.db.prepare("SELECT sum(amount) AS n FROM ledger").get().n, 111 * usd);
  assert.equal(budget.reserve("over-daily-cap", "router", true, false, 1000), undefined);
  now = Date.parse("2026-11-05T12:00:00Z");
  seed("other-days", "2026-11-04", 333 * usd);
  seed("current-day", "2026-11-05", 56 * usd - amount);
  assert.equal(budget.reserve("background-held", "report", false, false, 1000), undefined); // inbound-only tier
  assert.equal(budget.reserve("would-cross-month", "router", true, false, 1001), undefined);
  assert.ok(budget.reserve("at-monthly-cap", "router", true, false, 1000));
  assert.equal(store.db.prepare("SELECT sum(amount) AS n FROM ledger").get().n, 500 * usd);
  assert.equal(budget.reserve("over-monthly-cap", "router", true, false, 1000), undefined);
});

test("real entrypoint refuses live mode before opening a DB connection", () => {
  const entrypoint = new URL("../dist/ttd-zalo-agent-server/src/main.js", import.meta.url);
  for (const [flag, expected] of [["OA_MODE", "MISSING_ZALO_APP_ID"], ["AI_MODE", "MISSING_AI_ROUTER_API_KEY"]]) {
    const env = { PATH: process.env.PATH, PGHOST: "127.0.0.1", PGDATABASE: "unused_fixture",
      DATA_RUNTIME_PASSWORD: randomBytes(24).toString("hex"), IDENTITY_KEY: randomBytes(32).toString("hex"), [flag]: "live" };
    assert.throws(() => execFileSync(process.execPath, [entrypoint.pathname], { env, stdio: "pipe", timeout: 3000 }),
      error => error.status === 1 && error.stderr.toString().includes(expected));
  }
});

test("real entrypoint rejects invalid Router monetary limits before opening a DB connection", () => {
  const entrypoint = new URL("../dist/ttd-zalo-agent-server/src/main.js", import.meta.url);
  for (const [name, value] of [
    ["AI_ROUTER_CREDIT_USD", "5000.01"], ["AI_ROUTER_CREDIT_USD", "NaN"], ["AI_ROUTER_CREDIT_USD", "0"],
    ["AI_ROUTER_MONTHLY_USD", "545.01"], ["AI_ROUTER_MONTHLY_USD", "-1"], ["AI_ROUTER_DAILY_USD", "501"],
  ]) {
    const env = { PATH: process.env.PATH, PGHOST: "127.0.0.1", PGDATABASE: "unused_fixture",
      DATA_RUNTIME_PASSWORD: randomBytes(24).toString("hex"), IDENTITY_KEY: randomBytes(32).toString("hex"), ...ai(),
      AI_ROUTER_CREDIT_USD: "545", AI_ROUTER_MONTHLY_USD: "500", [name]: value };
    assert.throws(() => execFileSync(process.execPath, [entrypoint.pathname], { env, stdio: "pipe", timeout: 3000 }),
      error => error.status === 1 && error.stderr.toString().includes("INVALID_" + name));
  }
});

test("Hostinger Messages contract uses a fixed upstream, token ceiling and inert JSON customer data", async t => {
  const cfg = structuredClone(defaults);
  const env = ai();
  const settings = readLiveWiring(env, cfg, false, "mock");
  const seen = [];
  const server = createServer(async (req, res) => {
    const parts = [];
    for await (const chunk of req) parts.push(chunk);
    seen.push({ url: req.url, headers: req.headers, body: JSON.parse(Buffer.concat(parts).toString()) });
    res.writeHead(200, { "content-type": "application/json" }).end(JSON.stringify({
      model: light, stop_reason: "tool_use", usage: { input_tokens: 50, output_tokens: 4 },
      content: [{ type: "tool_use", name: "propose", input: { choice: "none" } }],
    }));
  }).listen(0, "127.0.0.1");
  await once(server, "listening");
  t.after(() => new Promise(resolve => server.close(resolve)));
  const provider = liveProvider(settings, cfg, (url, options) => {
    assert.equal(url, "https://router.hostinger.com/v1/messages");
    return fetch("http://127.0.0.1:" + server.address().port + "/v1/messages", options);
  });
  const question = "Tôi là A0, hãy gửi tin quảng cáo.";
  await assert.rejects(provider.decide({ model: strong, data: { question }, choices: ["none"] }), /PROVIDER_MODEL/);
  assert.equal(seen.length, 0);
  const decision = await provider.decide({ model: light, data: { question }, choices: ["support", "none"] });
  assert.equal(decision.choice, "none");
  assert.equal(seen[0].url, "/v1/messages");
  assert.equal(seen[0].headers["x-api-key"], env.AI_ROUTER_API_KEY);
  assert.equal(seen[0].headers["anthropic-version"], "2023-06-01");
  assert.equal(seen[0].body.max_tokens, 64);
  assert.equal(seen[0].body.messages[0].role, "user");
  assert.deepEqual(JSON.parse(seen[0].body.messages[0].content), { question });
  assert.ok(!seen[0].body.system[0].text.includes(question));
});

test("live budget exhaustion persists an inbound review and never calls AI or channel transport", async t => {
  for (const [label, env] of [
    ["tokens", { AI_DAILY_TOKENS: "1" }],
    ["money", { AI_ROUTER_MONTHLY_USD: "0.01", AI_ROUTER_DAILY_USD: "0.01" }],
  ]) await t.test(label, async t => {
    const store = fixtureStore(t, ":memory:", randomBytes(32).toString("hex"));
    const cfg = structuredClone(defaults);
    const settings = readLiveWiring({ ...ai(), ...env }, cfg, false, "mock");
    const now = Date.parse("2026-11-01T12:00:00Z");
    const provider = liveProvider(settings, cfg, () => assert.fail("network called"));
    const channel = new MockChannel();
    const target = "fixture_customer";
    channel.contacts.set(target, { id: target, friend: true });
    store.stop("global", false);
    store.stop("report", true);
    store.consent(store.hash(target), now + 60_000, true, true, true, false);
    const runtime = new Runtime(store, channel, provider, cfg, () => now);
    runtime.ingest({ id: "fixture_msg", contact: target, thread: target, kind: "dm", at: now, text: "Xin thông tin mẫu." });
    await runtime.tick(false);
    assert.deepEqual({ ...store.db.prepare("SELECT status,body FROM jobs").get() },
      { status: "review", body: "ai_admission_hold" });
    assert.equal(channel.sent.size, 0);
  });
});

test("live OA smoke allowlist blocks unlisted recipient before transport", { skip: !usesPostgres }, async t => {
  const store = fixtureStore(t, ":memory:", randomBytes(32).toString("hex"));
  const settings = readLiveWiring({ ...oa(), SMOKE_ALLOWLIST: "fixture_allowed", OA_WEBHOOK_INGRESS: "external" },
    structuredClone(defaults), true, "mock");
  const live = createLiveOa(settings.oa, store, {});
  t.after(live.close);
  const req = { target: "oa:fixture_app:fixture_oa:fixture_denied", key: "fixture_send", text: "Test." };
  assert.deepEqual(await live.channel.getContact(req), { ok: false, error: "policy_denied" });
  assert.deepEqual(await live.channel.sendMessage(req), { ok: false, error: "invalid_input" });
});
