---
task: OPS-01A/S2-D1
owner: Hostinger
next_owner: ChatGPT Điều phối
status: executed-offline-pending-work-reqa
verdict: OPS01A_S2_D1_LIFECYCLE_REMEDIATION_PASS_OFFLINE
---
# OPS-01A/S2-D1 Lifecycle Remediation

## Scope

Single focused repair on existing PR #24 branch `hostinger/ops-01a-s2-lifecycle-2026-11-23`. No VPS/KVM2, production, live metrics, credentials, cron, webhooks, notifications, paid provider, backup, firewall, SSH or TLS access.

Source HEAD before write: `d981c8189d30f87d5b1349525062322154719e64`. Base `main`: `e385c1bea2070973e3007e5717f7e980348d6ab3`.

## Findings fixed

1. Full input validation now runs before control-state mutation. Wrong resource/source/rule version, invalid timestamp, stale/blocked/unknown samples and non-advancing timestamps cannot advance trusted time, seen IDs, streaks or incident sequence.
2. Exact replay and same-ID conflicting replay are distinguished and rejected before control-state mutation. Wrong-source future samples no longer poison a corrected valid sample.
3. Strict UTC advancement prevents equal timestamps with different IDs from qualifying as successive samples.
4. Incident lifecycle and notification cooldown are separated. `OPEN` + bad×3 emits suppression at +899 and notification eligibility at +900/+901 without creating a new incident. `RECOVERED` + bad×3 creates a fresh incident independent of prior notification cooldown; emission is reported separately.
5. Events now carry stable `incident_id`, `sequence`, dedupe key and `notification_emitted`.
6. The S1 composition claim is narrowed to a pinned minimal evaluator fixture in tests. No runtime S1 behavior is changed or claimed.
7. Synthetic snapshot/replay does not create a duplicate incident.

## Focused D1 tests

- Input identity, invalid timestamp, wrong rule version, stale and blocked rejection with control snapshot unchanged.
- Corrected sample acceptance after rejected future/wrong-source sample.
- Exact timestamp boundary: duplicate timestamp IDs do not form bad×3.
- OPEN state at +899/+900/+901.
- RECOVERED state at +899/+900/+901 with fresh incident sequence.
- Exact/conflicting replay and UTC clock reversal.
- Pinned S1 evaluator composition: bad×3 -> OPEN and good×3 -> RECOVERED.
- Synthetic snapshot/replay with no duplicate incident.

Environment: offline synthetic only. No broad historical rerun; original S2 10/10 provenance is preserved separately.

## Handoff

`OPS01A_S2_D1_LIFECYCLE_REMEDIATION_PASS_OFFLINE`

This is not live monitoring, not a production sign-off, and not an independent Work QA acceptance. Work must re-QA the new PR #24 HEAD.
