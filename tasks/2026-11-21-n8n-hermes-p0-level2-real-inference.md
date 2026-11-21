---
id: ttd-ai-p0-level2-001
type: task
status: approved_to_execute
updated_at: 2026-11-21
approved_at: 2026-11-21
approval_level: 2
sensitivity: public
owner: codex
support: [hermes, hostinger-agent]
depends_on: [ttd-ai-p0-integration-001]
---

# TTD-AI-P0-LEVEL2-001 — Kiểm thử GPT-6 Luna và nghiệm thu Hermes E2E

## Ủy quyền của chủ dự án

Chủ dự án đã phê duyệt **Mức 2** ngày 2026-11-21, **chỉ** cho:
- Provider/model: **OpenAI `gpt-6-luna`**, phải xác minh model ID, khả dụng trong tài khoản và giá API hiện hành trước khi gọi.
- **Tối đa 5 lượt gọi tính phí** cho toàn bộ P0, tính cả retry, callback gây gọi thêm và phép thử lỗi nếu phát sinh phí.
- **Không quá 4.000 input tokens và 2.000 output tokens/lượt**; cấu hình hard `max_output_tokens`, tính cả reasoning tokens nếu provider tính trong output; phải kiểm soát prompt/context trước khi gửi.
- **Trần tổng 0,05 USD cho toàn P0** và **trần 0,05 USD mỗi ngày**. Theo kế hoạch bổ sung ở báo cáo Mức 1: tối đa 0,01 USD cho mỗi job, nhưng không dùng giới hạn job để nới tổng cap.
- **Chỉ dùng fake data**, không dữ liệu khách hàng, tài khoản Ads/GA4/WordPress thật hay thông tin bí mật.
- **Không thay đổi production**: không restart/recreate n8n hoặc Hermes chính, không đụng U4S `ttdnew.tech`, DNS, public port, firewall, SSL, account business; không publish, gửi email, sửa website/quảng cáo.
- Được cập nhật **runtime phụ sandbox** và cấu hình egress outbound tối thiểu chỉ tới provider đã duyệt nếu chứng minh được cô lập, auth, rollback và không làm lộ API key. Không mở inbound Internet hoặc thay đổi chính sách mạng toàn VPS.

Mọi phần ngoài giới hạn trên phải xin phê duyệt mới. Đây là giới hạn chi phí **mục tiêu bắt buộc**. Nếu hệ thống/provider không hỗ trợ chặn cứng thực tế hoặc không thể chứng minh cơ chế dừng trước request, **STOP**, ghi `BLOCKED_COST_CONTROL`; không diễn giải phê duyệt là chấp nhận rủi ro vượt cap.

## Đọc nguồn

- [Quyết định ADR-P0-001](../decisions/2026-11-21-p0-reasoning-integration-proposal.md).
- [Báo cáo Mức 1](../reports/2026-11-21-n8n-hermes-p0-sandbox-integration.md), [evidence](../reports/evidence/2026-11-21-ttd-ai-p0-integration-001.json), [mã sandbox](../sandbox/p0-level1/README.md).
- [Review phân biệt Provider/Hermes E2E](../reports/2026-11-21-p0-level1-review-and-level2-criteria.md).
- [Danh bạ và quy tắc chung](../agents/README.md), [quy tắc bàn giao](../rules/AGENT_WORKFLOW.md), [bảo mật repo](../rules/REPOSITORY_SECURITY.md).

## GATE 0 — Bắt buộc trước mọi paid call

