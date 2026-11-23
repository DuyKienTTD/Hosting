"""Synthetic GROW-01/S2 contract, not a service or authorization backend."""
import copy
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / 'reports/evidence/2026-11-23-hermes-grow01-s2-package-fixtures.json'
UTC = '2026-11-23T00:00:00Z'  # fixed synthetic clock; no claim of real event time

class ContractError(ValueError):
    pass

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')

def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def content_projection(p):
    return {k:p[k] for k in ('package_id','source_ref','source_sha','revision','language','target_channel','asset_refs','content_note')}

def fixture_packages():
    return copy.deepcopy(json.loads(FIXTURES.read_text())['packages'])

def validate(p):
    fields=('package_id','source_ref','source_sha','revision','language','target_channel','asset_refs',
            'asset_rights_status','technical_review_status','marketing_review_status','owner_approval_status',
            'consent_status','channel_status','proposed_cost','state','decision_log','idempotency_key','content_digest','created_at_utc','updated_at_utc','content_note')
    if not all(k in p for k in fields):raise ContractError('MISSING_FIELD')
    if not re.fullmatch(r'P[1-3]-[a-z0-9-]{3,80}',p['package_id']):raise ContractError('BAD_ID')
    if not re.fullmatch(r'[0-9a-f]{40}',p['source_sha']) or type(p['revision']) is not int or p['revision']<1:raise ContractError('BAD_VERSION')
    if p['content_digest'] != digest(content_projection(p)):raise ContractError('BAD_DIGEST')
    if len(canonical(p)) > 16384:raise ContractError('OVERSIZE')
    if p['proposed_cost'] is not None or p['asset_rights_status'] not in ('UNVERIFIED','VERIFIED_FIXTURE'):raise ContractError('UNSAFE_FIELD')
    if p['state'] not in ('DRAFT','IN_REVIEW','NEEDS_CHANGES','READY_FOR_OWNER_REVIEW','APPROVED_FOR_OFFLINE_HANDOFF','BLOCKED','REJECTED'):raise ContractError('BAD_STATE')
    return True

def audit_record(p, action, actor):
    return {'package_id':p['package_id'],'revision':p['revision'],'content_digest':p['content_digest'],
            'action':action,'actor_role':actor,'at_utc':UTC,'scope':'SYNTHETIC_OFFLINE_ONLY'}

def transition(p, action, role, key, ledger, expected_revision, expected_digest, review_tokens=None):
    if action in ('publish','paid_render','schedule','upload'):raise ContractError('FORBIDDEN_SIDE_EFFECT')
    if action.startswith('callback_'):raise ContractError('UNKNOWN_CALLBACK')
    validate(p)
    if not isinstance(key,str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{2,63}',key):raise ContractError('BAD_KEY')
    # This is a local in-memory simulation only. It is not durable and cannot authenticate a user.
    sig=digest({'package':p['package_id'],'action':action,'role':role,'revision':expected_revision,
                'content_digest':expected_digest,'review_tokens':review_tokens})
    ledger_key=(p['package_id'],key)
    if ledger_key in ledger:
        existing=ledger[ledger_key]
        if existing['signature'] != sig:raise ContractError('KEY_COLLISION')
        return copy.deepcopy(existing['result'])
    if expected_revision != p['revision']:raise ContractError('STALE_REVISION')
    if expected_digest != p['content_digest']:raise ContractError('STALE_DIGEST')
    allowed={'submit_review':('DRAFT','editor','IN_REVIEW'),
             'request_changes':('IN_REVIEW','reviewer','NEEDS_CHANGES'),
             'mark_ready':('IN_REVIEW','reviewer','READY_FOR_OWNER_REVIEW'),
             'decide_owner':('READY_FOR_OWNER_REVIEW','owner','APPROVED_FOR_OFFLINE_HANDOFF'),
             'block':('IN_REVIEW','reviewer','BLOCKED'),
             'reject':('READY_FOR_OWNER_REVIEW','owner','REJECTED')}
    if action not in allowed:raise ContractError('INVALID_TRANSITION')
    start,required_role,target=allowed[action]
    if role != required_role:raise ContractError('ROLE_FORBIDDEN' if role != 'editor' else 'SELF_APPROVAL')
    if p['state'] != start:raise ContractError('INVALID_TRANSITION')
    if action=='mark_ready':
        if not isinstance(review_tokens,dict) or not all(isinstance(review_tokens.get(x),str) and review_tokens[x].endswith('-fixture') for x in ('rights','technical','marketing','consent','channel')):
            raise ContractError('MISSING_FIXTURE_REVIEW')
        p.update(asset_rights_status='VERIFIED_FIXTURE',technical_review_status='VERIFIED_FIXTURE',
                 marketing_review_status='VERIFIED_FIXTURE',consent_status='VERIFIED_FIXTURE',channel_status='VERIFIED_FIXTURE')
    if action=='decide_owner':
        for field,error in [('asset_rights_status','RIGHTS_UNVERIFIED'),('technical_review_status','TECHNICAL_UNVERIFIED'),('marketing_review_status','MARKETING_UNVERIFIED'),('consent_status','CONSENT_UNVERIFIED'),('channel_status','CHANNEL_UNVERIFIED')]:
            if p.get(field)!='VERIFIED_FIXTURE':raise ContractError(error)
        if p.get('editor_role') == role:raise ContractError('SELF_APPROVAL')
        p['owner_approval_status']='FIXTURE_APPROVED_NOT_PUBLISH'
    p['state']=target
    p['idempotency_key']=key
    p['updated_at_utc']=UTC
    p['decision_log'].append(audit_record(p,action,role))
    result=copy.deepcopy(p)
    ledger[ledger_key]={'signature':sig,'result':result}
    return result

def fork_revision(p,role,note):
    validate(p)
    if role != 'editor' or not isinstance(note,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{3,64}',note):raise ContractError('BAD_FORK')
    child=copy.deepcopy(p)
    child['revision']+=1;child['content_note']=note;child['state']='DRAFT';child['decision_log']=[]
    child['asset_rights_status']='UNVERIFIED';child['technical_review_status']='UNVERIFIED'
    child['marketing_review_status']='UNVERIFIED';child['owner_approval_status']='UNVERIFIED';child['consent_status']='UNVERIFIED';child['channel_status']='UNVERIFIED'
    child['idempotency_key']=None;child['content_digest']=digest(content_projection(child));child['updated_at_utc']=UTC
    validate(child)
    return child
