import { createHmac, timingSafeEqual } from "node:crypto";
import { BaseAdapter, ChannelJournal, fail, id, ok } from "./common.js";
import type { ChannelEvent, Command, DeliveryReceipt, Result } from "./contract.js";

export type Direct = { contactId: string; conversationId: string; userId: string; profileId: string; friendUntil?: number };
export type SubizConfig = { accountId: string; agentId: string; channel: string; source: string; direct: Direct[] };
const origin = "https://api.subiz.com.vn";
export class SubizAdapter extends BaseAdapter {
  private scope: string;
  private readonly verified = new Map<string, number>();
  constructor(readonly config: SubizConfig, private journal: ChannelJournal, private fetcher = fetch, private clock = Date.now) {
    super();
    if (!config || ![config.accountId, config.agentId, config.channel, config.source].every(id) || !Array.isArray(config.direct) ||
      config.direct.some(row => !row || ![row.contactId, row.conversationId, row.userId, row.profileId].every(id) ||
        (row.friendUntil !== undefined && !Number.isSafeInteger(row.friendUntil))) ||
      ["contactId", "conversationId", "profileId", "userId"].some(key => new Set(config.direct.map(row => row[key as keyof Direct])).size !== config.direct.length)) {
      throw Error("INVALID_SUBIZ_ROUTE");
    }
    this.scope = "api:" + config.accountId + ":" + config.source;
  }
  private request(route: string, body?: object) {
    const token = process.env.SUBIZ_API_TOKEN;
    if (!token) throw Error("SUBIZ_AUTH_REQUIRED");
    return this.fetcher(origin + route, { method: body ? "POST" : "GET", redirect: "error", signal: AbortSignal.timeout(8000),
      headers: { Authorization: "Bearer " + token, "Content-Type": "application/json" }, body: body && JSON.stringify(body) });
  }
  private async response(r: Response, write: boolean) {
    if (r.status === 429) {
      const raw = r.headers.get("retry-after");
      const seconds = raw === null ? 60 : /^\d+$/.test(raw) ? Number(raw) : Math.ceil((Date.parse(raw) - this.clock()) / 1000);
      return fail("rate_limited", Number.isSafeInteger(seconds) ? Math.max(1, Math.min(seconds, 86_400)) : 60);
    }
    const body = await r.json().catch(() => null);
    if (r.status === 401 || r.status === 403 || (r.status === 400 &&
      [body?.code, body?.error?.code, body?.error_code].some(value =>
        typeof value === "string" && value.split(",").some(code => code.trim() === "access_deny")))) return fail("auth");
    if (r.ok && body && typeof body === "object") return ok(body);
    if ([400, 404, 422].includes(r.status)) return fail("invalid_input");
    return fail(write ? "unknown_delivery" : "temporary_failure");
  }
  async authenticate() {
    try {
      const result = await this.response(await this.request("/4.1/me"), false);
      return result.ok && (result.value.account_id !== this.config.accountId || result.value.id !== this.config.agentId) ? fail("auth") : result;
    } catch { return fail(process.env.SUBIZ_API_TOKEN ? "temporary_failure" : "auth"); }
  }
  async verifyConversation(route: Direct) {
    this.verified.delete(route.conversationId);
    try {
      const result = await this.response(await this.request("/4.0/conversations/" + route.conversationId), false);
      if (!result.ok) return result;
      const c = result.value;
      const users = Array.isArray(c.members) ? c.members.filter((m: { type?: string }) => m?.type === "user") : [];
      if (c.id !== route.conversationId || c.account_id !== this.config.accountId ||
        c.touchpoint?.channel !== this.config.channel || c.touchpoint?.source !== this.config.source ||
        c.touchpoint?.id !== route.profileId || users.length !== 1 || users[0].id !== route.userId || users[0].membership !== "active") {
        return fail("policy_denied");
      }
      this.verified.set(route.conversationId, this.clock() + 15_000);
      return ok(route);
    } catch { return fail(process.env.SUBIZ_API_TOKEN ? "temporary_failure" : "auth"); }
  }
  async history(conversationId: string) {
    if (!this.config.direct.some(route => route.conversationId === conversationId)) return fail("policy_denied");
    try {
      const r = await this.response(await this.request("/4.0/conversations/" + conversationId + "/messages?limit=100"), false);
      return r.ok && !Array.isArray(r.value) ? fail("temporary_failure") : r;
    } catch { return fail("temporary_failure"); }
  }
  async webhook(raw: Buffer, signature: string | undefined, onEvent?: (event: ChannelEvent) => void) {
    const secret = process.env.SUBIZ_WEBHOOK_SECRET;
    if (!secret || !signature?.startsWith("sha256=")) return 403;
    const candidates = signature.slice(7).split(",").map(value => value.trim());
    if (candidates.length > 2 || !candidates.every(s => /^[a-f0-9]{64}$/.test(s))) return 403;
    const digest = createHmac("sha256", secret).update(raw).digest();
    if (!candidates.some(s => timingSafeEqual(Buffer.from(s, "hex"), digest))) return 403;
    let body;
    try { body = JSON.parse(raw.toString("utf8")); } catch { return 400; }
    if (!Array.isArray(body?.events) || body.events.length > 200) return 400;
    const batch: { stream: string; event: ChannelEvent }[] = [];
    for (const item of body.events) {
      const m = item?.data?.message;
      const at = item?.event_time ?? item?.created;
      if (item?.account_id !== this.config.accountId || item?.type !== "message_sent" || item.by?.type !== "user" ||
        !id(item.id) || !Number.isSafeInteger(at) || Math.abs(at - this.clock()) > 86_400_000 ||
        (m?.is_internal !== undefined && m.is_internal !== false) ||
        m?.format !== "plaintext" || typeof m.text !== "string" || !m.text.trim() || m.text.length > 6000) continue;
      const route = this.config.direct.find(r => r.conversationId === m.conversation_id && r.userId === item.by.id);
      if (!route) continue;
      if (item.touchpoint && (item.touchpoint.channel !== this.config.channel || item.touchpoint.source !== this.config.source ||
        item.touchpoint.id !== route.profileId)) continue;
      batch.push({ stream: "direct", event: { version: 1, accountId: this.config.accountId, eventId: item.id,
        occurredAt: new Date(at).toISOString(), type: "messageReceived",
        payload: { messageId: item.id, senderId: route.contactId, thread: { kind: "direct", conversationId: route.conversationId }, text: m.text } } });
    }
    for (const event of this.journal.append(this.scope, batch)) onEvent?.(event);
    return 204;
  }
  override async receiveMessage(c: Command<"receiveMessage">) {
    if (c.accountId !== this.config.accountId) return fail("policy_denied");
    const page = this.journal.page(this.scope, "direct", c.payload);
    return page.ok ? ok({ ...page.value, items: page.value.items.filter((e): e is ChannelEvent<"messageReceived"> => e.type === "messageReceived") }) : page;
  }
  override async getContact(c: Command<"getContact">) {
    const route = this.config.direct.find(r => r.contactId === c.payload.contactId);
    if (c.accountId !== this.config.accountId || !route) return fail("policy_denied");
    const checked = await this.verifyConversation(route);
    if (!checked.ok) return checked;
    return ok({ contactId: route.contactId, friendship: route.friendUntil && route.friendUntil > this.clock() ? "accepted" as const : "unknown" as const });
  }
  override sendMessage(c: Command<"sendMessage">): Promise<Result<DeliveryReceipt>> {
    const route = this.config.direct.find(r => r.conversationId === c.payload.conversationId);
    if (c.accountId !== this.config.accountId || !route?.friendUntil || route.friendUntil <= this.clock()) return Promise.resolve(fail("policy_denied"));
    if (!id(c.idempotencyKey) || typeof c.payload.text !== "string" || !c.payload.text.trim() || c.payload.text.length > 2000) return Promise.resolve(fail("invalid_input"));
    if (!process.env.SUBIZ_API_TOKEN) return Promise.resolve(fail("auth"));
    return this.journal.write(this.scope, c, async () => {
      if ((this.verified.get(route.conversationId) ?? 0) <= this.clock()) return fail("policy_denied");
      const response = this.request("/4.1/conversations/" + route.conversationId + "/messages",
        { type: "message_sent", data: { message: { text: c.payload.text, format: "plaintext" } } });
      const result = await this.response(await response, true);
      if (!result.ok) return result;
      const event = result.value;
      return event.type === "message_sent" && event.account_id === c.accountId && id(event.id) &&
        event.data?.message?.conversation_id === route.conversationId
        ? ok({ providerMessageId: event.id, state: "accepted" as const }) : fail("unknown_delivery");
    });
  }
}
