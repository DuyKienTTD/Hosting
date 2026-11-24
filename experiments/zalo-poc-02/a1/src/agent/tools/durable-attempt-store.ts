import { DatabaseSync } from 'node:sqlite';
import type { AttemptStore } from './send-dispatch-guard.js';
/** One SQLite file per isolated sandbox. Reserve is a transactional UNIQUE insert. */
export function openDurableAttemptStore(filename: string): AttemptStore & { close(): void; status(key: string): string | undefined } {
  if (!filename || filename === ':memory:') throw Error('durable_file_required');
  const db = new DatabaseSync(filename);
  db.exec("PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; CREATE TABLE IF NOT EXISTS outbound_attempts (attempt_key TEXT PRIMARY KEY, state TEXT NOT NULL CHECK(state IN ('reserved','sent')), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)");
  const reserve = db.prepare("INSERT OR IGNORE INTO outbound_attempts(attempt_key,state) VALUES(?, 'reserved')");
  const mark = db.prepare("UPDATE outbound_attempts SET state='sent' WHERE attempt_key=? AND state='reserved'");
  const read = db.prepare('SELECT state FROM outbound_attempts WHERE attempt_key=?');
  return {
    reserveOnce: async (key: string) => { if (!key) throw Error('invalid_key'); return reserve.run(key).changes === 1; },
    markSent: async (key: string) => { if (mark.run(key).changes !== 1) throw Error('missing_or_duplicate_attempt'); },
    status: (key: string) => (read.get(key) as {state:string}|undefined)?.state,
    close: () => db.close(),
  };
}
