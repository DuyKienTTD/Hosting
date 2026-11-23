import copy
import unittest
from release_state import assess_release

BASE='e385c1bea2070973e3007e5717f7e980348d6ab3'
CAND='1'*40
TREE='2'*40
MERGED='3'*40
SNAP={'record_kind':'KNG_RELEASE_SOURCE_SNAPSHOT',
      'release_gate':{'phase':'PREMERGE_CANDIDATE','status':'NOT_EFFECTIVE'},
      'source_authority':'main_effective_rules_until_verified_activation',
      'main_sha':BASE,'production_authorized':False,'merge_authorized':False,
      'codex_authorized':False,'work_ack':'UNKNOWN','work_ack_task_id':None,
      'work_ack_receipt':None,'agent_status':{'Work':'QA_COMPLETE_NO_NEW_TASK'},
      'last_work_source_qa':{'actor':'Work','task_id':'WORK-KNG01-PR42-FINAL-FIXTURE-MICRO-RECHECK','verdict':'KNG01_PR42_SOURCE_QA_PASS_WITH_FINAL_GATES',
         'source_sha':'b8cd377d3c3696c486fed41adc941a9d4db92ecc',
         'record_type':'HISTORICAL_COMPLETED_SOURCE_QA_NOT_NEW_ACK'}}
APP={'candidate_sha':CAND,'target_tree':TREE,'baseline_sha':BASE,
     'a0_approved':True,'method':'merge','target_branch':'main','approval_id':'A0-TEST-RECEIPT'}
REMOTE={'branch':'main','head':MERGED,'merged':True,'tree':TREE,'parents':[BASE,CAND]}

def run(s=SNAP,a=APP,r=REMOTE,c=CAND,va=lambda x: True,vr=lambda x: True):
    return assess_release(s,approval=a,remote=r,candidate_sha=c,candidate_tree=TREE,
                          verify_approval=va,verify_remote=vr)

class Gate(unittest.TestCase):
    def test_default_candidate_never_effective(self):
        self.assertEqual('NOT_EFFECTIVE',assess_release(SNAP).state)
    def test_verified_approved_simulation(self):
        x=run();self.assertEqual('EFFECTIVE_IF_VERIFIED',x.state);self.assertEqual(MERGED,x.effective_source)
    def test_missing_approval(self):self.assertNotEqual('EFFECTIVE_IF_VERIFIED',run(a=None).state)
    def test_false_approval(self):
        a=copy.deepcopy(APP);a['a0_approved']=False;self.assertEqual('A0_APPROVAL_MISSING',run(a=a).reason)
    def test_unverified_approval(self):self.assertEqual('A0_APPROVAL_UNVERIFIED',run(va=lambda x:False).reason)
    def test_unverified_remote(self):self.assertEqual('REMOTE_READBACK_UNVERIFIED',run(vr=lambda x:False).reason)
    def test_wrong_tree(self):
        r=copy.deepcopy(REMOTE);r['tree']='4'*40;self.assertEqual('REMOTE_MAIN_TREE_MISMATCH',run(r=r).reason)
    def test_candidate_tree_mismatch(self):
        a=copy.deepcopy(APP);a['target_tree']='4'*40
        self.assertEqual('CANDIDATE_TREE_MISMATCH',run(a=a).reason)
    def test_not_merged_flag(self):
        r=copy.deepcopy(REMOTE);r['merged']=False
        self.assertEqual('NOT_MERGED',run(r=r).reason)
    def test_stale_main(self):
        r=copy.deepcopy(REMOTE);r['parents']=['4'*40,CAND];self.assertEqual('REMOTE_MERGE_PARENTS_MISMATCH',run(r=r).reason)
    def test_wrong_candidate(self):self.assertEqual('STALE_APPROVAL_SOURCE',run(c='4'*40).reason)
    def test_wrong_merge_method(self):
        a=copy.deepcopy(APP);a['method']='squash';self.assertEqual('A0_APPROVAL_MISSING',run(a=a).reason)
    def test_no_merge(self):
        r=copy.deepcopy(REMOTE);r['head']=BASE;self.assertEqual('NOT_MERGED',run(r=r).reason)
    def test_candidate_not_active_if_unsafe_flag(self):
        s=copy.deepcopy(SNAP);s['production_authorized']=True;self.assertEqual('UNSAFE_PERMISSION',run(s=s).reason)
    def test_stale_phase(self):
        s=copy.deepcopy(SNAP);s['release_gate']['phase']='EFFECTIVE';self.assertEqual('INVALID_SOURCE_PHASE',run(s=s).reason)
    def test_no_verified_callback(self):
        self.assertEqual('MISSING_INDEPENDENT_VERIFICATION',run(vr=None).reason)
    def test_stale_work_pending(self):
        s=copy.deepcopy(SNAP);s['agent_status']['Work']='KNG_D2_TARGETED_REQA_PENDING_ACK'
        self.assertEqual('UNRECONCILED_WORK_STATE',run(s=s).reason)
    def test_forged_work_ack(self):
        s=copy.deepcopy(SNAP);s['work_ack']='ACKNOWLEDGED'
        self.assertEqual('UNRECONCILED_WORK_STATE',run(s=s).reason)
    def test_fake_work_source_qa(self):
        s=copy.deepcopy(SNAP);s['last_work_source_qa']['verdict']='KNG_ACCEPTED'
        self.assertEqual('UNVERIFIED_WORK_SOURCE_QA',run(s=s).reason)
    def test_wrong_work_source_qa_actor(self):
        s=copy.deepcopy(SNAP);s['last_work_source_qa']['actor']='A1'
        self.assertEqual('UNVERIFIED_WORK_SOURCE_QA',run(s=s).reason)
    def test_untrusted_approval_exception(self):
        def fail(_):raise RuntimeError('remote denied')
        self.assertEqual('A0_APPROVAL_UNVERIFIED',run(va=fail).reason)
if __name__=='__main__':unittest.main()