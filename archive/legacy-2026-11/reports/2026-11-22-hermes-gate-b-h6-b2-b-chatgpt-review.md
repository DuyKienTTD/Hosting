---
id: hermes-gate-b-h6-b2-b-chatgpt-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# H6 B2-B reviewer — choose UID strategy and next safe scope

**REVIEW: H6_B2_B_READ_ONLY_PREFLIGHT_ACCEPTED / BLOCKED_UID_OR_MOUNT_FOR_APPLY.**
**NEXT DECISION under delegated workflow §10: H6_B2_C_UID_MODEL_OFFLINE_AUTHORIZED / REAL_LEDGER_APPLY_NOT_AUTHORIZED / PAID_GATE_B_BLOCKED_PREFLIGHT.**

## Provenance and acceptance

Reviewed exact [B2-B handoff commit 6a6e691](https://github.com/DuyKienTTD/Hosting/commit/6a6e691fb4d50af935b1fb9104affc9dca8ca0e0), all its relevant file patches, report `reports/2026-11-22-hermes-gate-b-h6-b2-b-preflight.md`, JSON evidence, task/ADR/rules, H6 Guard/writer and Level 2 adapter source. The commit adds redacted report/evidence, state and catalog index, not runtime code. Measurements are **VERIFIED_LIVE_REPORTED_BY_CODEX**, not independently re-probed KVM2 by ChatGPT.

Measured filesystem: real ledger file and stable lock both root:root 0600, parent root:root 0700, no POSIX ACL, rootful Docker without userns remap; Guard runs UID 0 with read-only **single-file** ledger bind and cannot see sibling lock; Level 2 directory bind is writable with configured root UID, service currently exited but restart policy unless-stopped. Guard provider/key and capture permissions root-only. UID 23062 writer is denied traversal/ledger read/lock open/create by DAC; local synthetic test supports that. H4 backup Compose byte matches and rendered preview minimal; pre/post KVM2 metadata equal, no real content reads/provider/runtime mutations/cost.

**B2-B preflight scope PASS; live sandbox application FAILS gate BLOCKED_UID_OR_MOUNT.** Preview writer with user 23062, network none, image entrypoint /bin/false is not a deployable writer. Do not promote its render PASS to working IPC or real ledger safety.

## Architecture decision and alternatives

**Preferred candidate for controlled OFFLINE comparison: root-owned (UID 0) writer with no effective/permitted/inheritable/ambient capabilities, network_mode none, read-only rootfs, no-new-privileges, provider secret absent, and an allowlisted **single** writable ledger directory bind plus private IPC directory.** Preserve real host ledger/lock root:root 0600 and parent 0700 and current Level 2 compatibility; no chmod/chown/ACL on real paths. Having UID 0 for this broker is NOT equivalent to proving its process/container isolation: root on rootful Docker host binds remains a sensitive authority boundary; a code/entrypoint compromise might mutate files within that directory. Validate effective caps=0, mount propagation, prohibited mounts, immutable rootfs, no ports and no network on a fake mirror before any proposal to deploy.

**Competing option:** dedicated non-root UID 23062 with tightly scoped ownership/ACL migration. Requires explicit coordination with Level 2 writer's 0600 mode, os.replace ownership and directory fsync, rollback, stable lock and default ACL inheritance; changing only group permissions or adding a broad ACL is insufficient and unapproved. A single root-compatible writer is favored for minimal impact to pre-existing filesystem metadata, subject to successful tests.

**IPC identity gap:** existing Guard is UID 0; existing Stage A code assumes Guard UID 23061/writer UID 23062. Switching both peer identities to 0 without additional authentication would weaken the peer boundary. Stage B2-C must test least-privilege route: socket only bind-mounted into authorized Guard, exclusive parent directories/mode, SO_PEERCRED with actual UID/GID and protocol-scoped HMAC or equivalent peer proof using synthetic secret isolated from writer/provider key; record threat model for a compromised Guard. Do not alter the real Guard credential ownership/capture or run any actual secret in fixture tests.

**Level 2 concurrency:** stopped is not disabled. Future writer and Level 2 (configured UID 0) must share stable lock inode across os.replace even if Level 2 restarts; Level 2's atomic_write currently fsyncs file but not containing directory. Fixing Level 2 production is out of scope. Test effect of simulated Level 2 re-entry on fake ledger and log durability limitation. Real ledger rollback must never replace original bytes after any committed permit, reserve or unknown outcome.

Official documentation checked: https://docs.docker.com/engine/storage/bind-mounts/ ; https://docs.docker.com/engine/containers/run/ ; https://docs.docker.com/engine/security/userns-remap

## Codex H6 B2-C bounded handoff

- `owner: codex`; `reviewer: chatgpt`; `from_agent: chatgpt`; `to_agent: codex`; `handoff_state: PREPARED_FOR_OWNER_FORWARD`; no automatic Codex delivery inferred.
- `FIRST_ACTION:` ACK latest rules §§7–10, task/ADR and this review, inspect full current H6 writer/Guard/one_shot/Level 2 adapter, B2-A/B2-B evidence, KVM2 inventory. Enumerate exact source/Compose diff and safety assumptions before code changes.
- `ALLOWED:` change sandbox-only source and offline Compose proposals, run isolated Docker fake-ledger DAC/IPC/lock tests with synthetic credentials and no host real-ledger bind. Read-only KVM2 metadata checks only if a concrete new change trigger exists. Compare root-with-zero-caps candidate against strictly scoped UID migration candidate; no production/actual service start, no real secret.
- `REQUIRED TEST DELTA:` fake root-owned 0700 directory, mock ledger/lock 0600, synthetic Level 2 writer with UID 0; fake Guard socket client with actual UID 0; wrong peer and unmounted socket failure; network/no provider key, mount boundary and cap=0 effective checks; lock inode, concurrency, replace, replay, crash/no-ACK; rollback mock fixture, not live ledger; unchanged Stage A/B1 tests reused when no relevant code change. Assess HMAC/peer binding and ensure it does not allow fake Guard to request generic ledger mutation.
- `WRITE_SET:` minimum `sandbox/p0-hermes-gate-a/` sources/tests/offline overlay and redacted `reports/` + `reports/evidence/`; append original task and status/index minimally after evidence. No new parent task.
- `DO_NOT_TOUCH:` actual KVM2 ledger+lock/owner/mode/ACL, live Guard/Level 2 container/Compose/runtime, real provider key, provider API, permit/kill switch, production n8n/Hermes, ports/network/firewall/DNS, ADR, budget and parent metadata.
- `ACCEPTANCE:` concrete tested root-candidate/UID strategy with source diff, fake-data matrix, effective capabilities/mount/network validation, Peer identity mitigation, Level 2 simultaneous writing and rollback, explicit risk and a separate reviewable minimal LIVE application plan. Failure => `BLOCKED_UID_MODEL` and safe alternate; only successful evidence merits future scoped apply decision.
- `STOP:` any need to chmod/chown/ACL real file, start production/Guard, mount real ledger, read credential, call provider, or uncertain DAC/lock. 0 provider operations/paid/cost. Gate B remains BLOCKED_PREFLIGHT.

This report constitutes **review and choice of offline next step only**, no H6 runtime/paid approval, no Codex ACK.
