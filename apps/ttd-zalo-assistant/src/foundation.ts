import { DatabaseSync } from "node:sqlite";
import { createHash, randomUUID } from "node:crypto";

import { Knowledge, localDate, migrateKnowledge, type Source } from "./knowledge.js";
import { FakeProvider, asksReference, extractSkus, questionDate, validatedDraft, type AIAdapter, type MemoryEvidence } from "./ai.js";
import { messageIdentity, migrateCustomer, validField, type FieldKind } from "./customer.js";

export const accountId = "synthetic-ttd";
export const customers = [
  { id: "customer-a", thread: "dm-a", name: "Nguyễn Minh" },
  { id: "customer-b", thread: "dm-b", name: "Nguyễn Minh" },
] as const;
export type Target = (typeof customers)[number]["id"];
export type Consent = { retain: boolean; respond: boolean; send: boolean };
export type Policy = Consent & { revision: number; expires: number; takeover: boolean };
type Row = { revision: number; expires: number; retain: number; respond: number; send: number; takeover: number };
type Approval = { intent?: string; id: string; target: Target; digest: string; revision: number; epoch: number; expires: number; generation: number };

type DraftOrigin = { target: Target; question: string; revision: number; epoch: number };

export function validTarget(value: unknown): value is Target {
  return customers.some((customer) => customer.id === value);
}

function contentDigest(target: Target, content: string) {
  if (!validTarget(target) || typeof content !== "string" || !content.trim() || content.length > 2000) {
    throw new Error("INVALID_MESSAGE");
  }
  const customer = customers.find((row) => row.id === target)!;
  return createHash("sha256").update(JSON.stringify([accountId, target, customer.thread, "dm", content])).digest("hex");
}

export class Foundation {
  private readonly db: DatabaseSync;
  private readonly catalogue: Knowledge;
  private readonly revisions = new Map<Target, number>();
  private readonly approvals = new Map<string, Approval>();

  private readonly refused = new Set<string>();
  private readonly origins = new Map<string, DraftOrigin>();

  constructor(path: string, private readonly ai: AIAdapter = new FakeProvider(),
    private readonly today = localDate) {
    this.db = new DatabaseSync(path);
    this.db.exec("PRAGMA busy_timeout=3000; PRAGMA foreign_keys=ON; PRAGMA synchronous=FULL; PRAGMA secure_delete=ON");
    this.catalogue = new Knowledge(this.db);
    try {
      this.transaction(() => {
        const version = Number(this.db.prepare("PRAGMA user_version").get()?.user_version);
        if (![0, 1, 2, 3].includes(version)) throw new Error("UNSUPPORTED_SCHEMA");
        if (version === 0) this.db.exec(`
          CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1), stopped INTEGER NOT NULL, epoch INTEGER NOT NULL);
          INSERT INTO state VALUES(1,1,0);
          CREATE TABLE consent(target TEXT PRIMARY KEY, revision INTEGER NOT NULL, expires INTEGER NOT NULL,
            retain INTEGER NOT NULL, respond INTEGER NOT NULL, send INTEGER NOT NULL, takeover INTEGER NOT NULL);
          CREATE TABLE attempt(id TEXT PRIMARY KEY, target TEXT NOT NULL, status TEXT NOT NULL);
          CREATE TABLE receipt(id TEXT PRIMARY KEY REFERENCES attempt(id));
          PRAGMA user_version=1;
        `);
        if (version < 2) this.db.exec(`
          CREATE TABLE inbound(id TEXT PRIMARY KEY, target TEXT NOT NULL, content TEXT, received INTEGER NOT NULL);
          CREATE TABLE memory(id INTEGER PRIMARY KEY, target TEXT NOT NULL, source TEXT NOT NULL REFERENCES inbound(id), fact TEXT NOT NULL);
          CREATE TABLE knowledge(id TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT NOT NULL);
          CREATE TABLE audit(id INTEGER PRIMARY KEY, at INTEGER NOT NULL, action TEXT NOT NULL, target TEXT);
          ALTER TABLE attempt ADD COLUMN intent TEXT;
          CREATE UNIQUE INDEX attempt_intent ON attempt(intent) WHERE intent IS NOT NULL;
          PRAGMA user_version=2;
        `);
        if (version < 3) {
          migrateKnowledge(this.db);
          migrateCustomer(this.db);
          this.db.exec("PRAGMA user_version=3");
        }
      });
    } catch (error) {
      this.db.close();
      throw error;
    }
  }

  private transaction<T>(fn: () => T): T {
    this.db.exec("BEGIN IMMEDIATE");
    try {
      const result = fn();
      this.db.exec("COMMIT");
      return result;
    } catch (error) {
      this.db.exec("ROLLBACK");
      throw error;
    }
  }

