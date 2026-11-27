"""GROW-01/S2: local-only package contract regression tests."""
import copy
import unittest
from contract import fixture_packages, transition, fork_revision, digest, ContractError, audit_record, validate, content_projection, MockLedger


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.pkgs = fixture_packages()
        self.p = copy.deepcopy(self.pkgs[0])
        self.ledger = MockLedger()

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
        self.act('submit_review',key='submit-3')
        tokens={'technical':'t-fixture','marketing':'m-fixture','consent':'c-fixture','channel':'h-fixture'}
        with self.assertRaisesRegex(ContractError, 'MISSING_FIXTURE_REVIEW'):
            self.act('mark_ready','reviewer','review-3',review_tokens=tokens)
        self.assertEqual(self.p['state'],'IN_REVIEW')
        self.assertEqual(self.p['asset_rights_status'],'UNVERIFIED')

    def test_04_p2_requires_technical_review(self):
        p=copy.deepcopy(self.pkgs[1]); ledger=MockLedger()
        transition(p,'submit_review','editor','p2-submit',ledger,p['revision'],p['content_digest'])
        tokens={'rights':'r-fixture','marketing':'m-fixture','consent':'c-fixture','channel':'h-fixture'}
        with self.assertRaisesRegex(ContractError,'MISSING_FIXTURE_REVIEW'):
            transition(p,'mark_ready','reviewer','p2-review',ledger,p['revision'],p['content_digest'],tokens)
        self.assertEqual(p['technical_review_status'],'UNVERIFIED')

    def test_05_unverified_channel_blocks_release(self):
        self.act('submit_review',key='submit-5')
        tokens={'rights':'r-fixture','technical':'t-fixture','marketing':'m-fixture','consent':'c-fixture'}
        with self.assertRaisesRegex(ContractError,'MISSING_FIXTURE_REVIEW'):
            self.act('mark_ready','reviewer','review-5',review_tokens=tokens)
        self.assertEqual(self.p['channel_status'],'UNVERIFIED')

    def test_06_self_approval_blocked(self):
        self.act('submit_review',key='submit-6')
        tokens={'rights':'r-fixture','technical':'t-fixture','marketing':'m-fixture','consent':'c-fixture','channel':'h-fixture'}
        self.act('mark_ready','reviewer','review-6',review_tokens=tokens)
        with self.assertRaisesRegex(ContractError,'SELF_APPROVAL'):
            self.act('decide_owner','editor','owner-6')
        self.assertEqual(self.p['owner_approval_status'],'UNVERIFIED')

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
        child = fork_revision(self.p, 'editor', 'synthetic-note-v2', self.ledger)
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

    def test_16_a1_f01_forged_ready_review_blocked(self):
        self.p['state'] = 'READY_FOR_OWNER_REVIEW'
        for field in ('asset_rights_status','technical_review_status','marketing_review_status','consent_status','channel_status'):
            self.p[field] = 'VERIFIED_FIXTURE'
        with self.assertRaisesRegex(ContractError, 'INVALID_PROVENANCE'):
            self.act('decide_owner',role='owner',key='forge-ready')
        self.assertEqual(self.p['decision_log'],[])

    def test_17_a1_f02_external_asset_blocked(self):
        self.p['asset_refs']=[{'asset_ref':'https://example.invalid/external-object','kind':'remote_asset','rights':'CLAIMED_RIGHTS'}]
        self.p['content_digest']=digest(content_projection(self.p))
        with self.assertRaisesRegex(ContractError,'INVALID_FIELD'):
            validate(self.p)

    def test_18_a1_f02_extra_property_blocked(self):
        self.p['extra_html']='<b>mock</b>'
        with self.assertRaisesRegex(ContractError,'INVALID_FIELD'):
            validate(self.p)

    def test_19_a1_f03_nan_typed_error(self):
        self.p['technical_review_status']=float('nan')
        with self.assertRaisesRegex(ContractError,'INVALID_FIELD'):
            validate(self.p)

    def test_20_a1_f03_html_note_blocked(self):
        self.p['content_note']='<img src=x onerror=alert(1)>'
        self.p['content_digest']=digest(content_projection(self.p))
        with self.assertRaisesRegex(ContractError,'INVALID_FIELD'):
            validate(self.p)

    def test_21_a1_f01_forged_owner_approval_blocked(self):
        self.p['state']='APPROVED_FOR_OFFLINE_HANDOFF'
        self.p['owner_approval_status']='FIXTURE_APPROVED_NOT_PUBLISH'
        with self.assertRaisesRegex(ContractError,'INVALID_PROVENANCE'):
            validate(self.p)

    def test_22_forged_plausible_history_cannot_bootstrap_ledger(self):
        tokens={'rights':'r-fixture','technical':'t-fixture','marketing':'m-fixture','consent':'c-fixture','channel':'h-fixture'}
        for action,role,key,tok in [('submit_review','editor','fake-submit',None),('mark_ready','reviewer','fake-review',tokens)]:
            if tok:
                for field in ('asset_rights_status','technical_review_status','marketing_review_status','consent_status','channel_status'):
                    self.p[field]='VERIFIED_FIXTURE'
            self.p['state']='IN_REVIEW' if action=='submit_review' else 'READY_FOR_OWNER_REVIEW'
            self.p['idempotency_key']=key
            self.p['decision_log'].append(audit_record(self.p,action,role,key,tok))
        self.assertTrue(validate(self.p))  # local history is structurally valid, NOT trusted provenance
        with self.assertRaisesRegex(ContractError,'UNTRUSTED_STATE'):
            self.act('decide_owner','owner','fake-owner')

    def test_23_tampering_after_real_review_rejected(self):
        self.act('submit_review',key='real-submit')
        tokens={'rights':'r-fixture','technical':'t-fixture','marketing':'m-fixture','consent':'c-fixture','channel':'h-fixture'}
        self.act('mark_ready','reviewer','real-review',review_tokens=tokens)
        self.p['updated_at_utc']='2026-11-24T00:00:00Z'
        with self.assertRaisesRegex(ContractError,'UNTRUSTED_STATE'):
            self.act('decide_owner','owner','real-owner')

    def test_24_nested_asset_extra_and_remote_ref_rejected(self):
        for change in ({'extra':'x'}, {'asset_ref':'https://example.invalid/asset'}):
            candidate=copy.deepcopy(self.p)
            candidate['asset_refs'][0].update(change)
            candidate['content_digest']=digest(content_projection(candidate))
            with self.assertRaisesRegex(ContractError,'INVALID_FIELD'):
                validate(candidate)

    def test_25_invalid_types_and_finite_numbers(self):
        for field,value in [('revision',True),('state',[]),('technical_review_status',float('inf')),
                            ('asset_refs',{}),('decision_log','[]'),('source_ref',None),('language',7)]:
            candidate=copy.deepcopy(self.p);candidate[field]=value
            with self.subTest(field=field),self.assertRaises(ContractError):
                validate(candidate)

    def test_26_raw_dict_ledger_rejected(self):
        with self.assertRaisesRegex(ContractError,'UNTRUSTED_STATE'):
            transition(self.p,'submit_review','editor','raw-dict',{},1,self.p['content_digest'])

    def test_27_fork_child_has_registered_state_and_new_review(self):
        self.act('submit_review',key='fork-before')
        child=fork_revision(self.p,'editor','synthetic-note-v2',self.ledger)
        self.assertEqual(transition(child,'submit_review','editor','fork-after',self.ledger,2,child['content_digest'])['state'],'IN_REVIEW')
        self.assertEqual(child['owner_approval_status'],'UNVERIFIED')

    def test_28_review_token_with_wrong_shape_is_atomic(self):
        self.act('submit_review',key='token-submit')
        before=copy.deepcopy(self.p)
        with self.assertRaisesRegex(ContractError,'MISSING_FIXTURE_REVIEW'):
            self.act('mark_ready','reviewer','token-bad',review_tokens={'rights':'r-fixture'})
        self.assertEqual(self.p,before)

    def test_29_owner_status_rewrite_after_approval_rejected(self):
        self.act('submit_review',key='approv-submit')
        tokens={'rights':'r-fixture','technical':'t-fixture','marketing':'m-fixture','consent':'c-fixture','channel':'h-fixture'}
        self.act('mark_ready','reviewer','approv-review',review_tokens=tokens)
        self.act('decide_owner','owner','approv-owner')
        self.p['owner_approval_status']='UNVERIFIED'
        with self.assertRaisesRegex(ContractError,'INVALID_PROVENANCE'):
            validate(self.p)

    def test_30_canonical_unicode_and_16k_byte_boundary(self):
        self.assertEqual(digest({'é':'thép','a':1}),digest({'a':1,'é':'thép'}))
        p=copy.deepcopy(self.p)
        p['asset_refs']=[copy.deepcopy(p['asset_refs'][0]) for _ in range(8)]
        p['content_note']='thép'*60
        p['content_digest']=digest(content_projection(p))
        self.assertTrue(validate(p))
        p['decision_log']=[{'padding':'x'*20000}]
        with self.assertRaisesRegex(ContractError,'OVERSIZE'):
            validate(p)

    def test_31_source_ref_and_revision_drift_rejected(self):
        p=copy.deepcopy(self.p)
        p['source_ref']=p['source_ref'].replace('P1-short-vi-craftsmanship','P2-install-howto-en')
        p['content_digest']=digest(content_projection(p))
        with self.assertRaisesRegex(ContractError,'INVALID_FIELD'):
            validate(p)
        child=copy.deepcopy(self.p);child['revision']=2
        child['content_digest']=digest(content_projection(child))
        with self.assertRaisesRegex(ContractError,'UNTRUSTED_STATE'):
            transition(child,'submit_review','editor','unforked',self.ledger,2,child['content_digest'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
