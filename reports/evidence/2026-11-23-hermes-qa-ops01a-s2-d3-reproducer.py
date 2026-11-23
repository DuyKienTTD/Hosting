"""Pinned offline independent D3 QA. No author tests, network or writes to source."""
import sys,json,platform,argparse,os,subprocess
from pathlib import Path
from datetime import datetime,timezone,timedelta
# Set OPS01A_D3_SOURCE_ROOT to a detached checkout's sandbox directory elsewhere.
ROOT=Path(os.environ.get('OPS01A_D3_SOURCE_ROOT','/data/cache/scratch/pr36_qa_d3_5626bb/sandbox/ops-monitoring-lifecycle'))
SHA='5626bb55072cdcca0d39f3ba57180d3c57af05ad'
BLOB='0043cb1a00ff1a3e9fbc7f1267900ebde02f4769'
actual=subprocess.check_output(['git','hash-object',str(ROOT/'lifecycle.py')],text=True).strip()
if actual!=BLOB:raise RuntimeError(f'SOURCE_DRIFT expected {BLOB} got {actual}')
sys.path.insert(0,str(ROOT))
from lifecycle import Lifecycle
BASE=datetime(2026,1,1,tzinfo=timezone.utc)
CASES=[]
def pkt(sid,sec,sig='bad',**kw):
 x={'sample_id':sid,'observed_at_utc':(BASE+timedelta(seconds=sec)).isoformat(timespec='microseconds').replace('+00:00','Z'),'resource':'kvm2','source':'synthetic','rule_version':'ops-01a-s2-v1','freshness':'fresh','health_status':'observed','signal':sig};x.update(kw);return x
def run(name,inputs,expected,fn,novel=False):
 try:
  observed=fn();status='PASS' if observed==expected else 'FAIL'
 except Exception as exc:observed=f'{type(exc).__name__}: {exc}';status='ERROR'
 CASES.append({'name':name,'inputs':inputs,'expected':expected,'observed':observed,'status':status,'novel_attack':novel,'source_sha':SHA})
 print(name,status)
def opened():
 x=Lifecycle()
 for i in range(3):x.ingest(pkt(f'o{i}',i))
 assert x.state=='OPEN'
 return x
def middle():
 x=opened();x.ingest(pkt('g1',10,'good'));x.ingest(pkt('g2',11,'good'))
 u=pkt('U',12,'unknown');x.ingest(u)
 for sid,t in [('g3',11.1),('g4',11.2)]:x.ingest(pkt(sid,t,'good'))
 return x,u
def r1():
 x,u=middle();b=(x.good_streak,x.state,x.last_ts.isoformat(),len(x.seen),len(x.interruption_replays))
 x.ingest(u);a=(x.good_streak,x.state,x.last_ts.isoformat(),len(x.seen),len(x.interruption_replays),x.audit[-1]['type'])
 return {'before':b,'after':a,'next':[v['kind'] for v in x.ingest(pkt('g5',13,'good'))]}
base=(2,'OPEN','2026-01-01T00:00:11.200000+00:00',7,1)
run('R1_exact_original','bad@0..2;g1@10,g2@11;U@12;g3@11.1,g4@11.2;U@12;g5@13',{'before':base,'after':base+('EXACT_REPLAY',),'next':['RECOVERED']},r1)
def r2():
 x,u=middle();y=Lifecycle.restore(x.snapshot());b=(y.good_streak,y.state,y.last_ts.isoformat(),len(y.seen),len(y.interruption_replays))
 y.ingest(pkt('U',12,'bad',freshness='stale'));a=(y.good_streak,y.state,y.last_ts.isoformat(),len(y.seen),len(y.interruption_replays),y.audit[-1]['type'])
 return {'before':b,'after':a,'next':[v['kind'] for v in y.ingest(pkt('g5',13,'good'))]}
run('R2_conflict_original_restore','R1 sequence;restore;U@12 stale/bad;g5@13',{'before':base,'after':base+('CONFLICTING_REPLAY',),'next':['RECOVERED']},r2)
def collision():
 x,u=middle();pre=x.snapshot();x.ingest(pkt('U',13,'good'));a=(x.audit[-1]['type'],x.snapshot()!=pre and x.good_streak==2,len(x.interruption_replays))
 y=opened();y.ingest(pkt('g1',10,'good'));y.ingest(pkt('g2',11,'good'));y.ingest(pkt('g2',12,'unknown'));b=(y.audit[-1]['type'],y.good_streak,len(y.interruption_replays));return a,b