  close() { this.approvals.clear(); this.origins.clear(); this.refused.clear(); this.db.close(); }

  private state() {
    return this.db.prepare("SELECT stopped,epoch FROM state WHERE id=1").get() as { stopped: number; epoch: number };
  }

  private row(target: Target) {
    if (!validTarget(target)) throw new Error("INVALID_TARGET");
    return this.db.prepare("SELECT * FROM consent WHERE target=?").get(target) as Row | undefined;
  }

  policy(target: Target, now = Date.now()): Policy {
    const row = this.row(target);
    const active = Boolean(row && row.expires > now && !row.takeover && !this.state().stopped);
    return {
      retain: active && row?.retain === 1, respond: active && row?.respond === 1,
      send: active && row?.send === 1, takeover: row?.takeover === 1,
      expires: row?.expires ?? 0, revision: row?.revision ?? 0,
    };
  }

  status() {
    return {
      stopped: this.state().stopped === 1,
      connection: { channel: "fake" as const, state: "offline-ready" as const },
      fakeSends: Number(this.db.prepare("SELECT count(*) AS n FROM receipt").get()?.n),
      customers: customers.map((customer) => {
        const row = this.row(customer.id);
        return { ...customer, policy: this.policy(customer.id), configured: {
          retain: row?.retain === 1, respond: row?.respond === 1, send: row?.send === 1, takeover: row?.takeover === 1,
        } };
      }),
    };
  }

  setStopped(stopped: boolean) {
    if (typeof stopped !== "boolean") throw new Error("INVALID_STOP");
    this.db.prepare("UPDATE state SET stopped=?, epoch=epoch+1 WHERE id=1").run(Number(stopped));
    this.approvals.clear();
    this.origins.clear();
    this.refused.clear();
    this.audit(stopped ? "stop" : "resume");
  }

  setConsent(target: Target, consent: Consent, expires: number, takeover: boolean) {
    if (!validTarget(target) || !consent || [consent.retain, consent.respond, consent.send, takeover]
      .some((flag) => typeof flag !== "boolean") || !Number.isSafeInteger(expires)) throw new Error("INVALID_CONSENT");
    this.db.prepare(`INSERT INTO consent VALUES(?,1,?,?,?,?,?)
      ON CONFLICT(target) DO UPDATE SET revision=revision+1, expires=excluded.expires,
      retain=excluded.retain, respond=excluded.respond, send=excluded.send, takeover=excluded.takeover`)
      .run(target, expires, Number(consent.retain), Number(consent.respond), Number(consent.send), Number(takeover));
    for (const [id, origin] of this.origins) if (origin.target === target) { this.origins.delete(id); this.refused.delete(id); }
    this.audit(takeover ? "takeover" : "consent", target);
  }

  private audit(action: string, target?: Target) {
    this.db.prepare("INSERT INTO audit(at,action,target) VALUES(?,?,?)").run(Date.now(), action, target ?? null);
  }

  receive(target: Target, id: string, content: string) {
    contentDigest(target, content);
    if (typeof id !== "string" || !/^[a-zA-Z0-9-]{1,80}$/.test(id)) throw new Error("INVALID_EVENT");
    return this.transaction(() => {
      const policy = this.policy(target);
      if (!policy.retain && !policy.respond) {
        this.audit("inbound-denied", target);
        return { state: "denied", id, canDraft: false };
      }
      const key = target + ":" + id;
      const scope = this.identity(target);
      const identity = messageIdentity(scope.account, scope.user, scope.thread, key);
      const result = this.db.prepare("INSERT OR IGNORE INTO inbound VALUES(?,?,?,?)")
        .run(key, target, policy.retain ? content : null, Date.now());
      if (!result.changes) return { state: "duplicate", id: key, identity, canDraft: false };
      this.invalidateApprovals(target);
      if (policy.respond) {
        for (const [k, origin] of this.origins) if (origin.target === target) { this.origins.delete(k); this.refused.delete(k); }
        this.origins.set(key, { target, question: content, revision: policy.revision, epoch: this.state().epoch });
      }
      this.audit(policy.retain ? "inbound-retained" : "inbound-ephemeral", target);
      return { state: policy.retain ? "retained" : "ephemeral", id: key, identity, canDraft: policy.respond };
    });
  }

  conversation(target: Target) {
    if (!this.policy(target).retain) return [];
    return this.db.prepare("SELECT id,content,received FROM inbound WHERE target=? AND content IS NOT NULL ORDER BY received DESC,rowid DESC LIMIT 100")
      .all(target) as { id: string; content: string; received: number }[];
  }

