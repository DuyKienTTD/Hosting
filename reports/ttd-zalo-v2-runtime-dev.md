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
