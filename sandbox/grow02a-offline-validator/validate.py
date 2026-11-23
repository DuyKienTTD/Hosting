"""GROW-02A/S1-SUPPORT: deterministic offline contract checks, no network/IO beyond fixture.
Usage: python3 -B sandbox/grow02a-offline-validator/validate.py
"""
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'reports/evidence/2026-11-23-hermes-grow02a-s1-events-and-tests.json'


def validate_utm(url):
    p = urlsplit(url)
    if p.scheme != 'https' or p.hostname != 'example.invalid' or p.username or p.password or p.fragment:
        return 'BLOCKED_URL'
    pairs = parse_qsl(p.query, keep_blank_values=True)
    if len(pairs) != len(dict(pairs)):
        return 'BLOCKED_DUPLICATE_PARAMETER'
    query = dict(pairs)
    if any(k not in {'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'} for k in query):
        return 'BLOCKED_UNEXPECTED_PARAMETER'
    if any(k not in query or not re.fullmatch(r'[a-z0-9_]{2,48}', query[k]) for k in ('utm_source', 'utm_medium', 'utm_campaign')):
        return 'BLOCKED_MISSING_OR_INVALID_UTM'
    if any(not re.fullmatch(r'[a-z0-9_]{2,48}', v) for v in query.values()):
        return 'BLOCKED_INVALID_UTM'
    return 'VALID_DRAFT_URL'


def check(case, seen):
    kind = case['kind']
    if kind == 'utm':
        return validate_utm(case['url'])
    if kind == 'event':
        event_id = case['event_id']
        payload = case['payload']
        if event_id in seen:
            return 'DUPLICATE_IGNORED' if seen[event_id] == payload else 'BLOCKED_CONFLICTING_REPLAY'
        seen[event_id] = payload
        return 'ACCEPTED_SYNTHETIC'
    if kind == 'join':
        return 'BLOCKED_NO_CONSENT_OR_JOIN_POLICY' if not case['consent_and_join_policy_approved'] else 'NEEDS_SEPARATE_AUTH'
    if kind == 'qualification':
        return 'BLOCKED_NO_SALES_DECISION' if not case['sales_decision_exists'] else 'NEEDS_SEPARATE_AUTH'
    raise ValueError('unknown test case')


def main():
    d = json.loads(DATA.read_text())
    seen = {}
    assert d['task_id'] == 'GROW-02A/S1-SUPPORT'
    assert len(d['events']) >= 12
    assert len({e['name'] for e in d['events']}) == len(d['events'])
    for e in d['events']:
        assert re.fullmatch(r'[a-z][a-z0-9]*(?:_[a-z0-9]+)+', e['name'])
        assert e['required_fields'] and e['optional_fields'] is not None
        assert e['schema_version'] == d['schema_version']
        assert e['implementation_status'] in {'OFFLINE_PROPOSED', 'REAL_UNVERIFIED'}
        assert e['retention'] == 'PROPOSED_UNAPPROVED'
        assert all(e.get(k) for k in ('owner', 'trigger', 'source', 'unit', 'allowed_values', 'cardinality', 'idempotency', 'timestamp', 'privacy_class', 'consent_gate', 'supporting_pr'))
        assert 'event_id' in e['required_fields'] and 'occurred_at_utc' in e['required_fields']
    assert len(d['kpi_links']) == 16
    assert len({x['kpi_name'] for x in d['kpi_links']}) == 16
    assert all(x['baseline'] == 'BASELINE_UNKNOWN' for x in d['kpi_links'])
    assert all(x['measurement_status'] in {'MEASURABLE_OFFLINE', 'NEEDS_REAL_READ_AUTH', 'NEEDS_CONSENTED_CRM', 'NOT_MEASURABLE_YET'} for x in d['kpi_links'])
    assert all(x['source_refs'] and x['numerator'] and x['denominator'] for x in d['kpi_links'])
    assert all(x['event_or_source'] or x['gap'] for x in d['kpi_links'])
    for c in d['tests']:
        observed = check(c, seen)
        assert observed == c['expected'] == c['observed'], (c['id'], c['expected'], observed)
        print(f"{c['id']}: {observed}")
    assert len(d['tests']) >= 4
    assert all(v == 0 for v in d['side_effects'].values())
    print(f"PASS: events={len(d['events'])} kpi_links={len(d['kpi_links'])} tests={len(d['tests'])}; offline only")


if __name__ == '__main__':
    main()
