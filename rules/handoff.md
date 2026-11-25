---
id: hosting-rule-handoff
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-25
sensitivity: public
---
[Workflow index](AGENT_WORKFLOW.md) — candidate; not effective until approved merge and verification.

## 7. Bàn giao và lưu lịch sử

Lưu report ngày/task trong reports/, artifact đúng thư mục, log đã khử dữ liệu nhạy cảm; ghi scope, thay đổi, tests PASS/FAIL/BLOCKED, evidence, residual risks, next owner. Commit/push đúng branch, verify remote, cập nhật nguồn trạng thái/index/changelog khi phù hợp. Không ghi đè report cũ, không tạo hồ sơ hành chính trùng. Tin nhắn bàn giao chỉ cần kết quả ngắn trong ô copy, report/commit/PR URL, blocker và next action. B6 — PR dài có một comment trạng thái hiện hành do Điều phối quản lý, dẫn nguồn gốc; chỉ là hiển thị dẫn xuất, không cấp quyền, ACK hoặc nghiệm thu.

Nội dung lịch sử được truy xuất khi cần bằng chứng qua [chỉ mục lịch sử](../references/history/README.md), không phải quyền mới hoặc luồng đọc bắt buộc.
