import { createServer } from "node:http";
import { chmodSync, readFileSync, renameSync, existsSync } from "node:fs";
import { backup } from "node:sqlite";
import { defaults, day } from "./config.js";
import { MockChannel } from "./channel.js";
import { ClaudeProvider, FakeProvider, isAgent } from "./provider.js";
import { Runtime, type Schedule } from "./runtime.js";
import { operator } from "./operator.js";
import { Store } from "./store.js";
import { readRoutes, setupChannels, webhookHandler } from "./adapters/setup.js";
import { smoke } from "./adapters/smoke.js";

process.umask(0o077);
const command = process.argv[2] ?? "serve";
const mode = process.env.CHANNEL_MODE ?? "mock";
const smokeOnly = process.env.CHANNEL_SMOKE_ONLY === "1";
const path = process.env.DB_PATH ?? "./runtime.sqlite";
const key = process.env.IDENTITY_KEY || (mode === "mock" && !process.env.ANTHROPIC_API_KEY ? "offline-fixture" : "");
const config = structuredClone(defaults);
config.advertising.enabled = process.env.ADS_ENABLED === "true";
const providerMode = process.env.AI_PROVIDER ?? "anthropic";
if (providerMode !== "anthropic" && providerMode !== "anthropic-compatible") throw Error("INVALID_AI_PROVIDER");
config.budget.provider = providerMode;
if (providerMode === "anthropic-compatible") {
  config.budget.compatibleDailyUsd = Number(process.env.AI_ROUTER_DAILY_USD);
  config.budget.compatibleRateMultiplier = Number(process.env.AI_ROUTER_RATE_MULTIPLIER);
}
const anchor = Number(process.env.CREDIT_CYCLE_START_DAY ?? config.budget.cycleStartDay);
if (!Number.isInteger(anchor) || anchor < 1 || anchor > 28 || key.length < 8 ||
  !["mock", "subiz"].includes(mode)) throw Error("INVALID_CONFIGURATION");
