import { Pool, type PoolConfig } from "pg";
import { id } from "./adapters/common.js";
import { OaAdapter, OaRuntimeChannel } from "./channels/oa/adapter.js";
import { Envelope } from "./channels/oa/crypto.js";
import { OaTokens } from "./channels/oa/tokens.js";
import { accountScope, OaInbox, oaWebhook, oaWebhookMaxSkewMs } from "./channels/oa/webhook.js";
import type { Config } from "./config.js";
import { ClaudeProvider, FakeProvider } from "./provider.js";
import { loginClientAddress } from "./web/login-limits.js";
import type { Store } from "./store.js";

// https://www.hostinger.com/support/what-is-hostinger-ai-router-and-how-to-get-started/
const router = "https://router.hostinger.com/v1";
type Env = NodeJS.ProcessEnv;

function mode(env: Env, name: string) {
  const value = env[name] ?? "mock";
  if (value !== "mock" && value !== "live") throw Error("INVALID_" + name);
  return value;
}

function required(env: Env, name: string) {
  const value = env[name]?.trim();
  if (!value) throw Error("MISSING_" + name);
  return value;
}

function bounded(env: Env, name: string, fallback: number, min: number, max: number, integer = false) {
  const value = env[name] === undefined ? fallback : Number(required(env, name));
  if (!Number.isFinite(value) || value < min || value > max || (integer && !Number.isSafeInteger(value))) {
    throw Error("INVALID_" + name);
  }
  return value;
}

export function readLiveWiring(env: Env, config: Config, smokeOnly: boolean, channelMode: string) {
  const oaMode = mode(env, "OA_MODE");
  const aiMode = mode(env, "AI_MODE");
  const smokeAllowlist = !env.SMOKE_ALLOWLIST ? undefined :
    new Set(required(env, "SMOKE_ALLOWLIST").split(",").map(value => value.trim()));
  if (smokeAllowlist && [...smokeAllowlist].some(uid => !id(uid))) throw Error("INVALID_SMOKE_ALLOWLIST");
  if ((oaMode === "live" && (!["mock", "oa"].includes(channelMode) || (smokeOnly && !smokeAllowlist))) ||
      (smokeAllowlist && channelMode === "subiz")) throw Error("OA_LIVE_CHANNEL_CONFIGURATION");
  if (aiMode === "live" && smokeOnly) throw Error("AI_LIVE_DISABLED_IN_SMOKE");
  const oa = oaMode === "live" ? readOa(env, smokeAllowlist) : undefined;
  const aiKey = aiMode === "live" ? configureAi(env, config.budget) : undefined;
  return { oaMode, aiMode, oa, aiKey, smokeOnly, smokeAllowlist };
}

export function readOa(env: Env, allowedUids?: ReadonlySet<string>) {
  const account = { appId: required(env, "ZALO_APP_ID"), oaId: required(env, "ZALO_OA_ID"),
    webhookSecret: required(env, "ZALO_WEBHOOK_SECRET") };
  const appSecret = required(env, "ZALO_APP_SECRET");
  const key = required(env, "ZALO_OA_ENCRYPTION_KEY");
  if (!id(account.appId) || !id(account.oaId) || !/^[0-9a-f]{64}$/i.test(key)) throw Error("INVALID_ZALO_OA_CONFIGURATION");
  const ingress = env.OA_WEBHOOK_INGRESS ?? "embedded";
  if (ingress !== "embedded" && ingress !== "external") throw Error("INVALID_OA_WEBHOOK_INGRESS");
  return { account, appSecret, envelope: new Envelope(Buffer.from(key, "hex")), ingress, allowedUids,
    maxSkewMs: oaWebhookMaxSkewMs(env.OA_WEBHOOK_MAX_SKEW_SECONDS),
    allowAfter48h: env.OA_ALLOW_AFTER_48H === "1",
    monthlyQuota: bounded(env, "OA_MONTHLY_QUOTA", 500, 0, Number.MAX_SAFE_INTEGER, true),
    allowPaidOverflow: env.OA_ALLOW_PAID_OVERFLOW === "1" };
}

