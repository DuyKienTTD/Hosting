"""GROW-01/S2: local-only package contract regression tests."""
import copy
import unittest
from contract import fixture_packages, transition, fork_revision, digest, ContractError, audit_record


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.pkgs = fixture_packages()
        self.p = copy.deepcopy(self.pkgs[0])
        self.ledger = {}

    def act(self, action, role='editor', key='action-1', **kwargs):
        return transition(self.p, action, role, key, self.ledger,
                          expected_revision=self.p['revision'], expected_digest=self.p['content_digest'], **kwargs)

    def test_01_three_inherited_drafts(self):
        self.assertEqual(len(self.pkgs), 3)
        self.assertEqual({p['state'] for p in self.pkgs}, {'DRAFT'})
        self.assertEqual({p['asset_rights_status'] for p in self.pkgs}, {'UNVERIFIED'})

    def test_02_draft_to_review(self):
        self.assertEqual(self.act('submit_review')['state'], 'IN_REVIEW')

    def test_03_missing_rights_blocks_approval(self):
        self.p.update(state='READY_FOR_OWNER_REVIEW', technical_review_status='VERIFIED_FIXTURE',
                      marketing_review_status='VERIFIED_FIXTURE', consent_status='VERIFIED_FIXTURE',
                      channel_status='VERIFIED_FIXTURE')
        with self.assertRaisesRegex(ContractError, 'RIGHTS_UNVERIFIED'):
            self.act('decide_owner', 'owner', 'action-2')
        self.assertEqual(self.p['state'], 'READY_FOR_OWNER_REVIEW')

    def test_04_p2_requires_technical_review(self):
        p = copy.deepcopy(self.pkgs[1]); p['asset_rights_status'] = 'VERIFIED_FIXTURE'
        p['marketing_review_status'] = 'VERIFIED_FIXTURE'; p['technical_review_status'] = 'UNVERIFIED'
        p['state'] = 'READY_FOR_OWNER_REVIEW'
        with self.assertRaisesRegex(ContractError, 'TECHNICAL_UNVERIFIED'):
            transition(p, 'decide_owner', 'owner', 'p2-owner', {}, p['revision'], p['content_digest'])

    def test_05_unverified_channel_blocks_release(self):
        self.p.update(state='READY_FOR_OWNER_REVIEW',asset_rights_status='VERIFIED_FIXTURE',technical_review_status='VERIFIED_FIXTURE',marketing_review_status='VERIFIED_FIXTURE',consent_status='VERIFIED_FIXTURE')
        with self.assertRaisesRegex(ContractError, 'CHANNEL_UNVERIFIED'):
            self.act('decide_owner', 'owner')

    def test_06_self_approval_blocked(self):
        self.p.update(state='READY_FOR_OWNER_REVIEW',asset_rights_status='VERIFIED_FIXTURE',technical_review_status='VERIFIED_FIXTURE',marketing_review_status='VERIFIED_FIXTURE',consent_status='VERIFIED_FIXTURE',channel_status='VERIFIED_FIXTURE')
        with self.assertRaisesRegex(ContractError, 'SELF_APPROVAL'):
            self.act('decide_owner', 'editor')

    def test_07_stale_revision_and_digest_rejected(self):
        with self.assertRaisesRegex(ContractError, 'STALE_REVISION'):
            transition(self.p,'submit_review','editor','stale',self.ledger,99,self.p['content_digest'])
        with self.assertRaisesRegex(ContractError, 'STALE_DIGEST'):
            transition(self.p,'submit_review','editor','digest',self.ledger,1,'0'*64)

    def test_08_replay_stable(self):
        first = self.act('submit_review', key='replay')
        again = transition(self.p,'submit_review','editor','replay',self.ledger,1,first['content_digest'])
        self.assertEqual(first, again)
        self.assertEqual(len(self.p['decision_log']),1)

    def test_09_key_collision_rejected(self):
        self.act('submit_review',key='collision')
        with self.assertRaisesRegex(ContractError, 'KEY_COLLISION'):
            self.act('request_changes', 'reviewer', 'collision')

    def test_10_fork_invalidates_review(self):
        self.act('submit_review')
        prior = self.p['content_digest']
        child = fork_revision(self.p, 'editor', 'synthetic-note-v2')
        self.assertEqual(child['state'],'DRAFT')
        self.assertEqual(child['decision_log'],[])
        self.assertNotEqual(child['content_digest'],prior)
        self.assertEqual(child['revision'],2)

    def test_11_publish_and_paid_render_blocked(self):
        for action in ('publish','paid_render'):
            with self.assertRaisesRegex(ContractError,'FORBIDDEN_SIDE_EFFECT'):
                self.act(action,key=action)

    def test_12_missing_callback_and_out_of_order(self):
        for action in ('callback_missing','callback_reordered','callback_unknown'):
            with self.assertRaisesRegex(ContractError,'UNKNOWN_CALLBACK'):
                self.act(action,key=action)
        self.assertEqual(len(self.p['decision_log']),0)

    def test_13_unauthorized_role_and_client_switch(self):
        with self.assertRaisesRegex(ContractError,'ROLE_FORBIDDEN'):
            self.act('submit_review','client_owner_switch')

    def test_14_synthetic_owner_sequence(self):
        self.act('submit_review',key='seq-a')
        self.act('mark_ready',role='reviewer',key='seq-b',review_tokens={'rights':'r-fixture','technical':'t-fixture','marketing':'m-fixture','consent':'c-fixture','channel':'h-fixture'})
        self.assertEqual(self.p['state'],'READY_FOR_OWNER_REVIEW')
        self.act('decide_owner',role='owner',key='seq-c')
        self.assertEqual(self.p['state'],'APPROVED_FOR_OFFLINE_HANDOFF')
        self.assertEqual(self.p['owner_approval_status'],'FIXTURE_APPROVED_NOT_PUBLISH')
        self.assertEqual(len(self.p['decision_log']),3)

    def test_15_digest_canonical_and_audit(self):
        a={'b':1,'a':2}; b={'a':2,'b':1}
        self.assertEqual(digest(a),digest(b))
        record=audit_record(self.p,'REVIEW_REQUESTED','editor')
        self.assertEqual(record['package_id'],self.p['package_id'])
        self.assertNotIn('secret',record)


if __name__ == '__main__':
    unittest.main(verbosity=2)
