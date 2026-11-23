---
id: hermes-grow02a-s1-event-dictionary-task-2026-11-23
type: task
status: draft_delivered_for_review
updated_at: 2026-11-23
sensitivity: public-redacted
owner: hermes-webui-support
next_owner: chatgpt
---

# GROW-02A/S1-SUPPORT — nguồn task hẹp cho bản nháp đo lường

- **ACK:** `EXECUTE GROW-02A/S1-SUPPORT`; [chỉ thị PR #20](https://github.com/DuyKienTTD/Hosting/pull/20#issuecomment-7091269345).
- **Parent portfolio owner:** ChatGPT/Work; Hermes chỉ làm bounded draft/support. A0 là owner quyết định chính sách KPI, attribution và retention. Không sửa GROW-01, BIZ-01, BIZ-02 hay các quyết định A0.
- **FIRST_ACTION:** fetch latest `origin/main`, PR #6/#12/#18/#20 và refs ENG/UX; đọc rules và evidence BIZ-02 16 KPI; kiểm tra branch/path GROW-02A trùng trước khi viết.
- **Read status:** `FULL_READ` cho rules hiện hành ở main `e385c1bea2070973e3007e5717f7e980348d6ab3` và các evidence JSON BIZ-01/GROW-01/BIZ-02 đã ghim SHA. Các report nguồn được dùng với đúng giới hạn offline/draft, không coi là quyền live.

## Trạng thái kế thừa và phạm vi test delta

| Hạng mục | Trạng thái | Bằng chứng | Test delta |
|---|---|---|---|
| BIZ-01 discovery | DONE_REPORTED/ACCEPTED_WITH_LIMITS | PR #12 `8c821bb` | Không khảo sát lại API |
| GROW-01 draft/rights gate | DONE_REPORTED/ACCEPTED_WITH_LIMITS | PR #18 `3c8cb40` | Không rerun fixture |
| BIZ-02 use cases/16 KPI/5 A0 choices | DONE_REPORTED/ACCEPTED_WITH_LIMITS | PR #20 `fcdc0f8` | Chỉ mapping, không sửa definition |
| GROW-02A event contract | NOT_RUN trước lượt này | Không có path/branch trùng sau fetch | Sinh dictionary và kiểm định offline |

- **READ_SET:** PR #20 comment; `AGENTS.md`, `PROJECT.md`, `GOALS_AND_ROADMAP.md`, `rules/AGENT_WORKFLOW.md` §§7–10, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/hermes.md`; refs PR #6/#12/#18/#20/#13/#19/#16.
- **WRITE_SET:** chỉ task này, `reports/2026-11-23-hermes-grow02a-s1-attribution-contract.md`, `reports/evidence/2026-11-23-hermes-grow02a-s1-events-and-tests.json`, `sandbox/grow02a-offline-validator/validate.py` trên branch riêng.
- **INVARIANTS:** tên/nghĩa sáu event BIZ-02 giữ nguyên; đủ 16 KPI với baseline `BASELINE_UNKNOWN`; không thay A0 decision; quyền truy cập account vẫn `UNVERIFIED`.
- **DO_NOT_TOUCH:** account thật, customer data, tracking production, PR nguồn, các file `STATE/CATALOG/CHANGELOG/rules`, API paid/live, publish, VPS.
- **STOP:** nếu cần OAuth, PII, legal approval, retention, conversion count, spend hoặc account access; ghi `UNKNOWN`/`NEEDS_A0` và vẫn hoàn thành phần offline.
- **PASS:** `GROW02A_S1_DRAFT_EVENT_CONTRACT_READY_FOR_REVIEW` cho schema/tài liệu/mock-only, không phải live tracking hay policy approved.
- **HANDOFF:** [report](../reports/2026-11-23-hermes-grow02a-s1-attribution-contract.md) + [JSON](../reports/evidence/2026-11-23-hermes-grow02a-s1-events-and-tests.json) → ChatGPT Điều phối.
