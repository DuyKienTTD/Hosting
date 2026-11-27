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
    try:
        return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise ContractError('INVALID_FIELD') from exc

def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def content_projection(p):
    return {k:p[k] for k in ('package_id','source_ref','source_sha','revision','language','target_channel','asset_refs','content_note')}

def fixture_packages():
    return copy.deepcopy(json.loads(FIXTURES.read_text())['packages'])

def _valid_review_tokens(tokens):
    return (type(tokens) is dict and set(tokens)=={'rights','technical','marketing','consent','channel'}
            and all(type(value) is str and re.fullmatch(r'[a-zA-Z0-9_-]{1,48}-fixture',value) for value in tokens.values()))

def validate(p):
    fields=('package_id','source_ref','source_sha','revision','language','target_channel','asset_refs',
            'asset_rights_status','technical_review_status','marketing_review_status','owner_approval_status',
            'consent_status','channel_status','proposed_cost','state','decision_log','idempotency_key','content_digest','created_at_utc','updated_at_utc','content_note')
    if type(p) is not dict:raise ContractError('INVALID_FIELD')
    if not set(fields) <= set(p):raise ContractError('MISSING_FIELD')
    if set(p)!=set(fields):raise ContractError('INVALID_FIELD')
    if type(p['package_id']) is not str or not re.fullmatch(r'P[1-3]-[a-z0-9-]{3,80}',p['package_id']):raise ContractError('BAD_ID')
    if type(p['source_sha']) is not str or not re.fullmatch(r'[0-9a-f]{40}',p['source_sha']) or type(p['revision']) is not int or p['revision']<1:raise ContractError('BAD_VERSION')
    if (type(p['source_ref']) is not str or len(p['source_ref'])>256 or
            p['source_ref']!='reports/evidence/2026-11-23-hermes-grow-01-s1-content-packages.json#'+p['package_id']):raise ContractError('INVALID_FIELD')
    if type(p['language']) is not str or p['language'] not in ('vi','en','en-vi') or type(p['target_channel']) is not str or p['target_channel'] not in ('youtube_shorts','youtube_video','wordpress_page'):
        raise ContractError('INVALID_FIELD')
    if type(p['asset_refs']) is not list or len(p['asset_refs'])>8:raise ContractError('INVALID_FIELD')
    for asset in p['asset_refs']:
        if (type(asset) is not dict or set(asset)!={'asset_ref','kind','rights'} or type(asset['asset_ref']) is not str
                or len(asset['asset_ref'])>100 or not re.fullmatch(r'placeholder-P[1-3]-[a-z0-9-]{3,80}',asset['asset_ref'])
                or asset['kind']!='synthetic_placeholder' or asset['rights']!='UNVERIFIED'):
            raise ContractError('INVALID_FIELD')
    for status in ('asset_rights_status','technical_review_status','marketing_review_status','consent_status','channel_status'):
        if type(p[status]) is not str or p[status] not in ('UNVERIFIED','VERIFIED_FIXTURE'):raise ContractError('INVALID_FIELD')
    if type(p['owner_approval_status']) is not str or p['owner_approval_status'] not in ('UNVERIFIED','FIXTURE_APPROVED_NOT_PUBLISH') or p['proposed_cost'] is not None:
        raise ContractError('INVALID_FIELD')
    states=('DRAFT','IN_REVIEW','NEEDS_CHANGES','READY_FOR_OWNER_REVIEW','APPROVED_FOR_OFFLINE_HANDOFF','BLOCKED','REJECTED')
    if type(p['state']) is not str or p['state'] not in states:raise ContractError('INVALID_FIELD')
    if (type(p['content_note']) is not str or not p['content_note'] or len(p['content_note'])>256
            or any(c in p['content_note'] for c in '<>&')):
        raise ContractError('INVALID_FIELD')  # Mock rejects markup; future UI must escape every string contextually.
    for name in ('created_at_utc','updated_at_utc'):
        if type(p[name]) is not str or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',p[name]):raise ContractError('INVALID_FIELD')
    if p['idempotency_key'] is not None and (type(p['idempotency_key']) is not str or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{2,63}',p['idempotency_key'])):
        raise ContractError('INVALID_FIELD')
    if type(p['decision_log']) is not list or len(p['decision_log'])>64:raise ContractError('INVALID_FIELD')
    if type(p['content_digest']) is not str or not re.fullmatch(r'[0-9a-f]{64}',p['content_digest']):raise ContractError('BAD_DIGEST')
    if p['content_digest']!=digest(content_projection(p)):raise ContractError('BAD_DIGEST')
    if len(canonical(p))>16384:raise ContractError('OVERSIZE')
    allowed={'submit_review':('DRAFT','editor','IN_REVIEW'), 'request_changes':('IN_REVIEW','reviewer','NEEDS_CHANGES'),
             'mark_ready':('IN_REVIEW','reviewer','READY_FOR_OWNER_REVIEW'), 'decide_owner':('READY_FOR_OWNER_REVIEW','owner','APPROVED_FOR_OFFLINE_HANDOFF'),
             'block':('IN_REVIEW','reviewer','BLOCKED'), 'reject':('READY_FOR_OWNER_REVIEW','owner','REJECTED')}
    state='DRAFT'; reviewed=False
    for record in p['decision_log']:
        if type(record) is not dict or set(record)!={'package_id','revision','content_digest','action','actor_role','at_utc','scope','idempotency_key','review_tokens'}:
            raise ContractError('INVALID_PROVENANCE')
        action=record['action']
        if (type(action) is not str or action not in allowed or state!=allowed[action][0]
                or record['actor_role']!=allowed[action][1] or record['package_id']!=p['package_id']
                or record['revision']!=p['revision'] or record['content_digest']!=p['content_digest']
                or record['scope']!='SYNTHETIC_OFFLINE_ONLY' or record['at_utc']!=UTC
                or type(record['idempotency_key']) is not str or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{2,63}',record['idempotency_key'])):
            raise ContractError('INVALID_PROVENANCE')
        if action=='mark_ready':
            if not _valid_review_tokens(record['review_tokens']):raise ContractError('INVALID_PROVENANCE')
            reviewed=True
        elif record['review_tokens'] is not None:raise ContractError('INVALID_PROVENANCE')
        state=allowed[action][2]
    if state!=p['state'] or p['idempotency_key']!=(p['decision_log'][-1]['idempotency_key'] if p['decision_log'] else None):
        raise ContractError('INVALID_PROVENANCE')
    for field in ('asset_rights_status','technical_review_status','marketing_review_status','consent_status','channel_status'):
        if p[field]!=('VERIFIED_FIXTURE' if reviewed else 'UNVERIFIED'):raise ContractError('INVALID_PROVENANCE')
    if p['owner_approval_status']!=('FIXTURE_APPROVED_NOT_PUBLISH' if state=='APPROVED_FOR_OFFLINE_HANDOFF' else 'UNVERIFIED'):
        raise ContractError('INVALID_PROVENANCE')
    return True

def audit_record(p, action, actor, key=None, review_tokens=None):
    return {'package_id':p['package_id'],'revision':p['revision'],'content_digest':p['content_digest'],
            'action':action,'actor_role':actor,'at_utc':UTC,'scope':'SYNTHETIC_OFFLINE_ONLY',
            'idempotency_key':key,'review_tokens':copy.deepcopy(review_tokens)}

class MockLedger:
    """Ephemeral in-process fixture store. Never accept a caller-provided dict as authority.

    This is not IAM, a signature, a durable log, or protection against hostile Python
    code running in this process. A service must supply its own trusted persistence.
    """
    __slots__ = ('__states','__requests')

    def __init__(self):
        self.__states = {(p['package_id'],p['revision']):copy.deepcopy(p) for p in fixture_packages()}
        self.__requests = {}

    def __len__(self):return len(self.__requests)

    def check(self,p):
        if self.__states.get((p['package_id'],p['revision'])) != p:
            raise ContractError('UNTRUSTED_STATE')

    def replay(self,p,key,sig):
        stored=self.__requests.get((p['package_id'],key))
        if stored is None:return None
        if stored['signature']!=sig:raise ContractError('KEY_COLLISION')
        return copy.deepcopy(stored['result'])

    def record(self,p,key,sig):
        self.__requests[(p['package_id'],key)]={'signature':sig,'result':copy.deepcopy(p)}
        self.__states[(p['package_id'],p['revision'])]=copy.deepcopy(p)

    def fork(self,child):
        identity=(child['package_id'],child['revision'])
        if identity in self.__states:raise ContractError('REVISION_COLLISION')
        self.__states[identity]=copy.deepcopy(child)

def _trusted_state(p,ledger):
    if not isinstance(ledger,MockLedger):raise ContractError('UNTRUSTED_STATE')
    ledger.check(p)

def transition(p, action, role, key, ledger, expected_revision, expected_digest, review_tokens=None):
    if type(action) is not str:raise ContractError('INVALID_TRANSITION')
    if action in ('publish','paid_render','schedule','upload'):raise ContractError('FORBIDDEN_SIDE_EFFECT')
    if action.startswith('callback_'):raise ContractError('UNKNOWN_CALLBACK')
    validate(p)
    _trusted_state(p,ledger)
    if not isinstance(key,str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{2,63}',key):raise ContractError('BAD_KEY')
    # This is a local in-memory simulation only. It is not durable and cannot authenticate a user.
    sig=digest({'package':p['package_id'],'action':action,'role':role,'revision':expected_revision,
                'content_digest':expected_digest,'review_tokens':review_tokens})
    replay=ledger.replay(p,key,sig)
    if replay is not None:return replay
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
        if not _valid_review_tokens(review_tokens):
            raise ContractError('MISSING_FIXTURE_REVIEW')
    updated=copy.deepcopy(p)
    if action=='mark_ready':
        updated.update(asset_rights_status='VERIFIED_FIXTURE',technical_review_status='VERIFIED_FIXTURE',
                 marketing_review_status='VERIFIED_FIXTURE',consent_status='VERIFIED_FIXTURE',channel_status='VERIFIED_FIXTURE')
    if action=='decide_owner':
        for field,error in [('asset_rights_status','RIGHTS_UNVERIFIED'),('technical_review_status','TECHNICAL_UNVERIFIED'),('marketing_review_status','MARKETING_UNVERIFIED'),('consent_status','CONSENT_UNVERIFIED'),('channel_status','CHANNEL_UNVERIFIED')]:
            if p.get(field)!='VERIFIED_FIXTURE':raise ContractError(error)
        if p.get('editor_role') == role:raise ContractError('SELF_APPROVAL')
        updated['owner_approval_status']='FIXTURE_APPROVED_NOT_PUBLISH'
    updated['state']=target
    updated['idempotency_key']=key
    updated['updated_at_utc']=UTC
    updated['decision_log'].append(audit_record(updated,action,role,key,review_tokens))
    validate(updated)
    p.clear();p.update(copy.deepcopy(updated))
    result=copy.deepcopy(updated)
    ledger.record(p,key,sig)
    return result

def fork_revision(p,role,note,ledger):
    validate(p)
    _trusted_state(p,ledger)
    if role != 'editor' or not isinstance(note,str) or not re.fullmatch(r'[a-zA-Z0-9_-]{3,64}',note):raise ContractError('BAD_FORK')
    child=copy.deepcopy(p)
    child['revision']+=1;child['content_note']=note;child['state']='DRAFT';child['decision_log']=[]
    child['asset_rights_status']='UNVERIFIED';child['technical_review_status']='UNVERIFIED'
    child['marketing_review_status']='UNVERIFIED';child['owner_approval_status']='UNVERIFIED';child['consent_status']='UNVERIFIED';child['channel_status']='UNVERIFIED'
    child['idempotency_key']=None;child['content_digest']=digest(content_projection(child));child['updated_at_utc']=UTC
    validate(child)
    ledger.fork(child)
    return child
