#!/usr/bin/env python3
"""KNG-01 candidate checks. Only stdlib; never modifies inputs."""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path, PurePosixPath

ALLOWED = {'KEEP', 'MERGE', 'ARCHIVE', 'DELETE'}
STATES = {'KNG_ONLY', 'ON_HOLD_DEPENDENCY_KNG01', 'DONE_WITH_EVIDENCE', 'BLOCKED_SECURITY', 'BLOCKED_TECHNICAL'}
REQUIRED_RULES = {'AGENTS.md', 'rules/AGENT_WORKFLOW.md', 'rules/REPOSITORY_SECURITY.md', 'STATE.md', 'CATALOG.yaml'}
SECRET_RE = re.compile(r'(-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?i:password|client_secret|access_token|api_key)\s*[:=]\s*[\'\"]\S{8,}[\'\"])')
LINK_RE = re.compile(r'(?<!!)\[[^]]+\]\(([^)]+)\)')
ID_RE = re.compile(r'^\|\s*([A-Z][A-Z0-9-]+)\s*\|', re.M)


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def validate(root):
    root = Path(root)
    errors = []
    def reject(code, detail): errors.append({'code': code, 'detail': str(detail)})
    state = load(root / 'program/current.json')
    inventory = load(root / 'program/kng/inventory.json')
    migration = load(root / 'program/kng/migration.json')
    if state.get('mode') != 'KNG_ONLY': reject('UNSAFE_PRIORITY', state.get('mode'))
    if state.get('source_authority') != 'main_effective_rules_until_approved_merge': reject('WRONG_AUTHORITY', 'candidate cannot supersede main')
    if set(state.get('must_read', [])) != REQUIRED_RULES: reject('MISSING_MANDATORY_RULE', state.get('must_read'))
    if state.get('production_authorized') is not False or state.get('merge_authorized') is not False or state.get('codex_authorized') is not False: reject('UNSAFE_PERMISSION', 'production, merge and codex must remain false')
    if state.get('work_ack') not in ('UNKNOWN','ACKNOWLEDGED'): reject('FALSE_ACK', state.get('work_ack'))
    if state.get('agent_status',{}).get('Hostinger') != 'ON_HOLD_DEPENDENCY_KNG01': reject('STALE_AGENT_STATE', 'Hostinger')
    if not re.fullmatch('[a-f0-9]{40}', state.get('main_sha','')): reject('INVALID_SHA', 'main SHA')
    rows = inventory.get('facts', [])
    keys = [r.get('fact_key') for r in rows]
    if len(keys) != len(set(keys)): reject('DUPLICATE_FACT_ID', [x for x,c in Counter(keys).items() if c>1])
    for r in rows:
        if r.get('decision') not in ALLOWED: reject('INVALID_DISPOSITION', r.get('fact_key'))
        if not re.fullmatch('[a-f0-9]{40}', r.get('source_sha','')): reject('INVALID_SHA', r.get('fact_key'))
        if r.get('decision') == 'DELETE' and not (r.get('reference_check') == 'CLEAR' and r.get('retention_check') == 'CLEAR' and r.get('recovery_ref')):
            reject('UNSAFE_DELETE', r.get('fact_key'))
        if r.get('decision') in ('MERGE','ARCHIVE','DELETE') and not r.get('recovery_ref'): reject('MISSING_RECOVERY', r.get('fact_key'))
    targets = [x.get('path') for x in migration.get('proposed_updates',[])]
    if len(targets)!=len(set(targets)): reject('DUPLICATE_MIGRATION_TARGET', targets)
    protected={'AGENTS.md','PROJECT.md','STATE.md','CATALOG.yaml','rules/AGENT_WORKFLOW.md','rules/REPOSITORY_SECURITY.md','README.md','CHANGELOG.md'}
    for x in migration.get('proposed_updates',[]):
        if x.get('path') in protected and x.get('execution') != 'PREVIEW_ONLY_SHARED_WRITER_GATE': reject('UNSAFE_SHARED_WRITE', x['path'])
        if x.get('path') in protected and not x.get('pr31_conflict_review'): reject('MISSING_CONFLICT_REVIEW', x['path'])
        if not re.fullmatch('[a-f0-9]{40}',x.get('base_blob','')): reject('INVALID_SHA',x.get('path'))
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
