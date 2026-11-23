#!/usr/bin/env python3
"""Safely derive KNG views from typed evidence; no trust from unverified claims."""
import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from provenance import GitObjects

BEGIN = '<!-- KNG:BEGIN_GENERATED -->'
END = '<!-- KNG:END_GENERATED -->'
CAT_BEGIN = '  # KNG:BEGIN_GENERATED_REPORTS'
CAT_END = '  # KNG:END_GENERATED_REPORTS'
SHA = re.compile(r'^[0-9a-f]{40}$')
WS02_TASK = 'tasks/2026-11-22-work-ws02-monitoring-and-triage.md'
WS02_ACTOR = 'Work'
WS02_ID = 'WS-02'
D2_WORK_ID = 'WORK-KNG01-D2-TARGETED-INDEPENDENT-REQA'


def source(root):
    return json.loads((Path(root) / 'program/current.json').read_text(encoding='utf8'))


def _safe_path(value, prefix=None):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('PROVENANCE_UNVERIFIED: invalid source path')
    p = PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or str(p) != value or (prefix and not value.startswith(prefix)):
        raise ValueError('PROVENANCE_UNVERIFIED: unsafe source path')
    return value


def _git_evidence(root, evidence, code):
    """Resolve the precise immutable Git blob and return its bytes.

    A URL, a 40-character SHA, or a JSON field is not itself evidence. The
    commit/path/blob triple must be resolvable in the selected Git graph.
    """
    if not isinstance(evidence, dict):
        raise ValueError(code + ': evidence object missing')
    commit, path, blob = (evidence.get(k) for k in ('commit', 'path', 'git_blob'))
    if not isinstance(commit, str) or not SHA.fullmatch(commit) or not isinstance(blob, str) or not SHA.fullmatch(blob):
        raise ValueError(code + ': invalid pinned commit/blob')
    _safe_path(path)
    try:
        GitObjects(root).verify(commit, path, blob)
        raw = GitObjects(root).run('show', commit + ':' + path)
    except (LookupError, ValueError) as exc:
        raise ValueError(code + ': PROVENANCE_UNVERIFIED: ' + str(exc)) from exc
    return raw


def _receipt(root, handoff):
    status = handoff.get('status', 'UNKNOWN')
    receipt = handoff.get('ack_receipt')
    if status != 'ACKNOWLEDGED':
        if receipt is not None:
            raise ValueError('ACK_RECEIPT_MISMATCH: receipt claimed without acknowledged state')
        return False
    if handoff.get('source_task') != WS02_TASK:
        raise ValueError('ACK_RECEIPT_MISMATCH: wrong source task')
    if not isinstance(receipt, dict) or receipt.get('task_id') != WS02_ID or receipt.get('actor') != WS02_ACTOR or receipt.get('event') != 'ACK' or receipt.get('status') != 'ACKNOWLEDGED' or receipt.get('authorized_task_id') != WS02_TASK:
        raise ValueError('ACK_RECEIPT_MISMATCH: task/actor/event/status mismatch')
    if receipt.get('immutable_evidence_url'):
        expected_url = 'https://github.com/DuyKienTTD/Hosting/blob/' + str(receipt.get('commit')) + '/' + str(receipt.get('path'))
        if receipt['immutable_evidence_url'] != expected_url:
            raise ValueError('ACK_RECEIPT_MISMATCH: URL not bound to exact commit/path')
    raw = _git_evidence(root, receipt, 'ACK_RECEIPT_MISMATCH')
    try:
        observed = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError('ACK_RECEIPT_MISMATCH: source is not structured receipt') from exc
    required = ('task_id', 'actor', 'event', 'status', 'authorized_task_id', 'source_task')
    if any(observed.get(k) != receipt.get(k) for k in required) or observed.get('source_task') != WS02_TASK:
        raise ValueError('ACK_RECEIPT_MISMATCH: source fields differ from receipt claim')
    if observed.get('immutable_evidence_url') != receipt.get('immutable_evidence_url'):
        raise ValueError('ACK_RECEIPT_MISMATCH: URL is not bound to source')
    return True


def _report_metadata(raw):
    try:
        result = json.loads(raw)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, TypeError):
        pass
    lines = raw.splitlines()
    if not lines or lines[0].strip() != '---':
        raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: missing structured report disposition')
    result = {}
    for line in lines[1:]:
        if line.strip() == '---':
            return result
        if ':' in line and not line.startswith((' ', '\t')):
            k, v = line.split(':', 1)
            if k in result:
                raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: duplicate frontmatter key')
            result[k.strip()] = v.strip().strip('\"\'')
    raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: unclosed frontmatter')


def _accepted_report(root, record):
    if not isinstance(record, dict):
        raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: acceptance record missing')
    report = record.get('last_evidence')
    review = record.get('review_state', 'UNKNOWN_NEW_REPORT')
    if report is None:
        if review == 'ACCEPTED_PAPER_EXERCISE':
            raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: accepted with no report')
        return None
    if review != 'ACCEPTED_PAPER_EXERCISE':
        raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: evidence not accepted')
    if not isinstance(report, dict):
        raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: report metadata malformed')
    path = _safe_path(report.get('path'), 'reports/')
    if report.get('task_id') != WS02_ID or report.get('actor') != WS02_ACTOR or report.get('disposition') != 'ACCEPTED_PAPER_EXERCISE':
        raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: task/actor/disposition mismatch')
    raw = _git_evidence(root, report, 'ACCEPTANCE_PROVENANCE_INVALID')
    if not raw.strip():
        raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: empty report')
    # Evidence must be machine-verifiable rather than accepted by filename alone.
    observed = _report_metadata(raw)
    required = {'task_id': WS02_ID, 'actor': WS02_ACTOR, 'disposition': 'ACCEPTED_PAPER_EXERCISE', 'path': path}
    if any(observed.get(k) != v for k, v in required.items()):
        raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: source disposition mismatch')
    if observed.get('evidence_ref') != report.get('evidence_ref') or not observed.get('evidence_ref'):
        raise ValueError('ACCEPTANCE_PROVENANCE_INVALID: source evidence ref missing/mismatched')
    return report


