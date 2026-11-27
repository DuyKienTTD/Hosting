---
id: repository-operating-plan-2026-11-21
type: task
status: ready
updated_at: 2026-11-21
sensitivity: public
owner: coordinator
---

# Kế hoạch vận hành repository và phối hợp AI

## Mục tiêu

Thiết lập cách làm việc thống nhất cho Hostinger, VPS, Docker, Hermes, n8n, website, media, SEO và các workflow AI trong repository `DuyKienTTD/Hosting`.

## Phạm vi

- Quy tắc phối hợp nhiều AI.
- Quản lý mục tiêu 30/60/90 ngày.
- Chuẩn hóa task, report, evidence và decision.
- Kiểm soát thay đổi Git và production.
- Xác định backlog ưu tiên sau khi kế hoạch được duyệt.

## Không thuộc phạm vi

- Không tự ý nâng cấp, restart, xóa hoặc thay đổi production.
- Không đưa secret, IP riêng, hostname nội bộ, token hoặc nội dung `.env` vào repository.
- Không đánh dấu các tích hợp đang `BLOCKED` là đã hoàn tất.

## Các workstream

### WS-01, Governance

- [ ] Áp dụng `rules/MULTI_AGENT_COLLABORATION.md` cho task mới.
- [ ] Kiểm tra các template còn thiếu metadata bắt buộc.
- [ ] Xác định khi nào cần cập nhật `STATE.md`, `CATALOG.yaml`, `CHANGELOG.md`.

**Acceptance:** task mới có owner, status, scope, acceptance criteria và evidence.

### WS-02, Infrastructure reliability

- [ ] Kiểm tra định kỳ container, disk, CPU/RAM, restart loop và HTTPS.
- [ ] Ghi runbook rollback cho thay đổi Docker/reverse proxy.
- [ ] Xác minh backup có thể khôi phục bằng test không phá hủy.

**Acceptance:** mỗi mục có kết quả `PASS`, `FAIL` hoặc `BLOCKED`, kèm bằng chứng và ngày kiểm tra.

### WS-03, AI integration

- [ ] Tách rõ Hermes, n8n, MCP, API private và endpoint public.
- [ ] Ghi input/output schema, timeout, retry, idempotency và log cho từng workflow.
- [ ] Thiết lập approval gate cho workflow có tác động production.

**Acceptance:** workflow quan trọng có test case thành công, lỗi xác thực, lỗi timeout và retry.

### WS-04, Website, content và media

- [ ] Phân loại mục tiêu: website, SEO, media, quảng cáo, email và thương mại điện tử.
- [ ] Tạo backlog nội dung theo mục tiêu kinh doanh và kênh phân phối.
- [ ] Đo lường trước khi tối ưu, không dùng giả định thay cho baseline.

**Acceptance:** mỗi sáng kiến có owner, audience, KPI, trạng thái xuất bản và link evidence.

### WS-05, Security và data governance

- [ ] Chạy kiểm tra secret exposure trước mỗi push.
- [ ] Duy trì nguyên tắc least privilege và tách sandbox/production.
- [ ] Ghi rõ dữ liệu nào được lưu, nơi lưu, thời hạn giữ và cách xóa.

**Acceptance:** không có secret trong diff; mọi exception có decision record.

## Ưu tiên thực hiện

1. Hoàn thiện governance và acceptance criteria.
2. Xác minh trạng thái hạ tầng hiện tại.
3. Chuẩn hóa health check và rollback.
4. Kiểm thử các tích hợp AI theo ma trận lỗi.
5. Xây dựng backlog growth/content/media dựa trên baseline.

## Definition of Ready

Task chỉ chuyển sang `ready` khi có:

- mục tiêu một câu;
- owner;
- phạm vi và ngoài phạm vi;
- dependencies;
- acceptance criteria;
- rủi ro và approval cần thiết;
- đường dẫn evidence dự kiến.

## Definition of Done

Task chỉ chuyển sang `complete` khi có kết quả kiểm tra, evidence, commit/PR reference và cập nhật metadata cần thiết.

## Blocker hiện tại

- Chưa tự động xác nhận toàn bộ health check của production trong tài liệu này.
- Các tích hợp private/API phải được xác minh riêng, không suy luận từ tên dịch vụ.
- Các chỉ số growth chưa có baseline trong task này.

## Kết quả đầu ra dự kiến

- `GOALS_AND_ROADMAP.md`
- `rules/MULTI_AGENT_COLLABORATION.md`
- task này
- commit có message `docs: add multi-agent operating plan and task governance`
