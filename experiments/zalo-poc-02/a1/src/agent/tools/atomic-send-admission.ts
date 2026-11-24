import { DatabaseSync } from 'node:sqlite';

/** Offline synthetic policy authority, not connected to Zalo or real consent. */
export type SendBinding = Readonly<{
  accountId: string; threadId: string; senderId: string; recipientId: string;
  threadType: 'dm' | 'group'; attemptKey: string;
}>;
export type PolicyMutation = Readonly<{
  accountId: string; threadId: string; senderId: string; threadType: 'dm' | 'group';
  verified: boolean; respond: boolean; retain: boolean; outbound: boolean;
  optedOut: boolean; takeover: boolean; stopped: boolean; running: boolean;
  revision: number; expiresAtMs: number;
}>;
export type AdmissionOutcome<T> =
  | { status: 'blocked'; reason: string }
  | { status: 'unknown'; reason: string }
  | { status: 'sent'; value: T };
const id = (s: string) => typeof s === 'string' && /^[a-zA-Z0-9][\w:@.\-]{0,127}$/.test(s);
const valid = (p: PolicyMutation) => p &&
  [p.accountId,p.threadId,p.senderId].every(id) &&
  (p.threadType === 'dm' || p.threadType === 'group') &&
  Number.isSafeInteger(p.revision) && p.revision >= 1 && Number.isSafeInteger(p.expiresAtMs);

/** All real policy writers must use the same transactional admission boundary.
 * Do not treat this synthetic table as evidence of real customer consent.
 */
