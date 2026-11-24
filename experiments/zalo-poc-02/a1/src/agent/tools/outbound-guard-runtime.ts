import { dispatchWithLateGuard, type PolicyReader, type AttemptStore, type Destination } from './send-dispatch-guard.js';

/** OFFLINE POC: nothing registers this in production; missing binding denies every send.
 * Integration owner must replace this per-process adapter with A2-approved durable
 * policy/consent snapshots, including a shared STOP fence.
 */
let runtime: { readPolicy: PolicyReader; attempts: AttemptStore } | null = null;
export function setOfflineOutboundGuardRuntime(value: { readPolicy: PolicyReader; attempts: AttemptStore } | null): void {
  runtime = value;
}
export class OutboundGuardDenied extends Error {
  constructor(readonly reason: string) { super('outbound_guard_' + reason); }
}
export async function sendWithOutboundGuard(input: {
  threadKey: string;
  threadId: string;
  threadType: number;
  stableKey: string | undefined;
  send: () => Promise<unknown>;
}): Promise<unknown> {
  if (!runtime) throw new OutboundGuardDenied('missing_authoritative_policy');
  const pos = input.threadKey.indexOf(':');
  const accountId = pos > 0 ? input.threadKey.slice(0,pos) : '';
  const binding = pos > 0 ? input.threadKey.slice(pos+1) : '';
  if (!accountId || binding !== input.threadId || !input.stableKey) throw new OutboundGuardDenied('missing_or_mismatched_binding');
  const kind = input.threadType === 0 ? 'dm' : input.threadType === 1 ? 'group' : null;
  if (!kind) throw new OutboundGuardDenied('unknown_thread_type');
  const destination: Destination = { accountId, threadId: input.threadId, recipientId: input.threadId, threadType: kind };
  let value: unknown;
  const result = await dispatchWithLateGuard({
    destination,
    expected: destination,
    idempotencyKey: input.stableKey,
  }, runtime.readPolicy, runtime.attempts, async () => { value = await input.send(); });
  if (result.status !== 'sent') throw new OutboundGuardDenied(result.reason);
  return value;
}
