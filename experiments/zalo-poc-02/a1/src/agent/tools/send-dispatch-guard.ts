/** Legacy read-then-send contract is permanently fail-closed.
 * STOP race was reproduced by independent Work: an asynchronous read cannot
 * serialize policy revocation with transport start.
 * Production candidate sends use atomic-send-admission.ts instead.
 */
export type Destination = Readonly<{ accountId: string; threadId: string; recipientId: string; threadType: 'dm' | 'group' }>;
export type Authorization = Readonly<{ destination: Destination; consent: 'opt_in' | 'opt_out' | 'unknown'; humanTakeover: boolean | null; threadStop: boolean | null; globalStop: boolean | null; accountRunning: boolean | null; version: string }>;
export type PolicyReader = (destination: Destination) => Promise<Authorization | null>;
export type AttemptStore = { reserveOnce(key: string): Promise<boolean>; markSent(key: string): Promise<void> };
export type DispatchIntent = Readonly<{ destination: Destination; idempotencyKey: string; expected: Destination }>;
export type DispatchResult = { status: 'sent' } | { status: 'blocked'; reason: string } | { status: 'unknown'; reason: string };
const saneId = (v: string): boolean => typeof v === 'string' && /^[a-zA-Z0-9][a-zA-Z0-9_:@.\-]{0,127}$/.test(v);
/** Deprecated: no reader or in-memory attempt store can authorize transport.
 * All invocations are blocked, including otherwise valid opt-in.
 */
export async function dispatchWithLateGuard(
  intent: DispatchIntent,
  _readPolicy: PolicyReader,
  _store: AttemptStore,
  _send: () => Promise<unknown>,
  _beforeFinalCheck?: () => Promise<void>,
): Promise<DispatchResult> {
  if (!saneId(intent.idempotencyKey)) return {status:'blocked',reason:'invalid_idempotency_key'};
  return {status:'blocked',reason:'unsafe_legacy_non_atomic_dispatch_disabled'};
}
