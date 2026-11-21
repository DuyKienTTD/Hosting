---
id: hermes-gate-b-h6-b2-k-cross-service-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-K — Async adapter qua ba tiến trình mock

**ACKNOWLEDGED / H6_B2_K_CROSS_SERVICE_MOCK_PASS.** ACK phê duyệt `4a527e752744f4f41f1107dfae3cd566348fa86b`, AGENTS, AGENT_WORKFLOW §§7–10, security, STATE/CATALOG, hồ sơ Codex, task mẹ/ADR-P0-003 và Work B2-J review tại `4d5b5e9a7b5e46d782dea3316b697d6f115e4ee6`. B2-K không sửa writer startup. [Phê duyệt](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Review B2-I](2026-11-22-hermes-gate-b-h6-b2-i-chatgpt-review.md).

## Đã xác minh offline

Ba process Python riêng trên Windows loopback có ba SQLite tạm, mỗi process được truyền một path với đúng một bảng. Adapter commit `POST /jobs → 202`, giữ job/task/correlation/canonical input SHA và ánh xạ run sau `POST /runs`. Executor giả giữ run ID và cho một transition dispatch duy nhất. Receiver nhận binding qua endpoint bearer riêng, xác minh HMAC callback và trả receipt ký bằng khóa khác, gắn job/run/event SHA. Binding khớp trước khi ghi receipt. Adapter chỉ ký outcome terminal đọc từ executor. Cả ba vai trò chạy với tiến trình, cổng và trạng thái riêng. Isolation đã đo ở mức process/database ứng dụng trên cùng OS user.

| Test delta | Kết quả |
| --- | --- |
| Split process/SQLite, mất `202` sau commit, mất run ACK | Cùng job ID sau adapter restart và cùng run ID sau executor restart. Một dispatch/settlement/receipt. |
| Admission, mapping và start đồng thời | Sáu admission quy về một job, bốn mapping cùng run, một trong bốn start được nhận. Duplicate collect/delivery không nhân kết quả. |
| Auth và thứ tự | Từ chối callback trước binding, sai khóa/hết hạn, sai sequence, job/run/task/correlation/SHA lệch. Replay sau receiver restart và outcome mâu thuẫn bị chặn. |
| Mất dispatch/callback ACK, unknown | Một dispatch giả, 0 settlement, reserve giữ `held`. Outbox vào `dead_letter`, redelivery đối soát một receipt có chữ ký sau restart, không re-dispatch. |
| Receiver không khả dụng | Dead-letter được phục hồi có giới hạn sau receiver khởi động. Một dispatch/settlement/receipt. |
| Receipt bị sửa chữ ký | Outbox giữ dead-letter dù receiver đã commit. Gửi lại cùng event đối soát receipt hợp lệ, số lần dispatch/settlement/receipt không tăng. |

Lệnh `python -B sandbox/p0-hermes-gate-a/h6_b2k_services_test.py` đạt **6/6**. Test chỉ chạy delta cross-process và recovery. Các timeline B2-I 5/21/31/46 giây giữ bằng chứng tại `8ded770`. Fixture điều khiển start/finish bằng RPC test, và `paid_succeeded` luôn synthetic. [Source](../sandbox/p0-hermes-gate-a/h6_b2k_services.py) · [Test](../sandbox/p0-hermes-gate-a/h6_b2k_services_test.py) · [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-k-cross-service.json).

## Gate kế tiếp và rollback

Bridge đã đọc từ Git gọi `POST /v1/runs` với Idempotency-Key rồi poll `GET /v1/runs/{run_id}`. Tài liệu upstream mô tả run ID replay qua restart. Những gì đã xác nhận với bản Hermes đang cài đến từ B2-H. Tính bền của run ID/idempotency và deadline trên bản đích vẫn `UNKNOWN`. Nếu lần gửi thực tế mất ACK, giữ trạng thái đối soát và dừng submit cho đến khi đọc lại được run hoặc bảo đảm deduplication trên đúng build/credential. [Bridge](../sandbox/p0-hermes-gate-a/bridge.py) · [Tài liệu Runs API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server).

Sau review, cấu hình khả thi nhỏ nhất là một route sandbox song song với datastore riêng, khóa callback/receipt tách, mapping persisted và worker poll hữu hạn, dùng fake executor cho lần tích hợp đầu. Rollback dừng admission route mới, giữ mapping/outbox để drain hoặc đối soát rồi gỡ tài nguyên mock riêng. Không replay inference hay phục hồi ledger cũ. B2-K có 0 KVM2/live apply, production, ledger/permit/key thật, API provider, paid và USD. `LIVE_INTEGRATION_NO_GO / BLOCKED_PREFLIGHT`. `next_owner: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`.
