---
id: ttd-hermes-gate-a-001
type: task
status: approved_to_execute
updated_at: 2026-11-21
approved_at: 2026-11-21
approval_scope: gate-a-mock-only
sensitivity: public
owner: codex
support: [hermes, hostinger-agent]
depends_on: [ttd-hermes-e2e-hard-cap-001]
paid_inference_approval: false
---

# TTD-HERMES-GATE-A-001 — Triển khai Hermes auxiliary, inference guard và bridge (mock only)

## Phê duyệt của chủ dự án — 2026-11-21

Chủ dự án **đã phê duyệt Bước A theo [ADR-P0-002](../decisions/2026-11-21-hermes-auxiliary-guard-bridge-approval-proposal.md)**: Codex được triển khai **Hermes phụ nguyên bản, private inference guard, authenticated bridge/callback và đúng hai service secrets** trên sandbox KVM2 để kiểm thử **provider mock**. Giữ **kill switch ON** và **0 paid calls**. Không thay đổi production. **Bước B chưa được phê duyệt**.

Phạm vi cho phép:
- Hermes auxiliary runtime có image/tag/digest pinned và state riêng, tuyệt đối không mount lại volumes, secrets, identity, workspace/memory hoặc credentials production.
- Inference guard là đường duy nhất Hermes có thể gửi yêu cầu mô phỏng đến provider; không có direct egress hay bypass; guard enforce trước dispatch `model=gpt-6-luna`, `max_output_tokens=600`, input ≤4,000 billable tokens, không tools, không fallback/auxiliary calls, 1 turn.
- Authenticated bridge `n8n sandbox -> real Hermes auxiliary -> guard -> provider mock -> authenticated n8n callback`, có schema/idempotency/correlation ID.
- Tạo **hai bí mật mới**: `API_SERVER_KEY` và guard service token bằng CSPRNG; files `600`, thư mục `700`. Không in secret ra chat/Git/log, không sửa secret/encryption production. Provider credential không được cấp cho Hermes auxiliary; **provider mock không cần key trả phí**.
- Tiếp tục dùng **đúng P0 persistent atomic ledger** đã ghi 1 paid attempt. Chỉ dùng ledger copy để stress/rehearsal nếu cần biến đổi; ledger thật không reset, kill switch thật luôn ON.
- Preflight health/CPU/RAM, image provenance, backup, rollback, recovery/access checks. Không restart/recreate n8n/Hermes production; không đổi DNS, firewall, public port, U4S `ttdnew.tech`, Google Ads, website, credentials hiện hữu hoặc business services. Không tạo phí hosting/service mới.
- Chỉ private mock capture: capture **full serialized Hermes request** qua guard, xác minh bằng tokenizer thực tế/upper bound chặt cho ≤4K input, ≤600 output, exact model, no-tools, 1 request/no fallback, no direct provider egress, auth, callback, negative auth/schema/model/path/oversize, timeout/retry/idempotency/concurrency; rollback/restore và production health.

## STOP / hard gate

Dừng ngay nếu: không chứng minh được giới hạn token trước request hoặc yêu cầu vượt bound, có đường egress bypass, extra provider call, kill switch bị tắt/chuyển, rủi ro lộ secrets, không đủ CPU/RAM, ảnh hưởng production, cần public inbound/network mutation, mất quyền, phát sinh phí mới hoặc không có rollback đáng tin. Không tự vượt qua blocker.

## Cấm tuyệt đối trong Bước A

- **Không gọi OpenAI API trả phí**, dù approval Mức 2 cũ vẫn còn hạn mức chưa dùng.
- **Không tắt, reset, temporarily unlock kill switch**; không mở đường provider paid.
- Không mở quyền truy cập từ Internet tới sandbox, không thay Hostinger production.
- Không xem mock PASS là `HERMES_E2E_PAID_PASS`, cũng không đánh dấu toàn P0 complete.
- Không tự tiến hành Bước B sau khi mock PASS; phải trình riêng một đề xuất phê duyệt **đúng một paid Hermes call**, dùng chung ledger và ngân sách P0.

## Acceptance Bước A

1. Hermes Agent auxiliary được xác định bằng process/runtime evidence, guard/bridge hoạt động trên private network và authentication PASS.
2. Full request capture qua mock PASS: exact model/output cap/input ≤4K, tools disabled, one-turn/one-request, direct egress blocked, không bypass policy/ledger; kill switch vẫn ON.
3. Mock E2E n8n → Hermes thật → provider mock → n8n callback PASS, kèm negative/fault/retry/idempotency tests.
4. Backup và rollback/restore PASS; production pre/post health PASS, restarts/downtime 0.
5. Paid calls mới 0; chi phí API mới 0; secrets không vào repo/chat/log.

## Bàn giao

Codex tạo báo cáo `reports/2026-11-21-hermes-gate-a-mock-results.md` (hoặc ngày thực hiện), evidence JSON trong `reports/evidence/`, cập nhật task, STATE, CATALOG và CHANGELOG. Nêu rõ: đã triển khai/không triển khai, kết quả test, ảnh hưởng môi trường, chính sách token, trạng thái ledger/kill switch, rollback và có đủ điều kiện **đề xuất GATE B** hay chưa. Chỉ report redacted lên GitHub public, commit/push và cung cấp URL kết quả.
