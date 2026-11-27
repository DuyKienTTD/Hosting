---
id: repository-security-rules
type: rule
status: current
updated_at: 2026-11-21
sensitivity: public
---

# Quy tắc an toàn repository

Repository `DuyKienTTD/Hosting` là công khai.

## Không được commit

- File `.env` hoặc bản sao của `.env`.
- Mật khẩu, token, cookie, session ID, API key, OAuth secret.
- SSH private key, TLS private key hoặc seed/recovery phrase.
- Database dump, backup ứng dụng, dữ liệu người dùng.
- IP/hostname thật của máy chủ nếu không có quyết định công khai rõ ràng.
- Log có thông tin xác thực, dữ liệu cá nhân hoặc request payload.

## Được phép commit

- Kiến trúc, phiên bản phần mềm và tài nguyên tổng quát.
- Tên service/container/image/volume/network.
- Port mapping và chính sách firewall đã khử định danh.
- Tên biến môi trường nhưng không có giá trị.
- Runbook, checklist, báo cáo và script chỉ đọc.

## Trước khi push

1. Chạy `git diff --cached` và đọc toàn bộ nội dung.
2. Tìm chuỗi nhạy cảm: `password`, `secret`, `token`, `api_key`, `private key`, `.env`.
3. Xác nhận không có database dump, archive hoặc log lớn.
4. Nếu bí mật từng bị commit, phải thu hồi/rotate bí mật; xóa commit không đủ.
