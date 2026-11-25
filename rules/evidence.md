---
id: hosting-rule-evidence
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-25
sensitivity: public
---
[Workflow index](AGENT_WORKFLOW.md) — candidate; not effective until approved merge and verification.

## 5. Bằng chứng, kiểm thử và nghiệm thu

Đặc tả ghi trạng thái DONE_VERIFIED, DONE_REPORTED, PARTIAL, FAILED, BLOCKED, NOT_RUN kèm URL/commit/môi trường/thời gian/phạm vi. Reuse evidence tương đương; chỉ rerun khi change_trigger, thiếu bằng chứng, lỗi mới, không tái lập hoặc cần độ tươi trước thao tác rủi ro. Ưu tiên targeted tests; không phủ nhận historical PASS, không nâng mock/source/author report thành live hoặc QA độc lập. Phân biệt VERIFIED_LIVE, VERIFIED_MOCK, REPORTED, DOCUMENTED, UNKNOWN, BLOCKED, DESIGNED_NOT_RUN. Báo cáo tiến độ tách maturity/readiness, nêu nguồn, trọng số có căn cứ và sai số; không tính PR chưa merge là sản phẩm live. Nghiệm thu dựa trên khả năng sử dụng, outcome, evidence và reviewer khác tác giả; không dựa vào số test hoặc hình thức. Roadmap-level QA không miễn security/release gate.
