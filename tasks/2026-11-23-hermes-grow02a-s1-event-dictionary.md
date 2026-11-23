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
| BIZ-01 discovery | DONE_REPORTED/ACCEPTED_WITH_LIMITS | branch `hermes/biz-01-integration-matrix-2026-11-23` commit `8c821bb` | Không khảo sát lại API |
| GROW-01 draft/rights gate | DONE_REPORTED/ACCEPTED_WITH_LIMITS | branch `hermes/grow-01-s1-editorial-packages-2026-11-23` commit `3c8cb40`; lệnh ở PR #12 | Không rerun fixture |
| BIZ-02 use cases/16 KPI/5 A0 choices | DONE_REPORTED/ACCEPTED_WITH_LIMITS | branch `hermes/biz-02-s1-priorities-kpi-draft-2026-11-23` commit `fcdc0f8`; lệnh ở PR #18 | Chỉ mapping, không sửa definition |
| GROW-02A event contract | NOT_RUN trước lượt này | Không có path/branch trùng sau fetch | Sinh dictionary và kiểm định offline |

- **READ_SET:** PR #20 comment; `AGENTS.md`, `PROJECT.md`, `GOALS_AND_ROADMAP.md`, `rules/AGENT_WORKFLOW.md` §§7–10, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/hermes.md`; refs PR #6/#12/#18/#20/#13/#19/#16.
- **WRITE_SET:** chỉ task này, `reports/2026-11-23-hermes-grow02a-s1-attribution-contract.md`, `reports/evidence/2026-11-23-hermes-grow02a-s1-events-and-tests.json`, `sandbox/grow02a-offline-validator/validate.py` trên branch riêng.
- **INVARIANTS:** tên/nghĩa sáu event BIZ-02 giữ nguyên; đủ 16 KPI với baseline `BASELINE_UNKNOWN`; không thay A0 decision; quyền truy cập account vẫn `UNVERIFIED`.
- **DO_NOT_TOUCH:** account thật, customer data, tracking production, PR nguồn, các file `STATE/CATALOG/CHANGELOG/rules`, API paid/live, publish, VPS.
- **STOP:** nếu cần OAuth, PII, legal approval, retention, conversion count, spend hoặc account access; ghi `UNKNOWN`/`NEEDS_A0` và vẫn hoàn thành phần offline.
- **PASS:** `GROW02A_S1_DRAFT_EVENT_CONTRACT_READY_FOR_REVIEW` cho schema/tài liệu/mock-only, không phải live tracking hay policy approved.
- **HANDOFF:** [report](../reports/2026-11-23-hermes-grow02a-s1-attribution-contract.md) + [JSON](../reports/evidence/2026-11-23-hermes-grow02a-s1-events-and-tests.json) → ChatGPT Điều phối.

## D1 corrective checkpoint — GROW02A-QA-01

- **ACK / nguồn:** [PR #23 comment 7091502269](https://github.com/DuyKienTTD/Hosting/pull/23#issuecomment-7091502269), `GROW-02A/S1-D1`; from/next owner ChatGPT Điều phối; executor Hermes WebUI. Fetch main/PR #23/PR #20; `BASE_SHA=PR23_HEAD=44dd545e1698f884b41fd8dd49c94929e1415e50`; branch hiện tại `hermes/grow-02a-s1-event-dictionary-2026-11-23` sạch và đồng bộ trước sửa.
- **PREVIOUSLY_VERIFIED:** 9/9 S1 author-run được báo tại base, nhưng thiếu source/version nên không kiểm chứng contract composite. **CHANGE_TRIGGER:** GROW02A-QA-01; chỉ kiểm thử namespace/idempotency và chạy validator GROW02A bị ảnh hưởng, không chạy suite BIZ-02/GROW-01.
- **FIRST_ACTION / READ_SET:** đọc quy tắc main `e385c1bea2070973e3007e5717f7e980348d6ab3`, HEAD PR23, bản PR20/BIZ-02, report/JSON/validator hiện tại; tái hiện lỗi với cùng ID khác nguồn trước sửa.
- **WRITE_SET:** validator `sandbox/grow02a-offline-validator/validate.py`, `tests`/kết quả `d1_delta` trong JSON, addendum của report và checkpoint task này. **DO_NOT_TOUCH:** 14 event definitions, 16 KPI definitions, 5 quyết định A0, GROW-01/BIZ-02, STATE/CATALOG/CHANGELOG, accounts/live tracking/customer data/production/paid.
- **TEST_DELTA / PASS:** 12 fixture mới và T4/T5/T5b bổ sung namespace; 21/21 fixture GROW02A hiện tại chạy offline, có actual `expected == observed`, source blob và remote readback. `GROW02A_S1_D1_COMPOSITE_DEDUP_PASS` chỉ áp dụng validator offline; không cấp chính sách hoặc quyền live.
- **HANDOFF:** addendum tại [report](../reports/2026-11-23-hermes-grow02a-s1-attribution-contract.md#d1--grow02a-qa-01-composite-idempotency-delta-addendum), JSON evidence và commit PR #23 → ChatGPT Điều phối review độc lập.
