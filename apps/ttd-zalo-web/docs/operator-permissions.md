---
id: z4-web-operator-permissions
type: reference
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# Quyền vận hành

| Màn hình | Chủ dự án | CSKH | Bán hàng | A0 |
| --- | --- | --- | --- | --- |
| Tổng quan | Xem | Xem | Xem | Xem |
| Hộp thư khách | Xem, duyệt nháp | Xem, duyệt nháp | Xem | Xem |
| Báo giá | Xem, lưu, duyệt và gửi OA | Xem | Xem, lưu, duyệt và gửi OA | Xem |
| Khách hàng & theo sát | Xem | Xem | Xem | Xem |
| Phòng điều phối | Xem, đăng trao đổi, tạo phiếu | Xem | Xem | Xem |
| Agent & AI Router | Xem | Chặn | Chặn | Xem |
| Kênh Zalo | Xem, bật kill switch | Xem | Xem | Xem |
| Dữ liệu & quyền riêng tư | Xem, yêu cầu xóa | Xem | Xem | Xem |
| Cài đặt | Xem, tạo tài khoản Bán hàng và CSKH | Chặn | Chặn | Xem |

Phiên không có quyền nhận 403 khi gọi API tương ứng. AI Router và Cài đặt tải từ endpoint riêng. Workspace dùng chung không trả provider, model hoặc ngân sách AI Router. Các quyền trên áp dụng cho vai trò người vận hành trong web app.

Cả hai thao tác báo giá yêu cầu chọn khách, quy cách, số lượng hợp lệ, bảng giá đã duyệt và xác nhận. Gửi qua OA còn yêu cầu đủ điều kiện kênh và consent báo giá. Kết quả xếp hàng chưa xác nhận đã giao tin.

[Hợp đồng OpenAPI](api-contract.yaml)
