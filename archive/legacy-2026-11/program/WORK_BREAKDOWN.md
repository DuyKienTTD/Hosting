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
