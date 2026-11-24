#!/usr/bin/env python3
"""KNG-01 candidate checks. Only stdlib; never modifies inputs."""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from provenance import GitObjects, SHA
import hashlib

PINNED_REFS={'main':'e385c1bea2070973e3007e5717f7e980348d6ab3', 'PR31':'a770de80a2467ca1789c820b63416209cf53b7d1', 'PR39':'22d741e3f1dd325540932dea63c3a6da635113c3'}
COMMON_PATHS={'README.md','PROJECT.md','STATE.md','AGENTS.md','CATALOG.yaml','rules/AGENT_WORKFLOW.md'}

ALLOWED = {'KEEP', 'MERGE', 'ARCHIVE', 'DELETE'}
STATES = {'KNG_ONLY', 'ON_HOLD_DEPENDENCY_KNG01', 'DONE_WITH_EVIDENCE', 'BLOCKED_SECURITY', 'BLOCKED_TECHNICAL'}
REQUIRED_RULES = {'AGENTS.md', 'rules/AGENT_WORKFLOW.md', 'rules/REPOSITORY_SECURITY.md', 'STATE.md'}
SECRET_RE = re.compile(r'(-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?i:password|client_secret|access_token|api_key)\s*[:=]\s*[\'\"]\S{8,}[\'\"])')
LINK_RE = re.compile(r'(?<!!)\[[^]]+\]\(([^)]+)\)')
ID_RE = re.compile(r'^\|\s*([A-Z][A-Z0-9-]+)\s*\|', re.M)


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def validate(root, *, verify_objects=True):
    root = Path(root)
    errors = []
    def reject(code, detail): errors.append({'code': code, 'detail': str(detail)})
    state = load(root / 'program/current.json')
    inventory = load(root / 'program/kng/inventory.json')
    migration = load(root / 'program/kng/migration.json')
    try: lock = load(root / 'program/kng/provenance-lock.json')
    except (OSError,ValueError) as exc:
        reject('PROVENANCE_UNVERIFIED', 'missing/invalid provenance lock: '+str(exc))
        return errors
    actual_git = GitObjects(root)
    sources = lock['sources']
    ref_pins = lock.get('refs', {})
    if ref_pins != PINNED_REFS: reject('SOURCE_PIN_MISMATCH', 'trusted main/PR31/PR39 commit pins drift')
    if state.get('main_sha') != PINNED_REFS['main'] or state.get('pr31_sha') != PINNED_REFS['PR31'] or state.get('pr39_source_sha') != PINNED_REFS['PR39']:
        reject('SOURCE_PIN_MISMATCH','candidate base refs drift')
    def validate_object(commit, path, blob, label):
        if verify_objects:
            try: actual_git.verify(commit, path, blob)
            except LookupError as exc: reject('PROVENANCE_UNVERIFIED', label + ': ' + str(exc))
            except ValueError as exc: reject('SOURCE_BLOB_MISMATCH', label + ': ' + str(exc))
    if state.get('mode') != 'KNG_ONLY': reject('UNSAFE_PRIORITY', state.get('mode'))
    if state.get('record_kind') != 'KNG_RELEASE_SOURCE_SNAPSHOT' or state.get('source_authority') != 'main_effective_rules_until_verified_activation': reject('WRONG_AUTHORITY', 'source snapshot cannot independently activate main')
    gate = state.get('release_gate', {})
    if not isinstance(gate, dict) or gate.get('phase') != 'PREMERGE_CANDIDATE' or gate.get('status') != 'NOT_EFFECTIVE' or gate.get('approval_event') is not None or gate.get('remote_main_readback') is not None:
        reject('UNVERIFIED_RELEASE_ACTIVATION', 'effective authority must be established by external authenticated A0 + main-tree readback')
    if set(state.get('must_read', [])) != REQUIRED_RULES: reject('MISSING_MANDATORY_RULE', state.get('must_read'))
    if state.get('catalog_registry') != 'CATALOG.yaml' or state.get('catalog_access') != 'INDEX_ONLY_VALIDATE_FULL_CATALOG_WITH_TOOL':
        reject('CATALOG_ACCESS_POLICY_MISMATCH', 'full registry must be machine-validated; agents read relevant entries only')
    if state.get('production_authorized') is not False or state.get('merge_authorized') is not False or state.get('codex_authorized') is not False: reject('UNSAFE_PERMISSION', 'production, merge and codex must remain false')
    # A real Work ACK must be bound to the exact dispatch, not a swapped task ID.
    if state.get('work_ack_task_id') is not None:
        reject('ACK_RECEIPT_MISMATCH', 'no new current Work dispatch; historical D2 task ID belongs only to historical QA record')
    if state.get('agent_status', {}).get('Work') != 'QA_COMPLETE_NO_NEW_TASK':
        reject('STALE_AGENT_STATE', 'Work must reflect completed source QA without new dispatch')
    work_qa = state.get('last_work_source_qa', {})
    if not isinstance(work_qa, dict) or work_qa.get('actor') != 'Work' or work_qa.get('task_id') != 'WORK-KNG01-PR42-FINAL-FIXTURE-MICRO-RECHECK' or work_qa.get('source_sha') != 'b8cd377d3c3696c486fed41adc941a9d4db92ecc' or work_qa.get('verdict') != 'KNG01_PR42_SOURCE_QA_PASS_WITH_FINAL_GATES' or work_qa.get('receipt_url') != 'https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7103815886' or work_qa.get('record_type') != 'HISTORICAL_COMPLETED_SOURCE_QA_NOT_NEW_ACK':
        reject('SOURCE_QA_PROVENANCE_MISMATCH', 'completed Work source QA must retain exact immutable D5 readback')
    if state.get('work_ack') not in ('UNKNOWN','ACKNOWLEDGED'): reject('FALSE_ACK', state.get('work_ack'))
    if state.get('work_ack') == 'ACKNOWLEDGED':
        receipt = state.get('work_ack_receipt')
        expected = lock.get('work_ack_receipt')
        if not isinstance(receipt, dict) or receipt != expected or not expected or 'PENDING_ACK' in state.get('agent_status',{}).get('Work',''):
            reject('ACK_RECEIPT_MISMATCH', 'Work ACK must match pinned task-specific immutable receipt and nonpending state')
    elif state.get('work_ack_receipt'):
        reject('ACK_RECEIPT_MISMATCH', 'receipt exists but work_ack is UNKNOWN')
    if state.get('agent_status',{}).get('Hostinger') != 'ON_HOLD_DEPENDENCY_KNG01': reject('STALE_AGENT_STATE', 'Hostinger')
    if not re.fullmatch('[a-f0-9]{40}', state.get('main_sha','')): reject('INVALID_SHA', 'main SHA')
    rows = inventory.get('facts', [])
    keys = [r.get('fact_key') for r in rows]
    if len(keys) != len(set(keys)): reject('DUPLICATE_FACT_ID', [x for x,c in Counter(keys).items() if c>1])
    for r in rows:
        if r.get('decision') not in ALLOWED: reject('INVALID_DISPOSITION', r.get('fact_key'))
        if not re.fullmatch('[a-f0-9]{40}', r.get('source_sha','')): reject('INVALID_SHA', r.get('fact_key'))
        key = r.get('fact_key')
        pin = sources.get(key)
        if not pin or (r.get('source_path'), r.get('source_sha'), r.get('recovery_ref')) != (pin['path'],pin['blob'],pin['ref']):
            reject('SOURCE_PIN_MISMATCH', key)
        else:
            label,_,commit = r['recovery_ref'].partition('@')
            if label not in ref_pins or ref_pins[label] != commit or commit != pin['commit']:
                reject('RECOVERY_REF_INVALID', key)
            else:
                validate_object(commit, r['source_path'], r['source_sha'], key)
        if r.get('decision') == 'DELETE' and not (r.get('reference_check') == 'CLEAR' and r.get('retention_check') == 'CLEAR' and r.get('recovery_ref')):
            reject('UNSAFE_DELETE', r.get('fact_key'))
        if r.get('decision') in ('MERGE','ARCHIVE','DELETE') and not r.get('recovery_ref'): reject('MISSING_RECOVERY', r.get('fact_key'))
    targets = [x.get('path') for x in migration.get('proposed_updates',[])]
    if len(targets)!=len(set(targets)): reject('DUPLICATE_MIGRATION_TARGET', targets)
    protected={'AGENTS.md','PROJECT.md','STATE.md','CATALOG.yaml','rules/AGENT_WORKFLOW.md','rules/REPOSITORY_SECURITY.md','README.md','CHANGELOG.md'}
    for x in migration.get('proposed_updates',[]):
        ex = x.get('execution')
        if x.get('path') in protected and ex not in ('PREVIEW_ONLY_SHARED_WRITER_GATE','APPLIED_ISOLATED_INTEGRATION'): reject('UNSAFE_SHARED_WRITE', x['path'])
        if ex == 'APPLIED_ISOLATED_INTEGRATION':
            integration = state.get('integration',{})
            if x.get('path') not in COMMON_PATHS or integration.get('mode') != 'HISTORICAL_D2_SOURCE_INTEGRATION' or integration.get('branch') != 'a1/kng01-shared-integration-d2-2026-11-23' or integration.get('grant_url') != 'https://github.com/DuyKienTTD/Hosting/pull/40#issuecomment-7098528192':
                reject('UNSAFE_SHARED_WRITE', x.get('path'))
            if x.get('source_ref','').split('@')[-1] != lock.get('migration_bases',{}).get(x.get('path'),{}).get('commit'):
                reject('SOURCE_PIN_MISMATCH', x.get('path'))
            target = root / x.get('path','')
            if not target.is_file():reject('MISSING_SOURCE', x.get('path'))
            else:
                actual_bytes=target.read_bytes()
                actual_hash=hashlib.sha1(b'blob '+str(len(actual_bytes)).encode()+b'\0'+actual_bytes).hexdigest()
                if x.get('result_blob') != actual_hash:
                    # The D2 result pin is an immutable historical claim, not the
                    # hash of every future governance candidate. Verify it against
                    # the independently pinned main integration commit; NEVER
                    # move the D2 pin to match working-tree edits.
                    if x.get('path') in ('AGENTS.md', 'rules/AGENT_WORKFLOW.md', 'README.md', 'STATE.md'):
                        validate_object('d549564de52429e777c68daf9df7a93df5f22f27',
                                        x['path'], x['result_blob'],
                                        'historical integrated result '+x['path'])
                        if not actual_bytes.strip() or b'NOT_EFFECTIVE' not in actual_bytes and b'candidate' not in actual_bytes.lower():
                            reject('UNSAFE_CURRENT_RULE', x['path']+' must remain an explicitly non-effective candidate')
                    else:
                        reject('INTEGRATED_BLOB_MISMATCH', x.get('path')+' '+actual_hash)

        if x.get('path') in protected and not x.get('pr31_conflict_review'): reject('MISSING_CONFLICT_REVIEW', x['path'])
        if not re.fullmatch('[a-f0-9]{40}',x.get('base_blob','')): reject('INVALID_SHA',x.get('path'))
        pin = lock.get('migration_bases', {}).get(x.get('path'))
        if not pin or pin['blob'] != x.get('base_blob'):
            reject('MIGRATION_BLOB_MISMATCH', x.get('path'))
        else:
            validate_object(pin['commit'], x['path'], x['base_blob'], 'migration '+x['path'])
    expected = state.get('source_paths', [])
    for path in expected:
        pp=PurePosixPath(path)
        if pp.is_absolute() or '..' in pp.parts or not (root/path).is_file():reject('MISSING_SOURCE',path)
    for rel in ('program/README.md','program/KNOWLEDGE_OPTIMIZATION.md','program/OPERATING_PROTOCOL.md','program/WORK_BREAKDOWN.md','program/roadmaps/a1.md'):
        path=root/rel
        if not path.is_file(): reject('MISSING_SOURCE',rel); continue
        data=path.read_text(encoding='utf-8')
        if SECRET_RE.search(data):reject('SECRET_LITERAL',rel)
        for target in LINK_RE.findall(data):
            if target.startswith(('http://','https://','#','mailto:')): continue
            file=target.split('#',1)[0]
            if not file: continue
            target_path=(path.parent/file).resolve()
            if not str(target_path).startswith(str(root.resolve())+'/') or not target_path.exists(): reject('BROKEN_LINK',rel+' -> '+target)
    wbs=(root/'program/WORK_BREAKDOWN.md').read_text(encoding='utf-8')
    wids=ID_RE.findall(wbs)
    if len(wids)!=len(set(wids)):reject('DUPLICATE_WBS_ID',str([k for k,n in Counter(wids).items() if n>1]))
    for forbidden in ('Hostinger is resumed for new hosting/infra work','Start G0-01 (A2), G1-01 (A1), INF-01 (Hostinger)'):
        for rel in ('program/README.md','program/WORK_BREAKDOWN.md'):
            if forbidden in (root/rel).read_text(encoding='utf-8'):reject('STALE_PRIORITY_TEXT',rel+': '+forbidden)
    if migration.get('implementation_status') == 'APPLIED_ON_ISOLATED_D2_BRANCH_NOT_MAIN':
        if set(targets) != COMMON_PATHS: reject('INCOMPLETE_SHARED_WRITE_SET', str(sorted(set(targets)^COMMON_PATHS)))
        try:
            from derive import run as check_generated
            if not check_generated(root): reject('DERIVED_MIRROR_DRIFT', 'STATE/CATALOG differs from typed source')
        except (ValueError,OSError,KeyError) as exc:reject('DERIVED_MIRROR_DRIFT',str(exc))
    # Catalog IDs must never collide, even if a source appears through many Git snapshots.
    catalog=root/'CATALOG.yaml'
    if catalog.is_file():
        ids=re.findall(r'^\s*- id:\s*(\S+)\s*$', catalog.read_text(encoding='utf8'),re.M)
        dupe=[k for k,n in Counter(ids).items() if n>1]
        if dupe:reject('DUPLICATE_CATALOG_ID',str(dupe))
    return sorted(errors,key=lambda e:(e['code'],e['detail']))


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--json',action='store_true');a=p.parse_args()
    errors=validate(a.root)
    if a.json: print(json.dumps({'status':'PASS' if not errors else 'FAIL','errors':errors},ensure_ascii=False,indent=2))
    else:
        print('PASS' if not errors else 'FAIL')
        for e in errors:print(e['code']+': '+e['detail'])
    return 0 if not errors else 1
if __name__=='__main__':sys.exit(main())
