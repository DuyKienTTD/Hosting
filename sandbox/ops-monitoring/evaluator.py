import json
from datetime import datetime, timezone
from pathlib import Path

POLICY = json.loads((Path(__file__).parent / 'policy.json').read_text())

def _ts(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)

def evaluate(samples):
    accepted, audit = [], []
    seen, previous = set(), None
    for sample in samples:
        sid = sample.get('sample_id')
        if not sid or sid in seen:
            audit.append({'type': 'DUPLICATE_SAMPLE', 'sample_id': sid})
            continue
        seen.add(sid)
        try:
            current = _ts(sample['observed_at_utc'])
        except Exception:
            audit.append({'type': 'INVALID_TIMESTAMP', 'sample_id': sid})
            continue
        if previous and current < previous:
            audit.append({'type': 'OUT_OF_ORDER_SAMPLE', 'sample_id': sid})
            continue
        previous = current
        if sample.get('resource_alias') != POLICY['expected_resource_alias']:
            audit.append({'type': 'IDENTITY_MISMATCH', 'sample_id': sid})
            continue
        if sample.get('source') not in POLICY['allowed_sources']:
            audit.append({'type': 'SOURCE_UNKNOWN', 'sample_id': sid})
            continue
        accepted.append(sample)

    decisions = []
    emitted = set()
    def add(rule, state, refs, reason, severity='info', **extra):
        key = f"{POLICY['expected_resource_alias']}:{rule}"
        if key in emitted and state == 'OPEN':
            audit.append({'type': 'COOLDOWN_SUPPRESSED', 'rule': rule, 'cooldown_seconds': POLICY['dedupe']['cooldown_seconds']})
            return
        emitted.add(key)
        item = {'rule_version': POLICY['rule_version'], 'rule': rule, 'state': state, 'sample_refs': refs, 'reason': reason, 'severity': severity}
        item.update(extra)
        decisions.append(item)

    def streak(measure, predicate, count=3):
        groups, run = [], []
        rows = [x for x in accepted if x.get('measure_name') == measure]
        for row in rows:
            if predicate(row):
                run.append(row)
            else:
                if len(run) >= count: groups.append(run)
                run = []
        if len(run) >= count: groups.append(run)
        return groups

    bad = streak('n8n_readiness', lambda x: x.get('value') == 503)
    if bad:
        add('N8N_READINESS', 'OPEN', [x['sample_id'] for x in bad[-1]], 'three coherent readiness failures', 'high')
    good = streak('n8n_readiness', lambda x: x.get('value') == 200)
    if good and bad:
        add('N8N_READINESS', 'RECOVER', [x['sample_id'] for x in good[-1]], 'three coherent readiness successes', 'info')
    disk = streak('disk_used_pct', lambda x: isinstance(x.get('value'), (int, float)) and x['value'] >= POLICY['proposed_thresholds']['disk_high_pct'])
    if disk:
        add('DISK_HIGH', 'OPEN', [x['sample_id'] for x in disk[-1]], 'disk at or above proposed threshold', 'high')
    deadline = streak('disk_trend_deadline_hours', lambda x: isinstance(x.get('value'), (int, float)) and x['value'] <= POLICY['proposed_thresholds']['disk_deadline_hours'])
    if deadline:
        add('DISK_TREND_DEADLINE', 'OPEN', [x['sample_id'] for x in deadline[-1]], 'three coherent deadline samples', 'high')
    for sample in accepted:
        measure, value = sample.get('measure_name'), sample.get('value')
        if measure == 'backup_age_hours' and isinstance(value, (int, float)) and value > 192:
            add('BACKUP_AGE', 'OVERDUE', [sample['sample_id']], 'backup overdue; restore UNKNOWN', 'medium', restore_status='UNKNOWN')
        if measure == 'p0_reasoner_state' and value == 'exited_137' and sample.get('oom_killed') is False:
            add('P0_REASONER', 'RISK', [sample['sample_id']], 'exit 137, OOMKilled false, root cause UNKNOWN', 'high', root_cause='UNKNOWN')
        if measure == 'tls_probe' and value in ('absent', 'blocked'):
            add('TLS', 'UNKNOWN', [sample['sample_id']], 'TLS source absent or blocked', 'medium')
    if any(x['type'] == 'IDENTITY_MISMATCH' for x in audit):
        add('IDENTITY', 'BLOCK', [], 'identity mismatch; no health inference', 'high')
    if any(x['type'] == 'SOURCE_UNKNOWN' for x in audit):
        add('SOURCE', 'UNKNOWN', [], 'source unknown; no health inference', 'medium')
    return {'rule_version': POLICY['rule_version'], 'decisions': decisions, 'audit': audit, 'accepted_samples': len(accepted), 'external_transport': False}
