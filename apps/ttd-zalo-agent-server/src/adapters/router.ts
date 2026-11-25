import { fail, validIdempotencyKey, type BaseAdapter } from "./common.js";
import type { ChannelAdapter as Contract, ChannelEvent, Command, Operation, Results, Result } from "./contract.js";
import type { ChannelAdapter, ChannelError, Contact, Event, Request } from "../channel.js";

export type Source = "api" | "bot" | "ui";
export type Capability = Partial<Record<Operation, Source>>;
type Adapter = { adapter: Contract & Partial<Pick<BaseAdapter, "localContact">>; operations: readonly Operation[] };
export class CapabilityRouter {
  constructor(readonly capabilities: Capability, private adapters: Partial<Record<Source, Adapter>>) {
    for (const [operation, source] of Object.entries(capabilities)) {
      if (!adapters[source]?.operations.includes(operation as Operation)) throw Error("UNSUPPORTED_CAPABILITY_CONFIG");
    }
  }
  localContact(accountId: string, contactId: string) {
    const source = this.capabilities.getContact;
    return source ? this.adapters[source]?.adapter.localContact?.(accountId, contactId) : fail("not_supported");
  }
  run<K extends Operation>(command: Command<K>): Promise<Result<Results[K]>> {
    if (!validIdempotencyKey(command.idempotencyKey)) return Promise.resolve(fail("invalid_input"));
    const source = this.capabilities[command.operation];
    const adapter = source && this.adapters[source]?.adapter;
    if (!adapter) return Promise.resolve(fail("not_supported"));
    // Command discriminant and result are paired by the contract's operation map.
    const method = adapter[command.operation] as (c: Command<K>) => Promise<Result<Results[K]>>;
    return method.call(adapter, command);
  }
}
export function command<K extends Operation>(accountId: string, idempotencyKey: string, operation: K,
  payload: import("./contract.js").CommandPayloads[K]): Command<K> {
  return { version: 1, accountId, idempotencyKey, operation, payload } as Command<K>;
}
export function runtimeEvent(e: ChannelEvent): Event {
  if (e.type === "friendAccepted") return { id: e.eventId, at: Date.parse(e.occurredAt),
    contact: e.payload.contactId, thread: e.payload.contactId, kind: "accepted" };
  const { thread, senderId, text } = e.payload;
  return { id: e.eventId, at: Date.parse(e.occurredAt), contact: senderId, text,
    ...(thread.kind === "direct" ? { kind: "dm" as const, thread: thread.conversationId } : { kind: "group" as const, thread: thread.groupId }) };
}
function convert<T, U>(r: Result<T>, map: (v: T) => U): import("../channel.js").Result<U> {
  return r.ok ? { ok: true, value: map(r.value) } : { ok: false, error: r.error.code as ChannelError };
}

export class RuntimeChannel implements ChannelAdapter {
  private cursors = new Map<string, string>();
  private next = new Map<string, string>();
  constructor(private router: CapabilityRouter, private account: string,
    private direct: ReadonlyMap<string, string>, private groupReads: readonly string[]) {}
  acknowledge(stream: "message" | "friend") {
    for (const [key, cursor] of this.next) if (key.startsWith(stream + ":")) {
      this.cursors.set(key, cursor);
      this.next.delete(key);
    }
  }
  private remember(stream: string, cursor: string | undefined) { if (cursor !== undefined) this.next.set(stream, cursor); }
  async receiveMessage(req: Request) {
    const events: Event[] = [];
    if (this.router.capabilities.receiveMessage) {
      const key = "message:direct";
      const r = await this.router.run(command(this.account, req.key, "receiveMessage", { cursor: this.cursors.get(key) }));
      if (!r.ok) return convert(r, () => []);
      this.remember(key, r.value.nextCursor);
      events.push(...r.value.items.map(runtimeEvent));
    }
    for (const group of this.groupReads) {
      const key = "message:group:" + group;
      const r = await this.router.run(command(this.account, req.key, "readGroupMessages", { groupId: group, cursor: this.cursors.get(key) }));
      if (!r.ok) return convert(r, () => []);
      this.remember(key, r.value.nextCursor);
      events.push(...r.value.items.map(runtimeEvent));
    }
    return { ok: true as const, value: events };
  }
  async onFriendAccepted(req: Request) {
    if (!this.router.capabilities.onFriendAccepted) return { ok: true as const, value: [] };
    const key = "friend:accepted";
    const r = await this.router.run(command(this.account, req.key, "onFriendAccepted", { cursor: this.cursors.get(key) }));
    if (r.ok) this.remember(key, r.value.nextCursor);
    return convert(r, v => v.items.map(runtimeEvent));
  }
  localContact(req: Request) {
    if (req.thread && this.direct.get(req.target) !== req.thread) return { ok: false as const, error: "policy_denied" as const };
    const r = this.router.localContact(this.account, req.target);
    return r && convert(r, v => ({ id: v.contactId, friend: v.friendship === "accepted" }));
  }
  async getContact(req: Request): Promise<import("../channel.js").Result<Contact>> {
    const r = await this.router.run(command(this.account, req.key, "getContact", { contactId: req.target }));
    return convert(r, v => ({ id: v.contactId, friend: v.friendship === "accepted" }));
  }
  async sendMessage(req: Request) {
    const conversationId = this.direct.get(req.target);
    if (!conversationId || (req.thread && req.thread !== conversationId)) return convert(fail("policy_denied"), () => undefined);
    return convert(await this.router.run(command(this.account, req.key, "sendMessage", { conversationId, text: req.text ?? "" })), () => undefined);
  }
  async listGroups(req: Request) {
    return convert(await this.router.run(command(this.account, req.key, "listGroups", {})), r => r.items.map(g => g.groupId));
  }
  async readGroupMessages(req: Request) {
    return convert(await this.router.run(command(this.account, req.key, "readGroupMessages", { groupId: req.target })), r => r.items.map(runtimeEvent));
  }
  async postToGroup(req: Request) {
    return convert(await this.router.run(command(this.account, req.key, "postToGroup", { groupId: req.target, text: req.text ?? "" })), () => undefined);
  }
  async createGroup(req: Request) {
    if (!req.memberIds?.length) return convert(fail("invalid_input"), () => undefined);
    return convert(await this.router.run(command(this.account, req.key, "createGroup", { name: req.text ?? "", memberIds: req.memberIds })), () => undefined);
  }
  async moderateGroup(req: Request) {
    return convert(await this.router.run(command(this.account, req.key, "moderateGroup",
      { action: "delete_message", groupId: req.target, messageId: req.message ?? "" })), () => undefined);
  }
  async sendFriendRequest(req: Request) {
    return convert(await this.router.run(command(this.account, req.key, "sendFriendRequest", { contactId: req.target })), () => undefined);
  }
}
