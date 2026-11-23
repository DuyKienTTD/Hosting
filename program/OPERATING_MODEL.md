---
id: hosting-dgn2-operating-model-candidate-2026-11-24
type: knowledge
status: candidate-not-effective
updated_at: 2026-11-24
sensitivity: public
---
# HOSTING — Operating Model & Agent Capability Governance

**DGN-2 integrated operating model — Coordinator design candidate.**  
**Status:** `COORDINATOR_DRAFT_ONLY / NOT_EFFECTIVE_RULE / PACKAGE_ACCEPTANCE_PENDING`.  
**Purpose:** define how outcomes become WBS work, how skills and authority are matched, how a real session receives and executes work, and how evidence is accepted without per-item micro-management.

## 1. Authority precedence

Apply these layers in order; lower layers cannot override higher ones.

1. **Effective repository/security policy and platform terms:** current `main` `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, and applicable provider rules define hard boundaries. A branch, PR, profile, registry preface or historical decision does not amend them.
2. **Explicit A0 owner decision:** A0 retains reserved decisions including merge/release, production, deployment, publication, permission uplift, and paid spend. Record exact scope, target/source SHA, actor, timestamp, expiry, cost ceiling and rollback. Strategic delegation to Coordinator permits safe next-step selection inside existing authority; it does not create credentials or remove STOP.
3. **Coordinator work order:** one accountable owner, outcome, WBS ID, READ_SET/WRITE_SET, environment, first action, acceptance, evidence destination, cost/STOP and fallback. A task narrows authority; it cannot enlarge policy or A0 authority.
4. **Recipient session receipt:** SENT requires actual transport evidence. ACKNOWLEDGED requires the named recipient's own session confirmation for that exact task/scope. A role ACK, Git commit, PR, issue comment or another Agent's report is not a task ACK.
5. **Capability and skill evidence:** ability and authorization are separate axes. Both are necessary. Own-session current evidence outranks historical survey; REPORTED, DOCUMENTED, CONNECTED_VISIBLE_UNTESTED and INSTALLABLE do not become VERIFIED or INSTALLED by inference.
6. **Execution evidence and acceptance:** author self-QA is not independent QA. A0 Assistant is independent reviewer, not A0 decision authority. No document/status self-activates work.

**Conflict rule:** preserve older snapshots as history, but explicitly label superseded routing. Current main policy controls until a separately approved, authorized rule change is integrated and read back from main.

## 2. Outcome-to-work operating chain

`Business/Product Outcome → Product feature/UI contract → WBS row → Required Skill IDs → capability evidence → permission/cost check → one proposed owner → scoped work order → actual session SENT/ACK → self-directed execution → evidence → roadmap-level acceptance → A0 reserved decision (if required)`

- Product Charter defines why and what; WBS defines each independently deliverable unit; Skill Registry defines the canonical skill vocabulary and evidence boundaries; Assignment Matrix maps each WBS to one owner candidate and any genuine fallback; each Agent roadmap is the recipient's execution view.
- GitHub is the durable source/evidence store, not a live session dispatcher or presence detector.
- n8n is a workflow engine/runtime, not an Agent or authority issuer.
- A prepared task is not dispatched. A proposed owner is not an assignment. A skill match is not permission. A mock result is not a live result.

## 3. Canonical capability and authorization model

For each proposed assignment, record:
- `WBS_ID`, `PRIMARY_OWNER` (exactly one), eligible `AGENT_CANDIDATES`, non-owning `CONTRIBUTORS`.
- exact `REQUIRED_SKILL_IDS` from the canonical K-ID dictionary and minimum tool capability;
- capability state and proof: `VERIFIED_THIS_SESSION`, `EVIDENCED_HISTORICAL`, `REPORTED_BY_AGENT`, `DOCUMENTED`, `CONNECTED_VISIBLE_UNTESTED`, `INSTALLABLE_CANDIDATE`, `UNKNOWN`;
- execution authorization separately: task scope, READ_SET, WRITE_SET, branch, environment, data class, expiry, account scope, cost ceiling and approval ID;
- fallback type and activation condition. A consultant or reviewer is not an execution fallback.

### Agent directory — role and evidence boundary

| Agent | Primary responsibility in this design | Evidence boundary and routing rule |
|---|---|---|
| Chat Điều phối | Accountable delivery director; integrated WBS, Operating Model, Assignment Matrix, dependencies, source reconciliation and roadmap-level delivery | Current GitHub authoring capability is evidenced in this session; never self-certifies independent package review or A0 reserved approval |
| Trợ lý A0 độc lập | Independent strategy, governance and package reviewer | Role profile exists on candidate PR47 branch only; profile/session must be read and capability verified; not an executor or A0 proxy |
| A1 | Capability/skills inventory, source engineering, schema and bounded technical design | PR46 proves authored DGN-2 source; cannot self-verify another Agent's live tools or independently QA its own registry |
| A2 | Product Charter, Operator UI, business requirements, WP/SEO, attribution and media workflow design | PR44/PR48 prove authored design and roadmap; actual WP/Ads/GA4/media access remains task-specific UNKNOWN |
| Work | UI feasibility, integration, browser/Linux testing and independent QA when not author | DGN feasibility and Work roadmap are evidence; Playwright Python/Node were observed in Work Linux at 2026-11-23 18:07 UTC; axe-core and live cross-session control remain UNKNOWN |
| Hostinger Agent | Hosting/hPanel/VPS/DNS/TLS/backup/recovery and infrastructure operations | Historical specialist evidence only; PAUSED for new/unfinished tasks until A0 resumes and Hostinger acknowledges a new scoped task |
| Hermes | Reasoning/tool/runtime and n8n integration analysis | Historical survey only; new tasks remain cost-gated; distinguish WebUI from production/KVM2 runtime |
| Codex | Exception-only complex code/integration/test work | NOT_AUTHORIZED absent a task-specific A0 exception with alternatives, max scope/cost, STOP and independent reviewer |

**Non-Agent:** n8n is orchestration/runtime, not a ninth Agent.

## 4. Work-order contract and recipient handoff

Every new work order must make the recipient independently actionable:
- why/outcome and exact WBS ID;
- deliverable, acceptance, evidence path and FIRST_ACTION;
- required skills, minimum tools and source pins;
- one owner, candidate/fallback and why the recipient is best fit;
- dependencies and parallel lanes;
- READ_SET, WRITE_SET, DO_NOT_TOUCH, branch and baseline;
- environment, data class, permissions and proof required;
- cost model/ceiling or explicit UNKNOWN, STOP and rollback;
- next owner or decision.

Handoff lifecycle:
- `PREPARED`: work order committed; not sent.
- `SENT`: actual delivery through a verified channel with destination/attempt evidence.
- `ACKNOWLEDGED`: recipient confirms exact task in its own session.
- `IN_PROGRESS`: recipient begins within scope.
- `DONE_WITH_EVIDENCE`: deliverable and evidence are committed/read back.
- `READY_FOR_ROADMAP_ACCEPTANCE`: entire assigned roadmap reaches its acceptance criteria.
- `ROADMAP_PARTIAL_BLOCKED`: safe alternatives were tried and a specific residual blocker remains.

If no verified inter-session channel exists, use `PREPARED_FOR_OWNER_FORWARD`; owner forwards once to the exact session. Never claim automation or fabricate SENT/ACK. Manual owner-forward is a valid current fallback for delivery, not proof of an automated controller.

## 5. Self-progress and acceptance model

Each Agent is sole writer of its own roadmap and updates its items:
`PLANNED → IN_PROGRESS → DONE_WITH_EVIDENCE`.
Each update records timestamp, source SHA, environment, tests/results, evidence URL and NEXT_ACTION. Continue independent safe work without Coordinator/A0 microacceptance.

Coordinator:
- integrates outcome, WBS, skill and owner mappings;
- resolves dependencies and source conflicts;
- checks roadmap-level completeness and cross-source consistency;
- accepts handoff at roadmap/package level, not every safe routine item;
- escalates only genuine security/permission/technical blockers or reserved A0 decisions.

A0 Assistant:
- independently reviews the complete DGN package against the six subject areas and five evaluation criteria in its role profile;
- reports PASS / PASS_WITH_CONDITIONS / FAIL with exact evidence and conditions;
- does not take over delivery ownership or issue production/merge approval.

A0:
- makes the final package decision and retains reserved authority.

## 6. Risk, fallback and STOP

- Least privilege; no credentials or PII in public GitHub.
- No production, deployment, publication, external account write, paid inference, Codex spend, merge or permission uplift without exact approval, preflight, cost cap and rollback.
- Hostinger remains paused; Hermes cost-gated; Codex exception-only; all UI build, business pilot, WP/Ads/media operations and automated dispatch remain HOLD unless separately released.
- If a capability or permission is UNKNOWN, keep the task NOT_DISPATCHED/HOLD; do not silently reassign. Coordinator may propose a qualified fallback but must create a new scoped handoff and obtain its real ACK.
- STOP only the unsafe side effect; continue independent safe reading/design/source reconciliation.
- On failure, preserve evidence, identify affected WBS, observed result, attempted alternatives, owner and unblocking condition. Do not turn missing evidence into PASS or zero.

## 7. DGN-2 source integration and current limits

Canonical capability source: `program/SKILL_REGISTRY.md` from A1 PR46 head `070189b381dd3e17680c85fdff01e84978c0bf93`, blob `6d79a1c5d11bab1ef03c55c68d2b8d55d32609bf`.
- Eight Agent role families.
- 20 canonical `K-*` skill IDs; 19 `S-*` integration surfaces.
- Nine installable candidates; **none installed by DGN-2**.
- Original 32 WBS rows' skill IDs resolve 20/20 against the canonical dictionary.
- Other-Agent current session capability/permission claims remain UNKNOWN or REPORTED unless each Agent self-verifies.
- Candidate list does not authorize installation. Installation requires candidate ID, target WBS, measured gap, provider/version, OS, scopes, data class, payer, current price/quota source, max cost, safe test, rollback owner and approval ID.

## 8. Effectiveness and change control

This document is a **Coordinator candidate design artifact only**. It does not amend `rules/AGENT_WORKFLOW.md`, `AGENTS.md`, `STATE.md` or main. It is not an effective rule, dispatcher, permission grant or release approval. Any rule amendment requires its own authorized write-set, security/diff review, A0 approval where reserved, and remote main readback. Until then, current main rules govern.

**Package dependencies:** DGN-1 Product Charter + Operator UI; DGN-2 capability directory; DGN-3 32-row WBS; DGN-4 32-row assignment matrix and Agent-owned roadmaps. **Package status:** NOT_ACCEPTED pending one independent package review and A0 decision.
