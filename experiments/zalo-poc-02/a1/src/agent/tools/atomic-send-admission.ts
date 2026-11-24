import { DatabaseSync } from 'node:sqlite';

/** Offline synthetic policy authority, not connected to Zalo or real consent. */
export type SendBinding = Readonly<{
  accountId: string; threadId: string; senderId: string; recipientId: string;
  threadType: 'dm' | 'group'; attemptKey: string;
}>;
export type PolicyMutation = Readonly<{
  accountId: string; threadId: string; senderId: string; threadType: 'dm' | 'group';
  verified: boolean; respond: boolean; retain: boolean; passiveGroup: boolean; outbound: boolean;
  optedOut: boolean; takeover: boolean; stopped: boolean; running: boolean;
  revision: number; expiresAtMs: number;
}>;
export type PolicySnapshot = Readonly<PolicyMutation & {globalStopped:boolean;accountStopped:boolean;observedAtMs:number}>;
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
 verified INTEGER NOT NULL, can_respond INTEGER NOT NULL, can_retain INTEGER NOT NULL, passive_group INTEGER NOT NULL,
 can_outbound INTEGER NOT NULL, opted_out INTEGER NOT NULL, takeover INTEGER NOT NULL,
 stopped INTEGER NOT NULL, running INTEGER NOT NULL, revision INTEGER NOT NULL,
 expires_at_ms INTEGER NOT NULL,
 PRIMARY KEY(account_id,thread_id,sender_id,thread_type));
CREATE TABLE IF NOT EXISTS synthetic_outbound_stops (scope TEXT NOT NULL,scope_id TEXT NOT NULL,stopped INTEGER NOT NULL,revision INTEGER NOT NULL,PRIMARY KEY(scope,scope_id));
CREATE TABLE IF NOT EXISTS synthetic_outbound_attempts (
 key TEXT PRIMARY KEY, state TEXT NOT NULL CHECK(state IN ('reserved','admitted','sent','unknown')),
 account_id TEXT NOT NULL, thread_id TEXT NOT NULL, revision INTEGER NOT NULL);
