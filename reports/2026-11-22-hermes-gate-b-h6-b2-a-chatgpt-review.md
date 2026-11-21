---
id: hermes-gate-b-h6-b2-a-chatgpt-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# H6 B2-A — ChatGPT review and B2-B read-only decision

**DECISION: H6_B2_A_ACCEPTED / VERIFIED_OFFLINE_LEDGER_COMPATIBILITY (Codex evidence) / B2_B_READ_ONLY_PREFLIGHT_AUTHORIZED / REAL_LEDGER_WRITE_NOT_APPROVED / PAID_GATE_B_BLOCKED_PREFLIGHT.**

Reviewed repository commit [1caf096](https://github.com/DuyKienTTD/Hosting/commit/1caf0961898452a08abbecd027de552ed4e4ef3f), handoff [c97fca2](https://github.com/DuyKienTTD/Hosting/commit/c97fca2026d3fbab2587258d610ed5c9a3817981), and complete 2-commit diff since B2-A approval `da79cc9`. Reviewed source `one_shot.py`, `h6_writer.py`, `h6_b2a_ledger_test.py`, and unchanged original `sandbox/p0-level2/adapter.py`; B2-A report/JSON evidence, task/ADR and AGENT_WORKFLOW §§7–10. No direct rerun by ChatGPT; measurements are **VERIFIED_OFFLINE_MOCK_REPORTED_BY_CODEX**, source behavior independently reviewed.

## Findings and limits

- Real Level 2 v1 adapter code was used to construct synthetic ledger fixtures. H6/Level 2 lock a stable shared `.json.lock` inode and preserve root/day/task/permit extensions. Four simultaneous H6 admissions produce one ACK after durable pre-dispatch consume/reserve. Ledger pathname reopens after `os.replace`, avoiding stale file-bind inode reads.
- Crash before fsync and after durable commit but before ACK produces no successful ACK; reservation and consumed permit persist after post-commit crash; replay rejected; settlement `usage_recorded`/`outcome_unknown` idempotent on mock without refund. Fourteen malformed/unauthorized data/scope cases rejected; Stage A mock and changed-code regressions passed by Codex.
- Compose inputs unchanged from B1; no KVM2 operations, real ledger/permit operations, provider API calls, paid inference or production effects. These are Codex evidence, not independent live KVM2 observations.
- **Critical interface limit:** Level 2 adapter's `atomic_write()` fsyncs the file then os.replace, but does not fsync the containing directory; H6 writer does both. Shared locking and schema interop tests do **not** prove equal power-loss durability of Level 2 writes. Do not casually change Level 2 production or overwrite the real ledger to remedy this: separately review changes and only run changed, targeted tests.
- `h6_writer.py` remains **Stage A fixture-only** (path and marker enforced), `settle_mock` does not book actual paid spend, and no live shared-ledger writer or provider transport is implemented. B2-A PASS is NOT real writer integration or provider E2E.

## Next step by delegated ChatGPT coordinator (§10): B2-B read-only KVM2 preflight

**AUTHORIZED NOW:** Codex checks KVM2 live metadata using read-only OS/Docker APIs, without touching secret values or changing any filesystem state. Determine exact mount configuration (directory vs file) and identity mapping for real shared ledger and its stable lock; UID/GID, mode, DAC/ACL, user namespaces, read/write process identities and isolated shared-writer topology; inspect existing production/GATE A baselines and backup/rollback path. Do not read/buffer raw ledger content beyond minimum preexisting approved redacted metadata; no hash of credential, no new provider request. Render an **offline proposed** future writer overlay and compare complete service/network/volume/mount/port/security/entrypoint delta against current KVM2 inventory without applying it. Use source-based validation and mock fixtures to prove candidate UID/permission model; note whether both processes' ability to write can be preserved while writer has no network or credential.

**NOT AUTHORIZED:** new writer with real ledger mount, changing ownership/mode/ACL of real ledger or lock, creating a live permit, changing kill switch, Docker up/recreate of any live/Guard service, enabling provider route, provider token count/metadata/inference, paid attempts or production changes. Live read-only checks must not call Level 2 `/healthz` if endpoint reserializes ledger. Use direct read-only stat/inspect rather than open-with-write paths; keep raw private path/owner details out of public Git.

**B2-B ACCEPTANCE:** sanitized inventory matrix of existing ledger source/parent and lock inode/ownership/permissions, runtime UID/userns mapping, last known GATE A/production baseline and discrepancy list; exact rendered proposed overlay with proposed minimal write boundary and rollback, change-triggered mock test plan, explicit STOP and whether real mount is technically feasible without breaking Level 2. Classify VERIFIED_LIVE vs DOCUMENTED/UNKNOWN. If incomplete, BLOCKED_UID_OR_MOUNT and continue safe independent analysis. No declaration of Stage B2 runtime PASS from read-only checks.

**Handoff:** Codex is single technical owner; ChatGPT reviewer and delegated next-step decision maker. Handoff `PREPARED_FOR_OWNER_FORWARD` only until actually delivered and ACKed in Codex session. Parent task metadata `status: blocked`, `owner: codex`, original ADR conditional paid approval unchanged. No new task. `GATE_B_PAID: BLOCKED_PREFLIGHT`.

Reference reports: `reports/2026-11-22-hermes-gate-b-h6-b2-a.md` and `reports/evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-a.json`.
