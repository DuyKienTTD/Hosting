import copy, json, subprocess, tempfile, unittest
from pathlib import Path
from derive import run, source, materialize_state, materialize_catalog, D2_WORK_ID, WS02_TASK

STATE='''header\n<!-- KNG:BEGIN_GENERATED -->\nold\n<!-- KNG:END_GENERATED -->\nfooter\n'''
CAT='''documents:\n  # KNG:BEGIN_GENERATED_REPORTS\n  # KNG:END_GENERATED_REPORTS\n'''

def cmd(root,*args):
 return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()

class D3Evidence(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  (self.root/'program').mkdir()
  self.data={'main_sha':'a'*40,'pr31_sha':'b'*40,'agent_status':{'Work':'KNG_D2_TARGETED_REQA_PENDING_ACK'},'work_ack_task_id':D2_WORK_ID,'work_ack':'UNKNOWN','work_ack_receipt':None,'current_handoffs':{'WS-02':{'source_task':WS02_TASK,'status':'PREPARED_FOR_OWNER_FORWARD','ack_receipt':None}},'acceptance_index':{'WS-02':{'review_state':'UNKNOWN_NEW_REPORT','last_evidence':None}}}
  (self.root/'STATE.md').write_text(STATE);(self.root/'CATALOG.yaml').write_text(CAT)
  subprocess.run(['git','init','-q',str(self.root)],check=True)
  self.persist()
 def tearDown(self):self.tmp.cleanup()
 def persist(self):(self.root/'program/current.json').write_text(json.dumps(self.data))
 def commit(self,path,content):
  f=self.root/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(content))
  subprocess.run(['git','-C',str(self.root),'add',path],check=True)
  subprocess.run(['git','-C',str(self.root),'-c','user.name=KNG Test','-c','user.email=test@example.invalid','commit','-qm','fixture'],check=True)
  return {'path':path,'commit':cmd(self.root,'rev-parse','HEAD'),'git_blob':cmd(self.root,'rev-parse','HEAD:'+path)}
 def snapshots(self):return ((self.root/'STATE.md').read_bytes(),(self.root/'CATALOG.yaml').read_bytes())
 def fails_without_writes(self,error):
  self.persist();before=self.snapshots()
  with self.assertRaisesRegex(ValueError,error):run(self.root,False)
  self.assertEqual(before,self.snapshots())
  with self.assertRaisesRegex(ValueError,error):run(self.root,True)
  self.assertEqual(before,self.snapshots())
 def test_baseline_idempotent(self):
  self.assertFalse(run(self.root,False));self.assertTrue(run(self.root,True));self.assertTrue(run(self.root,False))
  before=self.snapshots();self.assertTrue(run(self.root,True));self.assertEqual(before,self.snapshots())
 def test_fake_url_ack_rejected(self):
  self.data['current_handoffs']['WS-02']={'source_task':WS02_TASK,'status':'ACKNOWLEDGED','ack_receipt':{'task_id':'WS-02','actor':'Work','event':'ACK','status':'ACKNOWLEDGED','authorized_task_id':WS02_TASK,'immutable_evidence_url':'https://example.invalid/no-receipt','path':'reports/receipt.json','commit':'a'*40,'git_blob':'b'*40}}
  self.fails_without_writes('ACK_RECEIPT_MISMATCH')
 def test_missing_object_rejected(self):
  self.data['current_handoffs']['WS-02']={'source_task':WS02_TASK,'status':'ACKNOWLEDGED','ack_receipt':{'task_id':'WS-02','actor':'Work','event':'ACK','status':'ACKNOWLEDGED','authorized_task_id':WS02_TASK,'path':'reports/not-found.json','commit':'a'*40,'git_blob':'b'*40}}
  self.fails_without_writes('PROVENANCE_UNVERIFIED')
 def test_wrong_actor_task_and_status(self):
  for field,value in [('task_id','WS-01'),('actor','A1'),('event','DONE'),('status','DONE'),('authorized_task_id','WORK-KNG01-TARGETED-D2-REQA')]:
   self.data['current_handoffs']['WS-02']={'source_task':WS02_TASK,'status':'ACKNOWLEDGED','ack_receipt':{'task_id':'WS-02','actor':'Work','event':'ACK','status':'ACKNOWLEDGED','authorized_task_id':WS02_TASK}}
   self.data['current_handoffs']['WS-02']['ack_receipt'][field]=value
   self.fails_without_writes('ACK_RECEIPT_MISMATCH')
 def test_stale_binding(self):
  self.data['work_ack_task_id']='WORK-KNG01-TARGETED-D2-REQA';self.fails_without_writes('ACK_RECEIPT_MISMATCH')
 def test_fake_d2_top_level_ack(self):
  self.data['work_ack']='ACKNOWLEDGED';self.data['work_ack_receipt']={'task_id':D2_WORK_ID,'actor':'Work','event':'ACK','status':'ACKNOWLEDGED'}
  self.fails_without_writes('ACK_RECEIPT_MISMATCH')
 def test_nonexistent_report(self):
  self.data['acceptance_index']['WS-02']={'review_state':'ACCEPTED_PAPER_EXERCISE','last_evidence':{'path':'reports/qa-no-such-report.md','git_blob':'0'*40,'commit':'a'*40,'task_id':'WS-02','actor':'Work','disposition':'ACCEPTED_PAPER_EXERCISE'}}
  self.fails_without_writes('PROVENANCE_UNVERIFIED')
 def test_unknown_report_rejected(self):
  self.data['acceptance_index']['WS-02']={'review_state':'UNKNOWN_NEW_REPORT','last_evidence':{'path':'reports/qa-no-such-report.md','git_blob':'0'*40,'commit':'a'*40}}
  self.fails_without_writes('ACCEPTANCE_PROVENANCE_INVALID')
 def test_wrong_report_disposition(self):
  self.data['acceptance_index']['WS-02']={'review_state':'ACCEPTED_PAPER_EXERCISE','last_evidence':{'path':'reports/qa-no-such-report.md','git_blob':'0'*40,'commit':'a'*40,'task_id':'WS-02','actor':'Work','disposition':'PENDING'}}
  self.fails_without_writes('ACCEPTANCE_PROVENANCE_INVALID')
 def test_real_receipt_success_idempotent(self):
  payload={'task_id':'WS-02','actor':'Work','event':'ACK','status':'ACKNOWLEDGED','authorized_task_id':WS02_TASK,'source_task':WS02_TASK,}
  evidence=self.commit('reports/receipt.json',payload)
  self.data['current_handoffs']['WS-02']={'source_task':WS02_TASK,'status':'ACKNOWLEDGED','ack_receipt':{**payload,**evidence}}
  self.persist()
  self.fails_without_writes('AUTHORITY_UNVERIFIED')  # D4: blob alone is not approval
 def test_real_report_success_idempotent(self):
  name='reports/2026-paper.json';payload={'task_id':'WS-02','actor':'Work','disposition':'ACCEPTED_PAPER_EXERCISE','path':name,'evidence_ref':'sha-verified-paper'}
  evidence=self.commit(name,payload)
  self.data['acceptance_index']['WS-02']={'review_state':'ACCEPTED_PAPER_EXERCISE','last_evidence':{**payload,**evidence}}
  self.persist()
  self.fails_without_writes('AUTHORITY_UNVERIFIED')  # D4: independent reviewer approval is required
 def test_real_markdown_report_frontmatter(self):
  name='reports/approved.md'
  content='---\ntask_id: WS-02\nactor: Work\ndisposition: ACCEPTED_PAPER_EXERCISE\npath: reports/approved.md\nevidence_ref: paper-sha\n---\n\n# QA evidence\n'
  f=self.root/name;f.parent.mkdir(exist_ok=True);f.write_text(content)
  subprocess.run(['git','-C',str(self.root),'add',name],check=True)
  subprocess.run(['git','-C',str(self.root),'-c','user.name=KNG Test','-c','user.email=test@example.invalid','commit','-qm','markdown-report'],check=True)
  evidence={'path':name,'commit':cmd(self.root,'rev-parse','HEAD'),'git_blob':cmd(self.root,'rev-parse','HEAD:'+name),'task_id':'WS-02','actor':'Work','disposition':'ACCEPTED_PAPER_EXERCISE','evidence_ref':'paper-sha'}
  self.data['acceptance_index']['WS-02']={'review_state':'ACCEPTED_PAPER_EXERCISE','last_evidence':evidence}
  self.persist()
  self.fails_without_writes('AUTHORITY_UNVERIFIED')  # D4: author Git metadata does not confer authority
 def test_cli_rejects_invalid_without_writes(self):
  self.data['acceptance_index']['WS-02']={'review_state':'UNKNOWN_NEW_REPORT','last_evidence':{'path':'reports/absent.md','git_blob':'0'*40}}
  self.persist();before=self.snapshots()
  for extra in [[],['--write']]:
   done=subprocess.run(['python3',str(Path(__file__).with_name('derive.py')),'--root',str(self.root),*extra],capture_output=True,text=True)
   self.assertNotEqual(done.returncode,0)
   self.assertIn('ACCEPTANCE_PROVENANCE_INVALID',done.stdout)
   self.assertEqual(before,self.snapshots())
 def test_valid_git_blob_but_false_report_body(self):
  name='reports/wrong.json';payload={'task_id':'WS-02','actor':'Work','disposition':'PENDING','path':name,'evidence_ref':'real-doc'}
  evidence=self.commit(name,payload)
  self.data['acceptance_index']['WS-02']={'review_state':'ACCEPTED_PAPER_EXERCISE','last_evidence':{**payload,**evidence,'disposition':'ACCEPTED_PAPER_EXERCISE'}}
  self.fails_without_writes('AUTHORITY_UNVERIFIED')

if __name__=='__main__':unittest.main()
