/** Offline candidate only. Not yet wired into application send paths. */
export type Destination = Readonly<{ accountId: string; threadId: string; recipientId: string; threadType: 'dm' | 'group' }>;
export type Authorization = Readonly<{ destination: Destination; consent: 'opt_in' | 'opt_out' | 'unknown'; humanTakeover: boolean | null; threadStop: boolean | null; globalStop: boolean | null; accountRunning: boolean | null; version: string }>;
export type PolicyReader = (destination: Destination) => Promise<Authorization | null>;
export type AttemptStore = { reserveOnce(key: string): Promise<boolean>; markSent(key: string): Promise<void> };
export type DispatchIntent = Readonly<{ destination: Destination; idempotencyKey: string; expected: Destination }>;
export type DispatchResult = { status: 'sent' } | { status: 'blocked'; reason: string } | { status: 'unknown'; reason: string };
const saneId = (v: string): boolean => typeof v === 'string' && /^[a-zA-Z0-9][a-zA-Z0-9_:@.\-]{0,127}$/.test(v);
const same = (a: Destination, b: Destination): boolean => a.accountId === b.accountId && a.threadId === b.threadId && a.recipientId === b.recipientId && a.threadType === b.threadType;
function allowed(intent: DispatchIntent, current: Authorization | null): string | null {
  const d = intent.destination;
  if (![d.accountId, d.threadId, d.recipientId, intent.idempotencyKey].every(saneId)) return 'invalid_identity';
  if (d.threadType !== 'dm' && d.threadType !== 'group') return 'invalid_thread_type';
  if (!same(d, intent.expected)) return 'wrong_recipient_or_type';
  if (d.threadType === 'dm' && d.recipientId !== d.threadId) return 'dm_target_mismatch';
  if (!current || !same(current.destination, d) || !saneId(current.version)) return 'unknown_policy_or_binding';
  if (current.consent !== 'opt_in') return 'opt_out_or_unknown_consent';
  if (current.humanTakeover !== false) return 'human_takeover_or_unknown';
  if (current.globalStop !== false || current.threadStop !== false) return 'stopped_or_unknown';
  if (current.accountRunning !== true) return 'not_running_or_unknown';
  return null;
}
/** Requires atomic durable AttemptStore and an already audited transport closure.
 * An ambiguous send permanently retains its reserved idempotency key.
 */
export async function dispatchWithLateGuard(intent: DispatchIntent, readPolicy: PolicyReader, store: AttemptStore, send: () => Promise<unknown>, beforeFinalCheck?: () => Promise<void>): Promise<DispatchResult> {
  if (!saneId(intent.idempotencyKey)) return { status: 'blocked', reason: 'invalid_idempotency_key' };
  let first: Authorization | null;
  try { first = await readPolicy(intent.destination); } catch { return { status: 'blocked', reason: 'policy_read_failed' }; }
  const initial = allowed(intent, first);
  if (initial) return { status: 'blocked', reason: initial };
  try {
    if (!(await store.reserveOnce(intent.idempotencyKey))) return { status: 'blocked', reason: 'duplicate_or_uncertain_attempt' };
  } catch { return { status: 'blocked', reason: 'idempotency_unavailable' }; }
  try {
    if (beforeFinalCheck) await beforeFinalCheck();
    const fresh = await readPolicy(intent.destination);
    const reason = allowed(intent, fresh);
    if (reason) return { status: 'blocked', reason };
    if (fresh!.version !== first!.version) return { status: 'blocked', reason: 'policy_changed_since_enqueue' };
  } catch { return { status: 'blocked', reason: 'policy_recheck_failed' }; }
  try { await send(); } catch { return { status: 'unknown', reason: 'delivery_outcome_uncertain_no_retry' }; }
  try { await store.markSent(intent.idempotencyKey); } catch { return { status: 'unknown', reason: 'delivered_but_receipt_failed_no_retry' }; }
  return { status: 'sent' };
}
