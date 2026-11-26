# Z4-S2-OA delivery log

Nền triển khai: PR #75 tại `a56ec820148ab0bdc4a3577808f25a4a9d3077b6`. Phạm vi gồm module OA này và `test/oa.test.mjs`. CI Postgres hiện có chạy ca OA qua `RUN_POSTGRES_TESTS=1`.

- OAuth v4 lưu cặp token AES-256-GCM trong Postgres. Khóa advisory theo app/OA điều phối nhiều process. Tiêu thụ refresh token trước khi gọi Zalo. Nếu mất phản hồi sau khi đã gọi, worker yêu cầu cấp quyền lại. Lỗi access token vô hiệu áp dụng đúng thế hệ token và lượt gửi kế tiếp mới dùng token đã làm mới.
- Webhook xác thực chữ ký trên byte gốc, ghi bền receipt theo event ID hoặc khóa ổn định cho sự kiện thiếu ID. Tin văn bản đã mã hóa được Runtime lấy qua hàng đợi sau ACK. Cursor xử lý nằm trong tiến trình. Khi khởi động lại, Runtime đọc lại hàng đợi còn hạn và dùng khóa inbound/job hiện có để loại lặp. Nội dung hàng đợi hết hạn sau 24 giờ, giữ khóa khử lặp.
- Follow ghi nhận quan tâm OA riêng với sự đồng ý theo mục đích. Unfollow thu hồi quảng cáo. `user_withdraw` thu hồi các mục đích đang có, khóa OA cho UID và xóa nội dung còn chờ trong hàng đợi. Bằng chứng consent được ghi nối tiếp. Khác biệt thứ tự hoặc follow trở lại không tự mở opt-out.
- Tin Tư vấn văn bản bắt đầu từ Guard, sau khi đọc lại consent/STOP và commit giữ chỗ vào `send_log`. Cờ `allowAfter48h` mặc định tắt để tránh phát sinh chi phí. Chỉ định bật cờ khi hạn mức 48 giờ–7 ngày đã được A0 duyệt. Ngoài 7 ngày kênh luôn từ chối. Cấu hình tuổi tin đầu vào của Guard có thể đặt giới hạn chặt hơn. API dùng header `appsecret_proof` theo SDK Zalo. Khi giao không rõ, giữ trạng thái `unknown_delivery` và khóa gửi lại.

## Điểm nối bàn giao

Áp dụng [schema.sql](schema.sql) sau hai migration của PR #75. Schema bổ sung quyền truy cập các đối tượng OA mới cho `data_runtime` đã có. Dùng chung khóa định danh với Store và cấp khóa mã hóa OA 32 byte từ môi trường triển khai. Bootstrap ủy quyền OAuth của quản trị viên gọi `OaTokens.install` với cặp token và thời điểm được cấp.

Nối `OaRuntimeChannel` vào Runtime và đăng ký `oaWebhook` sau reverse proxy HTTPS, hoặc dùng `createOaWebhookServer` khi lớp tiếp nhận kết thúc TLS trực tiếp. Dành tiến trình riêng cho ingress để việc chờ Postgres đồng bộ ở Runtime không chặn đồng hồ phản hồi webhook. Dùng pool ingress có deadline kết nối/truy vấn trong ngân sách 2 giây. Chạy worker định kỳ để xử lý nội dung còn hạn và dọn ciphertext hết hạn.

Wiring cho `src/main.ts`, migration tự động khi Compose khởi động, lịch dọn khi worker dừng, và đối soát hàng đợi OA trong luồng restore thuộc phạm vi tích hợp tiếp theo. Cấu hình đa kênh và liên kết UID với hồ sơ CRM hiện có cũng cần xử lý ở lớp tích hợp. Kiểm thử giao thức dùng Postgres thật và Zalo mock.

Nguồn Zalo truy cập ngày 26/11/2026

- [OAuth v4](https://docs.zaloplatforms.com/docs/OA/bat-dau/xac-thuc-va-uy-quyen-cho-ung-dung-new)
- [Webhook HTTPS và thời hạn ACK](https://docs.zaloplatforms.com/docs/OA/webhook/tong-quan)
- [Điều kiện gửi Tin Tư vấn](https://docs.zaloplatforms.com/docs/OA/tin-nhan/tin-tu-van/dieu-kien-gui-tin-tu-van) · [API gửi văn bản](https://docs.zaloplatforms.com/docs/OA/tin-nhan/tin-tu-van/gui-tin-tu-van-dang-van-ban)
- [App Secret Proof trong SDK Zalo](https://github.com/zaloplatform/zalo-php-sdk/blob/6bacb1bea670ce1fa9f1ae616bbbfd92742e20aa/src/Zalo.php#L229-L234)
