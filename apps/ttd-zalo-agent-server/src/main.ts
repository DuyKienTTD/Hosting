import { createServer } from "node:http";
import { chmodSync, readFileSync, renameSync, existsSync } from "node:fs";
import { backup } from "node:sqlite";
import { defaults, day } from "./config.js";
import { MockChannel, SubizAdapter } from "./channel.js";
import { ClaudeProvider, FakeProvider, isAgent } from "./provider.js";
import { Runtime, type Schedule } from "./runtime.js";
import { operator } from "./operator.js";
import { Store } from "./store.js";

process.umask(0o077);
const command = process.argv[2] ?? "serve";
const mode = process.env.CHANNEL_MODE ?? "mock";
const path = process.env.DB_PATH ?? "./runtime.sqlite";
const key = process.env.IDENTITY_KEY || (mode === "mock" && !process.env.ANTHROPIC_API_KEY ? "offline-fixture" : "");
const config = structuredClone(defaults);
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
  const channel = mode === "mock" ? new MockChannel() : new SubizAdapter();
  // The Subiz scaffold cannot enter live operation. Exercising real Claude requires explicit opt-in.
  const claudeKey = process.env.ANTHROPIC_API_KEY;
  const enableClaude = process.env.CLAUDE_ENABLED === "1";
  if (enableClaude && (!claudeKey || process.env.CLAUDE_CREDIT_CONFIRMED !== "1" || mode !== "mock")) {
    throw Error("CLAUDE_CREDIT_CONFIGURATION_REQUIRED");
  }
  const provider = enableClaude && claudeKey ? new ClaudeProvider(claudeKey, config.budget) : new FakeProvider();
  const schedule: Schedule[] = process.env.SCHEDULE_PATH ? JSON.parse(readFileSync(process.env.SCHEDULE_PATH, "utf8")) : [];
  if (!Array.isArray(schedule) || schedule.some(task => !task || !task.key || !task.target ||
    typeof task.key !== "string" || !/^[a-zA-Z0-9_-]{1,80}$/.test(task.key) ||
    typeof task.target !== "string" || !Number.isSafeInteger(task.at) ||
    !(task.agent === "campaign" ? task.kind === "advertising" : task.agent === "community" &&
      ["group_post", "group_create", "group_moderate"].includes(task.kind)) ||
    (task.kind === "group_moderate" ? typeof task.message !== "string" :
      typeof task.text !== "string" || !task.text.trim() || task.text.length > config.scheduling.maxText)) ||
    new Set(schedule.map(task => task.key)).size !== schedule.length) throw Error("INVALID_SCHEDULE");
  const runtime = new Runtime(store, channel, provider, config, Date.now, schedule);
  let lastTick = Date.now();
  const interval = setInterval(() => {
    void runtime.readChannel().catch(() => runtime.guard.failure());
    void runtime.tick(false).then(done => { if (done) lastTick = Date.now(); }, () => {
      store.notice("runtime-error", Date.now(), "Một chu kỳ xử lý không hoàn tất.");
    });
  }, config.scheduling.pollMs);
  const operatorPassword = process.env.OPERATOR_PASSWORD;
  if (operatorPassword && (operatorPassword.length < 24 || operatorPassword.includes(":"))) throw Error("INVALID_OPERATOR_PASSWORD");
  const operatorHandler = operator(store, operatorPassword);
  const server = createServer((req, res) => {
    if (req.url !== "/health" || req.method !== "GET") {
      void operatorHandler(req, res).catch(() => { if (!res.headersSent) res.writeHead(500); res.end(); });
      return;
    }
    const okay = Date.now() - lastTick < 4 * config.scheduling.pollMs;
    res.writeHead(okay ? 200 : 503, { "content-type": "application/json" }).end(JSON.stringify({
      ready: okay, channel: mode === "mock" ? "mock" : "not_supported", stopped: store.stopped("global"),
    }));
  }).listen(8080, process.env.HTTP_BIND === "container" ? "0.0.0.0" : "127.0.0.1");
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
    server.close(() => process.exit(0));
  });
}
