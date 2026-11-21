---
id: agent-hermes
type: knowledge
status: current
updated_at: 2026-11-21
sensitivity: public-redacted
---

# Hermes Agent — AI reasoning và tool execution

**Role ưu tiên:** AI operator/analyst; lập kế hoạch, phân tích, tạo nội dung có cấu trúc, sử dụng công cụ; dự kiến phối hợp n8n trong hệ thống 24/7.

## REPORTED với chứng cứ

- Hermes [tự đánh giá](../reports/2026-11-21-hermes-self-assessment.md): WebUI session dùng model `gpt-5.4` (provider OpenAI) **trong phiên kiểm tra**, 55 skills liệt kê, tool files/terminal/web/browser, memory/session_search, cronjob_manage (0 job), GitHub SSH/push.
- [Audit VPS](../reports/2026-11-21-n8n-hermes-integration-audit.md): dashboard Hostinger Hermes `0.22.5`, container healthy, web control/dashboard API auth hoạt động; n8n đã reach được dashboard.
- Hai báo cáo xem xét môi trường khác nhau (WebUI shell vs VPS container); không được mặc định chúng dùng chung network/filesystem/CLI.

## Có thể giao phù hợp

- Phân tích yêu cầu/dữ liệu, lên kế hoạch, viết brief/scripts, phân loại, QA sơ bộ và tổng hợp báo cáo.
- Sử dụng skills/tools có sẵn trong phiên; đọc đặc tả qua GitHub, tạo báo cáo và push nếu GitHub auth vẫn hoạt động.
- Khảo sát connector/media/Ads/SEO và lập đề xuất trước khi gọi API có chi phí/ghi production.

## BLOCKED / NOT YET PROVEN

- Hermes **chưa expose live agent inference API** từ Hostinger dashboard image trong audit; API upstream theo docs ≠ API của instance hiện hữu.
- n8n instance-level MCP đang disabled; chưa có workflow, chưa có luồng Hermes ↔ n8n E2E thành công.
- Chưa chứng minh khả năng chạy cron 24/7, self-healing, cost controls và marketing connectors production-ready.
- Memory/session recall ở phiên WebUI đã được thử; lưu trữ memory vật lý trên VPS chưa xác minh.

## Phối hợp/bàn giao

- Nhận task theo URL GitHub hoặc n8n callback khi tích hợp đã PASS; gửi output có schema/task_id, evidence và trạng thái.
- Việc chạy lịch/retry/idempotency nên giao n8n; việc xây connector/debug cho Codex; publish/chi phí/Ads write cần chính sách phê duyệt.
- Không coi việc có tool trong catalog là bằng chứng đã có credentials/khả năng API.

**Khảo sát còn thiếu:** [Agent capability survey](../tasks/2026-11-21-agent-capability-survey.md), mục Hermes.
