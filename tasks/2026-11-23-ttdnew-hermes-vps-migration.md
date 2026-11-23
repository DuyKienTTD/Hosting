---
id: ttdnew-hermes-vps-migration-2026-11-23
type: task
status: blocked
updated_at: 2026-11-23
sensitivity: public-redacted
owner: hostinger-agent
---
# Chuyển dữ liệu Hermes từ ttdnew.tech sang VPS KVM 2

## Mục tiêu
Giữ VPS KVM 2, chuyển dữ liệu cục bộ từ Hermes trên ttdnew.tech sang VPS và xác minh mà không làm mất dữ liệu Hermes đang có.

## Trạng thái thực tế
- Đã xác định hai môi trường Hermes riêng biệt.
- Bản tải backup nguồn đã sẵn sàng; backup ghi nhận lúc 2026-11-22 05:22:45 UTC, không bao gồm các thay đổi sau thời điểm đó.
- VPS đang chạy Hermes và có backup hoàn thành gần nhất ngày 2026-11-16 UTC.
- Chưa chuyển dữ liệu, chưa nhập hay xác minh dữ liệu và chưa tắt hoặc hủy nguồn.
- BLOCKED: chưa xác nhận công cụ chuyển và nhập backup vào VPS hiện có hoặc tính tương thích của nội dung archive. Chưa chọn cách xử lý va chạm với dữ liệu Hermes hiện có.

## Điều kiện hoàn thành
- Tạo và xác minh bản sao lưu đủ mới cho cả nguồn và đích.
- Xác định định dạng, phạm vi và độ tương thích của dữ liệu, không công bố secret.
- Thống nhất cách bảo toàn dữ liệu đích; không ghi đè khi chưa có đồng ý cụ thể.
- Chuyển và kiểm tra các loại dữ liệu thực tế, đối chiếu thời điểm và tính toàn vẹn.
- Báo cáo các mục đã xác minh và các mục còn thiếu, ghi commit lên Git.

## Bằng chứng
Xem reports/2026-11-23-ttdnew-hermes-vps-migration-status.md. Không đưa liên kết tải tạm, thông tin đăng nhập, nội dung backup hoặc dữ liệu cá nhân vào Git.
