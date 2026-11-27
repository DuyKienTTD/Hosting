---
id: ttd-a1-gov02-s2-reconciliation-2026-11-23
type: task
status: completed_proposal_pending_coordinator_review
updated_at: 2026-11-23
owner: a1
next_owner: chatgpt
sensitivity: public
approval_scope: safe_offline_analysis_only
---

# A1-GOV02-S2-A — Metadata reconciliation proposal (not Phase B)

**TASK_ACK:** `ACKNOWLEDGED`. **FROM:** ChatGPT Điều phối. **OWNER:** A1 (ChatGPT Standard). **MODE:** EXECUTE read-only source verification + isolated proposal/evidence. **SPEC:** [PR #30 comment #7092666512](https://github.com/DuyKienTTD/Hosting/pull/30#issuecomment-7092666512). **NEXT_OWNER:** ChatGPT Điều phối; Work independent reviewer.

**FIRST_ACTION:** Inspect PR30 Phase A report/evidence and current source PR heads/trees, main governance/security rules, PR31 unmerged §11 cost-first directive and PR32 independent QA assignment.

**BASE_SHA:** `e385c1bea2070973e3007e5717f7e980348d6ab3`.

**READ_SET:** `PROJECT.md`, `AGENTS.md`, `STATE.md`, `CATALOG.yaml`, `rules/AGENT_WORKFLOW.md` (current main + unmerged PR31 §11), `rules/REPOSITORY_SECURITY.md`, `agents/a1.md` PR31; GitHub HEAD/tree and relevant source docs PR #6/#10/#13/#16/#19/#20/#21/#22/#23/#24/#25/#27/#28/#29/#30/#31/#32; Work QA finding/assignments, all 40 ledger rows in PR30 evidence. PR30 head `be48b3e19c6b2deee48f631497feac4be2ef2834`.

**PREVIOUSLY_VERIFIED:** PR28 validator 7/7 author suite historical; PR32 A1 target 7/7 author suite; Work independent PR32 QA **PENDING**; PR24 S2-D1 Hostinger author tests only, Work re-QA **PENDING**. Do not rerun any of them here.

**WRITE_SET:** exactly this new task, `reports/2026-11-23-a1-gov02-s2-reconciliation.md`, `reports/evidence/2026-11-23-a1-gov02-s2-reconciliation.json`, on branch `a1/gov02-s2-metadata-reconciliation-2026-11-23`.

**DO_NOT_TOUCH:** main, PR #6/#10/#13/#24/#28/#30/#31/#32 branches, their source files, `CATALOG.yaml`, `STATE.md`, `CHANGELOG.md`, secrets/OAuth, VPS/KVM2, production, paid service, Actions trigger, merges/rebases, force push.

**INVARIANTS:** no main/production/paid changes, no retroactive approvals, stable IDs/provenance, 40 old rows + new #24 D1/#30/#31/#32/A1 coverage, one future writer per shared file, exact SHA and source scope, no assumed Work PASS.

**TEST_DELTA:** verify current Git tree SHA/path presence and original pinned blob; catalog ID/path uniqueness, source-id collision, main missing paths, PR6/24 drift, PR31 pre-indexed paths; 12 *tabletop* synthetic decision cases in standalone evidence JSON. No runnable validator code written; do not call tabletop cases real code/CI tests.

**STOP:** unknown source/changed ownership/failed pin or unexplained conflict => record `SOURCE_UNAVAILABLE` or `HEAD_DRIFT` and hold affected future metadata application. **ACCEPTANCE:** `A1_GOV02_S2_RECONCILIATION_PLAN_READY_FOR_REVIEW` only after reports/evidence pushed to a new branch, remotely read back, with no shared writes. Phase B stays `NOT_AUTHORIZED`.

**Artifacts:** [Report](../reports/2026-11-23-a1-gov02-s2-reconciliation.md) · [Decision matrix/ledger JSON](../reports/evidence/2026-11-23-a1-gov02-s2-reconciliation.json).