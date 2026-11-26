# Z6-ROOM-AGENTS · Phòng điều phối qua API

Owner gửi `POST /api/v1/room-messages` với `{ text }`. Ví dụ `@report tóm tắt hội thoại hôm nay` tạo phiếu khi tên agent ở đầu lời nhắn. `@Claude` là bí danh của `@router`. Phản hồi có `task` khi tạo phiếu. `POST /api/v1/work-items` hỗ trợ chọn agent trực tiếp.

Runner đọc phiếu nội bộ từ PostgreSQL. Phiếu chạy theo model đã cấu hình cho vai, qua provider và sổ ngân sách ngày/tháng dùng chung. `@report` chỉ nhận số tổng hợp tin đã lưu trong ngày UTC+7. Agent CRM, điều phối, CSKH và bán hàng chỉ đưa đề xuất lên phiếu. Runner dùng danh sách lựa chọn cố định, kiểm tra vai trước khi tạo kết quả và kiểm tra lại owner, STOP và epoch trước khi gọi AI và khi ghi kết quả. Phiếu cần người xem chuyển sang cột chờ duyệt. Khi mock, runner trả kết quả giả lập và giữ nguyên ngân sách.

Owner xem và quyết định qua `POST /api/v1/work-items/{id}/review` với `{ decision: "accept" | "dismiss" }`. API ghi người duyệt và quyết định. Chấp nhận xác nhận kết quả của phiếu; mọi thao tác nghiệp vụ tiếp theo do người vận hành thực hiện.

`GET /api/v1/agent-router` trả model, quyền, trạng thái bật và chi phí ước tính từng agent cho owner. Dòng chưa phân vai gồm các lượt trước migration. `POST /api/v1/agent-router/{id}/enabled` nhận `{ enabled: boolean }` từ owner. Công tắc dùng cờ STOP theo vai của runtime; Global STOP vẫn có hiệu lực. Các số liệu chi phí lấy từ ledger, gồm khoản dự trữ chưa quyết toán. Cài migration `015-room-agents.sql` trước runtime mới.
