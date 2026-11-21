---
id: ttd-hermes-e2e-hard-cap-001
type: task
status: ready_for_read_only_feasibility
updated_at: 2026-11-21
sensitivity: public
owner: codex
support: [hermes, hostinger-agent]
depends_on: [ttd-ai-p0-level2-001]
implementation_approval: pending
paid_inference_approval: pending_new_gate
---

# TTD-HERMES-E2E-HARD-CAP-001 — Chứng minh hard token cap trong Hermes Agent thực

## Mục tiêu

Tháo blocker `HERMES_E2E=BLOCKED_COST_CONTROL` mà không vượt qua giới hạn chi phí đã duyệt. Đầu tiên thực hiện **read-only feasibility và thiết kế kỹ thuật**. Không được xem task này là giấy phép triển khai runtime mới, mở egress, tắt kill switch hoặc phát sinh paid calls.

## Cơ sở bằng chứng

- [Level 2 results](../reports/2026-11-21-n8n-hermes-p0-level2-results.md): `PROVIDER_E2E=PASS`, 1 paid call, 131 input + 73 output, usage-based USD 0.0000496 (invoice chưa đối soát), kill switch đang bật.
- [Evidence Level 2](../reports/evidence/2026-11-21-ttd-ai-p0-level2-001.json): `HERMES_E2E=BLOCKED_COST_CONTROL`; Hermes CLI one-shot chưa chứng minh `max_output_tokens` trước khi gửi, model mặc định `(auto)`, tools chưa được chứng minh đã tắt hoàn toàn và chưa có private callback inference route.
- [P0 Level 2 approved bounds](../decisions/2026-11-21-p0-reasoning-integration-proposal.md): tổng 5 paid calls, ≤4,000 input và ≤2,000 output tokens/call, USD 0.05/day và USD 0.05 toàn P0, fake-data only, không thay production. **Đây không phải quyền nới giới hạn hay gọi tiếp khi cap không kiểm soát được**.

## Chủ đề cần chứng minh — chưa thực hiện paid call

1. **Hermes runtime thật:** kiểm tra CLI/API upstream + Hostinger wrapper version/image/entrypoint; phân biệt Hermes WebUI và U4S riêng. Đề xuất runtime phụ **có danh tính Hermes kiểm chứng được**, pin version/digest và tách biệt production.
2. **Provider-side hard output cap:** chỉ chấp nhận phương án gắn tham số output-token limit vào request **trước khi provider thực thi**, có evidence ở request serialization/schema hoặc test miễn phí với provider mock. Cắt output sau khi nhận/usage report hậu kiểm **không đạt**.
3. **Exact model và tool-off:** chứng minh request được gửi với `gpt-6-luna`, `max_output_tokens<=2000`, input ceiling ≤4000, **không tool use, web/search, MCP, memory-driven tool invocation, sub-agent hoặc recursive model calls**. Nếu Hermes nội bộ sinh thêm requests hoặc auto-retry, chúng phải đi qua cùng admission budget guard.
4. **Atomic spend gate chung:** chia sẻ **cùng** persistent P0 budget ledger đang có (hiện 1 paid call), không tạo/reset ledger mới. Trước mọi external call reserve worst-case upper bound có locking; chống bypass bởi Hermes, retry, tool/subcall, concurrent jobs. Kiểm tra kill-switch vẫn bật. Nếu không enforce được, STOP.
5. **API/callback:** authenticated private bridge `n8n sandbox -> real Hermes Agent -> authenticated n8n callback`, JSON schema, task/correlation IDs, health and error tests; không dùng adapter gọi thẳng OpenAI làm bằng chứng Hermes.
6. **Cô lập và rollback:** không thay Hermes/n8n production, `ttdnew.tech`, firewall, DNS, public ports hoặc credentials. Đánh giá CPU/RAM, backup, image source, egress domain allowlist, service-token permissions và tác động recreate. Không thêm service/egress khi chưa được chủ dự án duyệt.
7. **Đề xuất ít nhất hai phương án khả thi:** cấu hình supported trên Hermes upstream/CLI vs adapter/transport enforcing provider request pre-dispatch (nếu vẫn thực sự chạy Hermes); ưu/nhược/rủi ro, test miễn phí, xác suất tương thích, rollback và tiêu chí STOP. Không chấp nhận bọc OpenAI SDK rồi đặt tên Hermes.

## Được phép ngay

Read-only inspection trên nguồn tài liệu, repository, source code đã có quyền, CLI help, image metadata, config schema đã redacted và tests offline không phát sinh phí/không đổi runtime. Ghi report lên GitHub.

## Cần phê duyệt riêng sau feasibility

Mọi việc triển khai Hermes auxiliary runtime mới, thay sandbox compose, tạo secrets mới, thay proxy/egress, mở khóa kill switch hoặc phát sinh paid inference. Phê duyệt tiền còn lại từ Level 2 không được diễn giải là quyền test Hermes khi vẫn `BLOCKED_COST_CONTROL`.

## Nghiệm thu của task này

Một tài liệu **feasibility + kế hoạch triển khai có chốt kỹ thuật** ghi:
- Cơ chế hard output cap trước request đã VERIFIED hoặc BLOCKED, với chứng cứ.
- Đúng Hermes runtime, exact model, tools-off, atomic shared ledger, callback — phân loại VERIFIED/PLANNED/BLOCKED.
- Có phương án preflight offline và rehearsal kiểm chứng không có đường bypass.
- Bảng thay đổi dự kiến, backup/rollback, tác động production, số paid calls còn lại, dự toán upper bound và quyền cần duyệt.
- Kết luận GO/NO-GO cho **đề nghị phê duyệt triển khai riêng**; không tự đánh dấu Hermes E2E PASS.

## Bàn giao

Tạo `reports/2026-11-21-hermes-agent-e2e-hard-cap-feasibility.md` (hoặc ngày thực tế), cập nhật catalog/state/changelog khi có bằng chứng mới và push commit. Chỉ ghi metadata đã khử bí mật trên GitHub public.
