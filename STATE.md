---
id: current-state
type: state
status: release-source-snapshot-external-activation-required
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
---

# Hosting — KNG release-source snapshot (NOT_EFFECTIVE unless verified externally)

This document is an **immutable release-source checkpoint**, not a live VPS, WordPress, n8n, Hermes, Google Ads, or A0 merge-approval observation. Before merge the candidate is NOT_EFFECTIVE; even after merge no authority is inferred until an independently authenticated A0 exact-tree approval and remote main readback. **Full prior PR31 `STATE.md` history preserved verbatim at [immutable PR31 source](https://github.com/DuyKienTTD/Hosting/blob/a770de80a2467ca1789c820b63416209cf53b7d1/STATE.md), Git blob `53d6d79aa6fd9a952ea6ceab8679104da77a597c`.** The earlier main snapshot is at [main source](https://github.com/DuyKienTTD/Hosting/blob/e385c1bea2070973e3007e5717f7e980348d6ab3/STATE.md), blob `c8e8941aa1418f70ed9542063f0485a129739d25`. Neither is a live permission source.

<!-- KNG:BEGIN_GENERATED -->
- **Portfolio priority in this source:** KNG_ONLY.
- **Director:** Chat Điều phối. **Implementation:** A1. **Independent Work source QA:** QA_COMPLETE_NO_NEW_TASK (no new Work ACK).
- **Source baseline main:** `e385c1bea2070973e3007e5717f7e980348d6ab3`. **PR31 historical source:** `a770de80a2467ca1789c820b63416209cf53b7d1`.
- **Release authority:** PREMERGE_CANDIDATE / NOT_EFFECTIVE in this immutable source snapshot. After A0-approved merge, effective authority requires independent exact-tree and remote main readback; this file alone is never proof.
- **Completed source QA:** KNG01_PR42_SOURCE_QA_PASS_WITH_FINAL_GATES at https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7103815886 (historical, not an active task).
- **Permission gates:** production=false, paid=false, merge=false, Codex=false; no automatic dispatch. Non-KNG task activation remains HOLD unless separately authorized.
- **WS-02 historical handoff:** PREPARED_FOR_OWNER_FORWARD; receipt=NONE; new report=NONE.
<!-- KNG:END_GENERATED -->

## Dated current Git evidence, not production telemetry

- [A0 KNG-only direction and Director roadmap](https://github.com/DuyKienTTD/Hosting/pull/39#issuecomment-7097692066); [A0 source migration authority](https://github.com/DuyKienTTD/Hosting/pull/39#issuecomment-7097409581).
- [Historical Work D1 QA](https://github.com/DuyKienTTD/Hosting/pull/40#issuecomment-7098400020) identified four fail-opens (subsequently corrected). [Work PR42 source QA](https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7103815886) completed with final release gates still required. [Director D2 corrective grant](https://github.com/DuyKienTTD/Hosting/pull/40#issuecomment-7098528192) is for isolated candidate only.
- [ENG-01A/S4 Work Linux offline QA](https://github.com/DuyKienTTD/Hosting/pull/21#issuecomment-7094836398) retains its separate source-only/real assembly evidence boundaries. [OPS S2-D3 Hermes QA](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7094319094) is offline PASS_WITH_LIMITS; no production approval implied.
- [PR31 cost-first proposal](https://github.com/DuyKienTTD/Hosting/pull/31) remains unmerged. Every full dated status record and its evidence URLs remain in pinned PR31 STATE above; do not repeat older milestone summaries as current active assignments.
- For VPS history consult [inventory](inventory/current-vps-state.md), [n8n↔Hermes historical audit](reports/2026-11-21-n8n-hermes-integration-audit.md), [security review](reports/2026-11-21-vps-security-review.md) and their timestamps before drawing conclusions.

## Current authority & STOP

[Full AGENTS](AGENTS.md), [operative workflow](rules/AGENT_WORKFLOW.md), [security rules](rules/REPOSITORY_SECURITY.md) remain mandatory complete sources. [CATALOG](CATALOG.yaml) is a machine-validated registry: Agent reads the relevant entries only, not the full file. [Typed KNG routing](program/current.json) is a source snapshot. Its baseline main SHA is historical; after A0-authorized merge the [release-state verifier](program/kng/release_state.py) must independently confirm the exact approved main tree/merge parents and remote readback before treating KNG routing as effective. Task-specific ACK/receipt must be externally evidenced, not inferred from this snapshot. Do not activate GATE B, resume Hostinger, invoke Codex, change production or claim live readiness without separate approvals and fresh verification.
