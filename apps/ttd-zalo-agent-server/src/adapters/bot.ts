import { createHash, timingSafeEqual } from "node:crypto";
import { BaseAdapter, ChannelJournal, fail, id, ok } from "./common.js";
import type { ChannelEvent, Command, DeliveryReceipt, Result } from "./contract.js";

const hash = (s: string) => createHash("sha256").update(s).digest();
export type BotConfig = { accountId: string; botId: string; groups: string[] };
export class ZaloBotAdapter extends BaseAdapter {
  private readonly scope: string;
  private enabled = false;
  constructor(readonly config: BotConfig, private journal: ChannelJournal, private fetcher = fetch) {
    super();
    if (![config.accountId, config.botId].every(id) || !Array.isArray(config.groups) || !config.groups.every(id)) {
      throw Error("INVALID_BOT_CONFIG");
    }
    this.scope = "bot:" + config.accountId + ":" + config.botId;
  }
  private async call(method: "getMe" | "sendMessage", body: object) {
    const token = process.env.ZALO_BOT_TOKEN;
    if (!token || !/^[A-Za-z0-9:_-]{1,256}$/.test(token)) return fail("auth");
    try {
      const response = await this.fetcher("https://bot-api.zaloplatforms.com/bot" + token + "/" + method, {
        method: "POST", redirect: "error", signal: AbortSignal.timeout(8000),
        headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
      });
      const json = await response.json().catch(() => null);
      const code = json?.error_code ?? response.status;
      if (response.ok && json?.ok === true && json.result) return ok(json.result);
      if (code === 429 || response.status === 429) return fail("rate_limited", 60);
      if ([401, 403, 404].includes(code)) return fail("auth");
      return fail(method === "sendMessage" ? "unknown_delivery" : "temporary_failure");
    } catch { return fail(method === "sendMessage" ? "unknown_delivery" : "temporary_failure"); }
  }
  async authenticate() {
    const result = await this.call("getMe", {});
    this.enabled = result.ok && result.value.id === this.config.botId && result.value.can_join_groups === true;
    return result.ok ? (this.enabled ? ok(true) : fail("not_supported")) : result;
  }
  webhook(raw: Buffer, header: string | undefined) {
    const secret = process.env.ZALO_BOT_WEBHOOK_SECRET;
    if (!secret || !header || !timingSafeEqual(hash(secret), hash(header))) return 403;
    if (!this.enabled) return 503;
    let body;
    try { body = JSON.parse(raw.toString("utf8")); } catch { return 400; }
    const m = body?.message;
    if (body?.event_name !== "message.text.received" || m?.message_type !== "CHAT_TEXT" ||
      m.chat?.chat_type !== "GROUP" || !this.config.groups.includes(m.chat.id) || !id(m.from?.id) || m.from.is_bot !== false ||
      !id(m.message_id) || !Number.isSafeInteger(m.date) || m.date < 0 || m.date > 8.64e15 ||
      typeof m.text !== "string" || !m.text.trim() || m.text.length > 6000) return 204;
    const event: ChannelEvent = { version: 1, accountId: this.config.accountId, eventId: m.message_id,
      occurredAt: new Date(m.date).toISOString(), type: "messageReceived",
      payload: { messageId: m.message_id, senderId: "bot-" + this.config.botId + "-" + m.from.id,
        thread: { kind: "group", groupId: m.chat.id }, text: m.text } };
    this.journal.append(this.scope, [{ stream: m.chat.id, event }]);
    return 204;
  }
  override async readGroupMessages(c: Command<"readGroupMessages">) {
    if (!this.enabled) return fail("not_supported");
    if (c.accountId !== this.config.accountId || !this.config.groups.includes(c.payload.groupId)) return fail("policy_denied");
    const page = this.journal.page(this.scope, c.payload.groupId, c.payload);
    return page.ok ? ok({ ...page.value, items: page.value.items.filter((e): e is ChannelEvent<"messageReceived"> => e.type === "messageReceived") }) : page;
  }
  override postToGroup(c: Command<"postToGroup">): Promise<Result<DeliveryReceipt>> {
    if (!this.enabled) return Promise.resolve(fail("not_supported"));
    if (c.accountId !== this.config.accountId || !this.config.groups.includes(c.payload.groupId)) return Promise.resolve(fail("policy_denied"));
    if (typeof c.payload.text !== "string" || !c.payload.text.trim() || c.payload.text.length > 2000) {
      return Promise.resolve(fail("invalid_input"));
    }
    return this.journal.write(this.scope, c, async () => {
      const result = await this.call("sendMessage", { chat_id: c.payload.groupId, text: c.payload.text });
      if (!result.ok) return result;
      return id(result.value.message_id) ? ok({ providerMessageId: result.value.message_id, state: "accepted" as const }) : fail("unknown_delivery");
    });
  }
}
