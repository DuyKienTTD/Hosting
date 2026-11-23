import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from lifecycle import Lifecycle

def s(i,t,signal='bad',**kw): return {'sample_id':str(i),'observed_at_utc':f'2026-01-01T{t//3600:02d}:{(t%3600)//60:02d}:{t%60:02d}Z','signal':signal,'resource':'kvm2','source':'synthetic','rule_version':'ops-01a-s2-v1','freshness':'fresh','health_status':'observed',**kw}
def batch(x,start,signal='bad',prefix='b'):
 out=[]
 for i in range(3): out+=x.ingest(s(f'{prefix}{start}-{i}',start+i,signal))
 return out
class PinnedS1Evaluator:
 RULE_VERSION='s1-pinned-v1'
 def __init__(self): self.bad=0; self.good=0
 def evaluate(self,signal):
  if signal=='bad': self.bad+=1; self.good=0
  else: self.good+=1; self.bad=0
  return self.bad>=3,self.good>=3
class D1(unittest.TestCase):
 def test_identity_before_mutation_then_corrected_sample(self):
  x=Lifecycle(); before=x.control_snapshot(); self.assertEqual(x.ingest(s('future',999,resource='other')),[]); self.assertEqual(before,x.control_snapshot()); self.assertEqual(x.ingest(s('future',1)),[]); self.assertEqual(x.ingest(s('b',2)),[]); self.assertEqual(x.ingest(s('c',3))[0]['kind'],'OPEN')
 def test_bad_rule_timestamp_stale_and_blocked_are_no_control_mutation(self):
  for kw in ({'rule_version':'wrong'},{'observed_at_utc':'bad'},{'freshness':'stale'},{'health_status':'blocked'}):
   x=Lifecycle(); before=x.control_snapshot(); x.ingest(s('x',1,**kw)); self.assertEqual(before,x.control_snapshot())
 def test_replay_is_distinguished_and_no_control_mutation(self):
  x=Lifecycle(); x.ingest(s('same',1)); before=x.control_snapshot(); x.ingest(s('same',2)); self.assertEqual(before,x.control_snapshot()); self.assertEqual(x.audit[-1]['type'],'CONFLICTING_REPLAY')
 def test_same_timestamp_ids_do_not_form_streak(self):
  x=Lifecycle(); x.ingest(s('a',1)); x.ingest(s('b',1)); x.ingest(s('c',1)); self.assertNotEqual(x.state,'OPEN')
 def test_open_899_900_901_are_notification_only(self):
  for delta,kind,emitted in ((899,'SUPPRESSED_COOLDOWN',False),(900,'NOTIFICATION',True),(901,'NOTIFICATION',True)):
   x=Lifecycle(); batch(x,0); events=batch(x,delta); self.assertEqual([e['kind'] for e in events],[kind]); self.assertEqual(x.incident_seq,1); self.assertEqual(events[0]['notification_emitted'],emitted)
 def test_recovered_boundaries_start_new_incident(self):
  for delta,emitted in ((899,False),(900,True),(901,True)):
   x=Lifecycle(); batch(x,0); batch(x,10,'good','g'); old_alert=x.last_alert_ts; events=batch(x,delta,'bad','r'); self.assertEqual([e['kind'] for e in events],['OPEN']); self.assertEqual(x.state,'OPEN'); self.assertEqual(x.incident_seq,2); self.assertEqual(x.last_alert_ts != old_alert,emitted)
 def test_wrong_source_future_does_not_poison_corrected_timestamp(self):
  x=Lifecycle(); before=x.control_snapshot(); x.ingest(s('x',999,source='wrong')); self.assertEqual(before,x.control_snapshot()); self.assertEqual([e['kind'] for e in batch(x,1)],['OPEN'])
 def test_pinned_s1_composition_fixture(self):
  s1=PinnedS1Evaluator(); x=Lifecycle(); events=[]
  for i in range(3): bad,good=s1.evaluate('bad'); events+=x.ingest(s(i,i))
  self.assertTrue(bad and not good and [e['kind'] for e in events]==['OPEN'])
  for i in range(3): bad,good=s1.evaluate('good'); events+=x.ingest(s(f'g{i}',10+i,'good'))
  self.assertTrue(good and [e['kind'] for e in events]==['OPEN','RECOVERED'])
 def test_snapshot_replay_no_duplicate_incident(self):
  x=Lifecycle(); batch(x,0); y=Lifecycle.restore(x.snapshot()); self.assertEqual(y.ingest(s('b0-0',99)),[]); self.assertEqual(y.incident_seq,1)
 def test_clock_reversal_rejected_without_advancing_trusted_time(self):
  x=Lifecycle(); x.ingest(s('a',10)); before=x.control_snapshot(); x.ingest(s('b',9)); self.assertEqual(before,x.control_snapshot()); self.assertEqual(x.audit[-1]['type'],'NON_ADVANCING_TIMESTAMP')
