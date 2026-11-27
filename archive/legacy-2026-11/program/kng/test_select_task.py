"""D5 fail-closed task discovery tests; synthetic fixture only."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from select_task import CatalogRejected, select_candidates


class CandidateSelector(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'tasks').mkdir()
        for p in ('tasks/archive.md', 'tasks/eligible.md', 'tasks/unknown.md'):
            (self.root/p).write_text('---\nid: example\n---\n', encoding='utf-8')
        self.records = [
            {'id':'archive','path':'tasks/archive.md','type':'task','status':'archived-inactive-not-dispatchable','dispatch_eligible':False},
            {'id':'eligible','path':'tasks/eligible.md','type':'task','status':'ready-for-dispatch-review','dispatch_eligible':True},
            {'id':'unknown','path':'tasks/unknown.md','type':'task','status':'ready-for-dispatch-review'},
        ]
        self.save()

    def save(self):
        import yaml
        (self.root/'CATALOG.yaml').write_text(yaml.safe_dump({'schema_version':1,'documents':self.records}, allow_unicode=True),encoding='utf-8')

    def cli(self):
        return subprocess.run([sys.executable, str(Path(__file__).with_name('select_task.py')), '--root', str(self.root)],capture_output=True,text=True)

    def test_one_positive_and_archived_negative(self):
        self.assertEqual([{'id':'eligible','path':'tasks/eligible.md'}],select_candidates(self.root))
        response=self.cli()
        self.assertEqual(0,response.returncode)
        self.assertEqual('CANDIDATES_ONLY_NOT_AUTHORIZATION',json.loads(response.stdout)['status'])
        self.assertNotIn('archive.md',response.stdout)
        self.assertNotIn('unknown.md',response.stdout)

    def test_no_current_eligibles_is_valid_empty_result(self):
        self.records[1].pop('dispatch_eligible')
        self.save()
        self.assertEqual([],select_candidates(self.root))
        self.assertEqual([],json.loads(self.cli().stdout)['candidates'])

    def test_explicit_false_never_selected(self):
        self.records[1]['dispatch_eligible']=False
        self.save()
        self.assertEqual([],select_candidates(self.root))

    def test_unknown_and_string_eligibility_rejected(self):
        self.records[1]['dispatch_eligible']='true'
        self.save()
        with self.assertRaisesRegex(CatalogRejected,'ELIGIBILITY_INVALID'):select_candidates(self.root)
        self.assertEqual(2,self.cli().returncode)

    def test_archived_true_conflict_stops(self):
        self.records[0]['dispatch_eligible']=True
        self.save()
        with self.assertRaisesRegex(CatalogRejected,'ARCHIVED_DISPATCH_CONFLICT'):select_candidates(self.root)

    def test_unsupported_active_status_stops(self):
        self.records[1]['status']='complete'
        self.save()
        with self.assertRaisesRegex(CatalogRejected,'TASK_STATUS_UNSUPPORTED'):select_candidates(self.root)

    def test_duplicate_id_stops_and_emits_nothing(self):
        self.records[1]['id']='archive'
        self.save()
        self.assertEqual(2,self.cli().returncode)
        self.assertEqual([],json.loads(self.cli().stdout)['candidates'])

    def test_duplicate_path_stops(self):
        self.records[1]['path']='tasks/archive.md'
        self.save()
        with self.assertRaisesRegex(CatalogRejected,'CATALOG_DUPLICATE_PATH'): select_candidates(self.root)
        self.assertEqual(2,self.cli().returncode)

    def test_missing_target_stops(self):
        (self.root/'tasks/eligible.md').unlink()
        self.assertEqual(2,self.cli().returncode)

    def test_unsafe_traversal_stops(self):
        self.records[0]['path']='../escape.md'
        self.save()
        with self.assertRaisesRegex(CatalogRejected,'PATH_INVALID'):select_candidates(self.root)

    def test_invalid_yaml_stops(self):
        (self.root/'CATALOG.yaml').write_text('schema_version: 1\ndocuments: [\n')
        self.assertEqual(2,self.cli().returncode)

    def test_duplicate_yaml_key_stops(self):
        (self.root/'CATALOG.yaml').write_text('schema_version: 1\nschema_version: 1\ndocuments: []\n')
        self.assertEqual(2,self.cli().returncode)

    def test_invalid_schema_stops(self):
        (self.root/'CATALOG.yaml').write_text('schema_version: no\ndocuments: []\n')
        self.assertEqual(2,self.cli().returncode)

    def test_eligibility_is_boolean_not_integer(self):
        self.records[1]['dispatch_eligible']=1
        self.save()
        self.assertEqual(2,self.cli().returncode)

    def test_not_a_dispatcher_and_does_not_write_files(self):
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.cli()
        after={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)


if __name__=='__main__':unittest.main()
