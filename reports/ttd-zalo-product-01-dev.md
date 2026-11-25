---
id: ttd-zalo-product-01-dev
type: report
status: draft
owner: ChatGPT Work
task_id: TTD-ZALO-P1-OFFLINE
lifecycle: DURABLE
updated_at: 2026-11-26
sensitivity: public
---

# TTD Zalo Assistant · giao bản ngoại tuyến P1

- Bản mã được kiểm tra: `9e3f63bb9ecd92bf856e26fc90b7febd338bc85b`, tree `2cb941c8aa5d91be6bed723a1fe57265a977975a`. Base MVP: `52b7c5ccac572b170925d28c44c5613c1e73a849`. Commit tiếp theo chỉ thêm báo cáo này.
- Đặc tả: [kế hoạch ZPC-06/07/08/10](https://github.com/DuyKienTTD/Hosting/blob/3dfc6fa1a0140267ac8d5604a5169299bd62b68d/program/zalo-mvp01/PRODUCT_COMPLETION_PLAN.md), [corpus](https://github.com/DuyKienTTD/Hosting/tree/3dfc6fa1a0140267ac8d5604a5169299bd62b68d/program/zalo-mvp01/zpc-03-corpus) và [ma trận âm](https://github.com/DuyKienTTD/Hosting/blob/3dfc6fa1a0140267ac8d5604a5169299bd62b68d/program/zalo-mvp01/zpc-04-security/TEST_MATRIX.md).
- Lệnh thực thi P1 do A0 giao trực tiếp trong phiên Work. [Work order quản trị mở lại phạm vi ngoại tuyến](https://github.com/DuyKienTTD/Hosting/blob/3dfc6fa1a0140267ac8d5604a5169299bd62b68d/tasks/zalo-resume-01-gov.md) ghi nhận ranh giới ủy quyền.
- ZPC-06: định danh account/user/thread/message ổn định cho hai khách mẫu. Hồ sơ có dòng thời gian và provenance từ tin nhắn đã lưu. Xuất đúng khách, xóa dữ liệu nội dung và thu hồi quyền, giữ ID chống phát lại và audit tối thiểu.
- ZPC-07: migration SQLite lên v3, FTS5/BM25, lọc SKU chính xác, bản ghi sản phẩm/giá/chính sách có nguồn và ngày hiệu lực. Tệp TXT/MD được tìm kiếm dưới dạng văn bản. Nháp hỏi lại khi giá thiếu hoặc xung đột.
- ZPC-08 seam / ZPC-10 offline: FakeProvider đồng bộ trong main process, kiểm tra schema/nguồn và kiểm lại quyền trước khi trả nháp. UI tiếng Việt hiển thị căn cứ, ID nguồn, hồ sơ, follow-up và trạng thái Fake Channel. IPC có kiểm tra nguồn gọi, số lượng và kiểu tham số. Gửi giả lập tiếp tục qua phê duyệt chính xác, STOP, thu hồi và chống lặp. Không thêm dependency.

## Kiểm thử

| Lệnh | Exit | Kết quả |
|---|---:|---|
| `npm ci` | 0 | 79 package theo lockfile |
| `npm run typecheck` | 0 | PASS |
| `npm run build` | 0 | PASS |
| `npm test` | 0 | 17/17, gồm 10 test cũ và 7 mới |
| `node scripts/evaluate-corpus.mjs` | 0 | 48/48 khớp hành vi, tập ID nguồn, hiệu ứng và các dữ kiện chính được kiểm tra |
| `python3 -m unittest discover -s scripts -p test_data_integrity.py` | 0 | 15/15 |
| `python3 -m unittest discover -s program/kng -p 'test_*.py'` | 0 | 134/134 |
| `python3 program/kng/validate.py --json` và `python3 scripts/validate-catalog-partitions.py` | 0 | PASS |
| `python3 scripts/validate-data-integrity.py --root . --base 52b7c5ccac572b170925d28c44c5613c1e73a849 --json` | 0 | PASS |
| `powershell -NoProfile -File scripts/validate-repository.ps1` | 127 | `powershell: command not found` |

7 test mới kiểm migration/restart, FTS và các phần áp dụng của N01/N02/N06/N07/N09/N16/N24/N25/N27/N28/N30/N37/N38, cùng kiểm lại phiên sau callback đồng bộ. Corpus chạy trên Foundation/FakeProvider với SQLite trong bộ nhớ, ánh xạ hai khách trùng tên vào hai định danh riêng và chạy ca khách C trên DB riêng. 48/48 là kết quả kiểm tự động, còn giọng điệu, edit distance và nghiệm thu độc lập chưa được chấm.

**Giới hạn.** Windows launch `NOT_VERIFIED`. Electron UI smoke chưa chạy vì Linux không có display, `apt-get download xvfb` exit 100 với `Unable to locate package xvfb`. Kết quả IPC runtime của smoke còn mở. Thử nghiệm dùng dữ liệu tổng hợp, không gọi nhà cung cấp thật và không kết nối Zalo thật. Nghiệm thu độc lập thuộc A0 và reviewer được chỉ định.

## FIX1 · 26/11/2026

Sửa hai lỗi ZPC-07 trên PR #68 theo [biên nhận nghiệm thu độc lập](https://github.com/DuyKienTTD/Hosting/pull/68#issuecomment-7173315862). Baseline trước sửa: `713dfbfa68cb1ec1bcd7eb2e2eb76d9a54cfabb8`.

- Câu hỏi có cả giá và thông số trả phần thông số có nguồn, đồng thời hỏi lại khi giá thiếu hoặc xung đột. Nháp có đủ hai nguồn khi có giá và thông số hợp lệ.
- FTS5/BM25 truy xuất tài liệu liên quan cho luồng nháp. FakeProvider nhận định danh tham khảo và trích đúng ID. Nháp hướng người vận hành đối chiếu tài liệu, không diễn giải nội dung tài liệu thành kết luận nghiệp vụ. Nội dung tài liệu không đi vào adapter và giá chỉ lấy từ bản ghi giá có thẩm quyền.
- Ba test hồi quy bao phủ câu hỏi nhiều ý, trích nguồn Markdown sau mở lại DB và ca Markdown chứa lệnh thay đổi STOP/quyền/gửi hoặc giá giả.

| Lệnh chạy lại trong app | Exit | Kết quả |
|---|---:|---|
| `npm ci` | 0 | 79 package theo lockfile |
| `npm run typecheck` | 0 | PASS |
| `npm run build` | 0 | PASS |
| `npm test` | 0 | 20/20, gồm 17 test trước FIX1 và 3 hồi quy |
| `node scripts/evaluate-corpus.mjs` | 0 | 48/48 theo các tiêu chí tự động của corpus |
