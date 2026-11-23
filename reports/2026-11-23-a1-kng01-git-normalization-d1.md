---
id: report-2026-11-23-a1-kng01-git-normalization-d1
type: report
owner: a1
status: author-candidate-pending-independent-qa-and-shared-writer
updated_at: 2026-11-23
sensitivity: public-redacted
---

# A1 KNG-01 — actual candidate normalization, measurements and unresolved gate

**ACK:** `EXECUTE A1-KNG01-GIT-NORMALIZATION-D1`. **Mode:** offline code + scoped GitHub branch write. **Next owner:** Chat Điều phối → Work independent QA. **Source pins:** main `e385c1bea2070973e3007e5717f7e980348d6ab3`, PR31 `a770de80a2467ca1789c820b63416209cf53b7d1`, PR39 `22d741e3f1dd325540932dea63c3a6da635113c3`.

## Actual applied source (not only documents)

- `program/current.json` is one machine-readable **candidate** priority/owner/permission routing index; never replaces effective main. It now distinguishes Work KNG QA **PENDING_ACK** rather than incorrectly labeling Work generally held. Candidate `program/README.md` and `OPERATING_PROTOCOL.md` point to it while explicitly requiring full five effective main files.
- `program/WORK_BREAKDOWN.md` repairs stale parallel G0/INF/UC01 critical path **while preserving exactly 32/32 WBS IDs, owners, skill IDs, dependencies and acceptance fields** against original PR39 WBS blob `60beab3ad23abf7c67adf288dc0c213c14befcfe`. No non-KNG work marked DONE or ACK.
- `program/roadmaps/a1.md` captures the A1 author implementation state; G1-04 Work independent QA pending and other items held. `program/KNOWLEDGE_OPTIMIZATION.md` replaces vague 30–50% language with a replicable UTF-8 measurement protocol.
- `program/kng/inventory.json`: **12 pinned facts, 5 named contradictions, KEEP 5 / MERGE 4 / ARCHIVE 3 / DELETE 0**. Every formerly referenced historical blob is retained and has recovery ref. ARCHIVE means replacing active claim and retaining old PR/Git provenance; **zero files physically deleted**.
- `program/kng/migration.json` contains **six concrete shared-source migration operations** with old main blob SHA, PR31 conflict review, exact solo-writer prerequisite, and STOP. [Six-file unified patch preview](../program/kng/shared-source-preview.patch) has verified source context anchors against main; **NOT APPLIED** to main/PR31/README/PROJECT/STATE/AGENTS/CATALOG/effective rules. Because PR31 changes five of those six paths, the coordinator's exclusive writer/conflict gate remains real, not a validator failure.
- `program/kng/validate.py` and 18 `unittest` fixtures detect duplicate canonical facts and WBS IDs, invalid SHA, broken scoped Markdown links, missing candidate source, unsafe priority/permissions/authority, false ACK, bad Hostinger state, unsafe delete/recovery and unauthorized shared-file edits. Standard-library-only. Does not validate every historic repository path; focused **candidate** validator and fixtures.

## Actually executed code tests

`python3 -m unittest discover -s program/kng -p test_validate.py -v` on Linux CPython 3.13.5: **18/18 PASS** (1 positive, 17 distinct negative cases), 0 failures/errors, exit 0. The local test harness reconstructs only candidate files and uses placeholders for **unchanged** main docs; Linux direct GitHub clone is DNS blocked. Independent GitHub source blob remote readback is separately verified. **Not** a full Linux repository checkout/CI, not Work QA. WBS preservation was separately checked against exact PR39 source remotely: 32/32 IDs and four existing fields preserved.

## Before/after context read-path size (actual bytes; NOT comprehension)

Both sides include the same **118,810 mandatory UTF-8 bytes** from main `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`. Other path sizes are from pinned original PR39 and the updated candidate. Fixed scenario paths and method are in JSON.

| Task | Before UTF-8 bytes | Candidate after | Bytes saved | File reads before→after |
| --- | ---: | ---: | ---: | ---: |
| Routine content/business | 141,898 | 131,793 | 10,105 | 10→9 |
| Git/code change | 146,743 | 137,099 | 9,644 | 11→11 |
| Security-sensitive VPS request | 139,613 | 133,262 | 6,351 | 10→10 |

No tokenized-count or human task-time claim; this is **fixed-path byte proxy only** and effective main remains unchanged. The short navigation pack does **not** permit skipping mandatory rules. Work must evaluate three source-pinned tasks for objective/owner/safety, wrong-authority, STOP, evidence recall and context load independently before claiming an optimization success.

## Four manual-update scenarios: static point-of-use model, not observed migrations

| Change | Baseline possible duplicate edit targets | Candidate intended canonical targets |
| --- | ---: | ---: |
| Agent role reassignment | 4 | 2 |
| Task status | 4 | 2 |
| Evidence acceptance | 4 | 2 |
| Rule supersession | 5 | 2 |

These counts are **explicitly modeled file/field targets**, not timed edits and not a proven real-main reduction. Exact assumed file lists are in JSON; historic evidence remains append-only. Work should independently audit the model and coordinator must execute authorized shared-source normalization before treating modeled reductions as actual.

## Limits and handoff

**AUTHOR VERDICT:** `KNG01_A1_AUTHOR_CANDIDATE_READY_FOR_INDEPENDENT_QA_WITH_SHARED_SOURCE_GATE`. PR39 original remains unmodified; an isolated A1 branch (descendant of PR39) contains real candidate program file changes. No source deletions, history rewrite, shared metadata edits, PR31/main writes, merge, VPS, production, paid API or Codex. Actual Work independent comprehension and Git release integration **NOT_RUN**. PR31 shared-file writer conflict and A0 final merge gate still block effective main normalization.

**NEXT_OWNER:** Chat Điều phối to dispatch Work once actual session ACK, review source pins and 18 targeted negative tests, blind-score three comprehension situations and four write-amplification scenarios, confirm archive/recovery and safety, then resolve exclusive shared-source integration with PR31. Preserve all old evidence. No KNG accepted/main-effective assertion before that gate.