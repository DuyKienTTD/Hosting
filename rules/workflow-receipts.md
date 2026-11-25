---
id: hosting-rule-workflow-receipts
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-26
sensitivity: public
---
[Workflow](AGENT_WORKFLOW.md)

# Biên nhận B2

PREPARED là tài liệu đã ghi; SENT cần kênh gửi thực; B2 — ACKNOWLEDGED chỉ khi cùng một receipt chứng minh TASK_ID, recipient, session, event/phạm vi, thời điểm và nguồn truy xuất được. ACK review khác ACK thực thi; commit chuẩn bị và bằng chứng task/Agent khác không phải ACK. Thiếu định danh phiên hoặc thuộc tính khác thì giữ PREPARED/UNKNOWN đối với tuyên bố chưa xác minh, không bịa UUID; IN_PROGRESS/DONE cần bằng chứng. Không có kênh thì PREPARED_FOR_OWNER_FORWARD; không giả định Agent chạy nền hoặc GitHub comment tự dừng runtime. Chuyển tiếp chính xác URL, không tạo task trùng.

Task ACK là sự kiện có ngày và receipt.
