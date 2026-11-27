---
id: hermes-gate-a-mock-results-2026-11-21
type: report
status: complete
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-gate-a-001
result: gate_a_mock_pass
---

# Hermes auxiliary guard/bridge — kết quả GATE A mock

## Kết luận

**GATE A PASS** trên sandbox KVM 2. Luồng `n8n sandbox -> authenticated bridge -> Hermes auxiliary -> private guard -> provider mock -> authenticated callback` đã chạy end-to-end với Hermes thật, không gọi provider trả phí. Exact model, hard output cap, giới hạn input, tools disabled, authentication, no-bypass, idempotency, fault handling, rollback và production health đều được kiểm chứng.

GATE B **không được thực hiện**. Kết quả này chỉ đủ điều kiện để chủ dự án xem xét phê duyệt riêng đúng một paid Hermes call; không phải `HERMES_E2E_PAID_PASS` và không đóng toàn bộ P0.

## Phạm vi đã triển khai

- Bốn container sandbox: Hermes auxiliary, inference guard, provider mock và authenticated bridge; không container nào publish port.
- Ba network mới đều `internal=true`: control, guard và mock-upstream. Hermes chỉ thấy guard, không được nối vào mock-upstream hay public egress.
- Image được pin bằng digest `sha256:0ea63377bd672cb76de6a8510aaaef619fe2a045558b771656c072ef527c344f`.
- Hai service secret mới được sinh bằng CSPRNG, lưu trong thư mục mode `700`, file mode `600`, root-owned. Giá trị không được in, log hoặc đưa vào Git.
- Hermes auxiliary không nhận provider credential. Provider duy nhất của GATE A là mock private.
- P0 ledger thật chỉ được đọc để xác nhận kill switch; không reset, unlock hoặc thay đổi số liệu.

Mã triển khai secret-free nằm trong [`sandbox/p0-hermes-gate-a/`](../sandbox/p0-hermes-gate-a/README.md).

## Nghiệm thu

| Điều kiện | Kết quả | Bằng chứng đã khử bí mật |
|---|---|---|
| Runtime và authentication | PASS | Bốn service healthy, restart count 0, không public port; Hermes API sai token trả 401, token đúng với body sai trả 400; bridge và callback dùng auth riêng. |
| Exact model | PASS | Mọi request bắt được tại guard đều là `gpt-6-luna`; model khác bị chặn 422 trước mock. |
| Hard output-token cap | PASS | Guard inject/enforce `max_output_tokens=600`; request cap cao hơn bị chặn 422. |
| Input <= 4K | PASS | Guard đo toàn bộ canonical serialized request bằng ASCII bytes trước dispatch. Giá trị lớn nhất quan sát là 3.315 bytes; dùng 1 byte <= 1 token làm upper bound bảo thủ, nên dưới 4.000 token. Oversize bị chặn 422. |
| Tools disabled, one turn | PASS | Capture xác nhận không có `tools`, `tool_choice` hoặc `parallel_tool_calls`; cấu hình Hermes giới hạn một turn, retry/fallback bị tắt. |
| No-bypass | PASS | Hermes không resolve/gọi được public OpenAI hay service provider-egress hiện hữu; chỉ guard có đường đến mock trên private network. |
| Mock E2E | PASS | Authenticated n8n workflow gọi Hermes API thật, guard chuyển đúng một physical request tới mock và callback về n8n HTTP 200. |
| Negative/fault/idempotency | PASS | Missing/wrong auth 401; invalid schema 422; conflict 409; provider error 502; timeout replay, 5-way concurrency và duplicate replay không tạo thêm physical request ngoài dự kiến. |
| Rollback/restore | PASS | Corrected rollback rehearsal dừng toàn bộ GATE A, khôi phục reasoner/workflow trước đó; redeploy và post-rollback smoke đều PASS. |
| Production health | PASS | n8n `/healthz` và Hermes `/api/health` đều HTTP 200 trước/sau; restart count 0, downtime 0. |
| Chi phí và kill switch | PASS | Paid calls mới 0, chi phí API mới USD 0; ledger thật không đổi và kill switch vẫn ON. |

Capture cuối ghi nhận 10 physical request tới **mock** trong toàn bộ diagnostics, fault rehearsal và smoke; tất cả exact-model, cap 600, no-tools. Raw request chỉ được giữ root-only trên VPS để kiểm chứng và không đưa lên repository.

## E2E và fault results

- Normal E2E: HTTP 200, callback HTTP 200, `mode=hermes_mock`, `paid_inference=false`.
- Client timeout: một physical mock request; retry cùng idempotency key replay kết quả, không nhân đôi dispatch.
- Concurrency: năm request đồng thời cùng key cho một physical mock request; các request còn lại nhận trạng thái pending/replay và kết quả cuối HTTP 200.
- Idempotency conflict: cùng key với payload khác bị chặn 409, physical delta 0.
- Provider fault: mock error được bridge trả 502, không fallback hoặc provider call phụ.
- Post-rollback smoke: HTTP 200 và authenticated callback HTTP 200.

## Rollback và sự cố đã xử lý

Lần rehearsal đầu phát hiện file workflow rollback được copy với ownership `root:root`, khiến n8n sandbox không đọc được khi import. Đây là lỗi sandbox, không ảnh hưởng production. Runtime cũ được khôi phục ngay; script sau đó được sửa để cài file với ownership của n8n sandbox (`1000:1000`).

Rehearsal sửa lỗi chạy lại đã PASS: GATE A running count 0, reasoner cũ healthy, workflow cũ được import/publish. Sau đó GATE A được redeploy, các service healthy và smoke test PASS. Backup trước thay đổi được giữ ngoài Git trên VPS.

## Bất biến production và ngân sách

- Không restart/recreate n8n hoặc Hermes production; restart count cuối vẫn 0.
- Không đổi DNS, firewall, public port, production credential/encryption key, U4S, website, quảng cáo hoặc business service.
- P0 ledger trước/sau giữ nguyên: attempts 1, reserved USD 0.0035, actual USD 0.0000496; hash file không đổi.
- Kill switch vẫn `true`; paid provider không có đường hoạt động trong GATE A.

## Giới hạn còn lại và quyết định cần phê duyệt

- Hermes upstream poll response trả đúng runtime *requested* nhưng để trống trường served model/provider. Bridge xác nhận requested pair, từ chối mọi non-empty mismatch; guard capture là bằng chứng có thẩm quyền cho model thực tế được forward. Đây là hạn chế metadata upstream, không phải bypass.
- Compose GATE A hiện là sandbox thủ công, không có restart policy để tự khởi động sau reboot. Không nên biến nó thành service bền vững trước một phê duyệt vận hành riêng.
- Mock PASS không chứng minh paid Hermes E2E. GATE B cần phê duyệt riêng cho đúng một call, vẫn dùng shared atomic ledger, hard guard và trần ngân sách P0. Chưa có credential/provider paid nào được cấp cho Hermes auxiliary.

Đề xuất trạng thái: **GO_FOR_GATE_B_APPROVAL**, không phải quyền tự thực hiện GATE B.

## Liên kết

- [Task GATE A](../tasks/2026-11-21-hermes-auxiliary-guard-bridge-gate-a.md)
- [ADR-P0-002](../decisions/2026-11-21-hermes-auxiliary-guard-bridge-approval-proposal.md)
- [Evidence JSON](evidence/2026-11-21-ttd-hermes-gate-a-001.json)
