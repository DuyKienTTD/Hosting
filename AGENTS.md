# Hướng dẫn bắt đầu nhiệm vụ HOSTING

Bản tinh gọn candidate ngày 24/11/2026; không tự kích hoạt hoặc mở quyền. Main hiện hành vẫn kiểm soát đến khi tích hợp hợp lệ.

## Đọc trước khi làm

- Xác minh remote main HEAD, đọc đầy đủ [quy tắc vận hành](rules/AGENT_WORKFLOW.md), [bảo mật](rules/REPOSITORY_SECURITY.md), [trạng thái](STATE.md), hồ sơ vai trò và task chính xác. Ghi SHA; nếu nội dung bị cắt, đọc các khoảng dòng liên tục cùng SHA. Không suy đoán phần thiếu.
- [CATALOG](CATALOG.yaml) là chỉ mục tra cứu; công cụ kiểm toàn bộ ID/path, Agent chỉ đọc mục liên quan. [PROJECT](PROJECT.md) là mục tiêu, [README](README.md) là điều hướng.
- [Routing snapshot](program/current.json) và [release gate](program/kng/release_state.py) phải được đối chiếu quyền thực tế. KNG chỉ effective khi A0 phê duyệt exact candidate/tree và có independent remote main merge/tree/ordered parents readback. Thiếu chứng cứ thì STOP new dispatch.

## Phạm vi và trách nhiệm

Chat Điều phối phân công và quản lý shared-write; A0 Assistant reviewer độc lập trong quyền được giao. Không tự mở task, ACK, paid, production, merge, Codex hoặc thay đổi quyền từ Git access. Hostinger/Hermes và công việc ngoài KNG tiếp tục HOLD trừ task grant hợp lệ.

Thực thi theo task, một writer, read/write set, invariants, preflight, cost, STOP, rollback và targeted tests. Tiếp tục phần an toàn không cần duyệt vi mô; không làm lại evidence tương đương. Không tự nghiệm thu độc lập. GitHub commit không phải SENT/ACK; xác minh remote sau push và bàn giao đúng owner.

[Quy tắc chi tiết](rules/AGENT_WORKFLOW.md) là nguồn chính; [lịch sử](references/history/README.md) chỉ tra cứu khi cần. Không lặp quy tắc hoặc status ở nhiều nơi.
