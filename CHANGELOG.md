# Lịch sử cập nhật

## 2026-11-21

- Tạo task `TTD-AI-PLATFORM-AUDIT-001` kiểm toán live n8n ↔ Hermes và thiết kế hệ thống AI Automation dựa trên báo cáo tự đánh giá Hermes. Chưa thực hiện kiểm toán VPS.

- Thêm `reports/2026-11-21-hermes-self-assessment.md`, catalog tương ứng và cập nhật `STATE.md` cho đợt tự đánh giá năng lực Hermes Agent hiện tại.
- Ghi nhận đã xác minh được skills, session recall và GitHub push của agent; đồng thời giữ trạng thái chưa kiểm chứng cho exact Hermes build/version, live API endpoint và live n8n integration.

- Thêm `PROJECT.md` xác định mục tiêu nền tảng AI TTD METAL và tiến độ thực tế.
- Thêm `rules/AGENT_WORKFLOW.md` thống nhất giao task qua GitHub, báo cáo trở lại GitHub, quy định tối thiểu không khóa phương pháp.
- Liên kết entrypoint và danh mục cho mọi tác nhân; chuẩn bị `tasks/` cho các đặc tả tiếp theo.

- Tổ chức repository thành nguồn tri thức cho nhiều tác nhân với `AGENTS.md`, `STATE.md` và `CATALOG.yaml`.
- Thêm quy trình đóng góp, cấu trúc inventory/report/knowledge/runbook/decision/reference/archive và các mẫu tài liệu.
- Thêm trình kiểm tra repository để phát hiện metadata, liên kết, catalog hoặc dấu hiệu bí mật không hợp lệ.
- Chuẩn hóa tên file và chuyển báo cáo bảo mật có ngày từ `inventory/` sang `reports/`.
- Khởi tạo cấu trúc tài liệu vận hành cho repository.
- Ghi nhận kiểm kê trực tiếp VPS Hostinger sau khi xóa `CHUNG_KHOAN_PRO` và Alibaba OneTalk.
- Ghi nhận cấu hình n8n, Hermes Agent, Docker, PostgreSQL, Nginx, UFW, Fail2ban, SSH và sao lưu.
- Thêm đánh giá bảo mật và lộ trình cải thiện.
- Thêm quy tắc chống commit bí mật và script kiểm kê chỉ đọc.
