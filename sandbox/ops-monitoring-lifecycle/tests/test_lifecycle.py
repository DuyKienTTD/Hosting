import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from lifecycle import Lifecycle
def s(i,t,signal,**kw): return {'sample_id':f's-{i}','observed_at_utc':f'2026-01-01T00:{t//60:02d}:{t%60:02d}Z','signal':signal,'resource':'kvm2','source':'synthetic','freshness':'fresh','health_status':'observed',**kw}
def kinds(es): return [x['kind'] for x in es]
class S2(unittest.TestCase):
 def test_a_open_recover_second_open(self):
  x=Lifecycle(); e=[]
  for i in range(3): e+=x.ingest(s(i,i,'bad'))
  for i in range(3): e+=x.ingest(s(10+i,180+i,'good'))
  for i in range(3): e+=x.ingest(s(20+i,1200+i,'bad'))
  self.assertEqual(kinds(e),['OPEN','RECOVERED','OPEN']); self.assertEqual(x.incident_seq,2)
 def test_b_899_suppressed(self):
  x=Lifecycle(); e=[]
  for i in range(3): e+=x.ingest(s(i,i,'bad'))
  for i in range(3): e+=x.ingest(s(10+i,899+i,'bad'))
  self.assertEqual(kinds(e),['OPEN','SUPPRESSED_COOLDOWN'])
 def test_c_900_eligible_reopen(self):
  x=Lifecycle(); e=[]
  for i in range(3): e+=x.ingest(s(i,i,'bad'))
  for i in range(3): e+=x.ingest(s(10+i,900+i,'bad'))
  self.assertEqual(kinds(e),['OPEN','REOPEN'])
 def test_d_unknown_interrupts(self):
  x=Lifecycle(); e=[]
  e+=x.ingest(s(1,1,'bad')); e+=x.ingest(s(2,2,'bad')); e+=x.ingest(s(3,3,'bad',health_status='blocked')); e+=x.ingest(s(4,4,'bad')); e+=x.ingest(s(5,5,'bad')); e+=x.ingest(s(6,6,'bad'))
  self.assertEqual(kinds(e),['UNKNOWN','OPEN'])
 def test_e_duplicate_order_identity_source_fail_closed(self):
  x=Lifecycle(); x.ingest(s(1,1,'bad')); x.ingest(s(1,2,'bad')); x.ingest(s(2,0,'bad')); x.ingest(s(3,3,'bad',resource='other')); x.ingest(s(4,4,'bad',source='other')); self.assertEqual(x.state,'NORMAL'); self.assertEqual({a['type'] for a in x.audit},{'DUPLICATE_SAMPLE','OUT_OF_ORDER_SAMPLE','IDENTITY_MISMATCH','SOURCE_MISMATCH'})
 def test_f_source_change_cannot_spoof(self):
  x=Lifecycle(); x.ingest(s(1,1,'bad')); x.ingest(s(2,2,'bad')); x.ingest(s(3,3,'bad',source='other')); x.ingest(s(4,4,'bad')); x.ingest(s(5,5,'bad')); self.assertEqual(x.state,'NORMAL')
 def test_g_s1_composition(self):
  x=Lifecycle(); e=[]
  for i in range(3): e+=x.ingest(s(i,i,'bad'))
  for i in range(3): e+=x.ingest(s(10+i,10+i,'good'))
  self.assertEqual(kinds(e),['OPEN','RECOVERED'])
 def test_clock_reversal(self):
  x=Lifecycle(); x.ingest(s(1,100,'bad')); x.ingest(s(2,101,'bad')); x.ingest(s(3,99,'bad')); self.assertNotEqual(x.state,'OPEN'); self.assertIn('OUT_OF_ORDER_SAMPLE',{a['type'] for a in x.audit})
 def test_snapshot_replay(self):
  x=Lifecycle(); x.ingest(s(1,1,'bad')); x.ingest(s(2,2,'bad')); y=Lifecycle.restore(x.snapshot()); e=y.ingest(s(3,3,'bad')); self.assertEqual(kinds(e),['OPEN']); self.assertEqual(y.incident_seq,1)
 def test_cooldown_is_distinct_from_notification(self):
  x=Lifecycle(cooldown_seconds=900); x.ingest(s(1,1,'bad')); x.ingest(s(2,2,'bad')); e=x.ingest(s(3,3,'bad')); self.assertEqual(e[0]['cooldown_seconds'],900); self.assertIn('dedupe_key',e[0])
if __name__=='__main__': unittest.main(verbosity=2)
