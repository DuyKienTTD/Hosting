---
id: ttd-hermes-gate-b-single-paid-call-proposal-2026-11-21
type: decision
status: approved_with_restrictions
approved_at: 2026-11-21
approval_scope: exactly_one_hermes_paid_attempt
updated_at: 2026-11-21
sensitivity: public
decision_owner: business-owner
related_task: ttd-hermes-gate-a-001
paid_call_approval: true
---

# ADR-P0-003 — Đề xuất GATE B: đúng một Hermes Agent paid inference

**APPROVED WITH RESTRICTIONS — 2026-11-21.** Chủ dự án phê duyệt tối đa đúng **một** physical paid Hermes Agent call qua `gpt-6-luna`, ≤4.000 input tokens, `max_output_tokens=600`, dữ liệu giả, không tools, không paid retry, không thay production; dùng atomic **one-shot permit** tự tiêu thụ/khóa lại trước dispatch, không tắt global kill switch. Nếu không bảo đảm bất kỳ giới hạn nào phải **STOP, không gọi API**. [Task Codex thực thi](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md).

## Bằng chứng đã đối chiếu

- [GATE A report](../reports/2026-11-21-hermes-gate-a-mock-results.md) và [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-a-001.json), commit `ab319ee0ca5b234dbbe6b34e919173145ff95a2f`: GATE_A_MOCK_PASS, 4 auxiliary services healthy, no public ports; exact model, 600 output cap, canonical ASCII request <=3315 bytes, tools absent, direct egress blocked, callback PASS, rollback/restore PASS.
- GATE A có **0 paid calls** và giữ kill switch ON. P0 ledger giữ 1 paid attempt, USD 0.0035 reserved và USD 0.0000496 usage-based actual, **chưa đối soát hóa đơn**; không reset ledger.
- Provider E2E bằng adapter đã PASS 1 paid call, nhưng Hermes Agent paid E2E **chưa thực hiện**.
- Một lỗi sandbox rollback ownership được sửa và retest PASS; GATE A chưa có restart policy tự phục hồi sau VPS reboot.

## Phạm vi ủy quyền đã được duyệt

Codex được kiểm thử **đúng một** provider request có trả phí qua route:

`n8n sandbox → authenticated bridge → Hermes auxiliary verified → pre-dispatch inference guard → OpenAI Responses API gpt-6-luna → authenticated callback n8n`.

Chỉ **một** fake-data task, tối đa **một physical paid attempt**. Dừng và báo BLOCKED nếu attempt fail, timeout, response mất hoặc lỗi; **không tự retry paid**. Có thể replay cached/idempotent result miễn phí, không dispatch lần hai.

### Safety và cost gates bắt buộc

1. Preflight live: production health, no restarts, backup/rollback, model availability & current standard pricing, API access, available budget, valid secret mount; không thay đổi production, public port, DNS, firewall, U4S hoặc tài khoản kinh doanh.
2. Giữ nguyên **shared persistent atomic P0 ledger**, hiện 1 attempt / USD 0.0035 reserved. Không tạo/reset ledger, không dùng ledger test cho paid. Giữ cap cũ toàn P0: **≤5 attempts, ≤USD 0.05/ngày, ≤USD 0.05 tổng**, đồng thời **≤USD 0.01/job** và thêm hard constraint **chính xác tối đa 1 Hermes paid attempt** cho GATE B.
3. Mỗi request: **≤4.000 billable input tokens**, **max_output_tokens=600** (bao gồm reasoning output nếu provider tính), exact model `gpt-6-luna`, no tools/web/MCP/media, one turn, no fallback/auxiliary calls. Guard verify request before dispatch, reject vượt cap. Admission phải reserve worst-case upper bound trước khi gửi, bảo đảm giá đã kiểm tra và upper bound không vượt 0.05 tổng; if not provable, STOP.
4. Giữ Hermes auxiliary và bridge **không có provider credential hay direct Internet egress**; guard là đường duy nhất đến `api.openai.com:443` qua allowlist proxy. Kiểm tra network policy và deny-bypass trước khi chuyển từ mock sang paid; không expose inbound/public.
5. Kill switch ON mặc định. Chỉ nếu được duyệt: dùng thao tác **atomic, scoped one-shot permit** tại guard cho chính task/idempotency-key đã duyệt; giảm thiểu phạm vi mở. Nếu không thể one-shot permit mà phải tắt global switch, **STOP để xin phê duyệt thiết kế lại**. Tự động relock/consume permit **trước dispatch**, kể cả lỗi/timeout; không lưu cấu hình unlock.
6. Sau attempt: ghi provider response-ID hash, model request/served ID, input/output/reasoning usage, usage-based estimate, invoice status, callback/schema/idempotency, ledger, kill switch ON, health; không lộ raw secret/data trong Git.
7. Mọi preflight fail, token/price/cost/egress/auth mismatch, extra request, secret exposure, data leak, crash hoặc production impact → STOP và rollback sandbox.

## Acceptance

- `HERMES_E2E_PAID_PASS` chỉ khi evidence xác nhận request **thực sự đi qua Hermes Agent**, guard và provider, một physical attempt, authenticated n8n callback và output JSON đúng schema.
- Paid attempts delta = 1, usage/cost trong giới hạn và ledger không reset; kill switch cuối ON, no bypass, no production changes.
- Báo cáo tách rõ usage-estimated cost và actual provider invoice nếu chưa đối soát. Không kết luận đã hoàn tất hoạt động 24/7/production readiness từ một paid test.

## Trạng thái

**GATE B APPROVED / NOT EXECUTED BY THIS RECORD.** GATE A đã PASS; chủ dự án đã cho phép Codex thực hiện đúng một lượt trong các gate được quy định. Việc cập nhật GitHub không tự kích hoạt Hermes paid inference.

Preflight thực thi ghi `BLOCKED_PREFLIGHT / 0 paid attempt`: [báo cáo](../reports/2026-11-21-hermes-gate-b-paid-results.md). Atomic one-shot permit và reservation chưa được chứng minh trên runtime hiện có; chưa có GATE B paid E2E PASS.

Kiểm tra lại sau remediation vẫn **BLOCKED_PREFLIGHT**, với 0 paid attempts mới. One-shot, fingerprint toàn bộ body và hạch toán đã chạy trên mock. Live bridge truy cập được proxy Level 2, guard chưa có paid route riêng, quyền provider của guard và số token theo provider của body cuối chưa được chứng minh. [Báo cáo mới nhất](../reports/2026-11-21-hermes-gate-b-preflight-recheck.md).

## Bàn giao Codex sau thực thi

Codex tạo `reports/2026-11-21-hermes-gate-b-paid-results.md` và evidence JSON redacted, cập nhật ADR/task/STATE/CATALOG/CHANGELOG, ghi rõ STOP/PASS và commit.
