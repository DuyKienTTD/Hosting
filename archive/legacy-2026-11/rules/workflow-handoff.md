---
id: hosting-rule-workflow-handoff
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-26
sensitivity: public
---
[Workflow](AGENT_WORKFLOW.md)

# Bàn giao và lưu lịch sử

Lưu report ngày/task trong reports/, artifact đúng thư mục, log đã khử dữ liệu nhạy cảm; ghi scope, thay đổi, tests PASS/FAIL/BLOCKED, evidence, residual risks, next owner. Commit/push đúng branch, verify remote, cập nhật nguồn trạng thái/index/changelog khi phù hợp. Không ghi đè report cũ, không tạo hồ sơ hành chính trùng. Tin nhắn bàn giao ngắn trong ô copy: TASK_ID, RESULT, VERDICT (PASS/FAIL/PARTIAL/BLOCKED), EVIDENCE (URL pin đặc tả/report/commit/PR), LIMITS, NEXT_OWNER. Người nhận thực tế ACK đúng task khi nhận. B6 — PR dài có một comment trạng thái hiện hành do Điều phối quản lý, dẫn nguồn gốc; chỉ là hiển thị dẫn xuất, không cấp quyền, ACK hoặc nghiệm thu.

Nội dung lịch sử được truy xuất khi cần bằng chứng qua [chỉ mục lịch sử](../references/history/README.md), không phải quyền mới hoặc luồng đọc bắt buộc.

Handoff ghi task_id, from_agent, to_agent, why_this_agent, objective, first_action, inputs_and_urls, constraints_and_approval, acceptance, deliverable_path, next_owner_or_decision, handoff_state. Đọc thêm [biên nhận B2](workflow-receipts.md) để xác định trạng thái.
