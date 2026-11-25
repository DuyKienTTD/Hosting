---
id: hosting-rule-workflow-restricted-operations
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-26
sensitivity: public
---
[Workflow](AGENT_WORKFLOW.md)

# Thao tác dành riêng và ngoại lệ chi phí

Cần quyết định A0 đúng phạm vi và còn hiệu lực, preflight, runbook và rollback, STATE và nguồn live phù hợp. Giữ reviewer khác tác giả, CI và remote readback theo gate khi merge. Áp dụng Security và CONTRIBUTING cho Git, cùng gate xóa và [Lifecycle protocol](DATA_LIFECYCLE_CONTEXT.md) khi xóa dữ liệu quản trị.

Giữ các gate VPS/SEC, paid, production, GATE B và real ledger. [Gate B lịch sử](GATE-B-INDEX.md) chỉ điều hướng; kiểm authority live, ledger và kill switch trước phần phụ thuộc.

Codex chỉ ngoại lệ khi có ALTERNATIVES_CHECKED, WHY_ONLY_CODEX, MAX_SCOPE, ESTIMATED_COST_OR_CALL_CAP, STOP, ACCEPTANCE, INDEPENDENT_REVIEWER, A0_APPROVAL_ID; thiếu bất kỳ mục nào thì không dispatch. Hermes ngoại lệ cần chứng minh năng lực không thay thế và A0 duyệt cap token/USD. Không dùng token cộng dồn/ước tính làm invoice; đối soát usage/spend theo phạm vi. Không tìm cách vượt content_policy_blocked. Paid API, render/publish cần approved scope, cost cap, consent, credential, STOP và đối soát. Không tự retry paid hoặc side effect chưa chứng minh idempotency.
