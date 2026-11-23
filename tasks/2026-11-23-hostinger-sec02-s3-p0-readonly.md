---
task: SEC-02/S3-P0-R1
owner: Hostinger Agent
next_owner: ChatGPT Điều phối
mode: fresh-readonly-diagnostic
status: completed-pending-handoff
branch: hostinger/sec02-s3-p0-r1-readonly-2026-11-23
---
# SEC-02/S3-P0-R1 — Fresh P0 Read-only Diagnostic

## Scope

Target only the P0 reasoner on KVM2 VPS `1722328` and its compose project identity. Do not inspect the separate managed-app resource, do not touch OPS-01A/S2-D1 PR #24, and do not use unrestricted Docker details or logs.

## Allowed work

- Hostinger control-plane VPS identity/status/resource checks.
- Safe Docker project/container inventory sufficient to identify current P0 state.
- Safe host read-only checks: uptime, memory, disk, Docker process listing, SSH reachability.
- Lightweight backup/snapshot metadata only to describe rollback readiness.
- Redacted evidence with `VERIFIED_LIVE`, `HISTORICAL` and `UNKNOWN` labels.

## Prohibited work

No restart, recreate, redeploy, pull, restore, migration, firewall change, credential read/rotation, secret retrieval, unrestricted logs/inspect, inference request, paid API, production write or monitoring activation.

## Acceptance

Answer current P0 state, causal certainty, evidence for/against OOM or exit-137, owner/resource identity, rollback/backup status, and the exact safe gate for any future action. Stop and redact if an endpoint exposes plaintext credentials.
