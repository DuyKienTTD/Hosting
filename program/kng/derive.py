#!/usr/bin/env python3
"""Derive the bounded human KNG state from typed source, never reverse.

This is a candidate-only operation. No GitHub, production, or external IO.
"""
import argparse
import json
import re
from pathlib import Path

BEGIN='<!-- KNG:BEGIN_GENERATED -->'
END='<!-- KNG:END_GENERATED -->'

def source(root):
    return json.loads((Path(root)/'program/current.json').read_text(encoding='utf8'))

def generated_lines(j):
    pins=(j['main_sha'],j['pr31_sha'])
    if not all(re.fullmatch('[a-f0-9]{40}',z) for z in pins):
        raise ValueError('invalid source pins')
    work=j['agent_status']['Work']
    handoff=j.get('current_handoffs',{}).get('WS-02',{})
    status=handoff.get('status','UNKNOWN')
    receipt=handoff.get('ack_receipt')
    if status=='ACKNOWLEDGED' and not (isinstance(receipt,dict) and receipt.get('task_id')=='WS-02' and receipt.get('actor')=='Work' and receipt.get('immutable_evidence_url')):
        raise ValueError('ACK_RECEIPT_MISMATCH for WS-02')
    acceptance=j.get('acceptance_index',{}).get('WS-02',{})
    report=acceptance.get('last_evidence')
    if report and not (isinstance(report,dict) and report.get('path','').startswith('reports/') and re.fullmatch('[a-f0-9]{40}',report.get('git_blob',''))):
        raise ValueError('ACCEPTANCE_PROVENANCE_INVALID')
    evidence=(report.get('path') if report else 'NONE')
    return '\n'.join([
       '- **Portfolio priority:** KNG_ONLY.',
       '- **Director:** Chat Điều phối. **Implementation:** A1. **Independent QA:** Work; D1 finding needs A1 delta; D2 reviewer ACK pending.' if work=='KNG_D2_TARGETED_REQA_PENDING_ACK' else '- **Director:** Chat Điều phối. **Implementation:** A1. **Independent QA status:** '+work+'.',
       '- **Effective main:** `'+pins[0]+'`. **PR31 draft:** `'+pins[1]+'`.',
       '- **Permission gates:** production=false, paid=false, merge=false, Codex=false; PR/branch does not authorize live work. New non-KNG dispatch is ON_HOLD.',
       '- **WS-02 historical handoff:** '+status+'; receipt='+('VERIFIED_REFERENCE' if receipt else 'NONE')+'; new report='+evidence+'.'
    ])

def materialize_state(text,j):
    if text.count(BEGIN)!=1 or text.count(END)!=1: raise ValueError('STATE marker missing or repeated')
    a=text.index(BEGIN)+len(BEGIN);b=text.index(END)
    if b<a:raise ValueError('bad marker order')
    return text[:a]+'\n'+generated_lines(j)+'\n'+text[b:]

CAT_BEGIN='  # KNG:BEGIN_GENERATED_REPORTS'
CAT_END='  # KNG:END_GENERATED_REPORTS'

def materialize_catalog(text,j):
    if text.count(CAT_BEGIN)!=1 or text.count(CAT_END)!=1:raise ValueError('CATALOG generated marker missing/duplicated')
    a=text.index(CAT_BEGIN)+len(CAT_BEGIN);b=text.index(CAT_END)
    if b<a:raise ValueError('bad catalog marker order')
    acceptance=j.get('acceptance_index',{}).get('WS-02',{})
    report=acceptance.get('last_evidence')
    lines=[]
    if report:
        path=report.get('path','')
        if not path.startswith('reports/') or '..' in Path(path).parts:raise ValueError('unsafe acceptance path')
        if not re.fullmatch('[a-f0-9]{40}',report.get('git_blob','')):raise ValueError('invalid report blob')
        lines=[
            '  - id: kng-derived-ws02-paper-report',
            '    path: '+path,
            '    type: report',
            '    status: accepted-paper-exercise-not-live',
            '    authoritative_for: ws02-paper-exercise-accepted-evidence',
            '    updated_at: 2026-11-23',
            '    sensitivity: public-redacted'
        ]
    return text[:a]+'\n'+('\n'.join(lines)+'\n' if lines else '')+text[b:]

def run(root,write=False):
    root=Path(root);p=root/'STATE.md'
    data=source(root)
    old=p.read_text(encoding='utf8');new=materialize_state(old,data)
    cp=root/'CATALOG.yaml';co=cp.read_text(encoding='utf8');cn=materialize_catalog(co,data)
    if write:
        if old!=new:p.write_text(new,encoding='utf8')
        if co!=cn:cp.write_text(cn,encoding='utf8')
        return True
    return old==new and co==cn

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    ok=run(a.root,a.write)
    print('PASS' if ok else 'DERIVED_STATE_DRIFT')
    raise SystemExit(0 if ok else 1)
