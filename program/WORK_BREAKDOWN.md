# Hosting — KNG-01 frozen 32-item WBS with original deliverable and gate

**Current dispatch: KNG-01 ONLY.** The 32 rows below preserve the original Gate, Deliverable, Owner, Required skills, Dependencies and Acceptance fields verbatim from PR39 Git blob `60beab3ad23abf7c67adf288dc0c213c14befcfe`; only the final `Current route` is candidate-derived. No non-KNG assignment is activated. [Current route](current.json) · [Effective full rules](../rules/AGENT_WORKFLOW.md).

| WBS ID | Gate | Original deliverable | Required skills | Owner | Dependencies | Acceptance | Current route |
|---|---|---|---|---|---|---|---|
| G0-01 | G0 | Reconciled product charter with final outcome, personas and business KPIs | K-DOC,K-DATA | A2 | existing PROJECT, ROADMAP | charter & conflicts documented | ON_HOLD_DEPENDENCY_KNG01 |
| G0-02 | G0 | Operator Console navigation, task/agent/approval UI flows | K-UX,K-DOC | A2 | G0-01 | functional UI spec and acceptance | ON_HOLD_DEPENDENCY_KNG01 |
| G0-03 | G0 | MVP and roadmap dependencies, distinguish mock vs live | K-DOC,K-SCHEMA | Coordinator | G0-01,G0-02 | milestone gates and paths | ON_HOLD_DEPENDENCY_KNG01 |
| G1-01 | G1 | Git knowledge inventory, redundant facts and authority map | K-GIT,K-PY,K-DOC | A1 | current repo, PR31 | inventory with counts/source pins | KNG_ONLY |
| G1-02 | G1 | Compact context entry and pilot per-task pack | K-GIT,K-SCHEMA,K-DOC | A1 | G1-01 | linked test case with provenance | KNG_ONLY |
| G1-03 | G1 | Metadata/links/secret/scope validator; checks run offline | K-PY,K-SCHEMA,K-TEST,K-SEC | A1 | G1-02 | passing + negative fixtures and logs | KNG_ONLY |
| G1-04 | G1 | Comprehension/token A/B evaluation, no safety regression | K-QA,K-TEST,K-DATA | Work | G1-02,G1-03 | independent actual metrics/verdict | KNG_ONLY_INDEPENDENT_QA_PENDING_ACK |
| G2-01 | G2 | Roadmap-level autonomous item update + exception contract | K-DOC,K-SCHEMA,K-SEC | Coordinator | G0-03 | no ordinary per-item acceptance | ON_HOLD_DEPENDENCY_KNG01 |
| G2-02 | G2 | Durable task item/update event schema and repeatable status generation | K-PY,K-SCHEMA,K-GIT | A1 | G2-01,G1-03 | real write/readback and dedupe tests | ON_HOLD_DEPENDENCY_KNG01 |
| G2-03 | G2 | Risk-based QA and versioned approval/merge protocol | K-SEC,K-QA,K-DOC | Coordinator | G2-01 | targeted policy checks; no gate bypass | ON_HOLD_DEPENDENCY_KNG01 |
| G3-01 | G3 | Capability/skills including optional installation candidates | K-DOC,K-GIT,K-DATA | A2 | G0-01 | five-agent role rows, provenance | ON_HOLD_DEPENDENCY_KNG01 |
| G3-02 | G3 | PR portfolio consolidation + dependency routing | K-GIT,K-DATA,K-SCHEMA | Coordinator | G0-03,G1-01 | actionable list with owner/next | ON_HOLD_DEPENDENCY_KNG01 |
| G3-03 | G3 | Roadmap issuance, per-agent sole writer ownership | K-GIT,K-SCHEMA | Coordinator | G2-01,G3-02 | exact per-agent roadmap/readback | ON_HOLD_DEPENDENCY_KNG01 |
| INF-01 | Infra | VPS/hosting/WordPress service baseline, risks, health | K-VPS,K-SEC,K-OBS | Hostinger | existing inventory | fresh scoped live read evidence | ON_HOLD_DEPENDENCY_KNG01 |
| INF-02 | Infra | Backup/restore verified in safe environment | K-VPS,K-BACKUP,K-TEST,K-SEC | Hostinger | INF-01 | restore evidence and rollback | ON_HOLD_DEPENDENCY_KNG01 |
| INF-03 | Infra | Monitoring, fault alerts and secure runtime plan | K-VPS,K-OBS,K-SEC | Hostinger | INF-01 | live checks scoped + report | ON_HOLD_DEPENDENCY_KNG01 |
| INF-04 | Infra | Minimal safe n8n integration capability and recoverability | K-VPS,K-N8N,K-API,K-TEST | Hostinger | INF-02,INF-03 | sandbox execution and rollback | ON_HOLD_DEPENDENCY_KNG01 |
| UI-01 | Product | Operator Console UI prototype connected to representative task schema | K-UX,K-BROW,K-PY | Work | G0-02,G2-02 | real interactive UX and edge cases | ON_HOLD_DEPENDENCY_KNG01 |
| UI-02 | Product | Operator Console integration with durable task state and approvals | K-UX,K-API,K-TEST,K-SEC | Work | UI-01,G2-02,INF-03 | E2E live/sandbox documented | ON_HOLD_DEPENDENCY_KNG01 |
| CTRL-01 | Product | Two existing Agent sessions dispatch/ACK/receipt PoC | K-BROW,K-AUTO,K-TEST,K-SEC | Work | G2-01 | synthetic two-session evidence | ON_HOLD_DEPENDENCY_KNG01 |
| UC01-01 | Business | Bounded WordPress product/page/post content audit | K-WP,K-SEO,K-DATA | A2 | existing authenticated source | repeatable audit + UNKNOWN/errors | ON_HOLD_DEPENDENCY_KNG01 |
| UC01-02 | Business | Reproducible audit pipeline/report and UX consumption | K-WP,K-PY,K-API,K-TEST | Work | UC01-01,UI-01 | input->output->UI trace, QA | ON_HOLD_DEPENDENCY_KNG01 |
| GROW-01 | Business | Ads/GA4/UTM lead attribution read-only baseline | K-ADS,K-DATA,K-SEC | A2 | consent/source scoped | proven attribution limitations | ON_HOLD_DEPENDENCY_KNG01 |
| GROW-02 | Business | Media/social editorial workflow with human approval | K-MEDIA,K-DOC,K-UX,K-SEC | A2 | G0-01 | draft-to-approval demo | ON_HOLD_DEPENDENCY_KNG01 |
| GROW-03 | Business | Cross-channel dashboard with provenance and costs | K-DATA,K-ADS,K-API,K-UX | Work | GROW-01,UI-02 | validated data freshness/KPI | ON_HOLD_DEPENDENCY_KNG01 |
| REL-01 | Release | Integrated roadmap review, independent QA and next milestone | K-QA,K-SEC,K-GIT | Coordinator | sufficient gate deliverables | one roadmap-level verdict, no false LIVE | ON_HOLD_DEPENDENCY_KNG01 |
| REL-02 | Release | Owner portfolio acceptance, scoped live approvals if needed | K-DOC,K-SEC | A0 | REL-01 | explicit decision/event | ON_HOLD_DEPENDENCY_KNG01 |
| G3-A1 | G3 | Check A1 capability and data inventory claims against executed evidence | K-GIT,K-TEST | A1 | G1-03 | source-linked delta with actual checks | ON_HOLD_DEPENDENCY_KNG01 |
| QA-U01 | G4 | Independently sample A2 WordPress audit, report incorrect inference | K-QA,K-SEO,K-DATA | A1 | UC01-01 | sampled audit evidence and verdict | ON_HOLD_DEPENDENCY_KNG01 |
| EXIST-QA31 | Existing | Execute already assigned PR31 cost-first/progress independent QA | K-QA,K-GIT,K-SEC | Work | PR31 pinned assignment | one factual verdict, no unrelated rerun | SEPARATE_IN_FLIGHT_OR_PARK_WITH_EVIDENCE |
| SEC-H | Infra | Secure hardening plan for SSH/exposed ports/firewall/backup | K-SEC,K-VPS,K-BACKUP | Hostinger | INF-01 | risk-gated work package with live evidence | ON_HOLD_DEPENDENCY_KNG01 |
| WP-H | Infra | Diagnose WordPress HTTP500 source as safely reproducible | K-VPS,K-WP,K-OBS | Hostinger | UC01-01 | bounded diagnosis, no site mutation | ON_HOLD_DEPENDENCY_KNG01 |

