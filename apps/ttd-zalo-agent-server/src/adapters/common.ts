import { createCipheriv, createDecipheriv, randomBytes } from "node:crypto";
import type { ChannelAdapter, ChannelErrorCode, ChannelEvent, Command, Operation, PageRequest, Result, Results } from "./contract.js";
import type { Store } from "../store.js";

export const fail = (code: ChannelErrorCode, retryAfterSeconds?: number): { ok: false; error: { code: ChannelErrorCode; retryAfterSeconds?: number } } =>
  ({ ok: false, error: retryAfterSeconds === undefined ? { code } : { code, retryAfterSeconds } });
export const ok = <T>(value: T): Result<T> => ({ ok: true, value });
export const id = (v: unknown): v is string => typeof v === "string" && /^[A-Za-z0-9_-]{1,180}$/.test(v);
export const validIdempotencyKey = (v: unknown): v is string =>
  typeof v === "string" && v.length > 0 && [...v].length <= 128;
export const unsupported = async () => fail("not_supported");
export class BaseAdapter implements ChannelAdapter {
  localContact(_accountId: string, _contactId: string): Result<Results["getContact"]> | undefined { return undefined; }
  receiveMessage(_c: Command<"receiveMessage">): Promise<Result<Results["receiveMessage"]>> { return unsupported(); }
  sendMessage(_c: Command<"sendMessage">): Promise<Result<Results["sendMessage"]>> { return unsupported(); }
  listGroups(_c: Command<"listGroups">): Promise<Result<Results["listGroups"]>> { return unsupported(); }
  readGroupMessages(_c: Command<"readGroupMessages">): Promise<Result<Results["readGroupMessages"]>> { return unsupported(); }
  postToGroup(_c: Command<"postToGroup">): Promise<Result<Results["postToGroup"]>> { return unsupported(); }
  createGroup(_c: Command<"createGroup">): Promise<Result<Results["createGroup"]>> { return unsupported(); }
  moderateGroup(_c: Command<"moderateGroup">): Promise<Result<Results["moderateGroup"]>> { return unsupported(); }
  sendFriendRequest(_c: Command<"sendFriendRequest">): Promise<Result<Results["sendFriendRequest"]>> { return unsupported(); }
  onFriendAccepted(_c: Command<"onFriendAccepted">): Promise<Result<Results["onFriendAccepted"]>> { return unsupported(); }
  getContact(_c: Command<"getContact">): Promise<Result<Results["getContact"]>> { return unsupported(); }
}

