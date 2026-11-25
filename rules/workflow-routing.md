---
id: hosting-rule-workflow-routing
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-26
sensitivity: public
---
[Workflow](AGENT_WORKFLOW.md)

# Định tuyến ngoài KNG và ghi trạng thái

Đọc [STATE](../STATE.md) và nguồn live có thẩm quyền trước phần phụ thuộc. Công việc ngoài KNG HOLD trừ quyền riêng được xác minh. Không mở WS-04. Hostinger PAUSED (resume cần A0 và ACK), Hermes HOLD_NO_NEW_TASKS, Codex NOT_AUTHORIZED; không tự kích hoạt. Không suy diễn quyền từ báo cáo lịch sử.

Khi cập nhật canonical event/field, sinh STATE bằng công cụ đã kiểm chứng; cập nhật CATALOG chỉ khi tri thức dùng chung thay đổi, không sinh mục báo cáo từ sự kiện nghiệm thu. Bảo toàn marker và stable ID/path.
