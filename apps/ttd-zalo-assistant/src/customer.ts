import { createHash } from "node:crypto";
import type { DatabaseSync } from "node:sqlite";

export const fieldKinds = ["tag", "stage", "need", "follow-up"] as const;
export type FieldKind = (typeof fieldKinds)[number];
export function validField(value: unknown): value is FieldKind {
  return fieldKinds.some(kind => kind === value);
}

export function messageIdentity(account: string, user: string, thread: string, message: string) {
  return { account, user, thread, message: createHash("sha256")
    .update(JSON.stringify([account, user, thread, message])).digest("hex") };
}

export function migrateCustomer(db: DatabaseSync) {
  db.exec(`
    CREATE TABLE customer_field(id INTEGER PRIMARY KEY, target TEXT NOT NULL,
      source TEXT NOT NULL REFERENCES inbound(id), kind TEXT NOT NULL, value TEXT NOT NULL,
      created INTEGER NOT NULL, UNIQUE(target,source,kind,value));
    CREATE INDEX customer_field_target ON customer_field(target,kind,id);
  `);
}
