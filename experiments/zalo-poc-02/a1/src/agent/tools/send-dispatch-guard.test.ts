import test from 'node:test';
import assert from 'node:assert/strict';
import { dispatchWithLateGuard } from './send-dispatch-guard.js';
import type { Authorization, Destination, DispatchIntent, AttemptStore } from './send-dispatch-guard.js';
const destination: Destination = { accountId: 'synthetic_1', threadId: 'user_1', recipientId: 'user_1', threadType: 'dm' };
const intent = (key: string, d: Destination = destination): DispatchIntent => ({ idempotencyKey: key, expected: destination, destination: d });
const ok = (): Authorization => ({ destination, consent: 'opt_in', humanTakeover: false, threadStop: false, globalStop: false, accountRunning: true, version: 'v1' });
const store = () => {
  const seen = new Set<string>(); const sent = new Set<string>();
  const adapter: AttemptStore = {
    reserveOnce: async key => { if (seen.has(key)) return false; seen.add(key); return true; },
    markSent: async key => { sent.add(key); },
  };
  return { adapter, seen, sent };
};
test('legacy send path is disabled even for synthetic opt-in', async () => {
  let sends = 0; const s = store();
  const r = await dispatchWithLateGuard(intent('msg_1'), async () => ok(), s.adapter, async () => { sends++; });
  assert.equal(r.status, 'blocked'); assert.equal(sends, 0); assert.equal(s.sent.size, 0);
});
test('unknown, opt-out, takeover, STOP and paused account fail closed', async () => {
  const scenarios: Array<Authorization | null> = [null, { ...ok(), consent: 'unknown' }, { ...ok(), consent: 'opt_out' }, { ...ok(), humanTakeover: true }, { ...ok(), humanTakeover: null }, { ...ok(), globalStop: true }, { ...ok(), threadStop: true }, { ...ok(), accountRunning: false }];
  for (const [i, policy] of scenarios.entries()) {
    let sends = 0;
    const r = await dispatchWithLateGuard(intent('blocked_'+i), async () => policy, store().adapter, async () => { sends++; });
    assert.equal(r.status, 'blocked'); assert.equal(sends, 0);
  }
});
test('wrong recipient, cross-thread group, malformed recipient and thread type', async () => {
  const cases: Destination[] = [{ ...destination, recipientId: 'user_2' }, { ...destination, threadId: 'group_2', recipientId: 'group_2', threadType: 'group' }, { ...destination, threadId: '../bad' }, { ...destination, threadType: 'evil' as Destination['threadType'] }];
  for (const [i, d] of cases.entries()) {
    let sends = 0; const r = await dispatchWithLateGuard(intent('bad_'+i, d), async () => ok(), store().adapter, async () => { sends++; });
    assert.equal(r.status, 'blocked'); assert.equal(sends, 0);
  }
});
test('queued before opt-out blocks after revocation', async () => {
  let p = ok(); let sends = 0;
  const r = await dispatchWithLateGuard(intent('queue_1'), async () => p, store().adapter, async () => { sends++; }, async () => { p = { ...p, consent: 'opt_out', version: 'v2' }; });
  assert.equal(r.status, 'blocked'); assert.equal(sends, 0);
});
test('mid-multipart STOP blocks second part', async () => {
  let p = ok(); let sends = 0; const s = store();
  assert.equal((await dispatchWithLateGuard(intent('part_1'), async () => p, s.adapter, async () => { sends++; p = { ...p, threadStop: true, version: 'v2' }; })).status, 'sent');
  assert.equal((await dispatchWithLateGuard(intent('part_2'), async () => p, s.adapter, async () => { sends++; })).status, 'blocked'); assert.equal(sends, 1);
});
test('legacy ambiguous send never attempts transport', async () => {
  const s = store(); let sends = 0;
  const run = () => dispatchWithLateGuard(intent('retry_1'), async () => ok(), s.adapter, async () => { sends++; throw Error('ambiguous'); });
  assert.equal((await run()).status, 'blocked'); assert.equal((await run()).status, 'blocked');
  assert.equal((await dispatchWithLateGuard(intent('retry_1'), async () => ok(), s.adapter, async () => { sends++; })).status, 'blocked'); assert.equal(sends, 0);
});
test('policy epoch change while queued blocks', async () => {
  let p = ok(); let sends = 0;
  const r = await dispatchWithLateGuard(intent('epoch_1'), async () => p, store().adapter, async () => { sends++; }, async () => { p = { ...p, version: 'v2' }; });
  assert.equal(r.status, 'blocked'); assert.equal(sends, 0);
});
test('failed initial/final policy read and unavailable idempotency fail closed', async () => {
  let sends = 0; const fail = async (): Promise<Authorization> => { throw Error('offline'); };
  assert.equal((await dispatchWithLateGuard(intent('read_1'), fail, store().adapter, async () => { sends++; })).status, 'blocked');
  let reads = 0;
  assert.equal((await dispatchWithLateGuard(intent('read_2'), async () => { if (++reads > 1) throw Error('offline'); return ok(); }, store().adapter, async () => { sends++; })).status, 'blocked');
  const broken: AttemptStore = { reserveOnce: async () => { throw Error('db'); }, markSent: async () => {} };
  assert.equal((await dispatchWithLateGuard(intent('db_1'), async () => ok(), broken, async () => { sends++; })).status, 'blocked'); assert.equal(sends, 0);
});
