import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { openDurableAttemptStore } from './durable-attempt-store.js';
import { sendWithOutboundGuard, setOfflineOutboundGuardRuntime, OutboundGuardDenied } from './outbound-guard-runtime.js';
import type { Authorization, Destination } from './send-dispatch-guard.js';

const destination: Destination = { accountId: 'synthetic_1', threadId: 'user_1', recipientId: 'user_1', threadType: 'dm' };
const policy = (): Authorization => ({ destination, consent: 'opt_in', humanTakeover: false, globalStop: false, threadStop: false, accountRunning: true, version: 'epoch_1' });
function sandbox() { const dir=fs.mkdtempSync(path.join(os.tmpdir(),'send-guard-runtime-')); return { dir, db: path.join(dir,'attempts.db') }; }
test('late guard sends only once with durable SQLite key', async () => {
  const f=sandbox(), store=openDurableAttemptStore(f.db); let sends=0;
  try {
    setOfflineOutboundGuardRuntime({ readPolicy: async()=>policy(), attempts:store });
    const args={ threadKey:'synthetic_1:user_1', threadId:'user_1', threadType:0, stableKey:'chat_synthetic_1_user_1_msg1:segment_1', send:async()=>{sends++;return {fake:true};} };
    assert.deepEqual(await sendWithOutboundGuard(args),{fake:true});
    await assert.rejects(sendWithOutboundGuard(args), OutboundGuardDenied);
    assert.equal(sends,1);
  } finally {setOfflineOutboundGuardRuntime(null);store.close();fs.rmSync(f.dir,{recursive:true,force:true});}
});
test('STOP arriving after enqueue but before final send denies',async()=>{
  const f=sandbox(),store=openDurableAttemptStore(f.db);let reads=0,sends=0;
  try{
    setOfflineOutboundGuardRuntime({ readPolicy:async()=>{ reads++;return reads>=2?{...policy(),threadStop:true,version:'epoch_2'}:policy(); },attempts:store });
    await assert.rejects(sendWithOutboundGuard({ threadKey:'synthetic_1:user_1',threadId:'user_1',threadType:0,stableKey:'stop_1',send:async()=>{sends++;} }), OutboundGuardDenied);
    assert.equal(sends,0);
  }finally{setOfflineOutboundGuardRuntime(null);store.close();fs.rmSync(f.dir,{recursive:true,force:true});}
});
test('revoke opt-in and human takeover each deny final fake send',async()=>{
  for(const change of [{consent:'opt_out',version:'epoch_2'} as const,{humanTakeover:true,version:'epoch_2'} as const]){
    const f=sandbox(),store=openDurableAttemptStore(f.db);let reads=0,sends=0;
    try{
      setOfflineOutboundGuardRuntime({readPolicy:async()=>++reads===1?policy():{...policy(),...change},attempts:store});
      await assert.rejects(sendWithOutboundGuard({threadKey:'synthetic_1:user_1',threadId:'user_1',threadType:0,stableKey:'takeover_1',send:async()=>{sends++;}}),OutboundGuardDenied);
      assert.equal(sends,0);
    }finally{setOfflineOutboundGuardRuntime(null);store.close();fs.rmSync(f.dir,{recursive:true,force:true});}
  }
});
test('unknown policy, malformed identity and unset policy block without transport',async()=>{
  let sends=0;
  await assert.rejects(sendWithOutboundGuard({threadKey:'synthetic_1:user_1',threadId:'user_1',threadType:0,stableKey:'none_1',send:async()=>{sends++;}}),OutboundGuardDenied);
  const f=sandbox(),store=openDurableAttemptStore(f.db);
  try{
    setOfflineOutboundGuardRuntime({readPolicy:async()=>policy(),attempts:store});
    await assert.rejects(sendWithOutboundGuard({threadKey:'synthetic_1:user_1',threadId:'other_1',threadType:0,stableKey:'wrong_1',send:async()=>{sends++;}}),OutboundGuardDenied);
    await assert.rejects(sendWithOutboundGuard({threadKey:'synthetic_1:user_1',threadId:'user_1',threadType:99,stableKey:'bad_1',send:async()=>{sends++;}}),OutboundGuardDenied);
    assert.equal(sends,0);
  }finally{setOfflineOutboundGuardRuntime(null);store.close();fs.rmSync(f.dir,{recursive:true,force:true});}
});
