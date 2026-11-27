---
id: hermes-biz02-s1-prioritization-2026-11-23
type: report
status: draft_ready_for_review
updated_at: 2026-11-23
sensitivity: public-redacted
task_id: BIZ-02/S1
owner: hermes-webui
next_owner: chatgpt
---

# BIZ-02/S1 — Hồ sơ quyết định use-case, KPI và ưu tiên (draft)

## ACK và phạm vi
- `EXECUTE BIZ-02/S1`; `MAIN_SHA`/rules: `e385c1bea2070973e3007e5717f7e980348d6ab3`; PR #6 `03fb56b6d3b4f42a1cb65c6e3c87a19099785044`.
- Lệnh: [PR #18 comment 7091126062](https://github.com/DuyKienTTD/Hosting/pull/18#issuecomment-7091126062).[8]
- Đã đọc AGENTS, PROJECT, GOALS_AND_ROADMAP, rules/AGENT_WORKFLOW §§7–10, rules/REPOSITORY_SECURITY, STATE, CATALOG, agents/hermes và task/nguồn liên quan. Git SSH push có khả năng; business account OAuth, khách hàng và production không truy cập.
- BIZ-01 PR #12 (8c821bb) và GROW-01 PR #18 (3c8cb40) được tái sử dụng, không chạy lại.[2][3]
- ENG-01A S1/S2 PR #10/#13 chỉ là offline contract/mock.[4][5]
- UX-01 S1/S2 PR #14/#16 là spec/offline UI; PR #16 browser E2E và backend chưa chứng minh.[6][7]
- Ngữ cảnh sản phẩm: PROJECT xác định các luồng media, Ads, WordPress/Woo, social, reporting.[1] Không có approved customer demand, prices, conversion baseline hay revenue trong READ_SET. `BASELINE_UNKNOWN` cho mọi KPI.
- `WRITE_SET`: chỉ task, report, JSON evidence BIZ-02/S1. Không sửa shared indexes; đề xuất cập nhật CATALOG/STATE/CHANGELOG cho ChatGPT sau coordinated diff review.

## Ma trận phân khúc và persona (giả thuyết, không phải khách hàng thật)
| Persona | Loại | Vùng | Vấn đề cần xác nhận | Mức bằng chứng |
|---|---|---|---|---|
| VI_HOME_INSTALL | end_customer_hypothesis | Vietnam | style/fit questions without engineering claims | PROVISIONAL_FOR_A0 |
| EN_IMPORTER | end_customer_hypothesis | international English-speaking | product fit and trade inquiry | PROVISIONAL_FOR_A0 |
| INTERNAL_MARKETING_SALES | Hosting_operator | internal | auditable draft/review, channel/KPI visibility | PROJECT_DIRECTION_NO_DEMAND_BASELINE |
| PRODUCT_TECH_REVIEW | Hosting_operator | internal | safety/spec signoff before public claims | GROW01_DRAFT_GATE |

Khách hàng cuối (VI/EN) khác **operator dùng nền tảng Hosting** (marketing/sales/reviewer). Phân khúc EN/VI xuất phát từ định hướng PROJECT và bản nháp GROW-01, không chứng minh doanh số hay nhu cầu thị trường.[1][3]

## 8 use case: outcome, workflow, gate và đo lường
Mỗi bản ghi dưới đây là đề xuất đo được *sau khi có nguồn số liệu*. Score/priority không phải authorization. Chi tiết KPI, source, cost, privacy và dependencies nằm trong JSON cùng ID.

### UC06 — Approval queue and incident monitoring draft | MVP_OFFLINE_NOW
- **Outcome/khách hàng/actor:** operator reliability; internal operator and reviewer; operator. **Pain:** unknown outcomes and overdue approvals hide risk.
- **Workflow:** mock queue delay or synthetic incident → synthetic approval/job state → Hermes triage guidance → UX-01 S2 offline UI → review queue with escalation and no automatic retry → duyệt operator reviews; production notification requires separate scope → audit job_id, state transition, decision reason.
- **Source/capability:** project, UX_S2, ENG_S1; OFFLINE_MOCK_ONLY / BACKEND_UNIMPLEMENTED; PR hiện có #16, #10. Source status `PROJECT_DIRECTION_AND_PROVISIONAL_HYPOTHESIS`. Không biến vendor docs hoặc mock thành quyền tài khoản.
- **Expected value (testable, chưa đo):** hypothesis to test after baseline; no numeric benefit promised. Leading `triage_coverage`; lagging `mean_synthetic_resolution_time`. Cả hai `BASELINE_UNKNOWN`.
- **Recovery/cost/privacy:** unknown outcome -> hold and escalate; no automatic retry; no paid or live alert action; metadata only, no payload in shared logs.
- **Dependencies:** UX-01 S2, ENG-01A S1, Hostinger infra/security baseline; **illustrative score** 3.500/4.

### UC01 — WP/Woo content and product inventory gap detection | MVP_OFFLINE_NOW
- **Outcome/khách hàng/actor:** content readiness; internal marketing/operator; editor. **Pain:** manual content audit and missing metadata.
- **Workflow:** weekly draft audit → synthetic posts/pages/products and approved taxonomy → Hermes analysis of gaps → ENG-01A S2 fake read adapter → gap list with provenance and human review → duyệt human editor; real read requires site owner consent → audit report version + source watermark.
- **Source/capability:** project, BIZ01, ENG_S2; DOCUMENTED / VERIFIED_IN_PROJECT_SITE / UNVERIFIED_ACCOUNT_ACCESS / OFFLINE_MOCK_ONLY; PR hiện có #13. Source status `PROJECT_DIRECTION_AND_PROVISIONAL_HYPOTHESIS`. Không biến vendor docs hoặc mock thành quyền tài khoản.
- **Expected value (testable, chưa đo):** hypothesis to test after baseline; no numeric benefit promised. Leading `inventory_review_coverage`; lagging `resolved_content_gap_rate`. Cả hai `BASELINE_UNKNOWN`.
- **Recovery/cost/privacy:** 403/429/timeout -> UNKNOWN; retain last verified snapshot, no write; zero paid calls; offline only; only synthetic catalog content; avoid unpublished product facts.
- **Dependencies:** BIZ-01, #13, ENG-01A S3 for integration; **illustrative score** 3.300/4.

### UC04 — Multilingual P1/P2/P3 draft and rights QA | MVP_OFFLINE_NOW
- **Outcome/khách hàng/actor:** editorial throughput; VI homeowner/installer and EN importer hypotheses; editor + product reviewer. **Pain:** content production slow and claims may lack rights or technical approval.
- **Workflow:** approved draft request → synthetic P1/P2/P3 briefs only → Hermes drafts and QA flags → GROW-01 runbook and fake gate → draft package with blocked/needs-review states → duyệt business + rights + engineer + privacy; no real approval in S1 → audit package version and reviewer decision references.
- **Source/capability:** project, GROW01, BIZ01; OFFLINE_DRAFT_ONLY / UNVERIFIED_ACCOUNT_ACCESS; PR hiện có #18. Source status `PROJECT_DIRECTION_AND_PROVISIONAL_HYPOTHESIS`. Không biến vendor docs hoặc mock thành quyền tài khoản.
- **Expected value (testable, chưa đo):** hypothesis to test after baseline; no numeric benefit promised. Leading `draft_review_completion`; lagging `QA_rework_rate`. Cả hai `BASELINE_UNKNOWN`.
- **Recovery/cost/privacy:** unapproved spec/rights -> BLOCKED; preserve original draft; zero paid render and no publish; placeholder assets only; consent/rights UNKNOWN.
- **Dependencies:** GROW-01, BIZ-02 KPI decision, product engineer for P2; **illustrative score** 3.300/4.

### UC03 — UTM source and lead funnel reporting design | MVP_OFFLINE_NOW
- **Outcome/khách hàng/actor:** measurement correctness; marketing and sales operators; analyst. **Pain:** clicks, messages and qualified leads are conflated.
- **Workflow:** new campaign brief or weekly mock review → synthetic campaign/source and separate form/chat/CRM aggregates → Hermes designs reconciled definitions → offline event schema only → illustrative funnel with missing join marked UNKNOWN → duyệt privacy owner must approve join and event policy separately → audit UTM taxonomy + separate aggregate source provenance.
- **Source/capability:** project, BIZ01, GROW01, ENG_S1; DOCUMENTED / OFFLINE_DESIGN_ONLY / UNVERIFIED_ACCOUNT_ACCESS; PR hiện có #10, #18. Source status `PROJECT_DIRECTION_AND_PROVISIONAL_HYPOTHESIS`. Không biến vendor docs hoặc mock thành quyền tài khoản.
- **Expected value (testable, chưa đo):** hypothesis to test after baseline; no numeric benefit promised. Leading `UTM_validity_rate`; lagging `qualified_lead_rate`. Cả hai `BASELINE_UNKNOWN`.
- **Recovery/cost/privacy:** missing source key -> UNKNOWN, separate totals; no inferred attribution; no spend; design only; do not join identity or export customer data.
- **Dependencies:** BIZ-01, GROW-01, GROW-02A future full dictionary, ENG-01A S3; **illustrative score** 2.800/4.

### UC02 — GA4 read-only channel aggregate review | NEXT_AFTER_READ_AUTH
- **Outcome/khách hàng/actor:** channel visibility; internal marketing/operator; analyst. **Pain:** no trusted source-level performance baseline.
- **Workflow:** weekly reporting proposal → synthetic aggregate rows by date/source/medium → Hermes comparison → ENG-01A S2 fake GA4 read adapter → channel trends with provenance, never customer identity → duyệt GA4 property owner verifies read scope before real use → audit source/date window + freshness flag.
- **Source/capability:** project, BIZ01, ENG_S2; DOCUMENTED / UNVERIFIED_ACCOUNT_ACCESS / OFFLINE_MOCK_ONLY; PR hiện có #13. Source status `PROJECT_DIRECTION_AND_PROVISIONAL_HYPOTHESIS`. Không biến vendor docs hoặc mock thành quyền tài khoản.
- **Expected value (testable, chưa đo):** hypothesis to test after baseline; no numeric benefit promised. Leading `channel_attribution_coverage`; lagging `engaged_session_rate`. Cả hai `BASELINE_UNKNOWN`.
- **Recovery/cost/privacy:** quota/403/timeout -> stale/unknown; no retry that implies complete data; read-only permission required; cost unknown until owner plan; aggregate data only; no identity join.
- **Dependencies:** BIZ-01, #13, GA4 property owner read grant, ENG-01A S3; **illustrative score** 2.500/4.

### UC05 — Manual approved publish handoff | LATER_WITH_SEPARATE_WRITE_APPROVAL
- **Outcome/khách hàng/actor:** controlled distribution; internal marketing/publisher; publisher. **Pain:** inconsistent signoffs and handoff receipts.
- **Workflow:** real publication request AFTER separate authorization → human-approved package and channel-owner permission → Hermes prepares export checklist only → no live connector in S1 → handoff receipt draft; actual publish outside S1 → duyệt separate business, rights, account, spend and final publish approval → audit signed decision IDs and published URL only after actual action.
- **Source/capability:** GROW01, BIZ01, UX_S2; DOCUMENTED / UNVERIFIED_ACCOUNT_ACCESS / FRONTEND_MOCK_ONLY; PR hiện có #18, #16. Source status `PROJECT_DIRECTION_AND_PROVISIONAL_HYPOTHESIS`. Không biến vendor docs hoặc mock thành quyền tài khoản.
- **Expected value (testable, chưa đo):** hypothesis to test after baseline; no numeric benefit promised. Leading `handoff_gate_completeness`; lagging `authorized_publish_success_rate`. Cả hai `BASELINE_UNKNOWN`.
- **Recovery/cost/privacy:** missing rights/permission -> STOP, no export to platform; approval + channel owner; paid render prohibited; no content/PII leakage; manual owner action only.
- **Dependencies:** GROW-01, SEC-01 rights, account owner write approval; **illustrative score** 2.100/4.

### UC07 — Customer inquiry triage with human handoff | NEXT_AFTER_READ_AUTH
- **Outcome/khách hàng/actor:** response quality; VI homeowner/installer and EN importer hypotheses; sales operator. **Pain:** unclassified requests may sit in inbox.
- **Workflow:** future consented inbound inquiry → synthetic message categories, no real text → Hermes classifies draft labels → offline-only schema; no connected mailbox → human queue item, not automatic reply → duyệt consent + sales owner approval → audit synthetic case ID, category and reviewer.
- **Source/capability:** project, BIZ01, GROW01; DOCUMENTED / UNVERIFIED_ACCOUNT_ACCESS / NO_LIVE_INBOX; PR hiện có NONE_FOR_REAL_PATH. Source status `PROJECT_DIRECTION_AND_PROVISIONAL_HYPOTHESIS`. Không biến vendor docs hoặc mock thành quyền tài khoản.
- **Expected value (testable, chưa đo):** hypothesis to test after baseline; no numeric benefit promised. Leading `synthetic_triage_coverage`; lagging `qualified_inquiry_handoff_rate`. Cả hai `BASELINE_UNKNOWN`.
- **Recovery/cost/privacy:** ambiguity or consent unknown -> human queue, no send; no email send or provider spend; customer text/PII not accessed in S1.
- **Dependencies:** BIZ-01, SEC-01 privacy, mailbox owner read approval, ENG-01A S3 if authorized; **illustrative score** 1.700/4.

### UC08 — Paid Ads optimization proposal | LATER_WITH_SEPARATE_WRITE_APPROVAL
- **Outcome/khách hàng/actor:** spend efficiency; marketing account owner; campaign manager. **Pain:** optimization lacks trustworthy conversion evidence.
- **Workflow:** future owner-approved campaign review → consented performance aggregates and budget guard → Hermes proposes changes only → Ads docs; no live account → recommendation draft, no mutation → duyệt A0 budget + account owner + separate write approval → audit change proposal ID, before/after only after real approval.
- **Source/capability:** project, BIZ01; DOCUMENTED / UNVERIFIED_ACCOUNT_ACCESS / NOT_APPROVED_FOR_WRITE; PR hiện có NONE_FOR_REAL_PATH. Source status `PROJECT_DIRECTION_AND_PROVISIONAL_HYPOTHESIS`. Không biến vendor docs hoặc mock thành quyền tài khoản.
- **Expected value (testable, chưa đo):** hypothesis to test after baseline; no numeric benefit promised. Leading `proposal_review_coverage`; lagging `cost_per_qualified_lead`. Cả hai `BASELINE_UNKNOWN`.
- **Recovery/cost/privacy:** unknown billing/attribution -> no optimization action; explicit spend ceiling and rollback; none authorized here; no Ads login or customer export.
- **Dependencies:** BIZ-01, GROW-02A policy, A0 budget approval, ENG-01B real connector approval; **illustrative score** 1.600/4.

## KPI tree và định nghĩa đo
Mục tiêu → nguồn/độ sạch dữ liệu → hoạt động draft/read → kết quả đã được con người xác nhận. `click`/GA4 session là aggregate tương tác; `chat message` là thông điệp; `form submission` là yêu cầu gửi biểu mẫu; `CRM lead` là hồ sơ được đồng ý xử lý; `qualified lead` là quyết định đủ chuẩn của sales. Không tự quy đổi hay join person-level. Mọi mẫu số bằng 0/không có nguồn → `UNKNOWN`, không tự hiển thị 0%.

| Use case | KPI | Tử số | Mẫu số | Đơn vị/cửa sổ | Owner | Attribution/dedup/consent | Baseline |
|---|---|---|---|---|---|---|---|
| UC06 | triage_coverage | synthetic blocked/unknown items with owner | synthetic blocked/unknown items created | ratio; weekly | operator | unique job_id+state transition; replay same ID not counted twice; NO_REAL_CUSTOMER_DATA | BASELINE_UNKNOWN |
| UC06 | mean_synthetic_resolution_time | sum of elapsed minutes for resolved synthetic incidents | number of resolved synthetic incidents | minutes per resolved incident; monthly | operator | exclude open incidents; real incident stream unavailable; BASELINE_UNKNOWN | BASELINE_UNKNOWN |
| UC01 | inventory_review_coverage | fake records reviewed | fake records in selected fixture | ratio; weekly | content owner | version/site+locale+record ID, dedup update watermark; NO_REAL_CUSTOMER_DATA | BASELINE_UNKNOWN |
| UC01 | resolved_content_gap_rate | gaps marked resolved after human check | unique confirmed content gaps | ratio; monthly | content owner | one gap per record+field+version, no live site inference; REQUIRES_OWNER_REVIEW | BASELINE_UNKNOWN |
| UC04 | draft_review_completion | synthetic drafts with all mandatory QA fields | synthetic drafts submitted for review | ratio; weekly | editorial owner | stable package_id/version; not count of published content; NO_REAL_CUSTOMER_DATA | BASELINE_UNKNOWN |
| UC04 | QA_rework_rate | reviewed drafts returned for substantive correction | reviewed drafts with recorded decision | ratio; monthly | editorial owner | one review decision per package version; REQUIRES_RIGHTS_REVIEW | BASELINE_UNKNOWN |
| UC03 | UTM_validity_rate | synthetic campaign links with valid source+medium+campaign | synthetic campaign links checked | ratio; weekly | marketing owner | dedup normalized URL; GROW-02A owns full dictionary; NO_PII | BASELINE_UNKNOWN |
| UC03 | qualified_lead_rate | CRM leads explicitly qualified by sales | distinct consented CRM leads reviewed | ratio; monthly | sales owner | no person join to GA4/chat without key/consent; do not infer from clicks; UNKNOWN_REQUIRES_CONSENT | BASELINE_UNKNOWN |
| UC02 | channel_attribution_coverage | aggregate sessions with channel tag | all aggregate sessions for same property/window | ratio; weekly | analytics owner | GA4 property/date/channel only; do not infer unique people; READ_AUTH_PENDING | BASELINE_UNKNOWN |
| UC02 | engaged_session_rate | GA4 engaged sessions | GA4 sessions | ratio; monthly | analytics owner | GA4 definitions/property only; no form/lead joins; READ_AUTH_PENDING | BASELINE_UNKNOWN |
| UC05 | handoff_gate_completeness | packages with all separately verified approvals | packages submitted for real handoff | ratio; weekly | publisher | package_id+version; synthetic signoffs excluded; REQUIRES_CONSENT | BASELINE_UNKNOWN |
| UC05 | authorized_publish_success_rate | real authorized posts confirmed by platform | real attempted authorized posts | ratio; monthly | account owner | platform post ID; never count exported drafts as posts; REQUIRES_APPROVAL | BASELINE_UNKNOWN |
| UC07 | synthetic_triage_coverage | synthetic inquiries assigned a category and reviewer | synthetic inquiries provided | ratio; weekly | sales owner | one case ID per inquiry, not contact identity; NO_REAL_CUSTOMER_DATA | BASELINE_UNKNOWN |
| UC07 | qualified_inquiry_handoff_rate | consented inquiries sales explicitly accepts as qualified | consented inquiries human-reviewed | ratio; monthly | sales owner | separate messages/inquiries from qualified leads; no merge with GA4; CONSENT_AND_READ_AUTH_PENDING | BASELINE_UNKNOWN |
| UC08 | proposal_review_coverage | Ads proposals reviewed by budget owner | Ads proposals submitted | ratio; monthly | ads owner | campaign ID scope only, no customer identity; ACCOUNT_ACCESS_UNKNOWN | BASELINE_UNKNOWN |
| UC08 | cost_per_qualified_lead | approved campaign spend in currency | distinct consented qualified leads attributed under reviewed policy | currency per qualified lead; monthly | ads + sales owners | attribution policy and dedup required; never equate clicks with leads; ATTRIBUTION_AND_CONSENT_UNKNOWN | BASELINE_UNKNOWN |

6 event names *đề xuất tối thiểu*, không phải dictionary GROW-02A và không emit:
`content_draft_submitted`, `content_review_decided`, `catalog_gap_detected`, `campaign_link_checked`, `lead_form_submitted`, `inquiry_qualified`.
Naming: `lower_snake_case`, nghĩa ổn định, không nhúng PII; `lead_form_submitted` không đồng nghĩa `inquiry_qualified`. GROW-02A chịu trách nhiệm event dictionary đầy đủ, consent và attribution taxonomy.

## Ưu tiên theo score minh họa và hard gates
Trọng số giả định: impact 30%, evidence confidence 20%, ease of delivery 20%, safety/approval ease 20%, dependency ease 10%. Điểm mỗi chiều 0–4 ordinal; `Σ(weight × grade)/100`, không phải ROI hay forecast. Trọng số và điểm đều chờ A0 xem xét. Hard gate ưu tiên cao hơn điểm: không auth đọc → không NEXT live; có publish/paid/PII join → LATER bất kể impact.
| Rank | UC | Điểm /4 | Tier | Hard gate |
|---|---|---:|---|---|
| 1 | UC06 | 3.500 | MVP_OFFLINE_NOW | synthetic only |
| 2 | UC01 | 3.300 | MVP_OFFLINE_NOW | synthetic only |
| 3 | UC04 | 3.300 | MVP_OFFLINE_NOW | synthetic only |
| 4 | UC03 | 2.800 | MVP_OFFLINE_NOW | synthetic only |
| 5 | UC02 | 2.500 | NEXT_AFTER_READ_AUTH | owner verifies read scope and consent |
| 6 | UC05 | 2.100 | LATER_WITH_SEPARATE_WRITE_APPROVAL | separate write/budget/privacy approval |
| 7 | UC07 | 1.700 | NEXT_AFTER_READ_AUTH | owner verifies read scope and consent |
| 8 | UC08 | 1.600 | LATER_WITH_SEPARATE_WRITE_APPROVAL | separate write/budget/privacy approval |

- `MVP_OFFLINE_NOW`: UC01, UC03, UC04, UC06 chỉ fixture/report/draft; không đọc account thật.
- `NEXT_AFTER_READ_AUTH`: UC02, UC07 chỉ sau khi owner xác minh quyền đọc, phân loại dữ liệu và consent. Phần thiết kế UC02 có thể làm offline, nhưng UC02 ở bảng chỉ xếp theo **business realization**.
- `LATER_WITH_SEPARATE_WRITE_APPROVAL`: UC05, UC08; giao package thủ công sau nhiều chữ ký khác hẳn quyền publish thật. Ads optimization/marketing spend chỉ sau decision riêng.
- **Dependency chain:** PROJECT + BIZ-01 (khả năng, không credential) → GROW-01 draft/rights → BIZ-02/A0 KPI choice.[1][2][3]
- Codex ENG-01A S3 tại PR #19 đã báo cáo tích hợp **offline fixture** 8/8, không phải integration live; Work UX-01 S2 chỉ UI mock.[7][9] Hostinger INF/SEC cần xác minh rủi ro hạ tầng trước mọi runtime; GROW-02A mới làm dictionary đầy đủ. Không gọi ENG-01A S1/S2/S3 hay UX-S2 là live.

## ROI và cost framework (công thức, không có số liệu)
| Đại lượng | Công thức hoặc ranh giới |
|---|---|
| `labor_saved_hours` | eligible_cases * (manual_minutes_per_case - assisted_minutes_per_case) / 60 - QA_minutes / 60; avoid double counting |
| `labor_value` | labor_saved_hours * fully_loaded_hourly_cost; value unknown until A0 supplies data |
| `cost_per_qualified_lead` | approved_campaign_spend / distinct_consent_based_qualified_leads; undefined when denominator=0 or attribution policy absent |
| `campaign_efficiency` | qualified_leads_attributed / approved_campaign_spend; not computable absent policy/spend |
| `content_throughput` | human_approved_packages / editorial_period; drafts != approved != published |
| `qa_rework` | returned_package_versions / reviewed_package_versions |
| `total_incremental_cost` | infra_delta + provider_inference + media_render + connector_subscription + review_labor + approved_campaign_spend |
| `net_roi` | (attributable_incremental_margin + defensible_labor_value - total_incremental_cost) / total_incremental_cost; undefined for zero or unknown cost |

Không cộng attributed margin vào lợi ích nếu chưa có attribution/consent policy và baseline đối chứng. Không quy đổi views, clicks, form messages thành qualified leads. Mọi mẫu số 0/UNKNOWN => công thức undefined, không thay bằng 0.

### Data request register — chỉ hỏi owner, không thu thập ở S1
| Owner | Dữ liệu thật tối thiểu cần cấp ở bước riêng | Vì sao | Trạng thái |
|---|---|---|---|
| A0/business | target segment, qualification criteria, success KPI, RPO/retention and allowable spend | decision | NOT_COLLECTED |
| marketing/content owner | manual and assisted minutes by workflow, review time, package versions, approval timestamps | labor/QA | NOT_COLLECTED |
| site owner | read-only WP/Woo API scope, site/locale taxonomy and record counts | catalog | NOT_COLLECTED |
| GA4 property owner | aggregate sessions, engaged sessions, channel tags, attribution settings, read access | analytics | NOT_COLLECTED |
| form/CRM and privacy owner | consented form submissions, distinct lead IDs, qualification decisions, dedup and retention policy | lead | NOT_COLLECTED |
| Ads/budget owner | approved spend by currency/date/campaign, platform fees and budget cap | cost | NOT_COLLECTED |
| infra/provider owner | incremental hosting, model usage/rates, media render bills, connector subscriptions | cost | NOT_COLLECTED |

## A0 decision register — tất cả AWAITING_A0_DECISION
| ID | Lựa chọn cần chốt | Options | Khuyến nghị tạm và lý do |
|---|---|---|---|
| A0-1 | Đối tượng đầu tiên? | VI homeowner/installer; EN importer/distributor; internal operator only | internal operator only for offline MVP; external segment choice remains A0; no customer demand evidence. `AWAITING_A0_DECISION` |
| A0-2 | KPI chính sau khi có dữ liệu? | qualified consented leads; editorial QA throughput; channel aggregate visibility | editorial QA throughput for offline MVP; qualified leads only after consented source; mock data cannot prove lead value. `AWAITING_A0_DECISION` |
| A0-3 | Nguồn dữ liệu mở đọc đầu tiên? | WP/Woo inventory; GA4 aggregates; manual CRM export with consent | WP/Woo read after owner confirms scope; mock first; site presence known; real API rights not verified. `AWAITING_A0_DECISION` |
| A0-4 | MVP slice? | editorial+approval mock; catalog gap report mock; full cross-channel live dashboard | editorial+approval mock, then catalog gap report mock; reuses GROW/UX/ENG offline; avoids live joins. `AWAITING_A0_DECISION` |
| A0-5 | Cadence and retention? | weekly aggregate review + A0-defined retention; monthly aggregate review + A0-defined retention; defer until policy owner decides | weekly synthetic review only; real retention deferred to A0/privacy owner; no approved data retention policy. `AWAITING_A0_DECISION` |

## Tabletop negative case và kiểm thử
Fixture `NEG-01`: giả lập đề xuất auto-publish TikTok và join GA4 aggregate với CRM lead định danh khi chưa có OAuth, consent, spend cap hay publisher approval. **Expected**: LATER/BLOCKED, không vào MVP. **Observed trong policy evaluator offline**: LATER/BLOCKED. Không có request tới API thật, không tạo lead hay chiến dịch. JSON evidence giữ input/expected/observed và phép tính từng UC. Test này không chứng minh deployed gate.

## Blocker, nguồn và bàn giao
- `BASELINE_UNKNOWN` cho toàn bộ KPI và ROI. Account rights, audience demand, revenue, lead definitions và consent chưa được xác minh. A0 chưa quyết định 5 mục.
- No paid API, account access, publish, migration, production write or customer data; phê duyệt chỉ là đề xuất.
- Index follow-up sau coordinated review: ChatGPT cân nhắc đăng ký ba artifact vào CATALOG, tóm tắt STATE và CHANGELOG; không sửa trong WRITE_SET này.

**Sources (fetched GitHub refs):**
- project: PROJECT.md@e385c1bea2070973e3007e5717f7e980348d6ab3
- roadmap: GOALS_AND_ROADMAP.md@e385c1bea2070973e3007e5717f7e980348d6ab3
- BIZ01: https://github.com/DuyKienTTD/Hosting/commit/8c821bbf1842eccb8519127f54ba7673965276d5
- GROW01: https://github.com/DuyKienTTD/Hosting/commit/3c8cb40357ee23d13a2c1aa7e07e6848ff5256dd
- ENG_S1: https://github.com/DuyKienTTD/Hosting/pull/10
- ENG_S2: https://github.com/DuyKienTTD/Hosting/pull/13
- UX_S1: https://github.com/DuyKienTTD/Hosting/pull/14
- UX_S2: https://github.com/DuyKienTTD/Hosting/pull/16
- ENG_S3: https://github.com/DuyKienTTD/Hosting/pull/19 (head `c343f7dded47a67e385ab05b8bb46aed88444f15`; offline only, reported)

**Final handoff:** `TASK=BIZ-02/S1 | AGENT=Hermes WebUI | MAIN_SHA=e385c1bea2070973e3007e5717f7e980348d6ab3 | EXECUTE_ACK=ACKNOWLEDGED | USE_CASES=UC01..UC08 | KPI_TREE=16 KPI formulas + six event-name proposals, all BASELINE_UNKNOWN | PRIORITY_TIERS=3, gated | A0_DECISIONS=5 AWAITING_A0_DECISION | TABLETOP=NEG-01 PASS_OFFLINE_ONLY | EVIDENCE=reports/evidence/2026-11-23-hermes-biz02-s1-priority-matrix.json | VERDICT=BIZ02_S1_PRIORITIZATION_DRAFT_READY_FOR_REVIEW | BLOCKERS=business baselines, rights, consent, account auth, spend approval unknown | NEXT_OWNER=chatgpt`

## Sources

[1] https://github.com/DuyKienTTD/Hosting/blob/e385c1bea2070973e3007e5717f7e980348d6ab3/PROJECT.md
[2] https://github.com/DuyKienTTD/Hosting/commit/8c821bbf1842eccb8519127f54ba7673965276d5
[3] https://github.com/DuyKienTTD/Hosting/commit/3c8cb40357ee23d13a2c1aa7e07e6848ff5256dd
[4] https://github.com/DuyKienTTD/Hosting/pull/10
[5] https://github.com/DuyKienTTD/Hosting/pull/13
[6] https://github.com/DuyKienTTD/Hosting/pull/14
[7] https://github.com/DuyKienTTD/Hosting/pull/16
[8] https://github.com/DuyKienTTD/Hosting/pull/18
[9] https://github.com/DuyKienTTD/Hosting/pull/19
