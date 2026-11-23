"""Independent offline PR36 QA probes. Only imports pinned source; no network/write."""
import sys,json,copy,platform,subprocess
from pathlib import Path
sys.path.insert(0,'/data/cache/scratch/pr36_qa_6838ca/sandbox/ops-monitoring-lifecycle')
from lifecycle import Lifecycle
from datetime import datetime,timezone,timedelta
R=[]
BASE=datetime(2026,1,1,tzinfo=timezone.utc)
def sample(id,sec,signal='bad',**over):
 x={'sample_id':id,'observed_at_utc':(BASE+timedelta(seconds=sec)).strftime('%Y-%m-%dT%H:%M:%SZ'),'resource':'kvm2','source':'synthetic','rule_version':'ops-01a-s2-v1','freshness':'fresh','health_status':'observed','signal':signal}
 x.update(over);return x
def put(x,id,sec,signal='bad',**over):return x.ingest(sample(id,sec,signal,**over))
def open_instance():
 x=Lifecycle(); events=[]
 for i in range(3):events+=put(x,f'o{i}',i)
 assert len(events)==1 and events[0]['kind']=='OPEN';return x
def check(name,expected,fn):
 try:observed=fn();status='PASS' if observed==expected else 'FAIL'
 except Exception as e:observed=f'{type(e).__name__}: {e}';status='ERROR'
 R.append({'case':name,'expected':expected,'observed':observed,'status':status})
 print(name,status,'observed=',observed)
def f1_good():
 x=open_instance();put(x,'g1',10,'good');put(x,'g2',11,'good');last=x.last_ts;seen=dict(x.seen);seq=x.incident_seq;alert=x.last_alert_ts
 put(x,'u',12,'unknown'); a=(x.audit[-1]['type'],x.state,x.good_streak,x.last_ts==last,x.seen==seen,x.incident_seq==seq,x.last_alert_ts==alert)
 put(x,'g3',13,'good');before=x.state
 put(x,'g4',14,'good');e=put(x,'g5',15,'good')
 return (a,before,[v['kind'] for v in e])
check('F1_open_good2_unknown_good3',(('TRUSTED_INTERRUPTION','OPEN',0,True,True,True,True),'OPEN',['RECOVERED']),f1_good)
def f1_bad(state):
 x=Lifecycle() if state=='NORMAL' else open_instance()
 if state=='RECOVERED':
  for i in range(3):put(x,f'r{i}',10+i,'good')
 seq=x.incident_seq;put(x,'b1',20);put(x,'b2',21);last=x.last_ts;seen=dict(x.seen)
 put(x,'u',22,'bad',health_status='blocked');before=(x.bad_streak,x.last_ts==last,x.seen==seen,x.incident_seq==seq)
 a=[put(x,f'b{i}',22+i) for i in range(3,6)]
 return (before,[e[0]['kind'] if e else None for e in a],x.incident_seq)
check('F1_normal_bad2_blocked_bad3',( (0,True,True,True),[None,None,'OPEN'],1),lambda:f1_bad('NORMAL'))
check('F1_recovered_bad2_blocked_bad3',( (0,True,True,True),[None,None,'OPEN'],2),lambda:f1_bad('RECOVERED'))
def seen_interruption():
 x=open_instance();put(x,'g1',10,'good');put(x,'g2',11,'good');before=x.control_snapshot();put(x,'g2',12,'unknown');a=x.audit[-1]['type'];same=before==x.control_snapshot();e=put(x,'g3',13,'good');return a,same,[v['kind'] for v in e]
check('F1_seen_id_interruption_ignored_then_valid',('CONFLICTING_REPLAY',True,['RECOVERED']),seen_interruption)
def stale_interruption():
 x=open_instance();put(x,'g1',10,'good');put(x,'g2',11,'good');before=x.control_snapshot();put(x,'u',11,'unknown');a=x.audit[-1]['type'];same=before==x.control_snapshot();e=put(x,'g3',12,'good');return a,same,[v['kind'] for v in e]
check('F1_stale_utc_interruption_ignored',('NON_ADVANCING_TIMESTAMP',True,['RECOVERED']),stale_interruption)
def foreign_interruption():
 x=open_instance();put(x,'g1',10,'good');put(x,'g2',11,'good');out=[]
 for n,kw in enumerate([{'source':'else'},{'resource':'else'},{'rule_version':'else'},{'rule':'WRONG'}]):
  before=x.control_snapshot();put(x,f'bad{n}',100+n,'unknown',**kw);out.append((x.audit[-1]['type'],before==x.control_snapshot()))
 e=put(x,'g3',12,'good')
 return out,[v['kind'] for v in e]
