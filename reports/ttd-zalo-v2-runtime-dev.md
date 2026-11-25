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
