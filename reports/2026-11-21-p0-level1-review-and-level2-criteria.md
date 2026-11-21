---
id: p0-level1-review-and-level2-criteria-2026-11-21
type: report
status: current
updated_at: 2026-11-21
sensitivity: public
reviewer: chatgpt
related_task: ttd-ai-p0-integration-001
---

# Review P0 Level 1 và tiêu chí phê duyệt Mức 2

## Kết quả xác minh qua GitHub

Đã đối chiếu [báo cáo P0](2026-11-21-n8n-hermes-p0-sandbox-integration.md), [evidence JSON](evidence/2026-11-21-ttd-ai-p0-integration-001.json), [mã sandbox](../sandbox/p0-level1/README.md) và commit `21fdae66620e39b49ddb44cadd82392745704f69`.

**LEVEL1_PASS:** 9/9 test structural E2E dùng mock (auth, JSON schema, callback, retry, idempotency, timeout), rollback/restore PASS. Theo evidence: 0 production restart, 0 downtime, 0 paid inference. Chưa tự đo lại VPS từ phiên ChatGPT này; kết quả là xác minh báo cáo/evidence, không phải independent runtime audit.

**P0 tổng thể chưa PASS:** `ttd-p0-reasoner` là deterministic mock adapter, không phải Hermes inference runtime.

## Provider/model/pricing

Tài liệu chính thức OpenAI `https://developers.openai.com/api/docs/models/gpt-6-luna` và changelog API liệt kê model ID `gpt-6-luna`; giá Standard đối với 4K input + 2K output: USD 0.10/1M input và USD 0.50/1M output. Một call giới hạn như trên khoảng USD 0.0014, 5 call USD 0.007, không bao gồm công cụ tính phí khác, phụ phí tier/region hay phát sinh ngoài giả định.

Đề xuất 5 calls, max 4K input + 2K output/call, max USD 0.01/job và USD 0.05/ngày & USD 0.05 toàn P0 là quy mô nhỏ. **Cost cap ứng dụng không mặc nhiên là hard billing cap provider.** Cần đếm token cả hidden/reasoning nếu billable, hạn chế retry và concurrency, kiểm tra actual usage/cost và thiết lập kill-switch trước khi gọi.

## Phân biệt hai mục tiêu nghiệm thu

1. `PROVIDER_E2E_PASS`: `n8n sandbox -> private adapter -> OpenAI GPT-6 Luna -> authenticated callback -> n8n`, output schema/usage/billing validated. Điều này chỉ xác minh provider integration.
2. `HERMES_E2E_PASS`: `n8n -> real Hermes Agent inference/runtime -> n8n callback`, có bằng chứng request đi qua **Hermes Agent** thực sự. Nếu adapter chỉ gọi OpenAI trực tiếp, **không** được gọi đó là Hermes E2E hoặc hoàn tất nhiệm vụ tích hợp n8n↔Hermes.

## Gate Mức 2 — CHƯA ĐƯỢC PHÊ DUYỆT

- Chủ dự án chưa phê duyệt model/provider/cost cap cho paid calls.
- Nếu triển khai provider pilot, ghi nhãn `provider-only`, không dùng như chứng cứ thay thế Hermes runtime.
- Giữ sandbox cô lập, network egress tối thiểu theo policy; xác minh nếu network `internal=true` cần egress qua một proxy/connector network riêng mà không mở sandbox public hoặc mất segmentation. Không làm yếu mạng mặc định.
- API key/credentials không in trong log/Git/chat; chỉ fake data; không Ads, WP, social, media writes.
- Chứng minh admission control trước call, usage accounting và dừng sau 5 calls hoặc tới USD 0.05; nếu không thể thiết lập hard cap thực sự ở provider thì ghi residual spend risk và yêu cầu owner chấp thuận.
- Mọi thay đổi production, Hermes chính, public ports/firewall, container downtime cần approval riêng.
- Trong báo cáo Mức 2, ghi provider URL, model ID, service tier, token usage, ước tính vs billed cost, call count, tiêu chí E2E tương ứng, và evidence đã khử bí mật.

**Bước tiếp theo đề xuất:** Codex đánh giá đường đi đến Hermes inference runtime độc lập với OpenAI provider client, và chuẩn bị kế hoạch provider-only pilot rõ scope. Chỉ thực hiện paid inference khi có phê duyệt Mức 2 riêng.
