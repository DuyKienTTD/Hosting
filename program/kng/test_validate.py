#!/usr/bin/env python3
"""KNG negatives run with only stdlib."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from validate import validate

BASE=Path(__file__).resolve().parents[2]
RELS=['program/kng/validate.py','program/kng/test_validate.py','program/current.json','program/kng/inventory.json','program/kng/migration.json','program/kng/provenance-lock.json',
      'program/README.md','program/KNOWLEDGE_OPTIMIZATION.md','program/OPERATING_PROTOCOL.md',
      'program/WORK_BREAKDOWN.md','program/roadmaps/a1.md',
      'program/PRODUCT_AND_UI.md','program/SKILL_REGISTRY.md','program/roadmaps/work.md',
      'AGENTS.md','PROJECT.md','STATE.md','CATALOG.yaml',
      'rules/AGENT_WORKFLOW.md','rules/REPOSITORY_SECURITY.md']
class Contract(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        for rel in RELS:
            d=self.root/rel;d.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(BASE/rel,d)
    def tearDown(self):self.temp.cleanup()
    def obj(self,rel):return json.loads((self.root/rel).read_text())
    def put(self,rel,obj):(self.root/rel).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
    def err(self,code):self.assertIn(code,{z['code'] for z in validate(self.root, verify_objects=False)})
    def test_positive_candidate(self):self.assertEqual([],validate(self.root, verify_objects=False))
    def test_work_ack_requires_receipt_and_state(self):
        p='program/current.json';j=self.obj(p);j['work_ack']='ACKNOWLEDGED';self.put(p,j);self.err('ACK_RECEIPT_MISMATCH')
    def test_source_sha_valid_but_wrong(self):
        p='program/kng/inventory.json';j=self.obj(p);j['facts'][0]['source_sha']='0'*40;self.put(p,j);self.err('SOURCE_PIN_MISMATCH')
    def test_recovery_ref_plausible_nonexistent_commit(self):
        p='program/kng/inventory.json';j=self.obj(p);j['facts'][1]['recovery_ref']='PR39@'+'0'*40;self.put(p,j);self.err('SOURCE_PIN_MISMATCH')
    def test_migration_base_valid_but_wrong(self):
        p='program/kng/migration.json';j=self.obj(p);j['proposed_updates'][0]['base_blob']='0'*40;self.put(p,j);self.err('MIGRATION_BLOB_MISMATCH')

    def test_duplicate_catalog_id(self):
        p=self.root/'CATALOG.yaml';p.write_text('documents:\n  - id: kng-same\n    path: a.md\n  - id: kng-same\n    path: b.md\n');self.err('DUPLICATE_CATALOG_ID')
    def test_lock_pin_mutation(self):
        p='program/kng/provenance-lock.json';j=self.obj(p);j['refs']['main']='0'*40;self.put(p,j);self.err('SOURCE_PIN_MISMATCH')
    def test_missing_provenance_lock(self):
        (self.root/'program/kng/provenance-lock.json').unlink();self.err('PROVENANCE_UNVERIFIED')
    def test_missing_git_objects_fail_closed(self):
        codes={e['code'] for e in validate(self.root)}
        self.assertIn('PROVENANCE_UNVERIFIED',codes)
    def test_claim_v_evidence_consistency(self):
        p='program/current.json';j=self.obj(p);j['work_ack_receipt']={'task':'fake','owner':'Work'};self.put(p,j);self.err('ACK_RECEIPT_MISMATCH')
    def test_duplicate_fact_id(self):
        p='program/kng/inventory.json';j=self.obj(p);j['facts'].append(copy.deepcopy(j['facts'][0]));self.put(p,j);self.err('DUPLICATE_FACT_ID')
    def test_missing_source(self):
        (self.root/'program/OPERATING_PROTOCOL.md').unlink();self.err('MISSING_SOURCE')
    def test_broken_link(self):
        p=self.root/'program/README.md';p.write_text(p.read_text()+'\n[broken](missing-source.md)');self.err('BROKEN_LINK')
    def test_unsafe_permissions(self):
        p='program/current.json';j=self.obj(p);j['merge_authorized']=True;self.put(p,j);self.err('UNSAFE_PERMISSION')
    def test_unsafe_priority(self):
        p='program/current.json';j=self.obj(p);j['mode']='G0_AND_KNG';self.put(p,j);self.err('UNSAFE_PRIORITY')
    def test_wrong_authority(self):
        p='program/current.json';j=self.obj(p);j['source_authority']='PR39_IS_EFFECTIVE';self.put(p,j);self.err('WRONG_AUTHORITY')
    def test_fake_work_ack(self):
        p='program/current.json';j=self.obj(p);j['work_ack']='DONE';self.put(p,j);self.err('FALSE_ACK')
    def test_stale_agent_state(self):
        p='program/current.json';j=self.obj(p);j['agent_status']['Hostinger']='ACTIVE_INFRA';self.put(p,j);self.err('STALE_AGENT_STATE')
    def test_unsafe_delete_without_reference_review(self):
        p='program/kng/inventory.json';j=self.obj(p);j['facts'][0]['decision']='DELETE';self.put(p,j);self.err('UNSAFE_DELETE')
    def test_missing_recovery(self):
        p='program/kng/inventory.json';j=self.obj(p);j['facts'][1]['recovery_ref']='';self.put(p,j);self.err('MISSING_RECOVERY')
    def test_unsafe_shared_edit(self):
        p='program/kng/migration.json';j=self.obj(p);j['proposed_updates'][0]['execution']='APPLY_NOW';self.put(p,j);self.err('UNSAFE_SHARED_WRITE')
    def test_duplicate_migration_target(self):
        p='program/kng/migration.json';j=self.obj(p);j['proposed_updates'].append(copy.deepcopy(j['proposed_updates'][0]));self.put(p,j);self.err('DUPLICATE_MIGRATION_TARGET')
    def test_missing_mandatory_rules(self):
        p='program/current.json';j=self.obj(p);j['must_read'].remove('rules/REPOSITORY_SECURITY.md');self.put(p,j);self.err('MISSING_MANDATORY_RULE')
    def test_invalid_sha(self):
        p='program/kng/inventory.json';j=self.obj(p);j['facts'][0]['source_sha']='fake';self.put(p,j);self.err('INVALID_SHA')
    def test_secret_literal(self):
        p=self.root/'program/README.md';p.write_text(p.read_text()+'\napi_key = "SYNTHETIC_FAKE_SECRET_123"');self.err('SECRET_LITERAL')
    def test_stale_priority_phrase(self):
        p=self.root/'program/README.md';p.write_text(p.read_text()+'\nHostinger is resumed for new hosting/infra work');self.err('STALE_PRIORITY_TEXT')
    def test_duplicate_wbs(self):
        p=self.root/'program/WORK_BREAKDOWN.md';p.write_text(p.read_text()+'\n| G1-01 | extra |');self.err('DUPLICATE_WBS_ID')


# D2 explicit real-object and derived-mirror tests (synthetic local Git history)
class GitObjectEngine(unittest.TestCase):
    def test_real_commit_blob_and_mutated_sha(self):
        import subprocess
        from provenance import GitObjects
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);subprocess.run(['git','init','-q',d],check=True)
            (p/'source.txt').write_text('safe historical record\n')
            subprocess.run(['git','-C',d,'add','source.txt'],check=True)
            subprocess.run(['git','-C',d,'-c','user.name=KNG Fixture','-c','user.email=fixture@example.invalid','commit','-qm','synthetic'],check=True)
            commit=subprocess.check_output(['git','-C',d,'rev-parse','HEAD'],text=True).strip()
            blob=subprocess.check_output(['git','-C',d,'rev-parse','HEAD:source.txt'],text=True).strip()
            self.assertTrue(GitObjects(d).verify(commit,'source.txt',blob))
            with self.assertRaises(ValueError):GitObjects(d).verify(commit,'source.txt','0'*40)
            with self.assertRaises(LookupError):GitObjects(d).verify('0'*40,'source.txt',blob)

class DerivedState(unittest.TestCase):
    def test_generated_view_is_idempotent_and_requires_receipt(self):
        from derive import materialize_state
        data=json.loads((BASE/'program/current.json').read_text())
        base='top\n<!-- KNG:BEGIN_GENERATED -->\nobsolete\n<!-- KNG:END_GENERATED -->\nfooter\n'
        one=materialize_state(base,data)
        self.assertEqual(one,materialize_state(one,data))
        data.setdefault('current_handoffs',{})['WS-02']={'status':'ACKNOWLEDGED','ack_receipt':None}
        with self.assertRaisesRegex(ValueError,'ACK_RECEIPT_MISMATCH'):materialize_state(base,data)
        data['current_handoffs']['WS-02']['ack_receipt']={'task_id':'WS-02','actor':'Work','immutable_evidence_url':'https://github.com/test/x'}
        self.assertIn('ACKNOWLEDGED',materialize_state(base,data))
        from derive import materialize_catalog
        cat='documents:\n  # KNG:BEGIN_GENERATED_REPORTS\n  # KNG:END_GENERATED_REPORTS\n'
        self.assertEqual(cat,materialize_catalog(cat,data))
        data.setdefault('acceptance_index',{})['WS-02']={'last_evidence':{'path':'reports/dummy.md','git_blob':'a'*40}}
        self.assertIn('kng-derived-ws02-paper-report',materialize_catalog(cat,data))

if __name__ == "__main__":
    unittest.main()
