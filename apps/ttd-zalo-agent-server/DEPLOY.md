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

Chỉ `resume` sau khi người vận hành kiểm tra lý do dừng. STOP ngăn khởi tạo lượt gửi tiếp theo. Đối soát trạng thái `reserved`, `started` hoặc `unknown` trước khi can thiệp. Adapter live phải bắt đầu gửi đồng bộ tại điểm gọi và cung cấp hợp đồng xác thực sự kiện, định danh, tính bạn bè, idempotency và thứ tự opt-out. Cấu hình các năng lực đã xác minh theo phần kết nối adapter bên dưới.

## Claude và ngân sách

Bảng giá có nguồn và ngày xem trong [config.ts](src/config.ts). Sau khi A0 cho phép kiểm thử Claude trên MockChannel, xác nhận credit Ultra đúng tổ chức Console, đúng số dư và chu kỳ, khóa riêng cho runtime, không có auto-reload, credit trả phí hoặc invoicing, và để các ứng dụng khác ngoài tổ chức dùng chung credit. Sau đó điền `ANTHROPIC_API_KEY`, đặt `CLAUDE_CREDIT_CONFIRMED=1`, cấu hình `CREDIT_CYCLE_START_DAY` theo ngày reset đã đối chiếu và đặt `CLAUDE_ENABLED=1`. Chỉ số ngày hiện hỗ trợ 1–28 theo ngày Việt Nam. Nếu mốc cấp credit thực tế khác, giữ chế độ mô phỏng đến khi lịch ngân sách khớp. Tài liệu chính thức nêu số dư dùng chung tổ chức và có thể trừ credit mua thêm hoặc lập hóa đơn sau khi credit tặng đã hết. Sổ runtime kiểm soát các lần gọi của chính dịch vụ. [Credit Claude](https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-ultra-and-team-plans).

Dùng biến `MODEL_ROUTER`, `MODEL_SUPPORT`, `MODEL_CRM`, `MODEL_CAMPAIGN`, `MODEL_COMMUNITY`, `MODEL_LISTEN`, `MODEL_SALES` và `MODEL_REPORT` để chọn một trong các model có giá đã xác minh. Prompt gửi `cache_control` cho phần hướng dẫn cố định. Cache hit phụ thuộc độ dài prefix và quy tắc Anthropic. Batch được dùng cho lắng nghe và báo cáo. Runtime giữ chỗ theo ước tính token của toàn bộ request văn bản, gồm prompt, tool schema và phần dự phòng giao thức, cộng max_tokens đầu ra. Sau đó runtime quyết toán theo usage. Nếu usage vượt dự phòng hoặc model trả về không khớp, runtime bật budget STOP. Lần gọi chưa rõ billing giữ dự phòng qua chu kỳ tiếp theo.

`AI_PROVIDER=anthropic` là mặc định. Với endpoint tương thích Anthropic, chọn `AI_PROVIDER=anthropic-compatible`, cấp `AI_ROUTER_BASE_URL` (HTTPS prefix đứng trước `/messages`), `AI_ROUTER_API_KEY`, `AI_ROUTER_DAILY_USD` theo ngày Việt Nam và `AI_ROUTER_RATE_MULTIPLIER` theo trần biểu phí đã xác minh. Chỉ đặt `AI_ROUTER_CREDIT_CONFIRMED=1` sau khi A0 xác minh router dùng đúng hạn mức credit đã phê duyệt, không phát sinh thanh toán, và hệ số bao hết mọi thành phần giá của route. Vẫn cần `CLAUDE_CREDIT_CONFIRMED=1` và `CLAUDE_ENABLED=1`. Chế độ tương thích dùng Messages cho cả tác vụ nền, với giá dự phòng riêng và tổng trần tháng vẫn áp dụng. Yêu cầu gửi ID model từ allowlist và chỉ sử dụng phản hồi có trường `model` khớp chính xác. URL, biểu phí thật, định tuyến và nguồn credit Hostinger cần xác minh trong pilot trước khi bật.


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

## Kết nối adapter trên VPS

