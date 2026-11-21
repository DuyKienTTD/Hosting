---
id: hermes-gate-b-h6-b2-m-kvm2-idle-canary-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-M — Canary startup-only trên KVM2

**ACKNOWLEDGED / KVM2_FAKE_IDLE_CANARY_PASS / ROLLBACK_PASS.** ACK phê duyệt `5ce7537ba39ec428293055544ddc149a6ee723c5` và AGENTS, full Workflow §§7–10, security, STATE/CATALOG, Codex profile, toàn bộ task/ADR-P0-003 và B2-K/L reports/review tại `b6466081ad9d2b57cd907c464cb63e78df64bd4a`. Task blob khớp phê duyệt. Đã đọc delta `1948568` mở Work QA độc lập. [Review B2-K/L](2026-11-22-hermes-gate-b-h6-b2-k-l-chatgpt-review.md) · [Work QA](../tasks/2026-11-22-work-b2-m-independent-canary-qa.md).

## Cổng kiểm trước up

Baseline chỉ đọc trên KVM2 gồm 9 container, 11 network và 11 volume. GATE A chạy theo baseline, Level2 dừng, n8n/Hermes production trả HTTP 200/200. Chỉ lấy Docker mount metadata và `lstat`/ACL cho đường dẫn ledger/lock thật. Runner xác minh SHA-256 của chính nó, blob Compose, sáu file B2-L tại `c4d5402` và helper inventory B2-E. Image cache được inspect đúng digest, không pull. [Runner](../sandbox/p0-hermes-gate-a/h6_b2m_canary.py) · [Compose](../sandbox/p0-hermes-gate-a/h6_b2m_compose.yaml).

Render đủ profile qua stdin, dùng chỉ project `h6-b2-m-idle-canary`. So với baseline, thay đổi duy nhất dự kiến là thêm đúng một container writer có nhãn owner riêng. Không có network mới/external, volume Docker mới, cổng public, secret definition, Docker socket, host namespace hay dependency. So tên project/container, label và mọi source mount với toàn bộ inventory. Render lặp khớp byte và đối chiếu lại ngay trước up. Hash JSON đã khử đường dẫn/owner `a33d284eec705b8b22459952ae9f57650b137aeb0e0f4cc96b785b619a8b6543`. Bản render local đã khử định danh khớp hash KVM2. [Evidence và toàn bộ render](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-m-kvm2-idle-canary.json).

| Mount | Phạm vi |
| --- | --- |
| `/opt/b2m-src` | Sáu file nguồn B2-L ghim, bind RO |
| `/tmp/h6-b2l-canary` | Fixture ext4 riêng RO, ledger parent root:root 0700, ledger/lock 0600, khóa IPC giả 0400 |
| `/tmp/h6-b2l-canary/ipc` | Bind RW chỉ cho socket/lifetime lock giả |
| `/opt/data` | Tmpfs 8 MiB che volume mặc định của image |

Ba bind đều `rprivate`, không tạo source path tự động. Kiểm Docker inspect và bên trong container sau up và restart đều đúng image/entrypoint, UID/GID 0, toàn bộ cap sets bằng 0, NoNewPrivs bật, rootfs/ledger/key RO, chỉ interface `lo`. Writer chỉ chạy startup-only health, không có đường nối provider/proxy.

## Test và rollback

- Hai lần khởi động với zero permit, mỗi lần 10 health HMAC liên tiếp trả `IDLE_NO_PERMIT`. Bytes, device/inode và atime/mtime/ctime của ledger/lock giả khớp. Baseline fixture giữ 1 attempt, reserve giả USD 0.0035, actual giả 0.
- Key sai bị từ chối. Hai peer sai UID hoặc GID kết nối được vào socket giả rồi bị cắt trước HMAC. Chỉ mở quyền traverse trên cây fixture trong lúc thử, phục hồi ngay sau đó, và xác minh health lại. Writer giữ caps bằng 0.
- Lock contention trả `UNAVAILABLE` sau khoảng 202 ms rồi phục hồi. Ledger hoặc lock vắng và lock thay inode trả `BLOCKED`; phục hồi file giả đúng inode trả idle. Với permit giả còn hạn và đúng scope, writer báo `STARTUP_ONLY` và chặn admit/settle/snapshot, fixture bất biến. Không có đường dispatch hoặc fake POST.
- Rollback xác minh chính xác container ID/name/owner label trước khi gỡ, rồi đối chiếu inode thư mục trước khi dọn fixture. Sau rollback còn 0 container canary. Toàn bộ inventory cũ và metadata ledger/lock thật khớp; GATE A/production giữ trạng thái, PID/start time, health và restart counters. Production HTTP sau rollback 200/200. Không restore ledger.

Đã tái sử dụng B2-L cho sáu cửa sổ crash. B2-M kiểm ext4 trong startup/health, không kiểm mất điện. Deadline/idempotency Hermes và callback n8n thực tế thuộc gate riêng. Có 0 truy cập nội dung ledger/lock/permit/key thật, provider API, paid inference hoặc production mutation và USD 0.

**`LIVE_INTEGRATION_NO_GO / BLOCKED_UID_OR_MOUNT / BLOCKED_PREFLIGHT`.** `next_owner: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`. ChatGPT đối chiếu kết quả với QA Work độc lập trước khi quyết định bước fake-provider tiếp theo.
