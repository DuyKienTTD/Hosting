# Skill-linked master work breakdown (candidate)

Status: PLANNED; table is an actionable **program backlog** not claims of work completed. Authoritative historical evidence remains in existing PRs/reports. Date: 2026-11-23.

Skill IDs:
K-GIT GitHub branch/diff/PR; K-DOC structured writing; K-DATA data analysis/SQL; K-PY Python/JS scripting; K-SCHEMA YAML/JSON validation; K-SEC security/privacy; K-UX UI/interaction/accessibility; K-BROW browser/Computer Use; K-WP WordPress/JETPACK/Woo; K-SEO SEO/content; K-ADS GA4/Google Ads/UTM; K-MEDIA Canva/HeyGen/Kling/ElevenLabs/vidIQ; K-API connector/API; K-TEST automated/integration test; K-VPS Hostinger VPS/Docker/network; K-BACKUP backup/restore; K-OBS metrics/monitoring; K-N8N n8n/queues; K-QA independent validation; K-AUTO agent session lifecycle. Evidence of skill vs `INSTALLABLE` candidates in [Registry](SKILL_REGISTRY.md).

| WBS ID | Gate | Deliverable / tangible result | Required skills | Lead | Dependencies | Acceptance evidence |
|---|---|---|---|---|---|---|
| G0-01 | G0 | Reconciled product charter with final outcome, personas and business KPIs | K-DOC,K-DATA | A2 | existing PROJECT, ROADMAP | charter & conflicts documented |
| G0-02 | G0 | Operator Console navigation, task/agent/approval UI flows | K-UX,K-DOC | A2 | G0-01 | functional UI spec and acceptance |
| G0-03 | G0 | MVP and roadmap dependencies, distinguish mock vs live | K-DOC,K-SCHEMA | Coordinator | G0-01,G0-02 | milestone gates and paths |
| G1-01 | G1 | Git knowledge inventory, redundant facts and authority map | K-GIT,K-PY,K-DOC | A1 | current repo, PR31 | inventory with counts/source pins |
| G1-02 | G1 | Compact context entry and pilot per-task pack | K-GIT,K-SCHEMA,K-DOC | A1 | G1-01 | linked test case with provenance |
| G1-03 | G1 | Metadata/links/secret/scope validator; checks run offline | K-PY,K-SCHEMA,K-TEST,K-SEC | A1 | G1-02 | passing + negative fixtures and logs |
| G1-04 | G1 | Comprehension/token A/B evaluation, no safety regression | K-QA,K-TEST,K-DATA | Work | G1-02,G1-03 | independent actual metrics/verdict |
| G2-01 | G2 | Roadmap-level autonomous item update + exception contract | K-DOC,K-SCHEMA,K-SEC | Coordinator | G0-03 | no ordinary per-item acceptance |
| G2-02 | G2 | Durable task item/update event schema and repeatable status generation | K-PY,K-SCHEMA,K-GIT | A1 | G2-01,G1-03 | real write/readback and dedupe tests |
| G2-03 | G2 | Risk-based QA and versioned approval/merge protocol | K-SEC,K-QA,K-DOC | Coordinator | G2-01 | targeted policy checks; no gate bypass |
| G3-01 | G3 | Capability/skills including optional installation candidates | K-DOC,K-GIT,K-DATA | A2 | G0-01 | five-agent role rows, provenance |
| G3-02 | G3 | PR portfolio consolidation + dependency routing | K-GIT,K-DATA,K-SCHEMA | Coordinator | G0-03,G1-01 | actionable list with owner/next |
| G3-03 | G3 | Roadmap issuance, per-agent sole writer ownership | K-GIT,K-SCHEMA | Coordinator | G2-01,G3-02 | exact per-agent roadmap/readback |
| INF-01 | Infra | VPS/hosting/WordPress service baseline, risks, health | K-VPS,K-SEC,K-OBS | Hostinger | existing inventory | fresh scoped live read evidence |
| INF-02 | Infra | Backup/restore verified in safe environment | K-VPS,K-BACKUP,K-TEST,K-SEC | Hostinger | INF-01 | restore evidence and rollback |
| INF-03 | Infra | Monitoring, fault alerts and secure runtime plan | K-VPS,K-OBS,K-SEC | Hostinger | INF-01 | live checks scoped + report |
| INF-04 | Infra | Minimal safe n8n integration capability and recoverability | K-VPS,K-N8N,K-API,K-TEST | Hostinger | INF-02,INF-03 | sandbox execution and rollback |
| UI-01 | Product | Operator Console UI prototype connected to representative task schema | K-UX,K-BROW,K-PY | Work | G0-02,G2-02 | real interactive UX and edge cases |
| UI-02 | Product | Operator Console integration with durable task state and approvals | K-UX,K-API,K-TEST,K-SEC | Work | UI-01,G2-02,INF-03 | E2E live/sandbox documented |
| CTRL-01 | Product | Two existing Agent sessions dispatch/ACK/receipt PoC | K-BROW,K-AUTO,K-TEST,K-SEC | Work | G2-01 | synthetic two-session evidence |
| UC01-01 | Business | Bounded WordPress product/page/post content audit | K-WP,K-SEO,K-DATA | A2 | existing authenticated source | repeatable audit + UNKNOWN/errors |
| UC01-02 | Business | Reproducible audit pipeline/report and UX consumption | K-WP,K-PY,K-API,K-TEST | Work | UC01-01,UI-01 | input->output->UI trace, QA |
| GROW-01 | Business | Ads/GA4/UTM lead attribution read-only baseline | K-ADS,K-DATA,K-SEC | A2 | consent/source scoped | proven attribution limitations |
| GROW-02 | Business | Media/social editorial workflow with human approval | K-MEDIA,K-DOC,K-UX,K-SEC | A2 | G0-01 | draft-to-approval demo |
| GROW-03 | Business | Cross-channel dashboard with provenance and costs | K-DATA,K-ADS,K-API,K-UX | Work | GROW-01,UI-02 | validated data freshness/KPI |
| REL-01 | Release | Integrated roadmap review, independent QA and next milestone | K-QA,K-SEC,K-GIT | Coordinator | sufficient gate deliverables | one roadmap-level verdict, no false LIVE |
| REL-02 | Release | Owner portfolio acceptance, scoped live approvals if needed | K-DOC,K-SEC | A0 | REL-01 | explicit decision/event |
 
