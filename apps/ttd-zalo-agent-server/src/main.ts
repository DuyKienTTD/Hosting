import { oaWebInbox } from "./web/oa-inbox.js";
import { latestSmokeUid, modeError, sendOaSmoke } from "./channels/oa/smoke-cli.js";
import type { Result as OaResult, Results as OaResults } from "./adapters/contract.js";
import { createOperator } from "./web/accounts.js";
import { serveWebAssets } from "./web/static.js";
import { Pool } from "pg";
import { Envelope } from "./channels/oa/crypto.js";
import { OaAdapter, OaRuntimeChannel } from "./channels/oa/adapter.js";
import { OaTokens } from "./channels/oa/tokens.js";
import { accountScope, OaInbox, oaWebhook } from "./channels/oa/webhook.js";
import { webApi } from "./web/api.js";
import { attachNickAudit } from "./adapters/nick-audit.js";
import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import { PostgresRuntimeDatabase } from "./data/runtime-database.js";
import { defaults } from "./config.js";
import { MockChannel } from "./channel.js";
import { isAgent } from "./provider.js";
import { Runtime, type Schedule } from "./runtime.js";
import { operator } from "./operator.js";
import { Store } from "./store.js";
import { readRoutes, setupChannels, webhookHandler } from "./adapters/setup.js";
import { smoke } from "./adapters/smoke.js";
import { createLiveOa, liveProvider, readLiveWiring, readOa } from "./live-wiring.js";

process.umask(0o077);
const command = process.argv[2] ?? "serve";
const mode = process.env.CHANNEL_MODE ?? "mock";
const smokeOnly = process.env.CHANNEL_SMOKE_ONLY === "1";
if (command === "oa-smoke-send") {
  const error = modeError({ oaMode: process.env.OA_MODE ?? "mock", smokeOnly,
    smokeAllowlist: new Set((process.env.SMOKE_ALLOWLIST ?? "").split(",").map(uid => uid.trim()).filter(Boolean)),
  }, process.argv[3] ?? "");
  if (error) {
    console.log(JSON.stringify({ ok: false, error }));
    process.exit(1);
  }
}
const { PGHOST, PGDATABASE, DATA_RUNTIME_PASSWORD } = process.env;
if (!PGHOST || !PGDATABASE || !DATA_RUNTIME_PASSWORD) throw Error("POSTGRES_CONFIGURATION_REQUIRED");
const key = process.env.IDENTITY_KEY ?? "";
const config = structuredClone(defaults);
config.advertising.enabled = process.env.ADS_ENABLED === "true";
const anchor = Number(process.env.CREDIT_CYCLE_START_DAY ?? config.budget.cycleStartDay);
if (!Number.isInteger(anchor) || anchor < 1 || anchor > 28 || Buffer.byteLength(key) < 32 ||
  !["mock", "subiz", "oa"].includes(mode)) throw Error("INVALID_CONFIGURATION");
config.budget.cycleStartDay = anchor;
const wiring = readLiveWiring(process.env, config, smokeOnly, mode);
const postgres = { host: PGHOST, database: PGDATABASE, user: "data_runtime", password: DATA_RUNTIME_PASSWORD };
const store = new Store(new PostgresRuntimeDatabase(postgres), key, Number(process.env.DATA_RETENTION_DAYS ?? "30"));
let smokeReceipt: OaResult<OaResults["sendMessage"]> | undefined;
const liveOa = wiring.oa && createLiveOa(wiring.oa, store, postgres,
  command === "oa-smoke-send" ? receipt => { smokeReceipt = receipt; } : undefined);
const onboarding = command === "serve" && process.env.WEB_ORIGIN && process.env.OA_ONBOARD_ENABLED === "1"
  ? liveOa || createLiveOa(readOa({ ...process.env, OA_WEBHOOK_INGRESS: "external" }), store, postgres)
  : undefined;
