import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';
import {spawnSync, spawn} from 'node:child_process';
import {DatabaseSync} from 'node:sqlite';
import {openSyntheticAtomicAdmission} from './atomic-send-admission.js';
const base={accountId:'synthetic_1',threadId:'user_1',senderId:'user_1',recipientId:'user_1',threadType:'dm' as const,attemptKey:'msg_1:part_1'};
const p=(revision=1)=>({accountId:base.accountId,threadId:base.threadId,senderId:base.senderId,threadType:base.threadType,verified:true,respond:true,retain:false,passiveGroup:false,outbound:true,optedOut:false,takeover:false,stopped:false,running:true,revision,expiresAtMs:1890000000000});
function fixture(){const dir=fs.mkdtempSync(path.join(os.tmpdir(),'poc02atomic-'));return {dir,file:path.join(dir,'guard.db')}}
test('atomic STOP before admission prevents send after microtask',async()=>{const f=fixture();const s=openSyntheticAtomicAdmission(f.file);try{assert.equal(s.mutatePolicy(p()),true);let fake=0;let stopped=false;await Promise.resolve().then(()=>{s.mutatePolicy({...p(2),stopped:true});stopped=true});const r=await s.dispatch(base,async()=>{if(stopped)fake++;return 'ok'},Date.now());assert.equal(r.status,'blocked');assert.equal(fake,0);}finally{s.close();fs.rmSync(f.dir,{recursive:true,force:true})}});
test('already admitted send is in-flight when STOP linearizes later',async()=>{const f=fixture();const s=openSyntheticAtomicAdmission(f.file);try{s.mutatePolicy(p());let started=0;let done:(x:string)=>void=()=>{};const waiting=new Promise<string>(resolve=>{done=resolve});const operation=s.dispatch(base,()=>{started++;return waiting},Date.now());s.mutatePolicy({...p(2),stopped:true});done('ok');const r=await operation;assert.equal(started,1);assert.equal(r.status,'sent');const blocked=await s.dispatch({...base,attemptKey:'msg_1:part_2'},async()=>{started++;return 'bad'},Date.now());assert.equal(blocked.status,'blocked');assert.equal(started,1);}finally{s.close();fs.rmSync(f.dir,{recursive:true,force:true})}});
test('STOP, opt-out, takeover, expiry and unknown deny',async()=>{for(const changes of [{stopped:true},{optedOut:true},{takeover:true},{outbound:false},{verified:false},{expiresAtMs:1}]){const f=fixture();const s=openSyntheticAtomicAdmission(f.file);try{s.mutatePolicy({...p(),...changes});let sends=0;assert.equal((await s.dispatch(base,async()=>{sends++;return 1},Date.now())).status,'blocked');assert.equal(sends,0)}finally{s.close();fs.rmSync(f.dir,{recursive:true,force:true})}}});
test('actual process restart durable idempotency and no retry after unknown',async()=>{const f=fixture();const s=openSyntheticAtomicAdmission(f.file);try{s.mutatePolicy(p());assert.equal((await s.dispatch(base,async()=>{throw Error('ambiguous')},Date.now())).status,'unknown');s.close();const source=new URL('./atomic-send-admission.js',import.meta.url).href;const js='import {openSyntheticAtomicAdmission} from '+JSON.stringify(source)+';const s=openSyntheticAtomicAdmission(process.argv[1]);const result=await s.dispatch('+JSON.stringify(base)+',async()=>{throw Error("duplicate transport invoked")},Date.now());process.stdout.write(result.status+":"+result.reason);s.close()';const child=spawnSync(process.execPath,['--input-type=module','-e',js,f.file],{encoding:'utf8',env:{PATH:process.env.PATH}});assert.equal(child.status,0,child.stderr);assert.equal(child.stdout,'blocked:duplicate_or_uncertain_attempt')}finally{fs.rmSync(f.dir,{recursive:true,force:true})}});
test('policy revision monotonic and group/type binding',async()=>{const f=fixture();const s=openSyntheticAtomicAdmission(f.file);try{s.mutatePolicy(p());assert.equal(s.mutatePolicy(p()),false);assert.throws(()=>s.mutatePolicy({...p(0),stopped:true}),/invalid_policy_mutation/);let sends=0;const bad=await s.dispatch({...base,threadType:'group' as const,recipientId:'group_1'},async()=>{sends++;return 'x'},Date.now());assert.equal(bad.status,'blocked');assert.equal(sends,0);}finally{s.close();fs.rmSync(f.dir,{recursive:true,force:true})}});
test('concurrent updates and sends linearize by transaction in one process',async()=>{const f=fixture();const s=openSyntheticAtomicAdmission(f.file);try{s.mutatePolicy(p());const events:string[]=[];let calls=0;const send=s.dispatch(base,async()=>{events.push('admitted');calls++;return 'ok'},Date.now());const stop=Promise.resolve().then(()=>{s.mutatePolicy({...p(2),stopped:true});events.push('stopped')});await Promise.all([send,stop]);assert.deepEqual(events,['admitted','stopped']);assert.equal(calls,1);assert.equal((await s.dispatch({...base,attemptKey:'next'},async()=>{calls++;return 'wrong'},Date.now())).status,'blocked');assert.equal(calls,1);}finally{s.close();fs.rmSync(f.dir,{recursive:true,force:true})}});

