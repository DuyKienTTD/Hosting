---
id: hermes-gov01-s2-a0-options-2026-11-23
type: business-approval-dossier
status: completed-draft-pending-a0
updated_at: 2026-11-23
sensitivity: public-redacted
---
# GOV-01/S2 — A0 Decision-Ready Options Pack

`TASK=GOV-01/S2 | AGENT=Hermes WebUI | MAIN_SHA=e385c1b | SOURCE_BIZ01=fcdc0f8 | SOURCE_BIZ02_S2=6b2a770 | SOURCE_GROW02A=f2f092a | NEXT_OWNER=chatgpt`

## Authority boundary

Năm quyết định A0 giữ nguyên trạng thái `AWAITING_A0_DECISION`. Các đề xuất bên dưới đều là `PROPOSAL_NOT_APPROVED`. A0/user là decision owner. Không có lựa chọn nào trong hồ sơ này phê duyệt ngân sách, consent, retention, connector, publish, paid API hoặc production write.

## Five choices

| ID | Câu hỏi | Options | Proposal, chưa phê duyệt | Risk / benefit / cost boundary | Minimum evidence and dependency |
|---|---|---|---|---|---|
| A0-1 | Đối tượng đầu tiên? | VI homeowner/installer; EN importer/distributor; internal operator only | Internal operator only cho offline MVP | Lợi ích: scope an toàn; rủi ro: không chứng minh demand bên ngoài; chi phí offline không spend, live segment cần approval | A0 chọn segment, demand evidence; dependency business scope/consent |
| A0-2 | KPI chính sau khi có dữ liệu? | Qualified consented leads; editorial QA throughput; channel aggregate visibility | Editorial QA throughput cho offline MVP | Lợi ích: đo được offline; rủi ro: chưa phải revenue; lead KPI cần consented source và baseline | KPI definition, baseline plan; dependency A0-3/privacy |
| A0-3 | Nguồn dữ liệu mở đọc đầu tiên? | WP/Woo inventory; GA4 aggregates; manual CRM export with consent | WP/Woo read sau owner xác nhận scope, mock trước | Lợi ích: inventory đã biết; rủi ro: rights/consent chưa xác minh; read-only không publish | Owner consent, field allow-list, identity and privacy scope |
| A0-4 | MVP slice? | Editorial+approval mock; catalog gap report mock; full cross-channel live dashboard | Editorial+approval mock, sau đó catalog gap report mock | Lợi ích: tái dùng offline; rủi ro: không chứng minh live; dashboard cần connector/budget/consent | Synthetic journeys, field dictionary, approved connectors nếu đi live |
| A0-5 | Cadence and retention? | Weekly aggregate review + A0-defined retention; monthly aggregate review + A0-defined retention; defer until policy owner decides | Weekly synthetic review; retention thật deferred | Lợi ích: cadence rõ trong mock; rủi ro: retention chưa approved; không lưu data thật | Privacy owner retention decision, source scope, dependency A0-2/A0-3 |

## Binding implications matrix

| Decision | Option proposal affects | Would unlock if later approved | Never unlocks automatically | Authority |
|---|---|---|---|---|
| A0-1 | personas, copy, workflow audience | offline segment-specific mock | demand proof, outreach, spend | A0 |
| A0-2 | KPI tree, QA reports, event dictionary | selected offline measurement | revenue claim, attribution or optimization | A0 |
| A0-3 | source adapter, fields, consent | approved read-only source | identity join, CRM export or publish | A0 + data/privacy owner |
| A0-4 | MVP backlog, UX, ENG mock | selected offline slice | live dashboard, connector or paid action | A0 |
| A0-5 | cadence, retention, reporting | synthetic review cadence | real retention or data processing | A0 + privacy owner |

## Three tabletop safety scenarios

1. **SC-01, offline demo only:** editorial/approval mock remains `SAFE_OFFLINE_ONLY`; it unlocks only synthetic workflow, never live publish, paid API or production write.
2. **SC-02, GA4 without owner consent:** result is `BLOCKED_PENDING_CONSENT`; no query or identity join is permitted.
3. **SC-03, paid Ads optimization without budget/provider/publisher approval:** result is `LATER_BLOCKED`; no spend, publish or production connector is unlocked.

## Acceptance

- Register has exactly five unique IDs, each with 2–3 options.
- All five actual statuses remain `AWAITING_A0_DECISION`.
- Every recommendation is explicitly `PROPOSAL_NOT_APPROVED`.
- Validator: schema PASS, 5 decisions, unique IDs, no implicit approval.
- Scenarios: 3/3 observed equals expected.
- No customer data, live account access, paid API, publish, migration or production write.

## Verdict

`GOV01_S2_A0_OPTIONS_PASS_PENDING_A0`.

This is a decision-ready dossier, not an A0 decision and not an execution authorization.