run('cross_registry_id_conflicts','U@12 then good ID U@13; valid g2@11 then U ID g2@12',(('CONFLICTING_REPLAY',True,1),('CONFLICTING_REPLAY',2,0)),collision)
def rejected_no_poison():
 x=opened();out=[]
 bad=[(pkt('Z',100,'unknown',source='foreign'),'SOURCE_MISMATCH'),(pkt('Z',101,'unknown',rule='WRONG'),'RULE_MISMATCH'),(pkt('Z',102,'unknown',resource='else'),'IDENTITY_MISMATCH'),(pkt('Z',103,'unknown',rule_version='wrong'),'RULE_VERSION_MISMATCH'),(pkt('Z',104,'unknown',signal=float('nan')),'INVALID_PAYLOAD'),(pkt(['Z'],105,'unknown'),'INVALID_SAMPLE_ID')]
 for p,e in bad:
  before=(x.control_snapshot(),len(x.interruption_replays));x.ingest(p);out.append((x.audit[-1]['type']==e,before==(x.control_snapshot(),len(x.interruption_replays))))
 x.ingest(pkt('Z',12,'unknown'));return out+[('TRUSTED_INTERRUPTION'==x.audit[-1]['type'],len(x.interruption_replays)==1)]
run('F2_F3_invalid_foreign_no_registry_poison','six bad Z or malformed IDs at t100..105 then corrected Z@12',[(True,True)]*7,rejected_no_poison)
def time_canon():
 x,u=middle();x.ingest(pkt('U',12,'unknown',observed_at_utc='2026-01-01T00:00:12Z'));a=x.audit[-1]['type'];x.ingest(pkt('U',10,'unknown'));b=x.audit[-1]['type'];x.ingest(pkt('g5',13,'good'));x.ingest(u);c=x.audit[-1]['type'];return a,b,c,x.state,x.good_streak
run('N1_canonical_format_time_rollback','U accepted 12.000000Z; replay 12Z then 10Z; advance g5@13 then exact U',('CONFLICTING_REPLAY','CONFLICTING_REPLAY','EXACT_REPLAY','RECOVERED',0),time_canon,True)
def snapshot_validation():
 x,u=middle();d=json.loads(x.snapshot());out=[]
 mutations=[('missing',{k:v for k,v in d.items() if k!='interruption_replays'}),('list',{**d,'interruption_replays':[]}),('oversized',{**d,'interruption_replays':{f'Z{i}':'{}' for i in range(257)}}),('collision',{**d,'interruption_replays':{'g1':'{}'}}),('bad_id',{**d,'interruption_replays':{'ñ':'{}'}}),('bad_val',{**d,'interruption_replays':{'U':3}}),('version',{**d,'snapshot_version':3})]
 for tag,p in mutations:
  try:Lifecycle.restore(json.dumps(p));out.append((tag,'RESTORED'))
  except Exception as e:out.append((tag,f'{type(e).__name__}:{e}'))
 return out
run('v2_restore_rejects_corruption','v2 missing/list/257/collision/nonascii-id/int-value/version=3',[(x,'ValueError:'+('UNSUPPORTED_SNAPSHOT_VERSION' if x=='version' else 'REPLAY_ID_COLLISION' if x=='collision' else 'INVALID_INTERRUPTION_REPLAY_REGISTRY')) for x in ('missing','list','oversized','collision','bad_id','bad_val','version')],snapshot_validation)
def v1():
 x,u=middle();d=json.loads(x.snapshot());d.pop('snapshot_version');d.pop('interruption_replays');a=None
 try:Lifecycle.restore(json.dumps(d));a='RESTORED'
 except Exception as e:a=str(e)
 y=opened();e=json.loads(y.snapshot());e.pop('snapshot_version');e.pop('interruption_replays');z=Lifecycle.restore(json.dumps(e));return (a,z.state,len(z.interruption_replays))
run('legacy_v1_with_vs_without_interruption','v1 of middle (audit U) and v1 of opened (no U)',('LEGACY_INTERRUPTION_REPLAY_UNAVAILABLE','OPEN',0),v1)
def cap():
 x=Lifecycle();c=[]
 for i in range(255):x.ingest(pkt(f'U{i}',i+1,'unknown'))
 c.append(len(x.interruption_replays));x.ingest(pkt('U255',256,'unknown'));c.append((len(x.interruption_replays),x.audit[-1]['type']))
 b=(x.control_snapshot(),x.snapshot());x.ingest(pkt('U256',257,'unknown'));c.append((len(x.interruption_replays),x.audit[-1]['type'],x.control_snapshot()==b[0],x.snapshot()!=b[1]))
 x.ingest(pkt('U0',1,'unknown'));c.append((x.audit[-1]['type'],len(x.interruption_replays)))
 y=Lifecycle.restore(x.snapshot());y.ingest(pkt('newgood',258,'good'));c.append((y.audit[-1]['type'],y.state,y.last_ts,len(y.seen)))
 y.ingest(pkt('newbad',259,'bad'));c.append((y.audit[-1]['type'],y.state,y.last_ts,len(y.seen)))
 return c
