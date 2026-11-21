---
id: ttd-hermes-gate-b-001
type: task
status: blocked
approved_at: 2026-11-21
updated_at: 2026-11-21
approval_scope: exactly_one_hermes_paid_attempt
paid_inference_approval: true
sensitivity: public
owner: codex
support: [hermes, hostinger-agent]
depends_on: [ttd-hermes-gate-a-001]
---

# TTD-HERMES-GATE-B-001 — Một lượt GPT-6 Luna qua Hermes Agent thật

## Phê duyệt chủ dự án — 2026-11-21

Chủ dự án đã **phê duyệt GATE B theo [ADR-P0-003](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md)**. Codex được phép thực hiện **tối đa đúng một physical paid inference attempt** qua Hermes Agent thật, trên sandbox KVM2 đã được kiểm thử GATE A, chỉ với dữ liệu giả. Đây là giới hạn tối đa, **không buộc phải thực hiện call nếu safety/cost gate không PASS**.

Route bắt buộc: `n8n sandbox → authenticated bridge → Hermes auxiliary đã xác minh → private pre-dispatch guard → OpenAI Responses API → authenticated n8n callback`.

## Giới hạn bắt buộc

- Provider/model **chỉ OpenAI `gpt-6-luna`**; xác minh exact model, giá, quyền API live trước dispatch.
- **≤4.000 input tokens**, `max_output_tokens=600` (bao gồm output/reasoning tokens do provider tính), không tools/web/search/media/MCP/subagent, một turn, không fallback.
- **Một task ID/idempotency key được phê duyệt; tối đa một physical paid attempt GATE B.** Không retry có tính phí, dù timeout/error/response lost. Cached replay cùng request chỉ đọc, không dispatch thêm. Không gọi lại provider adapter để test.
- Dùng **chung persistent atomic P0 ledger**: baseline 1 previous paid attempt, USD 0.0035 reserved, USD 0.0000496 usage-based actual (chưa đối soát hóa đơn). Không reset, nới, hoặc thay ledger. Ngưỡng tổng P0 **≤5 attempts, ≤USD 0.05/ngày, ≤USD 0.05 toàn P0**, ≤USD 0.01/job; upper-bound reservation bảo thủ trước request. Nếu bất kỳ ngưỡng, mức giá, hoặc phép hạch toán không chắc chắn, STOP.
- Kill switch **ON toàn cục**. Chỉ chấp nhận **atomic scoped one-shot permit** ở guard cho task/idempotency key được duyệt. Permit phải được validate và **consume/relock bền vững trước provider dispatch**, kể cả lỗi hoặc timeout; không được mở toàn cục, không mở cửa sổ cho request thứ hai. Nếu chỉ có cách tắt global kill switch, STOP để xin quyết định mới.
- **Không sửa production** n8n/Hermes, website, Ads, business services, firewall, DNS, public port, SSL hoặc U4S `ttdnew.tech`. Không restart/recreate các service chính hoặc tạo downtime. Không tạo account/service tính phí mới.
- Hermes auxiliary và bridge **không giữ provider key** và không có direct provider Internet egress; chỉ guard có kết nối outbound tối thiểu qua allowlist proxy. Secrets không xuất hiện trên GitHub public, chat, logs hoặc báo cáo.

## Preflight — bắt buộc trước paid attempt

1. Đọc [GATE A report](../reports/2026-11-21-hermes-gate-a-mock-results.md), [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-a-001.json) và [ADR-P0-003](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md); xác minh runtime image pin/version, private auth, full serialized input ≤4K và provider request cap 600/no-tools đã kiểm chứng.
2. Backup/config/rollback và production prehealth; CPU/RAM/network safety, no-bypass, callback reachability/authorization.
3. Chứng minh **atomic one-shot permit bằng test offline/mock**, cùng shared ledger, chống simultaneous requests, loss/restart và retries. Có chứng cứ permit consumed trước actual dispatch. Kiểm tra route không có cách gọi trực tiếp OpenAI từ Hermes.
4. Xác minh giá Standard chính thức đang áp dụng, model accessible, khả năng reserve upper bound và reconcile API usage. Nếu không có cách bảo đảm không vượt cap theo phép tính bảo thủ, STOP.
5. Chỉ khi tất cả gates PASS mới cho đúng một request fake-data đi qua guard; không test thêm paid dù cần debug.

