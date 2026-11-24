import { DatabaseSync } from "node:sqlite";
import { createHash, randomUUID } from "node:crypto";

export const accountId = "synthetic-ttd";
export const customers = [
  { id: "customer-a", thread: "dm-a", name: "Nguyễn Minh" },
  { id: "customer-b", thread: "dm-b", name: "Nguyễn Minh" },
] as const;
export type Target = (typeof customers)[number]["id"];
export type Consent = { retain: boolean; respond: boolean; send: boolean };
export type Policy = Consent & { revision: number; expires: number; takeover: boolean };
type Row = { revision: number; expires: number; retain: number; respond: number; send: number; takeover: number };
type Approval = { intent?: string; id: string; target: Target; digest: string; revision: number; epoch: number; expires: number };

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
  private readonly approvals = new Map<string, Approval>();

  private readonly origins = new Map<string, DraftOrigin>();

  constructor(path: string) {
    this.db = new DatabaseSync(path);
    this.db.exec("PRAGMA busy_timeout=3000; PRAGMA foreign_keys=ON; PRAGMA synchronous=FULL");
    try {
      this.transaction(() => {
        const version = Number(this.db.prepare("PRAGMA user_version").get()?.user_version);
        if (![0, 1, 2].includes(version)) throw new Error("UNSUPPORTED_SCHEMA");
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

  close() { this.approvals.clear(); this.origins.clear(); this.db.close(); }

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
    this.audit(stopped ? "stop" : "resume");
  }

  setConsent(target: Target, consent: Consent, expires: number, takeover: boolean) {
    if (!validTarget(target) || !consent || [consent.retain, consent.respond, consent.send, takeover]
      .some((flag) => typeof flag !== "boolean") || !Number.isSafeInteger(expires)) throw new Error("INVALID_CONSENT");
    this.db.prepare(`INSERT INTO consent VALUES(?,1,?,?,?,?,?)
      ON CONFLICT(target) DO UPDATE SET revision=revision+1, expires=excluded.expires,
      retain=excluded.retain, respond=excluded.respond, send=excluded.send, takeover=excluded.takeover`)
      .run(target, expires, Number(consent.retain), Number(consent.respond), Number(consent.send), Number(takeover));
    for (const [id, origin] of this.origins) if (origin.target === target) this.origins.delete(id);
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
      const result = this.db.prepare("INSERT OR IGNORE INTO inbound VALUES(?,?,?,?)")
        .run(key, target, policy.retain ? content : null, Date.now());
      if (!result.changes) return { state: "duplicate", id: key, canDraft: false };
      this.invalidateApprovals(target);
      if (policy.respond) {
        for (const [k, origin] of this.origins) if (origin.target === target) this.origins.delete(k);
        this.origins.set(key, { target, question: content, revision: policy.revision, epoch: this.state().epoch });
      }
      this.audit(policy.retain ? "inbound-retained" : "inbound-ephemeral", target);
      return { state: policy.retain ? "retained" : "ephemeral", id: key, canDraft: policy.respond };
    });
  }

  conversation(target: Target) {
    if (!this.policy(target).retain) return [];
    return this.db.prepare("SELECT id,content,received FROM inbound WHERE target=? AND content IS NOT NULL ORDER BY received DESC LIMIT 100")
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

  importKnowledge(document: string) {
    if (typeof document !== "string" || document.length > 3000) throw new Error("INVALID_DOCUMENT");
    const fields = /^SKU: ([A-Z0-9_-]{1,40})\r?\nTên: ([^\r\n]{1,120})\r?\nThông tin: ([^\r\n]{1,2000})\r?\n?$/u.exec(document);
    if (!fields) throw new Error("INVALID_DOCUMENT");
    const [, id, title, summary] = fields;
    this.db.prepare("INSERT INTO knowledge VALUES(?,?,?)").run(id, title, summary);
    this.approvals.clear();
    this.audit("knowledge-imported");
    return id;
  }

  knowledge(query = "") {
    if (typeof query !== "string" || query.length > 100) throw new Error("INVALID_QUERY");
    return this.db.prepare("SELECT * FROM knowledge WHERE instr(lower(id || ' ' || title),lower(?)) > 0 OR ?='' ORDER BY id LIMIT 100")
      .all(query, query) as { id: string; title: string; summary: string }[];
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
    const sku = /(?:^|\s)SKU[ :]+([A-Z0-9_-]{1,40})(?![A-Z0-9_-])/i.exec(question)?.[1]?.toUpperCase();
    const source = sku ? this.knowledge(sku).find((row) => row.id === sku) : undefined;
    const asksPrice = /giá|price|bao nhiêu/iu.test(question);
    if (!source || (asksPrice && !/giá\s*[:=]/iu.test(source.summary))) {
      return { text: "Bạn vui lòng xác nhận mã sản phẩm và thông tin cần hỏi để tôi kiểm tra thêm.", source: null };
    }
    return { text: source.title + ": " + source.summary, source: { id: source.id, title: source.title } };
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
    for (const [id, approval] of this.approvals) if (approval.target === target) this.approvals.delete(id);
  }

  approve(target: Target, content: string, intent?: string) {
    const digest = contentDigest(target, content);
    const approval = this.transaction(() => {
      const now = Date.now();
      const policy = this.policy(target, now);
      if (!policy.send) throw new Error("SEND_DENIED");
      if (intent) this.requireOrigin(target, intent);

      return { id: randomUUID(), target, digest, intent, revision: policy.revision, epoch: this.state().epoch,
        expires: Math.min(policy.expires, now + 60_000) };
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
            this.state().epoch !== approval.epoch || approval.expires <= now) throw new Error("SEND_REVOKED");
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
