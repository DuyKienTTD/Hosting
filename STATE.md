---
id: current-state
type: state
status: release-source-snapshot-external-activation-required
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
---

# HOSTING — current state view (candidate)

MKOE-01 và READSET-OPT-01 đã merge (main `6dea328`). TTD Zalo ACTIVE — phát triển offline theo `HOSTING-ZALO-RESUME-01` (quyết định chủ dự án 26/11/2026); vẫn cấm production, paid API, tài khoản Zalo thật, gửi tin thật, dữ liệu khách thật. Không gọi nhà cung cấp AI thật hoặc mở thêm quyền merge hay quyền Agent. [Kế hoạch](program/zalo-mvp01/PRODUCT_COMPLETION_PLAN.md) · [Theo dõi lỗi vận hành Agent](reports/agent-operational-issues.md). Verify actual authority through [Core](AGENTS.md), [Workflow](rules/AGENT_WORKFLOW.md), task and current A0 decisions. MSC main integration: [receipt](https://github.com/DuyKienTTD/Hosting/pull/60#issuecomment-7140360768). Historical KNG snapshot and prior evidence: [archive](references/history/kng-state-2026-11-23.md). The machine-managed block below is retained solely for KNG compatibility, NOT_EFFECTIVE as independent authority; do not interpret it as current dispatch. [Typed source](program/current.json) and [release verifier](program/kng/release_state.py) remain unchanged. Exact approved tree/parents and authenticated readback required; missing/stale evidence STOP dispatch.

<!-- KNG:BEGIN_GENERATED -->
- **Portfolio priority in this source:** KNG_ONLY.
- **Director:** Chat Điều phối. **Implementation:** A1. **Independent Work source QA:** QA_COMPLETE_NO_NEW_TASK (no new Work ACK).
- **Source baseline main:** `e385c1bea2070973e3007e5717f7e980348d6ab3`. **PR31 historical source:** `a770de80a2467ca1789c820b63416209cf53b7d1`.
- **Release authority:** PREMERGE_CANDIDATE / NOT_EFFECTIVE in this immutable source snapshot. After A0-approved merge, effective authority requires independent exact-tree and remote main readback; this file alone is never proof.
- **Completed source QA:** KNG01_PR42_SOURCE_QA_PASS_WITH_FINAL_GATES at https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7103815886 (historical, not an active task).
- **Permission gates:** production=false, paid=false, merge=false, Codex=false; no automatic dispatch. Non-KNG task activation remains HOLD unless separately authorized.
- **WS-02 historical handoff:** PREPARED_FOR_OWNER_FORWARD; receipt=NONE; new report=NONE.
<!-- KNG:END_GENERATED -->