if __name__=='__main__': unittest.main(verbosity=2)

# A1 D2 focused regressions, separate from Hostinger's historical D1 fixtures.
class D2(unittest.TestCase):
 def open(self):
  x=Lifecycle(); self.assertEqual([e['kind'] for e in batch(x,0)],['OPEN']); return x
 def reject_no_control(self,x,sample,reason):
  before=x.control_snapshot(); before_seen=dict(x.seen); before_alert=x.last_alert_ts
  self.assertEqual(x.ingest(sample),[])
  self.assertEqual(x.audit[-1]['type'],reason)
  self.assertEqual(x.control_snapshot(),before)
  self.assertEqual(x.seen,before_seen)
  self.assertEqual(x.last_alert_ts,before_alert)
  self.assertIn(x.audit[-1]['sample_id'],(None,sample.get('sample_id') if isinstance(sample,dict) else None))
 def interrupt_good(self,field,value):
  x=self.open()
  x.ingest(s('g1',10,'good'));x.ingest(s('g2',11,'good'))
  self.assertEqual(x.good_streak,2)
  before=x.control_snapshot(); stamp=x.last_ts
  data=s('interrupt',12,'good');data[field]=value
  self.assertEqual(x.ingest(data),[])
  self.assertEqual(x.audit[-1]['type'],'TRUSTED_INTERRUPTION')
  self.assertEqual(x.good_streak,0)
  self.assertEqual(x.state,'OPEN');self.assertEqual(x.last_ts,stamp)
  self.assertNotIn('interrupt',x.seen)
  self.assertNotEqual(x.control_snapshot(),before) # only streak changes
  self.assertEqual(x.ingest(s('g3',13,'good')),[])
  self.assertEqual(x.state,'OPEN')
  return x
 def test_f1_unknown_interrupts_good_streak(self):
  self.interrupt_good('signal','unknown')
 def test_f1_stale_interrupts_good_streak(self):
  self.interrupt_good('freshness','stale')
 def test_f1_blocked_interrupts_good_streak(self):
  self.interrupt_good('health_status','blocked')
 def test_f1_requires_three_NEW_goods_after_break(self):
  for field,value in [('signal','unknown'),('freshness','stale'),('health_status','blocked')]:
   with self.subTest(field=field):
    x=self.interrupt_good(field,value)
    self.assertEqual(x.ingest(s('g4',14,'good')),[])
    self.assertEqual(x.good_streak,2)
    self.assertEqual(x.ingest(s('g5',15,'good'))[0]['kind'],'RECOVERED')
    self.assertEqual(x.state,'RECOVERED')
 def test_f1_interruption_breaks_BAD_streak_in_normal(self):
  x=Lifecycle();x.ingest(s('b1',1));x.ingest(s('b2',2));self.assertEqual(x.bad_streak,2)
  x.ingest(s('u',3,signal='unknown'));self.assertEqual(x.bad_streak,0)
  self.assertEqual(x.ingest(s('b3',4)),[])
  self.assertEqual(x.ingest(s('b4',5)),[])
  self.assertEqual(x.ingest(s('b5',6))[0]['kind'],'OPEN')
 def test_f1_interruption_breaks_BAD_streak_in_recovered(self):
  x=self.open();batch(x,10,'good','g');self.assertEqual(x.state,'RECOVERED');x.ingest(s('b1',20));x.ingest(s('b2',21))
  seq=x.incident_seq;x.ingest(s('u',22,freshness='stale'))
  self.assertEqual((x.bad_streak,x.incident_seq,x.state),(0,seq,'RECOVERED'))
  self.assertEqual(x.ingest(s('b3',23)),[]);self.assertEqual(x.ingest(s('b4',24)),[])
  self.assertEqual(x.ingest(s('b5',25))[0]['kind'],'OPEN');self.assertEqual(x.incident_seq,seq+1)
 def test_f1_foreign_identity_does_NOT_interrupt_streak(self):
  x=self.open();x.ingest(s('g1',10,'good'));x.ingest(s('g2',11,'good'))
  for field,value,code in [('resource','foreign','IDENTITY_MISMATCH'),('source','foreign','SOURCE_MISMATCH'),('rule_version','foreign','RULE_VERSION_MISMATCH'),('rule','WRONG','RULE_MISMATCH')]:
   self.reject_no_control(x,s('bad'+field,12,'good',**{field:value}),code)
  self.assertEqual(x.good_streak,2)
  self.assertEqual(x.ingest(s('g3',13,'good'))[0]['kind'],'RECOVERED')
 def test_f1_trusted_interrupt_snapshot_restore(self):
  x=self.open();x.ingest(s('g1',10,'good'));x.ingest(s('g2',11,'good'));x.ingest(s('stale',12,freshness='stale'))
  y=Lifecycle.restore(x.snapshot());self.assertEqual(y.control_snapshot(),x.control_snapshot());self.assertEqual(y.audit,x.audit)
  self.assertEqual(y.ingest(s('g3',13,'good')),[]);self.assertEqual(y.state,'OPEN')
 def test_f2_invalid_sample_ids_list_dict_float_none_empty_oversize(self):
  x=Lifecycle()
  for sample_id in (['x'],{'id':'x'},1.25,None,'','a'*129,b'abc','has spaces','nonascii-é'):
   with self.subTest(id_type=type(sample_id).__name__):
    self.reject_no_control(x,{**s('good',1),'sample_id':sample_id},'INVALID_SAMPLE_ID')
    self.assertIsNone(x.audit[-1]['sample_id'])
  self.assertEqual(x.ingest(s('good',1)),[]);self.assertEqual(len(x.seen),1)
 def test_f2_invalid_non_dict_payloads(self):
  x=Lifecycle()
  for payload in (['x'],None,100,'string'):
   self.reject_no_control(x,payload,'INVALID_PAYLOAD')
 def test_f2_non_json_object_and_extra_field(self):
  x=Lifecycle()
  for payload in (s('x1',1,unexpected=object()),s('x2',2,unexpected='text')):
   self.reject_no_control(x,payload,'INVALID_PAYLOAD')
 def test_f2_nan_infinity_cyclic_payloads(self):
  x=Lifecycle()
  for bad in (float('nan'),float('inf'),-float('inf')):
   self.reject_no_control(x,s('nf'+str(len(x.audit)),1,unexpected=bad),'INVALID_PAYLOAD')
  cyclic=[];cyclic.append(cyclic)
  self.reject_no_control(x,s('cycle',1,unexpected=cyclic),'INVALID_PAYLOAD')
  self.assertTrue(all('payload' not in row and 'unexpected' not in row for row in x.audit))
 def test_f2_unserializable_allowed_field(self):
  x=Lifecycle()
  self.reject_no_control(x,{**s('xx',1),'observed_at_utc':object()},'INVALID_PAYLOAD')
 def test_f2_corrected_same_id_after_invalid(self):
  x=Lifecycle();bad={**s('same',1),'unexpected':'sensitive'}
  self.reject_no_control(x,bad,'INVALID_PAYLOAD')
  self.assertEqual(x.ingest(s('same',1)),[]);self.assertIn('same',x.seen)
 def test_f3_wrong_explicit_rule_rejected_no_mutation(self):
  x=Lifecycle();self.reject_no_control(x,s('rule-wrong',1,rule='WRONG'),'RULE_MISMATCH')
  self.assertEqual([z['kind'] for z in batch(x,10)],['OPEN'])
 def test_f3_correct_explicit_rule_accepted(self):
  x=Lifecycle();events=[]
  for i in range(3):events+=x.ingest(s(f'r{i}',i,rule='N8N_READINESS'))
  self.assertEqual([e['kind'] for e in events],['OPEN'])
 def test_f3_missing_rule_backward_compatible(self):
  x=Lifecycle();self.assertEqual([e['kind'] for e in batch(x,0)],['OPEN'])
 def test_f3_bad_rule_type_rejected(self):
  x=Lifecycle();self.reject_no_control(x,s('rr',1,rule=['N8N_READINESS']),'INVALID_PAYLOAD')
 def test_d1_replay_precedes_time_and_snapshot(self):
  x=self.open();y=Lifecycle.restore(x.snapshot());old=y.control_snapshot()
  y.ingest(s('b0-0',999));self.assertEqual(y.audit[-1]['type'],'CONFLICTING_REPLAY')
  self.assertEqual(y.control_snapshot(),old);self.assertEqual(y.incident_seq,1)
 def test_d1_equal_time_and_wrong_source_corrected(self):
  x=Lifecycle();x.ingest(s('a',10));self.reject_no_control(x,s('b',10),'NON_ADVANCING_TIMESTAMP')
  self.reject_no_control(x,s('c',999,source='foreign'),'SOURCE_MISMATCH')
  self.assertEqual(x.ingest(s('b',11)),[])
 def test_d2_policy_order_matches_code(self):
  import json
  policy=json.loads((Path(__file__).parents[1]/'policy.json').read_text())
  a=policy['validation_order'];self.assertLess(a.index('sample_id_replay'),a.index('strictly_advancing_time'))
  self.assertLess(a.index('optional_explicit_rule'),a.index('sample_id_replay'))
  self.assertEqual(policy['rule_binding']['absent_rule'].startswith('backward_compatible'),True)
