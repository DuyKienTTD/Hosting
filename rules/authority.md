---
id: hosting-rule-authority
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-25
sensitivity: public
---
[Workflow index](AGENT_WORKFLOW.md) — candidate; not effective until approved merge and verification.

## 1. Nguồn và quyền

[MKOE-01](HOSTING-MKOE-01.md) quy định kiến trúc tài liệu và kế hoạch. [AGENTS](../AGENTS.md) là quy tắc cốt lõi và quy định ba nhóm đọc ban đầu. File này là nguồn chi tiết khi thao tác kích hoạt điều kiện điều phối, review, quyền, chi phí hoặc ghi dùng chung. Tuân thủ quy tắc đọc đủ và tái sử dụng theo blob trong AGENTS.

GitHub là kho tri thức, không phải quyền runtime. Xác minh quyền từng phiên, task-specific approval, môi trường, chi phí, preflight và rollback trước side effect. A0 giữ quyền tài chính, production, merge và các quyền dành riêng; ủy quyền phải đúng phạm vi. Không tự kích hoạt từ file, trạng thái, comment hoặc kết quả mô phỏng.
