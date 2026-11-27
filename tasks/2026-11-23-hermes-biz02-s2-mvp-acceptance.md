---
id: hermes-biz02-s2-mvp-acceptance-task-2026-11-23
type: task
status: draft_delivered_for_review
updated_at: 2026-11-23
sensitivity: public-redacted
owner: hermes-webui
next_owner: chatgpt
---

# BIZ-02/S2 — ACK và ranh giới nghiệm thu MVP offline

- **ACK:** `EXECUTE BIZ-02/S2`, [PR #23 comment 7091682554](https://github.com/DuyKienTTD/Hosting/pull/23#issuecomment-7091682554); from/next owner ChatGPT Điều phối, Hermes thiết kế acceptance nghiệp vụ.
- **FIRST_ACTION:** fetch `origin/main`, các PR #6/#10/#12/#13/#14/#16/#18/#19/#20/#21/#22/#23; xác minh PR heads và không có branch/path S2 trùng. Sau đó đọc rules, BIZ-02/S1 evidence và báo cáo UX/ENG/OPS liên quan.
- **BASE/RULE:** `origin/main=e385c1bea2070973e3007e5717f7e980348d6ab3`; `AGENTS.md@cb6a8af9`, `AGENT_WORKFLOW.md@69ec0db9`, `REPOSITORY_SECURITY.md@c24d6080`, `STATE.md@c8e8941a`, `CATALOG.yaml@719c9c5d`, `agents/hermes.md@618b8efc` (blob SHA prefix). Full heads của các PR trong JSON evidence.
- **PREVIOUSLY_VERIFIED:** BIZ-01 discovery #12; GROW-01 draft gates #18; BIZ-02/S1 #20 8 use cases/16 KPI/A0 pending; GROW-02A D1 #23 source accepted with limits, independent QA pending. Không chạy lại suite nguồn. UX S2 browser E2E untested; ENG S3/S4 chỉ offline, S4 Linux unrun; OPS #22 chỉ synthetic evaluator.
- **READ_SET:** rules/ownership và PR/evidence trên; **WRITE_SET:** chỉ task này, `reports/2026-11-23-hermes-biz02-s2-mvp-acceptance.md`, `reports/evidence/2026-11-23-hermes-biz02-s2-mvp-scenarios.json`, `sandbox/biz02-mvp-acceptance/validate.py` trên branch `hermes/biz-02-s2-mvp-acceptance-2026-11-23`.
- **INVARIANTS:** 8 UC, 16 KPI giữ nguyên field và `BASELINE_UNKNOWN`; 5 A0 giữ `AWAITING_A0_DECISION`. Không sửa PR nguồn hoặc ưu tiên/ROI. `PASS_TABLETOP` khác kiểm thử UI/browser/backend; local evaluator chỉ so decision table. `MVP_OFFLINE_DEMO` chỉ là khuyến nghị cho owner.
- **STOP:** tài khoản thật, OAuth, PII, API paid, production, publish, tracking/monitoring live, VPS/Docker, đổi quyền hoặc chi phí. Thiếu gate không chặn việc soạn offline; gắn `BLOCKED_*` cho luồng chưa được phép.
- **PASS:** đủ 5 story có actor/precondition/action/UI/mock/receipt/audit/block; ít nhất 10 ca synthetic; trace 8 UC/16 KPI; deterministic check chạy thật; remote SHA/blob readback. **NEXT_OWNER:** ChatGPT Điều phối xem xét và xin A0 quyết định riêng.
