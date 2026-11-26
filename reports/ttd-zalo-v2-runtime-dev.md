---
id: ttd-zalo-v2-runtime-dev
type: report
status: draft
owner: ChatGPT Work
task_id: V2-02-RUNTIME
lifecycle: ACTIVE
retention_trigger: A0 completes runtime acceptance
updated_at: 2026-11-26
sensitivity: public
---

# V2-02-RUNTIME · Bàn giao developer

Base [242dbfe](https://github.com/DuyKienTTD/Hosting/commit/242dbfe7ec9013739709fdc7ec76277f67d8a359). Nhánh `dev/ttd-zalo-v2-runtime` hướng vào `dev/ttd-zalo-mvp01`. Write-set gồm hai thư mục ứng dụng và báo cáo này. Nguồn QA [ZPC-04 Test Matrix](https://github.com/DuyKienTTD/Hosting/blob/6eb9efb3b45ae81afde5373de78bc8e96a9645db/program/zalo-mvp01/zpc-04-security/TEST_MATRIX.md). A0 là người nghiệm thu tiếp theo. Work order V2-02-RUNTIME được A0 giao trực tiếp trong phiên ngày 26/11/2026. Nguồn GitHub gồm [roadmap V2](https://github.com/DuyKienTTD/Hosting/blob/e4d9f6c34ca3d366f5e816e214de4293340b6fb9/program/zalo-mvp01/PRODUCT_V2_ROADMAP.md), [quyết định V2](https://github.com/DuyKienTTD/Hosting/blob/e4d9f6c34ca3d366f5e816e214de4293340b6fb9/decisions/ZALO-PRODUCT-DIRECTION-02.md) và [work order tiền nhiệm HOSTING-ZALO-RESUME-01](https://github.com/DuyKienTTD/Hosting/blob/6eb9efb3b45ae81afde5373de78bc8e96a9645db/tasks/zalo-resume-01-gov.md) để truy vết các điều kiện đã được A0 thay thế.

- [Runtime và triển khai](../apps/ttd-zalo-agent-server/DEPLOY.md) dùng Node 24, SQLite, kênh giả và điều phối Claude Messages tool use theo các lựa chọn hữu hạn. Runtime chia sẻ logic policy/transaction, schema CRM, truy xuất tri thức và quyết định giá của desktop. Model đề xuất vai trò và lựa chọn. CSKH dùng bản trả lời có nguồn do mã xác minh, kể cả phần thông số khi giá thiếu. Mẫu chào hàng có sẵn, lịch cộng đồng và chiến dịch đến từ cấu hình người vận hành. Dữ liệu đầu vào không được cấp quyền gọi công cụ.
- Quảng cáo và lời mời đi qua kiểm tra bạn bè, consent, opt-out, giờ Việt Nam, giới hạn liên hệ/ngày, giãn nhịp và tự dừng khi bất thường. Lượt bán hàng yêu cầu sự kiện chấp nhận kết bạn và consent quảng cáo riêng. SQLite giữ khóa gửi trước khi transport bắt đầu. Khi trạng thái giao hàng mơ hồ, giữ lượt và chặn phát lại. Nút DỪNG và báo cáo/cảnh báo nằm trên trang vận hành qua SSH, cũng có CLI. Cảnh báo cần mở trang hoặc đọc CLI.
- Sổ ngân sách ghi dự phòng và usage theo token, có tiền trần $195 và chia hạn mức theo chu kỳ. Bảng giá Anthropic, ngày xem, model, hệ số Batch và các ngưỡng nằm trong config. Tin vượt hạn mức giữ dấu hàng chờ trong SQLite, nội dung giữ trong RAM trong thời hạn cấu hình. Khôi phục hàng chờ sau restart phụ thuộc replay của adapter. Báo cáo tóm tắt và kết quả batch lưu trên VPS.
- Phạm vi chưa xác minh gồm Docker build/Compose restart trên VPS, cache hit thực tế, credit thực tế và bảo đảm toàn chu kỳ khi nhiều ứng dụng cùng tiêu credit. Subiz chỉ là khung, chờ đối chiếu hợp đồng V2-01. Mã nguồn và mô phỏng đã thực thi ngoại tuyến với dữ liệu tổng hợp. Chưa kết nối Zalo/Subiz hoặc gọi Claude API thật.

## Bằng chứng thực thi

| Lệnh | Exit | Kết quả |
|---|---:|---|
| Desktop `ELECTRON_SKIP_BINARY_DOWNLOAD=1 npm ci --no-audit --no-fund` | 0 | Cài lockfile |
| Desktop `npm run typecheck`, `npm run build`, `npm test` | 0 | 20/20 |
| Desktop `node scripts/evaluate-corpus.mjs` | 0 | 48/48 action, source, hiệu ứng và dữ kiện |
| Server `npm ci --no-audit --no-fund`, `npm run typecheck`, `npm run build`, `npm test` | 0 | 18/18, gồm E2E 7 ngày, tháng 30 ngày và HTTP Claude/Batches bằng fixture |
| Server smoke với `node dist/ttd-zalo-agent-server/src/main.js`, `curl` và Node assertions | 0 | Health, xác thực, CSRF, DỪNG agent, backup SQLite qua `PRAGMA integrity_check` |
| `python3 -m unittest discover -s scripts -p test_data_integrity.py` | 0 | 15/15 |
| `python3 -m unittest discover -s program/kng -p 'test_*.py'` | 0 | 134/134 |
| `python3 program/kng/validate.py --json`, `python3 scripts/validate-catalog-partitions.py` | 0 | PASS, 18 bản ghi đúng |

INCIDENT: Sandbox thiếu Docker/Compose và PowerShell. Các lệnh container/VPS và `scripts/validate-repository.ps1` chưa chạy. Đã kiểm tra ứng dụng Node và backup SQLite trực tiếp, chạy bộ kiểm tra Python tương ứng workflow Data integrity. Kiểm thử phát hiện lỗi bootstrap migrate, lời mời tính chính reservation hiện tại và định dạng Content-Type của form STOP. Đã sửa và chạy lại.

## V2-02-RUNTIME-FIX1 · 26/11/2026

Theo [biên nhận A0 trên PR #71](https://github.com/DuyKienTTD/Hosting/pull/71#issuecomment-7174651830), tại đúng 70% trần an toàn runtime chọn Haiku, tại đúng 90% ngừng giữ chỗ cho tác vụ nền, tại $195 hoặc khi có `budgetStop` chặn mọi thao tác ghi kênh. Kiểm tra dùng cùng số dư SQLite như khi giữ chỗ cho AI và chạy trong transaction ngay trước khi bắt đầu gửi. Lượt ưu đãi đã xếp hàng và lượt bán hàng đang chờ giữ trạng thái khi bị chặn. Tin khách còn hiệu lực giữ trong hàng chờ. Nếu đã có quyết định AI, runtime yêu cầu quyết định mới sau khi gỡ chặn, kể cả khi khôi phục hàng chờ qua replay. Cảnh báo hiển thị qua trang vận hành và CLI.

| Chạy lại trên Linux, Node 24 | Exit | Kết quả |
|---|---:|---|
| Cả hai app `npm ci --no-audit --no-fund` (desktop với `ELECTRON_SKIP_BINARY_DOWNLOAD=1`), `npm run typecheck`, `npm run build`, `npm test` | 0 | Desktop 20/20, runtime 31/31 |
| Desktop `node scripts/evaluate-corpus.mjs` | 0 | 48/48 |
| Runtime `node --test --test-name-pattern="seven-day end to end" test/runtime.test.mjs` | 0 | 1/1 |
| Runtime `node --test --test-name-pattern="month budget under sustained demand" test/runtime.test.mjs` | 0 | 1/1 |

13 ca mới gồm chín phép thử sát biên dưới/đúng/trên của 70%, 90% và $195, ưu đãi được xếp lúc 06:30 ICT rồi gặp trần lúc 08:30 ICT, lượt `sales-ready` và sáu loại thao tác ghi kênh, cùng hai ca tin khách bị giữ do ledger chạm trần khi chuẩn bị gửi hoặc do `budgetStop` trong lúc AI đang xử lý. Các ca chạm trần quan sát 0 lượt gửi.

## V2-02C-GUARD-BUDGET-FIX · 26/11/2026

Base `c5cccd45954b8aa26874978bc7ace8a7cd667df7`. Cập nhật nhận diện opt-out cả tiếng Việt có dấu, không dấu và viết tắt. Từ đơn phải đứng riêng, còn cụm phải khớp ý định dừng. Footer dùng “Nhắn DỪNG NHẬN TIN để không nhận ưu đãi”. “Không” đơn lẻ giữ nguyên consent.

Sonnet giữ chỗ theo prompt thực tế bằng ước tính byte văn bản cộng overhead, cộng giới hạn output. Lượt thử vẫn đủ hạn mức sau khi dùng $2,75 trong ngày. SQLite quyết toán theo usage và bật STOP khi model sai hoặc usage vượt dự phòng. Các ngưỡng 70/90/100% và chặn transport đã xếp hàng vẫn đạt trong test. Schema 2 giữ khả năng quyết toán các lượt cũ theo bảng giá lịch sử. Ước tính input cần đối chiếu với provider trong pilot, và kiểm usage vượt dự phòng chỉ có thể thực hiện sau phản hồi.

Dùng Sonnet 5.5 ($2/$10) và Haiku 5.5 ($0,10/$0,50 trong tier tối đa 100.000 token) theo USD/triệu token input/output. Giá đọc 26/11/2026. ZPC-02 xác nhận Sonnet 5 là Legacy và hướng nâng cùng mức giá. Chế độ tương thích Anthropic có HTTPS base URL và khóa riêng, model allowlist, từ chối phản hồi báo model khác và có hạn mức ngày riêng cùng tổng trần. Chỉ bật sau khi xác minh nguồn credit/biểu phí Hostinger, cấu hình và payload thực tế. [ZPC-02](https://github.com/DuyKienTTD/Hosting/blob/367c36454e021dbf11ea30afb72ebff0f1131afc/program/zalo-mvp01/zpc-01-02/ZPC-02-ai-provider-decision.md) · [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing) · [Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/overview) · [Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview).

| Lệnh trên Node 24.22.3 | Exit | Kết quả |
|---|---:|---|
| Hai app `npm ci --no-audit --no-fund`, `npm run typecheck`, `npm run build`, `npm test` | 0 | Server 47/47 với `PLAYWRIGHT_TEST_EXECUTABLE=/tmp/chromium`, desktop 20/20 với `ELECTRON_SKIP_BINARY_DOWNLOAD=1` khi cài |
| Desktop `node scripts/evaluate-corpus.mjs` | 0 | 48/48 |

Không gọi Claude, Hostinger, Zalo hay Subiz thật. Test Playwright dùng Chromium headless từ gói npm tạm và HTML cục bộ.

## V2-02C-FIX1 · 26/11/2026

Theo biên nhận độc lập trên [PR #73](https://github.com/DuyKienTTD/Hosting/pull/73), bộ nhận diện tất định xử lý chủ ngữ, chuỗi hậu tố và yêu cầu rút khỏi danh sách quảng cáo ở dạng có hoặc không dấu. Từ đơn vẫn chỉ có hiệu lực khi đứng riêng. Hai test hồi quy bao gồm 16 câu dương mới (ba câu báo lỗi, ba biến thể không dấu, mười câu tự nhiên khác), 18 câu âm mới và các ca cũ giữ nguyên.

Bước phân loại con đường tin nhắn riêng hiện tại có hai lựa chọn bổ sung. Yêu cầu rõ ràng có thể thu hồi quảng cáo đúng đối tượng trong transaction và hủy việc chờ. Ý định chưa rõ chỉ tạo cờ vận hành với ID nội bộ, không đổi consent. Cổng gửi tiếp tục kiểm tra trạng thái và revision tất định. Test bằng FakeProvider xác nhận tin nhóm không có lựa chọn này, giá trị đăng ký lại nằm ngoài allowlist và lượt quảng cáo cũ bị chặn. Chưa đo phân loại bằng Claude thật.

| Lệnh trên Node 24.22.3 | Exit | Kết quả |
|---|---:|---|
| Cả hai app `npm run typecheck`, `npm run build`, `npm test` (server với `PLAYWRIGHT_TEST_EXECUTABLE=/tmp/chromium`) | 0 | Server 49/49, desktop 20/20 |
| Server `PLAYWRIGHT_TEST_EXECUTABLE=/tmp/chromium node --test --test-name-pattern='Playwright fixture' test/adapters.test.mjs` | 0 | 1/1 |
| Desktop `node scripts/evaluate-corpus.mjs` | 0 | 48/48 |

## V2-02C-FIX2 · 26/11/2026

Thay danh sách cụm hoàn chỉnh bằng luật kết hợp dấu hiệu dừng và đối tượng nhắn tin hoặc quảng cáo trong cùng một câu. Khoảng cách mặc định là 8 từ và có thể cấu hình qua `optOutMaxGapWords`. Câu hỏi, ngữ cảnh giao dịch rõ ràng và từ “dùng” được xử lý riêng. Từ đơn tiếp tục chỉ có hiệu lực khi đứng riêng. Tin riêng chưa đủ căn cứ được gắn cờ ngay khi nhận, kể cả khi AI đang dừng. Nhánh phân loại AI hiện hữu vẫn chỉ có thể thu hồi quảng cáo hoặc gắn cờ.

Ba câu báo lỗi của A0 nằm trong tập phát triển và đều đạt. [Tập kiểm định riêng](../apps/ttd-zalo-agent-server/test/fixtures/opt-out-validation.json) được soạn sau khi hoàn thiện luật. Không chỉnh luật theo kết quả của tập này. Lần chấm đầu tiên đạt **30/30 ca xin ngừng và 20/20 ca âm**, gồm nhiều kiểu diễn đạt, tên shop, số tổng hợp, không dấu và viết tắt.

| Lệnh trên Node 24.22.3 | Exit | Kết quả |
|---|---:|---|
| Hai app `npm run typecheck`, `npm run build`, `npm test` (server với `PLAYWRIGHT_TEST_EXECUTABLE=/tmp/chromium`) | 0 | Server 52/52, desktop 20/20 |
| Server `node --test test/opt-out-validation.test.mjs` (chấm corpus riêng) | 0 | 30/30, 20/20 |
| Server `PLAYWRIGHT_TEST_EXECUTABLE=/tmp/chromium node --test --test-name-pattern='Playwright fixture' test/adapters.test.mjs` | 0 | 1/1 |
| Desktop `node scripts/evaluate-corpus.mjs` | 0 | 48/48 |

## V2-02C-FIX3 · 26/11/2026

Theo biên nhận lần 3 trên [PR #73](https://github.com/DuyKienTTD/Hosting/pull/73), yêu cầu rõ ràng mới chuyển `opted_out`. Luật kiểm tra động từ và đối tượng trong một mệnh đề, loại câu hỏi/thao tác với tin cụ thể/ngữ cảnh thương mại khỏi quyết định thu hồi vĩnh viễn. Dấu hiệu từ chối cùng ngữ cảnh nhắn tin chưa đủ chắc sẽ lưu `ads_paused_review`, giữ consent và gắn cờ. Guard chặn cả hai trạng thái với quảng cáo. Test chứng minh phản hồi 1:1 còn đủ quyền vẫn gửi được. Trang vận hành có nút xác nhận thu hồi hoặc bỏ tạm dừng, kiểm CSRF và phiên bản phiếu. AI chỉ xác nhận thu hồi hoặc đặt cờ.

[Corpus cũ](../apps/ttd-zalo-agent-server/test/fixtures/opt-out-validation.json) giữ nguyên câu và chấm theo tiêu chí mới. Tám câu A0 thành ca hồi quy. [Tập mới 30 + 20](../apps/ttd-zalo-agent-server/test/fixtures/opt-out-fix3-validation.json) qua Runtime và Guard đạt **0/30 lượt quảng cáo gửi**, **0/20 opted_out nhầm**, **16/20 ca âm tạm dừng (80%)**. Đây là đánh đổi của việc tạm dừng khi có dấu hiệu chưa chắc chắn, cần người vận hành xác nhận. Lần chạy đầu phát hiện một câu hỏi gián tiếp cần quy tắc loại trừ và một ca kiểm khoảng cách dùng cụm vượt ngưỡng 2 từ. Đã sửa và chạy lại. Kết quả là kiểm thử tổng hợp, chưa đo phân loại Claude thật.

| Lệnh trên Node 24.22.3 | Exit | Kết quả |
|---|---:|---|
| Hai app `npm run typecheck`, `npm run build`, `npm test` (server với `PLAYWRIGHT_TEST_EXECUTABLE=/tmp/chromium`) | 0 | Server 54/54, desktop 20/20 |
| Server `PLAYWRIGHT_TEST_EXECUTABLE=/tmp/chromium node --test --test-name-pattern='Playwright fixture' test/adapters.test.mjs` | 0 | 1/1 |
| Desktop `node scripts/evaluate-corpus.mjs` | 0 | 48/48 |

## V2-02C-FIX4 · 26/11/2026

Bộ lọc tất định chỉ dừng hoặc tạm dừng quảng cáo khi cùng câu có dấu hiệu tiếp thị và từ chối, ngoài lệnh đứng riêng. Phủ định kép và lỗi giao dịch đi qua trạng thái active. Dấu hiệu bổ sung gồm dẹp, cắt, bớt, tránh, miễn và đủ rồi. Chín câu A0 đều đạt.

[Tập FIX4](../apps/ttd-zalo-agent-server/test/fixtures/opt-out-fix4-validation.json) đi qua Runtime và Guard. Kết quả **0/30 quảng cáo lọt**, **0/20 ca âm khó bị opted_out**, **0/30 tin thường bị opted_out**, **0/30 tin thường bị paused**. Hai tập cũ giữ nguyên dữ liệu và được chấm để thấy ảnh hưởng của chính sách mới. Mức chặn tất định lần lượt là **26/30 và 17/30**, vì câu chỉ có dấu hiệu tin/gửi/nhắn hoặc hai dấu hiệu ở hai câu riêng cần lớp AI. Các ca âm cũ vẫn 0 opted_out nhầm. Chưa đo lớp AI trên pilot.

Node 24.22.3. Typecheck, build và test đều exit 0. Server **55/55** gồm Playwright fixture, desktop **20/20**, corpus **48/48**.

## V2-02C-FIX5 · 26/11/2026

Ads tắt mặc định. Guard trả và ghi `ads_disabled` trước các điều kiện khác, trước tra liên hệ và trước gửi; luồng CSKH 1:1 vẫn áp dụng policy riêng. Chỉ bật `ADS_ENABLED=true` sau khi đo lớp AI một chiều trên tin thật và được chủ dự án duyệt.

Phủ định trong cùng mệnh đề có thể chi phối động từ dừng qua các từ trung gian. Bộ lọc tất định không thu hồi consent trong mệnh đề như vậy. Router cũng bỏ lựa chọn thu hồi khi phát hiện phạm vi phủ định. Sáu câu phủ định và ca AI trả lựa chọn ngoài danh sách đều đạt hồi quy. Tập FIX4 giữ kết quả 0/30 quảng cáo lọt, 0/20 opted_out nhầm ở ca âm khó và 0/30 tin thường tạm dừng.

Node 24.22.3. Typecheck, build và test exit 0. Server 58/58, desktop 20/20, Playwright chạy riêng 1/1, corpus 48/48. Chưa đo AI trên tin thật.

## Z4-S1-DATA · Delivery log

Nguồn quyết định [DIRECTION-04 tại main](https://github.com/DuyKienTTD/Hosting/blob/b9ec088/decisions/ZALO-PRODUCT-DIRECTION-04.md). Base `480fcdd` chứa bản merge PR #73.

- Migration Postgres, repository với phân quyền tại tầng dịch vụ, intake hàng đợi và phiếu việc độc lập với nội dung tin khách.
- Retention tự động trong phạm vi tin nhắn, có kiểm tra version/chính sách/legal hold, cách ly, audit chỉ ghi thêm và tombstone ngoài DB.
- Compose riêng, backup mã hóa và restore vào DB tạm, quy trình cấu hình và rollback trong [DEPLOY](../apps/ttd-zalo-agent-server/DEPLOY.md).
- Runtime cũ vẫn dùng repository SQLite. Chưa có cutover các luồng policy, AI và gửi tin sang repository Postgres. Chỉ test với fixture.

| Kiểm tra trên Node 24.22.3 | Exit | Kết quả |
|---|---:|---|
| Assistant `npm run typecheck`, `npm run build`, `npm test` | 0 | 20/20 |
| Runtime `npm run typecheck`, `npm run build` | 0 | TypeScript đạt |
| Runtime `RUN_POSTGRES_TESTS=1 npm test` trên PostgreSQL 17.12, có Chromium | 0 | 62/62, gồm kiểm quyền, xóa và restore bản backup cũ |
| `docker compose -f compose.data.yaml --profile maintenance config --quiet` | 0 | Compose hợp lệ với biến giả lập |

CI `Z4 Postgres data` chạy lại bằng PostgreSQL service container.

## Z4-S1-DATA-B · Runtime trên Postgres

Bổ sung trên PR #75, từ HEAD `32d080b`. Runtime triển khai dùng Postgres cho AI, ledger ngân sách, journal kênh, consent/opt-out và gửi. SQLite phục vụ fixture cục bộ. Ảnh runtime loại bản cài đặt repository SQLite khỏi output triển khai.

- Migration 002 và quyền DB riêng cho runtime. Consent theo mục đích có bằng chứng, hạn hiệu lực và lịch sử rút lại. Tin 1-1 chỉ được ghi nội dung khi khách còn consent lưu giữ.
- Guard đọc cờ `ADS_ENABLED`, consent và `ad_status` sau bước xác minh đích. Cùng transaction, Guard xét lại giới hạn và ghi giữ chỗ vào `send_log`. Khóa Postgres giữ đến khi bắt đầu gọi kênh. Ghi kết quả trong transaction kế tiếp. Lượt `unknown_delivery` và giữ chỗ chưa quyết toán không tự chạy lại. Restore bật STOP để đối soát trước khi phục vụ.
- [DEPLOY](../apps/ttd-zalo-agent-server/DEPLOY.md) ghi cấu hình Postgres mặc định, migration cho DB đã có schema 001 và quy trình đối soát khi restore. API dữ liệu `/messages` chuẩn bị cho tích hợp OA tiếp theo. Adapter runtime hiện có đi qua đường tiếp nhận của runtime.

| Kiểm tra | Kết quả |
|---|---|
| Runtime Node 24 `npm run typecheck` và `npm run build` | Exit 0 |
| Assistant Node 24 `npm run typecheck`, `npm run build`, `npm test` | Exit 0, 20/20 |
| Postgres 17 `node --test test/postgres.test.mjs` với `RUN_POSTGRES_TESTS=1` | Exit 0, 5/5 |
| SQLite cục bộ `npm test` | Exit 0, 58 đạt, 2 bộ Postgres bỏ qua khi không có DB |
| `docker compose --profile maintenance config --quiet` và cùng lệnh với `-f compose.data.yaml` | Exit 0 |

CI chạy toàn bộ suite runtime với Postgres service container. Ca tích hợp dùng role triển khai `data_runtime` và đi từ MockChannel qua FakeProvider, Guard đến `send_log`. Ca kiểm tra nhìn thấy giữ chỗ đã commit từ kết nối độc lập, thay đổi cờ quảng cáo, trạng thái và consent sau xác minh đích, và chặn gửi lại khi kênh trả `unknown_delivery`.

## Z4-S1-FIX1 · Biên nhận tombstone trước purge

Migration 003 bỏ `authorize_purge`. Chỉ `data_worker` được gọi entrypoint purge từ các vai trò dịch vụ. Worker giữ transaction mở, ghi và đọc lại tombstone ở kho độc lập, rồi ký biên nhận gắn với đúng bản ghi và phiên bản. PostgreSQL xác thực biên nhận trước khi ghi audit và xóa. Trigger chặn DELETE và TRUNCATE trực tiếp thiếu biên nhận.

Hồi quy Postgres tái tạo backup → cách ly → hết hạn → gọi trực tiếp theo từng vai trò → restore. Bản ghi vẫn còn khi purge bị từ chối. Khi SQL lỗi sau khi xóa, dữ liệu và audit nội bộ rollback, tombstone đã ghi ngoài DB vẫn bền. Lần chạy lại tái sử dụng tombstone, purge thành công, và restore backup cũ không làm bản ghi sống lại. `DEPLOY.md` ghi cách cấp khóa và áp migration trước khi chạy worker.

## Z4-S1-FIX2 · Tombstone hai pha

Migration 004 lưu biên nhận commit theo `purge_id` và phiên bản trong transaction xóa. Worker ghi pending trước khi xóa, chỉ xuất bản confirmed có proof lấy từ biên nhận đã commit. Lần chạy lại đối soát xác nhận chưa xuất bản. Job dọn pending quá 24 giờ theo biên nhận của DB nguồn, giữ các lượt commit đang chờ xuất bản.

Restore chỉ áp confirmed có proof hợp lệ lên bảng tin nhắn. Legal hold, danh tính bản ghi lệch và phiên bản mới hơn chặn replay, giữ bản ghi và ghi cảnh báo. Pending và tệp cũ không có bằng chứng commit không được áp. Hồi quy Postgres tái hiện rollback sau DELETE, đặt legal hold rồi backup/restore, cùng các lỗi sau ghi pending, sau commit trước confirm và sau confirm trước ghi nhận xuất bản. Nếu mất DB nguồn trước khi xuất bản confirmed và bản backup không chứa commit, restore giữ bản ghi vì thiếu bằng chứng xác nhận.
