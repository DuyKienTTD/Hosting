---
id: ttd-hermes-gate-b-guard-hardening-001
type: task
status: ready_for_code_and_mock
updated_at: 2026-11-21
sensitivity: public
owner: codex
support: [hermes, hostinger-agent]
depends_on: [ttd-hermes-gate-b-001]
new_paid_call_approval: false
live_implementation_approval: pending
---

# TTD-HERMES-GATE-B-GUARD-HARDENING-001 — Hoàn thiện one-shot permit và shared-ledger reservation

## Vì sao task này tồn tại

[GATE B preflight](../reports/2026-11-21-hermes-gate-b-paid-results.md) dừng `BLOCKED_PREFLIGHT` vì GATE A guard chỉ mount shared P0 ledger read-only, chưa có atomic scoped one-shot permit, consume/relock trước dispatch, worst-case budget reservation hoặc paid upstream. [Evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-001.json) ghi 0 Hermes paid attempts mới, USD 0 chi phí mới. Kiểm tra live ledger, kill switch và production **chưa được thực hiện trong phiên preflight đó**.

Chủ dự án đã phê duyệt GATE B có điều kiện trong [ADR-P0-003](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md), nhưng yêu cầu tất cả preflight gates PASS trước paid dispatch. Phê duyệt paid attempt **không phải** quyền vượt qua bất kỳ gate nào.

## Phạm vi được giao ngay — code, offline/mock và kiểm tra read-only

Codex được:
1. Phân tích code guard/bridge/ledger và quyền file/socket/shared lock thực tế qua nguồn đã được cấp quyền; không tiết lộ secret.
2. Thiết kế + phát triển mã **atomic one-shot permit** gắn với task ID/idempotency key, exact model và request fingerprint. Permit dùng 1 lần, không mở global kill switch; reject nonmatching task, TTL-expired, reused, concurrent, failed validation.
3. Thiết kế + phát triển **shared P0 ledger reservation** trên cùng nguồn trạng thái đang dùng, không tạo budget song song; chống race giữa adapter/guard/process bằng cùng lock, durable write + fsync, fail-closed. Không reset ledger, không xóa lịch sử 1 attempt đã có. Không hoàn lại reservation của request đã có khả năng được dispatch khi timeout/unknown outcome.
4. Chứng minh **thứ tự transaction**: verify policy + auth -> acquire shared lock -> check cap/call-count and permit -> durable reserve + consume permit as one committed state -> release/retain lock as necessary -> exactly one physical upstream dispatch. Crash/restart ở mọi mốc phải fail-closed, không lặp paid dispatch. Xác định cơ chế chống duplicate across process restarts.
5. Kiểm thử **chỉ bằng provider mock và ledger COPY**, gồm concurrency >=10, idempotency, crash/restart trước/sau commit, failure of disk writes, timeout, duplicate, malformed schema, unauthorized task, incorrect model, oversized input, tools, prices/caps mismatch, provider 5xx; chứng minh max physical dispatch 1. Không dùng ledger thật cho destructive test.
6. Xác minh guard vẫn ép `gpt-6-luna`, input <=4K, `max_output_tokens=600`, no-tools, 1 turn, no fallback/no retry paid, no direct egress, authenticated callback; bảo vệ provider key chỉ trong guard.
7. Lập phương án deploy sandbox có backup, resource envelope, secure mount/ownership cho shared ledger, no-production-change và rollback không xóa paid-call history.

## Không được tự thực hiện trong task này

- Không gọi paid AI API, không tắt/unlock global kill switch, không tạo paid permit live.
- Không thay container/runtime/compose/network/egress/secret **đang chạy** chỉ dựa trên task này. Chỉ tạo PR/commit code secret-free và test offline. Triển khai sandbox live sau preflight engineering phải được chủ dự án chấp thuận cụ thể nếu tạo thay đổi runtime hoặc credential.
- Không restart/recreate/thay n8n hoặc Hermes production, public port/firewall/DNS, U4S, business services.
- Không coi mock test PASS là `HERMES_E2E_PAID_PASS`; không khởi động lại GATE B paid attempt tự động.

## Kết quả cần bàn giao để xin quyết định triển khai

- Thiết kế transaction/lock/permit với failure matrix: mỗi thời điểm crash, ledger/permit và số dispatch.
- Mã patch có test chạy offline/mock, kết quả test chi tiết và logs đã khử nhạy cảm; provider mock cap test, no-bypass.
- Compatibility review với ledger P0 hiện hữu; cơ chế migrate/restore state an toàn, không thay đổi baseline/cost/accounting.
- Tình trạng được tách `CODE_READY`, `MOCK_PASS`, `LIVE_PREFLIGHT_PENDING`, `BLOCKED`; phương án deploy sandbox với rollback và những quyền cần duyệt.
- Không sử dụng live health/ledger cũ làm bằng chứng hiện tại. Codex cần xác minh live preflight trong cửa sổ thi hành được phép trước mọi paid request.
- Báo cáo `reports/2026-11-21-hermes-gate-b-guard-hardening.md` (hoặc ngày thực tế), evidence JSON redacted; cập nhật task, `STATE.md`, `CATALOG.yaml`, `CHANGELOG.md`; push commit. Nếu không push được, báo `NOT_PUSHED`.

**Kết luận:** GATE B vẫn `BLOCKED_PREFLIGHT` cho tới khi one-shot permit + shared budget reservation được kiểm chứng toàn tuyến, live production/ledger/kill-switch được xác minh và mọi approval có liên quan được đáp ứng.
