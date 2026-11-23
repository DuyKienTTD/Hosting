import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from evaluator import evaluate
ROOT = Path(__file__).parents[1]
def load(name): return json.loads((ROOT/'fixtures'/name).read_text())['samples']
def states(out, rule): return [d['state'] for d in out['decisions'] if d['rule'] == rule]
class OfflineMonitoringTests(unittest.TestCase):
    def test_readiness_recover_is_chronological(self): self.assertEqual(states(evaluate(load('readiness_bad_then_good.json')), 'N8N_READINESS'), ['OPEN','RECOVER'])
    def test_good_before_bad_never_recovers(self): self.assertEqual(states(evaluate(load('readiness_good_then_bad.json')), 'N8N_READINESS'), ['OPEN'])
    def test_unknown_interleave_resets_streak(self): self.assertEqual(states(evaluate(load('readiness_unknown_interleave.json')), 'N8N_READINESS'), ['UNKNOWN','OPEN'])
    def test_disk_threshold_and_trend(self):
        out=evaluate(load('disk_threshold_trend.json')); self.assertIn('OPEN', states(out,'DISK_HIGH')); self.assertIn('OPEN', states(out,'DISK_TREND_DEADLINE'))
    def test_backup_overdue(self): self.assertEqual(states(evaluate(load('backup_overdue.json')), 'BACKUP_AGE'), ['OVERDUE'])
    def test_backup_schedule_unknown(self): self.assertEqual(states(evaluate(load('backup_schedule_unknown.json')), 'BACKUP_AGE'), ['UNKNOWN'])
    def test_p0_exit_unknown_root(self): self.assertEqual(states(evaluate(load('p0_exit_137.json')), 'P0_REASONER'), ['RISK'])
    def test_tls_unknown(self): self.assertEqual(states(evaluate(load('tls_blocked.json')), 'TLS'), ['UNKNOWN'])
    def test_negative_duplicate_identity_source(self):
        out=evaluate(load('negative_controls.json')); kinds={x['type'] for x in out['audit']}; self.assertTrue({'OUT_OF_ORDER_SAMPLE','DUPLICATE_SAMPLE','IDENTITY_MISMATCH','SOURCE_UNKNOWN'} <= kinds); self.assertEqual(states(out,'N8N_READINESS'), [])
    def test_no_external_transport_contract(self):
        self.assertFalse(evaluate(load('tls_blocked.json'))['external_transport']); self.assertFalse(json.loads((ROOT/'policy.json').read_text())['external_transport'])
if __name__ == '__main__': unittest.main(verbosity=2)
