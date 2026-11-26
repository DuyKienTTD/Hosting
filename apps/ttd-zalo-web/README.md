# TTD Zalo Assistant

Ứng dụng vận hành 8 màn hình bằng React, TypeScript và Vite. Dữ liệu phát triển dùng MSW với khách, tin nhắn, sản phẩm, kênh và tài khoản giả lập.

## Chạy tại máy

Yêu cầu Node.js 24 và npm.

```sh
npm ci
npm run dev
```

Mở URL do Vite in ra và chọn một tài khoản giả lập. Làm mới toàn bộ trang sẽ đặt lại dữ liệu demo. Đăng xuất để thử vai trò khác.

| Vai trò | Thao tác trong bản giả lập |
| --- | --- |
| Chủ dự án | Duyệt nháp, lập báo giá, tạo phiếu, bật kill switch, yêu cầu xóa |
| CSKH | Duyệt nháp |
| Bán hàng | Lập báo giá |
| A0 | Duyệt nháp, lập báo giá, tạo phiếu, bật kill switch, yêu cầu xóa |

Bảng trên mô tả quyền thao tác UI dự kiến cho tài khoản vận hành. Quyền agent vẫn do hệ thống hiện hành quản lý.

## Tích hợp API

[Hợp đồng OpenAPI](docs/api-contract.yaml) dùng cùng nguồn với giao diện, dưới `/api/v1`. Bản dựng mặc định dùng form tài khoản và phiên cookie do backend cấp. Backend cần thực thi hợp đồng, phân quyền theo phạm vi tài khoản và quyết định chính sách tại nơi thao tác. MSW mô phỏng xếp hàng và kiểm tra quyền. Bản demo không tạo lượt gửi thực tế.

Giao diện hiển thị consent theo mục đích và kết quả phân loại opt-out. Duyệt nháp cần đối chiếu nội dung và người nhận. Phản hồi `queued` chỉ xác nhận đã vào hàng đợi. Worker phải kiểm tra lại Guard ngay trước khi gửi và giữ `ADS_ENABLED=false`. Giao diện hiển thị `unknown_delivery` để đối chiếu thủ công và gửi yêu cầu xóa để backend kiểm tra nghĩa vụ lưu giữ.

## Kiểm thử

```sh
npm run build
npm run contract
npm test
npx playwright install --with-deps --only-shell chromium
npm run smoke
```

Có thể đặt `PLAYWRIGHT_CHROMIUM_EXECUTABLE` trỏ tới Chromium đã cài sẵn. Smoke chạy cả desktop và viewport điện thoại.