1. Xác minh **model ID `gpt-6-luna` đúng và khả dụng** qua official documentation + tài khoản API hiện tại, billing enabled/authorized, region/support, đơn giá input/output và phí công cụ nếu có. Không tự đổi sang model khác nếu fail.
2. Kiểm tra **estimated maximum billable units** trước request, bao gồm context, system/developer prompts, cached vs uncached, reasoning/billable output, retries, tool cost, overhead và any minimum-charge. Nếu không có cách đặt/ước lượng **upper bound đáng tin** để không thể vượt trần 0,05 USD, **không gọi**.
3. Dùng cơ chế **admission control/kill switch atomic** với bộ đếm persistent riêng P0: count mọi attempt/call có thể tính phí, dự toán worst-case before send, reject concurrent calls vượt cap; không reset bộ đếm khi restart/retry; kiểm tra actual usage sau response và đối soát provider billing nếu available. Cấm tự động retry không giới hạn. Nếu provider không có hard billing cap tuyệt đối, nêu residual risk, **dừng trước call** nếu không kiểm soát được theo điều kiện người dùng.
4. API key có thể được cấu hình **chỉ trong sandbox** theo phương pháp secret root-only/secret mount an toàn; không in, commit, log, chuyển qua chat, export public. Không đụng `N8N_ENCRYPTION_KEY` production.
5. Preflight health/backup/rollback, hạn chế outbound provider, verify no inbound exposure/no production side effects. Nếu thay đổi đòi restart production, sửa firewall/public exposure hay vượt least privilege, **STOP**.
6. Đánh dấu `PREFLIGHT_PASS` bằng bằng chứng đã khử nhạy cảm rồi mới chạy trả phí.

## Mốc A — Provider E2E (riêng biệt)

Kiểm thử `n8n sandbox → private adapter → OpenAI GPT-6 Luna → authenticated callback → n8n` trên fake data. Kiểm tra:
- model thực nhận đúng model ID, structured output JSON Schema, task/correlation ID.
- auth, timeout, retry bounded/idempotency; mọi retry tính trong 5 calls, tránh lặp paid charge.
- input/output billable tokens, call count, projected và actual spend.
- end-to-end log/result hash, health và rollback.

Kết luận **`PROVIDER_E2E_PASS`** chỉ khi có **live provider inference evidence**; nếu adapter gọi trực tiếp OpenAI thì tuyệt đối **không** coi đây là Hermes Agent.

## Mốc B — Hermes Agent E2E (riêng biệt)

Điều tra **đường gọi inference của Hermes Agent thật** (không phải deterministic mock hoặc provider adapter):
- Kiểm tra tính khả thi với Hermes runtime trên KVM2 hoặc một Hermes runtime phụ **cô lập** được xác minh là Hermes, không sửa Hermes chính; so sánh với U4S riêng biệt.
- Nếu đủ an toàn và **không cần thêm paid calls ngoài trần**, kiểm thử `n8n → real Hermes Agent runtime → n8n callback`, lưu evidence nhận dạng runtime/process/agent execution và kết quả reasoning thực.
- Nếu cần thay image/container Hermes chính, mở public API, mua thêm dịch vụ, hoặc vượt 5 calls / 0,05 USD: **BLOCKED / APPROVAL_REQUIRED**. Có thể bàn giao feasibility/proposal nhưng **không** tự mở rộng quyền.
- Nghiệm thu `HERMES_E2E_PASS` chỉ khi chứng minh request **thực sự đi qua Hermes Agent**; `PROVIDER_E2E_PASS` không thay thế.

## Stop conditions

Dừng ngay khi: model/giá/credential không xác minh được; không kiểm soát upper bound chi phí; tới 5 lượt hoặc chạm bất kỳ ngưỡng tiền/token nào; auth/egress có vấn đề; nghi ngờ secret leak; có side effect production; health giảm; output/schema hoặc quyền truy cập vượt phạm vi. Không tìm cách tự vượt chặn hoặc tạo tài khoản chi phí mới.

## Bàn giao và báo cáo

Tạo báo cáo **riêng cho Mức 2** `reports/2026-11-21-n8n-hermes-p0-level2-results.md` (hoặc ngày thực hiện thực tế), evidence JSON redacted trong `reports/evidence/`, có:
- Bảng `PROVIDER_E2E` và `HERMES_E2E` trạng thái độc lập PASS/PARTIAL/BLOCKED, không tạo PASS giả.
- Tên model/provider/tier, actual calls, token usage input/output/reasoning, estimated vs billed cost, cap enforcement, xác thực billing và rủi ro residual.
- Topology/route của từng request, có hay không Hermes Agent, schema/callback/rollback/health tests.
- Thay đổi đã làm, không làm, blockers, GitHub commit.
- Cập nhật `STATE.md`, `CATALOG.yaml`, `CHANGELOG.md`, báo cáo và code (không secret). Nếu không thể push thì `NOT_PUSHED`.

Không tự kết luận P0 toàn bộ complete nếu Hermes Agent E2E vẫn chưa PASS.
