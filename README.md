# Hosting

Kho lưu trữ tài liệu vận hành, checkpoint và tri thức cho hạ tầng Hosting/VPS.

## Trạng thái hiện tại

- Nhà cung cấp: Hostinger, gói KVM 2 tại Kuala Lumpur, Malaysia.
- Hệ điều hành: Ubuntu 24.04.4 LTS.
- Tài nguyên: 2 vCPU, 8 GB RAM, 100 GB SSD, 8 TB băng thông/tháng.
- Ứng dụng đang chạy: n8n và Hermes Agent qua Docker Compose.
- Ứng dụng `CHUNG_KHOAN_PRO` và Alibaba OneTalk đã bị xóa khỏi VPS ngày 2026-11-21.

## Tài liệu

- [Kiểm kê VPS hiện tại](inventory/VPS_CURRENT_STATE.md)
- [Đánh giá bảo mật](inventory/SECURITY_REVIEW_2026-11-21.md)
- [Quy tắc an toàn repository](rules/REPOSITORY_SECURITY.md)
- [Script kiểm kê an toàn](scripts/vps-audit-safe.sh)
- [Lịch sử cập nhật](CHANGELOG.md)

## Lưu ý bảo mật

Repository này là **công khai**. IP, hostname, mật khẩu, token, khóa API, khóa SSH, nội dung `.env`, dữ liệu cá nhân và bản sao cơ sở dữ liệu không được phép commit. Báo cáo chỉ lưu cấu hình vận hành đã được khử thông tin nhạy cảm.

Cập nhật gần nhất: 2026-11-21.
