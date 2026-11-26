---
id: ttd-zalo-v2-runtime-deploy
type: runbook
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# TTD Zalo Runtime trên VPS Linux

## Chạy bản mô phỏng

Thực hiện các bước [Z4-S1-DATA và Postgres](#z4-s1-data-và-postgres). Dịch vụ `runtime` dùng `MockChannel` và FakeProvider với cấu hình pilot mặc định. Xác minh health qua mạng riêng hoặc proxy quản trị. Postgres khởi tạo với STOP toàn hệ thống và quảng cáo tắt.

## DỪNG và khôi phục

Đặt `OPERATOR_PASSWORD` bằng mật khẩu ngẫu nhiên dài ít nhất 24 ký tự. Dùng reverse proxy quản trị riêng đến `ttd-zalo-runtime:8080`. Mở `/operator` qua mạng quản trị, đăng nhập `owner` và dùng nút DỪNG toàn hệ thống hoặc từng agent. Báo cáo hằng ngày và cảnh báo ngân sách nằm trên trang này và qua lệnh `notices`.

```sh
docker compose exec runtime node dist/ttd-zalo-agent-server/src/main.js stop global
docker compose exec runtime node dist/ttd-zalo-agent-server/src/main.js stop sales
docker compose exec runtime node dist/ttd-zalo-agent-server/src/main.js notices
docker compose exec runtime node dist/ttd-zalo-agent-server/src/main.js resume global
```

Chỉ `resume` sau khi người vận hành kiểm tra lý do dừng. STOP ngăn khởi tạo lượt gửi tiếp theo. Đối soát trạng thái `reserved` hoặc `unknown_delivery` trước khi can thiệp. Adapter live phải bắt đầu gửi đồng bộ tại điểm gọi và cung cấp hợp đồng xác thực sự kiện, định danh, tính bạn bè, idempotency và thứ tự opt-out. Cấu hình các năng lực đã xác minh theo phần kết nối adapter bên dưới.

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

`consent` nhận `target`, `expires` (epoch ms), các cờ boolean `retain`, `respond`, `send`, `ads` và bằng chứng gồm `displayedText`, `policyVersion`, `evidence`. Chỉ đặt `ads=true` với bằng chứng đồng ý trước. Kết bạn độc lập với consent quảng cáo. `catalogue` nhận đối tượng Source của app desktop. `export` và `delete` nhận `{ "target": "synthetic-id" }`. Postgres lưu trạng thái hàng chờ. Nội dung tin 1-1 chỉ được ghi vào `messages` khi còn consent lưu giữ. Sau restart, adapter cần phát lại sự kiện để dựng lại hàng chờ còn hiệu lực. Xóa hồ sơ loại bỏ trường CRM và hàng chờ, giữ dấu HMAC tối thiểu để từ chối quảng cáo và phát lại. Phạm vi xóa dữ liệu vận hành bao gồm cả lịch riêng và bản sao lưu theo chính sách của chủ dự án.

Lịch chiến dịch và cộng đồng đọc từ `SCHEDULE_PATH` nếu mount tệp JSON riêng chỉ đọc vào container. Mỗi đề mục có `key` duy nhất, `agent`, `kind`, `at` (epoch ms), `target`, `text` hoặc `message` cho kiểm duyệt. Agent chiến dịch nhận `advertising`, cộng đồng nhận `group_post`, `group_create`, `group_moderate`. Dùng nội dung nhóm phi quảng cáo do chủ dự án duyệt.

Dùng [backup và restore Postgres](#z4-s1-data-và-postgres). Khi khôi phục snapshot cũ, giữ STOP và đối soát lượt gửi, consent và chi phí phát sinh sau snapshot. Khôi phục đầy đủ các khóa lượt gửi đang `reserved` hoặc `unknown_delivery` trước khi mở STOP. Không phát lại lượt chưa rõ kết quả.

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

2. Đặt reverse proxy TLS trước service runtime. Chỉ public `POST /webhooks/subiz`, và `POST /webhooks/zalo-bot` khi bật bot. Giới hạn request 256 KiB, giữ nguyên raw body và các header xác thực, tắt log body và header bí mật. Giữ `/operator` và các đường quản trị trong mạng riêng. Đăng ký URL HTTPS `/webhooks/subiz` trong Subiz và chỉ chọn `message_sent`. Sau khi lưu webhook, nạp shared secret thật vào môi trường dịch vụ. Hai digest trong giai đoạn đổi secret được hỗ trợ. Inbound được mã hóa, ghi bền vững trước ACK và tự dọn sau 24 giờ.

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

`ADS_ENABLED` mặc định là `false`. Guard trả `ads_disabled` trước kiểm consent, ngân sách hoặc liên hệ đối với mọi đề xuất quảng cáo. Luồng CSKH 1:1 tiếp tục áp dụng các điều kiện riêng. Chỉ đặt `ADS_ENABLED=true` khi lớp AI một chiều đã được đo trên tin nhắn thật và chủ dự án duyệt bật quảng cáo.

## Z4-S1-DATA và Postgres

Dùng Compose riêng `compose.data.yaml`. `runtime` chạy AI, Guard, journal kênh và gửi, với Postgres là backend bắt buộc. `app` nhận tin và phiếu việc đã xác thực ở API dữ liệu, `worker` xử lý hàng đợi tiếp nhận và retention. API dữ liệu `/messages` lưu tin cho lớp tích hợp OA sau này. Các adapter runtime hiện có đưa sự kiện trực tiếp vào runtime. SQLite dùng cho fixture cục bộ.

Guard đọc `settings.ADS_ENABLED`, consent theo mục đích và `ad_status` trong transaction giữ chỗ ngay sau khi xác minh đích. Transaction commit giữ chỗ trước khi gọi kênh. Kết quả cập nhật trong transaction riêng, với `unknown_delivery` và giữ chỗ chưa quyết toán đều chặn phát lại. Bật quảng cáo cần phê duyệt trước và thay đổi cờ trong Postgres bằng đường bảo trì. Cấu hình pilot đặt lại cờ về tắt mỗi khi service runtime khởi động.

1. SSH vào VPS và tạo thư mục triển khai riêng. Checkout đúng hai thành phần của cùng một commit đã nghiệm thu. Từ gốc repository, build bằng `docker build -f apps/ttd-zalo-agent-server/Dockerfile.data .` và `docker build apps/ttd-zalo-agent-server/postgres`. Lưu hai image theo commit và đặt `DATA_APP_IMAGE`, `DATA_POSTGRES_IMAGE` theo digest đã kiểm tra trong registry.
2. Từ thư mục app, sao chép `.env.example` thành `.env.data` ngoài Git, đặt quyền đọc chỉ cho người vận hành. Cấp riêng mật khẩu quản trị, app, runtime, worker và token từng vai trò dùng thử. Tất cả token tối thiểu 32 ký tự, không dùng chung. Migration khởi tạo 001–005 chạy trên volume Postgres mới. Không trỏ runtime vào DB SQLite cũ. Giữ STOP trong suốt chuyển đổi dữ liệu. Với volume Postgres đã chạy schema 001, sao lưu rồi dùng tài khoản bảo trì chạy `psql -v ON_ERROR_STOP=1 -f postgres/002-runtime.sql -f postgres/runtime-grants.sql` trên DB đích. Nạp `DATA_RUNTIME_PASSWORD` từ kho bí mật trước khi chạy. Thay đổi schema tiếp theo phải chạy migration đã duyệt bằng tài khoản bảo trì trước khi đổi image. Migration 003 xóa hàm purge cũ và 004 bổ sung xác nhận sau commit. Với DB đã cài, giữ worker dừng, chạy `psql -v ON_ERROR_STOP=1 -f postgres/003-purge.sql -f postgres/004-purge-confirmation.sql -f postgres/purge-key.sql` khi nâng từ 002. Nếu đã ở 003, áp 004 rồi 005. Nếu đã ở 004, chỉ áp 005. Giữ khóa hiện có và chạy migration `postgres/005-purge-recovery.sql` trước khi khởi động worker mới. Cấp `DATA_TOMBSTONE_KEY` bằng 32 byte ngẫu nhiên ở dạng hex từ kho bí mật cho PostgreSQL, worker và tiến trình restore. Khóa này không đi vào dump. Để quảng cáo tắt và giữ cấu hình provider `anthropic-compatible`.
3. Chuẩn bị riêng network ingress mà reverse proxy HTTPS được phép tham gia. Điền tên miền và network trong môi trường triển khai. Dùng [mẫu route Caddy](ops/Caddyfile.data) trên reverse proxy đang phục vụ 443 với biến `DATA_DOMAIN`. Bật route chỉ sau khi kiểm tra TLS, health và quyền. Compose không mở cổng host cho Postgres, app hoặc worker. Webhook retention `POST /retention` chỉ có trong mạng riêng, dùng bearer retention và JSON gồm `record_id`, `expected_version`, `policy_version`, `reason_code`. Tin khách đi vào `POST /messages` bằng token kênh. Phiếu việc dùng riêng `POST /tasks` và token vai trò được cấp.
4. Dùng đích rclone ngoài VPS cho backup. Chuẩn bị hai cấu hình quyền hẹp. Worker được đọc và ghi `tombstones/pending/`, xóa pending quá hạn theo đối soát, và đọc/ghi bất biến tại `tombstones/confirmed/`. Backup được ghi và dọn theo tuổi trong `dumps/`, không được sửa/xóa tombstone. Worker ghi và đọc lại pending trước khi xóa. PostgreSQL ghi biên nhận commit cùng transaction xóa. Sau commit, worker lấy proof từ biên nhận, ghi sổ chỉ ghi thêm rồi mới xuất bản confirmed. Worker đối soát các commit chưa xuất bản khi chạy lại và dọn pending quá 24 giờ mỗi giờ. Giữ khóa xác minh cho toàn bộ thời hạn lưu bản sao. Gọi SQL trực tiếp thiếu biên nhận bị chặn. Quyền superuser và thay đổi DDL thuộc ranh giới quản trị tin cậy. Cấu hình object retention trên đích, giữ tombstone ít nhất lâu hơn mọi bản sao có thể restore. Tạo object `tombstones/_format` với đúng chuỗi `z4-tombstones-v1` tại prefix dành riêng cho cơ sở dữ liệu này. Khóa giải mã age giữ riêng với hệ thống chạy thường trực. Host chỉ cần public recipient khi backup.
5. Chạy `docker compose --env-file .env.data -f compose.data.yaml config --quiet`, sau đó `docker compose --env-file .env.data -f compose.data.yaml up -d --wait`. Xác minh health trong project và qua route HTTPS. Khởi tạo hội thoại fixture bằng đường bảo trì DB trước khi gửi tin fixture. Khi chưa có bản test restore thành công, giữ route tắt.
6. Lập lịch hằng ngày cho `docker compose --env-file .env.data -f compose.data.yaml --profile maintenance run --rm backup`. Worker thực thi retention mỗi 30 giây. Muốn gọi từ cron một lần, chạy `docker compose --env-file .env.data -f compose.data.yaml run --rm worker cron`. Skill đưa JSON vào stdin của `docker compose --env-file .env.data -f compose.data.yaml run --rm -T worker delete-eligible`. CLI chỉ cấp cho tiến trình có quyền dùng worker. Chỉ tin nhắn quá hạn và không bị giữ theo luật mới tự vào cách ly. Chỉnh thời gian cách ly bằng `deletion_policy.quarantine_seconds` từ vai trò bảo trì.
7. Thử khôi phục bằng `ops/restore.sh <tên.dump.age> <restore_tên_thử>` trong môi trường bảo trì có Postgres client cùng major version, age, rclone và Python. Cấp thông số kết nối quản trị, quyền đọc kho offsite và `AGE_IDENTITY_FILE` cùng `DATA_TOMBSTONE_KEY`. Dừng writer, worker và giữ nguyên trạng thái legal hold ở nguồn trong lúc đối soát đến khi đổi đích kết nối. Restore luôn vào DB staging khóa quyền CONNECT của các vai trò phục vụ. Đặt `RESTORE_SOURCE_DATABASE` tới DB nguồn có thẩm quyền. Có thể cấu hình `RESTORE_SOURCE_HOST`, `RESTORE_SOURCE_PORT`, `RESTORE_SOURCE_USER`, `RESTORE_SOURCE_PASSWORD` khi nguồn ở máy khác. Vai trò đọc nguồn cần quyền EXECUTE trên `purge_recovery_evidence` và `purge_restore_held`. Restore đối soát nguồn trước, rồi sổ biên nhận độc lập, rồi proof của confirmed trong kho. Legal hold ở nguồn truy cập được hoặc trong staging chặn replay và ghi cảnh báo. Hold đã xác minh ở nguồn được ghi lại trong staging để tiếp tục bảo vệ sau promote. Rollback có bằng chứng được bỏ khỏi replay. Pending chưa xác minh bị cách ly và chặn promote, kể cả tệp cũ thiếu proof. Dùng `ops/restore-control.sh <DB staging> list`, rồi owner chạy `resolve <purge_id> delete|restore` cho từng trường hợp đã đối soát. Quyết định ghi audit. Chạy `promote` cùng script sau khi hết pending chưa xử lý, kiểm tra STOP vẫn bật rồi mới đổi đích kết nối ứng dụng. Khi restore lỗi, bỏ DB thử lỗi và điều tra. Tên DB đích bắt đầu bằng `restore_`. Test CI tạo backup trước khi purge, restore sau khi purge và kiểm tra từ chối cả bản cũ lẫn sự kiện gửi lại.
8. Rollback bằng cách dừng intake, giữ volume và đổi về digest đã nghiệm thu nếu tương thích migration. Nếu cần rollback dữ liệu, khôi phục vào DB mới bằng bước 7 và xác minh tombstone trước khi trỏ app/worker sang DB đã nghiệm thu. Chỉ dùng lệnh với đúng file Compose của project này. Không dừng, thay cấu hình hay xóa volume của project khác.


### Sổ biên nhận purge độc lập

Đặt `PURGE_RECEIPT_REMOTE` vào bucket hoặc đích rclone riêng, ngoài VPS và ngoài prefix backup DB. Sổ có một object bất biến theo mỗi `purge_id`. Cấp worker quyền thêm và đọc object, khóa ghi đè/xóa bằng chính sách của backend. Worker ghi sổ sau khi biết kết quả commit, đối soát lại ở lần chạy kế tiếp khi lỗi mạng. Tuổi lưu của sổ phải ít nhất bằng thời hạn của backup lâu nhất còn được phép restore.

Chạy `ops/backup-purge-receipts.sh` riêng hằng ngày bằng credential chỉ đọc sổ chính và chỉ thêm vào `PURGE_RECEIPT_BACKUP_REMOTE` trên một đích offsite khác. Bản sao này có chính sách lưu riêng với dump DB. Khi cần khôi phục sổ, trỏ `PURGE_RECEIPT_REMOTE` của tiến trình restore tới bản sao đã xác minh. Nếu cả DB nguồn và sổ đều thiếu bằng chứng, staging giữ dữ liệu cách ly tới khi owner quyết định.

## Audit worker nick Zalo

Với DB hiện hữu, áp migration [008-nick-audit.sql](postgres/008-nick-audit.sql) bằng quy trình migration trước khi bật endpoint. Cấp cùng một `NICK_WORKER_AUTH` ngẫu nhiên (tối thiểu 32 byte) cho runtime và một worker. Reverse proxy TLS chuyển WebSocket Upgrade của `/internal/nick-worker` đến `ttd-zalo-runtime:8080` và giữ header Authorization. Cảnh báo bền xuất hiện ở mục Báo cáo và cảnh báo trên trang quản trị owner. Endpoint tiếp nhận audit cho lượt reply đã được đăng ký trước trong `send_log` với `agent='nick-worker'`.

### Web operator API and OA

Apply `postgres/009-web-operator.sql` once as database administrator on existing databases, after migrations `007` and `008` where present. The SQL provisions no default account or price. To create or rotate an operator, run `node ops/web-provision-operator.mjs` with administrator PostgreSQL connection settings and pass `account`, `label`, `role` and `passphrase` as JSON on standard input through a secure local process. Rotation revokes prior sessions. Set `web_operators.enabled=false` to disable access.

Build the web SPA with `npm run build`, serve `apps/ttd-zalo-web/dist` over HTTPS, and proxy `/api/v1/` to the runtime service on the same origin. Set `WEB_ORIGIN` to that exact HTTPS origin without a trailing slash. For OA, set `CHANNEL_MODE=oa` and configure `OA_APP_ID`, `OA_ID`, `OA_APP_SECRET`, `OA_WEBHOOK_SECRET`, and a persistent 32-byte hex `OA_ENVELOPE_KEY`. Provision the OA token pair through the OA authorization bootstrap and route `/webhooks/zalo-oa` to the runtime. Monthly quota defaults to 500. No paid overflow is used for operator quotes. Optional `WEB_USD_VND` exposes the configured budget conversion in the UI.

Use the authoritative catalogue and customer records in PostgreSQL. The administrator enables an approved price by inserting a versioned `web_approved_prices` row referencing `catalogue.id`; retire a version by setting `revoked_at`. An OA recipient must have a verified `channel_identities` entry for the configured OA ID, linked to the same customer as the hashed `runtime_customer` mapping. Current proof-backed `respond` and `send` consent and a retained inbound admission record are required by Guard.

Web deletion creates a review request. Web work items and room messages are persisted for operators. Nick STOP is persisted in runtime settings. Each deployment still needs its approved channel accounts and worker configuration.

### Ghép cặp nick worker

Áp `postgres/014-nick-enrollment.sql` một lần cho DB đang chạy trước khi dùng ghép cặp. Runtime có `WEB_ORIGIN` nhận mã dùng một lần tại `POST /nick-worker/pair` và xác thực credential riêng khi nâng cấp WSS tại `/nick-worker/socket`. Dùng mẫu Nginx cùng PR. Vẫn chặn `/internal/nick-worker` từ ngoài. Giao diện chủ dự án cấp mã và thu hồi kết nối. Runtime đặt STOP khi ghép cặp hoặc thu hồi. Endpoint quản lý kết nối và audit, chưa triển khai điều phối gửi nick.
