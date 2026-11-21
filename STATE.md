---
id: current-state
type: state
status: current
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
---

# Trạng thái hiện tại

Đây là điểm đọc nhanh. Chi tiết đầy đủ nằm trong `inventory/current-vps-state.md`.

## VPS

- Hostinger KVM 2, Ubuntu 24.04.4 LTS, 2 vCPU, 8 GB RAM, 100 GB đĩa.
- Đang chạy n8n và Hermes Agent bằng Docker Compose.
- PostgreSQL và Nginx đang chạy; Nginx hiện không phục vụ site hay chứng chỉ.
- `CHUNG_KHOAN_PRO` và Alibaba OneTalk đã bị xóa khỏi filesystem và dịch vụ đang chạy.
- Hai backup Hostinger cũ có thể vẫn chứa trạng thái trước khi xóa.

## Rủi ro ưu tiên

- SSH cho phép root và mật khẩu.
- XRDP và hai cổng Docker đang công khai.
- Hostinger firewall chưa có quy tắc.
- Có 90 gói cần nâng cấp và VPS cần khởi động lại.
- Hermes chạy bằng root trong container; image n8n/Hermes dùng tag `latest`.

## Nền tảng AI Automation TTD METAL

- Mục tiêu tổng thể: [PROJECT.md](PROJECT.md).
- Đã chuẩn hóa giao nhiệm vụ qua `tasks/`, kết quả qua `reports/`; [quy tắc](rules/AGENT_WORKFLOW.md).
- Báo cáo tự đánh giá Hermes đã được bổ sung tại `reports/2026-11-21-hermes-self-assessment.md`; đã xác minh được skills, session recall, GitHub push và đường tích hợp n8n theo docs, nhưng chưa xác minh API/live n8n.
- Chưa kiểm thử thực tế tích hợp hai chiều n8n ↔ Hermes. Đã giao đặc tả cho Codex tại [TTD-AI-PLATFORM-AUDIT-001](tasks/2026-11-21-n8n-hermes-integration-audit.md); chưa có báo cáo thực thi.

## Việc đang chờ

- Chưa thực hiện hardening SSH/XRDP hoặc firewall.
- Chưa đặt n8n/Hermes sau reverse proxy HTTPS.
- Chưa xử lý các backup Hostinger có thể chứa ứng dụng đã xóa.
- Chưa cập nhật hệ điều hành hoặc reboot.
- Chưa xác minh exact build/version của Hermes Hostinger image hoặc live API endpoint từ runtime hiện tại.

## Tài liệu tiếp theo

- Kiểm kê: `inventory/current-vps-state.md`
- Báo cáo bảo mật: `reports/2026-11-21-vps-security-review.md`
- Quy tắc an toàn: `rules/REPOSITORY_SECURITY.md`
