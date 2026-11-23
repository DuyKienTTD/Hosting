"""D4 F4/F5: explicit states, authority-root pins and zero-write errors.

Synthetic positive approval pins are injected only by isolated tests; no live
WS02 approval exists in the shipped empty authority table.
"""
import copy
import json
import subprocess
import unittest
from unittest.mock import patch
from test_derive_d3 import D3Evidence, cmd, WS02_TASK, STATE, CAT
import derive


class D4Safety(D3Evidence):
    # Inherit D3 regressions; also run D4-specific cases.
    def test_f4_outer_handoff_invalid_no_write(self):
        for value in ('INVALID_STATUS', 'DONE', '', None, 'ACCEPTED_PAPER_EXERCISE'):
            self.data['current_handoffs']['WS-02']['status'] = value
            self.fails_without_writes('WS02_STATUS_INVALID')

    def test_f4_outer_review_invalid_no_write(self):
        for value in ('INVALID_STATUS', 'ACKNOWLEDGED', 'DONE', '', None):
            self.data['acceptance_index']['WS-02']['review_state'] = value
            self.fails_without_writes('WS02_REVIEW_STATE_INVALID')

    def test_f4_unauthorized_transition_and_pending_report(self):
        handoff = self.data['current_handoffs']['WS-02']
        handoff['status'] = 'ACKNOWLEDGED'
        handoff['scope'] = 'HISTORICAL_PRE_KNG_NO_DISPATCH'
        self.fails_without_writes('frozen pre-KNG lane')
        handoff.pop('scope')
        handoff['status'] = 'PREPARED_FOR_OWNER_FORWARD'
        self.data['acceptance_index']['WS-02'] = {'review_state': 'PENDING_REVIEW', 'last_evidence': {'path': 'reports/claim.json'}}
        self.fails_without_writes('pending/rejected')

    def _git_record(self, name, data):
        return self.commit(name, data)

    def _approval(self, kind, event_id, subject, decision='AUTHORIZED_ACK', reviewer='Chat Điều phối', actor='Work'):
        approval_body = {'event_id': event_id, 'kind': kind, 'reviewer': reviewer,
                         'decision': decision, 'task_id': 'WS-02', 'actor': actor,
                         'subject': {k: subject[k] for k in ('commit','path','git_blob')}}
        return self._git_record('reports/approval-'+event_id+'.json', approval_body)

    def _claim(self, name, content, kind, event_id, approval=None):
        subject = self._git_record(name, content)
        ref = {'event_id': event_id, **subject}
        if approval:
            ref['approval_ref'] = approval
        return ref

    def test_f5_self_asserted_valid_git_ack_rejected(self):
        content = {'task_id': 'WS-02', 'actor': 'Work', 'event': 'ACK',
                   'status': 'ACKNOWLEDGED', 'authorized_task_id': WS02_TASK,
                   'source_task': WS02_TASK}
        receipt = self._claim('reports/self-ack.json', content, 'WS02_ACK', 'evt-self-ack-1000')
        self.data['current_handoffs']['WS-02'] = {'status': 'ACKNOWLEDGED', 'source_task': WS02_TASK, 'ack_receipt': {**content, **receipt}}
        self.fails_without_writes('AUTHORITY_UNVERIFIED')

    def test_f5_fake_git_author_name_is_not_trust(self):
        content = {'task_id': 'WS-02', 'actor': 'Work', 'event': 'ACK',
                   'status': 'ACKNOWLEDGED', 'authorized_task_id': WS02_TASK,
                   'source_task': WS02_TASK}
        subject = self._git_record('reports/pretend-work.json', content)
        # A self-authored approval cannot substitute a reviewer-pinned entry.
        approval = self._approval('WS02_ACK', 'evt-pretend-100', subject)
        receipt = {'event_id': 'evt-pretend-100', **content, **subject, 'approval_ref': approval}
        self.data['current_handoffs']['WS-02'] = {'status': 'ACKNOWLEDGED', 'source_task': WS02_TASK, 'ack_receipt': receipt}
        self.fails_without_writes('AUTHORITY_UNVERIFIED')

    def test_f5_self_ref_and_missing_approval_report(self):
        name='reports/self-report.json'
        # Source and claim mention same fake evidence ref, but no actual Git evidence content.
        fake_ref={'path':'reports/not-found.json','commit':'0'*40,'git_blob':'0'*40}
        content={'task_id':'WS-02','actor':'Work','disposition':'ACCEPTED_PAPER_EXERCISE',
                 'path':name,'evidence_ref':fake_ref}
        claim=self._claim(name,content,'WS02_ACCEPTANCE','evt-self-report-1000')
        self.data['acceptance_index']['WS-02']={'review_state':'ACCEPTED_PAPER_EXERCISE',
             'last_evidence':{**content,**claim}}
        self.fails_without_writes('AUTHORITY_UNVERIFIED')

    def test_f5_trusted_fixture_ack_positive_and_idempotent(self):
        payload={'task_id':'WS-02','actor':'Work','event':'ACK','status':'ACKNOWLEDGED',
                 'authorized_task_id':WS02_TASK,'source_task':WS02_TASK}
        subject=self._git_record('reports/trusted-ack.json',payload)
        eid='evt-authorized-ack-100'
        approval=self._approval('WS02_ACK',eid,subject)
        receipt={**subject,**payload,'event_id':eid,'approval_ref':approval}
        self.data['current_handoffs']['WS-02']={'source_task':WS02_TASK,'status':'ACKNOWLEDGED','ack_receipt':receipt}
        anchor={('WS02_ACK',eid):{'subject':subject,'approval':approval,'reviewer':'Chat Điều phối'}}
        with patch.dict(derive.TRUSTED_DECISIONS, anchor):
            self.persist()
            self.assertTrue(derive.run(self.root,True));self.assertTrue(derive.run(self.root,False))
            self.assertIn('VERIFIED_REFERENCE',(self.root/'STATE.md').read_text())
            snap=self.snapshots();self.assertTrue(derive.run(self.root,True));self.assertEqual(snap,self.snapshots())
        # Removing the pinned approval must reject even though the Git objects remain.
        self.fails_without_writes('AUTHORITY_UNVERIFIED')

    def test_f5_trusted_fixture_report_requires_resolved_evidence(self):
        evidence=self._git_record('reports/actual-evidence.json', {'observation':'paper test only'})
        name='reports/trusted-report.json'
        content={'task_id':'WS-02','actor':'Work','disposition':'ACCEPTED_PAPER_EXERCISE',
                 'path':name,'evidence_ref':evidence}
        subject=self._git_record(name,content)
        eid='evt-review-accept-100'
        approval=self._approval('WS02_ACCEPTANCE',eid,subject,decision='ACCEPTED_PAPER_EXERCISE')
        claim={**subject,**content,'event_id':eid,'approval_ref':approval}
        self.data['acceptance_index']['WS-02']={'review_state':'ACCEPTED_PAPER_EXERCISE','last_evidence':claim}
        pin={('WS02_ACCEPTANCE',eid):{'subject':subject,'approval':approval,'reviewer':'Chat Điều phối'}}
        with patch.dict(derive.TRUSTED_DECISIONS,pin):
            self.persist();self.assertTrue(derive.run(self.root,True));self.assertTrue(derive.run(self.root,False))
            self.assertIn('accepted-paper-exercise-not-live',(self.root/'CATALOG.yaml').read_text())
            before=self.snapshots();self.assertTrue(derive.run(self.root,True));self.assertEqual(before,self.snapshots())
        self.fails_without_writes('AUTHORITY_UNVERIFIED')

    def test_f4_f5_cli_check_write_fail_closed(self):
        runner = str(__import__('pathlib').Path(derive.__file__))
        for mutation, expected in (('handoff','WS02_STATUS_INVALID'),
                                   ('review','WS02_REVIEW_STATE_INVALID'),
                                   ('untrusted','AUTHORITY_UNVERIFIED')):
            self.data['current_handoffs']['WS-02'] = {'status':'PREPARED_FOR_OWNER_FORWARD',
                'source_task':WS02_TASK,'ack_receipt':None}
            self.data['acceptance_index']['WS-02'] = {'review_state':'UNKNOWN_NEW_REPORT',
                'last_evidence':None}
            if mutation == 'handoff':
                self.data['current_handoffs']['WS-02']['status']='INVALID_STATUS'
            elif mutation == 'review':
                self.data['acceptance_index']['WS-02']['review_state']='INVALID_STATUS'
            else:
                payload={'task_id':'WS-02','actor':'Work','event':'ACK','status':'ACKNOWLEDGED',
                         'authorized_task_id':WS02_TASK,'source_task':WS02_TASK}
                receipt=self._git_record('reports/local-author-only.json',payload)
                self.data['current_handoffs']['WS-02'] = {'status':'ACKNOWLEDGED',
                    'source_task':WS02_TASK,'ack_receipt':{**payload,**receipt,
                     'event_id':'event-untrusted-author-10'}}
            self.persist();before=self.snapshots()
            for extra in ([], ['--write']):
                proc=subprocess.run(['python3',runner,'--root',str(self.root),*extra],
                                    text=True,capture_output=True)
                self.assertNotEqual(proc.returncode,0,(mutation,extra))
                self.assertIn(expected,proc.stdout)
                self.assertEqual(before,self.snapshots())

    def test_f5_anchored_approval_but_unresolved_evidence_rejected(self):
        name='reports/anchored-but-unresolved.json'
        missing={'commit':'0'*40,'path':'reports/missing.json','git_blob':'0'*40}
        payload={'task_id':'WS-02','actor':'Work','disposition':'ACCEPTED_PAPER_EXERCISE',
                 'path':name,'evidence_ref':missing}
        subject=self._git_record(name,payload)
        event='event-missing-evidence-100'
        approval=self._approval('WS02_ACCEPTANCE',event,subject,
                                decision='ACCEPTED_PAPER_EXERCISE')
        self.data['acceptance_index']['WS-02']={'review_state':'ACCEPTED_PAPER_EXERCISE',
            'last_evidence':{**payload,**subject,'event_id':event,'approval_ref':approval}}
        pin={('WS02_ACCEPTANCE',event):{'subject':subject,'approval':approval,
                                       'reviewer':'Chat Điều phối'}}
        with patch.dict(derive.TRUSTED_DECISIONS,pin):
            self.fails_without_writes('PROVENANCE_UNVERIFIED')

    def test_f5_anchored_but_forged_decision_content_rejected(self):
        payload={'task_id':'WS-02','actor':'Work','event':'ACK','status':'ACKNOWLEDGED',
                 'authorized_task_id':WS02_TASK,'source_task':WS02_TASK}
        subject=self._git_record('reports/ack-false-approval.json',payload)
        event='event-forged-decision-100'
        approval=self._approval('WS02_ACK',event,subject,decision='REJECTED')
        self.data['current_handoffs']['WS-02']={'status':'ACKNOWLEDGED',
            'source_task':WS02_TASK,'ack_receipt':{**payload,**subject,
            'event_id':event,'approval_ref':approval}}
        pin={('WS02_ACK',event):{'subject':subject,'approval':approval,
                                 'reviewer':'Chat Điều phối'}}
        with patch.dict(derive.TRUSTED_DECISIONS,pin):
            self.fails_without_writes('AUTHORITY_UNVERIFIED')

    def test_f5_real_approval_object_without_independent_pin_denied(self):
        payload={'task_id':'WS-02','actor':'Work','event':'ACK','status':'ACKNOWLEDGED',
                 'authorized_task_id':WS02_TASK,'source_task':WS02_TASK}
        subject=self._git_record('reports/alleged-receipt.json',payload)
        event='event-alleged-approval-100'
        approval=self._approval('WS02_ACK',event,subject)
        self.data['current_handoffs']['WS-02']={'status':'ACKNOWLEDGED',
             'source_task':WS02_TASK,'ack_receipt':{**payload,**subject,
              'event_id':event,'approval_ref':approval}}
        self.fails_without_writes('AUTHORITY_UNVERIFIED')

    def test_f5_rejected_wrong_reviewer_even_with_git_approval(self):
        payload={'task_id':'WS-02','actor':'Work','event':'ACK','status':'ACKNOWLEDGED',
                 'authorized_task_id':WS02_TASK,'source_task':WS02_TASK}
        subject=self._git_record('reports/wrong-reviewer.json',payload)
        eid='evt-wrong-reviewer-100'
        approval=self._approval('WS02_ACK',eid,subject,reviewer='QA Fixture')
        self.data['current_handoffs']['WS-02']={'status':'ACKNOWLEDGED','source_task':WS02_TASK,
            'ack_receipt':{**subject,**payload,'event_id':eid,'approval_ref':approval}}
        with patch.dict(derive.TRUSTED_DECISIONS,{('WS02_ACK',eid):{'subject':subject,'approval':approval,'reviewer':'QA Fixture'}}):
            self.fails_without_writes('AUTHORITY_UNVERIFIED')


if __name__ == '__main__':
    unittest.main()
