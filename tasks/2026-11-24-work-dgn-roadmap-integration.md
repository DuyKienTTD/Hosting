---
id: hosting-work-roadmap-integration-2026-11-24
type: task
status: review-ready
dispatch_eligible: false
owner: Work
sensitivity: public
---
# Work — Integrate assigned DGN-3/DGN-4 rows into own roadmap

**TASK_ID:** `WORK-DGN-ROADMAP-INTEGRATION`  
**OWNER:** Work only for `program/roadmaps/work.md`  
**MODE:** DESIGN_ONLY / ROADMAP_MAINTENANCE / NO_PRODUCT_BUILD  
**HANDOFF_STATE:** `PREPARED_FOR_OWNER_FORWARD` — no direct cross-session send or ACK is claimed.

## Required bootstrap
Before acting, read in full current `main`: `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, your Work role profile if available, and this task. Record source SHAs. Read the pinned WBS and Assignment Matrix.

## Inputs
- WBS: `program/WORK_BREAKDOWN.md`, branch `coordinator/dgn3-dgn4-row-level-2026-11-24`, blob `11261e92d520e720d4798087d89f8269f8c19b20`.
- Assignment: `program/ASSIGNMENT_MATRIX.md`, same branch, blob `248947cd9d05bcfcd39e6e3ba12f298da57a1f3a`.
- Coordinator status: `program/roadmaps/coordinator.md`, blob `469c215d0147a9daee6e6335cad607520be98954`.
- Completed feasibility: commit `4309773bfc20a43970a6b773f352999ef09b77cf`.

## Outcome
Update **only your own** `program/roadmaps/work.md` to integrate the future Work-owned/proposed rows and preserve the completed feasibility evidence and known blockers.

## Your WBS mapping
- `G1-04,EXIST-QA31`: historical completed QA/lineage; preserve evidence and do not repeat.
- `UI-01,UI-02`: proposed future UI prototype/integration owners; HOLD until separate A0 product-build release and Work task ACK. No build in this task.
- `CTRL-01`: proposed research/test owner only; BLOCKED_CHANNEL_UNKNOWN until a supported channel, session identity/consent, receipt authenticity and separate test authorization are proven. Manual owner-forward remains fallback, not an automated capability.
- `UC01-02,GROW-03`: proposed future pipeline/reporting owners; HOLD pending authorized read-only source, UI/backend build permission and task ACK.
- `G3-A1`: proposed independent QA owner for A1 DGN-2 evidence. Work must remain reviewer, not co-author. Do not perform the QA in this roadmap-integration task; await a separately scoped task if needed.
- Work is not owner of A2's Product Charter, A1 Registry, Coordinator WBS/Assignment or Hostinger infrastructure.

## Required roadmap fields
For every Work-owned/proposed row show WBS ID, outcome/deliverable, FIRST_ACTION, skills and actual tools, dependencies, READ_SET, WRITE_SET, branch, permissions, environment/data class, cost, STOP/rollback, acceptance/evidence, status/provenance and next owner. Correct tool evidence precisely: Playwright Python/Node modules were observed available in Work Linux environment on 2026-11-23 18:07 UTC; axe-core remains UNKNOWN_NOT_VERIFIED; no browser accessibility/screen-reader test was executed.

## WRITE_SET / restrictions
- Sole WRITE_SET: `program/roadmaps/work.md` on a Work-owned branch.
- Do not edit WBS, Assignment Matrix, Product Charter, Skill Registry, other Agent roadmaps, rules, STATE, CATALOG, main, production or external accounts.
- No UI build, deployment, live RBAC test, cross-session control, paid API or merge.

## Acceptance
Work can read its roadmap alone and determine which items are historical, proposed, HOLD or channel-blocked; the exact first safe action after authorization; current Playwright/axe evidence; required skills/tools; evidence path; reviewer separation; and STOP. Remote readback must match; do not invent ACK or completion.

## Handoff
After actual receipt, reply in the Work session with `TASK_ACKNOWLEDGED — WORK-DGN-ROADMAP-INTEGRATION`, source SHAs and FIRST_ACTION. Then update only your roadmap. Final status: `READY_FOR_ROADMAP_ACCEPTANCE` or `ROADMAP_PARTIAL_BLOCKED`. `NEXT_OWNER`: Coordinator for integrated package.
