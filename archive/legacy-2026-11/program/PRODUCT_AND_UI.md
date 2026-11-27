# Product Charter, outcomes and operator UI

Status: DRAFT / not implemented | Date: 2026-11-23
Source reconciliation: `PROJECT.md`, `GOALS_AND_ROADMAP.md`, PR31 progress report and A0 operating directives. This is a target, not a report of live capability.

## Final outcome
A **TTD METAL AI Business Automation Platform** that turns authorized business goals into measurable workflows across WordPress/WooCommerce/SEO, marketing attribution/Ads, media/social and reporting, with a user-facing Operator Console, auditable multi-agent delegation, bounded spend and recoverability. Preserve existing ChatGPT Standard (A1/A2), Work, Hostinger and other existing chats; do not replace them with API-only clones.

The **Session/Agent Controller** is a supporting subsystem; success of business automation must not depend on full controller automation being finished.

## Personas and permissions
- **Owner/A0:** business goals, milestones, portfolio outcomes, exception/side-effect approvals, cost ceilings, emergency STOP.
- **Coordinator:** prioritized roadmap, blocked dependencies, acceptance dashboard, evidence provenance, assigns execution.
- **Executor agent:** receives scoped work, tools, evidence, updates item state, raises precise exceptions.
- **Sales/content/marketing operator (future):** sees tasks and outputs specific to role; approval and final publishing limited by roles.

## Operator Console: minimum viable UI
1. **Overview:** current business outcomes, usable workflows vs design/mock, service health, owner/last update, decisions required.
2. **Roadmaps:** one panel per agent, tasks/status/skills/priority/dependencies, progress based on accepted deliverables not percentages from PR counts; direct deep-links to evidence.
3. **Agent Sessions:** named existing sessions, last observed ACK, active task, dispatch receipt, missing/unknown states, no false 24/7 indicator.
4. **Work Queue / Dependencies:** ready/blocked states, work item detail, acceptance and rollback requirements; one accountable owner.
5. **Business Modules:** WordPress SEO content audit; Ads/GA4 attribution and leads; media/social pipeline; multi-channel KPI reports.
6. **Approvals & Risk:** grouped pending approvals only for sensitive/paid/production/publish actions, named scope/cost/rollback; no per-item managerial approvals.
7. **Audit & Cost:** event timeline with source timestamp and SHA, provider invoice-derived spending where available; source freshness, errors and retry history.
8. **Settings/Integrations:** connector status and granted scopes as observed (never expose tokens), worker capabilities, kill switch, retention.

### Key flows
`goal → milestone → assigned agent roadmap → execution → self-evidence → independent risk-based verification → roadmap-level acceptance → next milestone`.
`blocked item → safe independent items continue → precise reason/evidence → partial roadmap acceptance/exception decision`.
`operator clicks task → source/pinned inputs + evidence + current execution status`.

### UI acceptance
Keyboard and responsive navigation; meaningful empty/error/loading states; labels in Vietnamese by default; no secrets/PII; visible distinction MOCK/OFFLINE/STAGING/LIVE; read-only demo first, then authenticated real-data operator workflow; error/unknown/duplicate-receipt states; owner can view approvals without digging through GitHub comments. Visual prototype alone ≠ integrated app.

## Product milestone gates
- **M0 — governance substrate:** concise knowledge entry; 4 role/skills maps; backlog; distinct agent roadmaps; measured context/QA regression; no data loss.
- **M1 — business read-only MVP:** reproducible WP/Woo content and SEO audit sourced from real read-only account, material UNKNOWN/failure handling, actionable output and QA; UI surfaces output.
- **M2 — operator console MVP:** usable UI connected to durable task state, read-only evidence/roadmap/dashboard, real login/roles (if deployed), health/error handling, recoverable operations.
- **M3 — orchestration:** repeatable n8n/worker task lifecycle, authenticated callbacks, idempotency and bounded retry with no false receipt assertions; connected agents only where proven.
- **M4 — business expansion:** attribution/Ads read-only baseline; marketing media/social approval pipeline; measured costs and business utility.
- **M5 — secured operation:** verified backup/restore, alerting, access boundaries, secrets, exception playbook, recovery exercises, real SLA evidence.

## Definition of product success
One authorized operator can identify the active goal, assigned agent, evidence, next action and blocker via UI; run at least one repeatable, verified business workflow end-to-end; no claim of unattended operation until scheduler/monitoring/recovery are live-validated. Track lead time, completion quality, cost per accepted output, uptime/incidents and business impact; no invented baseline or percentage.
