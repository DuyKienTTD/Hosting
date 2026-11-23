#!/usr/bin/env python3
"""KNG-01 release-state assessment. Never derives authority from a mutable file.

This function consumes *independently verified* A0 approval and GitHub remote
readback through two caller-provided verifiers. Ordinary CLI/file access is not
an authority oracle; without both verifiers it always returns NOT_EFFECTIVE.
"""
from dataclasses import dataclass
import re

SHA = re.compile(r'^[0-9a-f]{40}$')

@dataclass(frozen=True)
class ReleaseAssessment:
    state: str
    reason: str
    effective_source: str | None = None


def assess_release(snapshot, *, approval=None, remote=None,
                   candidate_sha=None, candidate_tree=None, verify_approval=None, verify_remote=None):
    """Evaluate a release, requiring independent A0 and main remote checks.

    The verifiers MUST authenticate provenance outside this source tree. An
    untrusted caller passing lambdas returning True cannot constitute approval.
    This is a decision helper, not a deployment/merge/dispatch authority.
    """
    fail = lambda why: ReleaseAssessment('NOT_EFFECTIVE', why)
    gate = snapshot.get('release_gate', {})
    if snapshot.get('record_kind') != 'KNG_RELEASE_SOURCE_SNAPSHOT' or gate.get('phase') != 'PREMERGE_CANDIDATE' or gate.get('status') != 'NOT_EFFECTIVE':
        return fail('INVALID_SOURCE_PHASE')
    if snapshot.get('source_authority') != 'main_effective_rules_until_verified_activation':
        return fail('INVALID_SOURCE_AUTHORITY')
    if any(snapshot.get(k) is not False for k in
           ('production_authorized', 'merge_authorized', 'codex_authorized')):
        return fail('UNSAFE_PERMISSION')
    if (snapshot.get('agent_status', {}).get('Work') != 'QA_COMPLETE_NO_NEW_TASK'
            or snapshot.get('work_ack') != 'UNKNOWN'
            or snapshot.get('work_ack_task_id') is not None
            or snapshot.get('work_ack_receipt') is not None):
        return fail('UNRECONCILED_WORK_STATE')
    qa = snapshot.get('last_work_source_qa', {})
    if (qa.get('actor') != 'Work'
            or qa.get('task_id') != 'WORK-KNG01-PR42-FINAL-FIXTURE-MICRO-RECHECK'
            or qa.get('verdict') != 'KNG01_PR42_SOURCE_QA_PASS_WITH_FINAL_GATES'
            or qa.get('source_sha') != 'b8cd377d3c3696c486fed41adc941a9d4db92ecc'
            or qa.get('record_type') != 'HISTORICAL_COMPLETED_SOURCE_QA_NOT_NEW_ACK'):
        return fail('UNVERIFIED_WORK_SOURCE_QA')
    if not all((approval, remote, candidate_sha, candidate_tree, verify_approval, verify_remote)):
        return fail('MISSING_INDEPENDENT_VERIFICATION')
    if not isinstance(approval, dict) or not isinstance(remote, dict):
        return fail('INVALID_EVIDENCE')
    required_sha = ('candidate_sha', 'target_tree', 'baseline_sha')
    if any(not isinstance(approval.get(k), str) or not SHA.fullmatch(approval[k])
           for k in required_sha):
        return fail('INVALID_APPROVAL_PIN')
    if approval.get('a0_approved') is not True or approval.get('method') != 'merge' \
       or approval.get('target_branch') != 'main' or not approval.get('approval_id'):
        return fail('A0_APPROVAL_MISSING')
    if not isinstance(candidate_tree, str) or not SHA.fullmatch(candidate_tree):
        return fail('INVALID_TARGET_TREE')
    if approval.get('target_tree') != candidate_tree:
        return fail('CANDIDATE_TREE_MISMATCH')
    if approval['baseline_sha'] != snapshot.get('main_sha') or \
       approval['candidate_sha'] != candidate_sha:
        return fail('STALE_APPROVAL_SOURCE')
    try:
        if verify_approval(approval) is not True:
            return fail('A0_APPROVAL_UNVERIFIED')
    except Exception:
        return fail('A0_APPROVAL_UNVERIFIED')
    if remote.get('merged') is not True:
        return fail('NOT_MERGED')
    if remote.get('branch') != 'main' or remote.get('tree') != approval['target_tree'] \
       or not isinstance(remote.get('head'), str) or not SHA.fullmatch(remote['head']):
        return fail('REMOTE_MAIN_TREE_MISMATCH')
    # An approved merge commit must have two exact parent commits. This also
    # prevents accepting stale main or another candidate under a valid tree.
    if remote.get('parents') != [snapshot['main_sha'], candidate_sha]:
        return fail('REMOTE_MERGE_PARENTS_MISMATCH')
    if remote['head'] in (snapshot['main_sha'], candidate_sha):
        return fail('NOT_MERGED')
    try:
        if verify_remote(remote) is not True:
            return fail('REMOTE_READBACK_UNVERIFIED')
    except Exception:
        return fail('REMOTE_READBACK_UNVERIFIED')
    return ReleaseAssessment('EFFECTIVE_IF_VERIFIED', 'EXTERNAL_A0_AND_MAIN_READBACK_VERIFIED', remote['head'])