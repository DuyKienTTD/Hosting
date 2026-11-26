import { createHash, timingSafeEqual } from "node:crypto";
import type { IncomingMessage, ServerResponse } from "node:http";
import { UnsupportedChannel, type Request, type Result, type Contact } from "../../channel.js";
import { classifyOptOut } from "../../opt-out.js";
import { Guard } from "../../guard.js";
import type { Config } from "../../config.js";
import type { Store } from "../../store.js";

export const botWebhookPath = "/webhooks/zalo-bot";
const id = (value: unknown): value is string => typeof value === "string" && /^[A-Za-z0-9_.-]{1,180}$/.test(value);
const hash = (value: string) => createHash("sha256").update(value).digest();
const maxBody = 16 * 1024;

export function readBot(env: NodeJS.ProcessEnv, smokeOnly: boolean) {
  const mode = env.BOT_MODE ?? "mock";
  if (mode === "mock") return;
  if (mode !== "live") throw Error("INVALID_BOT_MODE");
  const token = env.ZALO_BOT_TOKEN ?? "";
  const secret = env.ZALO_BOT_WEBHOOK_SECRET ?? "";
  const account = env.ZALO_BOT_ID ?? "";
  const peers = new Set((env.BOT_SMOKE_ALLOWLIST ?? "").split(",").map(x => x.trim()).filter(Boolean));
  if (!/^[A-Za-z0-9:_-]{1,256}$/.test(token) || !/^[A-Za-z0-9_-]{8,256}$/.test(secret) ||
    !id(account) || [...peers].some(peer => !id(peer))) throw Error("BOT_CONFIGURATION_REQUIRED");
  return { token, secret, account, peers, smokeOnly };
}

export class BotPilot extends UnsupportedChannel {
  constructor(private settings: NonNullable<ReturnType<typeof readBot>>, private store: Store,
    private config: Config, private fetcher = fetch, private clock = Date.now) { super(); }

  private target(peer: string) { return `bot:${this.settings.account}:${peer}`; }

  private async call(method: string, body: object) {
    const response = await this.fetcher(`https://bot-api.zaloplatforms.com/bot${this.settings.token}/${method}`, {
      method: "POST", redirect: "error", signal: AbortSignal.timeout(3500),
      headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    });
    const json = await response.json();
    return response.ok && json?.ok === true ? json.result : undefined;
  }

  private peer(target: string) {
    const prefix = this.target("");
    const peer = target.slice(prefix.length);
    return target.startsWith(prefix) && id(peer) ? peer : undefined;
  }

  private allowed(target: string) {
    const peer = this.peer(target);
    return !!peer && !this.store.stopped("bot") && this.settings.smokeOnly && this.settings.peers.has(peer);
  }

  override getContact = async (req?: Request): Promise<Result<Contact>> => req
    ? { ok: true, value: { id: req.target, friend: !!this.peer(req.target) } }
    : { ok: false, error: "invalid_input" };

  override sendMessage = async (req?: Request): Promise<Result> => {
    if (!req || !this.allowed(req.target) || this.store.contact(this.store.hash(req.target), this.clock())?.opted_out || !req.text?.trim() || [...req.text].length > 2000) {
      return { ok: false, error: "policy_denied" };
    }
    try {
      const receipt = await this.call("sendMessage", { chat_id: this.peer(req.target), text: req.text });
      if (id(receipt?.message_id)) return { ok: true, value: undefined };
    } catch { /* ambiguous transport outcomes never get retried */ }
    return { ok: false, error: "unknown_delivery" };
  };

  async reply(peer: unknown, text: unknown) {
    if (!id(peer) || typeof text !== "string" || !text.trim() || [...text].length > 2000) return "invalid_input";
    if (this.store.stopped("bot")) return "stopped";
    const target = this.target(peer);
    if (!this.allowed(target)) return "policy_denied";
    const digest = this.store.hash(target);
    const inbound = this.store.db.prepare("SELECT id FROM inbound WHERE target=? ORDER BY received DESC,id DESC LIMIT 1").get(digest);
    if (this.store.contact(digest, this.clock())?.opted_out) return "consent";
    if (!inbound) return "reply_denied";
    return new Guard(this.store, this, this.config, this.clock).dispatch({
      id: `bot-reply:${inbound.id}`, origin: String(inbound.id), agent: "support", kind: "reply", target, text,
      revision: this.store.policy(digest, "support", this.clock()).revision, epoch: this.store.setting("epoch"),
    });
  }

  private record(body: unknown) {
    if (!body || typeof body !== "object" || !("event_name" in body) || body.event_name !== "message.text.received" ||
      !("message" in body) || !body.message || typeof body.message !== "object") return;
    const m = body.message as { message_type?: unknown; message_id?: unknown; date?: number; text?: unknown;
      chat?: { chat_type?: unknown; id?: unknown }; from?: { id?: unknown; is_bot?: unknown } };
    const now = this.clock();
    if (m.message_type !== "CHAT_TEXT" || m.chat?.chat_type !== "PRIVATE" || !id(m.chat.id) ||
      m.from?.id !== m.chat.id || m.from.is_bot !== false || !id(m.message_id) ||
      typeof m.date !== "number" || !Number.isSafeInteger(m.date) || m.date <= 0 || m.date > now ||
      m.date < now - this.config.scheduling.maxInboundAgeMs ||
      typeof m.text !== "string" || !m.text.trim() || [...m.text].length > 2000) return;
    const peer = m.chat.id, at = m.date, bodyText = m.text;
    const rawTarget = this.target(peer);
    const target = this.store.hash(rawTarget);
    const event = this.store.eventKey(rawTarget, rawTarget, m.message_id);
    this.store.atomic(() => {
      if (!this.store.db.prepare("INSERT OR IGNORE INTO inbound VALUES(?,?,?)").run(event, target, at).changes) return;
      const optOut = classifyOptOut(bodyText, this.config.advertising);
      if (optOut === "stop") this.store.optOut(target);
      if (optOut === "review") this.store.pauseAdsForReview(target, event);
      if (optOut === "none" && this.store.policy(target, "support", now).retain) {
        this.store.retainMessage(target, rawTarget, "bot", event, bodyText, at);
      }
    });
  }

  webhook = async (req: IncomingMessage, res: ServerResponse) => {
    const finish = (status: number) => { res.writeHead(status).end(); };
    if (req.method !== "POST") { res.setHeader("Allow", "POST"); return finish(405); }
    const secret = req.headers["x-bot-api-secret-token"];
    if (typeof secret !== "string" || !timingSafeEqual(hash(secret), hash(this.settings.secret))) return finish(403);
    if (Number(req.headers["content-length"]) > maxBody) return finish(413);
    const chunks: Buffer[] = [];
    let size = 0;
    for await (const chunk of req.iterator({ destroyOnReturn: false })) {
      const buffer = Buffer.from(chunk);
      size += buffer.length;
      if (size > maxBody) return finish(413);
      chunks.push(buffer);
    }
    let body: unknown;
    try { body = JSON.parse(Buffer.concat(chunks).toString("utf8")); } catch { return finish(400); }
    this.record(body);
    this.store.set(this.statusKey(), this.clock());
    return finish(200);
  };

  private statusKey() { return "bot-webhook:" + this.store.hash(this.settings.account); }

  status() {
    const verified = this.store.setting(this.statusKey());
    return this.store.stopped("bot") ? { state: "stopped", detail: "Zalo Bot live · STOP" }
      : verified ? { state: "online", detail: "Webhook đã xác thực lần cuối: " + new Date(verified).toISOString() }
      : { state: "offline", detail: "Live · đang chờ webhook xác thực" };
  }
}
