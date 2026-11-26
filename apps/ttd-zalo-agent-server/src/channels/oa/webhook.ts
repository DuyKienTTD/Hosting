import { createHash, timingSafeEqual } from "node:crypto";
import type { IncomingMessage, ServerResponse } from "node:http";
import { createServer, type ServerOptions } from "node:https";
import type { Pool } from "pg";
import { id } from "../../adapters/common.js";
import type { Event } from "../../channel.js";
import type { Store } from "../../store.js";
import { Envelope } from "./crypto.js";

export const consultationWindow = 7 * 86_400_000;
export const freeWindow = 2 * 86_400_000;
export function oaWebhookMaxSkewMs(value?: string) {
  const seconds = value === undefined ? 300 : Number(value);
  const milliseconds = seconds * 1000;
  if (!Number.isSafeInteger(seconds) || seconds <= 0 || !Number.isSafeInteger(milliseconds)) {
    throw Error("INVALID_OA_WEBHOOK_MAX_SKEW_SECONDS");
  }
  return milliseconds;
}

const queueLifetime = 86_400_000;

export type OaAccount = { appId: string; oaId: string; webhookSecret: string };
export const accountScope = (account: OaAccount) => JSON.stringify([account.appId, account.oaId]);
const targetPrefix = (account: OaAccount) => `oa:${account.appId}:${account.oaId}:`;
export const oaTarget = (account: OaAccount, uid: string) => targetPrefix(account) + uid;
export function oaUid(account: OaAccount, target: string) {
  const uid = target.slice(targetPrefix(account).length);
  return target.startsWith(targetPrefix(account)) && id(uid) ? uid : undefined;
}
export const inboxContext = (scope: string, key: string) => JSON.stringify(["oa-inbox", scope, key]);

type OaEvent = { key: string; uid: string; at: number; kind: "message" | "follow" | "unfollow" | "user_withdraw" | "other"; text?: string };

// https://docs.zaloplatforms.com/docs/OA/webhook/tin-nhan/su-kien-nguoi-dung-gui-tin-nhan
// https://docs.zaloplatforms.com/docs/OA/webhook/quan-ly/su-kien-nguoi-dung-quan-tam-hay-bo-quan-tam-oa
// https://docs.zaloplatforms.com/docs/OA/webhook/quan-ly/su-kien-nguoi-dung-zalo-thuc-hien-quyen-chu-the-du-lieu
function verify(raw: Buffer, signature: string, account: OaAccount, now: number, maxSkewMs: number): OaEvent | number {
  let data;
  try { data = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(raw)); }
  catch { return 401; }
  const timestamp = String(data?.timestamp ?? "");
  const at = Number(timestamp);
  if (!/^\d{1,16}$/.test(timestamp) || !Number.isSafeInteger(at) || at <= 0) return 401;
  const mac = createHash("sha256").update(account.appId).update(raw).update(timestamp).update(account.webhookSecret).digest();
  if (!/^mac=[0-9a-f]{64}$/i.test(signature) || !timingSafeEqual(mac, Buffer.from(signature.slice(4), "hex"))) return 401;
  if (Math.abs(now - at) > maxSkewMs) return 401;
  const name = data.event_name;
  const incoming = typeof name === "string" && name.startsWith("user_send_");
  const oa = incoming ? data.recipient?.id : data.oa_id ?? data.recipient?.id;
  if (data.app_id !== account.appId || oa !== account.oaId) return 403;

  const kind = name === "user_send_text" ? "message" : name === "follow" || name === "unfollow" ||
    name === "user_withdraw" ? name : "other";
  const uid = incoming ? data.sender?.id : data.follower?.id ?? data.user_id;
  if (!id(name) || (kind !== "other" && !id(uid))) return 400;
  if (kind === "message" && (!id(data.message?.msg_id) || typeof data.message.text !== "string")) return 400;
  const sourceId = data.event_id ?? (incoming ? data.message?.msg_id : undefined);
  // Some OA events have no upstream event ID. Their signed fields form a stable key.
  const key = createHash("sha256").update(JSON.stringify(id(sourceId)
    ? [name, sourceId] : [name, uid, timestamp])).digest("hex");
  return { key, uid: id(uid) ? uid : "", at: Math.min(at, now), kind, text: kind === "message" ? data.message.text : undefined };
}

