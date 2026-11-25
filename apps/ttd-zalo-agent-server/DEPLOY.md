---
id: ttd-zalo-v2-runtime-deploy
type: runbook
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# TTD Zalo Runtime trên VPS Linux

## Chạy bản mô phỏng

Cần Docker Engine và Compose v2. Checkout commit đã nghiệm thu, vào `apps/ttd-zalo-agent-server` và tạo cấu hình riêng.

```sh
umask 077
cp .env.example .env
chmod 600 .env
docker compose config --quiet
docker compose up --build -d
docker compose ps
curl --fail --silent http://127.0.0.1:8080/health
```

Trước lần khởi động đầu tiên, đặt `IDENTITY_KEY` bằng khóa ngẫu nhiên riêng có ít nhất 32 byte và sao lưu khóa trong kho bí mật của chủ dự án. DB đã tạo gắn với khóa này. Giữ `CHANNEL_MODE=mock` và `CLAUDE_ENABLED=0` khi diễn tập. Hệ thống khởi tạo ở trạng thái DỪNG. Hai volume `database` và `backups` dùng riêng cho dịch vụ này. Compose bind cổng 8080 vào loopback của VPS.

## DỪNG và khôi phục

Đặt `OPERATOR_PASSWORD` bằng mật khẩu ngẫu nhiên dài ít nhất 24 ký tự. Dùng SSH port forwarding đến cổng 8080 trên VPS. Mở `http://127.0.0.1:8080/operator` qua đường hầm, đăng nhập `owner` và dùng nút DỪNG toàn hệ thống hoặc từng agent. Báo cáo hằng ngày và cảnh báo ngân sách nằm trên trang này và qua lệnh `notices`.

```sh
docker compose exec runtime node dist/ttd-zalo-agent-server/src/main.js stop global
docker compose exec runtime node dist/ttd-zalo-agent-server/src/main.js stop sales
docker compose exec runtime node dist/ttd-zalo-agent-server/src/main.js notices
docker compose exec runtime node dist/ttd-zalo-agent-server/src/main.js resume global
```

Chỉ `resume` sau khi người vận hành kiểm tra lý do dừng. STOP ngăn khởi tạo lượt gửi tiếp theo. Đối soát trạng thái `reserved`, `started` hoặc `unknown` trước khi can thiệp. Adapter live phải bắt đầu gửi đồng bộ tại điểm gọi và cung cấp hợp đồng xác thực sự kiện, định danh, tính bạn bè, idempotency và thứ tự opt-out. Khung Subiz hiện trả `not_supported` ở mọi thao tác, kể cả khi điền `SUBIZ_API_TOKEN` sau khi duyệt V2-01.

## Claude và ngân sách

Bảng giá có nguồn và ngày xem trong [config.ts](src/config.ts). Sau khi A0 cho phép kiểm thử Claude trên MockChannel, xác nhận credit Ultra đúng tổ chức Console, đúng số dư và chu kỳ, khóa riêng cho runtime, không có auto-reload, credit trả phí hoặc invoicing, và để các ứng dụng khác ngoài tổ chức dùng chung credit. Sau đó điền `ANTHROPIC_API_KEY`, đặt `CLAUDE_CREDIT_CONFIRMED=1`, cấu hình `CREDIT_CYCLE_START_DAY` theo ngày reset đã đối chiếu và đặt `CLAUDE_ENABLED=1`. Chỉ số ngày hiện hỗ trợ 1–28 theo ngày Việt Nam. Nếu mốc cấp credit thực tế khác, giữ chế độ mô phỏng đến khi lịch ngân sách khớp. Tài liệu chính thức nêu số dư dùng chung tổ chức và có thể trừ credit mua thêm hoặc lập hóa đơn sau khi credit tặng đã hết. Sổ runtime kiểm soát các lần gọi của chính dịch vụ. [Credit Claude](https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-ultra-and-team-plans).

Dùng biến `MODEL_ROUTER`, `MODEL_SUPPORT`, `MODEL_CRM`, `MODEL_CAMPAIGN`, `MODEL_COMMUNITY`, `MODEL_LISTEN`, `MODEL_SALES` và `MODEL_REPORT` để chọn một trong các model có giá đã xác minh. Prompt gửi `cache_control` cho phần hướng dẫn cố định. Cache hit phụ thuộc độ dài prefix và quy tắc Anthropic. Batch được dùng cho lắng nghe và báo cáo. Mọi lần gọi giữ chỗ theo giá tối đa trước khi gửi, rồi quyết toán theo usage. Lần gọi chưa rõ billing giữ dự phòng qua chu kỳ tiếp theo.

## Dữ liệu và sao lưu

Lệnh `consent`, `catalogue`, `export` và `delete` đọc JSON từ stdin. Ví dụ với tệp riêng được bảo vệ quyền truy cập:

```sh
docker compose exec -T runtime node dist/ttd-zalo-agent-server/src/main.js consent < /path/private/consent.json
docker compose exec -T runtime node dist/ttd-zalo-agent-server/src/main.js catalogue < /path/private/catalogue.json
docker compose exec -T runtime node dist/ttd-zalo-agent-server/src/main.js export < /path/private/customer.json
docker compose exec -T runtime node dist/ttd-zalo-agent-server/src/main.js delete < /path/private/customer.json
```

`consent` nhận `target`, `expires` (epoch ms) và các cờ boolean `retain`, `respond`, `send`, `ads`. Chỉ đặt `ads=true` với bằng chứng đồng ý trước. Kết bạn độc lập với consent quảng cáo. `catalogue` nhận đối tượng Source của app desktop. `export` và `delete` nhận `{ "target": "synthetic-id" }`. Hàng chờ SQLite lưu trạng thái, không lưu nội dung tin. Sau restart, adapter cần phát lại sự kiện để dựng lại hàng chờ còn hiệu lực. Xóa hồ sơ loại bỏ trường CRM và hàng chờ, giữ dấu HMAC tối thiểu để từ chối quảng cáo và phát lại. Phạm vi xóa dữ liệu vận hành bao gồm cả lịch riêng và bản sao lưu theo chính sách của chủ dự án.

Lịch chiến dịch và cộng đồng đọc từ `SCHEDULE_PATH` nếu mount tệp JSON riêng chỉ đọc vào container. Mỗi đề mục có `key` duy nhất, `agent`, `kind`, `at` (epoch ms), `target`, `text` hoặc `message` cho kiểm duyệt. Agent chiến dịch nhận `advertising`, cộng đồng nhận `group_post`, `group_create`, `group_moderate`. Dùng nội dung nhóm phi quảng cáo do chủ dự án duyệt.

SQLite backup trực tuyến tạo bản sao mỗi ngày UTC trong volume `backups`. Sao chép sang kho backup riêng, áp dụng chính sách lưu giữ và bảo vệ ổ đĩa backup. Khi phục hồi, dừng container, giữ bản hiện tại và khôi phục cùng khóa định danh. Dừng hệ thống trước khi xử lý tiếp và đối soát mọi lượt gửi/chi phí sau thời điểm snapshot để tránh replay. Chạy kiểm tra phục hồi định kỳ bằng dữ liệu mô phỏng.