Nguồn giao thức xem [Subiz webhook](https://subiz.com.vn/developers/webhooks/receiving), [Subiz conversation](https://subiz.com.vn/developers/api-reference/conversations/retrieve), [Subiz gửi 4.1](https://subiz.com.vn/developers/api-reference/messages/send), [Zalo Bot webhook](https://bot.zaloplatforms.com/docs/webhook/) và [Zalo Bot gửi](https://bot.zaloplatforms.com/docs/apis/sendMessage/). Đối chiếu ngày 26/11/2026 ICT.

1. Tạo workspace và PAT thử riêng. Chủ dự án tự liên kết Zalo Personal và đối chiếu đúng ID workspace, agent, channel và source Personal từ Subiz. GH không lưu PAT, webhook secret, hồ sơ trình duyệt hay tệp định tuyến của VPS. Nạp `SUBIZ_API_TOKEN`, `SUBIZ_WEBHOOK_SECRET` và `IDENTITY_KEY` vào môi trường dịch vụ. Đặt `CHANNEL_MODE=subiz`. Gắn tệp route chỉ đọc bằng Compose override riêng trên VPS, đặt `CHANNEL_ROUTES_PATH` trỏ đến đường dẫn trong container. Ví dụ cấu trúc với dữ liệu tổng hợp:

   ```json
   {
     "subiz": {
       "accountId": "fixture-account", "agentId": "fixture-agent",
       "channel": "zalo", "source": "fixture-personal-source",
       "direct": [{
         "contactId": "fixture-contact", "conversationId": "fixture-cid",
         "userId": "fixture-user", "profileId": "fixture-profile"
       }]
     },
     "capabilities": {
       "receiveMessage": "api", "sendMessage": "api", "getContact": "api"
     }
   }
   ```

   Mỗi route phải là một cuộc hội thoại 1:1 đã đối chiếu thủ công trong inbox. Dùng `friendUntil` theo Unix ms chỉ khi đã xác minh đúng trạng thái bạn bè và đặt ngày hết hạn kiểm chứng. Thiếu bằng chứng thì runtime không gửi. Gửi cần thêm consent của Policy Core. Bản nhận webhook chỉ nhận văn bản từ actor khách đúng cặp user/CID đã duyệt.

2. Đặt reverse proxy TLS trước loopback 8080. Chỉ public `POST /webhooks/subiz`, và `POST /webhooks/zalo-bot` khi bật bot. Giới hạn request 256 KiB, giữ nguyên raw body và các header xác thực, tắt log body và header bí mật. Giữ `/operator` và các đường quản trị trong mạng riêng. Đăng ký URL HTTPS `/webhooks/subiz` trong Subiz và chỉ chọn `message_sent`. Sau khi lưu webhook, nạp shared secret thật vào môi trường dịch vụ. Hai digest trong giai đoạn đổi secret được hỗ trợ. Inbound được mã hóa, ghi bền vững trước ACK và tự dọn sau 24 giờ.

3. **Smoke 1:1.** Đặt `CHANNEL_SMOKE_ONLY=1`, `CLAUDE_ENABLED=0` và khởi động dịch vụ trên DB pilot. Chế độ này nhận webhook nhưng không chạy worker tự động. Cấp consent phản hồi cho đúng liên hệ pilot, xác minh `friendUntil` còn hiệu lực và mở STOP trong phạm vi thử. Đặt `SUBIZ_SMOKE_CONTACT` bằng contact ID pilot và `SUBIZ_SMOKE_NONCE` là chuỗi ngẫu nhiên dạng `TTD-SMOKE-<12-ký-tự-trở-lên>`. Yêu cầu người thử gửi đúng chuỗi từ Zalo; chạy:

   ```sh
   docker compose exec runtime node dist/ttd-zalo-agent-server/src/main.js smoke
   ```

   Lệnh đợi webhook tối đa khoảng 90 giây, xác thực PAT, kiểm CID và history, rồi gửi tối đa một phản hồi cho nonce và liên hệ đó qua Guard. Chạy lại cùng nonce đối soát history. `accepted_in_history` là Subiz đã ghi nhận. Người thử kiểm màn hình nhận và xác nhận đúng một tin để nghiệm thu delivery. Dừng pilot nếu lệch ID, trùng, hết quyền hoặc trạng thái giao chưa rõ. Bật STOP, thu hồi PAT thử và tháo webhook thử sau nghiệm thu theo [SMOKE_TEST.md đã pin](https://github.com/DuyKienTTD/Hosting/blob/367c36454e021dbf11ea30afb72ebff0f1131afc/program/zalo-mvp01/v2-01-channel/SMOKE_TEST.md).

4. **Zalo Bot.** Nếu nhóm thử hỗ trợ Bot Beta và A0 xác nhận Bot đã tham gia, cấu hình `bot: {accountId, botId, groups}` bằng các ID đã đối chiếu, nạp `ZALO_BOT_TOKEN` và `ZALO_BOT_WEBHOOK_SECRET`, đăng ký URL `/webhooks/zalo-bot`. Chọn `readGroupMessages: "bot"` và/hoặc `postToGroup: "bot"`. Startup kiểm đúng bot và `can_join_groups`. Đọc tin văn bản mới từ webhook, với nhóm được phép. Danh mục Bot chưa công bố thao tác kiểm duyệt ở thời điểm đối chiếu nên trả `not_supported`.

5. **Subiz UI.** Chỉ bật sau khi A0 xác minh selector trên phiên thử, có quyền đúng workspace, và kiểm các thao tác với người/nhóm đã đồng ý. Cài Chromium trên VPS bằng `npx playwright install --with-deps chromium` trong thư mục runtime hoặc build image với `INSTALL_UI_BROWSER=1 docker compose build runtime`. Chạy Chromium dưới người dùng riêng với sandbox và profile seccomp cho user namespaces theo [Playwright Docker](https://playwright.dev/docs/docker). Chuẩn bị storage state qua phiên đăng nhập của chủ dự án, gắn chỉ đọc, quyền 0600. Đặt `SUBIZ_UI_URL` là URL đã xác minh trên `https://app.subiz.com.vn`, `SUBIZ_UI_STATE_PATH`, và tùy chọn `SUBIZ_UI_DIAGNOSTIC_PATH` ở volume ghi được. Khai báo `ui: {accountId, workspaceId, origin, selectors, groups, contacts, groupNames}` theo [UiConfig](src/adapters/ui.ts). Selector phải xác định duy nhất workspace, panel thao tác, đích, nút và receipt có ID ổn định. Điều kiện này phải được chứng minh trên chính giao diện đang sử dụng. Chọn năng lực UI cần thiết trong route. `createGroup` cần `memberIds` trong lịch, tất cả trong allowlist đã đồng ý. Nhánh đọc danh sách thành viên là chẩn đoán qua adapter, vì hợp đồng V2-01 chưa có lệnh này. Khi đổi selector, CAPTCHA, mất phiên hoặc receipt không chắc chắn, adapter khóa cấu hình selector đó trong SQLite. Ảnh chẩn đoán dựng từ trang sạch, không chụp inbox. Phục hồi chỉ sau khi quản trị viên kiểm phiên, đích, receipt và selector mới.

6. Trước mở tự động, xác nhận consent quảng cáo riêng, danh tính bạn bè, kỳ hạn bằng chứng, scope của từng nhóm, STOP, opt-out, quota và budget hold. Kiểm mỗi thao tác đã cấu hình trên pilot, đối soát đúng một lượt với đích, và giữ capability không kiểm chứng ngoài cấu hình. Không thiết lập fallback giữa API, Bot và UI. Chuẩn bị kế hoạch xóa dữ liệu theo yêu cầu và bảo vệ backup cùng secret key.

### Xử lý yêu cầu ngừng quảng cáo

- `active` vẫn yêu cầu consent quảng cáo hợp lệ. `ads_paused_review` giữ consent hiện có và tạm chặn quảng cáo riêng cho khách. `opted_out` thu hồi quảng cáo. Guard kiểm tra cả hai trạng thái chặn trước khi gửi. Luồng trả lời CSKH 1:1 vẫn áp dụng policy riêng.
- Trong `/operator`, mục **Quảng cáo tạm dừng chờ xem** có nút xác nhận bỏ tạm dừng hoặc xác nhận ngừng quảng cáo. Đối chiếu tin trong kênh vận hành trước khi xác nhận. Phiếu cũ hết hiệu lực nếu tin mới thay thế phiếu. AI có thể chuyển sang `opted_out` hoặc giữ tạm dừng và gắn cờ. Quyền bỏ tạm dừng thuộc người vận hành.
- Tiêu chí kiểm định gồm không gửi quảng cáo cho bất kỳ yêu cầu xin ngừng nào, không chuyển ca âm sang `opted_out`, và báo riêng tỷ lệ ca âm bị tạm dừng.