export class ChannelJournal {
  constructor(private store: Store, private clock = Date.now, private ttl = 86_400_000) {
    store.db.exec(`
      CREATE TABLE IF NOT EXISTS adapter_inbox(seq INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL,
        event TEXT NOT NULL, stream TEXT NOT NULL, sender TEXT NOT NULL, expires INTEGER NOT NULL, sealed TEXT NOT NULL, UNIQUE(scope,event));
      CREATE INDEX IF NOT EXISTS adapter_inbox_page ON adapter_inbox(scope,stream,seq);
      CREATE TABLE IF NOT EXISTS adapter_writes(scope TEXT NOT NULL, key TEXT NOT NULL, fingerprint TEXT NOT NULL,
        result TEXT, PRIMARY KEY(scope,key));
      CREATE TABLE IF NOT EXISTS adapter_throttle(scope TEXT PRIMARY KEY,until INTEGER NOT NULL);
    `);
  }
  private key() { return Buffer.from(this.store.hash("channel-inbox-aes"), "hex"); }
  private seal(value: unknown) {
    const iv = randomBytes(12);
    const cipher = createCipheriv("aes-256-gcm", this.key(), iv);
    return Buffer.concat([iv, cipher.update(JSON.stringify(value)), cipher.final(), cipher.getAuthTag()]).toString("base64");
  }
  private open<T>(value: string): T {
    const bytes = Buffer.from(value, "base64");
    const decipher = createDecipheriv("aes-256-gcm", this.key(), bytes.subarray(0, 12));
    decipher.setAuthTag(bytes.subarray(-16));
    return JSON.parse(Buffer.concat([decipher.update(bytes.subarray(12, -16)), decipher.final()]).toString());
  }
  append(scope: string, batch: { stream: string; event: ChannelEvent }[]) {
    const db = this.store.db;
    return this.store.atomic(() => {
      const inserted: ChannelEvent[] = [];
      this.prune();
      const add = db.prepare("INSERT OR IGNORE INTO adapter_inbox(scope,event,stream,sender,expires,sealed) VALUES(?,?,?,?,?,?)");
      for (const { stream, event } of batch) {
        const expires = Date.parse(event.occurredAt) + this.ttl;
        if (expires <= this.clock() || Date.parse(event.occurredAt) > this.clock() + 60_000) continue;
        const sender = this.store.hash(event.type === "messageReceived" ? event.payload.senderId : event.payload.contactId);
        if (this.store.contact(sender)?.expires === 0) continue;
        if (add.run(scope, this.store.hash(event.eventId), stream, sender, expires, this.seal(event)).changes) inserted.push(event);
      }
      return inserted;
    });
  }
  paused(scope: string) { return Boolean(this.store.setting("adapter-paused:" + this.store.hash(scope))); }
  pause(scope: string) { this.store.set("adapter-paused:" + this.store.hash(scope), 1); }
  prune() { this.store.db.prepare("DELETE FROM adapter_inbox WHERE expires<=?").run(this.clock()); }
  page(scope: string, stream: string, request: PageRequest) {
    const cursor = request.cursor === undefined ? 0 : Number(request.cursor);
    const limit = request.limit ?? 100;
    if (!Number.isSafeInteger(cursor) || cursor < 0 || !Number.isSafeInteger(limit) || limit < 1 || limit > 100) return fail("invalid_input");
    this.prune();
    const rows = this.store.db.prepare("SELECT seq,sealed FROM adapter_inbox WHERE scope=? AND stream=? AND seq>? ORDER BY seq LIMIT ?")
      .all(scope, stream, cursor, limit);
    return ok({ items: rows.map(r => this.open<ChannelEvent>(String(r.sealed))), nextCursor: String(rows.at(-1)?.seq ?? cursor) });
  }
  write<K extends Operation>(scope: string, command: Command<K>, start: () => Promise<Result<Results[K]>>): Promise<Result<Results[K]>> {
    const db = this.store.db;
    if (!validIdempotencyKey(command.idempotencyKey)) return Promise.resolve(fail("invalid_input"));
    const writeScope = "account:" + command.accountId;
    const key = this.store.hash(command.idempotencyKey);
    const fingerprint = this.store.hash(JSON.stringify([scope, command.operation, command.payload]));
    const previous = db.prepare("SELECT fingerprint,result FROM adapter_writes WHERE scope=? AND key=?").get(writeScope, key);
    if (previous) return Promise.resolve(previous.fingerprint !== fingerprint ? fail("invalid_input")
      : previous.result ? this.open<Result<Results[K]>>(String(previous.result)) : fail("unknown_delivery"));
    const until = Number(db.prepare("SELECT until FROM adapter_throttle WHERE scope=?").get(scope)?.until ?? 0);
    if (until > this.clock()) return Promise.resolve(fail("rate_limited", Math.ceil((until - this.clock()) / 1000)));
    // This statement and initiation run under Guard's writer lock in the runtime.
    if (!db.prepare("INSERT OR IGNORE INTO adapter_writes VALUES(?,?,?,NULL)").run(writeScope, key, fingerprint).changes) {
      return Promise.resolve(fail("unknown_delivery"));
    }
    const settle = (result: Result<Results[K]>) => {
      if (!result.ok && result.error.code === "rate_limited") {
        this.store.atomic(() => {
          db.prepare("INSERT INTO adapter_throttle VALUES(?,?) ON CONFLICT(scope) DO UPDATE SET until=max(until,excluded.until)")
            .run(scope, this.clock() + (result.error.retryAfterSeconds ?? 60) * 1000);
          db.prepare("DELETE FROM adapter_writes WHERE scope=? AND key=?").run(writeScope, key);
        });
      } else db.prepare("UPDATE adapter_writes SET result=? WHERE scope=? AND key=?").run(this.seal(result), writeScope, key);
      return result;
    };
    // The finite writes initiate synchronously, while settlement happens after the Guard commits.
    try { return start().then(settle, () => settle(fail("unknown_delivery"))); }
    catch { return Promise.resolve().then(() => settle(fail("unknown_delivery"))); }
  }
}