check('F1_foreign_identity_no_reset',([('SOURCE_MISMATCH',True),('IDENTITY_MISMATCH',True),('RULE_VERSION_MISMATCH',True),('RULE_MISMATCH',True)],['RECOVERED']),foreign_interruption)
def interrupt_replay():
 x=open_instance();put(x,'g1',10,'good');put(x,'g2',11,'good');u=sample('U',12,'unknown');put(x,'U',12,'unknown')
 put(x,'g3',13,'good');put(x,'g4',14,'good');pre=(x.good_streak,x.last_ts.isoformat(),len(x.seen))
 x.ingest(u); post=(x.good_streak,x.last_ts.isoformat(),len(x.seen),x.audit[-1]['type']);e=put(x,'g5',15,'good')
 return (pre,post,[v['kind'] for v in e])
# Desired idempotent interruption replay must not break a newer qualifying streak twice.
check('NOVEL_interruption_replayed_after_watermark_advanced',((2,'2026-01-01T00:00:14+00:00',7),(2,'2026-01-01T00:00:14+00:00',7,'NON_ADVANCING_TIMESTAMP'),['RECOVERED']),interrupt_replay)
def replay_before_watermark_catches_up():
 x=open_instance();put(x,'g1',10,'good');put(x,'g2',11,'good')
 u=sample('U',12,'unknown');x.ingest(u)
 x.ingest(sample('g3',11,'good',observed_at_utc='2026-01-01T00:00:11.100000Z'))
 x.ingest(sample('g4',11,'good',observed_at_utc='2026-01-01T00:00:11.200000Z'))
 pre=(x.good_streak,x.state,x.last_ts.isoformat(),len(x.seen))
 x.ingest(u)
 post=(x.good_streak,x.state,x.last_ts.isoformat(),len(x.seen),x.audit[-1]['type'])
 events=put(x,'g5',13,'good')
 return pre,post,[e['kind'] for e in events]
# After U, two distinct fresh goods were accepted. Re-delivery of U must be idempotent.
check('NOVEL_unrecorded_interruption_replay_before_clock_catches_up',((2,'OPEN','2026-01-01T00:00:11.200000+00:00',7),(2,'OPEN','2026-01-01T00:00:11.200000+00:00',7,'EXACT_REPLAY'),['RECOVERED']),replay_before_watermark_catches_up)
def conflicting_interrupt_replay_after_restore():
 x=open_instance();put(x,'g1',10,'good');put(x,'g2',11,'good')
 x.ingest(sample('U',12,'unknown'))
 for i,sec in ((3,'11.100000'),(4,'11.200000')):
  x.ingest(sample(f'g{i}',11,'good',observed_at_utc=f'2026-01-01T00:00:{sec}Z'))
 y=Lifecycle.restore(x.snapshot());before=(y.good_streak,y.state,y.last_ts.isoformat(),len(y.seen))
 y.ingest(sample('U',12,'bad',freshness='stale'))
 after=(y.good_streak,y.state,y.last_ts.isoformat(),len(y.seen),y.audit[-1]['type'])
 e=put(y,'g5',13,'good')
 return before,after,[v['kind'] for v in e]
check('NOVEL_conflicting_interruption_replay_after_restore',((2,'OPEN','2026-01-01T00:00:11.200000+00:00',7),(2,'OPEN','2026-01-01T00:00:11.200000+00:00',7,'CONFLICTING_REPLAY'),['RECOVERED']),conflicting_interrupt_replay_after_restore)
def malformed_ids():
 x=Lifecycle();out=[]
 for sid in (['x'],{'x':1},b'x','', 'x'*129,'café'):
  b=x.control_snapshot(); x.ingest(sample(sid,1));out.append((x.audit[-1],x.control_snapshot()==b))
 return out
check('F2_ids_list_dict_bytes_empty_long_unicode', [({'type':'INVALID_SAMPLE_ID','sample_id':None},True)]*6,malformed_ids)
def payloads():
 x=Lifecycle();cycle=[];cycle.append(cycle)
 bad=[None, [],sample('nan',1,signal=float('nan')),sample('inf',1,signal=float('inf')),sample('obj',1,signal=object()),sample('cycle',1,signal=cycle),sample('extra',1,unexpected='email@example.invalid')]
 out=[]
 for p in bad:
  b=x.control_snapshot();x.ingest(p);out.append((x.audit[-1],b==x.control_snapshot()))
 return out
