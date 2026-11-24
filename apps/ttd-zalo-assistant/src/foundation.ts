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
type Approval = { id: string; target: Target; digest: string; revision: number; epoch: number; expires: number };

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

  constructor(path: string) {
    this.db = new DatabaseSync(path);
    this.db.exec("PRAGMA busy_timeout=3000; PRAGMA foreign_keys=ON; PRAGMA synchronous=FULL");
    try {
      this.transaction(() => {
        const version = Number(this.db.prepare("PRAGMA user_version").get()?.user_version);
        if (version === 1) return;
        if (version !== 0) throw new Error("UNSUPPORTED_SCHEMA");
        this.db.exec(`
          CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1), stopped INTEGER NOT NULL, epoch INTEGER NOT NULL);
          INSERT INTO state VALUES(1,1,0);
          CREATE TABLE consent(target TEXT PRIMARY KEY, revision INTEGER NOT NULL, expires INTEGER NOT NULL,
            retain INTEGER NOT NULL, respond INTEGER NOT NULL, send INTEGER NOT NULL, takeover INTEGER NOT NULL);
          CREATE TABLE attempt(id TEXT PRIMARY KEY, target TEXT NOT NULL, status TEXT NOT NULL);
          CREATE TABLE receipt(id TEXT PRIMARY KEY REFERENCES attempt(id));
          PRAGMA user_version=1;
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

  close() { this.approvals.clear(); this.db.close(); }

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
      customers: customers.map((customer) => ({ ...customer, policy: this.policy(customer.id) })),
    };
  }

  setStopped(stopped: boolean) {
    if (typeof stopped !== "boolean") throw new Error("INVALID_STOP");
    this.db.prepare("UPDATE state SET stopped=?, epoch=epoch+1 WHERE id=1").run(Number(stopped));
    this.approvals.clear();
  }

  setConsent(target: Target, consent: Consent, expires: number, takeover: boolean) {
    if (!validTarget(target) || !consent || [consent.retain, consent.respond, consent.send, takeover]
      .some((flag) => typeof flag !== "boolean") || !Number.isSafeInteger(expires)) throw new Error("INVALID_CONSENT");
    this.db.prepare(`INSERT INTO consent VALUES(?,1,?,?,?,?,?)
      ON CONFLICT(target) DO UPDATE SET revision=revision+1, expires=excluded.expires,
      retain=excluded.retain, respond=excluded.respond, send=excluded.send, takeover=excluded.takeover`)
      .run(target, expires, Number(consent.retain), Number(consent.respond), Number(consent.send), Number(takeover));
  }

  approve(target: Target, content: string) {
    const digest = contentDigest(target, content);
    const approval = this.transaction(() => {
      const now = Date.now();
      const policy = this.policy(target, now);
      if (!policy.send) throw new Error("SEND_DENIED");
      return { id: randomUUID(), target, digest, revision: policy.revision, epoch: this.state().epoch,
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
    this.db.prepare("INSERT INTO attempt VALUES(?,?,'reserved')").run(id, target);
    try {
      await prepare?.();
      this.transaction(() => {
        const now = Date.now();
        const policy = this.policy(target, now);
        if (!policy.send || policy.revision !== approval.revision ||
            this.state().epoch !== approval.epoch || approval.expires <= now) throw new Error("SEND_REVOKED");
        // The fake transport initiates synchronously under the same SQLite writer lock.
        // A future adapter may not defer its initiation beyond this boundary.
        this.db.prepare("INSERT INTO receipt VALUES(?)").run(id);
        this.db.prepare("UPDATE attempt SET status='sent' WHERE id=?").run(id);
      });
      return { id, status: "fake-sent" as const };
    } catch (error) {
      this.db.prepare("UPDATE attempt SET status='closed' WHERE id=?").run(id);
      throw error;
    }
  }
}
