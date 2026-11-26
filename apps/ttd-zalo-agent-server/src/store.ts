import type { SendClassification } from "./channel.js";
import type { RuntimeDatabase } from "./sql.js";
import { createHmac } from "node:crypto";
import { effectivePolicy, type PolicyRow } from "../../ttd-zalo-assistant/src/policy-core.js";
import { Knowledge } from "../../ttd-zalo-assistant/src/knowledge.js";
import { messageIdentity } from "../../ttd-zalo-assistant/src/customer.js";

export class Store {
  readonly knowledge: Knowledge;
  private inTransaction = false;
  constructor(readonly db: RuntimeDatabase, private readonly identityKey: string, private readonly retentionDays = 30) {
    if (!Number.isInteger(retentionDays) || retentionDays < 1 || retentionDays > 365) throw Error("INVALID_RETENTION");
    this.knowledge = new Knowledge(db, db.backend);
    this.atomic(() => {
      const binding = this.hash("runtime-identity-key-binding");
      if (db.backend) db.prepare("INSERT INTO runtime_identity VALUES(1,?) ON CONFLICT(slot) DO NOTHING").run(binding);
      if (db.prepare("SELECT digest FROM runtime_identity").get()?.digest !== binding) throw Error("IDENTITY_KEY_MISMATCH");
    });
  }
  atomic<T>(fn: () => T) {
    if (this.inTransaction) return fn();
    this.inTransaction = true;
    try {
      this.db.exec(this.db.backend ? "BEGIN; SELECT pg_advisory_xact_lock(76425161)" : "BEGIN IMMEDIATE");
      const result = fn();
      this.db.exec("COMMIT");
      return result;
    } catch (error) {
      try { this.db.exec("ROLLBACK"); } catch { this.db.close(); }
      throw error;
    } finally { this.inTransaction = false; }
  }
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
  contact(target: string, now = Date.now()) {
    const row = this.db.prepare(this.db.backend ? "SELECT * FROM runtime_contact_policy WHERE target=?"
      : "SELECT * FROM contact WHERE target=?").get(target) as
      (PolicyRow & { ads: number; opted_out: number; ads_paused_review: string | null; accepted: number; interest: number;
        ad_state?: string; retain_until?: number; respond_until?: number; send_until?: number; ads_until?: number }) | undefined;
    if (row && this.db.backend) {
      if (Number(row.retain_until) <= now) row.retain = 0;
      if (Number(row.respond_until) <= now) row.respond = 0;
      if (Number(row.send_until) <= now) row.send = 0;
      if (Number(row.ads_until) <= now) row.ads = 0;
    }
    return row;
  }
  policy(target: string, agent: string, now: number) {
    return effectivePolicy(this.contact(target, now), this.stopped(agent), now);
  }
  private customerId(target: string) {
    const found = this.db.prepare("SELECT customer_id FROM runtime_customer WHERE target=?").get(target)?.customer_id;
    if (typeof found === "string") return found;
    const { id } = this.db.prepare("INSERT INTO customers DEFAULT VALUES RETURNING id").get()!;
    this.db.prepare("INSERT INTO runtime_customer VALUES(?,?)").run(target, id);
    return String(id);
  }
  consent(target: string, until: number, retain: boolean, respond: boolean, send: boolean, ads: boolean,
    proof?: { displayedText: string; policyVersion: string; evidence: object }) {
    this.atomic(() => {
      this.db.prepare(`INSERT INTO contact(target,expires,retain,respond,send,ads,revision) VALUES(?,?,?,?,?,?,1)
        ON CONFLICT(target) DO UPDATE SET expires=excluded.expires, retain=excluded.retain,respond=excluded.respond,
        send=excluded.send,ads=excluded.ads,revision=contact.revision+1`)
        .run(target, until, Number(retain), Number(respond), Number(send), Number(ads));
      if (!this.db.backend) return;
      if (!proof) throw Error("CONSENT_PROOF_REQUIRED");
      const customer = this.customerId(target);
      this.db.prepare("INSERT INTO ad_status(customer_id,state) VALUES(?,'active') ON CONFLICT DO NOTHING").run(customer);
      for (const [purpose, granted] of Object.entries({ retain, respond, send, ads })) {
        const prior = this.db.prepare(`SELECT id,withdrawn FROM consents WHERE customer_id=? AND purpose=?
          ORDER BY occurred_at DESC,id DESC LIMIT 1`).get(customer, purpose);
        if (!granted && (!prior || prior.withdrawn)) continue;
        this.db.prepare(`INSERT INTO consents(customer_id,purpose,displayed_text,policy_version,evidence,
          occurred_at,withdrawn,previous_id,valid_until_ms)
          VALUES(?,?,?,?,?,clock_timestamp(),?::boolean,?,?)`).run(customer,purpose,proof.displayedText,proof.policyVersion,
          JSON.stringify(proof.evidence),String(!granted),prior?.id ?? null,granted ? until : null);
      }
    });
  }
  optOut(target: string) {
    this.atomic(() => {
      this.db.prepare(`INSERT INTO contact(target,opted_out,revision) VALUES(?,1,1)
        ON CONFLICT(target) DO UPDATE SET opted_out=1,ads=0,ads_paused_review=NULL,revision=contact.revision+1`).run(target);
      if (!this.db.backend) return;
      const customer = this.customerId(target);
      this.setAdStatus(customer, "opted_out");
      this.db.prepare(`INSERT INTO consents(customer_id,purpose,displayed_text,policy_version,evidence,occurred_at,withdrawn,previous_id)
        SELECT customer_id,purpose,displayed_text,policy_version,'{"source":"opt_out"}',clock_timestamp(),true,id
        FROM (SELECT * FROM consents WHERE customer_id=? AND purpose='ads' ORDER BY occurred_at DESC,id DESC LIMIT 1) prior
        WHERE NOT withdrawn`).run(customer);
    });
  }
  private setAdStatus(customer: string, state: string) {
    this.db.prepare(`INSERT INTO ad_status(customer_id,state) VALUES(?,?)
      ON CONFLICT(customer_id) DO UPDATE SET state=excluded.state,changed_at=clock_timestamp()
      WHERE ad_status.state <> 'opted_out'`).run(customer, state);
  }
  pauseAdsForReview(target: string, event: string) {
    this.atomic(() => {
      this.db.prepare(`INSERT INTO contact(target,ads_paused_review,revision) VALUES(?,?,1)
        ON CONFLICT(target) DO UPDATE SET ads_paused_review=excluded.ads_paused_review WHERE contact.opted_out=0`).run(target, event);
      if (this.db.backend) this.setAdStatus(this.customerId(target), "ads_paused_review");
    });
  }
  resolveAdsReview(target: string, event: string, action: "active" | "opted_out") {
    return this.atomic(() => {
      if (this.db.backend && this.contact(target)?.ads_paused_review !== event) return false;
      const cleared = this.db.prepare(`UPDATE contact SET ads_paused_review=NULL,revision=revision+1
        WHERE target=? AND ads_paused_review=? AND opted_out=0`).run(target, event);
      if (cleared.changes !== 1) return false;
      if (action === "opted_out") this.optOut(target);
      else if (this.db.backend) this.setAdStatus(this.customerId(target), "active");
      this.notice("ads-review-resolved:" + event, Date.now(), action === "opted_out"
        ? "Người vận hành xác nhận ngừng quảng cáo." : "Người vận hành xác nhận kết thúc tạm dừng quảng cáo.");
      return true;
    });
  }
  // Hold the session lock until synchronous transport initiation. COMMIT
  // makes the reservation durable while database policy writers stay blocked.
  admit<T>(fn: () => T, start: (result: T) => void) {
    if (this.db.backend) this.db.exec("SELECT pg_advisory_lock(76425161)");
    try {
      const result = this.atomic(fn);
      start(result);
      return result;
    } finally {
      if (this.db.backend) this.db.exec("SELECT pg_advisory_unlock(76425161)");
    }
  }
  retainMessage(target: string, thread: string, channel: "oa" | "nick" | "bot", id: string, text: string, at: number) {
    if (!this.db.backend) return;
    const customer = this.customerId(target);
    const threadKey = this.hash(thread);
    const { id: conversation } = this.db.prepare(`INSERT INTO conversations(customer_id,channel,runtime_thread)
      VALUES(?,?,?) ON CONFLICT(customer_id,channel,runtime_thread)
      DO UPDATE SET runtime_thread=excluded.runtime_thread RETURNING id`).get(customer,channel,threadKey)!;
    this.db.prepare(`INSERT INTO messages(conversation_id,event_id,body,received_at,retain_until)
      SELECT ?,?,?,to_timestamp(?::double precision/1000),to_timestamp(?::double precision/1000)
      WHERE NOT EXISTS (SELECT 1 FROM restore_tombstones WHERE conversation_id=? AND event_id=?)
      ON CONFLICT(conversation_id,event_id) DO NOTHING`)
      .run(conversation,id,text,at,at+this.retentionDays*86_400_000,conversation,id);
  }
  reserveSend(id: string, target: string, agent: string, kind: string, now: number, classification?: SendClassification) {
    if (classification) {
      const { messageType, window, quotaAccount, quotaMonth, quotaBucket } = classification;
      return this.db.prepare(`INSERT INTO send_log(id,target,agent,kind,at,state,customer_id,
          message_type,send_window,quota_account,quota_month,quota_bucket) VALUES(?,?,?,?,?,'reserved',
          (SELECT customer_id FROM runtime_customer WHERE target=?),?,?,?,?,?) ON CONFLICT DO NOTHING`)
        .run(id, target, agent, kind, now, target, messageType, window, quotaAccount, quotaMonth, quotaBucket).changes === 1;
    }
    return this.db.prepare(this.db.backend
      ? `INSERT INTO send_log(id,target,agent,kind,at,state,customer_id) VALUES(?,?,?,?,?,'reserved',
          (SELECT customer_id FROM runtime_customer WHERE target=?)) ON CONFLICT DO NOTHING`
      : "INSERT OR IGNORE INTO send_log VALUES(?,?,?,?,?,'reserved')")
      .run(...(this.db.backend ? [id,target,agent,kind,now,target] : [id,target,agent,kind,now])).changes === 1;
  }
  notice(key: string, at: number, body: string) {
    this.db.prepare("INSERT INTO notices VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET at=excluded.at,body=excluded.body").run(key, at, body);
  }
  exportCustomer(raw: string) {
    const target = this.hash(raw);
    return this.atomic(() => ({
      consent: this.contact(target),
      fields: this.db.prepare("SELECT source,kind,value,created FROM customer_field WHERE target=?").all(target),
      attempts: this.db.prepare("SELECT kind,at,state FROM send_log WHERE target=?").all(target),
      queued: this.db.prepare("SELECT kind,status,created FROM jobs WHERE target=?").all(target),
    }));
  }
  deleteCustomer(raw: string) {
    const target = this.hash(raw);
    this.atomic(() => {
      this.optOut(target);
      if (this.db.backend) {
        this.db.prepare(`INSERT INTO consents(customer_id,purpose,displayed_text,policy_version,evidence,occurred_at,withdrawn,previous_id)
          SELECT customer_id,purpose,displayed_text,policy_version,'{"source":"customer_delete"}',clock_timestamp(),true,id
          FROM (SELECT DISTINCT ON (purpose) * FROM consents WHERE customer_id=? ORDER BY purpose,occurred_at DESC,id DESC) latest
          WHERE NOT withdrawn`).run(this.customerId(target));
      }
      this.db.prepare("UPDATE contact SET expires=0,retain=0,respond=0,send=0,accepted=0,interest=0 WHERE target=?").run(target);
      this.db.prepare("DELETE FROM customer_field WHERE target=?").run(target);
      this.db.prepare("DELETE FROM jobs WHERE target=?").run(target);
      this.db.prepare("UPDATE inbound SET received=0 WHERE target=?").run(target);
      if (this.db.backend || this.db.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name='adapter_inbox'").get()) {
        this.db.prepare("DELETE FROM adapter_inbox WHERE sender=?").run(target);
      }
    });
  }
}
