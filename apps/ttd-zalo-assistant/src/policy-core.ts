import type { DatabaseSync } from "node:sqlite";

export type Consent = { retain: boolean; respond: boolean; send: boolean };
export type Policy = Consent & { revision: number; expires: number; takeover: boolean };
export type PolicyRow = { revision: number; expires: number; retain: number; respond: number; send: number; takeover: number };

export function effectivePolicy(row: PolicyRow | undefined, stopped: boolean, now: number): Policy {
    const active = Boolean(row && row.expires > now && !row.takeover && !stopped);
    return {
      retain: active && row?.retain === 1, respond: active && row?.respond === 1,
      send: active && row?.send === 1, takeover: row?.takeover === 1,
      expires: row?.expires ?? 0, revision: row?.revision ?? 0,
    };
}

export function transaction<T>(db: DatabaseSync, fn: () => T): T {
  db.exec("BEGIN IMMEDIATE");
  try {
    const result = fn();
    db.exec("COMMIT");
    return result;
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }
}
