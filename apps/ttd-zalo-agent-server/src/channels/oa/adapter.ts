import { createHmac } from "node:crypto";
import { BaseAdapter, ChannelJournal, fail, id, ok } from "../../adapters/common.js";
import type { ChannelEvent, Command, Result, Results } from "../../adapters/contract.js";
import { command } from "../../adapters/router.js";
import { UnsupportedChannel, type ChannelAdapter, type Event, type Request, type Result as RuntimeResult } from "../../channel.js";
import type { Store } from "../../store.js";
import { Envelope } from "./crypto.js";
import { type Access, OaTokens } from "./tokens.js";
import { accountScope, consultationWindow, freeWindow, inboxContext, type OaAccount, oaUid } from "./webhook.js";

type Dm = Extract<Event, { kind: "dm" | "group" }>;
const endpoint = "https://openapi.zalo.me/v3.0/oa/message/cs";

// https://developers.zalo.me/changelog/v240409-them-tinh-nang-kiem-tra-app-secret-proof-khi-goi-api-co-su-dung-access-token-7603
// https://github.com/zaloplatform/zalo-php-sdk/blob/6bacb1bea670ce1fa9f1ae616bbbfd92742e20aa/src/Zalo.php#L229-L234
export const appSecretProof = (access: string, appSecret: string) => createHmac("sha256", appSecret).update(access).digest("hex");

export class OaAdapter extends BaseAdapter {
  readonly accountId: string;
  private readonly scope: string;
  private readonly journal: ChannelJournal;
  private readonly prepared = new Map<string, { target: string; token: Access }>();

  constructor(private readonly store: Store, private readonly box: Envelope, private readonly tokens: OaTokens,
    private readonly account: OaAccount, private readonly appSecret: string,
    private readonly options: { endpoint?: string; allowAfter48h?: boolean; clock?: () => number } = {}) {
    super();
    this.scope = accountScope(account);
    if (!store.db.backend || this.scope !== tokens.scope || !id(account.appId) || !id(account.oaId) || !appSecret) {
      throw Error("OA_INVALID_ACCOUNT");
    }
    this.accountId = "oa:" + this.scope;
    this.journal = new ChannelJournal(store, () => this.now());
  }

  private now() { return this.options.clock?.() ?? Date.now(); }

  // https://docs.zaloplatforms.com/docs/OA/tin-nhan/tin-tu-van/dieu-kien-gui-tin-tu-van
  private eligible(target: string) {
    const row = this.store.db.prepare("SELECT interaction_at,withdrawn FROM oa_contacts WHERE scope=? AND target=?")
      .get(this.scope, this.store.hash(target));
    const age = this.now() - Number(row?.interaction_at ?? 0);
    return !!row && !row.withdrawn && age >= 0 && age < consultationWindow &&
      (age < freeWindow || this.options.allowAfter48h === true);
  }

  override localContact(accountId: string, target: string): Result<Results["getContact"]> {
    return accountId === this.accountId && oaUid(this.account, target) && this.eligible(target)
      ? ok({ contactId: target, friendship: "accepted" }) : fail("policy_denied");
  }

  override async getContact(c: Command<"getContact">) {
    const target = c.payload.contactId;
    const local = this.localContact(c.accountId, target);
    if (!local.ok) return local;
    // OAuth may block on another process. Resolve it before Guard's final
    // policy transaction so sendMessage can begin the HTTP request synchronously.
    try {
      const token = await this.tokens.current();
      for (const [key, entry] of this.prepared) {
        if (entry.token.expires <= this.now()) this.prepared.delete(key);
      }
      this.prepared.delete(c.idempotencyKey);
      if (this.prepared.size >= 256) this.prepared.delete(this.prepared.keys().next().value!);
      this.prepared.set(c.idempotencyKey, { target, token });
      return local;
    } catch { return fail("auth"); }
  }

  override async receiveMessage(c: Command<"receiveMessage">): Promise<Result<Results["receiveMessage"]>> {
    const cursor = Number(c.payload.cursor ?? 0);
    const limit = c.payload.limit ?? 100;
    if (c.accountId !== this.accountId || !Number.isSafeInteger(cursor) || cursor < 0 ||
      !Number.isInteger(limit) || limit < 1 || limit > 100) return fail("invalid_input");
    const rows = this.store.atomic(() => {
      this.store.db.prepare("UPDATE oa_inbox SET sealed=NULL WHERE scope=? AND sealed IS NOT NULL AND expires_at<=clock_timestamp()").run(this.scope);
      return this.store.db.prepare(`SELECT seq,event_id,encode(sealed,'base64') AS body
        FROM oa_inbox WHERE scope=? AND seq>? AND sealed IS NOT NULL ORDER BY seq LIMIT ?`)
        .all(this.scope, cursor, limit);
    });
    const items = rows.map((row): ChannelEvent<"messageReceived"> => {
      const eventId = String(row.event_id);
      const event = JSON.parse(this.box.open(Buffer.from(String(row.body), "base64"), inboxContext(this.scope, eventId))) as Dm;
      return { version: 1, accountId: this.accountId, eventId, occurredAt: new Date(event.at).toISOString(),
        type: "messageReceived", payload: { messageId: eventId, senderId: event.contact, text: event.text,
          thread: { kind: "direct", conversationId: event.thread } } };
    });
    return ok({ items, nextCursor: String(rows.at(-1)?.seq ?? cursor) });
  }

