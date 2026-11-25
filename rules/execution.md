---
id: hosting-rule-execution
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-25
sensitivity: public
---
[Workflow index](AGENT_WORKFLOW.md) — candidate; not effective until approved merge and verification.

## 4. Thực thi liên tục và STOP

Theo đuổi outcome toàn phạm vi đã duyệt, tự phân rã và tiếp tục phần an toàn độc lập, không xin duyệt vi mô. Điều kiện chưa kiểm tra là việc cần làm, không mặc nhiên là blocker. Không deploy/recreate/dispatch trước khi gate bắt buộc PASS. Dừng đúng side effect nếu thiếu quyền, preflight, rollback, chi phí, phát hiện drift/bypass/lộ bí mật hoặc nguy cơ production; tiếp tục phần độc lập an toàn. Không tự đổi owner, mở quyền hoặc tăng ngân sách. Chỉ trình A0 khi cần quyền dành riêng hoặc blocker không thể tháo gỡ hợp lệ.

BLOCKED ghi observed, evidence, tác động, owner, first safe action và điều kiện gỡ chặn; không gọi việc chưa làm là lỗi kỹ thuật. Có thể retry read-only/idempotent/mock an toàn có lý do. B1 — Trước kết thúc lượt, đối chiếu toàn bộ đầu ra và acceptance; kiểm phần còn lại thuộc trách nhiệm, thông tin, quyền, công cụ và phần độc lập an toàn. Nếu khả thi và được phép, thực hiện ngay trong lượt; ACK, kế hoạch hoặc status không thay kết quả. Handoff kết thúc khi DONE/PASS, BLOCKED cụ thể, NEEDS_OWNER_DECISION hoặc INTERRUPTED_BY_ENVIRONMENT; status update không đóng task. B4 — Bắt buộc mở phiên chat mới khi bắt đầu một outcome lớn độc lập. Không mở phiên mới cho từng sửa lỗi, microfix hoặc bước nội bộ của cùng outcome; owner tiếp tục trong phiên hiện tại khi ngữ cảnh còn phù hợp. Bàn giao ngắn gồm mục tiêu, TASK_ID, phiên bản và bằng chứng. Chuyển phiên theo checkpoint tối thiểu. Checkpoint tối thiểu khi gián đoạn: task ID, evidence, phần chưa xong, first safe action. Không tuyên bố 24/7 khi runtime/scheduler/retry/recovery/alert chưa được xác minh.