export function openSyntheticAtomicAdmission(file: string) {
  if (!file || file === ':memory:') throw Error('durable_file_required');
  const db = new DatabaseSync(file);
  db.exec(`PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;
CREATE TABLE IF NOT EXISTS synthetic_outbound_policy (
 account_id TEXT NOT NULL, thread_id TEXT NOT NULL, sender_id TEXT NOT NULL,
 thread_type TEXT NOT NULL CHECK(thread_type IN ('dm','group')),
 verified INTEGER NOT NULL, can_respond INTEGER NOT NULL, can_retain INTEGER NOT NULL,
 can_outbound INTEGER NOT NULL, opted_out INTEGER NOT NULL, takeover INTEGER NOT NULL,
 stopped INTEGER NOT NULL, running INTEGER NOT NULL, revision INTEGER NOT NULL,
 expires_at_ms INTEGER NOT NULL,
 PRIMARY KEY(account_id,thread_id,sender_id,thread_type));
CREATE TABLE IF NOT EXISTS synthetic_outbound_attempts (
 key TEXT PRIMARY KEY, state TEXT NOT NULL CHECK(state IN ('admitted','sent','unknown')),
 account_id TEXT NOT NULL, thread_id TEXT NOT NULL, revision INTEGER NOT NULL);
`);
  const getPolicy = db.prepare(`SELECT * FROM synthetic_outbound_policy
    WHERE account_id=? AND thread_id=? AND sender_id=? AND thread_type=?`);
  const current = db.prepare(`SELECT revision FROM synthetic_outbound_policy
    WHERE account_id=? AND thread_id=? AND sender_id=? AND thread_type=?`);
  const upsert = db.prepare(`INSERT INTO synthetic_outbound_policy VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ON CONFLICT(account_id,thread_id,sender_id,thread_type) DO UPDATE SET
    verified=excluded.verified, can_respond=excluded.can_respond,
    can_retain=excluded.can_retain, can_outbound=excluded.can_outbound,
    opted_out=excluded.opted_out, takeover=excluded.takeover, stopped=excluded.stopped,
    running=excluded.running, revision=excluded.revision, expires_at_ms=excluded.expires_at_ms`);
  const reserve = db.prepare(`INSERT OR IGNORE INTO synthetic_outbound_attempts
    (key,state,account_id,thread_id,revision) VALUES(?,'admitted',?,?,?)`);
  const sent = db.prepare(`UPDATE synthetic_outbound_attempts SET state='sent' WHERE key=? AND state='admitted'`);
  const unknown = db.prepare(`UPDATE synthetic_outbound_attempts SET state='unknown' WHERE key=? AND state='admitted'`);
  const state = db.prepare(`SELECT state FROM synthetic_outbound_attempts WHERE key=?`);

  /** STOP/opt-out/takeover writer is serialized against dispatch admission. */
  function mutatePolicy(p: PolicyMutation): boolean {
    if (!valid(p)) throw Error('invalid_policy_mutation');
    db.exec('BEGIN IMMEDIATE');
    try {
      const row = current.get(p.accountId,p.threadId,p.senderId,p.threadType) as {revision:number}|undefined;
      if (row && p.revision <= row.revision) { db.exec('ROLLBACK'); return false; }
      upsert.run(p.accountId,p.threadId,p.senderId,p.threadType,
        Number(p.verified),Number(p.respond),Number(p.retain),Number(p.outbound),
        Number(p.optedOut),Number(p.takeover),Number(p.stopped),Number(p.running),
        p.revision,p.expiresAtMs);
      db.exec('COMMIT'); return true;
    } catch(e) {db.exec('ROLLBACK');throw e;}
  }
  /** Linearizes admission, not remote completion. No await while holding lock.
   * Transport MUST begin its side effect synchronously on invocation; async
   * deferred transport needs its own admission boundary at actual dispatch.
   */
  async function dispatch<T>(b: SendBinding, transport: () => Promise<T>, nowMs: number): Promise<AdmissionOutcome<T>> {
    if (![b.accountId,b.threadId,b.senderId,b.recipientId,b.attemptKey].every(id) ||
      (b.threadType !== 'dm' && b.threadType !== 'group') ||
      (b.threadType === 'dm' && (b.recipientId !== b.threadId || b.senderId !== b.threadId)) ||
      b.recipientId !== b.threadId || !Number.isSafeInteger(nowMs)) {
      return { status: 'blocked', reason: 'invalid_destination_or_attempt' };
    }
    let call: Promise<T>;
    db.exec('BEGIN IMMEDIATE');
    try {
      const p = getPolicy.get(b.accountId,b.threadId,b.senderId,b.threadType) as Record<string,number>|undefined;
      const reason = !p ? 'unknown_policy' : !p.verified ? 'unverified_policy'
        : !p.can_outbound ? 'no_outbound_consent' : p.opted_out ? 'opt_out'
        : p.takeover ? 'human_takeover' : p.stopped ? 'stop' : !p.running ? 'account_stopped'
        : p.expires_at_ms <= nowMs ? 'expired_policy' : null;
      if (reason) { db.exec('ROLLBACK'); return {status:'blocked',reason}; }
      if (reserve.run(b.attemptKey,b.accountId,b.threadId,p!.revision).changes !== 1) {
        db.exec('ROLLBACK');return {status:'blocked',reason:'duplicate_or_uncertain_attempt'};
      }
      // Start transport BEFORE releasing the policy writer's SQLite lock.
      try { call = Promise.resolve(transport()); }
      catch { unknown.run(b.attemptKey);db.exec('COMMIT');return {status:'unknown',reason:'transport_sync_throw'}; }
      db.exec('COMMIT');
    } catch { try {db.exec('ROLLBACK');} catch{}; return {status:'blocked',reason:'atomic_admission_unavailable'}; }
    try {
      const value = await call!;
      try {sent.run(b.attemptKey);} catch {return {status:'unknown',reason:'receipt_failure_no_retry'};}
      return {status:'sent',value};
    } catch {try {unknown.run(b.attemptKey);} catch{};return {status:'unknown',reason:'ambiguous_transport_no_retry'};}
  }
  return {mutatePolicy,dispatch,status:(key:string)=>(state.get(key) as {state:string}|undefined)?.state,close:()=>db.close()};
}
