# Hosting

Nguồn tri thức chung cho hạ tầng Hosting/VPS: trạng thái hiện tại, kiểm kê, báo cáo, quy tắc, runbook, quyết định và tài liệu tham khảo.

**Mục tiêu nền tảng AI Automation:** [PROJECT.md](PROJECT.md) — media, quảng cáo, SEO, website, mạng xã hội và báo cáo.  
**Danh bạ vai trò/năng lực các tác nhân:** [agents/README.md](agents/README.md) — ChatGPT, Codex, Hermes, Hostinger và n8n.  
**Quy tắc mới về nghiên cứu, phân vai, handoff có xác nhận và cập nhật tri thức:** [AGENT_WORKFLOW mục 7](rules/AGENT_WORKFLOW.md). Mọi AI phải đọc lại quy tắc trước task; không coi GitHub commit là đã thực sự gửi việc.  
**Quy ước giao việc và bàn giao tài liệu qua Git:** [rules/AGENT_WORKFLOW.md](rules/AGENT_WORKFLOW.md).

## Đọc nhanh cho tác nhân

1. Đọc [STATE.md](STATE.md) để biết trạng thái và rủi ro hiện tại.
2. Đọc [CATALOG.yaml](CATALOG.yaml) để tìm tài liệu có thẩm quyền.
3. Chỉ mở tài liệu chi tiết liên quan đến nhiệm vụ.
4. Trước khi thay đổi hạ tầng, xác minh lại dữ liệu có thể đã thay đổi trên hệ thống trực tiếp.
5. Sau khi hoàn tất, cập nhật tài liệu theo [CONTRIBUTING.md](CONTRIBUTING.md).

Quy tắc dành cho tác nhân nằm trong [AGENTS.md](AGENTS.md).

## Trạng thái hiện tại

- Nhà cung cấp: Hostinger, gói KVM 2 tại Kuala Lumpur, Malaysia.
- Hệ điều hành: Ubuntu 24.04.4 LTS.
- Tài nguyên: 2 vCPU, 8 GB RAM, 100 GB SSD, 8 TB băng thông/tháng.
- Ứng dụng đang chạy: n8n và Hermes Agent qua Docker Compose.
- `CHUNG_KHOAN_PRO` và Alibaba OneTalk đã bị xóa khỏi VPS ngày 2026-11-21.

## Tài liệu có thẩm quyền

- [Kiểm kê VPS hiện tại](inventory/current-vps-state.md)
- [Đánh giá bảo mật ngày 2026-11-21](reports/2026-11-21-vps-security-review.md)
- [Quy tắc an toàn repository](rules/REPOSITORY_SECURITY.md)
- [Script kiểm kê an toàn](scripts/vps-audit-safe.sh)
- [Lịch sử cập nhật](CHANGELOG.md)

## Cấu trúc

| Thư mục | Mục đích |
|---|---|
| `inventory/` | Trạng thái và cấu hình hiện tại, được cập nhật tại chỗ |
| `agents/` | Hồ sơ vai trò, khả năng đã thử, giới hạn và cách bàn giao giữa các tác nhân |
| `tasks/` | Đặc tả công việc, phạm vi và nghiệm thu cho từng tác nhân |
| `reports/` | Báo cáo có ngày, audit, sự cố và checkpoint lịch sử |
| `knowledge/` | Kiến thức bền vững, giải thích hệ thống và bài học |
| `runbooks/` | Quy trình vận hành có thể thực hiện từng bước |
| `decisions/` | Quyết định kiến trúc theo dạng ADR |
| `references/` | Liên kết và tài liệu tham khảo bên ngoài |
| `rules/` | Chính sách và giới hạn bắt buộc |
| `scripts/` | Công cụ kiểm tra hoặc tự động hóa an toàn |
| `templates/` | Mẫu thống nhất cho tài liệu mới |
| `archive/` | Tài liệu hết hiệu lực nhưng cần giữ lịch sử |

## Lưu ý bảo mật

Repository này là **công khai**. IP, hostname, mật khẩu, token, khóa API, khóa SSH, nội dung `.env`, dữ liệu cá nhân và bản sao cơ sở dữ liệu không được phép commit. Báo cáo chỉ lưu cấu hình vận hành đã được khử thông tin nhạy cảm.

Cập nhật gần nhất: 2026-11-21.