if (command === "serve" && (process.env.ADS_ENABLED === "false" || ((liveOa || mode === "oa") && process.env.WEB_ORIGIN))) store.set("ADS_ENABLED", 0);
const input = () => JSON.parse(readFileSync(0, "utf8"));
const commands: Record<string, () => unknown> = {
  smoke: async () => {
    if (mode !== "subiz" || !smokeOnly || process.env.CLAUDE_ENABLED === "1") {
      console.log(JSON.stringify({ status: "FAIL", step: "smoke_mode_required" }));
      process.exitCode = 1;
      return;
    }
    let outcome;
    try {
      const routes = readRoutes();
      const active = await setupChannels(store, routes, true);
      outcome = await smoke(store, config, routes, active, process.env.SUBIZ_SMOKE_CONTACT, process.env.SUBIZ_SMOKE_NONCE);
    } catch { outcome = { status: "FAIL", step: "configuration_or_transport" }; }
    console.log(JSON.stringify(outcome));
    if (outcome.status !== "PASS") process.exitCode = 1;
  },
  "web-bootstrap-owner": async () => {
    const result = await createOperator(store, null, {
      account: process.argv[3], label: process.argv[4], role: "owner",
      passphrase: readFileSync(0, "utf8").replace(/\r?\n$/, ""),
    });
    if (result.status !== 201) { console.error(result.message); process.exitCode = 1; }
    else console.log("Đã tạo tài khoản Chủ dự án.");
  },
  "oa-smoke-send": async () => {
    const uid = process.argv[3] ?? "";
    const option = process.argv[4];
    const error = modeError(wiring, uid);
    const result = error || !liveOa ? { ok: false, error: error ?? "oa_live_required" }
      : option !== undefined && option !== "--approve-consent" || process.argv.length > 5
        ? { ok: false, error: "invalid_arguments" }
        : await sendOaSmoke(store, config, liveOa, wiring, uid, readFileSync(0, "utf8"),
            option === "--approve-consent", () => smokeReceipt);
    console.log(JSON.stringify(result));
    if (!result.ok) process.exitCode = 1;
  },
  "oa-smoke-latest-uid": () => {
    // This is an operator discovery command and never sends.
    if (!process.env.WEB_ORIGIN || process.env.OA_ONBOARD_ENABLED !== "1") throw Error("OA_ONBOARD_REQUIRED");
    const oa = liveOa || createLiveOa(readOa({ ...process.env, OA_WEBHOOK_INGRESS: "external" }), store, postgres);
    return (async () => {
      try {
        const uid = latestSmokeUid(oa);
        if (!uid) throw Error("OA_SMOKE_INBOX_EMPTY");
        console.log(uid);
      } finally { if (oa !== liveOa) await oa.close(); }
    })();
  },
  "oa-install": async () => {
    if (!liveOa) throw Error("OA_LIVE_REQUIRED");
    const { access_token, refresh_token, expires_in, issued_at } = input();
    if (typeof access_token !== "string" || !access_token.trim() || typeof refresh_token !== "string" ||
      !refresh_token.trim() || !Number.isSafeInteger(issued_at) || issued_at <= 0 || issued_at > Date.now() ||
      !Number.isSafeInteger(Number(expires_in)) || Number(expires_in) < 1) throw Error("OA_INVALID_TOKEN_PAIR");
    await liveOa.tokens.install({ access: access_token, refresh: refresh_token, seconds: Number(expires_in) }, issued_at);
  },
  stop: () => {
    const agent = process.argv[3] ?? "global";
    if (agent !== "global" && !isAgent(agent)) throw Error("INVALID_AGENT");
    store.stop(agent, true);
  },
  resume: () => {
    const agent = process.argv[3] ?? "global";
    if (agent !== "global" && !isAgent(agent)) throw Error("INVALID_AGENT");
    store.stop(agent, false);
  },
  consent: () => {
    const { target, expires, retain, respond, send, ads, displayedText, policyVersion, evidence } = input();
    if (typeof target !== "string" || !target || !Number.isSafeInteger(expires) ||
      [retain, respond, send, ads].some(v => typeof v !== "boolean") ||
      typeof displayedText !== "string" || !displayedText.trim() || typeof policyVersion !== "string" || !policyVersion.trim() ||
      !evidence || typeof evidence !== "object" || Array.isArray(evidence) || !Object.keys(evidence).length) throw Error("INVALID_CONSENT");
    store.consent(store.hash(target), expires, retain, respond, send, ads, { displayedText, policyVersion, evidence });
  },
  export: () => console.log(JSON.stringify(store.exportCustomer(String(input().target)))),
  delete: () => store.deleteCustomer(String(input().target)),
  catalogue: () => store.knowledge.add(input()),
  notices: () => console.log(JSON.stringify(store.db.prepare("SELECT * FROM notices ORDER BY at DESC LIMIT 50").all())),
};
if (command !== "serve") {
  if (!Object.hasOwn(commands, command)) throw Error("INVALID_COMMAND");
  try { await commands[command](); }
  finally { store.db.close(); await liveOa?.close(); }
} else {
  const active = mode === "subiz" ? await setupChannels(store, readRoutes(), smokeOnly) : undefined;
  if (active && !smokeOnly && !(await active.subiz.authenticate()).ok) throw Error("SUBIZ_AUTH_FAILED");
  const webOrigin = process.env.WEB_ORIGIN;
  const oa = liveOa ?? (mode === "oa" ? (() => {
    const { OA_APP_ID, OA_ID, OA_APP_SECRET, OA_WEBHOOK_SECRET, OA_ENVELOPE_KEY, OA_FIXTURE_ENDPOINT } = process.env;
    if (!OA_APP_ID || !OA_ID || !OA_APP_SECRET || !OA_WEBHOOK_SECRET || !/^[a-f0-9]{64}$/i.test(OA_ENVELOPE_KEY ?? "")) {
      throw Error("OA_CONFIGURATION_REQUIRED");
    }
    let endpoint: string;
    if (OA_FIXTURE_ENDPOINT) {
      const url = new URL(OA_FIXTURE_ENDPOINT);
      if (!smokeOnly || url.protocol !== "http:" || url.hostname !== "127.0.0.1" || url.origin !== OA_FIXTURE_ENDPOINT) {
        throw Error("OA_INVALID_FIXTURE_ENDPOINT");
      }
      endpoint = url.origin + "/v3.0/oa/message/cs";
    } else throw Error("OA_FIXTURE_ENDPOINT_REQUIRED");
    const account = { appId: OA_APP_ID, oaId: OA_ID, webhookSecret: OA_WEBHOOK_SECRET };
    const box = new Envelope(Buffer.from(OA_ENVELOPE_KEY!, "hex"));
    const pool = new Pool(postgres);
    const tokens = new OaTokens(pool, box, accountScope(account), account.appId, OA_APP_SECRET,
      endpoint ? OA_FIXTURE_ENDPOINT + "/v4/oa/access_token" : undefined);
    const monthlyQuota = Number(process.env.OA_MONTHLY_QUOTA || "500");
    const channel = new OaRuntimeChannel(new OaAdapter(store, box, tokens, account, OA_APP_SECRET,
      { endpoint, allowAfter48h: true, monthlyQuota, allowedUids: wiring.smokeAllowlist }));
    return { channel, account, envelope: box, close: () => pool.end(), webhook: oaWebhook(new OaInbox(pool, store, box, account)) };
  })() : undefined);
  const channel = oa?.channel ?? active?.channel ?? new MockChannel();
  const provider = liveProvider(wiring, config);
  const schedule: Schedule[] = process.env.SCHEDULE_PATH ? JSON.parse(readFileSync(process.env.SCHEDULE_PATH, "utf8")) : [];
  if (!Array.isArray(schedule) || schedule.some(task => !task || !task.key || !task.target ||
    typeof task.key !== "string" || !/^[a-zA-Z0-9_-]{1,80}$/.test(task.key) ||
    typeof task.target !== "string" || !Number.isSafeInteger(task.at) ||
    !(task.agent === "campaign" ? task.kind === "advertising" : task.agent === "community" &&
      ["group_post", "group_create", "group_moderate"].includes(task.kind)) ||
    (active && task.kind === "group_create" && (!Array.isArray(task.memberIds) || !task.memberIds.length ||
      !task.memberIds.every(member => typeof member === "string" && /^[A-Za-z0-9_-]{1,180}$/.test(member)))) ||
    (task.kind === "group_moderate" ? typeof task.message !== "string" :
      typeof task.text !== "string" || !task.text.trim() || task.text.length > config.scheduling.maxText)) ||
    new Set(schedule.map(task => task.key)).size !== schedule.length) throw Error("INVALID_SCHEDULE");
  const runtime = new Runtime(store, channel, provider, config, Date.now, schedule, !!(webOrigin && oa));
  const hooks = active && webhookHandler(active.subiz, active.bot, smokeOnly ? undefined : event => {
    // The signed inbound event is already durable. Apply opt-out without waiting for the next poll.
    runtime.ingest(event);
  });
  let lastTick = Date.now();
  const interval = smokeOnly && !liveOa ? undefined : setInterval(() => {
    void Promise.resolve().then(() => { active?.journal.prune(); return runtime.tick(); }).then(done => { if (done) lastTick = Date.now(); }, () => {
      store.notice("runtime-error", Date.now(), "Một chu kỳ xử lý không hoàn tất.");
    });
  }, config.scheduling.pollMs);
  const pruneSmoke = smokeOnly && active ? setInterval(() => active.journal.prune(), config.scheduling.pollMs) : undefined;
  const operatorPassword = process.env.OPERATOR_PASSWORD;
  if (operatorPassword && (operatorPassword.length < 24 || operatorPassword.includes(":"))) throw Error("INVALID_OPERATOR_PASSWORD");
  const operatorHandler = operator(store, operatorPassword);
  const rate = Number(process.env.WEB_USD_VND || "0");
  if (!Number.isFinite(rate) || rate < 0 || rate > 1000000) throw Error("INVALID_WEB_USD_VND");
  const inboxSource = wiring.oa ?? (oa && "envelope" in oa ? oa : undefined) ??
    (onboarding ? readOa({ ...process.env, OA_WEBHOOK_INGRESS: "external" }) : undefined);
  const inboxChannel = oa?.channel ?? onboarding?.channel;
  const loopbackFixture = !liveOa && mode === "oa";
  const inboxMode = smokeOnly && !loopbackFixture ? "smoke_only" : oa ? "active" : "oa_unavailable";
  const inbox = webOrigin && inboxSource && inboxChannel ? oaWebInbox(store, config,
    { account: inboxSource.account, envelope: inboxSource.envelope }, inboxChannel, inboxMode) : undefined;
  const inboxTimer = inbox && setInterval(() => {
    try { inbox.project(); }
    catch { console.warn("OA inbox projection failed"); }
  }, 3000);
  const web = webOrigin ? webApi(store, config, webOrigin, oa, rate, {
    stop: () => closeNickAudit?.stop(),
    connected: () => closeNickAudit?.connected() ?? false,
  }, onboarding, inbox) : undefined;
  const server = createServer((req, res) => {
    void handle(req, res).catch(() => { if (!res.headersSent) res.writeHead(503); res.end(); });
  });
  const handle = async (req: import("node:http").IncomingMessage, res: import("node:http").ServerResponse) => {
    if (oa?.webhook && req.url === "/webhooks/zalo-oa") return oa.webhook(req, res);
    if (web && await web(req, res)) return;
    if (web && process.env.WEB_DIST && await serveWebAssets(req, res, process.env.WEB_DIST)) return;
    if (hooks && await hooks(req, res)) return;
    if (req.url !== "/health" || (req.method !== "GET" && req.method !== "HEAD")) {
      void operatorHandler(req, res).catch(() => { if (!res.headersSent) res.writeHead(500); res.end(); });
      return;
    }
    const okay = smokeOnly || Date.now() - lastTick < 4 * config.scheduling.pollMs;
    res.writeHead(okay ? 200 : 503, { "content-type": "application/json" }).end(JSON.stringify({
      ready: okay, channel: oa ? "oa" : mode, oaMode: wiring.oaMode, aiMode: wiring.aiMode, smokeOnly, stopped: store.stopped("global"),
    }));
  };
  const closeNickAudit = process.env.NICK_WORKER_AUTH && !smokeOnly
    ? attachNickAudit(server, store.db, process.env.NICK_WORKER_AUTH, webOrigin ? () => store.stopped("nick") : undefined) : undefined;
  const port = Number(process.env.HTTP_PORT || "8080");
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw Error("INVALID_HTTP_PORT");
  server.listen(port, process.env.HTTP_BIND === "container" ? "0.0.0.0" : "127.0.0.1");
  process.once("SIGTERM", () => {
    closeNickAudit?.();
    clearInterval(interval);
    clearInterval(pruneSmoke);
    clearInterval(inboxTimer);
    server.close(() => { store.db.close(); void Promise.all([oa?.close(), onboarding !== liveOa ? onboarding?.close() : undefined]).finally(() => process.exit(0)); });
  });
}
