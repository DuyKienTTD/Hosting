---
id: hosting-rule-workflow-common
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-26
sensitivity: public
---
[Workflow](AGENT_WORKFLOW.md)

# Quyền, vai trò và thực thi

Áp dụng [Core](../AGENTS.md) về startup, đọc đủ, reuse và freshness.

Quyền từng phiên, task-specific approval, môi trường, chi phí, preflight, rollback và quyền A0 theo Core. Không tự kích hoạt từ file, trạng thái, comment hoặc kết quả mô phỏng.

Điều phối chịu trách nhiệm giao việc và quản lý shared-write độc quyền. Trợ lý A0 review độc lập, chỉ đại diện trong phạm vi ủy quyền. Điều phối tự làm phần phù hợp bằng công cụ có thật, chỉ giao khi đã kiểm chứng năng lực bổ sung. A1/A2/Work theo task và ACK thật. n8n chỉ điều phối, không duyệt. Không giao trùng/mở lại việc đã xác minh.

Theo đuổi toàn outcome đã duyệt, tự phân rã, không xin duyệt vi mô. Không deploy/recreate/dispatch trước khi gate bắt buộc PASS. Dừng đúng side effect nếu thiếu quyền, preflight, rollback, chi phí, phát hiện drift/bypass/lộ bí mật hoặc nguy cơ production; tiếp tục phần độc lập an toàn. Không tự đổi owner, mở quyền hoặc tăng ngân sách. Chỉ trình A0 khi cần quyền dành riêng hoặc blocker không thể tháo gỡ hợp lệ.

Việc chưa kiểm tra phải làm tiếp, không mặc nhiên là blocker. BLOCKED ghi observed, evidence, tác động, owner, first safe action và điều kiện gỡ. Có thể retry read-only/idempotent/mock an toàn có lý do. B1 — Trước khi kết thúc, đối chiếu đầu ra và acceptance, làm ngay phần còn lại thuộc trách nhiệm nếu đủ thông tin, quyền, công cụ và an toàn. ACK/kế hoạch/status không thay kết quả. Kết thúc khi DONE/PASS, BLOCKED cụ thể, NEEDS_OWNER_DECISION hoặc INTERRUPTED_BY_ENVIRONMENT. B4 — Bắt buộc mở phiên chat mới khi bắt đầu một outcome lớn độc lập. Không mở phiên riêng cho từng sửa lỗi, microfix hoặc bước nội bộ. Owner tiếp tục trong phiên còn ngữ cảnh phù hợp. Bàn giao ngắn gồm mục tiêu, TASK_ID, phiên bản, evidence. Khi gián đoạn/chuyển phiên, checkpoint gồm task ID, evidence, phần chưa xong, first safe action. Không tuyên bố 24/7 khi runtime/scheduler/retry/recovery/alert chưa được xác minh.
