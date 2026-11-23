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
   x=Lifecycle(); batch(x,0); events=batch(x,delta); self.assertEqual(events,[kind]); self.assertEqual(x.incident_seq,1); self.assertEqual(events[0],kind); self.assertEqual(x.last_alert_ts is not None,True)
 def test_recovered_boundaries_start_new_incident(self):
  for delta,emitted in ((899,False),(900,True),(901,True)):
   x=Lifecycle(); batch(x,0); batch(x,10,'good','g'); old_alert=x.last_alert_ts; batch(x,delta,'bad','r'); self.assertEqual(x.state,'OPEN'); self.assertEqual(x.incident_seq,2); self.assertEqual(x.last_alert_ts != old_alert,emitted)
 def test_wrong_source_future_does_not_poison_corrected_timestamp(self):
  x=Lifecycle(); before=x.control_snapshot(); x.ingest(s('x',999,source='wrong')); self.assertEqual(before,x.control_snapshot()); self.assertEqual(batch(x,1),['OPEN'])
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
