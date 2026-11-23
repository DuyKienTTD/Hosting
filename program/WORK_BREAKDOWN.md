# Hosting — existing 32-item WBS, priority-gated KNG-only candidate

This file retains the **32 original work IDs and ownership** from PR39 source blob `60beab3ad23abf7c67adf288dc0c213c14befcfe`. The old parallel-start paragraph is superseded by A0 KNG priority. Historical full fields remain recoverable from PR39 HEAD `22d741e3f1dd325540932dea63c3a6da635113c3`; do not infer deleted/finished work. Detailed dependencies, skill IDs, acceptance are historical until coordinator resumes them. Required safety: [Operating protocol](OPERATING_PROTOCOL.md), [current mode](current.json).

| WBS ID | Owner | Required skills | Original dependencies | Acceptance | Current route |
|---|---|---|---|---|---|
| G0-01 | A2 | K-DOC,K-DATA | existing PROJECT, ROADMAP | charter & conflicts documented | ON_HOLD_DEPENDENCY_KNG01 |
| G0-02 | A2 | K-UX,K-DOC | G0-01 | functional UI spec and acceptance | ON_HOLD_DEPENDENCY_KNG01 |
| G0-03 | Coordinator | K-DOC,K-SCHEMA | G0-01,G0-02 | milestone gates and paths | ON_HOLD_DEPENDENCY_KNG01 |
| G1-01 | A1 | K-GIT,K-PY,K-DOC | current repo, PR31 | inventory with counts/source pins | KNG_ONLY |
| G1-02 | A1 | K-GIT,K-SCHEMA,K-DOC | G1-01 | linked test case with provenance | KNG_ONLY |
| G1-03 | A1 | K-PY,K-SCHEMA,K-TEST,K-SEC | G1-02 | passing + negative fixtures and logs | KNG_ONLY |
| G1-04 | Work | K-QA,K-TEST,K-DATA | G1-02,G1-03 | independent actual metrics/verdict | KNG_ONLY_INDEPENDENT_QA_PENDING_ACK |
| G2-01 | Coordinator | K-DOC,K-SCHEMA,K-SEC | G0-03 | no ordinary per-item acceptance | ON_HOLD_DEPENDENCY_KNG01 |
| G2-02 | A1 | K-PY,K-SCHEMA,K-GIT | G2-01,G1-03 | real write/readback and dedupe tests | ON_HOLD_DEPENDENCY_KNG01 |
| G2-03 | Coordinator | K-SEC,K-QA,K-DOC | G2-01 | targeted policy checks; no gate bypass | ON_HOLD_DEPENDENCY_KNG01 |
| G3-01 | A2 | K-DOC,K-GIT,K-DATA | G0-01 | five-agent role rows, provenance | ON_HOLD_DEPENDENCY_KNG01 |
| G3-02 | Coordinator | K-GIT,K-DATA,K-SCHEMA | G0-03,G1-01 | actionable list with owner/next | ON_HOLD_DEPENDENCY_KNG01 |
| G3-03 | Coordinator | K-GIT,K-SCHEMA | G2-01,G3-02 | exact per-agent roadmap/readback | ON_HOLD_DEPENDENCY_KNG01 |
| INF-01 | Hostinger | K-VPS,K-SEC,K-OBS | existing inventory | fresh scoped live read evidence | ON_HOLD_DEPENDENCY_KNG01 |
| INF-02 | Hostinger | K-VPS,K-BACKUP,K-TEST,K-SEC | INF-01 | restore evidence and rollback | ON_HOLD_DEPENDENCY_KNG01 |
| INF-03 | Hostinger | K-VPS,K-OBS,K-SEC | INF-01 | live checks scoped + report | ON_HOLD_DEPENDENCY_KNG01 |
| INF-04 | Hostinger | K-VPS,K-N8N,K-API,K-TEST | INF-02,INF-03 | sandbox execution and rollback | ON_HOLD_DEPENDENCY_KNG01 |
| UI-01 | Work | K-UX,K-BROW,K-PY | G0-02,G2-02 | real interactive UX and edge cases | ON_HOLD_DEPENDENCY_KNG01 |
| UI-02 | Work | K-UX,K-API,K-TEST,K-SEC | UI-01,G2-02,INF-03 | E2E live/sandbox documented | ON_HOLD_DEPENDENCY_KNG01 |
| CTRL-01 | Work | K-BROW,K-AUTO,K-TEST,K-SEC | G2-01 | synthetic two-session evidence | ON_HOLD_DEPENDENCY_KNG01 |
| UC01-01 | A2 | K-WP,K-SEO,K-DATA | existing authenticated source | repeatable audit + UNKNOWN/errors | ON_HOLD_DEPENDENCY_KNG01 |
| UC01-02 | Work | K-WP,K-PY,K-API,K-TEST | UC01-01,UI-01 | input->output->UI trace, QA | ON_HOLD_DEPENDENCY_KNG01 |
| GROW-01 | A2 | K-ADS,K-DATA,K-SEC | consent/source scoped | proven attribution limitations | ON_HOLD_DEPENDENCY_KNG01 |
| GROW-02 | A2 | K-MEDIA,K-DOC,K-UX,K-SEC | G0-01 | draft-to-approval demo | ON_HOLD_DEPENDENCY_KNG01 |
| GROW-03 | Work | K-DATA,K-ADS,K-API,K-UX | GROW-01,UI-02 | validated data freshness/KPI | ON_HOLD_DEPENDENCY_KNG01 |
| REL-01 | Coordinator | K-QA,K-SEC,K-GIT | sufficient gate deliverables | one roadmap-level verdict, no false LIVE | ON_HOLD_DEPENDENCY_KNG01 |
| REL-02 | A0 | K-DOC,K-SEC | REL-01 | explicit decision/event | ON_HOLD_DEPENDENCY_KNG01 |
| G3-A1 | A1 | K-GIT,K-TEST | G1-03 | source-linked delta with actual checks | ON_HOLD_DEPENDENCY_KNG01 |
| QA-U01 | A1 | K-QA,K-SEO,K-DATA | UC01-01 | sampled audit evidence and verdict | ON_HOLD_DEPENDENCY_KNG01 |
| EXIST-QA31 | Work | K-QA,K-GIT,K-SEC | PR31 pinned assignment | one factual verdict, no unrelated rerun | SEPARATE_IN_FLIGHT_OR_PARK_WITH_EVIDENCE |
| SEC-H | Hostinger | K-SEC,K-VPS,K-BACKUP | INF-01 | risk-gated work package with live evidence | ON_HOLD_DEPENDENCY_KNG01 |
| WP-H | Hostinger | K-VPS,K-WP,K-OBS | UC01-01 | bounded diagnosis, no site mutation | ON_HOLD_DEPENDENCY_KNG01 |

**Correction of original critical path:** Start G1-01/02/03 only. Work can run G1-04 independent baseline/final QA when it actually ACKs and its PR31 QA is finished or parked. All other routes remain held until formal KNG acceptance and A0 authorized main integration. Neither `PLANNED` nor a changed table implies another agent received a task.