def verified_views(root, j):
    pins = (j['main_sha'], j['pr31_sha'])
    if not all(isinstance(x, str) and SHA.fullmatch(x) for x in pins):
        raise ValueError('PROVENANCE_UNVERIFIED: invalid source pins')
    if j.get('work_ack_task_id') != D2_WORK_ID:
        raise ValueError('ACK_RECEIPT_MISMATCH: stale D2 task binding')
    work_ack = j.get('work_ack', 'UNKNOWN')
    work_receipt = j.get('work_ack_receipt')
    work_status = j.get('agent_status', {}).get('Work', '')
    if work_ack == 'UNKNOWN':
        if work_receipt is not None:
            raise ValueError('ACK_RECEIPT_MISMATCH: Work D2 receipt without ACK state')
    elif work_ack == 'ACKNOWLEDGED':
        if 'PENDING_ACK' in work_status or not isinstance(work_receipt, dict):
            raise ValueError('ACK_RECEIPT_MISMATCH: Work D2 pending or missing receipt')
        if any(work_receipt.get(k) != v for k, v in {
            'task_id': D2_WORK_ID, 'actor': WS02_ACTOR,
            'event': 'ACK', 'status': 'ACKNOWLEDGED'}.items()):
            raise ValueError('ACK_RECEIPT_MISMATCH: Work D2 task/actor/event/status mismatch')
        raw = _git_evidence(root, work_receipt, 'ACK_RECEIPT_MISMATCH')
        try:
            observed = json.loads(raw)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError('ACK_RECEIPT_MISMATCH: invalid Work D2 evidence content') from exc
        if any(observed.get(k) != work_receipt.get(k) for k in ('task_id', 'actor', 'event', 'status')):
            raise ValueError('ACK_RECEIPT_MISMATCH: Work D2 evidence differs from claim')
    else:
        raise ValueError('ACK_RECEIPT_MISMATCH: invalid Work D2 ACK state')
    handoff = j.get('current_handoffs', {}).get('WS-02', {})
    ack = _receipt(root, handoff)
    report = _accepted_report(root, j.get('acceptance_index', {}).get('WS-02', {}))
    return pins, handoff.get('status', 'UNKNOWN'), ack, report


def generated_lines(j, root='.'):
    pins, status, ack, report = verified_views(root, j)
    work = j['agent_status']['Work']
    evidence = report['path'] if report else 'NONE'
    role = ('- **Director:** Chat Điều phối. **Implementation:** A1. **Independent QA:** Work; D1 finding needs A1 delta; D2 reviewer ACK pending.'
            if work == 'KNG_D2_TARGETED_REQA_PENDING_ACK' else
            '- **Director:** Chat Điều phối. **Implementation:** A1. **Independent QA status:** ' + work + '.')
    return '\n'.join([
       '- **Portfolio priority:** KNG_ONLY.', role,
       '- **Effective main:** `' + pins[0] + '`. **PR31 draft:** `' + pins[1] + '`.',
       '- **Permission gates:** production=false, paid=false, merge=false, Codex=false; PR/branch does not authorize live work. New non-KNG dispatch is ON_HOLD.',
       '- **WS-02 historical handoff:** ' + status + '; receipt=' + ('VERIFIED_REFERENCE' if ack else 'NONE') + '; new report=' + evidence + '.'
    ])


def _replace_markers(text, begin, end, body, code):
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ValueError(code + ': marker missing or repeated')
    a = text.index(begin) + len(begin)
    b = text.index(end)
    if b < a:
        raise ValueError(code + ': invalid marker order')
    return text[:a] + '\n' + (body + '\n' if body else '') + text[b:]


def materialize_state(text, j, root='.'):
    return _replace_markers(text, BEGIN, END, generated_lines(j, root), 'STATE')


def materialize_catalog(text, j, root='.'):
    _, _, _, report = verified_views(root, j)
    lines = []
    if report:
        lines = [
            '  - id: kng-derived-ws02-paper-report',
            '    path: ' + report['path'],
            '    type: report',
            '    status: accepted-paper-exercise-not-live',
            '    authoritative_for: ws02-paper-exercise-accepted-evidence',
            '    updated_at: 2026-11-23',
            '    sensitivity: public-redacted'
        ]
    return _replace_markers(text, CAT_BEGIN, CAT_END, '\n'.join(lines), 'CATALOG')


def run(root, write=False):
    root = Path(root)
    j = source(root)
    state = root / 'STATE.md'
    catalog = root / 'CATALOG.yaml'
    old_state = state.read_text(encoding='utf8')
    old_catalog = catalog.read_text(encoding='utf8')
    # Validate BOTH outputs and ALL Git evidence before the first write.
    new_state = materialize_state(old_state, j, root)
    new_catalog = materialize_catalog(old_catalog, j, root)
    if write:
        if old_state != new_state:
            state.write_text(new_state, encoding='utf8')
        if old_catalog != new_catalog:
            catalog.write_text(new_catalog, encoding='utf8')
        return True
    return old_state == new_state and old_catalog == new_catalog


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    try:
        ok = run(a.root, a.write)
    except (ValueError, LookupError, KeyError, OSError) as exc:
        print('FAIL: ' + str(exc))
        return 1
    print('PASS' if ok else 'DERIVED_STATE_DRIFT')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