  remember(target: Target, source: string, fact: string) {
    contentDigest(target, fact);
    return this.transaction(() => {
      const row = this.db.prepare("SELECT content FROM inbound WHERE id=? AND target=?").get(source, target);
      if (!this.policy(target).retain || typeof row?.content !== "string" || !row.content.includes(fact)) {
        throw new Error("MEMORY_DENIED");
      }
      this.db.prepare("INSERT INTO memory(target,source,fact) VALUES(?,?,?)").run(target, source, fact);
      this.audit("memory-saved", target);
    });
  }

  profile(target: Target) {
    if (!this.policy(target).retain) return [];
    return this.db.prepare("SELECT source,fact FROM memory WHERE target=? ORDER BY id DESC LIMIT 100")
      .all(target) as { source: string; fact: string }[];
  }

  saveField(target: Target, source: string, kind: FieldKind, value: string) {
    contentDigest(target, value);
    if (!validField(kind) || typeof source !== "string" || value.length > 250) throw Error("INVALID_FIELD");
    this.transaction(() => {
      const row = this.db.prepare("SELECT content FROM inbound WHERE id=? AND target=?").get(source, target);
      if (!this.policy(target).retain || typeof row?.content !== "string") throw Error("MEMORY_DENIED");
      this.db.prepare("INSERT OR IGNORE INTO customer_field(target,source,kind,value,created) VALUES(?,?,?,?,?)")
        .run(target, source, kind, value.trim(), Date.now());
    });
  }

  private customerFields(target: Target, limited: boolean) {
    const limit = limited ? 100 : -1;
    return this.db.prepare(`SELECT id,source,kind,value,created FROM customer_field
      WHERE target=? ORDER BY id DESC LIMIT ?`).all(target, limit) as
      { id: number; source: string; kind: FieldKind; value: string; created: number }[];
  }

  fields(target: Target) {
    return this.policy(target).retain ? this.customerFields(target, true) : [];
  }

  private identity(target: Target) {
    if (!validTarget(target)) throw Error("INVALID_TARGET");
    const { thread } = customers.find(row => row.id === target)!;
    return { account: accountId, user: target, thread };
  }

  exportCustomer(target: Target) {
    return this.transaction(() => {
      if (!this.policy(target).retain) throw Error("EXPORT_DENIED");
      const identity = this.identity(target);
      const timeline = this.db.prepare(`SELECT id,content,received FROM inbound
        WHERE target=? AND content IS NOT NULL ORDER BY received,id`).all(target).map(row => ({
        ...row, identity: messageIdentity(identity.account, identity.user, identity.thread, String(row.id)),
      }));
      const memory = this.db.prepare("SELECT source,fact FROM memory WHERE target=? ORDER BY id").all(target);
      return { identity, timeline, memory, fields: this.customerFields(target, false) };
    });
  }

  deleteCustomer(target: Target) {
    this.identity(target);
    this.transaction(() => {
      this.db.prepare("DELETE FROM customer_field WHERE target=?").run(target);
      this.db.prepare("DELETE FROM memory WHERE target=?").run(target);
      // Keep only IDs for replay suppression. No customer text survives.
      this.db.prepare("UPDATE inbound SET content=NULL,received=0 WHERE target=?").run(target);
      this.setConsent(target, { retain: false, respond: false, send: false }, 0, false);
      this.invalidateApprovals(target);
      this.audit("customer-deleted", target);
    });
  }

  importKnowledge(document: string, filename?: string) {
    const id = this.catalogue.import(document, filename);
    this.knowledgeChanged();
    return id;
  }

  addCatalogueSource(source: Source) {
    const id = this.catalogue.add(source);
    this.knowledgeChanged();
    return id;
  }

  private knowledgeChanged() {
    for (const customer of customers) this.invalidateApprovals(customer.id);
    this.audit("knowledge-imported");
  }

  knowledge(query = "", sku?: string) {
    return this.catalogue.search(query, sku);
  }

  private requireOrigin(target: Target, intent: string) {
    const origin = this.origins.get(intent);
    const policy = this.policy(target);
    if (!origin || origin.target !== target || !policy.respond || origin.revision !== policy.revision ||
        origin.epoch !== this.state().epoch) throw new Error("DRAFT_DENIED");
    return origin;
  }