check('F2_non_dict_nan_inf_object_cycle_extra_sanitized', [({'type':'INVALID_PAYLOAD','sample_id':None},True)]*2+ [({'type':'INVALID_PAYLOAD','sample_id':i},True) for i in ('nan','inf','obj','cycle','extra')],payloads)
def corrected():
 x=Lifecycle();x.ingest(sample('id',1,unexpected=object()));invalid=x.audit[-1]['type'];events=[put(x,'id',1),put(x,'id',2),put(x,'id',2)];kinds=[x.audit[-2]['type'],x.audit[-1]['type']];y=Lifecycle.restore(x.snapshot());y.ingest(sample('id',1));return invalid, len(x.seen),kinds,y.audit[-1]['type'],len(y.seen)
check('F2_corrected_id_conflict_and_snapshot_restore',('INVALID_PAYLOAD',1,['CONFLICTING_REPLAY','CONFLICTING_REPLAY'],'EXACT_REPLAY',1),corrected)
def wrong_rule():
 x=Lifecycle();b=x.control_snapshot();put(x,'future',999,rule='WRONG');one=(x.audit[-1]['type'],b==x.control_snapshot());a=put(x,'future',1,rule='N8N_READINESS');put(x,'b2',2,rule='N8N_READINESS');e=put(x,'b3',3,rule='N8N_READINESS');return one,a,[v['kind'] for v in e]
check('F3_wrong_rule_future_same_id_corrected',(('RULE_MISMATCH',True),[],['OPEN']),wrong_rule)
def absent_rule():
 x=Lifecycle();es=[]
 for i in range(3):es+=put(x,'a'+str(i),i)
 return [e['kind'] for e in es],x.rule,x.source
check('F3_absent_rule_synthetic_only',(['OPEN'],'N8N_READINESS','synthetic'),absent_rule)
def cooldown(delta,recovered):
 x=open_instance(); first=x.incident_seq
 if recovered:
  for i in range(3):put(x,f'g{i}',10+i,'good')
 es=[]
 for i in range(3):es+=put(x,f'c{delta}-{i}',delta+i)
 e=es[0];return (e['kind'],e['notification_emitted'],e['incident_seq'],e['incident_id'],first,x.state)
for delta,kind,emit in ((899,'SUPPRESSED_COOLDOWN',False),(900,'NOTIFICATION',True),(901,'NOTIFICATION',True)):
 check(f'D1_OPEN_cooldown_{delta}',(kind,emit,1,'kvm2:N8N_READINESS:ops-01a-s2-v1:1',1,'OPEN'),lambda d=delta:cooldown(d,False))
for delta,emit in ((899,False),(900,True),(901,True)):
 check(f'D1_RECOVERED_new_incident_{delta}',('OPEN',emit,2,'kvm2:N8N_READINESS:ops-01a-s2-v1:2',1,'OPEN'),lambda d=delta:cooldown(d,True))
def policy():
 p=json.loads(Path('/data/cache/scratch/pr36_qa_6838ca/sandbox/ops-monitoring-lifecycle/policy.json').read_text())
 v=p['validation_order'];return (v.index('optional_explicit_rule')<v.index('sample_id_replay')<v.index('strictly_advancing_time'),p['s1_composition'].startswith('S1_EQUIVALENCE_FIXTURE_ONLY'),p['trusted_interruption']['control_fields_unchanged'])
check('P_policy_order_and_S1_boundary',(True,True,['state','last_ts','last_alert_ts','incident_seq','seen']),policy)
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--json',required=True);args=ap.parse_args()
 data={'task':'QA-A1-OPS01A-S2-D2-HERMES','pr36_head':'6838ca7d5e69b43f5272e5fe7f03ba5fff1d7222','pr24_base':'e9c2d8f759850ea9c654de7e103549e041f66679','python':platform.python_version(),'cases':R,'passed':sum(r['status']=='PASS' for r in R),'failed':sum(r['status']!='PASS' for r in R)}
 Path(args.json).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
 print('TOTAL',len(R),'PASS',data['passed'],'FAIL',data['failed'],'EVIDENCE',args.json)