run('capacity_256_257_restore_freeze','U0..U255 unknown t1..256;257th U256;old U0; restore; new good/bad', [255,(256,'TRUSTED_INTERRUPTION'),(256,'INTERRUPTION_REGISTRY_FULL',True,True),('EXACT_REPLAY',256),('INTERRUPTION_REGISTRY_FULL','NORMAL',None,0),('INTERRUPTION_REGISTRY_FULL','NORMAL',None,0)],cap)
def freeze_open():
 x=opened();x.ingest(pkt('g1',10,'good'));x.ingest(pkt('g2',11,'good'))
 for i in range(256):x.ingest(pkt(f'I{i}',12+i,'unknown'))
 b=(x.state,x.good_streak,x.last_ts.isoformat(),x.incident_seq,x.last_alert_ts.isoformat(),len(x.seen),len(x.interruption_replays))
 x.ingest(pkt('g3',1000,'good'));a=x.audit[-1]['type'];x.ingest(pkt('b3',1001,'bad'));return b,a,x.audit[-1]['type'],x.state,x.good_streak,x.last_ts.isoformat(),x.incident_seq,x.last_alert_ts.isoformat(),len(x.seen),len(x.interruption_replays)
run('N2_cap_freezes_open_incident_recovery','OPEN;g1@10,g2@11;256 unique U; new good@1000,bad@1001',(('OPEN',0,'2026-01-01T00:00:11+00:00',1,'2026-01-01T00:00:02+00:00',5,256),'INTERRUPTION_REGISTRY_FULL','INTERRUPTION_REGISTRY_FULL','OPEN',0,'2026-01-01T00:00:11+00:00',1,'2026-01-01T00:00:02+00:00',5,256),freeze_open,True)
def forged_snapshot():
 x,u=middle();d=json.loads(x.snapshot());d['interruption_replays']={};d['audit']=[];y=Lifecycle.restore(json.dumps(d));y.ingest(u)
 return y.audit[-1]['type'],len(y.interruption_replays),y.good_streak
run('N3_untrusted_v2_snapshot_history_erasure','v2 after middle; delete replay registry and diagnostic audit; restore; replay U@12',('TRUSTED_INTERRUPTION',1,0),forged_snapshot,True)
def snapshot_schema():
 x,u=middle();d=json.loads(x.snapshot());y=Lifecycle.restore(json.dumps(d));p=json.loads((ROOT/'policy.json').read_text());return json.loads(y.snapshot())==d,p['replay_registry_policy']['max_interruption_ids'],p['replay_registry_policy']['snapshot_version'],p['s1_composition'].startswith('S1_EQUIVALENCE_FIXTURE_ONLY')
run('v2_equality_policy_S1_boundary','middle; roundtrip v2; parse policy',(True,256,2,True),snapshot_schema)
def cooldown(delta,recovered):
 x=opened()
 if recovered:
  for i in range(3):x.ingest(pkt('r'+str(i),10+i,'good'))
 for i in range(3):e=x.ingest(pkt(f'c{delta}-{i}',delta+i,'bad'))
 return e[0]['kind'],e[0]['notification_emitted'],e[0]['incident_seq']
for delta in (899,900,901):
 run('cooldown_open_'+str(delta),f'OPEN bad@{delta}..+2',(('SUPPRESSED_COOLDOWN' if delta==899 else 'NOTIFICATION'),delta!=899,1),lambda d=delta:cooldown(d,False))
 run('cooldown_recovered_'+str(delta),f'RECOVERED bad@{delta}..+2',('OPEN',delta!=899,2),lambda d=delta:cooldown(d,True))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--json',required=True);args=ap.parse_args()
 data={'task':'QA-A1-OPS01A-S2-D3-HERMES','pr36_head':SHA,'source_blob':'0043cb1a00ff1a3e9fbc7f1267900ebde02f4769','runtime':platform.python_version(),'cases':CASES,'total':len(CASES),'passed':sum(c['status']=='PASS' for c in CASES),'failed':sum(c['status']!='PASS' for c in CASES)}
 Path(args.json).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
 print('TOTAL',data['total'],'PASS',data['passed'],'FAIL',data['failed'])
