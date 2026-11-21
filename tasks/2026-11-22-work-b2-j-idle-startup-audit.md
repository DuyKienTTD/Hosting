---
id: ttd-work-b2-j-idle-startup-001
type: task
status: prepared
approved_at: 2026-11-22
updated_at: 2026-11-22
sensitivity: public-redacted
owner: chatgpt-work
reviewer: chatgpt
depends_on: [ttd-hermes-gate-b-001]
---

# Work independent lane — H6 B2-J permitless idle-startup and recovery audit

## Executive mandate

**Work independently designs and reviews the permitless idle/health lifecycle of the P0 writer using existing source and official references.** Codex simultaneously executes the already-authorized B2-I async deadline/callback contract in a separate code surface. Work does NOT implement or modify source, task, production or live KVM2. Avoid delegating the same audit to Codex and Work.

Current Gate B `BLOCKED_PREFLIGHT`; live integration `NO_GO / BLOCKED_UID_OR_MOUNT`. This task is a **new, separate read-only Work deliverable**, not a second parent Gate B implementation task.

## Mandatory baseline and provenance

`FIRST_ACTION:` ACK latest HEAD and exact rule/task blobs; read `AGENTS.md`, entire `rules/AGENT_WORKFLOW.md` §§7–10, `rules/REPOSITORY_SECURITY.md`, `PROJECT.md`, `STATE.md`, `CATALOG.yaml`, `agents/README.md`, `agents/chatgpt.md`, original Gate B task in full, ADR-P0-003, B2-F/G/H Codex reports/evidence, ChatGPT B2-H reviewer and merged [Work B2-H audit](../reports/2026-11-22-work-b2-h-assurance.md). Read source `sandbox/p0-hermes-gate-a/{h6_provider.py,h6_writer.py,h6_p0.py,h6_ipc_auth.py,guard.py,one_shot.py,bridge.py,compose.yaml,compose.h4-provider-secret.yaml}`, Level 2 adapter startup and lock/health endpoints, plus related tests. Check newer commits/reports first. Do not rely on truncated snippets. Use official Docker/Linux/Python documentation with exact dated URLs.

`PREVIOUSLY_VERIFIED:`
| Status | Evidence | Scope |
| --- | --- | --- |
| DONE_REPORTED | H5 provider preflight and count, mock P0 one-shot | Project/credential metadata at H5 only, not paid CREATE |
| DONE_REPORTED | H6 B2-A/C/D/E/F/G PASS reports | Offline/KVM2 fake-ledger, HMAC and fake TLS only |
| DONE_REPORTED | B2-H KVM2 read-only, Codex `71fdd40` | Real DAC, mounts, live workflow metadata, rollback preview |
| DONE_VERIFIED_DOCS | Work B2-H report merged `3e9ccc8` | Independent source audit; startup requires permit |
| BLOCKED | Real writer mount/provider/paid | `BLOCKED_UID_OR_MOUNT` / `BLOCKED_PREFLIGHT` |
| NOT_RUN | Safe real-mode idle startup/restart with no permit | Target of this Work audit |

## Exact Work questions and acceptance

1. **Startup and recovery contract:** Prove from source where `require_ready` is called before writer listen and whether Guard startup/health also requires a ready permit. Design a deterministic state machine with `DISABLED`, `IDLE_NO_PERMIT`, `READY_PERMIT_VERIFIED`, `ADMISSION_COMMITTED`, `OUTCOME_UNKNOWN`, `SETTLED` and `BLOCKED`. A writer may become `healthy/idle` without admitting or dispatching; distinguish process readiness from paid job authorization. No permit may be minted, extended or consumed by health/readiness/status calls.
2. **Least-privilege health and IPC:** Define read-only authenticated status contract, fail-closed on malformed schema, missing secret, stale lock, invalid ownership/mode/mount, kill switch ON. Ensure independent root UID writer has no network/provider secret and cannot expose ledger content, permit or private paths in API/logs.
3. **Crash, restart and ledger durability:** Specify restart after zero permit, after consume/reserve before ACK, after ACK before dispatch, after provider dispatch before settlement, after unknown outcome and after successful settlement. No physical paid retry, no automatic rearm, no rollback of durable ledger, stable `.lock` inode, realistic filesystem fsync/rename assumptions. Cross-check the Level 2 adapter missing parent directory fsync, but **do not modify Level 2**.
4. **Scope and test matrix:** Specify a minimum reproducible fake-ledger test matrix (at least normal idle, 4 crash points, wrong peer/HMAC, stale/no permit, concurrent admission, health endpoint side effect check and KVM2 potential mount/UID drift), exact expected ledger bytes/attempt count and failures. Define what Codex will need to implement later and how to avoid unnecessary reruns of B2-C–G.
5. **Deployment gate proposal:** propose the smallest reversible **future** KVM2 sandbox startup check after mock source review, including rendered Compose, writer UID0/caps0, HMAC key provisioning as a secure reference only, Guard removal of stale single-file bind, precise mount boundary, backup, no-bypass and rollback without restoring ledger bytes. Clearly distinguish `SOURCE_DESIGN_READY` from `LIVE_APPLY_READY`; do not recommend apply now.

`ALLOWED:` independent GitHub code/read-only source review, official docs, analysis of sanitized existing reports and mock test architecture. When existing authorized tools actually provide read-only runtime metadata, use only necessary metadata; no secret values or real ledger contents. Research can run independently of Codex B2-I.

`WRITE_SET:` only `reports/2026-11-22-work-b2-j-idle-startup-audit.md` and optionally `reports/evidence/2026-11-22-work-b2-j-idle-startup-audit.json`, on a dedicated Work branch and PR where supported. Do not edit the parent task, Codex B2-I source, `STATE.md`, `CATALOG.yaml`, `CHANGELOG.md`, `rules/`, past reports, any code or existing Work task. ChatGPT integrates catalog/status after review.

`DO_NOT_TOUCH:` KVM2 Docker/Compose/runtime, real shared P0 ledger/lock/permit, provider/API, provider or IPC credential value/hash, n8n/Hermes production, firewall/ports/DNS, kill switch, account billing, ADR and original parent task approvals. Do not request access to secrets just to finish a document.

`TEST_DELTA:` Work does not rerun integration or paid tests. Independently reason about changed startup/health behavior and provide test vectors to Codex. If Work can safely use a separate synthetic local fixture, label any result `VERIFIED_MOCK` and keep it out of Codex's code directory; no generic code changes.

`INVARIANTS:` no provider operations, real permit or ledger mutation, production mutation, paid inference or real credential exposure. Stage B2 live `NO_GO`, paid `BLOCKED_PREFLIGHT`.

`STOP:` any need for unavailable protected runtime/account data, secret value, real ledger access or service mutation: mark only that check `BLOCKED_ACCESS`, complete all independent analysis and list next owner. Do not claim `LIVE_PASS` based on static code.

`PASS:` one actionable, independently sourced and version-pinned startup state machine, read-only status/health semantics, exact failure/recovery table, synthetic test vectors and minimum future deployment/rollback gate, with line references and remaining uncertainties classified. Output a concise `GO/NO-GO` to ChatGPT with no production claims. Push PR, verify remote file/blob/diff. Codex B2-I continues separately.

`HANDOFF:` from `chatgpt-work` to `chatgpt`, initial `PREPARED_FOR_OWNER_FORWARD` only. Work ACK must cite actual current rule/task SHA and access. ChatGPT will compare Work's recommendations to Codex B2-I results and decide the next **non-overlapping** Codex implementation step under delegated §10.