`);
  const getStop = db.prepare("SELECT stopped FROM synthetic_outbound_stops WHERE scope=? AND scope_id=?");
  const stopRev=db.prepare("SELECT revision FROM synthetic_outbound_stops WHERE scope=? AND scope_id=?");
  const putStop=db.prepare("INSERT INTO synthetic_outbound_stops VALUES(?,?,?,?) ON CONFLICT(scope,scope_id) DO UPDATE SET stopped=excluded.stopped,revision=excluded.revision");
  const getPolicy = db.prepare(`SELECT * FROM synthetic_outbound_policy
    WHERE account_id=? AND thread_id=? AND sender_id=? AND thread_type=?`);
  const current = db.prepare(`SELECT revision FROM synthetic_outbound_policy
    WHERE account_id=? AND thread_id=? AND sender_id=? AND thread_type=?`);
  const upsert = db.prepare(`INSERT INTO synthetic_outbound_policy VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ON CONFLICT(account_id,thread_id,sender_id,thread_type) DO UPDATE SET
    verified=excluded.verified, can_respond=excluded.can_respond,
    can_retain=excluded.can_retain, passive_group=excluded.passive_group, can_outbound=excluded.can_outbound,
    opted_out=excluded.opted_out, takeover=excluded.takeover, stopped=excluded.stopped,
    running=excluded.running, revision=excluded.revision, expires_at_ms=excluded.expires_at_ms`);
  const reserve = db.prepare(`INSERT OR IGNORE INTO synthetic_outbound_attempts
    (key,state,account_id,thread_id,revision) VALUES(?,'reserved',?,?,0)`);
  const admit=db.prepare("UPDATE synthetic_outbound_attempts SET state='admitted',revision=? WHERE key=? AND state='reserved'");
  const sent = db.prepare(`UPDATE synthetic_outbound_attempts SET state='sent' WHERE key=? AND state='admitted'`);
  const unknown = db.prepare(`UPDATE synthetic_outbound_attempts SET state='unknown' WHERE key=? AND state='admitted'`);
  const state = db.prepare(`SELECT state FROM synthetic_outbound_attempts WHERE key=?`);

  /** STOP/opt-out/takeover writer is serialized against dispatch admission. */
  function mutatePolicy(p: PolicyMutation): boolean {
    if (!valid(p) || ['verified','respond','retain','passiveGroup','outbound','optedOut','takeover','stopped','running'].some(k=>typeof (p as unknown as Record<string,unknown>)[k]!=='boolean')) throw Error('invalid_policy_mutation');
    db.exec('BEGIN IMMEDIATE');
    try {
      const row = current.get(p.accountId,p.threadId,p.senderId,p.threadType) as {revision:number}|undefined;
      if (row && p.revision <= row.revision) { db.exec('ROLLBACK'); return false; }
      upsert.run(p.accountId,p.threadId,p.senderId,p.threadType,
        Number(p.verified),Number(p.respond),Number(p.retain),Number(p.passiveGroup),Number(p.outbound),
        Number(p.optedOut),Number(p.takeover),Number(p.stopped),Number(p.running),
        p.revision,p.expiresAtMs);
      db.exec('COMMIT'); return true;
    } catch(e) {db.exec('ROLLBACK');throw e;}
  }
  function readSnapshot(identity:Pick<SendBinding,'accountId'|'threadId'|'senderId'|'threadType'>,nowMs=Date.now()):PolicySnapshot|null{
    if (![identity.accountId,identity.threadId,identity.senderId].every(id)) return null;
    const q=getPolicy.get(identity.accountId,identity.threadId,identity.senderId,identity.threadType) as Record<string,number>|undefined;
    if(!q||!Number.isSafeInteger(nowMs))return null;
    return Object.freeze({...identity,verified:Boolean(q.verified),respond:Boolean(q.can_respond),retain:Boolean(q.can_retain),
      passiveGroup:Boolean(q.passive_group),outbound:Boolean(q.can_outbound),optedOut:Boolean(q.opted_out),
      takeover:Boolean(q.takeover),stopped:Boolean(q.stopped),running:Boolean(q.running),
      revision:q.revision,expiresAtMs:q.expires_at_ms,observedAtMs:nowMs,
      globalStopped:Boolean((getStop.get('global','*') as {stopped:number}|undefined)?.stopped),
      accountStopped:Boolean((getStop.get('account',identity.accountId) as {stopped:number}|undefined)?.stopped)});
  }
  function mutateStop(scope:'global'|'account',accountId:string,stopped:boolean,revision:number):boolean{
    const scopeId=scope==='global'?'*':accountId;
    if(!['global','account'].includes(scope)||(scope==='account'&&!id(accountId))||typeof stopped!=='boolean'||!Number.isSafeInteger(revision)||revision<1)throw Error('invalid_stop');
    db.exec('BEGIN IMMEDIATE');
    try{const old=stopRev.get(scope,scopeId) as {revision:number}|undefined;
      if(old&&revision<=old.revision){db.exec('ROLLBACK');return false}
      putStop.run(scope,scopeId,Number(stopped),revision);db.exec('COMMIT');return true;
    }catch(e){try{db.exec('ROLLBACK')}catch{};throw e}
  }
  /** Reservation is committed BEFORE transport can begin, surviving crash/commit failure.
   * Same SQLite writer lock fences STOP mutation and synchronous transport initiation.
   * Already admitted in-flight delivery cannot be retracted; deferred network adapters must
   * perform actual initiation within this fence, not from a later microtask.
   */
  async function dispatch<T>(b:SendBinding,transport:()=>Promise<T>,nowMs:number):Promise<AdmissionOutcome<T>>{
    if(![b.accountId,b.threadId,b.senderId,b.recipientId,b.attemptKey].every(id)||
      (b.threadType!=='dm'&&b.threadType!=='group')||
      (b.threadType==='dm'&&b.senderId!==b.threadId)||b.recipientId!==b.threadId||
      !Number.isSafeInteger(nowMs))return {status:'blocked',reason:'invalid_binding'};
    try {
      db.exec('BEGIN IMMEDIATE');
      const reserved=reserve.run(b.attemptKey,b.accountId,b.threadId).changes===1;
      db.exec('COMMIT');
      if(!reserved)return {status:'blocked',reason:'duplicate_or_uncertain_attempt'};
    }catch {try{db.exec('ROLLBACK')}catch{};return {status:'blocked',reason:'reservation_not_durable'}}
    let call:Promise<T>|undefined,reason:string|undefined,began=false;
    try {
      db.exec('BEGIN IMMEDIATE');
      const q=readSnapshot(b,nowMs);
      reason=!q?'unknown_policy':!q.verified?'unverified_policy':!q.outbound?'no_outbound':
        q.optedOut?'opted_out':q.takeover?'takeover':q.stopped||q.globalStopped||q.accountStopped?'stop':
        !q.running?'not_running':q.expiresAtMs<=nowMs?'expired':undefined;
      if(!reason){
        if(admit.run(q!.revision,b.attemptKey).changes!==1)reason='not_reserved';
        else {try{began=true;call=Promise.resolve(transport())}catch{reason='transport_sync_throw'}}
      }
      db.exec('COMMIT');
    }catch{try{db.exec('ROLLBACK')}catch{};return {status:'unknown',reason:'admission_commit_uncertain_no_retry'}}
    if(reason)return began?{status:'unknown',reason}:{status:'blocked',reason};
    if(!call)return {status:'unknown',reason:'not_started'};
    try {const value=await call;try{if(sent.run(b.attemptKey).changes!==1)return {status:'unknown',reason:'receipt_missing'}}catch{return {status:'unknown',reason:'receipt_failed'}}return {status:'sent',value}}
    catch{try{unknown.run(b.attemptKey)}catch{};return {status:'unknown',reason:'ambiguous_delivery_no_retry'}}
  }
  return {mutatePolicy,mutateStop,readSnapshot,readOnly:Object.freeze({readSnapshot}),dispatch,
    status:(k:string)=>(state.get(k) as {state:string}|undefined)?.state,close:()=>db.close()};
}