  override sendMessage(c: Command<"sendMessage">): Promise<Result<Results["sendMessage"]>> {
    const { conversationId: target, text } = c.payload;
    const uid = oaUid(this.account, target);
    if (!uid || c.accountId !== this.accountId || typeof text !== "string" || !text.trim() || [...text].length > 2000) {
      return Promise.resolve(fail("invalid_input"));
    }
    const prepared = this.prepared.get(c.idempotencyKey);
    this.prepared.delete(c.idempotencyKey);
    if (!this.eligible(target) || this.store.stopped("support") ||
      !this.store.db.prepare(`SELECT 1 FROM send_log WHERE id=? AND target=? AND agent='support'
        AND kind='reply' AND state='reserved'`).get(c.idempotencyKey, this.store.hash(target))) {
      return Promise.resolve(fail("policy_denied"));
    }
    if (!prepared || prepared.target !== target || prepared.token.expires <= this.now() ||
      !this.store.db.prepare("SELECT 1 FROM oa_access_generation WHERE scope=? AND generation=?")
        .get(this.scope, prepared.token.generation)) return Promise.resolve(fail("auth"));

    return this.journal.write(this.accountId, c, () => this.deliver(uid, text, prepared.token));
  }

  // https://docs.zaloplatforms.com/docs/OA/tin-nhan/tin-tu-van/gui-tin-tu-van-dang-van-ban
  // https://docs.zaloplatforms.com/docs/OA/phu-luc/ma-loi
  private async deliver(uid: string, text: string, token: Access): Promise<Result<Results["sendMessage"]>> {
    try {
      const response = await fetch(this.options.endpoint ?? endpoint, { method: "POST", redirect: "error", signal: AbortSignal.timeout(5000),
        headers: { access_token: token.value, appsecret_proof: appSecretProof(token.value, this.appSecret),
          "content-type": "application/json" },
        body: JSON.stringify({ recipient: { user_id: uid }, message: { text } }) });
      if (response.status >= 500) return fail("unknown_delivery");
      if (response.status === 401) {
        await this.tokens.invalidate(token.generation);
        return fail("auth");
      }
      if (response.status === 429) return fail("rate_limited");
      const output = await response.json();
      if (output?.error === -216 || output?.error === -220) {
        await this.tokens.invalidate(token.generation);
        return fail("auth");
      }
      if (output?.error === -242 || output?.error === -223) return fail("auth");
      if (output?.error === -211) return fail("rate_limited");
      if ([-200, -201, -210, -213, -244, -248].includes(output?.error)) return fail("policy_denied");
      if (!response.ok || output?.error !== 0 || !id(output.data?.message_id) || output.data?.user_id !== uid) {
        return fail("unknown_delivery");
      }
      return ok({ providerMessageId: output.data.message_id, state: "accepted" });
    } catch { return fail("unknown_delivery"); }
  }
}

function runtimeResult<T, U>(result: Result<T>, map: (value: T) => U): RuntimeResult<U> {
  return result.ok ? { ok: true, value: map(result.value) } : { ok: false, error: result.error.code };
}

/** Bound to the Runtime and its Guard. Keeps OA identity and channel metadata on ingestion. */
export class OaRuntimeChannel implements ChannelAdapter {
  private cursor: string | undefined;
  private next: string | undefined;
  constructor(private readonly adapter: OaAdapter) {}
  private readonly unsupported = new UnsupportedChannel();
  listGroups = this.unsupported.listGroups;
  readGroupMessages = this.unsupported.readGroupMessages;
  postToGroup = this.unsupported.postToGroup;
  createGroup = this.unsupported.createGroup;
  moderateGroup = this.unsupported.moderateGroup;
  sendFriendRequest = this.unsupported.sendFriendRequest;

  receiveMessage = async (request: Request): Promise<RuntimeResult<Event[]>> => {
    const result = await this.adapter.receiveMessage(command(this.adapter.accountId, request.key, "receiveMessage", { cursor: this.cursor }));
    if (result.ok) this.next = result.value.nextCursor;
    return runtimeResult(result, page => page.items.map(event => ({
      id: event.eventId, contact: event.payload.senderId, thread: event.payload.senderId,
      at: Date.parse(event.occurredAt), channel: "oa", kind: "dm", text: event.payload.text,
    })));
  };

  acknowledge(stream: "message" | "friend") { if (stream === "message") this.cursor = this.next; }

  onFriendAccepted = async (): Promise<RuntimeResult<Event[]>> => ({ ok: true, value: [] });

  localContact(request: Request) {
    if (request.thread && request.thread !== request.target) return { ok: false as const, error: "policy_denied" as const };
    return runtimeResult(this.adapter.localContact(this.adapter.accountId, request.target), value =>
      ({ id: value.contactId, friend: value.friendship === "accepted" }));
  }

  getContact = async (request: Request) => runtimeResult(await this.adapter.getContact(
    command(this.adapter.accountId, request.key, "getContact", { contactId: request.target })),
  value => ({ id: value.contactId, friend: value.friendship === "accepted" }));

  sendMessage = (request: Request) => this.adapter.sendMessage(
    command(this.adapter.accountId, request.key, "sendMessage", {
      conversationId: request.target, text: request.text ?? "",
    })).then(result => runtimeResult(result, () => undefined));
}
