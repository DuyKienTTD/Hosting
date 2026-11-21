---
id: component-n8n
type: knowledge
status: current
updated_at: 2026-11-21
sensitivity: public-redacted
---

# n8n — workflow engine / execution plane

**Loại:** Thành phần điều phối, không phải tác nhân AI riêng biệt. Trách nhiệm: trigger, webhook, connector, schedule, workflow state, retry, lỗi, xác thực API và theo dõi tác vụ.

## VERIFIED theo [audit](../reports/2026-11-21-n8n-hermes-integration-audit.md)

- n8n `2.45.7`, health/readiness 200, Docker container healthy, 0 restart/OOM tại điểm đo.
- Production: **0 workflow**, instance-level MCP tắt; health/readiness 200 và restart count 0.
- P0 Level 1: instance sandbox độc lập có đúng một authenticated webhook; private service DNS, schema/callback/retry/idempotency structural E2E 9/9 PASS. Không gọi AI provider.
- Có 1 credential nhưng loại/quyền chưa kiểm tra; không kết luận các platform đã connected.

## PLANNED

- Phối hợp Hermes qua private inference API và MCP/webhooks sau khi được phê duyệt, test sandbox và có policy.
- Ghi execution logs, task ID, idempotency, quota và phê duyệt có kiểm soát trước publish/Ads.
- Chạy các pipeline media, ads reporting, SEO và social dựa trên connector thực tế.

**Không** dùng chính n8n làm kho lưu trữ video, engine render nặng hoặc AI reasoning tự do.

## Bàn giao

n8n không tự đọc quy tắc GitHub trừ khi workflow được lập trình để làm vậy. Codex/Hermes chịu trách nhiệm triển khai workflow tuân thủ quy ước; n8n ghi trạng thái runtime vào DB và xuất kết quả tổng hợp sang GitHub khi phù hợp.
