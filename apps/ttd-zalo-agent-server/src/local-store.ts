import { DatabaseSync } from "node:sqlite";
import { createHmac } from "node:crypto";
import { migrateKnowledge } from "../../ttd-zalo-assistant/src/knowledge.js";
import { migrateCustomer } from "../../ttd-zalo-assistant/src/customer.js";
import { transaction } from "../../ttd-zalo-assistant/src/policy-core.js";
import { Store } from "./store.js";

export class LocalStore extends Store {
  constructor(path: string, key: string) {
    const db = new DatabaseSync(path);
    db.exec("PRAGMA busy_timeout=5000; PRAGMA foreign_keys=ON; PRAGMA synchronous=FULL; PRAGMA secure_delete=ON");
    transaction(db, () => {
      const version = db.prepare("PRAGMA user_version").get()?.user_version;
      if (version === 0) {
        db.exec(`
          CREATE TABLE settings(key TEXT PRIMARY KEY,value INTEGER NOT NULL);
          CREATE TABLE runtime_identity(digest TEXT NOT NULL);
          INSERT INTO settings VALUES('global',1);
          CREATE TABLE contact(target TEXT PRIMARY KEY, revision INTEGER NOT NULL DEFAULT 0,
            expires INTEGER NOT NULL DEFAULT 0, retain INTEGER NOT NULL DEFAULT 0, respond INTEGER NOT NULL DEFAULT 0,
            send INTEGER NOT NULL DEFAULT 0, takeover INTEGER NOT NULL DEFAULT 0, ads INTEGER NOT NULL DEFAULT 0,
            opted_out INTEGER NOT NULL DEFAULT 0, accepted INTEGER NOT NULL DEFAULT 0, interest INTEGER NOT NULL DEFAULT 0);
          CREATE TABLE knowledge(id TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT NOT NULL);
          CREATE TABLE inbound(id TEXT PRIMARY KEY,target TEXT NOT NULL, received INTEGER NOT NULL);
          CREATE TABLE send_log(id TEXT PRIMARY KEY,target TEXT NOT NULL, agent TEXT NOT NULL,
            kind TEXT NOT NULL, at INTEGER NOT NULL, state TEXT NOT NULL);
          CREATE INDEX outbound_kind_at ON send_log(kind,at);
          CREATE INDEX outbound_target_kind_at ON send_log(target,kind,at);
          CREATE TABLE failures(at INTEGER NOT NULL);
          CREATE TABLE ledger(id TEXT PRIMARY KEY, cycle TEXT NOT NULL, date TEXT NOT NULL, model TEXT NOT NULL,
            amount INTEGER NOT NULL, state TEXT NOT NULL, batch TEXT, input INTEGER, output INTEGER,
            cache_write INTEGER, cache_read INTEGER, settled_cycle TEXT);
          CREATE TABLE jobs(id TEXT PRIMARY KEY, kind TEXT NOT NULL, target TEXT, status TEXT NOT NULL,
            created INTEGER NOT NULL, revision INTEGER, epoch INTEGER, body TEXT);
          CREATE TABLE notices(key TEXT PRIMARY KEY, at INTEGER NOT NULL, body TEXT NOT NULL);
        `);
        db.prepare("INSERT INTO runtime_identity VALUES(?)").run(createHmac("sha256", key).update("runtime-identity-key-binding").digest("hex"));
        migrateKnowledge(db);
        migrateCustomer(db);
      } else if (version !== 1 && version !== 2 && version !== 3) throw Error("UNSUPPORTED_RUNTIME_SCHEMA");
      if (version === 0 || version === 1) db.exec(`
        ALTER TABLE ledger ADD COLUMN provider TEXT NOT NULL DEFAULT 'anthropic';
        ALTER TABLE ledger ADD COLUMN rate_multiplier REAL NOT NULL DEFAULT 1;
        ALTER TABLE ledger ADD COLUMN input_bound INTEGER;
        PRAGMA user_version=2;
      `);
      if (version !== 3) db.exec(`
        ALTER TABLE contact ADD COLUMN ads_paused_review TEXT;
        PRAGMA user_version=3;
      `);
    });
    super(db, key);
  }
}
