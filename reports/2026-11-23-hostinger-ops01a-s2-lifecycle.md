---
id: ttd-hostinger-ops01a-s2-lifecycle-2026-11-23
type: offline-lifecycle-qa
status: OPS01A_S2_OFFLINE_LIFECYCLE_PASS
updated_at: 2026-11-23
sensitivity: public-redacted
---
# OPS-01A/S2 Offline Lifecycle QA

`TASK=OPS-01A/S2 | AGENT=hostinger-agent | ACK=ACKNOWLEDGED | MAIN_SHA=e385c1b | S1_PIN=ops-01a-s1-v2 / PR22 accepted synthetic baseline | NEXT_OWNER=chatgpt`

## Scope

Distinct S2 branch, new lifecycle files only. S1 history and PR #22 were not rewritten. No VPS, Docker daemon, network probe, production resource, credential, scheduler, notification, webhook, email, paging or paid API was accessed.

## State machine

For one fixed resource/rule/source:

`NORMAL -> OPEN -> RECOVERED -> OPEN`

- Three chronological qualifying `bad` samples emit `OPEN`.
- Three chronological qualifying `good` samples after `OPEN` emit `RECOVERED`.
- Three fresh qualifying bad samples after recovery can open a new incident when the declared cooldown permits it.
- `UNKNOWN`, stale, blocked, duplicate, out-of-order, wrong-resource and wrong-source samples never extend a valid streak.
- Incident dedupe, sample dedupe, notification cooldown and escalation remain distinct. No external notification is emitted.

## Exact cooldown behavior

- `899` seconds since the previous alert: `SUPPRESSED_COOLDOWN`, no second alert.
- `900` seconds since the previous alert: eligible `REOPEN`/new incident event.
- UTC observed timestamps are used. Clock reversal is rejected and audited.
- Dedupe key includes resource, rule, rule version and incident sequence.

## Tests executed

Offline sandbox result: `10/10` passed, `0` failed, duration `0.055s`.

A: bad×3 → `OPEN`, good×3 → `RECOVERED`, bad×3 after permitted interval → second `OPEN`.
B: duplicate bad streak within `899s` → suppressed.
C: bad streak at exact `900s` → eligible `REOPEN`.
D: blocked/unknown sample interrupts streak.
E: duplicate, out-of-order, wrong resource and wrong source fail closed.
F: source change cannot spoof a new resource.
G: S1 bad×3/good×3 composition remains `OPEN`/`RECOVERED`.
Additional: UTC clock reversal, synthetic snapshot/replay, and distinction between cooldown and notification metadata.

Control result: network calls `0`, external notifications `0`, live monitoring `0`, VPS/production actions `0`.

## Persistence boundary

Snapshot/replay is deterministic synthetic serialization only. No claim is made about persistence across process restarts in production. Sources, retention, alert delivery and escalation remain unapproved and belong to a separate OPS-01B gate.

## Verdict

`OPS01A_S2_OFFLINE_LIFECYCLE_PASS`.

This is an offline lifecycle contract pass only. It is not `MONITORING_LIVE`, production approval, an alert-channel approval, or Gate B approval.
