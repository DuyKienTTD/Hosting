# Mục tiêu và lộ trình vận hành

Cập nhật: 2026-11-21  
Phạm vi: repository `DuyKienTTD/Hosting`

## 1. Mục tiêu tổng thể

Xây dựng một hệ thống vận hành hosting và AI automation có thể kiểm chứng, lặp lại và bàn giao được. Mọi thay đổi phải để lại dấu vết trong Git, phân biệt rõ dữ kiện đã xác minh, đề xuất biên tập và vấn đề còn chưa xác định.

### Kết quả cần đạt

1. **Vận hành an toàn:** VPS, Docker, reverse proxy, firewall, backup và secret được quản lý theo nguyên tắc thay đổi nhỏ, có kiểm tra trước và có đường lui.
2. **AI phối hợp có kiểm soát:** mỗi AI có vai trò, đầu vào, đầu ra và giới hạn rõ ràng; không AI nào tự ý chuyển một giả định thành sự thật.
3. **Tự động hóa có bằng chứng:** workflow, API, media pipeline và các tích hợp chỉ được đánh dấu hoàn tất khi có log, response hoặc checkpoint tương ứng.
4. **Tài liệu sống:** `STATE.md`, `CATALOG.yaml`, task, report, rule và changelog được cập nhật cùng một đợt thay đổi.
5. **Tăng trưởng có đo lường:** nội dung, SEO, website, media, quảng cáo và thương mại điện tử đều có mục tiêu, chỉ số và tiêu chí dừng.

## 2. Mục tiêu theo giai đoạn

### Giai đoạn 0, chuẩn hóa nền tảng, 2026-11-21 đến 2026-12-05

- Hoàn thiện quy tắc phối hợp AI trong `rules/`.
- Chuẩn hóa mẫu task, report, decision và runbook.
- Xác nhận topology VPS, Docker, reverse proxy, backup và các endpoint health.
- Tạo một task riêng cho mọi thay đổi có tác động đến production.
- Không đưa IP, hostname nội bộ, token, API key, cookie, private URL hoặc nội dung `.env` vào Git.

**Tiêu chí đạt:** một người khác có thể đọc README, PROJECT, STATE, rule và task mới nhất để biết việc gì đang làm, bằng chứng ở đâu và bước tiếp theo là gì.

### Giai đoạn 1, độ tin cậy vận hành, 2026-12-06 đến 2027-01-04

- Thiết lập kiểm tra định kỳ cho container, disk, CPU/RAM, restart loop, backup và HTTPS.
- Mỗi tích hợp phải có health check, timeout, retry có giới hạn, idempotency và log tối thiểu.
- Tách sandbox khỏi production; mọi thử nghiệm có khả năng ghi dữ liệu phải có approval gate.
- Ghi nhận incident và hậu kiểm trong `reports/`.

**Tiêu chí đạt:** lỗi có thể được phát hiện, khoanh vùng, rollback và ghi lại mà không cần đoán dựa trên trí nhớ.

### Giai đoạn 2, tự động hóa và tăng trưởng, 2027-01-05 đến 2027-02-19

- Xây dựng backlog ưu tiên cho workflow n8n, Hermes, media, SEO, WordPress/WooCommerce và các kênh phân phối.
- Mỗi workflow có owner, trigger, input, output, quyền truy cập, giới hạn chi phí và kế hoạch khôi phục.
- Đo lường conversion, uptime, lỗi workflow, độ trễ, chi phí AI và chất lượng nội dung.
- Chỉ mở rộng production sau khi sandbox và kiểm thử chấp nhận đạt PASS.

**Tiêu chí đạt:** các workflow quan trọng có thể chạy lặp lại, truy vết được và không phụ thuộc vào một cuộc trò chuyện riêng lẻ.

## 3. Chỉ số điều hành

- **Reliability:** uptime, số incident, thời gian phát hiện, thời gian khôi phục, số lần restart ngoài kế hoạch.
- **Security:** secret exposure = 0, backup được kiểm tra, quyền tối thiểu, thay đổi firewall có bằng chứng.
- **Automation:** tỷ lệ workflow PASS, lỗi retry, lỗi timeout, queue backlog và thời gian xử lý.
- **Content/Growth:** nội dung đã xuất bản, index coverage, organic traffic, leads, conversion và chi phí mỗi kết quả.
- **Governance:** task có acceptance criteria, report có evidence, thay đổi có commit và changelog.

Không đặt chỉ tiêu số khi chưa có baseline. Nếu thiếu dữ liệu, ghi `UNKNOWN` và tạo task đo lường thay vì suy đoán.

## 4. Nguyên tắc ưu tiên

1. An toàn và khả năng khôi phục.
2. Tính đúng đắn và bằng chứng.
3. Độ tin cậy của workflow hiện tại.
4. Tự động hóa các việc lặp lại.
5. Tăng trưởng, nội dung và tối ưu hóa.
6. Tính tiện lợi hoặc thử nghiệm mới.

Khi có xung đột, ưu tiên mục ở trên cao hơn, trừ khi có decision record nêu rõ lý do.

## 5. Definition of Done

Một task chỉ được `complete` khi:

- mục tiêu và phạm vi đã rõ;
- thay đổi đã được thực hiện hoặc lý do không thể thực hiện đã được ghi;
- acceptance criteria đã được kiểm tra;
- evidence/report được liên kết;
- `STATE.md`, `CATALOG.yaml` hoặc `CHANGELOG.md` được cập nhật nếu phạm vi yêu cầu;
- không còn secret hoặc dữ liệu nhạy cảm trong diff;
- commit message mô tả đúng thay đổi.
