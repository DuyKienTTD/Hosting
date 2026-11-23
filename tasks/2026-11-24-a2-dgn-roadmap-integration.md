---
id: hosting-a2-roadmap-integration-2026-11-24
type: task
status: review-ready
dispatch_eligible: false
owner: A2
sensitivity: public
---
# A2 — Integrate assigned DGN-3/DGN-4 rows into own roadmap

**TASK_ID:** `A2-DGN-ROADMAP-INTEGRATION`  
**OWNER:** A2 only for `program/roadmaps/a2.md`  
**MODE:** DESIGN_ONLY / ROADMAP_MAINTENANCE / NO_EXECUTION_ACTIVATION  
**HANDOFF_STATE:** `PREPARED_FOR_OWNER_FORWARD` — no direct cross-session send or ACK is claimed.

## Required bootstrap
Before acting, read in full current `main`: `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/a2.md` if present (if absent, record NOT_FOUND; do not invent it), and this task. Record current main HEAD and source SHAs. Read the pinned Coordinator WBS and Assignment Matrix below.

## Inputs
- WBS: `program/WORK_BREAKDOWN.md`, branch `coordinator/dgn3-dgn4-row-level-2026-11-24`, blob `11261e92d520e720d4798087d89f8269f8c19b20`.
- Assignment: `program/ASSIGNMENT_MATRIX.md`, same branch, blob `248947cd9d05bcfcd39e6e3ba12f298da57a1f3a`.
- Coordinator status: `program/roadmaps/coordinator.md`, blob `469c215d0147a9daee6e6335cad607520be98954`.
- Completed DGN-1: PR #44 / head `bf232a313c0dd696c4ae824c35e7d1ddfda1a613`.

## Outcome
Update **only your own** `program/roadmaps/a2.md` to integrate row-level assignments and show clear distinction between completed DGN-1 design and future HOLD work.

## Your WBS mapping
- `G0-01,G0-02`: DGN-1 design complete with author evidence; do not rewrite or repeat.
- `UC01-01`: A2 proposed owner for future read-only WordPress audit; HOLD until task-specific ACK and verified read-only WP scope or approved sanitized export.
- `GROW-01`: A2 proposed owner for future read-only Ads/GA4 attribution; HOLD until task-specific ACK, consent and verified read-only scopes.
- `GROW-02`: A2 proposed owner for future media/social workflow; design scope only, HOLD on rendering/publishing until rights, consent, cost cap and approval.
- Other rows belong to Coordinator, A1, Work, Hostinger or A0 and must not be imported as A2-owned tasks.

## Required roadmap fields
For every A2-owned row show WBS ID, outcome/deliverable, FIRST_ACTION, required Skill IDs/tools, dependencies, READ_SET, WRITE_SET, branch, permissions, environment/data class, cost, STOP/rollback, acceptance/evidence, status/provenance and next owner. A2 is sole writer of Product/UI; this task does not authorize editing it.

## WRITE_SET / restrictions
- Sole WRITE_SET: `program/roadmaps/a2.md` on an A2-owned branch.
- Do not edit Product Charter, WBS, Assignment Matrix, Registry, other Agent roadmaps, rules, STATE, CATALOG, main, WordPress, Ads or media accounts.
- No live WP/Ads read until the required scope/consent is verified and task-specific work order is issued. No writes, spend, render, publish or merge.

## Acceptance
A2 can independently see completed DGN-1 evidence, its exact proposed future WBS, what is HOLD, first action after authorization, tools/scopes required, evidence destination and STOP. Remote readback must match; do not change status to SENT/ACK/IN_PROGRESS without actual receipt.

## Handoff
After actual receipt, reply in this A2 session with `TASK_ACKNOWLEDGED — A2-DGN-ROADMAP-INTEGRATION`, source SHAs and FIRST_ACTION. Then update only your roadmap. Final status: `READY_FOR_ROADMAP_ACCEPTANCE` or `ROADMAP_PARTIAL_BLOCKED`. `NEXT_OWNER`: Coordinator for integrated package.
