---
id: hosting-a1-roadmap-integration-2026-11-24
type: task
status: review-ready
dispatch_eligible: false
owner: A1
sensitivity: public
---
# A1 — Integrate assigned DGN-3/DGN-4 rows into own roadmap

**TASK_ID:** `A1-DGN-ROADMAP-INTEGRATION`  
**OWNER:** A1 only for `program/roadmaps/a1.md`  
**MODE:** DESIGN_ONLY / ROADMAP_MAINTENANCE / NO_EXECUTION_ACTIVATION  
**HANDOFF_STATE:** `PREPARED_FOR_OWNER_FORWARD` — no direct cross-session send or ACK is claimed.

## Required bootstrap
Before acting, read in full the current `main` versions of `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/a1.md`, and this task. Record actual main HEAD and source SHAs in your own roadmap. Read the exact Coordinator candidate sources below.

## Inputs
- WBS: `program/WORK_BREAKDOWN.md` on `coordinator/dgn3-dgn4-row-level-2026-11-24`, blob `11261e92d520e720d4798087d89f8269f8c19b20`.
- Assignment: `program/ASSIGNMENT_MATRIX.md` on the same branch, blob `248947cd9d05bcfcd39e6e3ba12f298da57a1f3a`.
- Coordinator current status and R1–R7 reconciliation: `program/roadmaps/coordinator.md`, blob `469c215d0147a9daee6e6335cad607520be98954`.
- Your completed DGN-2 remains at PR #46 / head `070189b381dd3e17680c85fdff01e84978c0bf93`.

## Outcome
Update **only your own** `program/roadmaps/a1.md` so it incorporates the row-level DGN-3/DGN-4 routing, distinguishes historical completion from future proposed work, and gives A1 a self-contained roadmap view.

## Your WBS mapping
- `G1-01,G1-02,G1-03,G3-01`: historical completed evidence; preserve as history, do not rerun.
- `G2-02`: proposed A1 schema/event-contract design owner. Current status is design-spec-required; implementation remains HOLD. FIRST_ACTION if/when this design task is activated: inspect G2-01/G2-03 contract and Work's feasibility report, then specify schema only (no DB/backend changes).
- `QA-U01`: proposed only after UC01-01 produces an authorized read-only audit; remain HOLD.
- `G3-A1`: Work is proposed independent QA owner; A1 is source author/respondent, not reviewer.
- All other rows assigned to A2/Work/Coordinator/Hostinger/A0 remain outside A1's ownership.

## Required roadmap fields
For every A1-owned or historically relevant row, show WBS ID, outcome/deliverable, priority, FIRST_ACTION/NEXT_ACTION, required Skill IDs and minimum tools, dependencies, READ_SET, WRITE_SET, branch, permissions, environment/data class, cost, STOP/rollback, acceptance/evidence, status/provenance and next owner. Use exact fallback type; a consultant/reviewer is not an execution fallback. Preserve HOLD and historical state.

## WRITE_SET / restrictions
- Sole WRITE_SET: `program/roadmaps/a1.md` on an A1-owned branch.
- Do not edit WBS, Assignment Matrix, Registry, any other Agent roadmap, rules, STATE, CATALOG, main, production, provider accounts or runtime.
- No install, paid API, Codex, deployment, live data mutation or merge.

## Acceptance
A1 can read its roadmap alone and determine exactly which rows are historical, proposed, HOLD, what it owns, the first action for any authorized future work, what skills/tools are needed, where to write evidence and when to STOP. Remote readback must match; no status may be promoted without actual task ACK/authority.

## Handoff
After actual receipt, reply in this A1 session with `TASK_ACKNOWLEDGED — A1-DGN-ROADMAP-INTEGRATION`, exact source SHAs and FIRST_ACTION. Then update only your roadmap. Final status: `READY_FOR_ROADMAP_ACCEPTANCE` or `ROADMAP_PARTIAL_BLOCKED` with precise evidence. `NEXT_OWNER`: Coordinator for integrated package.
