"""BIZ-02/S2 synthetic decision-table checker. Stdlib, local fixture only.
Run: python3 -B sandbox/biz02-mvp-acceptance/validate.py
Not a browser, server-auth, connector or production test.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'reports/evidence/2026-11-23-hermes-biz02-s2-mvp-scenarios.json'
SOURCE = 'origin/hermes/biz-02-s1-priorities-kpi-draft-2026-11-23:reports/evidence/2026-11-23-hermes-biz02-s1-priority-matrix.json'
ALLOWED = {'ACCEPT_OFFLINE', 'STUB_ONLY', 'BLOCKED_NEEDS_BACKEND', 'BLOCKED_NEEDS_A0', 'BLOCKED_ACCESS', 'NOT_TESTED'}


def classify(flags):
    """Offline policy decision only; never pretends to call a UI/backend."""
    if not flags.get('synthetic'):
        return 'BLOCKED_ACCESS'
    action = flags.get('action')
    if action == 'live_site_read' and not flags.get('read_auth'):
        return 'BLOCKED_ACCESS'
    if action in {'publish', 'write_site', 'identity_join', 'ads_write'}:
        return 'BLOCKED_NEEDS_A0'
    if action in {'paid_retry', 'server_approve', 'activate_live'}:
        return 'BLOCKED_NEEDS_BACKEND'
    if action == 'claim_inference':
        return 'NOT_TESTED'  # dashboard HTTP 200 proves no model completion
    if action in {'ack', 'review_gap', 'aggregate_report', 'submit_draft', 'simulate'}:
        return 'ACCEPT_OFFLINE'
    return 'NOT_TESTED'


def validate(data, source):
    stories = data['stories']
    cases = data['scenarios']
    trace = data['traceability']
    assert len(stories) == 5
    assert len(cases) >= 10 and len({c['case_id'] for c in cases}) == len(cases)
    assert len(trace) == len(source['use_cases']) == 8
    assert {t['use_case_id'] for t in trace} == {u['id'] for u in source['use_cases']}
    assert len(data['a0_pending']) == len(source['a0_decisions']) == 5
    assert [(a['id'], a['status'], a['question']) for a in data['a0_pending']] == [(a['id'], a['status'], a['question']) for a in source['a0_decisions']]
    assert all(a['status'] == 'AWAITING_A0_DECISION' for a in data['a0_pending'])
    ids = {s['id'] for s in stories}
    assert len(ids) == 5
    for s in stories:
        assert s['source_prs'] and all(p.startswith('#') for p in s['source_prs'])
        assert set(s['source_prs']) <= set(s['source_paths'])
        assert s['actor'] and s['preconditions'] and s['synthetic_input'] and len(s['steps']) >= 3
        assert s['approval_gate'] and s['audit'] and s['blocked_transitions'] and s['nonfunctional']
        assert s['coverage_status'] in ALLOWED and s['product_test_status'] == 'NOT_TESTED'
        assert len([c for c in cases if c['story_id'] == s['id']]) >= 2
        assert any(c['expected_status'].startswith('BLOCKED') or c['expected_status'] == 'NOT_TESTED' for c in cases if c['story_id'] == s['id'])
    for c in cases:
        assert c['story_id'] in ids and c['fixture_id'] == 'FX-' + c['story_id']
        assert c['failure_signal'] and c['expected_receipt'] and c['expected_audit']
        assert c['expected_status'] in ALLOWED
        actual = classify(c['input_flags'])
        assert actual == c['expected_status'] == c['observed'], (c['case_id'], actual, c['expected_status'], c['observed'])
        assert c['execution_method'] == 'OFFLINE_POLICY_EVALUATOR_EXECUTED'
        assert c['product_functional_result'] == 'NOT_TESTED'
        assert c['design_verdict'] == 'PASS_TABLETOP'
        print(c['case_id'], actual, 'policy_only')
    for row in trace:
        u = next(u for u in source['use_cases'] if u['id'] == row['use_case_id'])
        assert row['source_tier_unchanged'] == u['tier']
        assert row['kpis'] == [u['leading_kpi'], u['lagging_kpi']]
        assert len(row['kpis']) == 2 and all(k['baseline'] == 'BASELINE_UNKNOWN' for k in row['kpis'])
        assert row['story_ids'] and set(row['story_ids']) <= ids
        assert row['source_prs'] and row['scenario_ids'] and row['unmet_gate']
        assert set(row['scenario_ids']) <= {c['case_id'] for c in cases}
    assert data['minimum_launch_slice']['name'] == 'MVP_OFFLINE_DEMO'
    assert set(data['minimum_launch_slice']['recommended_story_ids']) == ids
    assert all(v == 0 for v in data['side_effects'].values())
    assert data['validator_status'] == 'EXECUTED_OFFLINE_POLICY_ONLY'
    print('PASS: 5 stories,', len(cases), 'policy cases, 8 UC, 16 unchanged KPI, 5 pending A0; product functional NOT_TESTED')


if __name__ == '__main__':
    data = json.loads(DATA.read_text())
    source = json.loads(subprocess.check_output(['git', 'show', SOURCE], cwd=ROOT))
    validate(data, source)
