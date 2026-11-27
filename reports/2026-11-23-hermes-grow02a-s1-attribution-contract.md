---
id: hermes-grow02a-s1-attribution-contract-2026-11-23
type: report
status: draft_ready_for_review
updated_at: 2026-11-23
sensitivity: public-redacted
task_id: GROW-02A/S1-SUPPORT
owner: hermes-webui-support
next_owner: chatgpt
---

# GROW-02A/S1-SUPPORT — Từ điển sự kiện và hợp đồng đo lường offline

## ACK / provenance / ranh giới
- ACK `EXECUTE GROW-02A/S1-SUPPORT`, từ [PR #20 comment 7091269345](https://github.com/DuyKienTTD/Hosting/pull/20#issuecomment-7091269345). Hermes chỉ support bounded draft; ChatGPT/Work giữ parent ownership, ChatGPT Điều phối nhận review và A0 chốt các lựa chọn chính sách.
- `MAIN_SHA` và rules SHA: `e385c1bea2070973e3007e5717f7e980348d6ab3`; PR #6 `03fb56b6d3b4f42a1cb65c6e3c87a19099785044`. Source commits: BIZ-01 `8c821bb`, GROW-01 `3c8cb40`, BIZ-02 `fcdc0f8`, ENG S2 `0235b5f`, ENG S3 `c343f7d`, UX S2 `9a629fb`. Chi tiết full SHA trong JSON.
- Đã đọc rules/AGENTS/PROJECT/roadmap/STATE/CATALOG/profile tại main, evidence và report BIZ-01/GROW-01/BIZ-02 từ refs riêng. PR #13/#19/#16 chỉ chứng minh mock/offline, không chứng minh real connector hoặc backend. Không dùng vendor docs mới để suy đoán live entitlement.
- `WRITE_SET`: task + report + JSON + validator Python offline. `DO_NOT_TOUCH`: nguồn, shared indexes/rules, live accounts, tracking, customer data, publishing, VPS. Chỉ đề xuất index update cho coordinator sau diff review.
- **Không có dữ liệu nghiệp vụ thật**: KPI 16/16 giữ đúng tên, numerator, denominator, unit, owner, window và `BASELINE_UNKNOWN` từ BIZ-02. Năm quyết định A0 vẫn `AWAITING_A0_DECISION`.

## 1. Từ điển sự kiện v0.1-proposal
Mọi sự kiện là **OFFLINE_PROPOSED** hoặc **REAL_UNVERIFIED**. Không có emitter live. Mỗi dòng trong JSON có owner, trigger, required/optional fields kèm kiểu, source, unit, allowed values, cardinality, idempotency, UTC timestamp, schema version, retention, privacy, consent và supporting PR; bảng dưới đây là index, JSON là contract chi tiết.
**Common envelope đề xuất**: `event_id:string` (ổn định trong source), `occurred_at_utc:string RFC3339 UTC`, `schema_version:string = 0.1-proposal`, `source_system:string`; optional `ingested_at_utc` chỉ cho pipeline tương lai. Khóa dedup `(source_system,event_id,schema_version)`; replay cùng payload bỏ qua, ID trùng với payload khác `BLOCKED`. Không dùng tên event hoặc URL làm nơi chứa PII.

| Event | Giữ tên BIZ-02 / mới | Owner; trigger; source | Unit/cardinality | Privacy/consent; status |
|---|---|---|---|---|
| `content_draft_submitted` | BIZ02_NAME_UNCHANGED | editorial owner; human submits package draft; GROW-01 synthetic package | distinct package versions; one per package_id+version | INTERNAL_METADATA; none for synthetic; rights/consent before real assets; OFFLINE_PROPOSED |
| `content_review_decided` | BIZ02_NAME_UNCHANGED | editorial owner; human records review decision; GROW-01 draft review | distinct decisions; one per package/version/review decision id | INTERNAL_METADATA; actual approval signature absent; fixture APPROVED not real; OFFLINE_PROPOSED |
| `catalog_gap_detected` | BIZ02_NAME_UNCHANGED | site content owner; offline audit identifies missing field; ENG-01A synthetic WP/Woo read | distinct record-field gaps; one per source record/version/field | BUSINESS_METADATA; read scope needed for real WP/Woo; no customer fields; OFFLINE_PROPOSED |
| `campaign_link_checked` | BIZ02_NAME_UNCHANGED | marketing owner; offline UTM string validator runs; synthetic URL fixture | distinct checked URLs; one per canonical URL+test version | PUBLIC_CAMPAIGN_METADATA; no PII in URL or terms; OFFLINE_PROPOSED |
| `lead_form_submitted` | BIZ02_NAME_UNCHANGED | site/form owner; future form accepted after consent; future first-party form; NOT CONNECTED | distinct consented submissions; one per form submission ref; no raw payload | IDENTITY_RESTRICTED; explicit form/legal/privacy approval before emission; no live emitter in S1; REAL_UNVERIFIED |
| `inquiry_qualified` | BIZ02_NAME_UNCHANGED | sales owner; human CRM qualification decision; future consented CRM; NOT CONNECTED | distinct human-qualified leads; one decision per lead_ref/decision_ref; click never qualifies | IDENTITY_RESTRICTED; consented CRM read + sales human signoff; absent in S1; REAL_UNVERIFIED |
| `ga4_aggregate_observed` | EXTENSION_PROPOSED | analytics owner; offline mock aggregate row read; ENG-01A S2 fake GA4 aggregate | sessions aggregate, never persons; one row per property+period+source_medium+snapshot | AGGREGATE_ONLY; real property read permission + analytics legal review required; OFFLINE_PROPOSED |
| `campaign_click_observed` | EXTENSION_PROPOSED | marketing owner; future platform aggregate click export; hypothetical platform aggregate; NOT CONNECTED | clicks (not sessions or leads); one aggregate row per campaign+period+source | AGGREGATE_ONLY; owner read authorization; no user identifiers; REAL_UNVERIFIED |
| `inquiry_message_received` | EXTENSION_PROPOSED | sales owner; future inbox consented inbound message; future inbox; NOT CONNECTED | messages (not leads); one platform message ID per inbound message; no raw text | IDENTITY_RESTRICTED; mailbox permission and retention approval; no message copied here; REAL_UNVERIFIED |
| `catalog_gap_resolved` | EXTENSION_PROPOSED | site content owner; human marks previously detected gap resolved; synthetic editorial audit | resolved gaps; one per gap_ref+record_version | BUSINESS_METADATA; real site change not authorized; OFFLINE_PROPOSED |
| `approval_queue_item_opened` | EXTENSION_PROPOSED | operator; synthetic blocked/unknown job enters review queue; UX-01 S2 offline UI | queue items; one per job/state transition | INTERNAL_METADATA; no payload/PII in audit events; OFFLINE_PROPOSED |
| `approval_queue_item_resolved` | EXTENSION_PROPOSED | operator; human resolves synthetic queue item; UX-01 S2 offline UI | minutes per resolved item; one per job_ref+resolution version | INTERNAL_METADATA; no customer payload; OFFLINE_PROPOSED |
| `publish_handoff_requested` | EXTENSION_PROPOSED | publisher; human submits package for approval handoff; GROW-01 draft gate | packages requested, NOT posts; one per package+version+request | INTERNAL_METADATA; rights, consent and actual channel permission remain unknown; OFFLINE_PROPOSED |
| `connector_read_outcome_recorded` | EXTENSION_PROPOSED | technical owner; synthetic adapter read reaches final state; ENG-01A S2/S3 offline mock | read attempts, NOT delivered business events; one durable outcome per run_ref; no retry unknown | INTERNAL_METADATA; live OAuth/connector not verified; OFFLINE_PROPOSED |

Sáu tên `BIZ02_NAME_UNCHANGED` chỉ kéo dài hợp đồng quan sát, **không đổi nghĩa**: `content_draft_submitted` là draft chứ không phải publish, `content_review_decided` có quyết định người thật chứ fixture không trao quyền, `catalog_gap_detected` là gap bản ghi, `campaign_link_checked` chỉ validate link, `lead_form_submitted` là future form có consent và `inquiry_qualified` cần quyết định sales; click không thể tự qualify.

## 2. UTM/attribution (proposed, A0 chưa duyệt)
- Canonical required: `utm_source`, `utm_medium`, `utm_campaign`; optional `utm_content`, `utm_term`; `campaign_ref` là opaque internal ref và provenance cần được lưu tách khỏi URL. Ví dụ chỉ dùng `example.invalid`, không phải link phát hành thật.
- Validator offline giới hạn HTTPS `example.invalid`, lower_snake `[a-z0-9_]{2,48}` cho từng giá trị, reject duplicate/unknown/empty parameters, URL userinfo/fragment, PII. Đây là **fixture policy**; host allowlist thật và casing/taxonomy phải do A0/marketing duyệt. Không tự đổi `utm_source` từ `youtube_shorts` trong nháp GROW-01.
- Source precedence **đề xuất chờ A0**: valid first-party UTM được ghi riêng; platform aggregate báo cáo riêng; thiếu/ambiguous → `UNKNOWN`, không tự mặc định direct hay organic. Dedup link theo canonical URL trong fixture; click, GA4 session, form submission, chat message, consented CRM lead và sales-qualified lead là những quần thể riêng, không join person-level từ GA4 aggregate.

| Ý tưởng URL synthetic | Link | Trạng thái |
|---|---|---|
| short | `https://example.invalid/railing?utm_source=youtube_shorts&utm_medium=organic_video&utm_campaign=prov_craft_v1` | example only, not published |
| website | `https://example.invalid/railing?utm_source=site_nav&utm_medium=internal_link&utm_campaign=prov_modular_v1` | example only, not published |
| hypothetical_ad | `https://example.invalid/railing?utm_source=google_ads&utm_medium=paid_search&utm_campaign=prov_ad_v1` | example only, not published |

## 3. Consent/data boundary
| Lớp | Chỉ lưu | Gate và quyền | Retention |
|---|---|---|
| PUBLIC_CAMPAIGN_METADATA | synthetic UTM names, aggregate campaign counts | reject PII in URL; A0 decides source precedence; access: draft analyst | PROPOSED_UNAPPROVED |
| AGGREGATE_ONLY | GA4 sessions and platform aggregate clicks, not persons | property owner read auth + cookie/analytics/legal review before real reads; access: authorized analyst only | PROPOSED_UNAPPROVED |
| IDENTITY_RESTRICTED | opaque form/inquiry/CRM refs, never raw email/phone/text here | explicit consent + privacy owner + CRM owner; no identity join in S1; access: authorized sales/privacy owner only | PROPOSED_UNAPPROVED |
| INTERNAL_METADATA | package/job/decision references with no payload | role based approval and erasure review; access: assigned reviewer/operator | PROPOSED_UNAPPROVED |

Không có dữ liệu cá nhân **thật** trong artifact. Fixture T8 cố tình chứa chuỗi email-shaped giả ở miền `example.invalid` để kiểm tra URL bị chặn; đây không phải địa chỉ khách hàng. Không sao chép email, điện thoại, text tin nhắn và IP/user ID thật vào public Git. Với real tracking: owner duyệt cookie/analytics notice, consent purpose, data minimization, access role, retention duration và erasure workflow; cho tới đó `PROPOSED_UNAPPROVED`. Aggregate không được tự đổi thành CRM person join.

## 4. Liên kết đủ 16 KPI BIZ-02 (không sửa KPI)
Trong JSON mỗi hàng giữ nguyên numerator/denominator/unit/window/owner/consent/baseline từ BIZ-02. `MEASURABLE_OFFLINE` chỉ có nghĩa công thức có thể thử trên fixture *khi có đủ source synthetic*, không có baseline kinh doanh. `NEEDS_REAL_READ_AUTH`, `NEEDS_CONSENTED_CRM`, `NOT_MEASURABLE_YET` đều là gate chờ. Nếu denominator=0 hoặc chưa có nguồn: `UNKNOWN`, không phải 0%. Với spend/cost cần currency theo account và time window.

| UC | KPI BIZ-02 | Event/source | Trạng thái | Gap/giới hạn |
|---|---|---|---|---|
| UC06 | `triage_coverage` | approval_queue_item_opened | MEASURABLE_OFFLINE | synthetic job/ref only |
| UC06 | `mean_synthetic_resolution_time` | approval_queue_item_resolved | MEASURABLE_OFFLINE | synthetic duration only |
| UC01 | `inventory_review_coverage` | connector_read_outcome_recorded, catalog_gap_detected | NOT_MEASURABLE_YET | GAP: reviewed-record count and denominator fixture inventory require separate mock snapshot, event alone insufficient |
| UC01 | `resolved_content_gap_rate` | catalog_gap_detected, catalog_gap_resolved | MEASURABLE_OFFLINE | human confirmed unique gaps and resolution version required |
| UC04 | `draft_review_completion` | content_draft_submitted, content_review_decided | MEASURABLE_OFFLINE | QA field completeness remains package metadata, not event-derived |
| UC04 | `QA_rework_rate` | content_review_decided | NOT_MEASURABLE_YET | decision must include returned-for-rework code in future approved schema; GAP in current draft |
| UC03 | `UTM_validity_rate` | campaign_link_checked | MEASURABLE_OFFLINE | count all checked URLs incl invalid; never count impressions |
| UC03 | `qualified_lead_rate` | lead_form_submitted, inquiry_qualified | NEEDS_CONSENTED_CRM | consented CRM reviewed-lead denominator requires separate approved CRM source; no GA4 join |
| UC02 | `channel_attribution_coverage` | ga4_aggregate_observed | NEEDS_REAL_READ_AUTH | GA4 aggregate with and without channel tag; read permission unknown |
| UC02 | `engaged_session_rate` | ga4_aggregate_observed | NEEDS_REAL_READ_AUTH | GA4 engaged_sessions and sessions from same property/window |
| UC05 | `handoff_gate_completeness` | publish_handoff_requested, content_review_decided | NOT_MEASURABLE_YET | GAP: real rights/business/tech/channel signoffs not present in offline event |
| UC05 | `authorized_publish_success_rate` | NONE | NOT_MEASURABLE_YET | GAP: authorized platform attempts and confirmed post IDs absent; must not infer from handoff |
| UC07 | `synthetic_triage_coverage` | inquiry_message_received | NOT_MEASURABLE_YET | GAP: current name refers synthetic inquiry fixtures; future event is restricted and not emitted; use synthetic fixture set only |
| UC07 | `qualified_inquiry_handoff_rate` | inquiry_message_received, inquiry_qualified | NEEDS_CONSENTED_CRM | human-reviewed inquiry denominator must come from consented sales system |
| UC08 | `proposal_review_coverage` | NONE | NOT_MEASURABLE_YET | GAP: Ads proposal/submitted/review decision source absent and approval unknown |
| UC08 | `cost_per_qualified_lead` | inquiry_qualified | NOT_MEASURABLE_YET | GAP: approved campaign spend/currency and lawful attribution policy absent; cannot join GA4 aggregate to person |

Đặc biệt: `authorized_publish_success_rate` không có platform post ID/attempt thật; `proposal_review_coverage` thiếu source Ads review; `cost_per_qualified_lead` thiếu campaign spend/currency và lawful attribution; các hàng đó phải giữ `NOT_MEASURABLE_YET` dù schema có event phụ. `QA_rework_rate` chưa có mã rework chuẩn; `inventory_review_coverage` cần mẫu số fixture inventory; đó là GAP, không tự tạo definition KPI mới.

## 5. Báo cáo mock và phép kiểm thử offline
| Example | Numerator | Denominator | Source / ý nghĩa | Kết luận |
|---|---:|---:|---|---|
| M1 | 1 | 2 | GROW-01 synthetic fixture; two synthetic content drafts, one review with required fields, one blocked rights case | 1/2 illustrative only, not a baseline |
| M2 | 2 | 3 | ENG-S2 synthetic GA4 aggregate; form counted separately; three GA4 synthetic sessions, two tagged, and one separate fake form submission | 2/3 tagged sessions; form is not joined to GA4 and not qualified |
| M3 | 1 | 2 | URL fixture and event replay fixture; two synthetic UTM links and one duplicate event ID, source missing for one link | 1/2 valid URL fixtures; missing attribution UNKNOWN; replay ignored |

Các con số trong bảng chỉ là **fixture synthetic được viết để minh họa**, không phải đo account. M2: form submission không được join với GA4 sessions. M3: thiếu attribution → `UNKNOWN`; replay event_id không làm tăng số đếm.

Lệnh đã chạy: `python3 -B sandbox/grow02a-offline-validator/validate.py` (Python stdlib, máy local workspace; không network). Validator parse JSON, kiểm đủ event fields/16 KPI/baselines, 0 side effects và expected=observed cho các case sau. Đây là **offline evaluator**, không phải triển khai tracking gate.

| Case | Kỳ vọng | Quan sát |
|---|---|---|
| T1-valid-utm | `VALID_DRAFT_URL` | `VALID_DRAFT_URL` |
| T2-missing-source | `BLOCKED_MISSING_OR_INVALID_UTM` | `BLOCKED_MISSING_OR_INVALID_UTM` |
| T3-duplicate-param | `BLOCKED_DUPLICATE_PARAMETER` | `BLOCKED_DUPLICATE_PARAMETER` |
| T4-unique-event | `ACCEPTED_SYNTHETIC` | `ACCEPTED_SYNTHETIC` |
| T5-replay-event | `DUPLICATE_IGNORED` | `DUPLICATE_IGNORED` |
| T5b-conflicting-replay | `BLOCKED_CONFLICTING_REPLAY` | `BLOCKED_CONFLICTING_REPLAY` |
| T6-unconsented-join | `BLOCKED_NO_CONSENT_OR_JOIN_POLICY` | `BLOCKED_NO_CONSENT_OR_JOIN_POLICY` |
| T7-click-is-not-qualified | `BLOCKED_NO_SALES_DECISION` | `BLOCKED_NO_SALES_DECISION` |
| T8-pii-url | `BLOCKED_MISSING_OR_INVALID_UTM` | `BLOCKED_MISSING_OR_INVALID_UTM` |

## 6. Product integration boundary
- **UX-01 Operator Console:** mock approval queue/report UI có thể hiển thị trạng thái và provenance; chưa có server-side auth hoặc browser E2E.
- **ENG-01A:** GA4/WP/Woo fake read adapters có thể cung cấp aggregate/catalog fixture; S3 chỉ offline integration, không lấy real data. Backend phải implement server-side role permissions, auth, schema validation, durable idempotent dedup, UTC clocks, consent/retention/erasure audit, cost/budget gate và unknown-outcome recovery sau task riêng.
- **GROW-01:** content draft/rights approval gate không phải analytics/legal consent; cần chữ ký người thực khi dùng asset hoặc publish. **GROW-02B** scheduled live reporting là nhánh future conditional, không có quyền trong S1.

## 7. A0/owner quyết định và handoff
- Giữ nguyên 5 câu hỏi `A0-1..A0-5` từ BIZ-02: `AWAITING_A0_DECISION`; không tự sửa trọng số/KPI/nhóm ưu tiên. Gợi ý thêm cho coordinator: chốt precedence nguồn, UTM taxonomy/campaign currency, consent notices và thời hạn lưu, retention/erasure. Đây là đề xuất, không phải quyết định A0.
- **STOP:** thiếu chủ tài khoản, phép đọc GA4/WP/Woo, approved consent/CRM, key join, quyền publish và spend. Không đọc tài khoản, khách hàng, API thật; không tạo tracking tag hay vận hành scheduler. Đề xuất index CATALOG/STATE/CHANGELOG chỉ cho ChatGPT sau coordinated diff review, không sửa ngoài WRITE_SET.
- **Verdict:** `GROW02A_S1_DRAFT_EVENT_CONTRACT_READY_FOR_REVIEW` (từ điển + mapping + kiểm thử offline). Không có live tracking/attribution, consent compliance, A0 approval hoặc KPI baseline thật.

**Handoff:** `TASK=GROW-02A/S1-SUPPORT | AGENT=Hermes WebUI (support) | MAIN_SHA=e385c1bea2070973e3007e5717f7e980348d6ab3 | EXECUTE_ACK=ACKNOWLEDGED | SOURCE_SHAS=PR6 03fb56b, BIZ01 8c821bb, BIZ02 fcdc0f8, GROW01 3c8cb40, ENG S2 0235b5f/S3 c343f7d, UX S2 9a629fb | EVENTS_COUNT=14 | KPI_MAPPING_16=16/16 BASELINE_UNKNOWN | TEST_CASES=9 offline | EVIDENCE=reports/evidence/2026-11-23-hermes-grow02a-s1-events-and-tests.json | VERDICT=GROW02A_S1_DRAFT_EVENT_CONTRACT_READY_FOR_REVIEW | A0_DECISIONS=5 pending | BLOCKERS=real auth, consent, retention and source precedence pending | NEXT_OWNER=ChatGPT Điều phối`

## D1 — GROW02A-QA-01 composite-idempotency delta (addendum)

- **ACK:** [PR #23 D1 chỉ thị](https://github.com/DuyKienTTD/Hosting/pull/23#issuecomment-7091502269), `GROW-02A/S1-D1` từ ChatGPT Điều phối → Hermes WebUI. `BASE_SHA/PR23_HEAD=44dd545e1698f884b41fd8dd49c94929e1415e50`; `origin/main=e385c1bea2070973e3007e5717f7e980348d6ab3`. Chỉ sửa validator và các fixture/test annotations trong JSON cùng addendum này và task; không sửa `main` hoặc shared indexes.
- **Finding reproduced (RED):** T4 nhận `evt-synthetic-001` từ `editorial_fixture`; kiểm tra cùng ID từ `catalog_fixture` trước sửa trả `DUPLICATE_IGNORED`, trong khi kỳ vọng `ACCEPTED_SYNTHETIC`. Nguyên nhân: `seen[event_id]` thay vì tuple namespace. Dòng 100–110 ở trên và `TEST_CASES=9` là **bằng chứng S1 trước D1**, không chứng minh tách namespace; không gộp 9/9 cũ thành chứng cứ chính sách.
- **Sửa chính xác:** `key=(source_system,event_id,schema_version)`; `source_system` là lower snake ASCII 2–48 ký tự; `event_id` là ASCII alnum đầu tiên, rồi alnum/`_`/`-`, dài 2–80; `schema_version` ở **fixture offline** chỉ cho mẫu `0.N-proposal` với `N>=1` (`0.1-proposal`, `0.2-proposal`). Trường thiếu/sai kiểu/sai cú pháp → `BLOCKED_INVALID_EVENT_NAMESPACE` trước khi chạm `seen`. Payload phải là JSON object hợp lệ, canonical JSON `sort_keys=True`, compact separators, `allow_nan=False`; replay cùng tuple cùng payload canonical → `DUPLICATE_IGNORED`; khác payload → `BLOCKED_CONFLICTING_REPLAY`. Cùng event ID khác source hay version hợp lệ được nhận riêng. Version `0.2-proposal` chỉ là **namespace giả để test**, không có event schema v0.2 được phê duyệt hay đường di trú live/backwards compatibility. Đây không phải một whitelist nguồn production.
- **Thực thi:** `python3 -B sandbox/grow02a-offline-validator/validate.py` trên Python `3.14.10`, `Linux-6.12.116+deb13-amd64-x86_64-with-glibc2.41`; validator blob được chạy `d07d2a0fa8df029009689363f494f13393c7c118` (Git blob SHA). 21/21 fixture hiện tại PASS; **12 ca D1 mới** cộng 9 ca S1 chạy lại chỉ vì cùng validator thay đổi. Các ca event 15/15 PASS với 4 khóa composite distinct. JSON `d1_delta` ghi `expected` và `observed` thực tế từng case, lịch sử 9/9 cũ, môi trường, source blob và tác động 0. Không gọi BIZ-02/GROW-01 suites.
- **Delta positive/negative:** T4/T5/T5b nay có đủ source/version; D1-other-source-same-id=`ACCEPTED_SYNTHETIC`, D1-other-source-replay=`DUPLICATE_IGNORED`, D1-other-version-same-id=`ACCEPTED_SYNTHETIC`, D1-other-version-conflict=`BLOCKED_CONFLICTING_REPLAY`; D1-reordered-payload-replay=`DUPLICATE_IGNORED`; D1-missing-source, D1-blank-source, D1-invalid-source-type, D1-missing-version, D1-invalid-version, D1-missing-event-id đều `BLOCKED_INVALID_EVENT_NAMESPACE`. Những đầu vào không hợp lệ không tạo khóa trong `seen`.
- **Bất biến:** So sánh trực tiếp evidence tại base SHA với bản D1: `events` 14/14 và `kpi_links` 16/16 **giữ nguyên từng giá trị**, `a0_pending` 5/5 giữ nguyên `AWAITING_A0_DECISION`; `schema_version`, UTM/consent/mock/side_effects không thay. Không có API thật, tracking, customer data hoặc chi phí. `GROW02A_S1_D1_COMPOSITE_DEDUP_PASS` chỉ là verdict **validator offline**; ChatGPT/Work và A0 vẫn phải review policy/schema độc lập trước bất kỳ triển khai nào.

**D1 handoff:** `TASK=GROW-02A/S1-D1 | AGENT=Hermes WebUI | ACK=ACKNOWLEDGED | BASE_SHA=44dd545e1698f884b41fd8dd49c94929e1415e50 | PR23_HEAD=44dd545e1698f884b41fd8dd49c94929e1415e50 (pre-delta) | TEST_DELTA=12 new / 21 total offline | SCHEMA_AND_NAMESPACE_VERDICTS=composite key, fail-closed namespace, 0.2-proposal synthetic only | EVIDENCE=reports/evidence/2026-11-23-hermes-grow02a-s1-events-and-tests.json | VERDICT=GROW02A_S1_D1_COMPOSITE_DEDUP_PASS | NEXT_OWNER=ChatGPT Điều phối`.

## Nguồn
- [Lệnh PR #20](https://github.com/DuyKienTTD/Hosting/pull/20#issuecomment-7091269345)
- [BIZ-02 branch commit fcdc0f8; lệnh gốc PR #18](https://github.com/DuyKienTTD/Hosting/commit/fcdc0f898b13b19a42a000d84c8ac4632de1806b)
- [BIZ-01 branch commit 8c821bb](https://github.com/DuyKienTTD/Hosting/commit/8c821bbf1842eccb8519127f54ba7673965276d5)
- [GROW-01 branch commit 3c8cb40; lệnh gốc PR #12](https://github.com/DuyKienTTD/Hosting/commit/3c8cb40357ee23d13a2c1aa7e07e6848ff5256dd)
- [ENG-01A S2 PR #13](https://github.com/DuyKienTTD/Hosting/pull/13), [S3 PR #19](https://github.com/DuyKienTTD/Hosting/pull/19), [UX-01 S2 PR #16](https://github.com/DuyKienTTD/Hosting/pull/16)
