import { DatabaseSync } from "node:sqlite";
import { createHmac } from "node:crypto";
import { effectivePolicy, transaction, type PolicyRow } from "../../ttd-zalo-assistant/src/policy-core.js";
import { Knowledge, migrateKnowledge } from "../../ttd-zalo-assistant/src/knowledge.js";
import { migrateCustomer, messageIdentity } from "../../ttd-zalo-assistant/src/customer.js";

export class Store {
  readonly db: DatabaseSync;
  readonly knowledge: Knowledge;
  constructor(path: string, private readonly identityKey: string) {
    this.db = new DatabaseSync(path);
    this.db.exec("PRAGMA busy_timeout=5000; PRAGMA foreign_keys=ON; PRAGMA synchronous=FULL; PRAGMA secure_delete=ON");
    this.knowledge = new Knowledge(this.db);
    this.atomic(() => {
      const version = this.db.prepare("PRAGMA user_version").get()?.user_version;
      if (version === 0) {
        this.db.exec(`
          CREATE TABLE settings(key TEXT PRIMARY KEY,value INTEGER NOT NULL);
          CREATE TABLE runtime_identity(digest TEXT NOT NULL);
          INSERT INTO settings VALUES('global',1);
          CREATE TABLE contact(target TEXT PRIMARY KEY, revision INTEGER NOT NULL DEFAULT 0,
            expires INTEGER NOT NULL DEFAULT 0, retain INTEGER NOT NULL DEFAULT 0, respond INTEGER NOT NULL DEFAULT 0,
            send INTEGER NOT NULL DEFAULT 0, takeover INTEGER NOT NULL DEFAULT 0, ads INTEGER NOT NULL DEFAULT 0,
            opted_out INTEGER NOT NULL DEFAULT 0, accepted INTEGER NOT NULL DEFAULT 0, interest INTEGER NOT NULL DEFAULT 0);
          CREATE TABLE knowledge(id TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT NOT NULL);
          CREATE TABLE inbound(id TEXT PRIMARY KEY,target TEXT NOT NULL, received INTEGER NOT NULL);
          CREATE TABLE outbound(id TEXT PRIMARY KEY,target TEXT NOT NULL, agent TEXT NOT NULL,
            kind TEXT NOT NULL, at INTEGER NOT NULL, state TEXT NOT NULL);
          CREATE INDEX outbound_kind_at ON outbound(kind,at);
          CREATE INDEX outbound_target_kind_at ON outbound(target,kind,at);
          CREATE TABLE failures(at INTEGER NOT NULL);
          CREATE TABLE ledger(id TEXT PRIMARY KEY, cycle TEXT NOT NULL, date TEXT NOT NULL, model TEXT NOT NULL,
            amount INTEGER NOT NULL, state TEXT NOT NULL, batch TEXT, input INTEGER, output INTEGER,
            cache_write INTEGER, cache_read INTEGER, settled_cycle TEXT);
          CREATE TABLE jobs(id TEXT PRIMARY KEY, kind TEXT NOT NULL, target TEXT, status TEXT NOT NULL,
            created INTEGER NOT NULL, revision INTEGER, epoch INTEGER, body TEXT);
          CREATE TABLE notices(key TEXT PRIMARY KEY, at INTEGER NOT NULL, body TEXT NOT NULL);
        `);
        this.db.prepare("INSERT INTO runtime_identity VALUES(?)").run(this.hash("runtime-identity-key-binding"));
        migrateKnowledge(this.db);
        migrateCustomer(this.db);
        this.db.exec("PRAGMA user_version=1");
      } else if (version !== 1) throw Error("UNSUPPORTED_RUNTIME_SCHEMA");
      if (this.db.prepare("SELECT digest FROM runtime_identity").get()?.digest !== this.hash("runtime-identity-key-binding")) {
        throw Error("IDENTITY_KEY_MISMATCH");
      }
    });
  }
  atomic<T>(fn: () => T) { return transaction(this.db, fn); }
  hash(value: string) { return createHmac("sha256", this.identityKey).update(value).digest("hex"); }
  eventKey(contact: string, thread: string, event: string) {
    return messageIdentity("runtime", this.hash(contact), this.hash(thread), this.hash(event)).message;
  }
  setting(key: string) {
    return Number(this.db.prepare("SELECT value FROM settings WHERE key=?").get(key)?.value ?? 0);
  }
  set(key: string, value: number) {
    this.db.prepare("INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value")
      .run(key, value);
  }
  stopped(agent: string) { return !!(this.setting("global") || this.setting(agent)); }
  stop(agent: string, stopped: boolean) {
    this.atomic(() => {
      this.set(agent, Number(stopped));
      this.set("epoch", this.setting("epoch") + 1);
    });
  }
  contact(target: string) {
    return this.db.prepare("SELECT * FROM contact WHERE target=?").get(target) as
      (PolicyRow & { ads: number; opted_out: number; accepted: number; interest: number }) | undefined;
  }
  policy(target: string, agent: string, now: number) {
    return effectivePolicy(this.contact(target), this.stopped(agent), now);
  }
  consent(target: string, until: number, retain: boolean, respond: boolean, send: boolean, ads: boolean) {
    this.db.prepare(`INSERT INTO contact(target,expires,retain,respond,send,ads,revision) VALUES(?,?,?,?,?,?,1)
      ON CONFLICT(target) DO UPDATE SET expires=excluded.expires, retain=excluded.retain,respond=excluded.respond,
      send=excluded.send,ads=excluded.ads,revision=revision+1`)
      .run(target, until, Number(retain), Number(respond), Number(send), Number(ads));
  }
  optOut(target: string) {
    this.db.prepare(`INSERT INTO contact(target,opted_out,revision) VALUES(?,1,1)
      ON CONFLICT(target) DO UPDATE SET opted_out=1,ads=0,revision=revision+1`).run(target);
  }
  notice(key: string, at: number, body: string) {
    this.db.prepare("INSERT OR REPLACE INTO notices VALUES(?,?,?)").run(key, at, body);
  }
  exportCustomer(raw: string) {
    const target = this.hash(raw);
    return this.atomic(() => ({
      consent: this.contact(target),
      fields: this.db.prepare("SELECT source,kind,value,created FROM customer_field WHERE target=?").all(target),
      attempts: this.db.prepare("SELECT kind,at,state FROM outbound WHERE target=?").all(target),
      queued: this.db.prepare("SELECT kind,status,created FROM jobs WHERE target=?").all(target),
    }));
  }
  deleteCustomer(raw: string) {
    const target = this.hash(raw);
    this.atomic(() => {
      this.optOut(target);
      this.db.prepare("UPDATE contact SET expires=0,retain=0,respond=0,send=0,accepted=0,interest=0 WHERE target=?").run(target);
      this.db.prepare("DELETE FROM customer_field WHERE target=?").run(target);
      this.db.prepare("DELETE FROM jobs WHERE target=?").run(target);
      this.db.prepare("UPDATE inbound SET received=0 WHERE target=?").run(target);
    });
  }
}