| G3-A1 | G3 | Check A1 capability and data inventory claims against executed evidence | K-GIT,K-TEST | A1 | G1-03 | source-linked delta with actual checks |
| QA-U01 | G4 | Independently sample A2 WordPress audit, report incorrect inference | K-QA,K-SEO,K-DATA | A1 | UC01-01 | sampled audit evidence and verdict |
| EXIST-QA31 | Existing | Execute already assigned PR31 cost-first/progress independent QA | K-QA,K-GIT,K-SEC | Work | PR31 pinned assignment | one factual verdict, no unrelated rerun |
| SEC-H | Infra | Secure hardening plan for SSH/exposed ports/firewall/backup | K-SEC,K-VPS,K-BACKUP | Hostinger | INF-01 | risk-gated work package with live evidence |
| WP-H | Infra | Diagnose WordPress HTTP500 source as safely reproducible | K-VPS,K-WP,K-OBS | Hostinger | UC01-01 | bounded diagnosis, no site mutation |

## Critical path and parallel work
Start G0-01 (A2), G1-01 (A1), INF-01 (Hostinger), Work current PR31 QA (existing task), all separate write sets. Coordinator develops G2-01 without writing shared PR31 sources. G0-02→UI-01; G1-02/03→G1-04; G2-01→G2-02; UC01-01 may begin from existing authenticated WP baseline without waiting for all governance changes. UI-02, CTRL-01, INF-04 require explicit technical readiness. Don't duplicate already PASS historical tasks.

## Result categories
`DRAFT`/design ≠ `OFFLINE_TESTED` ≠ `SANDBOX_INTEGRATED` ≠ `STAGING_VERIFIED` ≠ `LIVE_VERIFIED` ≠ `ACCEPTED`. Each WBS must cite its actual environment. Do not require management acceptance on every row; independent security/QA controls can be batched at roadmap completion.
