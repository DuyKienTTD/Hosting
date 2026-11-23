---
id: hermes-biz02-s2-mvp-acceptance-2026-11-23
type: report
status: draft_ready_for_review
updated_at: 2026-11-23
sensitivity: public-redacted
task_id: BIZ-02/S2
owner: hermes-webui
next_owner: chatgpt
---

# BIZ-02/S2 — Hợp đồng nghiệm thu operator, MVP offline (draft)

## ACK, nguồn, giới hạn
- ACK từ [PR #23 comment 7091682554](https://github.com/DuyKienTTD/Hosting/pull/23#issuecomment-7091682554). `BASE_SHA=e385c1bea2070973e3007e5717f7e980348d6ab3`; Git SSH write đã thử, tài khoản business/production không truy cập. SHA source chính: BIZ-02/S1 PR #20 `fcdc0f8`, GROW-02A/D1 PR #23 `f2f092a`, UX S2 PR #16 `9a629fb`, ENG S3 PR #19 `17ac45c`, S4 PR #21 `761e954`, OPS PR #22 `7f18955`. Full SHA và các PR khác nằm trong evidence.
- Quy tắc main đã đọc: `AGENTS.md`, `rules/AGENT_WORKFLOW.md` (main chỉ có §§1–7; không suy diễn §§8–10 từ branch khác), `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/hermes.md`, `PROJECT.md`. Branch tách từ `origin/main`; file S2 không có trên main hoặc branch cùng tên tại checkpoint.
- **Nguồn không phải nghiệm thu live:** UX S2 9 route frontend và DOM/source tests nhưng `BROWSER_UNTESTED`, không có backend server auth. ENG S3 bridge fake có D1 binding delta, không phải live connector; S4 manifest Linux chưa chạy. OPS chỉ evaluator cảnh báo giả. GROW-01 gói draft và GROW-02A dictionary là draft, independent QA còn chờ.
- `WRITE_SET` chỉ ba artifact và validator trong branch S2; không sửa source/STATE/CATALOG/CHANGELOG. Không gọi paid/real API, không login, dữ liệu khách hàng hoặc production.

## Quy ước trạng thái nghiệm thu
| Trạng thái | Nghĩa |
|---|---|
| `ACCEPT_OFFLINE` | Chấp nhận *kịch bản minh họa bằng fixture* để owner duyệt; không chứng minh UI/backend hoạt động |
| `STUB_ONLY` | Chỉ có bề mặt/proposal; chưa có integration đầy đủ |
| `BLOCKED_NEEDS_BACKEND` | Cần server authorization, durability/receipt, không dùng role client làm quyền |
| `BLOCKED_NEEDS_A0` | Cần quyết định về publish, consent, retention, budget hoặc attribution |
| `BLOCKED_ACCESS` | Thiếu quyền đọc tài khoản đã kiểm chứng |
| `NOT_TESTED` | Chưa có chứng cứ chức năng hoặc receipt; health 200 không chứng minh inference |

## Năm hành trình operator (human-runnable acceptance stories)

### J1 — Incident acknowledge/escalate
- **Actor/quyền:** operator → named on-call reviewer; synthetic reviewer only; no server authorization established. **Điều kiện:** offline fixtures isolated, no production credentials, roles and A0 decisions unapproved.
- **Fixture/input:** `FX-J1` {"job_id": "job-synthetic-01", "signal": "outcome_unknown"}.
- **Nguồn/trạng thái:** #16, #22, #20; `OFFLINE_MOCK_DESIGN` / `ACCEPT_OFFLINE`; product/browser `NOT_TESTED`. **UC:** UC06, UC07.
  1. User: open offline incident queue → UI: offline incident queue shows fixture and source watermark → mock: UX S2 fixture / OPS S1 evaluator supplies synthetic record only → receipt: no external receipt before operator decision.
  2. User: inspect data and choose review/hold → UI: show explicit state, provenance and blocked action → mock: no live write/paid dispatch → receipt: mock decision note, not alert delivery.
  3. User: record reviewer decision or escalate → UI: display owner and decision reason → mock: no real side effect → receipt: mock decision note, not alert delivery.
- **Audit:** job_id + source snapshot + operator role + reason + state transition. **Blocked:** retry, live alert dispatch, role self-approval. **Approval:** operator may mark local triage; escalation owner named; server authority BLOCKED_NEEDS_BACKEND.
- **Phi chức năng:** auth `BLOCKED_NEEDS_BACKEND`; privacy synthetic metadata only; no identity joins; durability backend durable receipt unverified; EN/VI/keyboard EN/VI and keyboard browser QA NOT_TESTED; retention `BLOCKED_NEEDS_A0`; finance paid/Ads/write disabled.
- **Evidence path refs:** #16 sandbox/operator-ui/README.md; #22 reports/2026-11-23-hostinger-ops01a-s1-monitoring-qa.md; #20 reports/evidence/2026-11-23-hermes-biz02-s1-priority-matrix.json.

### J2 — WP/Woo EN/VI gap inspection
- **Actor/quyền:** content operator + technical reviewer; synthetic reviewer only; no server authorization established. **Điều kiện:** offline fixtures isolated, no production credentials, roles and A0 decisions unapproved.
- **Fixture/input:** `FX-J2` {"record_ref": "product-synthetic-vi-01", "locale": "vi", "missing_field": "alt_text"}.
- **Nguồn/trạng thái:** #13, #19, #21, #20; `OFFLINE_MOCK_DESIGN` / `ACCEPT_OFFLINE`; product/browser `NOT_TESTED`. **UC:** UC01.
  1. User: open catalog gap view → UI: catalog gap view shows fixture and source watermark → mock: ENG S2 fake WP/Woo read through S3 mock bridge supplies synthetic record only → receipt: no external receipt before operator decision.
  2. User: inspect data and choose review/hold → UI: show explicit state, provenance and blocked action → mock: no live write/paid dispatch → receipt: versioned gap review draft; no site mutation.
  3. User: record reviewer decision or escalate → UI: display owner and decision reason → mock: no real side effect → receipt: versioned gap review draft; no site mutation.
- **Audit:** fixture source/watermark + locale + gap key + reviewer decision. **Blocked:** write product, publish page, assume stale snapshot current. **Approval:** site owner must approve real read; editor cannot write.
- **Phi chức năng:** auth `BLOCKED_NEEDS_BACKEND`; privacy synthetic metadata only; no identity joins; durability backend durable receipt unverified; EN/VI/keyboard EN/VI and keyboard browser QA NOT_TESTED; retention `BLOCKED_NEEDS_A0`; finance paid/Ads/write disabled.
- **Evidence path refs:** #13 reports/2026-11-23-eng-01a-s2-fake-channel-adapters.md; #19 reports/2026-11-23-eng-01a-s3-d1-prepared-result-binding.md; #21 reports/2026-11-23-eng-01a-s4-release-readiness.md; #20 reports/evidence/2026-11-23-hermes-biz02-s1-priority-matrix.json.

### J3 — GA4 aggregate and UTM provenance
- **Actor/quyền:** analyst + privacy owner; synthetic reviewer only; no server authorization established. **Điều kiện:** offline fixtures isolated, no production credentials, roles and A0 decisions unapproved.
- **Fixture/input:** `FX-J3` {"property_ref": "property-synthetic", "sessions": 3, "tagged_sessions": 2, "attribution": "UNKNOWN"}.
- **Nguồn/trạng thái:** #13, #19, #23, #20; `OFFLINE_MOCK_DESIGN` / `ACCEPT_OFFLINE`; product/browser `NOT_TESTED`. **UC:** UC02, UC03.
  1. User: open aggregate report panel → UI: aggregate report panel shows fixture and source watermark → mock: ENG S2 fake GA4 read and GROW02A offline UTM contract supplies synthetic record only → receipt: no external receipt before operator decision.
  2. User: inspect data and choose review/hold → UI: show explicit state, provenance and blocked action → mock: no live write/paid dispatch → receipt: synthetic aggregate report; identity attribution UNKNOWN.
  3. User: record reviewer decision or escalate → UI: display owner and decision reason → mock: no real side effect → receipt: synthetic aggregate report; identity attribution UNKNOWN.
- **Audit:** property mock ref + period + source label + freshness/unknown reason. **Blocked:** join to named CRM lead, infer qualified lead, enable live GA4. **Approval:** property read auth and lawful consent for real use BLOCKED_ACCESS.
- **Phi chức năng:** auth `BLOCKED_NEEDS_BACKEND`; privacy synthetic metadata only; no identity joins; durability backend durable receipt unverified; EN/VI/keyboard EN/VI and keyboard browser QA NOT_TESTED; retention `BLOCKED_NEEDS_A0`; finance paid/Ads/write disabled.
- **Evidence path refs:** #13 reports/2026-11-23-eng-01a-s2-fake-channel-adapters.md; #19 reports/2026-11-23-eng-01a-s3-d1-prepared-result-binding.md; #23 reports/2026-11-23-hermes-grow02a-s1-attribution-contract.md; #20 reports/evidence/2026-11-23-hermes-biz02-s1-priority-matrix.json.

### J4 — Bilingual draft and reviewer handoff
- **Actor/quyền:** editor + rights reviewer + engineer + publisher; synthetic reviewer only; no server authorization established. **Điều kiện:** offline fixtures isolated, no production credentials, roles and A0 decisions unapproved.
- **Fixture/input:** `FX-J4` {"package_ref": "P2-synthetic-v1", "locales": ["en", "vi"], "rights_verified": false, "technical_verified": false}.
- **Nguồn/trạng thái:** #18, #16, #23, #20; `OFFLINE_MOCK_DESIGN` / `ACCEPT_OFFLINE`; product/browser `NOT_TESTED`. **UC:** UC04, UC05.
  1. User: open content draft review → UI: content draft review shows fixture and source watermark → mock: GROW01 P1-P3 synthetic review gate supplies synthetic record only → receipt: no external receipt before operator decision.
  2. User: inspect data and choose review/hold → UI: show explicit state, provenance and blocked action → mock: no live write/paid dispatch → receipt: NEEDS_REVIEW/BLOCKED draft only, no channel post.
  3. User: record reviewer decision or escalate → UI: display owner and decision reason → mock: no real side effect → receipt: NEEDS_REVIEW/BLOCKED draft only, no channel post.
- **Audit:** package/version + separate reviewer roles + reason. **Blocked:** publish, export as approved, client-side role override. **Approval:** rights/tech/business/channel approvals and A0; fixture APPROVED != human signoff.
- **Phi chức năng:** auth `BLOCKED_NEEDS_BACKEND`; privacy synthetic metadata only; no identity joins; durability backend durable receipt unverified; EN/VI/keyboard EN/VI and keyboard browser QA NOT_TESTED; retention `BLOCKED_NEEDS_A0`; finance paid/Ads/write disabled.
- **Evidence path refs:** #18 reports/2026-11-23-hermes-grow-01-s1-media-workflow.md; #16 sandbox/operator-ui/README.md; #23 reports/2026-11-23-hermes-grow02a-s1-attribution-contract.md; #20 reports/evidence/2026-11-23-hermes-biz02-s1-priority-matrix.json.

### J5 — Workflow build, simulate, unknown receipt
- **Actor/quyền:** operator + security/budget owner; synthetic reviewer only; no server authorization established. **Điều kiện:** offline fixtures isolated, no production credentials, roles and A0 decisions unapproved.
- **Fixture/input:** `FX-J5` {"workflow_ref": "flow-synthetic-01", "outcome": "outcome_unknown", "paid_retry_requested": false}.
- **Nguồn/trạng thái:** #16, #10, #19, #21, #22, #20; `STUB_OR_MOCK_SPLIT` / `STUB_ONLY`; product/browser `NOT_TESTED`. **UC:** UC06, UC08.
  1. User: open builder and receipt timeline → UI: builder and receipt timeline shows fixture and source watermark → mock: UX S2 local simulate + ENG S3 fake bridge (S4 Linux unrun) supplies synthetic record only → receipt: no external receipt before operator decision.
  2. User: inspect data and choose review/hold → UI: show explicit state, provenance and blocked action → mock: no live write/paid dispatch → receipt: single synthetic receipt or UNKNOWN hold; no retry.
  3. User: record reviewer decision or escalate → UI: display owner and decision reason → mock: no real side effect → receipt: single synthetic receipt or UNKNOWN hold; no retry.
- **Audit:** workflow/version + run ref + receipt identity + decision reason. **Blocked:** auto paid retry, activate real workflow, dashboard 200 => model healthy. **Approval:** server-side auth/durable ledger and budget owner approval absent.
- **Phi chức năng:** auth `BLOCKED_NEEDS_BACKEND`; privacy synthetic metadata only; no identity joins; durability backend durable receipt unverified; EN/VI/keyboard EN/VI and keyboard browser QA NOT_TESTED; retention `BLOCKED_NEEDS_A0`; finance paid/Ads/write disabled.
- **Evidence path refs:** #16 sandbox/operator-ui/README.md; #10 reports/2026-11-23-eng-01a-s1-offline-connector-contract.md; #19 reports/2026-11-23-eng-01a-s3-d1-prepared-result-binding.md; #21 reports/2026-11-23-eng-01a-s4-release-readiness.md; #22 reports/2026-11-23-hostinger-ops01a-s1-monitoring-qa.md; #20 reports/evidence/2026-11-23-hermes-biz02-s1-priority-matrix.json.

## Scenario decision table — 15 fixture giả
`PASS_TABLETOP` là thiết kế kỳ vọng; `ACTUALLY_EXECUTED` chỉ áp dụng cho hàm quyết định offline trong validator, **không phải** UI/browser/connector/backend. Cột `product_result` giữ `NOT_TESTED`.
| Case / fixture | Positive/negative, failure signal | Kỳ vọng → quan sát offline | Event/receipt, product result |
|---|---|---|---|
| `S01` / `FX-J1` | positive triage; none | `ACCEPT_OFFLINE` → `ACCEPT_OFFLINE` (`PASS_TABLETOP`) | `approval_queue_item_opened`; local ack draft; `NOT_TESTED` |
| `S02` / `FX-J1` | unknown no paid retry; retry disabled | `BLOCKED_NEEDS_BACKEND` → `BLOCKED_NEEDS_BACKEND` (`PASS_TABLETOP`) | `connector_read_outcome_recorded`; UNKNOWN held; `NOT_TESTED` |
| `S03` / `FX-J1` | dashboard 200 is not inference; missing inference receipt | `NOT_TESTED` → `NOT_TESTED` (`PASS_TABLETOP`) | `none`; UNKNOWN model health; `NOT_TESTED` |
| `S04` / `FX-J2` | positive EN/VI gap review; none | `ACCEPT_OFFLINE` → `ACCEPT_OFFLINE` (`PASS_TABLETOP`) | `catalog_gap_detected`; mock gap draft; `NOT_TESTED` |
| `S05` / `FX-J2` | real site read without auth; missing site owner read scope | `BLOCKED_ACCESS` → `BLOCKED_ACCESS` (`PASS_TABLETOP`) | `none`; no live receipt; `NOT_TESTED` |
| `S06` / `FX-J2` | write product from mock; no write approval | `BLOCKED_NEEDS_A0` → `BLOCKED_NEEDS_A0` (`PASS_TABLETOP`) | `none`; no post ID; `NOT_TESTED` |
| `S07` / `FX-J3` | aggregate unknown provenance; none | `ACCEPT_OFFLINE` → `ACCEPT_OFFLINE` (`PASS_TABLETOP`) | `ga4_aggregate_observed`; mock rows; attribution UNKNOWN; `NOT_TESTED` |
| `S08` / `FX-J3` | GA4 join identified lead; no consent and join policy | `BLOCKED_NEEDS_A0` → `BLOCKED_NEEDS_A0` (`PASS_TABLETOP`) | `none`; no joined identity; `NOT_TESTED` |
| `S09` / `FX-J4` | draft bilingual review; none | `ACCEPT_OFFLINE` → `ACCEPT_OFFLINE` (`PASS_TABLETOP`) | `content_draft_submitted`; draft package only; `NOT_TESTED` |
| `S10` / `FX-J4` | rights/technical signoff missing; rights and engineer absent | `BLOCKED_NEEDS_A0` → `BLOCKED_NEEDS_A0` (`PASS_TABLETOP`) | `content_review_decided`; BLOCKED draft; no post; `NOT_TESTED` |
| `S11` / `FX-J4` | client role tampered; server RBAC not implemented | `BLOCKED_NEEDS_BACKEND` → `BLOCKED_NEEDS_BACKEND` (`PASS_TABLETOP`) | `none`; no real approval; `NOT_TESTED` |
| `S12` / `FX-J5` | local workflow simulation; none | `ACCEPT_OFFLINE` → `ACCEPT_OFFLINE` (`PASS_TABLETOP`) | `connector_read_outcome_recorded`; mock only; `NOT_TESTED` |
| `S13` / `FX-J5` | unknown receipt forbids retry; unknown state; paid retry forbidden | `BLOCKED_NEEDS_BACKEND` → `BLOCKED_NEEDS_BACKEND` (`PASS_TABLETOP`) | `connector_read_outcome_recorded`; UNKNOWN held; `NOT_TESTED` |
| `S14` / `FX-J5` | invalid mapping fixture; mapping invalid and activation unavailable | `BLOCKED_NEEDS_BACKEND` → `BLOCKED_NEEDS_BACKEND` (`PASS_TABLETOP`) | `none`; no dispatch; `NOT_TESTED` |
| `S15` / `FX-J5` | Ads optimization spend gate; A0 budget and Ads owner absent | `BLOCKED_NEEDS_A0` → `BLOCKED_NEEDS_A0` (`PASS_TABLETOP`) | `none`; no spend; `NOT_TESTED` |

Các gate đặc biệt: `S02`/`S13` outcome_unknown cấm paid retry; `S10` thiếu quyền asset/engineering cấm publish; `S08` aggregate GA4 không join lead định danh; `S03` dashboard HTTP 200 không chứng minh model inference; `S11` thay role client không qua được server approval (server gate **chưa triển khai**, không được tuyên bố đã chặn thật).

## Ma trận truy vết 8 UC → 5 story → 16 KPI nguồn BIZ-02/S1
Tên và toàn bộ định nghĩa KPI được **copy nguyên** trong JSON evidence và validator đối chiếu field-by-field với BIZ-02/S1; bảng là index, không tạo chính sách KPI mới. Mọi baseline `BASELINE_UNKNOWN`. Tier S1 là business-realization, không được đổi thành quyền demo/live.
| UC (tier S1) | Story; PR implementation | Synthetic cases | KPI leading + lagging | Gate còn thiếu |
|---|---|---|---|---|
| `UC01` `MVP_OFFLINE_NOW` | J2; #13, #19, #20, #21 | S04, S05, S06 | `inventory_review_coverage` + `resolved_content_gap_rate` (`BASELINE_UNKNOWN`) | real WP/Woo read auth and fixture denominator |
| `UC02` `NEXT_AFTER_READ_AUTH` | J3; #13, #19, #20, #23 | S07, S08 | `channel_attribution_coverage` + `engaged_session_rate` (`BASELINE_UNKNOWN`) | GA4 property read auth, consent and aggregate freshness |
| `UC03` `MVP_OFFLINE_NOW` | J3; #13, #19, #20, #23 | S07, S08 | `UTM_validity_rate` + `qualified_lead_rate` (`BASELINE_UNKNOWN`) | CRM consent and A0 attribution policy; no identity join |
| `UC04` `MVP_OFFLINE_NOW` | J4; #16, #18, #20, #23 | S09, S10, S11 | `draft_review_completion` + `QA_rework_rate` (`BASELINE_UNKNOWN`) | actual rights/engineering review, localization browser QA |
| `UC05` `LATER_WITH_SEPARATE_WRITE_APPROVAL` | J4; #16, #18, #20, #23 | S09, S10, S11 | `handoff_gate_completeness` + `authorized_publish_success_rate` (`BASELINE_UNKNOWN`) | rights/channel owner publish approval; no post receipt |
| `UC06` `MVP_OFFLINE_NOW` | J1, J5; #10, #16, #19, #20, #21, #22 | S01, S02, S03, S12, S13, S14, S15 | `triage_coverage` + `mean_synthetic_resolution_time` (`BASELINE_UNKNOWN`) | server RBAC/durable receipt and real escalation owner |
| `UC07` `NEXT_AFTER_READ_AUTH` | J1; #16, #20, #22 | S01, S02, S03 | `synthetic_triage_coverage` + `qualified_inquiry_handoff_rate` (`BASELINE_UNKNOWN`) | consented inbox read and sales human handoff |
| `UC08` `LATER_WITH_SEPARATE_WRITE_APPROVAL` | J5; #10, #16, #19, #20, #21, #22 | S12, S13, S14, S15 | `proposal_review_coverage` + `cost_per_qualified_lead` (`BASELINE_UNKNOWN`) | A0 budget, lawful attributed leads and Ads write approval |

## Khuyến nghị minimum launch slice — chỉ demo offline
- Đề nghị `MVP_OFFLINE_DEMO`: operator chạy fixture cho J1–J5, quan sát nguồn/owner/UNKNOWN, ghi quyết định **giả lập** và dừng ở gate. Không phải 5 feature deployable; J5 build/simulate mock nhưng activation/server receipt/paid vẫn khóa.
- **Không gồm:** browser E2E, quyền server, OAuth/connector thật, publish, paid retry, CRM person join, live monitoring, real retention. Chỉ đánh dấu `ACCEPT_OFFLINE` cho bàn thiết kế/fixture; những đoạn backend chưa triển khai là `BLOCKED_NEEDS_BACKEND`.
- **Success criteria để A0/owner xét:** đủ 5 flow có actor/nguồn/receipt/decision reason; mọi transition nguy hiểm bị giữ trong policy draft; 8 UC/16 KPI truy vết. Thời gian review/ROI chỉ có thể đo sau khi owner duyệt instrumentation và có dữ liệu hợp lệ; không đặt baseline synthetic thay số kinh doanh.
- **Rủi ro interface cao nhất:** approval client-side hoặc receipt `outcome_unknown` bị hiểu nhầm là quyền/settlement durable server; phải có server-side RBAC, authorization, receipt binding, replay gate và QA độc lập trước live.
- **A0 chờ:** `A0-1` nhóm đối tượng đầu tiên; `A0-2` KPI mục tiêu; `A0-3` nguồn dữ liệu real đầu tiên; `A0-4` chọn slice MVP; `A0-5` cadence/retention. Cả 5 là `AWAITING_A0_DECISION`, không tự chốt.

## Kiểm thử thật và bàn giao
- Đã chạy `python3 -B sandbox/biz02-mvp-acceptance/validate.py`: parse JSON, so 5 story/15 case/8 UC/16 KPI nguyên field/5 A0, so actual policy decision từ flags với expected và observed; chỉ chạy trên fixture local. **15/15 policy decision PASS**, `product_functional_result=NOT_TESTED` cho 15/15. Không chạy UX browser/ENG/OPS suites và không dùng network/API.
- JSON evidence là artifact canonical cho case ID, synthetic flags, expected event/receipt/audit, failure signal, status và full source SHAs. Gate chưa giải: server auth/durable receipt, browser/keyboard QA, lawful consent, site/GA4/inbox read auth, publisher rights, budget, retention, A0.
- **Verdict:** `BIZ02_S2_OFFLINE_MVP_ACCEPTANCE_DRAFT_READY_FOR_REVIEW` nghĩa là bản thiết kế + kiểm tra policy offline có thể đưa đi review, **không** phải nghiệm thu sản phẩm, A0 approval hay production readiness.
- **Handoff:** `TASK=BIZ-02/S2 | AGENT=Hermes | ACK=ACKNOWLEDGED | BASE_SHA=e385c1bea2070973e3007e5717f7e980348d6ab3 | STORIES=5 | SCENARIOS=15 | TRACEABILITY=8_UC_16_KPI | TEST_METHOD=offline policy evaluator 15/15; product NOT_TESTED | A0_PENDING=5 | EVIDENCE=reports/evidence/2026-11-23-hermes-biz02-s2-mvp-scenarios.json | VERDICT=BIZ02_S2_OFFLINE_MVP_ACCEPTANCE_DRAFT_READY_FOR_REVIEW | NEXT_OWNER=ChatGPT Điều phối`.

## Nguồn GitHub
- [Lệnh S2](https://github.com/DuyKienTTD/Hosting/pull/23#issuecomment-7091682554) · [BIZ-02/S1 PR #20](https://github.com/DuyKienTTD/Hosting/pull/20) · [GROW-02A PR #23](https://github.com/DuyKienTTD/Hosting/pull/23)
- [UX S2 PR #16](https://github.com/DuyKienTTD/Hosting/pull/16) · [ENG S3 PR #19](https://github.com/DuyKienTTD/Hosting/pull/19) · [ENG S4 PR #21](https://github.com/DuyKienTTD/Hosting/pull/21) · [OPS PR #22](https://github.com/DuyKienTTD/Hosting/pull/22)
- [BIZ-01 PR #12](https://github.com/DuyKienTTD/Hosting/pull/12) · [GROW-01 PR #18](https://github.com/DuyKienTTD/Hosting/pull/18) · [Master PR #6](https://github.com/DuyKienTTD/Hosting/pull/6)