function configureAi(env: Env, budget: Config["budget"]) {
  const key = required(env, "AI_ROUTER_API_KEY");
  if (env.AI_ROUTER_BASE_URL && env.AI_ROUTER_BASE_URL !== router) throw Error("INVALID_AI_ROUTER_BASE_URL");
  const models = [...new Set(required(env, "AI_MODEL_ALLOWLIST").split(",").map(value => value.trim()))];
  if (models.some(model => !Object.hasOwn(budget.models, model))) throw Error("AI_MODEL_UNPRICED");
  const assignments = Object.entries(budget.byAgent) as [keyof typeof budget.byAgent, string][];
  for (const [agent, defaultModel] of assignments) {
    const configured = env["MODEL_" + agent.toUpperCase()];
    const model = configured ?? (models.includes(defaultModel) ? defaultModel : models[0]);
    if (!models.includes(model)) throw Error("AI_MODEL_NOT_ALLOWED");
    budget.byAgent[agent] = model;
  }
  budget.provider = "anthropic-compatible";
  budget.allowedModels = models;
  budget.creditUsd = bounded(env, "AI_ROUTER_CREDIT_USD", budget.creditUsd, 0.01, 5000);
  budget.stopUsd = bounded(env, "AI_ROUTER_MONTHLY_USD", budget.stopUsd, 0.01, budget.creditUsd);
  budget.compatibleDailyUsd = bounded(env, "AI_ROUTER_DAILY_USD", NaN, 0.01, budget.stopUsd);
  budget.compatibleRateMultiplier = bounded(env, "AI_ROUTER_RATE_MULTIPLIER", NaN, 1, 100);
  budget.maxEstimatedInputTokens = bounded(env, "AI_MAX_INPUT_TOKENS", 18_000, 1, budget.maxEstimatedInputTokens, true);
  budget.maxOutputTokens = bounded(env, "AI_MAX_OUTPUT_TOKENS", budget.maxOutputTokens, 1, budget.maxOutputTokens, true);
  budget.dailyTokens = bounded(env, "AI_DAILY_TOKENS", NaN, 1, 1_000_000_000, true);
  budget.monthlyTokens = bounded(env, "AI_MONTHLY_TOKENS", NaN, budget.dailyTokens, 1_000_000_000, true);
  budget.manualReviewOnBudget = true;
  return key;
}

export function liveProvider(wiring: ReturnType<typeof readLiveWiring>, config: Config, fetcher = fetch) {
  if (wiring.aiKey) return new ClaudeProvider(wiring.aiKey, config.budget, fetcher, router);
  // Normal live OA cannot generate automatic replies from synthetic decisions.
  return new FakeProvider(wiring.oa && !wiring.smokeOnly ? () => "none" : undefined);
}

export function createLiveOa(settings: ReturnType<typeof readOa>, store: Store, postgres: PoolConfig, onSend?: ConstructorParameters<typeof OaRuntimeChannel>[1]) {
  const pool = new Pool({ ...postgres, max: 4, connectionTimeoutMillis: 1000,
    statement_timeout: 6500, query_timeout: 7000 });
  const ingressPool = settings.ingress === "embedded" ? new Pool({ ...postgres, max: 4,
    connectionTimeoutMillis: 650, statement_timeout: 1000, query_timeout: 1250 }) : undefined;
  const { account, appSecret, envelope } = settings;
  const tokens = new OaTokens(pool, envelope, accountScope(account), account.appId, appSecret);
  const channel = new OaRuntimeChannel(new OaAdapter(store, envelope, tokens, account, appSecret, settings), onSend);
  const clientAddress = loginClientAddress(process.env.TRUSTED_PROXY);
  const webhook = ingressPool ? oaWebhook(new OaInbox(ingressPool, store, envelope, account, Date.now, settings.maxSkewMs),
    request => clientAddress(request.socket.remoteAddress, request.headers["x-forwarded-for"])) : undefined;
  return { channel, account, webhook, tokens, appSecret, close: async () => { await Promise.all([pool.end(), ingressPool?.end()]); } };
}