  draft(target: Target, intent: string) {
    const { question } = this.requireOrigin(target, intent);
    const explicit = extractSkus(question);
    const canRead = this.policy(target).retain;
    const memory: MemoryEvidence[] = [];
    const stored = canRead ? this.profile(target) : [];
    if (asksReference(question)) {
      for (const row of stored) {
        const reference = row.fact.match(/\bREF-[A-Z0-9-]{1,60}\b/i)?.[0];
        if (reference) { memory.push({ id: row.source, type: "reference", value: reference }); break; }
      }
    }
    let sku = explicit.length === 1 ? explicit[0] : undefined;
    if (!explicit.length && /mẫu đó|mẫu kia|^vâng/iu.test(question)) {
      const recent = this.conversation(target).filter(row => row.id !== intent)
        .map(row => ({ id: row.id, codes: extractSkus(row.content) })).find(row => row.codes.length);
      if (recent?.codes.length === 1) {
        sku = recent.codes[0];
        if (stored.some(row => row.source === recent.id && extractSkus(row.fact).includes(sku!))) {
          memory.push({ id: recent.id, type: "sku", value: sku });
        }
      }
      if (!recent && !/mẫu kia/iu.test(question)) {
        for (const row of stored) {
          const codes = extractSkus(row.fact);
          if (codes.length === 1) { sku = codes[0]; memory.push({ id: row.source, type: "sku", value: sku }); break; }
        }
      }
    }
    const result = validatedDraft(this.ai, {
      question, sku, date: questionDate(question, this.today()), memory,
      sources: [...(sku ? this.catalogue.bySku(sku) : []), ...this.catalogue.policies()],
    });
    this.requireOrigin(target, intent);
    if (result.action === "từ chối") {
      this.refused.add(intent);
      this.invalidateApprovals(target);
    }
    return result;
  }

  activity() {
    return {
      audit: this.db.prepare("SELECT at,action,target FROM audit ORDER BY id DESC LIMIT 100")
        .all() as { at: number; action: string; target: Target | null }[],
      attempts: this.db.prepare("SELECT id,target,status FROM attempt ORDER BY rowid DESC LIMIT 100")
        .all() as { id: string; target: Target; status: string }[],
    };
  }

  invalidateApprovals(target: Target) {
    if (!validTarget(target)) throw new Error("INVALID_TARGET");
    this.revisions.set(target, (this.revisions.get(target) ?? 0) + 1);
    for (const [id, approval] of this.approvals) if (approval.target === target) this.approvals.delete(id);
  }

  approve(target: Target, content: string, intent?: string) {
    const digest = contentDigest(target, content);
    const approval = this.transaction(() => {
      const now = Date.now();
      const policy = this.policy(target, now);
      if (!policy.send) throw new Error("SEND_DENIED");
      if (intent) {
        this.requireOrigin(target, intent);
        if (this.refused.has(intent)) throw Error("DRAFT_DENIED");
      }

      return { id: randomUUID(), target, digest, intent, revision: policy.revision, epoch: this.state().epoch,
        generation: this.revisions.get(target) ?? 0, expires: Math.min(policy.expires, now + 60_000) };
    });
    for (const [id, previous] of this.approvals) {
      if (previous.target === target || previous.expires <= Date.now()) this.approvals.delete(id);
    }
    this.approvals.set(approval.id, approval);
    return approval.id;
  }

  async send(id: string, target: Target, content: string, prepare?: () => Promise<void>) {
    const approval = this.approvals.get(id);
    if (!approval || approval.target !== target || approval.digest !== contentDigest(target, content)) {
      throw new Error("APPROVAL_MISMATCH");
    }
    this.approvals.delete(id);
    // Commit reservation before any preparation or possible initiation.
    this.db.prepare("INSERT INTO attempt(id,target,status,intent) VALUES(?,?,'reserved',?)").run(id, target, approval.intent ?? null);
    try {
      await prepare?.();
      this.transaction(() => {
        const now = Date.now();
        const policy = this.policy(target, now);
        if (!policy.send || (approval.intent && !policy.respond) || policy.revision !== approval.revision ||
            this.state().epoch !== approval.epoch || (this.revisions.get(target) ?? 0) !== approval.generation || approval.expires <= now) throw new Error("SEND_REVOKED");
        // The fake transport initiates synchronously under the same SQLite writer lock.
        // A future adapter may not defer its initiation beyond this boundary.
        this.db.prepare("INSERT INTO receipt VALUES(?)").run(id);
        this.db.prepare("UPDATE attempt SET status='sent' WHERE id=?").run(id);
        this.audit("fake-sent", target);
      });
      return { id, status: "fake-sent" as const };
    } catch (error) {
      this.db.prepare("UPDATE attempt SET status='closed' WHERE id=?").run(id);
      this.audit("send-closed", target);
      throw error;
    }
  }
}
