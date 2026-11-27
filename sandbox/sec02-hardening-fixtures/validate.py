"""SEC-02/S2: no-network tabletop gate evaluator; NEVER operates on real infrastructure."""
import json
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[2] / 'reports/evidence/2026-11-23-hostinger-sec02-s2-tabletop.json'
ORDER = ['IDENTITY_VERIFIED', 'BACKUP_RECOVERY_PLAN', 'ALTERNATE_ADMIN_ACCESS_CONFIRMED', 'CHANGE_APPROVAL', 'SINGLE_CONTROL_CHANGE', 'HEALTH_CHECK', 'ROLLBACK_DECISION']


def decision(flags):
    """Purely hypothetical stop/hold decision over booleans; not an approval engine."""
    if flags.get('secret_value_seen'):
        return 'STOP_REDACT_ESCALATE'
    if flags.get('identity_mismatch') or flags.get('resource_owner_ambiguous'):
        return 'STOP_WRONG_OR_UNKNOWN_TARGET'
    if flags.get('privileged_command_blocked'):
        return 'STOP_NO_BYPASS'
    if not flags.get('recovery_plan') or flags.get('restore_proof_required_and_missing'):
        return 'STOP_RECOVERY_UNPROVEN'
    if not flags.get('alternate_admin_access') or flags.get('lockout_risk'):
        return 'STOP_ACCESS_RISK'
    if not flags.get('two_person_review') or not flags.get('change_approved'):
        return 'STOP_NOT_AUTHORIZED'
    if flags.get('n8n_outage') or flags.get('tls_break') or flags.get('health_degraded') or flags.get('inference_failed_despite_dashboard_200'):
        return 'STOP_HEALTH_ROLLBACK_DECISION'
    return 'HOLD_FOR_SEPARATE_CHANGE_WINDOW'  # Never authorizes a production write.


def main():
    d = json.loads(EVIDENCE.read_text())
    assert d['task_id'] == 'SEC-02/S2' and d['dag'] == ORDER
    assert len(d['findings']) == 7 and {f['id'] for f in d['findings']} == {f'SEC02-F{i:02}' for i in range(1, 8)}
    assert len(d['work_orders']) >= 4 and all(w['authorization'] == 'NOT_AUTHORIZED' and w['inverse_state'] == 'PROPOSED_NOT_TESTED' and w['rollback_tested'] == 'UNKNOWN' for w in d['work_orders'])
    assert len({w['id'] for w in d['work_orders']}) == len(d['work_orders'])
    assert all(len(w['finding_ids']) >= 1 for w in d['work_orders'])
    assert len(d['cases']) >= 6 and len({c['id'] for c in d['cases']}) == len(d['cases'])
    for c in d['cases']:
        observed = decision(c['flags'])
        assert c['expected'] == c['observed'] == observed, (c['id'], c['expected'], observed)
        assert c['classification'] == 'ACTUALLY_EXECUTED_OFFLINE_POLICY_ONLY'
        print(c['id'], observed)
    assert all(value == 0 for value in d['side_effects'].values())
    print(f"PASS_OFFLINE_ONLY cases={len(d['cases'])} findings={len(d['findings'])} orders={len(d['work_orders'])}")


if __name__ == '__main__':
    main()