Historical evidence and old parallel-start prose are preserved at [PR39 original WBS](https://github.com/DuyKienTTD/Hosting/blob/22d741e3f1dd325540932dea63c3a6da635113c3/program/WORK_BREAKDOWN.md). G1-01/02/03 are the only active implementation lane; G1-04 Work is independent QA once actual D2 ACK. Other lanes stay ON_HOLD_DEPENDENCY_KNG01. Candidate status is not a new task assignment or production authorization.


---

## DGN-3 — Complete row-level WBS (Coordinator design candidate, 2026-11-24)

**Status:** DGN3_ROW_LEVEL_DESIGN_CANDIDATE / NOT_FROZEN / NOT_DISPATCHED. The 32-row table above is preserved verbatim as historical baseline, including original IDs, Gate, deliverable, required skills, owner, dependencies, acceptance and source-era route. Historical routes are not current authorization. No original ID is deleted, renamed or silently merged.

**Authority/source pins:** DGN-1 A2 PR44 head bf232a313c0dd696c4ae824c35e7d1ddfda1a613; DGN-2 A1 PR46 head 070189b381dd3e17680c85fdff01e84978c0bf93; Work feasibility commit 4309773bfc20a43970a6b773f352999ef09b77cf; original WBS blob 0d800afb4531e4db65f81f19431c3afde8dab4b6; effective main AGENTS af42293a8ae7d3e864cd9f89442bc6861e85c080, workflow 9dd6a1601e9b2a1b472f4a1ae89e9626ada05797, security c24d608036b11dcd3fafcaefbefa23fdb591990e. This is a design branch, not an effective main update.

### Canonical schema

Every row defines: WBS_ID, PRODUCT_OUTCOME, FEATURE/UI, WORK_TYPE, PRIORITY, DELIVERABLE, REQUIRED_SKILL_IDS, MINIMUM_TOOL_CAPABILITY, AGENT_CANDIDATES, PREDECESSORS, ENVIRONMENT/DATA/ACCESS, RISK/COST/STOP, ACCEPTANCE, EVIDENCE/PROVENANCE, STATUS and TARGET_ROADMAP. One accountable primary candidate is named; candidate does not mean dispatched, accepted or authorized. UNKNOWN is never zero, PASS or permission.

### Priority and work-type semantics

- P0: prerequisite for coherent, auditable design/release decision; not production activation priority.
- P1: first measurable read-only business/UI value after separate A0 release.
- P2: integration, business expansion or reliability after foundational evidence.
- DESIGN: specification; HISTORICAL IMPLEMENTATION/QA: completed source-era work; BUILD/INTEGRATION: future product work; READ-ONLY AUDIT: data discovery; OPERATIONS: live environment; INDEPENDENT QA: separate reviewer; OWNER DECISION: reserved A0 action.
- Design order: DGN-1/DGN-2 → G0-03/G2-01/G2-03 → G2-02/G3-02/G3-03 → future UI/business/infra → REL-01 → REL-02.


### G0-01 — Product Charter with O1–O5, personas, authorization matrix, M0–M5 and KPI measurement contracts; author-complete.

- **WBS_ID:** G0-01
- **PRODUCT_OUTCOME:** O1,O5; product value, personas and KPI
- **FEATURE_UI:** S02; DGN-1 §§1,1.3
- **WORK_TYPE:** DESIGN
- **PRIORITY:** P0
- **DELIVERABLE:** Product Charter with O1–O5, personas, authorization matrix, M0–M5 and KPI measurement contracts; author-complete.
- **REQUIRED_SKILL_IDS:** K-DOC,K-DATA,K-UX
- **MINIMUM_TOOL_CAPABILITY:** GitHub source read/branch/diff/readback; Markdown/spec review; no business connector required for design.
- **PRIMARY_OWNER_CANDIDATE:** A2; Coordinator integrates
- **AGENT_CANDIDATES:** A2
- **CONTRIBUTORS:** Coordinator (integration owner)
- **PREDECESSORS:** Existing PROJECT/ROADMAP; DGN-1.
- **ENVIRONMENT_DATA_ACCESS:** ChatGPT + isolated Git branch; sanitized project context only.
- **RISK_COST_STOP:** No live KPI baseline; future data access/cost UNKNOWN. STOP on unsupported metric claims or unauthorized private data.
- **ACCEPTANCE:** Outcomes/personas/rights, KPI numerator/denominator/source/cadence/null semantics and source SHA; package gate later.
- **EVIDENCE_PROVENANCE:** PR44 Product/UI blob 72678f795409e4bef4ebefb7d157439dd4adda05.
- **STATUS:** DESIGN_DONE_WITH_AUTHOR_EVIDENCE; package gate pending.
- **TARGET_ROADMAP:** program/roadmaps/a2.md


### G0-02 — 12-screen specification, navigation, data/action/state contracts, five journeys and responsive/error/UNKNOWN/offline states.

- **WBS_ID:** G0-02
- **PRODUCT_OUTCOME:** O1–O5; Operator Console information architecture
- **FEATURE_UI:** S01–S12; J01–J05; DGN-1 §§2–5
- **WORK_TYPE:** DESIGN
- **PRIORITY:** P0
- **DELIVERABLE:** 12-screen specification, navigation, data/action/state contracts, five journeys and responsive/error/UNKNOWN/offline states.
- **REQUIRED_SKILL_IDS:** K-UX,K-DOC,K-SEC,K-DATA
- **MINIMUM_TOOL_CAPABILITY:** GitHub docs and source traceability; future browser/DOM harness not required for design.
- **PRIMARY_OWNER_CANDIDATE:** A2 sole product/UI writer; Work read-only consultant
- **AGENT_CANDIDATES:** A2
- **CONTRIBUTORS:** Work (feasibility consultant)
- **PREDECESSORS:** G0-01; Work DGN-FEASIBILITY.
- **ENVIRONMENT_DATA_ACCESS:** Design branch; future UI test environment separately authorized.
- **RISK_COST_STOP:** Accessibility, browser RBAC and live UI remain UNKNOWN. No build/deploy.
- **ACCEPTANCE:** S01–S12 each maps outcome, actor/permission, entry, source, action, state, KPI, evidence and T-case; T01–T24 unique and DESIGN_NOT_RUN.
- **EVIDENCE_PROVENANCE:** PR44; Work report commit 4309773.
- **STATUS:** DESIGN_DONE_WITH_AUTHOR_EVIDENCE; no runtime acceptance.
- **TARGET_ROADMAP:** program/roadmaps/a2.md


### G0-03 — Integrated milestone/dependency plan distinguishing governance, read-only business pilot, UI MVP, orchestration, expansion and reliable operation.

- **WBS_ID:** G0-03
- **PRODUCT_OUTCOME:** O1–O5; MVP M0–M5 sequencing and release boundary
- **FEATURE_UI:** S01–S12; product milestone architecture
- **WORK_TYPE:** DESIGN/ARCHITECTURE
- **PRIORITY:** P0
- **DELIVERABLE:** Integrated milestone/dependency plan distinguishing governance, read-only business pilot, UI MVP, orchestration, expansion and reliable operation.
- **REQUIRED_SKILL_IDS:** K-DOC,K-SCHEMA,K-DATA,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** GitHub docs, dependency graph and state modelling; no runtime required.
- **PRIMARY_OWNER_CANDIDATE:** Coordinator
- **AGENT_CANDIDATES:** Coordinator
- **CONTRIBUTORS:** A1 (schema consultant)
- **PREDECESSORS:** G0-01,G0-02; DGN-2; Work feasibility.
- **ENVIRONMENT_DATA_ACCESS:** Coordinator design branch; public Git sources only.
- **RISK_COST_STOP:** Historic HOLD not activated; future costs UNKNOWN. STOP at unapproved live/paid work.
- **ACCEPTANCE:** M0–M5 entry/exit criteria, predecessor graph, evidence gates, mock/live boundary and non-goals; acyclic DAG.
- **EVIDENCE_PROVENANCE:** A2 §§1.2,2; A1 Registry; Work report.
- **STATUS:** PLANNED; design in progress.
- **TARGET_ROADMAP:** program/roadmaps/coordinator.md


### G1-01 — Source-path inventory, authority map and duplicate/conflict analysis completed in KNG-01; preserve evidence.

- **WBS_ID:** G1-01
- **PRODUCT_OUTCOME:** Governance/source integrity; knowledge inventory
- **FEATURE_UI:** KNG-01 source lineage
- **WORK_TYPE:** HISTORICAL IMPLEMENTATION
- **PRIORITY:** P0
- **DELIVERABLE:** Source-path inventory, authority map and duplicate/conflict analysis completed in KNG-01; preserve evidence.
- **REQUIRED_SKILL_IDS:** K-GIT,K-PY,K-DOC,K-DATA
- **MINIMUM_TOOL_CAPABILITY:** GitHub source/blobs; local Git/Python only for concrete delta.
- **PRIMARY_OWNER_CANDIDATE:** A1 historical owner
- **AGENT_CANDIDATES:** A1 (historical)
- **CONTRIBUTORS:** None; historical
- **PREDECESSORS:** PR31/KNG baseline.
- **ENVIRONMENT_DATA_ACCESS:** Historical KNG evidence; no new live access.
- **RISK_COST_STOP:** No PASS rerun absent change trigger; no archive/delete without retention/reference audit.
- **ACCEPTANCE:** Historical KNG evidence and merged-main readback; delta-only regression if changed.
- **EVIDENCE_PROVENANCE:** KNG-01 merged main d549564; PR43.
- **STATUS:** HISTORICAL_COMPLETE_PER_KNG01_CHECKPOINT; not reopened.
- **TARGET_ROADMAP:** program/roadmaps/a1.md history


### G1-02 — Compact task entry/context pack and provenance migration completed in KNG-01; preserve historical source/evidence.

- **WBS_ID:** G1-02
- **PRODUCT_OUTCOME:** Governance/source integrity; compact task context pack
- **FEATURE_UI:** KNG-01 context pack
- **WORK_TYPE:** HISTORICAL IMPLEMENTATION
- **PRIORITY:** P0
- **DELIVERABLE:** Compact task entry/context pack and provenance migration completed in KNG-01; preserve historical source/evidence.
- **REQUIRED_SKILL_IDS:** K-GIT,K-SCHEMA,K-DOC
- **MINIMUM_TOOL_CAPABILITY:** GitHub source and offline schema validation only on change trigger.
- **PRIMARY_OWNER_CANDIDATE:** A1 historical owner
- **AGENT_CANDIDATES:** A1 (historical)
- **CONTRIBUTORS:** None; historical
- **PREDECESSORS:** G1-01.
- **ENVIRONMENT_DATA_ACCESS:** Historical KNG source.
- **RISK_COST_STOP:** No duplicate optimization or paid benchmark rerun absent measured trigger.
- **ACCEPTANCE:** Historical acceptance and source pins remain accessible; no source facts lost.
- **EVIDENCE_PROVENANCE:** KNG-01 merged main d549564; PR43.
- **STATUS:** HISTORICAL_COMPLETE_PER_KNG01_CHECKPOINT; not reopened.
- **TARGET_ROADMAP:** program/roadmaps/a1.md history


### G1-03 — Offline validator and positive/negative fixtures from KNG-01; preserve test evidence.

- **WBS_ID:** G1-03
- **PRODUCT_OUTCOME:** Governance/source integrity; metadata/link/secret/scope validator
- **FEATURE_UI:** KNG-01 validator
- **WORK_TYPE:** HISTORICAL IMPLEMENTATION
- **PRIORITY:** P0
- **DELIVERABLE:** Offline validator and positive/negative fixtures from KNG-01; preserve test evidence.
- **REQUIRED_SKILL_IDS:** K-PY,K-SCHEMA,K-TEST,K-SEC,K-GIT
- **MINIMUM_TOOL_CAPABILITY:** Python/Git objects/offline fixtures; no external service.
- **PRIMARY_OWNER_CANDIDATE:** A1 historical author; Work historical QA
- **AGENT_CANDIDATES:** A1 (historical)
- **CONTRIBUTORS:** Work (historical independent reviewer)
- **PREDECESSORS:** G1-02.
- **ENVIRONMENT_DATA_ACCESS:** Offline/local and GitHub read-only.
- **RISK_COST_STOP:** No broad rerun unless source/code changed; no secrets in fixtures/logs.
- **ACCEPTANCE:** Historical test evidence, independent QA and exact source pins; delta-only regression if changed.
- **EVIDENCE_PROVENANCE:** KNG-01 PR43; 61/61 independent Work QA per checkpoint.
- **STATUS:** HISTORICAL_COMPLETE_PER_KNG01_CHECKPOINT; not reopened.
- **TARGET_ROADMAP:** program/roadmaps/a1.md history


### G1-04 — Independent evaluation of context pack and validator; retain historical verdict and measurements.

- **WBS_ID:** G1-04
- **PRODUCT_OUTCOME:** Governance/source integrity; comprehension/token and safety regression QA
- **FEATURE_UI:** KNG-01 independent evaluation
- **WORK_TYPE:** HISTORICAL INDEPENDENT QA
- **PRIORITY:** P0
- **DELIVERABLE:** Independent evaluation of context pack and validator; retain historical verdict and measurements.
- **REQUIRED_SKILL_IDS:** K-QA,K-TEST,K-DATA,K-GIT
- **MINIMUM_TOOL_CAPABILITY:** Independent Work session and source-pinned offline harness.
- **PRIMARY_OWNER_CANDIDATE:** Work historical reviewer; Coordinator records lineage
- **AGENT_CANDIDATES:** Work (historical)
- **CONTRIBUTORS:** Coordinator (lineage only)
- **PREDECESSORS:** G1-02,G1-03.
- **ENVIRONMENT_DATA_ACCESS:** Offline QA only.
- **RISK_COST_STOP:** No rerun of historical PASS absent change trigger; reviewer differs from author.
- **ACCEPTANCE:** Verdict bound to exact candidate SHA; source integrity and safety preserved.
- **EVIDENCE_PROVENANCE:** KNG-01 PR43; 61/61 Work QA per checkpoint.
- **STATUS:** HISTORICAL_COMPLETE_PER_KNG01_CHECKPOINT; not reopened.
- **TARGET_ROADMAP:** program/roadmaps/work.md history


### G2-01 — Define task lifecycle, owner/attempt/receipt semantics, self-progress, UNKNOWN/STOP and one roadmap-level acceptance model.

- **WBS_ID:** G2-01
- **PRODUCT_OUTCOME:** O1,O2,O3; task/roadmap lifecycle and exception contract
- **FEATURE_UI:** S03,S04,S06,S07,S08
- **WORK_TYPE:** OPERATING MODEL DESIGN
- **PRIORITY:** P0
- **DELIVERABLE:** Define task lifecycle, owner/attempt/receipt semantics, self-progress, UNKNOWN/STOP and one roadmap-level acceptance model.
- **REQUIRED_SKILL_IDS:** K-DOC,K-SCHEMA,K-SEC,K-DATA
- **MINIMUM_TOOL_CAPABILITY:** GitHub docs and state-machine modelling; no dispatcher build.
- **PRIMARY_OWNER_CANDIDATE:** Coordinator
- **AGENT_CANDIDATES:** Coordinator
- **CONTRIBUTORS:** A1 (schema consultant); Work (feasibility input)
- **PREDECESSORS:** G0-03; DGN-1; DGN-2; Work feasibility.
- **ENVIRONMENT_DATA_ACCESS:** Coordinator design branch; no live session control.
- **RISK_COST_STOP:** Owner-forward only is currently verified; auto session dispatch/receipt UNKNOWN. STOP on missing ACK or uncertain side effect.
- **ACCEPTANCE:** PREPARED→SENT→ACKNOWLEDGED→IN_PROGRESS→DONE_WITH_EVIDENCE→READY_FOR_ROADMAP_ACCEPTANCE; BLOCKED/UNKNOWN/STOP alternatives; no PR-derived ACK.
- **EVIDENCE_PROVENANCE:** Coordinator C-D2; A1 registry; Work report.
- **STATUS:** DESIGN_DRAFT_IN_PROGRESS; NOT_EFFECTIVE_RULE until authorized integration.
- **TARGET_ROADMAP:** program/roadmaps/coordinator.md


### G2-02 — Specify append-only event schema, receipts, idempotency/deduplication, status projection, source freshness and reconciliation; build is separate gated phase.

- **WBS_ID:** G2-02
- **PRODUCT_OUTCOME:** O1,O2,O3; durable task/event and status projection
- **FEATURE_UI:** S03,S04,S06,S08
- **WORK_TYPE:** DATA/INTEGRATION DESIGN; later BUILD
- **PRIORITY:** P1
- **DELIVERABLE:** Specify append-only event schema, receipts, idempotency/deduplication, status projection, source freshness and reconciliation; build is separate gated phase.
- **REQUIRED_SKILL_IDS:** K-PY,K-SCHEMA,K-GIT,K-API,K-TEST,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** Design: docs/schema. Future build: isolated backend, DB, migration/test runner and authenticated Git/session adapter.
- **PRIMARY_OWNER_CANDIDATE:** A1 schema/technical candidate; Coordinator owns operating contract
- **AGENT_CANDIDATES:** A1
- **CONTRIBUTORS:** Coordinator (operating contract); Work (integration consultant)
- **PREDECESSORS:** G2-01,G1-03; Work feasibility; G2-03.
- **ENVIRONMENT_DATA_ACCESS:** Offline design; future sandbox with synthetic records only.
- **RISK_COST_STOP:** Cross-session connector and paid/API costs UNKNOWN. STOP before live ledger/provider callback without scope, backup and rollback.
- **ACCEPTANCE:** Test design covers duplicate same/different payload, event ordering, timeout UNKNOWN, replay, rollback and source-SHA binding; runtime tests only after build approval.
- **EVIDENCE_PROVENANCE:** A1 K-API/K-AUTO; Work SQLite fixture report.
- **STATUS:** DESIGN_SPEC_REQUIRED; implementation HOLD.
- **TARGET_ROADMAP:** program/roadmaps/a1.md


### G2-03 — Define approval scope/version/expiry/cost cap/revocation, author-reviewer separation, rollback and release gates.

- **WBS_ID:** G2-03
- **PRODUCT_OUTCOME:** O3; approval, STOP, risk-tier QA and merge protocol
- **FEATURE_UI:** S07,S08,S12
- **WORK_TYPE:** GOVERNANCE DESIGN
- **PRIORITY:** P0
- **DELIVERABLE:** Define approval scope/version/expiry/cost cap/revocation, author-reviewer separation, rollback and release gates.
- **REQUIRED_SKILL_IDS:** K-SEC,K-QA,K-DOC,K-SCHEMA
- **MINIMUM_TOOL_CAPABILITY:** GitHub PR review, versioned docs, negative policy fixtures; no main rule mutation.
- **PRIMARY_OWNER_CANDIDATE:** Coordinator; A0 approval authority
- **AGENT_CANDIDATES:** Coordinator
- **CONTRIBUTORS:** A1 (schema consultant); A0 (reserved approver, not contributor)
- **PREDECESSORS:** G2-01,G0-03.
- **ENVIRONMENT_DATA_ACCESS:** Coordinator branch; synthetic examples.
- **RISK_COST_STOP:** A0 retains paid/production/publish/deploy/merge decisions. No skill possession implies permission.
- **ACCEPTANCE:** Approval invalidated by target/SHA/cost drift or expiry; denial/revocation fail closed; independent reviewer; no auto-merge.
- **EVIDENCE_PROVENANCE:** Main rules; A0 directives; A2 S07/S12 and T07,T12–T16,T21.
- **STATUS:** DESIGN_DRAFT_IN_PROGRESS; effective rules unchanged.
- **TARGET_ROADMAP:** program/roadmaps/coordinator.md


### G3-01 — Eight Agent directory, 20 canonical K IDs, 19 S surfaces, nine installable candidates and capability/authorization distinction.

- **WBS_ID:** G3-01
- **PRODUCT_OUTCOME:** O2,O3; Agent capability/skills directory
- **FEATURE_UI:** S05,S06
- **WORK_TYPE:** CAPABILITY INVENTORY
- **PRIORITY:** P0
- **DELIVERABLE:** Eight Agent directory, 20 canonical K IDs, 19 S surfaces, nine installable candidates and capability/authorization distinction.
- **REQUIRED_SKILL_IDS:** K-DOC,K-GIT,K-DATA,K-SCHEMA,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** GitHub branch/diff/readback; each Agent must self-survey for fresh capability claims.
- **PRIMARY_OWNER_CANDIDATE:** A1 DGN-2 owner; A2 consult
- **AGENT_CANDIDATES:** A1
- **CONTRIBUTORS:** A2 (product requirements); Work (review only if separately assigned)
- **PREDECESSORS:** G0-01; DGN-1; agent profiles; Work report.
- **ENVIRONMENT_DATA_ACCESS:** A1 isolated branch; other Agent profiles remain historical/REPORTED unless self-confirmed.
- **RISK_COST_STOP:** No installation, paid spend, permission uplift or dispatch; A1 cannot verify other sessions.
- **ACCEPTANCE:** 20/20 WBS K IDs resolve; all Agent rows have provenance/fallback; nine candidates have preconditions/cost/rollback; UNKNOWN preserved.
- **EVIDENCE_PROVENANCE:** PR46 head 070189b; Registry blob 6d79a1c; A1 roadmap blob 76c47dac.
- **STATUS:** AUTHOR_COMPLETE_READY_FOR_ROADMAP_ACCEPTANCE; package gate pending.
- **TARGET_ROADMAP:** program/roadmaps/a1.md


### G3-02 — Resolve PR/task portfolio by outcome/dependency; remove assignment conflicts without deleting history; map every design WBS to one proposed owner.

- **WBS_ID:** G3-02
- **PRODUCT_OUTCOME:** O1,O2,O3; portfolio consolidation and dependency routing
- **FEATURE_UI:** S03,S05,S06
- **WORK_TYPE:** PORTFOLIO DESIGN
- **PRIORITY:** P0
- **DELIVERABLE:** Resolve PR/task portfolio by outcome/dependency; remove assignment conflicts without deleting history; map every design WBS to one proposed owner.
- **REQUIRED_SKILL_IDS:** K-GIT,K-DATA,K-SCHEMA,K-DOC,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** GitHub PR/branch metadata, source comparison and deterministic ID/dependency inventory.
- **PRIMARY_OWNER_CANDIDATE:** Coordinator
- **AGENT_CANDIDATES:** Coordinator
- **CONTRIBUTORS:** A1 (source evidence)
- **PREDECESSORS:** G0-03,G1-01,G3-01; DGN-1/DGN-2.
- **ENVIRONMENT_DATA_ACCESS:** Coordinator integration branch; GitHub read; no merge.
- **RISK_COST_STOP:** PR status is not Agent ACK; preserve HOLD; no unnecessary PR consolidation or source deletion.
- **ACCEPTANCE:** Each source classified by authoritative SHA, owner, status confidence, dependency, duplicate/superseded relation and next action.
- **EVIDENCE_PROVENANCE:** PR31/43/44/46; A1 registry; Work report.
- **STATUS:** IN_PROGRESS_DESIGN.
- **TARGET_ROADMAP:** program/roadmaps/coordinator.md


### G3-03 — Create actionable roadmaps from WBS/assignment; each recipient edits only its roadmap after actual task ACK.

- **WBS_ID:** G3-03
- **PRODUCT_OUTCOME:** O1,O2,O3; per-Agent roadmap issuance and sole-writer model
- **FEATURE_UI:** S04,S06
- **WORK_TYPE:** ROADMAP DESIGN/HANDOFF
- **PRIORITY:** P0
- **DELIVERABLE:** Create actionable roadmaps from WBS/assignment; each recipient edits only its roadmap after actual task ACK.
- **REQUIRED_SKILL_IDS:** K-GIT,K-SCHEMA,K-DOC,K-SEC,K-AUTO
- **MINIMUM_TOOL_CAPABILITY:** GitHub branch/PR/readback; owner-forward is manual; no cross-session dispatcher verified.
- **PRIMARY_OWNER_CANDIDATE:** Coordinator issues; each Agent sole-writes its roadmap
- **AGENT_CANDIDATES:** Coordinator
- **CONTRIBUTORS:** Each recipient Agent, sole-writer of own roadmap after ACK
- **PREDECESSORS:** G2-01,G2-02,G3-02.
- **ENVIRONMENT_DATA_ACCESS:** Per-Agent branch and file; manual handoff; no credentials.
- **RISK_COST_STOP:** No cross-Agent roadmap edits; PR/comment not SENT/ACK; Codex exception-only, Hermes cost-gated, Hostinger paused.
- **ACCEPTANCE:** Every eligible WBS routes to one roadmap with FIRST_ACTION, skills/tools, dependencies, READ/WRITE, cost/STOP, acceptance/evidence and next action.
- **EVIDENCE_PROVENANCE:** A1/A2/Work roadmaps; Work feasibility.
- **STATUS:** PLANNED_NOT_DISPATCHED.
- **TARGET_ROADMAP:** program/roadmaps/coordinator.md


### INF-01 — Fresh scoped inventory of hosting services, resource health, network, DNS/TLS and WordPress baseline.

- **WBS_ID:** INF-01
- **PRODUCT_OUTCOME:** O3; hosting/VPS/WordPress baseline
- **FEATURE_UI:** S10,S11
- **WORK_TYPE:** INFRA DIAGNOSTIC/OPERATIONS
- **PRIORITY:** P2
- **DELIVERABLE:** Fresh scoped inventory of hosting services, resource health, network, DNS/TLS and WordPress baseline.
- **REQUIRED_SKILL_IDS:** K-VPS,K-SEC,K-OBS,K-WP
- **MINIMUM_TOOL_CAPABILITY:** Hostinger hPanel/authorized SSH or read-only telemetry; verify identity/version.
- **PRIMARY_OWNER_CANDIDATE:** Hostinger Agent proposed specialist
- **AGENT_CANDIDATES:** Hostinger Agent (PAUSED)
- **CONTRIBUTORS:** None; A1 may provide static notes only if separately assigned
- **PREDECESSORS:** Existing inventory; separate A0 resume + Hostinger ACK.
- **ENVIRONMENT_DATA_ACCESS:** Provider/VPS read-only; no secrets in Git.
- **RISK_COST_STOP:** Hostinger PAUSED for new/unfinished tasks under main rules; cost UNKNOWN. STOP any mutation/restart/production access.
- **ACCEPTANCE:** Timestamped live observations, service/version/resource/network evidence, redacted logs and UNKNOWN where inaccessible.
- **EVIDENCE_PROVENANCE:** Main AGENT_WORKFLOW §11.1a/§12.4; historical Hostinger inventory.
- **STATUS:** HOLD_PAUSED_HOSTINGER; not dispatched.
- **TARGET_ROADMAP:** No active roadmap until resume and ACK


### INF-02 — Prove backup integrity and restore into isolated safe environment; document RPO/RTO evidence and rollback.

- **WBS_ID:** INF-02
- **PRODUCT_OUTCOME:** O3; backup and restore verification
- **FEATURE_UI:** S10,S12
- **WORK_TYPE:** RECOVERY TEST/OPERATIONS
- **PRIORITY:** P2
- **DELIVERABLE:** Prove backup integrity and restore into isolated safe environment; document RPO/RTO evidence and rollback.
- **REQUIRED_SKILL_IDS:** K-VPS,K-BACKUP,K-TEST,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** Authorized backup inventory, isolated restore target and integrity tools.
- **PRIMARY_OWNER_CANDIDATE:** Hostinger Agent proposed; A1 runbook design fallback
- **AGENT_CANDIDATES:** Hostinger Agent (PAUSED)
- **CONTRIBUTORS:** A1 (runbook design only; not restore execution)
- **PREDECESSORS:** INF-01.
- **ENVIRONMENT_DATA_ACCESS:** Isolated restore environment; data minimization.
- **RISK_COST_STOP:** Hostinger paused; no restore permission; costs UNKNOWN. STOP if no backup, isolation or rollback.
- **ACCEPTANCE:** Restore synthetic/non-sensitive snapshot, integrity and service validation, logs; backup presence alone is not PASS.
- **EVIDENCE_PROVENANCE:** Historical infra inventory; Work/A1 recovery design.
- **STATUS:** HOLD_PAUSED_HOSTINGER.
- **TARGET_ROADMAP:** No active roadmap until resume and ACK


### INF-03 — Define monitoring/alert thresholds, freshness, ownership, health-vs-inference semantics, redaction and incident/STOP path.

- **WBS_ID:** INF-03
- **PRODUCT_OUTCOME:** O3; monitoring, alerting and secure runtime plan
- **FEATURE_UI:** S10,S12
- **WORK_TYPE:** OBSERVABILITY DESIGN/OPERATIONS
- **PRIORITY:** P2
- **DELIVERABLE:** Define monitoring/alert thresholds, freshness, ownership, health-vs-inference semantics, redaction and incident/STOP path.
- **REQUIRED_SKILL_IDS:** K-VPS,K-OBS,K-SEC,K-API
- **MINIMUM_TOOL_CAPABILITY:** Architecture now; future metrics collector/dashboard/alert route in staging.
- **PRIMARY_OWNER_CANDIDATE:** Coordinator
- **AGENT_CANDIDATES:** Coordinator (design only); Hostinger Agent (future operations only after A0 resume and task ACK)
- **CONTRIBUTORS:** Hostinger Agent is not an active contributor while paused; future operational specialist only after separate resume/ACK
- **PREDECESSORS:** INF-01; INF-02 before production recovery claims.
- **ENVIRONMENT_DATA_ACCESS:** Design docs; future staging runtime.
- **RISK_COST_STOP:** Hostinger paused; recurring cost UNKNOWN. STOP before opening ports/public endpoints or external alerts.
- **ACCEPTANCE:** Runbook identifies signal/source/freshness/threshold/route/owner/escalation/recovery; synthetic fault test before live claims.
- **EVIDENCE_PROVENANCE:** A1 S-OBS-STACK candidate; Work stale/UNKNOWN UI findings.
- **STATUS:** DESIGN_CAN_PROCEED / LIVE_INFRA_HOLD.
- **TARGET_ROADMAP:** program/roadmaps/coordinator.md


### INF-04 — Demonstrate minimal safe workflow, durable state, retry/recovery and observability in isolated environment; n8n is runtime, not Agent.

- **WBS_ID:** INF-04
- **PRODUCT_OUTCOME:** O2,O3; n8n integration and recoverability
- **FEATURE_UI:** S03,S06,S10
- **WORK_TYPE:** INTEGRATION/RUNTIME
- **PRIORITY:** P2
- **DELIVERABLE:** Demonstrate minimal safe workflow, durable state, retry/recovery and observability in isolated environment; n8n is runtime, not Agent.
- **REQUIRED_SKILL_IDS:** K-VPS,K-N8N,K-API,K-TEST,K-SEC,K-OBS
- **MINIMUM_TOOL_CAPABILITY:** n8n sandbox, database, workflow export/import, signed webhook, synthetic trigger and logs.
- **PRIMARY_OWNER_CANDIDATE:** Hostinger proposed infra owner (paused); A1 schema support
- **AGENT_CANDIDATES:** Hostinger Agent (PAUSED)
- **CONTRIBUTORS:** A1 (schema consultant only)
- **PREDECESSORS:** INF-02,INF-03,G2-02.
- **ENVIRONMENT_DATA_ACCESS:** Isolated non-production; synthetic data.
- **RISK_COST_STOP:** Hostinger paused; n8n live state and cost UNKNOWN. STOP on production webhook, paid API or untested retry.
- **ACCEPTANCE:** Synthetic workflow with dedupe, timeout, retry, STOP, restore and E2E evidence; no 24/7 claim without scheduler/alert evidence.
- **EVIDENCE_PROVENANCE:** A1 Registry; Work report; historical n8n inventory.
- **STATUS:** HOLD_PAUSED_HOSTINGER / NOT_AUTHORIZED.
- **TARGET_ROADMAP:** No active roadmap until resume and ACK


### UI-01 — Build interactive sandbox prototype from A2 spec with source-linked tasks, roadmaps, skills, approvals, evidence and mobile layouts.

- **WBS_ID:** UI-01
- **PRODUCT_OUTCOME:** O1,O2,O3; Operator Console prototype
- **FEATURE_UI:** S01–S12; J01–J05
- **WORK_TYPE:** UI BUILD/PROTOTYPE
- **PRIORITY:** P1
- **DELIVERABLE:** Build interactive sandbox prototype from A2 spec with source-linked tasks, roadmaps, skills, approvals, evidence and mobile layouts.
- **REQUIRED_SKILL_IDS:** K-UX,K-BROW,K-PY,K-TEST,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** Work Linux/browser or approved local UI runtime; synthetic fixtures; future Playwright/axe only if installed/approved.
- **PRIMARY_OWNER_CANDIDATE:** Work proposed builder; A2 product input; A1 independent code QA
- **AGENT_CANDIDATES:** Work
- **CONTRIBUTORS:** A2 (product input); A1 (technical consultant/reviewer)
- **PREDECESSORS:** G0-02,G2-02,G2-03.
- **ENVIRONMENT_DATA_ACCESS:** Offline/mock or isolated sandbox; no live provider data.
- **RISK_COST_STOP:** Product build not authorized by design gate; tool/CI cost UNKNOWN. STOP before external writes, live data or deployment.
- **ACCEPTANCE:** All 12 screens represented; all loading/empty/error/UNKNOWN/offline/403/409/timeout/mobile states; run T-cases only after build approval.
- **EVIDENCE_PROVENANCE:** A2 PR44; Work PR16 DOM contract is historical fixture, not prototype; S-UX-E2E candidate.
- **STATUS:** HOLD_PRODUCT_BUILD; planned only.
- **TARGET_ROADMAP:** program/roadmaps/work.md


### UI-02 — Connect approved UI to durable task/evidence state, server RBAC/ABAC, approval ledger, freshness and scoped integrations.

- **WBS_ID:** UI-02
- **PRODUCT_OUTCOME:** O1,O2,O3; durable state, permissions and approvals integration
- **FEATURE_UI:** S01–S10,S12
- **WORK_TYPE:** BACKEND/API INTEGRATION
- **PRIORITY:** P1
- **DELIVERABLE:** Connect approved UI to durable task/evidence state, server RBAC/ABAC, approval ledger, freshness and scoped integrations.
- **REQUIRED_SKILL_IDS:** K-UX,K-API,K-TEST,K-SEC,K-SCHEMA,K-GIT
- **MINIMUM_TOOL_CAPABILITY:** Authenticated backend/API, database, test identity provider, migrations, audit and negative auth tests.
- **PRIMARY_OWNER_CANDIDATE:** Work proposed integrator; A1 schema support; Coordinator policy
- **AGENT_CANDIDATES:** Work
- **CONTRIBUTORS:** A1 (schema consultant); Coordinator (policy input)
- **PREDECESSORS:** UI-01,G2-02,G2-03,INF-03.
- **ENVIRONMENT_DATA_ACCESS:** Sandbox first, synthetic data.
- **RISK_COST_STOP:** RBAC/live integration UNKNOWN; costs UNKNOWN. STOP on privilege bypass, unbounded spend or missing rollback.
- **ACCEPTANCE:** Server rejects unauthorized action independent of UI; expiry/revocation/source drift fail closed; audit/readback and rollback verified in sandbox.
- **EVIDENCE_PROVENANCE:** A2 T07,T12–T16,T21,T23; Work RBAC UNKNOWN; S-AGENT-CONTROL not installed.
- **STATUS:** HOLD_PRODUCT_BUILD / live RBAC UNKNOWN.
- **TARGET_ROADMAP:** program/roadmaps/work.md


### CTRL-01 — After a supported channel is verified, prove two consenting test sessions receive unique synthetic work, issue real ACK and return exact-attempt receipts.

- **WBS_ID:** CTRL-01
- **PRODUCT_OUTCOME:** O2,O3; two-session dispatch/ACK/receipt proof
- **FEATURE_UI:** S03,S04,S06,S08
- **WORK_TYPE:** CROSS-SESSION SPIKE
- **PRIORITY:** P2
- **DELIVERABLE:** After a supported channel is verified, prove two consenting test sessions receive unique synthetic work, issue real ACK and return exact-attempt receipts.
- **REQUIRED_SKILL_IDS:** K-BROW,K-AUTO,K-TEST,K-SEC,K-API
- **MINIMUM_TOOL_CAPABILITY:** Verified destination and authorized browser/API adapter, isolated state store, two synthetic sessions, kill switch.
- **PRIMARY_OWNER_CANDIDATE:** Work research/test owner; Coordinator owns handoff semantics
- **AGENT_CANDIDATES:** Work
- **CONTRIBUTORS:** Coordinator (handoff semantics only)
- **PREDECESSORS:** G2-01,G2-02,G3-03; separate A0 test authorization.
- **ENVIRONMENT_DATA_ACCESS:** Isolated test sessions only; no business payload.
- **RISK_COST_STOP:** Channel UNKNOWN; no auto-dispatch authorization. STOP if destination, identity, consent, receipt, cost or kill switch unverified.
- **ACCEPTANCE:** Correct/wrong session tests, actual recipient ACK, completion correlation, duplicate idempotency, timeout UNKNOWN and STOP; source/time evidence.
- **EVIDENCE_PROVENANCE:** Work DGN-FEASIBILITY; S-AGENT-CONTROL candidate only.
- **STATUS:** BLOCKED_CHANNEL_UNKNOWN / NOT_DISPATCHED; manual owner-forward fallback.
- **TARGET_ROADMAP:** program/roadmaps/work.md


### UC01-01 — Audit authorized WP product/page/post content, metadata, internal links and errors; output source-linked findings and UNKNOWN/errors.

- **WBS_ID:** UC01-01
- **PRODUCT_OUTCOME:** O4,O5; WordPress/Woo content and SEO audit
- **FEATURE_UI:** S11
- **WORK_TYPE:** READ-ONLY BUSINESS AUDIT
- **PRIORITY:** P1
- **DELIVERABLE:** Audit authorized WP product/page/post content, metadata, internal links and errors; output source-linked findings and UNKNOWN/errors.
- **REQUIRED_SKILL_IDS:** K-WP,K-SEO,K-DATA,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** Verified WordPress connector/API read-only scope or sanitized export; source snapshot.
- **PRIMARY_OWNER_CANDIDATE:** A2 business owner candidate; Work QA
- **AGENT_CANDIDATES:** A2
- **CONTRIBUTORS:** Work (independent reviewer)
- **PREDECESSORS:** G0-01; separate read-only account authorization.
- **ENVIRONMENT_DATA_ACCESS:** Staging or authorized read-only source; sanitize identifiers.
- **RISK_COST_STOP:** A2 live connector/scope UNKNOWN. STOP if only write/admin scope or PII exposure.
- **ACCEPTANCE:** Repeatable agreed object set; each finding includes source/time/field/impact/recommendation/confidence; missing data UNKNOWN; no content changed.
- **EVIDENCE_PROVENANCE:** A2 S11; A1 WP connector visible-unverified; main WBS.
- **STATUS:** HOLD_BUSINESS_PILOT; no live read authorization.
- **TARGET_ROADMAP:** program/roadmaps/a2.md


### UC01-02 — Transform UC01-01 findings into reproducible report/evidence consumed by Console with bounded failures and provenance.

- **WBS_ID:** UC01-02
- **PRODUCT_OUTCOME:** O4,O5; audit pipeline/report and Console consumption
- **FEATURE_UI:** S03,S08,S11
- **WORK_TYPE:** PIPELINE/API/QA
- **PRIORITY:** P1
- **DELIVERABLE:** Transform UC01-01 findings into reproducible report/evidence consumed by Console with bounded failures and provenance.
- **REQUIRED_SKILL_IDS:** K-WP,K-PY,K-API,K-TEST,K-UX,K-DATA
- **MINIMUM_TOOL_CAPABILITY:** Synthetic fixture first; future worker/API with versioned schema and trace.
- **PRIMARY_OWNER_CANDIDATE:** Work pipeline candidate; A2 defines finding acceptance; A1 schema support
- **AGENT_CANDIDATES:** Work
- **CONTRIBUTORS:** A2 (acceptance definition); A1 (schema consultant)
- **PREDECESSORS:** UC01-01,UI-01,G2-02.
- **ENVIRONMENT_DATA_ACCESS:** Offline fixture/sandbox; read-only source only after approval.
- **RISK_COST_STOP:** Live WP/backend scope UNKNOWN; cost UNKNOWN. STOP on writes, missing trace or unbounded retry.
- **ACCEPTANCE:** Input→normalized finding→report→UI trace; malformed/missing source and duplicate tests; independent QA.
- **EVIDENCE_PROVENANCE:** Work feasibility; A2 S11/T15; A1 K-API/K-SCHEMA.
- **STATUS:** HOLD_BUSINESS_PILOT / fixtures only.
- **TARGET_ROADMAP:** program/roadmaps/work.md


### GROW-01 — Establish sourced lead/conversion/spend baseline and attribution limitations; distinguish form, message and qualified lead events.

- **WBS_ID:** GROW-01
- **PRODUCT_OUTCOME:** O4,O5; Ads/GA4/UTM attribution baseline
- **FEATURE_UI:** S09,S11
- **WORK_TYPE:** READ-ONLY ANALYTICS
- **PRIORITY:** P1
- **DELIVERABLE:** Establish sourced lead/conversion/spend baseline and attribution limitations; distinguish form, message and qualified lead events.
- **REQUIRED_SKILL_IDS:** K-ADS,K-DATA,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** Google Ads/GA4 read-only connector/API, consent and metric dictionary, bounded date range.
- **PRIMARY_OWNER_CANDIDATE:** A2 business analytics owner candidate; Work data QA
- **AGENT_CANDIDATES:** A2
- **CONTRIBUTORS:** Work (data QA only)
- **PREDECESSORS:** G0-01; consent and read-only access.
- **ENVIRONMENT_DATA_ACCESS:** Authorized aggregate reporting only; no campaign mutation.
- **RISK_COST_STOP:** Connector identity/scope/consent/cost UNKNOWN. STOP before bid/budget changes or customer-level export.
- **ACCEPTANCE:** Reconcile source totals/time zone/windows/event definitions/UTM gaps; missing data remains UNKNOWN; no invented baseline.
- **EVIDENCE_PROVENANCE:** A2 KPI contract; A1 S-A1-MARKETING untested; S-ADS-GA4 candidate.
- **STATUS:** HOLD_ANALYTICS_READ; no Ads writes.
- **TARGET_ROADMAP:** program/roadmaps/a2.md


### GROW-02 — Design and later validate draft→review→approval→publish with rights, asset provenance, consent and human approval.

- **WBS_ID:** GROW-02
- **PRODUCT_OUTCOME:** O4,O5; media/social editorial workflow
- **FEATURE_UI:** S11
- **WORK_TYPE:** CONTENT WORKFLOW DESIGN/LATER BUILD
- **PRIORITY:** P2
- **DELIVERABLE:** Design and later validate draft→review→approval→publish with rights, asset provenance, consent and human approval.
- **REQUIRED_SKILL_IDS:** K-MEDIA,K-DOC,K-UX,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** Asset library/source links, licensed/consented assets, draft sandbox.
- **PRIMARY_OWNER_CANDIDATE:** A2 content workflow owner candidate; Work UX review
- **AGENT_CANDIDATES:** A2
- **CONTRIBUTORS:** Work (UX review only)
- **PREDECESSORS:** G0-01,G2-03.
- **ENVIRONMENT_DATA_ACCESS:** Draft-only design; render/publish are separate paid/rights gates.
- **RISK_COST_STOP:** Credits/subscriptions/publishing rights UNKNOWN. STOP before paid generation, unconsented voice/image or publication.
- **ACCEPTANCE:** Each asset has source/license/consent, reviewer/approval, cost estimate/cap, publish receipt and rollback; design tests only until build release.
- **EVIDENCE_PROVENANCE:** A2 S11; A1 S-MEDIA-GEN candidate.
- **STATUS:** HOLD_MEDIA_EXECUTION; design only.
- **TARGET_ROADMAP:** program/roadmaps/a2.md


### GROW-03 — Aggregate validated business/operational metrics with provenance, freshness, currency, cost state and UNKNOWN semantics.

- **WBS_ID:** GROW-03
- **PRODUCT_OUTCOME:** O4,O5; cross-channel reporting, quality/freshness and costs
- **FEATURE_UI:** S01,S09,S10,S11
- **WORK_TYPE:** DATA INTEGRATION/DASHBOARD
- **PRIORITY:** P2
- **DELIVERABLE:** Aggregate validated business/operational metrics with provenance, freshness, currency, cost state and UNKNOWN semantics.
- **REQUIRED_SKILL_IDS:** K-DATA,K-ADS,K-API,K-UX,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** Read-only connectors/versioned imports, data dictionary, time-zone alignment, freshness monitor and fixtures.
- **PRIMARY_OWNER_CANDIDATE:** Work integration candidate; A2 owns KPI definitions; Coordinator policy
- **AGENT_CANDIDATES:** Work
- **CONTRIBUTORS:** A2 (KPI definitions); Coordinator (policy)
- **PREDECESSORS:** GROW-01,UI-02,G2-02.
- **ENVIRONMENT_DATA_ACCESS:** Mock fixtures first; later authorized read-only connectors.
- **RISK_COST_STOP:** Live sources/billing APIs UNKNOWN; subscription/compute cost UNKNOWN. STOP if UNKNOWN becomes zero or data crosses tenant.
- **ACCEPTANCE:** Every metric has source, observed/collected time, window, currency/unit, formula/version/confidence; stale/missing shows UNKNOWN; reconcile to provider.
- **EVIDENCE_PROVENANCE:** A2 KPI contracts; Work Evidence/Costs; A1 K-DATA/K-ADS.
- **STATUS:** HOLD_REPORTING_INTEGRATION; mock design only.
- **TARGET_ROADMAP:** program/roadmaps/work.md


### REL-01 — Collect complete Agent roadmap handoffs, verify consistency/evidence/HOLD boundaries and prepare one integrated verdict.

- **WBS_ID:** REL-01
- **PRODUCT_OUTCOME:** O1–O5; integrated design/release roadmap review
- **FEATURE_UI:** S01–S12; DGN-1..4
- **WORK_TYPE:** INDEPENDENT QA/RELEASE DESIGN
- **PRIORITY:** P0
- **DELIVERABLE:** Collect complete Agent roadmap handoffs, verify consistency/evidence/HOLD boundaries and prepare one integrated verdict.
- **REQUIRED_SKILL_IDS:** K-QA,K-SEC,K-GIT,K-DATA,K-SCHEMA
- **MINIMUM_TOOL_CAPABILITY:** GitHub source SHA/diff/readback; reviewer not author; package matrix; no deployment.
- **PRIMARY_OWNER_CANDIDATE:** Coordinator integration owner; A0 Assistant independent reviewer (self-session capability confirmation required)
- **AGENT_CANDIDATES:** Coordinator
- **CONTRIBUTORS:** A0 Assistant (independent reviewer, not execution owner)
- **PREDECESSORS:** DGN-1,DGN-2,DGN-3,DGN-4; roadmap-level handoffs or justified partial blockers.
- **ENVIRONMENT_DATA_ACCESS:** Design branches/PRs; read-only evidence.
- **RISK_COST_STOP:** Coordinator cannot self-review as independent. No merge authority. A0 Assistant live session evidence not yet available.
- **ACCEPTANCE:** Eight package properties: UI→WBS, skill evidence, one owner/fallback, actionable roadmaps, evidence/SHA/time, no conflicts, no unauthorized effects, clear next action/STOP.
- **EVIDENCE_PROVENANCE:** A0 directive; PR44/46; Work report; Agent roadmap receipts.
- **STATUS:** PLANNED; package gate not met.
- **TARGET_ROADMAP:** program/roadmaps/coordinator.md


### REL-02 — A0 reviews integrated package and decides PASS/PASS_WITH_CONDITIONS/FAIL; separately decides if/when build or operations are authorized.

- **WBS_ID:** REL-02
- **PRODUCT_OUTCOME:** O1–O5; A0 portfolio acceptance and release decision
- **FEATURE_UI:** All product outcomes / DGN package
- **WORK_TYPE:** OWNER DECISION/APPROVAL
- **PRIORITY:** P0
- **DELIVERABLE:** A0 reviews integrated package and decides PASS/PASS_WITH_CONDITIONS/FAIL; separately decides if/when build or operations are authorized.
- **REQUIRED_SKILL_IDS:** K-DOC,K-SEC (decision authority, not technical execution)
- **MINIMUM_TOOL_CAPABILITY:** Authenticated A0 decision tied to exact candidate/tree SHA, scope, conditions and expiry.
- **PRIMARY_OWNER_CANDIDATE:** A0 sole decision owner
- **AGENT_CANDIDATES:** None (A0 is decision authority, not Agent)
- **CONTRIBUTORS:** None
- **PREDECESSORS:** REL-01.
- **ENVIRONMENT_DATA_ACCESS:** Owner-controlled decision channel.
- **RISK_COST_STOP:** No Agent may impersonate A0 or infer approval from silence, PR, mergeability or author status.
- **ACCEPTANCE:** Immutable verdict tied to exact source SHAs and decision scope; execution remains HOLD absent separate authorization.
- **EVIDENCE_PROVENANCE:** A0 directive PR43; future package handoff.
- **STATUS:** NOT_STARTED / RESERVED_TO_A0.
- **TARGET_ROADMAP:** A0 owner decision


### G3-A1 — Sample A1 directory claims against reproducible evidence; flag unsupported current-session/permission claims without repeating inventory.

- **WBS_ID:** G3-A1
- **PRODUCT_OUTCOME:** O2,O3; independent audit of capability/data claims
- **FEATURE_UI:** S05,S06,S08
- **WORK_TYPE:** INDEPENDENT CAPABILITY QA
- **PRIORITY:** P1
- **DELIVERABLE:** Sample A1 directory claims against reproducible evidence; flag unsupported current-session/permission claims without repeating inventory.
- **REQUIRED_SKILL_IDS:** K-GIT,K-TEST,K-QA,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** Pinned GitHub blobs and targeted evidence checks; read-only.
- **PRIMARY_OWNER_CANDIDATE:** Work (independent QA owner candidate)
- **AGENT_CANDIDATES:** Work only, subject to task ACK and current session capability
- **CONTRIBUTORS:** A1 is source author/factual respondent only; A0 Assistant is package reviewer only, not execution owner
- **PREDECESSORS:** G1-03,G3-01.
- **ENVIRONMENT_DATA_ACCESS:** Read-only PR/source review.
- **RISK_COST_STOP:** A1 cannot self-certify; Work DGN feasibility report is not automatically QA of PR46; separate ACK required.
- **ACCEPTANCE:** Sampled claims have verdict/source/time/confidence; no other-Agent VERIFIED without own-session receipt.
- **EVIDENCE_PROVENANCE:** PR46; A1 roadmap says other-Agent checks external pending.
- **STATUS:** PLANNED_NOT_ACKED; may be included in package assurance.
- **TARGET_ROADMAP:** program/roadmaps/work.md


### QA-U01 — Sample A2 read-only WP findings for false positives, unsupported inference and reproducibility.

- **WBS_ID:** QA-U01
- **PRODUCT_OUTCOME:** O4,O5; independent sample of WordPress audit
- **FEATURE_UI:** S11
- **WORK_TYPE:** BUSINESS AUDIT QA
- **PRIORITY:** P1
- **DELIVERABLE:** Sample A2 read-only WP findings for false positives, unsupported inference and reproducibility.
- **REQUIRED_SKILL_IDS:** K-QA,K-SEO,K-DATA,K-WP
- **MINIMUM_TOOL_CAPABILITY:** Sanitized source snapshot or authorized read-only WP access; sampling protocol.
- **PRIMARY_OWNER_CANDIDATE:** A1 QA candidate; Work alternative if independent of author
- **AGENT_CANDIDATES:** A1
- **CONTRIBUTORS:** Work (independent reviewer only if separately scoped)
- **PREDECESSORS:** UC01-01.
- **ENVIRONMENT_DATA_ACCESS:** Read-only dataset; no write access.
- **RISK_COST_STOP:** No audit exists until UC01-01 authorized/completed; A1 WP connector visible-unverified.
- **ACCEPTANCE:** Sample findings against source fields; precision/false positives/missing data and reproducibility.
- **EVIDENCE_PROVENANCE:** A2 UC01-01; A1 Registry; no live WP scope verified.
- **STATUS:** HOLD_DEPENDENCY_UC01_01; not dispatched.
- **TARGET_ROADMAP:** program/roadmaps/a1.md


### EXIST-QA31 — Preserve already-assigned PR31 Work QA history; no recreation/re-run absent explicit change trigger.

- **WBS_ID:** EXIST-QA31
- **PRODUCT_OUTCOME:** Governance; PR31 cost-first/progress QA
- **FEATURE_UI:** Historical PR31 source
- **WORK_TYPE:** HISTORICAL INDEPENDENT QA
- **PRIORITY:** P0
- **DELIVERABLE:** Preserve already-assigned PR31 Work QA history; no recreation/re-run absent explicit change trigger.
- **REQUIRED_SKILL_IDS:** K-QA,K-GIT,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** Pinned PR31 diff/comments and exact historical QA artifact.
- **PRIMARY_OWNER_CANDIDATE:** Work historical owner; Coordinator records lineage
- **AGENT_CANDIDATES:** Work (historical)
- **CONTRIBUTORS:** Coordinator (lineage only)
- **PREDECESSORS:** PR31 pinned assignment.
- **ENVIRONMENT_DATA_ACCESS:** Read-only GitHub evidence.
- **RISK_COST_STOP:** No new task ACK or duplicate QA; no repeat of historical PASS without material change.
- **ACCEPTANCE:** Exact prior review comment/commit/verdict/scope linked; otherwise UNKNOWN.
- **EVIDENCE_PROVENANCE:** PR31/PR42/PR43 review history.
- **STATUS:** HISTORICAL_ASSIGNMENT_PRESERVED; verify only if needed.
- **TARGET_ROADMAP:** program/roadmaps/work.md history


### SEC-H — Prepare risk-gated hardening plan for SSH exposure, ports, firewall, backup and recovery; no live mutation during design.

- **WBS_ID:** SEC-H
- **PRODUCT_OUTCOME:** O3; SSH/network/firewall/backup security hardening
- **FEATURE_UI:** S07,S10,S12
- **WORK_TYPE:** SECURITY DESIGN/OPERATIONS
- **PRIORITY:** P2
- **DELIVERABLE:** Prepare risk-gated hardening plan for SSH exposure, ports, firewall, backup and recovery; no live mutation during design.
- **REQUIRED_SKILL_IDS:** K-SEC,K-VPS,K-BACKUP,K-OBS
- **MINIMUM_TOOL_CAPABILITY:** Provider/hPanel/VPS read-only topology; official docs; isolated validation later.
- **PRIMARY_OWNER_CANDIDATE:** Hostinger proposed specialist (paused); A1 static runbook fallback
- **AGENT_CANDIDATES:** Hostinger Agent (PAUSED)
- **CONTRIBUTORS:** A1 (static runbook consultant only)
- **PREDECESSORS:** INF-01.
- **ENVIRONMENT_DATA_ACCESS:** Redacted topology; staging first.
- **RISK_COST_STOP:** Hostinger PAUSED; no SSH/firewall/DNS changes; STOP absent verified topology, backup and rollback.
- **ACCEPTANCE:** Threat/risk register, least privilege plan, staged tests, rollback and owner approvals; implementation separately gated.
- **EVIDENCE_PROVENANCE:** Main Hostinger pause rules; historical infra inventory.
- **STATUS:** HOLD_PAUSED_HOSTINGER; no execution.
- **TARGET_ROADMAP:** No active roadmap until A0 resume and Hostinger ACK


### WP-H — Diagnose reproducible WP HTTP500 using logs/health/bounded request evidence; do not alter site/plugin state.

- **WBS_ID:** WP-H
- **PRODUCT_OUTCOME:** O4; safe diagnosis of WordPress HTTP500
- **FEATURE_UI:** S10,S11
- **WORK_TYPE:** INCIDENT DIAGNOSIS/READ-ONLY
- **PRIORITY:** P1
- **DELIVERABLE:** Diagnose reproducible WP HTTP500 using logs/health/bounded request evidence; do not alter site/plugin state.
- **REQUIRED_SKILL_IDS:** K-VPS,K-WP,K-OBS,K-SEC
- **MINIMUM_TOOL_CAPABILITY:** Read-only hPanel/web logs or sanitized trace; staging reproduction if available.
- **PRIMARY_OWNER_CANDIDATE:** Hostinger proposed specialist (paused); Coordinator/A1 static review only
- **AGENT_CANDIDATES:** Hostinger Agent (PAUSED)
- **CONTRIBUTORS:** A1 (static evidence consultant only)
- **PREDECESSORS:** INF-01; existing incident evidence; UC01-01 is not a live-access grant.
- **ENVIRONMENT_DATA_ACCESS:** Read-only diagnostic scope; redact logs.
- **RISK_COST_STOP:** Hostinger PAUSED; no production restart/plugin change. STOP if secrets/PII exposed or only write credential exists.
- **ACCEPTANCE:** Timestamped request correlated with server/PHP/WP evidence; bounded root-cause hypothesis; UNKNOWN distinguished from proven cause.
- **EVIDENCE_PROVENANCE:** Historical WP/hosting evidence; main Hostinger pause rule.
- **STATUS:** HOLD_PAUSED_HOSTINGER; no new live diagnosis.
- **TARGET_ROADMAP:** No active roadmap until A0 resume and Hostinger ACK


## Product/UI coverage matrix

| Screen / journey | WBS coverage | Acceptance coverage |
|---|---|---|
| S01 Overview | G0-03,UI-01,UI-02,GROW-03 | Dashboard, next action, source freshness, costs |
| S02 Goals | G0-01,G0-03 | Charter, KPI contracts, goal scope and approval version |
| S03 Tasks & Dependencies | G2-01,G2-02,G3-03 | Lifecycle, dependency DAG, event/receipt store |
| S04 Agent Roadmaps | G2-01,G3-03 | Sole-writer roadmap, self-progress, roadmap acceptance |
| S05 Skills & Candidates | G3-01,G3-02,G3-A1 | Skill directory, evidence freshness, install boundary |
| S06 Assignment & Sessions | G3-02,G3-03,CTRL-01 | Owner matching, real handoff/ACK, gated adapter |
| S07 Approvals & STOP | G2-03,SEC-H,REL-02 | Approval lifecycle, STOP and A0 authority |
| S08 Evidence & Status | G1-03,G2-02,G3-A1,QA-U01,REL-01 | Provenance, confidence, UNKNOWN and QA |
| S09 Costs | GROW-01,GROW-03,G0-01 | KPI/cost provenance, estimate vs billed vs UNKNOWN |
| S10 Integrations & Health | INF-01,INF-03,INF-04,UI-02,WP-H | Connector metadata, health freshness, runtime |
| S11 Business Modules | UC01-01,UC01-02,GROW-01,GROW-02,GROW-03,WP-H,QA-U01 | WP/SEO, Ads/GA4, media, reporting, audit |
| S12 Access & Settings | G2-03,UI-02,INF-02,SEC-H | Backend authorization, retention, audit and restore |
| J01–J05 and T01–T24 | G0-02,G2-01,G2-02,G2-03,UI-01,UI-02,CTRL-01,REL-01 | End-to-end trace; T01–T24 remain DESIGNED_NOT_RUN until build permission |

**Coverage decision:** no new WBS ID is justified at this point. KPI provenance maps to G0-01/GROW-01/GROW-03; authenticated receipt/event storage to G2-02; backend RBAC and approval enforcement to G2-03/UI-02; accessibility verification to UI-01 and cross-cutting UI acceptance; revocation/uncertainty reconciliation to G2-03/G2-02. If later evidence proves a distinct deliverable cannot fit an existing row without changing its acceptance, Coordinator may propose a new ID with a documented gap analysis. Do not create IDs solely to split administrative tasks.

## Dependency graph and critical path

**Core design/roadmap path:** G0-01 → G0-02 → G0-03 → G2-01 → G2-02 → G3-02 → G3-03 → REL-01 → REL-02. G3-01 (DGN-2) is author-complete and feeds G3-02/G3-03. G2-03 is a parallel P0 control lane after G2-01 and a prerequisite for UI-02 and REL-01.

**Future UI path:** G0-02 + G2-02 + G2-03 → UI-01 → UI-02 → UC01-02 / GROW-03.

**Business paths after separate release:** G0-01 + authorized read-only source → UC01-01 → QA-U01 + UC01-02; G0-01 + consent/source access → GROW-01 → GROW-03; G0-01 + G2-03 → GROW-02.

**Infrastructure path:** INF-01 → INF-02 and INF-03 in parallel → INF-04; SEC-H follows INF-01. WP-H requires authorized read-only diagnostics and INF-01, not WordPress mutation.

**Session controller:** G2-01 + G2-02 + G3-03 + verified supported channel + separate A0 test authority → CTRL-01. Without channel, status stays BLOCKED_CHANNEL_UNKNOWN and owner-forward remains fallback.

**Historical lanes:** G1-01→G1-02→G1-03→G1-04 and EXIST-QA31 are preserved; no rerun absent change trigger. G3-A1 samples G3-01 only when separately assigned. REL-02 is always A0's decision.

**Critical path for design package:** DGN-1 + DGN-2 → G0-03/G2-01/G2-03 → G2-02/G3-02/G3-03 → row-level DGN-4 → REL-01 → REL-02. Cross-session controller, live RBAC, live Ads/WP and Hostinger infrastructure are not design-critical-path blockers.

## Parallel lanes and HOLD controls

- **Can proceed now:** Coordinator C-D2/C-D3/C-D4 design and source reconciliation. No repeat of A1/A2/Work completed research.
- **Parallel only after explicit release:** UI-01 prototype and read-only WP audit may proceed independently after task-specific ACK and scope; Ads read-only baseline requires consent; infrastructure diagnostics require A0 resume and Hostinger ACK.
- **HOLD:** UI build/deploy, M1 business pilot, WP/Woo writes, Ads bid/budget changes, media render/publish, VPS/production, paid inference, Codex spend, Hermes new tasks, Hostinger tasks while paused, autonomous dispatcher and merge.
- All future owner fields are PROPOSED. SENT/ACKNOWLEDGED/IN_PROGRESS require actual authenticated handoff/recipient evidence.

## DGN-3 design completeness checks

- [x] All 32 original WBS IDs retained exactly once; no new ID without gap.
- [x] Every row contains all 18 canonical fields, with one primary owner candidate, separate executor candidates and non-owner contributors.
- [x] S01–S12 and J01–J05 mapped; T01–T24 remain DESIGN_ONLY.
- [x] All 20 original WBS K-skill IDs resolve to A1's canonical registry.
- [x] KNG/PR31 evidence preserved; HOLD not activated.
- [x] Dependencies, parallel lanes and critical path documented.

**Status:** DGN3_ROW_LEVEL_DESIGN_COMPLETE / AUTHOR_SELF_CHECK_ONLY / PACKAGE_ACCEPTANCE_PENDING. Candidate branch only; main unchanged. TARGET_ROADMAP identifies intended destination; Agent roadmap mutation belongs to that Agent after real ACK.