## Acceptance

- **`HERMES_E2E_PAID_PASS`** chỉ khi evidence chỉ rõ chạy qua real Hermes auxiliary (không phải provider adapter), guard, GPT-6 Luna và authenticated n8n callback; JSON Schema PASS; model served/requested khớp.
- Ledger tăng **tối đa +1** paid attempt; số token/cost đúng giới hạn. Trường hợp attempt thất bại, ghi FAILED/BLOCKED, **không retry paid** và không ghi PASS giả.
- Global kill switch luôn ON; scoped permit consumed vĩnh viễn trước dispatch; verify post-state, no-bypass và production health PASS.
- Không suy luận một paid E2E thành production-ready/24x7. Báo cáo chi phí dựa trên usage riêng và invoice/billing verified riêng, không đồng nhất.
- Backup/rollback sau khi cần thiết nhưng **không khôi phục/xóa ledger để làm mất dấu paid attempt**.

## STOP conditions

Bất kỳ vấn đề về hard-cap, budget admission, one-shot permit, model, key, public exposure, provider routing, auth, bypass, production health, secret, uncertainty in upper bound hay tính toán chi phí → STOP. Nếu gọi đã dispatch thì không thực hiện paid attempt mới; lock/reconcile/report.

## Bàn giao

Codex lưu `reports/2026-11-21-hermes-gate-b-paid-results.md` và JSON evidence đã khử bí mật (hoặc ngày thực tế), nêu preflight, exactly one attempt or zero if blocked, model, input/output/reasoning token, reserved/actual cost, invoice status, task/run IDs dưới dạng hash, correlation and callback, one-shot state, ledger, health/rollback. Push vào repo, cập nhật task, ADR, STATE.md, CATALOG.yaml, CHANGELOG.md; không đưa API keys/secret/private endpoints vào repo.

## Kết quả preflight 2026-11-21

`BLOCKED_PREFLIGHT`: guard GATE A chưa có atomic scoped one-shot permit/consume/relock và worst-case reservation. Không thực hiện paid request; xem [báo cáo](../reports/2026-11-21-hermes-gate-b-paid-results.md). Approval vẫn giới hạn tối đa một attempt sau khi toàn bộ gate được chứng minh.

## Kiểm tra lại sau remediation

**BLOCKED_PREFLIGHT.** Fingerprint của toàn bộ byte gửi đi và hạch toán sau response, timeout hoặc stream bị cắt đã PASS với guard và provider mock trên Linux. Live bridge chạm được proxy Level 2 cũ, guard chưa có paid route riêng và chưa xác minh quyền Responses của credential dành cho guard hoặc số input tokens của request cuối theo provider. Ledger thật giữ 1 attempt, 0 permit và kill switch ON trước/sau. Paid dispatch mới 0. [Báo cáo tổng hợp](../reports/2026-11-21-hermes-gate-b-preflight-recheck.md) · [Evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-preflight-recheck.json).

## Kiểm tra sau cô lập proxy

Proxy trên KVM2 đã rời mạng dùng chung. Guard vào được proxy và sáu container còn lại bị chặn trong phép thử. Mock callback, hạch toán mock riêng và rollback egress đã kiểm chứng. Task vẫn **BLOCKED_PREFLIGHT** vì thiếu credential dành cho guard đã xác minh, số tokens theo provider và một lượt mock kết hợp callback với one-shot accounting. Có một lần lỗi metadata Hermes trước callback. Paid attempts mới 0. [Báo cáo hiện tại](../reports/2026-11-21-hermes-gate-b-egress-isolation.md).