export class OaInbox {
  readonly scope: string;
  constructor(private readonly pool: Pool, private readonly identity: Pick<Store, "hash">, private readonly box: Envelope,
    private readonly account: OaAccount, private readonly clock = Date.now,
    private readonly maxSkewMs = oaWebhookMaxSkewMs()) {
    if (!id(account.appId) || !id(account.oaId) || !account.webhookSecret) throw Error("OA_INVALID_ACCOUNT");
    this.scope = accountScope(account);
  }

  async accept(raw: Buffer, signature: string, signal: AbortSignal) {
    const event = verify(raw, signature, this.account, this.clock(), this.maxSkewMs);
    if (typeof event === "number") return event;
    const contact = oaTarget(this.account, event.uid);
    const target = this.identity.hash(contact);
    const expiry = event.at + queueLifetime;
    let sealed: Buffer | null = null;
    if (event.text !== undefined && expiry > this.clock()) {
      const message: Event = { id: event.key, contact, thread: contact, at: event.at, channel: "oa", kind: "dm", text: event.text };
      sealed = this.box.seal(JSON.stringify(message), inboxContext(this.scope, event.key));
    }
    for (let attempt = 0; attempt < 2; attempt++) {
      if (signal.aborted) return 503;
      try {
        await this.pool.query("SELECT oa_accept_event($1,$2,$3,$4,$5,$6,$7)",
          [this.scope, event.key, target, event.at, event.kind, new Date(expiry), sealed]);
        return 200;
      } catch (error) {
        const code = (error as { code?: string })?.code;
        // Only retry failures Postgres confirms rolled back. The HTTP deadline
        // still governs both attempts. Zalo can replay the idempotent event.
        if (attempt !== 0 || (code !== "40001" && code !== "40P01")) return 503;
      }
    }
    return 503;
  }
}

// https://docs.zaloplatforms.com/docs/OA/webhook/tong-quan
export function oaWebhook(inbox: OaInbox, clientIp = (req: IncomingMessage) => req.socket.remoteAddress ?? "unknown") {
  const buckets = new Map<string, { count: number }>();
  let minute = -1;
  let dropped = 0;
  function admitDrop(req: IncomingMessage) {
    const current = Math.floor(Date.now() / 60_000);
    if (minute !== current) { minute = current; buckets.clear(); }
    const key = clientIp(req);
    let bucket = buckets.get(key);
    const overflow = !bucket && buckets.size >= 4096;
    if (!bucket && !overflow) {
      bucket = { count: 0 };
      buckets.set(key, bucket);
    }
    dropped++;
    if (Number.isInteger(Math.log2(dropped))) console.warn(JSON.stringify({ event: "oa_webhook_dropped", count: dropped }));
    return bucket && ++bucket.count <= 30 ? 200 : 429;
  }
  return (req: IncomingMessage, res: ServerResponse) => {
    const reply = (status: number) => {
      if (res.writableEnded || res.destroyed) return;
      res.writeHead(status, { "content-type": "application/json" });
      res.end(status === 200 ? '{"error":0}' : "{}");
    };
    if (req.url !== "/webhooks/zalo-oa") return reply(404);
    if (req.method !== "POST") return reply(405);
    const signature = req.headers["x-zevent-signature"];
    if (typeof signature !== "string") { req.resume(); return reply(admitDrop(req)); }
    const signal = AbortSignal.timeout(1750);
    signal.addEventListener("abort", () => reply(503), { once: true });
    const chunks: Buffer[] = [];
    let bytes = 0;
    req.on("data", (chunk: Buffer) => {
      if (res.writableEnded) return;
      bytes += chunk.length;
      if (bytes > 65_536) return reply(413);
      chunks.push(chunk);
    });
    req.on("end", () => {
      if (!res.writableEnded) void inbox.accept(Buffer.concat(chunks), signature, signal).then(status => {
        if (!res.writableEnded && !res.destroyed) reply(status === 401 ? admitDrop(req) : status);
      }, () => reply(503));
    });
    req.on("error", () => reply(400));
  };
}

export const createOaWebhookServer = (tls: ServerOptions, inbox: OaInbox) => createServer(tls, oaWebhook(inbox));
