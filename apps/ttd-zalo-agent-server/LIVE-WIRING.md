# Z4-LIVE-WIRING

Runtime khởi động ở `OA_MODE=mock` và `AI_MODE=mock` nếu bỏ trống cấu hình bằng cách không khai báo hai biến này. Chỉ nhận giá trị `mock` hoặc `live`. `CLAUDE_ENABLED` và `AI_PROVIDER` không còn chọn provider của runtime. Giữ bí mật trong môi trường được cấp quyền và nạp token OA riêng qua stdin.

## Zalo OA

`OA_MODE=live` cần `ZALO_APP_ID`, `ZALO_OA_ID`, `ZALO_APP_SECRET`, `ZALO_WEBHOOK_SECRET` và `ZALO_OA_ENCRYPTION_KEY` (32 byte dạng hex). Postgres cần migration 006 và 007. Sau bước ủy quyền OA, chạy entrypoint với lệnh `oa-install` và nạp JSON qua stdin gồm `access_token`, `refresh_token`, `expires_in` theo giây và `issued_at` theo Unix milliseconds. Runtime xoay cặp token trong Postgres. Access token có hạn tối đa 25 giờ, refresh token được tiêu thụ một lần. Gọi gửi tin và refresh có timeout 5 giây và mỗi lượt chỉ thực hiện một POST. Kết quả gửi không xác định giữ `unknown_delivery`. Nếu kết quả refresh không xác định, cấp quyền lại thay vì dùng lại refresh token.

`OA_WEBHOOK_INGRESS=embedded` mặc định đăng ký `POST /webhooks/zalo-oa`. Production dùng `external` khi tiến trình ingress riêng đã xử lý HTTPS và ghi vào cùng Postgres. Webhook có ngân sách phản hồi 1.75 giây và chỉ thử lại một lần khi Postgres xác nhận transaction đã rollback do serialization hoặc deadlock. Guard tiếp tục kiểm tra STOP, consent, cửa sổ tương tác và quota. `OA_ALLOW_AFTER_48H` và `OA_ALLOW_PAID_OVERFLOW` bật bằng `1`, mặc định tắt. `OA_MONTHLY_QUOTA` mặc định 500.

Smoke OA dùng `CHANNEL_SMOKE_ONLY=1`, `OA_MODE=live`, `AI_MODE=mock` và `SMOKE_ALLOWLIST` là UID OA phân cách bằng dấu phẩy. Adapter kiểm danh sách trước khi chuẩn bị token và trước transport. Các cuộc hội thoại ngoài danh sách cũng không được đưa vào runtime từ inbox. Khi chạy live OA ngoài smoke với AI mock, provider chỉ chọn `none` để dữ liệu mô phỏng không tự tạo phản hồi thật.

- [Zalo OAuth v4](https://docs.zaloplatforms.com/docs/OA/bat-dau/xac-thuc-va-uy-quyen-cho-ung-dung-new)
- [Zalo Webhook](https://docs.zaloplatforms.com/docs/OA/webhook/tong-quan)
- [API gửi Tin Tư vấn](https://docs.zaloplatforms.com/docs/OA/tin-nhan/tin-tu-van/gui-tin-tu-van-dang-van-ban)
- [App Secret Proof trong SDK Zalo](https://github.com/zaloplatform/zalo-php-sdk/blob/6bacb1bea670ce1fa9f1ae616bbbfd92742e20aa/src/Zalo.php#L229-L234)

## Hostinger AI Router

`AI_MODE=live` dùng Anthropic Messages tại `https://router.hostinger.com/v1` với `AI_ROUTER_API_KEY`. `AI_MODEL_ALLOWLIST` nhận danh sách ID model đã có đơn giá trong runtime. Các biến `MODEL_<AGENT>` tùy chọn phải thuộc danh sách đó, kể cả khi tự hạ model để tiết kiệm.

Khai báo `AI_ROUTER_DAILY_USD`, `AI_ROUTER_MONTHLY_USD`, `AI_ROUTER_RATE_MULTIPLIER`, `AI_DAILY_TOKENS` và `AI_MONTHLY_TOKENS`. Hệ số phải bao phủ chi phí trên Hostinger theo đơn giá đã xác minh trước khi bật live. Có thể hạ `AI_MAX_INPUT_TOKENS` (mặc định 18.000 token ước tính) và `AI_MAX_OUTPUT_TOKENS` (mặc định tối đa 256). Ledger Postgres giữ trước ngân sách, bảo lưu ước tính cho lượt chưa đối soát và quyết toán theo usage. Lượt inbound bị giữ do giới hạn hoặc lỗi AI trở thành job `review`, lý do `ai_admission_hold`, với cảnh báo trong operator. Nội dung khách gửi đi dưới dạng JSON trong trường user sau bước lọc của runtime. Lựa chọn model và hành động do code kiểm tra.

- [Hostinger AI Router và Anthropic API](https://www.hostinger.com/support/what-is-hostinger-ai-router-and-how-to-get-started/)

Fixture UI của #79 vẫn chạy chế độ OA mô phỏng qua `CHANNEL_MODE=oa` và endpoint loopback cùng `CHANNEL_SMOKE_ONLY=1`. Tích hợp giữ nguyên route và hợp đồng UI. Cấu hình triển khai ở #80 nằm ngoài phạm vi chỉnh sửa. Bộ test dùng HTTP fixture, không cần tài khoản hoặc token nhà cung cấp.
