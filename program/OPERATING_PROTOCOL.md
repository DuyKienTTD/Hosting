# Roadmap-level autonomous execution and acceptance

Status: proposed replacement/supplement, not effective until approved. Date 2026-11-23.
This policy may streamline management gates, **not** suppress controls mandated by effective `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, task-specific ADRs or real service rules.

## 1. One roadmap, one execution owner, bounded autonomy
Coordinator gives each Agent an ordered roadmap with explicit skill IDs, approved READ_SET, WRITE_SET, DEPS, STOP, acceptance, evidence expectations and external side-effect boundaries. Agent works through ready items without per-item review or manager approval. It may reorder independent items for performance. No 'ask permission' loop for safe docs, analysis, read-only APIs, local test fixtures and approved branch changes.

Agent owns **self-progress recording**: edit only its own `program/roadmaps/<agent>.md` item status/evidence plus expressly owned code/artifacts. GitHub commit/PR must be read back; events are factual. If edit blocked, report `UPDATE_UNAVAILABLE` and preserve artifact evidence rather than claiming updated.

## 2. Item state machine
`PLANNED` → `IN_PROGRESS` → `DONE_WITH_EVIDENCE`
Exceptions: `BLOCKED_SECURITY`, `BLOCKED_TECHNICAL`, `NOT_APPLICABLE`, `SUPERSEDED` (never delete historical evidence).
Every item row has immutable `ID`, objective, skill IDs, dependencies, `actual_state`, `evidence_uri`, `checked_at_utc`, optional `blocker_reason`. Do not pre-fill DONE for merely assigned items.
`DONE_WITH_EVIDENCE` means objective tested in the stated environment, not deployment/QA/production accepted.

## 3. Roadmap terminal states and acceptance
All independently actionable items done → `READY_FOR_ROADMAP_ACCEPTANCE`. If some remain blocked and every other item is done → `ROADMAP_PARTIAL_BLOCKED`. Agent submits one consolidated handoff with list of done/blocked, evidence and requested decision. Coordinator performs **roadmap-level** integrated acceptance; A0 reviews roadmap or material risk exceptions, not item-by-item. A roadmap cannot claim full PASS when material items remain blocked.
Separate QA is required for safety/security-sensitive, release/production, irreversible, or material cross-cutting changes. Perform it as a **batched roadmap acceptance** or change-triggered targeted test, not a procedural QA on every minor edit. Safe automated validators may support but do not replace independent assurance when required.

## 4. Exception language and stop
When no remaining independent authorized work exists and any item is blocked, agent must say **exactly**:
> Đã làm hết công việc có thể làm, một số công việc chưa thể làm do "Bảo mật"/ "Giới hạn kỹ thuật".
Then identify which kind per blocked item, `observed` (actual error/gate), `attempted`, `impact`, `next_safe_action`, `next_owner`, evidence. Never use a fabricated error to close a task. When a task can't be done because scope/cost isn't explicitly authorized, STOP only that side effect and continue safe work.

## 5. Direct permission policy
A0 stated A1/A2/Work/Hostinger have full permitted access to connected accounts and skills; omit redundant generic surveys. This does **not** imply every provider API/skill is installed, nor that vendor confirmation, consent, quotas, secret isolation, cost ceilings, staging/preflight and rollback magically exist. Detect **specific actual blockers at point of use**, not at generic pre-assignment. Production writes/paid inference/Ads budgets/publishing/irreversible change and Gate B must satisfy task-specific restrictions until A0 explicitly replaces them.

## 6. Concurrency and source drift
One accountable owner per task/output; distinct non-overlapping write-sets; don't update a shared summary/status field at every task change. Prefer own agent roadmap branch + shared register integration by coordinator at roadmap review. Re-fetch latest SHA before write; if shared file has drift, pause only conflicting write and continue independent work. Merge conflicts are not justification for force push.
No claimed cross-session handoff without exact session ACK; GitHub links are durable delivery preparation, not a runtime bus. Agent may self-update **while its session executes**; no inference of background persistence.

## 7. Metrics and cadence
Capture `READY_at`, `ACK_at`, `evidence_at`, `roadmap_review_at`, `usable_at`, `rework_count`, `provider_spend_verified`. Missing = UNKNOWN. Coordinator issues status dashboard at roadmap gate and on real blockers; avoid repeated reports. Never compute an exact percent complete from PR count or planned item count alone.

## 8. Review and adoption conditions
Current proposal is draft source on a separate branch. Before adopting, reconcile PR31 governance QA, pin all current sources, run deterministic schema/link tests and at least one sample Agent roadmap simulation + one security-sensitive blocked case. Do not merge automatically.