test('scoped read-only snapshot exposes independent passive/retain/outbound and STOP',async()=>{
  const f=fixture(),s=openSyntheticAtomicAdmission(f.file);
  try {
    s.mutatePolicy({...p(),respond:false,retain:true,passiveGroup:true,outbound:false});
    const read=s.readOnly.readSnapshot({accountId:base.accountId,threadId:base.threadId,senderId:base.senderId,threadType:'dm'},Date.now());
    assert.ok(read);assert.equal(read!.respond,false);assert.equal(read!.retain,true);
    assert.equal(read!.passiveGroup,true);assert.equal(read!.outbound,false);assert.equal(Object.isFrozen(read),true);
    assert.equal(s.readOnly.readSnapshot({accountId:base.accountId,threadId:'other',senderId:base.senderId,threadType:'group'}),null);
  } finally {s.close();fs.rmSync(f.dir,{recursive:true,force:true});}
});
test('global STOP and account STOP share policy admission fence',async()=>{
  for(const scope of ['global','account'] as const){
    const f=fixture(),s=openSyntheticAtomicAdmission(f.file);let called=0;
    try {
      s.mutatePolicy(p());
      assert.equal(s.mutateStop(scope,'synthetic_1',true,1),true);
      assert.equal(s.mutateStop(scope,'synthetic_1',false,1),false);
      const snap=s.readOnly.readSnapshot(base)!;
      assert.equal(scope==='global'?snap.globalStopped:snap.accountStopped,true);
      const r=await s.dispatch({...base,attemptKey:'stop_'+scope},async()=>{called++;return 'bad'},Date.now());
      assert.equal(r.status,'blocked');assert.equal(called,0);
      assert.equal(s.mutateStop(scope,'synthetic_1',false,2),true);
      assert.equal((await s.dispatch({...base,attemptKey:'resume_'+scope},async()=>{called++;return 'ok'},Date.now())).status,'sent');
      assert.equal(called,1);
    }finally{s.close();fs.rmSync(f.dir,{recursive:true,force:true});}
  }
});
test('reservation remains durable if transport throws synchronously, no resend after reopen',async()=>{
  const f=fixture(),s=openSyntheticAtomicAdmission(f.file);let calls=0;
  try {
    s.mutatePolicy(p());
    const r=await s.dispatch({...base,attemptKey:'crash_key'},()=>{calls++;throw Error('synchronous start failed')},Date.now());
    assert.equal(r.status,'unknown');assert.equal(calls,1);
    s.close();
    const reopened=openSyntheticAtomicAdmission(f.file);
    try {
      const retry=await reopened.dispatch({...base,attemptKey:'crash_key'},async()=>{calls++;return 'unsafe'},Date.now());
      assert.equal(retry.status,'blocked');assert.equal(calls,1);
    }finally{reopened.close();}
  }finally{fs.rmSync(f.dir,{recursive:true,force:true});}
});
test('mutation rejects non-boolean consent scopes instead of fabricating opt-in',async()=>{
  const f=fixture(),s=openSyntheticAtomicAdmission(f.file);
  try {
    assert.throws(()=>s.mutatePolicy({...p(),passiveGroup:undefined as unknown as boolean}),/invalid_policy_mutation/);
    assert.equal(s.readOnly.readSnapshot(base),null);
  }finally{s.close();fs.rmSync(f.dir,{recursive:true,force:true});}
});

test('cross-process STOP writer waits for SQLite lock and blocks later admission',async()=>{
  const f=fixture(),s=openSyntheticAtomicAdmission(f.file);
  let child:ReturnType<typeof spawn>|undefined;
  try {
    s.mutatePolicy(p());
    const source=new URL('./atomic-send-admission.js',import.meta.url).href;
    const script='import {openSyntheticAtomicAdmission} from '+JSON.stringify(source)+
      ';const s=openSyntheticAtomicAdmission(process.argv[1]);process.stdout.write("READY\\n");'+
      'process.stdin.once("data",()=>{s.mutateStop("global","synthetic_1",true,1);process.stdout.write("DONE\\n");s.close()})';
    child=spawn(process.execPath,['--import','tsx','--input-type=module','-e',script,f.file],{
      stdio:['pipe','pipe','pipe'],env:{PATH:process.env.PATH}
    });
    const ready=await new Promise<string>((resolve,reject)=>{
      child!.stdout!.once('data',v=>resolve(String(v)));
      child!.once('error',reject);
    });
    assert.match(ready,/READY/);
    const other=new DatabaseSync(f.file);
    try {
      other.exec('BEGIN IMMEDIATE');
      child.stdin!.write('GO\n');
      await new Promise(resolve=>setTimeout(resolve,80));
      other.exec('COMMIT');
    }finally{other.close();}
    const exit=await new Promise<number|null>(resolve=>child!.once('exit',resolve));
    assert.equal(exit,0);
    let sendCount=0;
    const denied=await s.dispatch({...base,attemptKey:'after_cross_process_stop'},async()=>{
      sendCount++;return 'bad';
    },Date.now());
    assert.equal(denied.status,'blocked');assert.equal(sendCount,0);
  }finally{if(child?.exitCode===null)child.kill();s.close();fs.rmSync(f.dir,{recursive:true,force:true});}
});