config.budget.cycleStartDay = anchor;
for (const agent of Object.keys(config.budget.byAgent) as (keyof typeof config.budget.byAgent)[]) {
  const model = process.env["MODEL_" + agent.toUpperCase()];
  if (model === undefined) continue;
  if (!Object.hasOwn(config.budget.models, model)) throw Error("MODEL_UNPRICED");
  config.budget.byAgent[agent] = model;
}
const store = new Store(path, key);
if (path !== ":memory:") chmodSync(path, 0o600);
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
    const { target, expires, retain, respond, send, ads } = input();
    if (typeof target !== "string" || !target || !Number.isSafeInteger(expires) ||
      [retain, respond, send, ads].some(v => typeof v !== "boolean")) throw Error("INVALID_CONSENT");
    store.consent(store.hash(target), expires, retain, respond, send, ads);
  },
  export: () => console.log(JSON.stringify(store.exportCustomer(String(input().target)))),
  delete: () => store.deleteCustomer(String(input().target)),
  catalogue: () => store.knowledge.add(input()),
  notices: () => console.log(JSON.stringify(store.db.prepare("SELECT * FROM notices ORDER BY at DESC LIMIT 50").all())),
  backup: async () => {
    const name = process.argv[3];
    if (!name) throw Error("BACKUP_PATH_REQUIRED");
    await backup(store.db, name);
    chmodSync(name, 0o600);
  },
};
if (command !== "serve") {
  if (!Object.hasOwn(commands, command)) throw Error("INVALID_COMMAND");
  try { await commands[command](); }
  finally { store.db.close(); }
} else {
  const active = mode === "subiz" ? await setupChannels(store, readRoutes(), smokeOnly) : undefined;
  if (active && !smokeOnly && !(await active.subiz.authenticate()).ok) throw Error("SUBIZ_AUTH_FAILED");
  const channel = active?.channel ?? new MockChannel();
  const compatible = providerMode === "anthropic-compatible";
  const claudeKey = compatible ? process.env.AI_ROUTER_API_KEY : process.env.ANTHROPIC_API_KEY;
  const base = compatible ? process.env.AI_ROUTER_BASE_URL : undefined;
  const enableClaude = process.env.CLAUDE_ENABLED === "1";
  if (enableClaude && (!claudeKey || process.env.CLAUDE_CREDIT_CONFIRMED !== "1" || smokeOnly)) {
    throw Error("CLAUDE_CREDIT_CONFIGURATION_REQUIRED");
  }
  if (enableClaude && compatible && (!base || process.env.AI_ROUTER_CREDIT_CONFIRMED !== "1" ||
    !(config.budget.compatibleDailyUsd > 0 && config.budget.compatibleDailyUsd <= 195) ||
    !(config.budget.compatibleRateMultiplier >= 1 && config.budget.compatibleRateMultiplier <= 100))) {
    throw Error("AI_ROUTER_BUDGET_CONFIGURATION_REQUIRED");
  }
  const provider = enableClaude && claudeKey ? new ClaudeProvider(claudeKey, config.budget, fetch, base) : new FakeProvider();
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
  const runtime = new Runtime(store, channel, provider, config, Date.now, schedule);
  const hooks = active && webhookHandler(active.subiz, active.bot, smokeOnly ? undefined : event => {
    // The signed inbound event is already durable. Apply opt-out without waiting for the next poll.
    runtime.ingest(event);
  });
  let lastTick = Date.now();
  const interval = smokeOnly ? undefined : setInterval(() => {
    void Promise.resolve().then(() => { active?.journal.prune(); return runtime.tick(); }).then(done => { if (done) lastTick = Date.now(); }, () => {
      store.notice("runtime-error", Date.now(), "Một chu kỳ xử lý không hoàn tất.");
    });
  }, config.scheduling.pollMs);
  const pruneSmoke = smokeOnly && active ? setInterval(() => active.journal.prune(), config.scheduling.pollMs) : undefined;
  const operatorPassword = process.env.OPERATOR_PASSWORD;
  if (operatorPassword && (operatorPassword.length < 24 || operatorPassword.includes(":"))) throw Error("INVALID_OPERATOR_PASSWORD");
  const operatorHandler = operator(store, operatorPassword);
  const server = createServer((req, res) => {
    void handle(req, res).catch(() => { if (!res.headersSent) res.writeHead(503); res.end(); });
  });
  const handle = async (req: import("node:http").IncomingMessage, res: import("node:http").ServerResponse) => {
    if (hooks && await hooks(req, res)) return;
    if (req.url !== "/health" || req.method !== "GET") {
      void operatorHandler(req, res).catch(() => { if (!res.headersSent) res.writeHead(500); res.end(); });
      return;
    }
    const okay = smokeOnly || Date.now() - lastTick < 4 * config.scheduling.pollMs;
    res.writeHead(okay ? 200 : 503, { "content-type": "application/json" }).end(JSON.stringify({
      ready: okay, channel: mode, smokeOnly, stopped: store.stopped("global"),
    }));
  };
  server.listen(8080, process.env.HTTP_BIND === "container" ? "0.0.0.0" : "127.0.0.1");
  let backingUp = false;
  const backupDir = process.env.BACKUP_DIR;
  const dailyBackup = async () => {
    if (!backupDir || backingUp) return;
    const file = backupDir + "/runtime-" + new Date().toISOString().slice(0, 10) + ".sqlite";
    if (existsSync(file)) return;
    backingUp = true;
    try {
      await backup(store.db, file + ".partial");
      chmodSync(file + ".partial", 0o600);
      renameSync(file + ".partial", file);
    } catch { store.notice("backup-error", Date.now(), "Sao lưu SQLite thất bại."); }
    finally { backingUp = false; }
  };
  if (backupDir) {
    void dailyBackup();
    setInterval(() => { void dailyBackup(); }, day / 24);
  }
  process.once("SIGTERM", () => {
    clearInterval(interval);
    clearInterval(pruneSmoke);
    server.close(() => process.exit(0));
  });
}
