import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { openDurableAttemptStore } from './durable-attempt-store.js';
function fixture() { const dir=fs.mkdtempSync(path.join(os.tmpdir(),'poc02-')); return {dir,db:path.join(dir,'attempts.db')}; }
test('transactional same key reserve only once',async()=>{const f=fixture();try{const s=openDurableAttemptStore(f.db);assert.equal(await s.reserveOnce('a1:dm:u1:part1'),true);assert.equal(await s.reserveOnce('a1:dm:u1:part1'),false);await s.markSent('a1:dm:u1:part1');assert.equal(s.status('a1:dm:u1:part1'),'sent');s.close();}finally{fs.rmSync(f.dir,{recursive:true,force:true})}});
test('actual Node process restart keeps uncertain reservation',async()=>{const f=fixture();try{const s=openDurableAttemptStore(f.db);assert.equal(await s.reserveOnce('a1:dm:u1:file1'),true);s.close();const child=spawnSync(process.execPath,['--experimental-strip-types','--input-type=module','-e',"import {openDurableAttemptStore} from "+JSON.stringify(new URL('./durable-attempt-store.ts',import.meta.url).href)+"; const s=openDurableAttemptStore(process.argv[1]);const result=await s.reserveOnce('a1:dm:u1:file1');s.close();process.stdout.write(String(result));",f.db],{encoding:'utf8',env:{PATH:process.env.PATH}});assert.equal(child.status,0,child.stderr);assert.equal(child.stdout,'false');}finally{fs.rmSync(f.dir,{recursive:true,force:true})}});
test('different segment key distinct, missing receipt rejected',async()=>{const f=fixture();try{const s=openDurableAttemptStore(f.db);assert.equal(await s.reserveOnce('a1:dm:u1:p1'),true);assert.equal(await s.reserveOnce('a1:dm:u1:p2'),true);assert.equal(s.status('a1:dm:u1:p2'),'reserved');await assert.rejects(s.markSent('a1:dm:u1:never'));s.close();}finally{fs.rmSync(f.dir,{recursive:true,force:true})}});
