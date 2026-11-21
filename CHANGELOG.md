# Lịch sử cập nhật

## 2026-11-21

- Thêm danh bạ vai trò `agents/` cho ChatGPT, Codex, Hermes, Hostinger/Hostinger Agent và n8n, phân biệt capability verified/reported/unknown.
- Đưa lên GitHub task `TTD-AGENT-CAPABILITY-SURVEY-001` để chủ dự án chuyển câu hỏi đến từng tác nhân và nhận báo cáo tự đánh giá.
- Liên kết các hồ sơ vào README, PROJECT, AGENTS, STATE và CATALOG.

- Hoàn tất `TTD-AI-PLATFORM-AUDIT-001` và thêm báo cáo/evidence đã khử định danh cho kiểm toán live n8n ↔ Hermes.
- Xác minh n8n `2.45.7`, Hermes `0.22.5`, network/auth hai chiều và trạng thái runtime; ghi rõ MCP, inference API và end-to-end còn `BLOCKED`.
- Đề xuất kiến trúc n8n control plane + Hermes reasoning + internal network + policy/approval gate + media-worker; cập nhật `PROJECT.md`, `STATE.md`, inventory và catalog.
- Không thay đổi production, không gọi model/media trả phí và không kết nối tài khoản marketing.

- Tạo task `TTD-AI-PLATFORM-AUDIT-001` kiểm toán live n8n ↔ Hermes và thiết kế hệ thống AI Automation dựa trên báo cáo tự đánh giá Hermes.

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
