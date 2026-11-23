"""A1 D3 replay regression cases independent of D1/D2 historical fixtures."""
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from lifecycle import Lifecycle

BASE=datetime(2026,1,1,tzinfo=timezone.utc)
def pkt(sid,t,signal='bad',**changes):
    x={'sample_id':sid,'observed_at_utc':(BASE+timedelta(seconds=t)).isoformat(timespec='microseconds').replace('+00:00','Z'), 'resource':'kvm2','source':'synthetic','rule_version':'ops-01a-s2-v1','freshness':'fresh','health_status':'observed','signal':signal}
    x.update(changes)
    return x

def opened():
    x=Lifecycle()
    for i in range(3):x.ingest(pkt(f'o{i}',i))
    assert x.state=='OPEN'
    return x

def mid_sequence():
    x=opened();x.ingest(pkt('g1',10,'good'));x.ingest(pkt('g2',11,'good'))
    u=pkt('U',12,'unknown');x.ingest(u)
    x.ingest(pkt('g3',11.1,'good'));x.ingest(pkt('g4',11.2,'good'))
    assert x.good_streak==2 and x.state=='OPEN'
    return x,u

class D3(unittest.TestCase):
    def test_r1_exact_before_watermark(self):
        x,u=mid_sequence();before=x.control_snapshot()
        self.assertEqual(x.ingest(u),[])
        self.assertEqual(x.audit[-1]['type'],'EXACT_REPLAY')
        self.assertEqual(x.control_snapshot(),before)
        self.assertEqual(x.ingest(pkt('g5',13,'good'))[0]['kind'],'RECOVERED')
    def test_r2_conflicting_after_restore(self):
        x,u=mid_sequence();y=Lifecycle.restore(x.snapshot());before=y.control_snapshot()
        self.assertEqual(y.ingest(pkt('U',12,'bad',freshness='stale')),[])
        self.assertEqual(y.audit[-1]['type'],'CONFLICTING_REPLAY')
        self.assertEqual(y.control_snapshot(),before)
        self.assertEqual(y.ingest(pkt('g5',13,'good'))[0]['kind'],'RECOVERED')
    def test_valid_after_interruption_id_is_collision(self):
        x,u=mid_sequence();before=x.control_snapshot()
        x.ingest(pkt('U',13,'good'))
        self.assertEqual(x.audit[-1]['type'],'CONFLICTING_REPLAY')
        self.assertEqual(x.control_snapshot(),before)
    def test_valid_id_then_interruption_is_collision(self):
        x=opened();x.ingest(pkt('g1',10,'good'));x.ingest(pkt('g2',11,'good'));before=x.control_snapshot()
        x.ingest(pkt('g2',12,'unknown'))
        self.assertEqual(x.audit[-1]['type'],'CONFLICTING_REPLAY')
        self.assertEqual(x.control_snapshot(),before)
    def test_foreign_invalid_do_not_poison_registry(self):
        x=opened();before=x.control_snapshot()
        for bad,err in ((pkt('Z',20,'unknown',source='foreign'),'SOURCE_MISMATCH'),(pkt('Z',21,'unknown',rule='wrong'),'RULE_MISMATCH'),({**pkt('Z',22,'unknown'),'sample_id':['list']},'INVALID_SAMPLE_ID')):
            x.ingest(bad);self.assertEqual(x.audit[-1]['type'],err)
        self.assertEqual(x.control_snapshot(),before)
        x.ingest(pkt('Z',12,'unknown'))
        self.assertEqual(x.audit[-1]['type'],'TRUSTED_INTERRUPTION')
    def test_after_watermark_replay_is_harmless(self):
        x,u=mid_sequence();x.ingest(pkt('g5',13,'good'));before=x.control_snapshot()
        x.ingest(u)
        self.assertIn(x.audit[-1]['type'],('EXACT_REPLAY','NON_ADVANCING_TIMESTAMP'))
        self.assertEqual(x.control_snapshot(),before)
    def test_bad_streak_restarts_once(self):
        x=Lifecycle();x.ingest(pkt('b1',1));x.ingest(pkt('b2',2));x.ingest(pkt('Q',3,'unknown'))
        x.ingest(pkt('b3',2.1));x.ingest(pkt('b4',2.2))
        x.ingest(pkt('Q',3,'unknown'))
        self.assertEqual(x.audit[-1]['type'],'EXACT_REPLAY')
        self.assertEqual(x.ingest(pkt('b5',4))[0]['kind'],'OPEN')
    def test_snapshot_deterministic_restore_and_duplicate(self):
        x,u=mid_sequence();snap=x.snapshot();y=Lifecycle.restore(snap)
        self.assertEqual(json.loads(y.snapshot()),json.loads(snap))
        y.ingest(u);self.assertEqual(y.audit[-1]['type'],'EXACT_REPLAY')
    def test_bounded_registry_no_eviction_replay(self):
        x=Lifecycle();limit=x._MAX_INTERRUPTION_IDS
        self.assertGreater(limit,0)
        for i in range(limit):x.ingest(pkt(f'U{i}',i+1,'unknown'))
        old=x.control_snapshot();x.ingest(pkt('EXTRA',limit+2,'unknown'))
        self.assertEqual(x.audit[-1]['type'],'INTERRUPTION_REGISTRY_FULL')
        self.assertEqual(x.control_snapshot(),old)
        x.ingest(pkt('U0',1,'unknown'))
        self.assertEqual(x.audit[-1]['type'],'EXACT_REPLAY')
        self.assertEqual(len(x.interruption_replays),limit)
    def test_full_registry_freezes_new_valid_progress(self):
        x=Lifecycle()
        for i in range(x._MAX_INTERRUPTION_IDS):x.ingest(pkt(f'R{i}',i+1,'unknown'))
        before=x.control_snapshot();x.ingest(pkt('fresh',9999,'bad'))
        self.assertEqual(x.audit[-1]['type'],'INTERRUPTION_REGISTRY_FULL')
        self.assertEqual(x.control_snapshot(),before)
    def test_legacy_restore_without_interruptions(self):
        x=opened();d=json.loads(x.snapshot());d.pop('snapshot_version',None);d.pop('interruption_replays',None)
        y=Lifecycle.restore(json.dumps(d));self.assertEqual(y.state,'OPEN')
    def test_legacy_restore_with_interruptions_rejected(self):
        x=Lifecycle();x.ingest(pkt('Q',1,'unknown'));d=json.loads(x.snapshot())
        d.pop('snapshot_version',None);d.pop('interruption_replays',None)
        with self.assertRaises(ValueError): Lifecycle.restore(json.dumps(d))
    def test_cooldown_remains(self):
        for delay,kind in ((899,'SUPPRESSED_COOLDOWN'),(900,'NOTIFICATION'),(901,'NOTIFICATION')):
            x=opened()
            for i in range(3):events=x.ingest(pkt(f'b{i}',delay+i))
            self.assertEqual(events[0]['kind'],kind)
            self.assertEqual(events[0]['incident_seq'],1)

if __name__=='__main__':unittest.main()
