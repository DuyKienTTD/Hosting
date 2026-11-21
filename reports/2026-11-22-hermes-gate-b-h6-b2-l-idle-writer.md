---
id: hermes-gate-b-h6-b2-l-idle-writer-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-L — Writer startup-only và health IPC chỉ đọc

**ACKNOWLEDGED / B2_L_SOURCE_MOCK_PASS.** ACK phê duyệt `4a527e752744f4f41f1107dfae3cd566348fa86b` và AGENTS, Workflow §§7–10, security, STATE/CATALOG, hồ sơ Codex, toàn bộ task, ADR-P0-003 và Work B2-J tại `4d5b5e9a7b5e46d782dea3316b697d6f115e4ee6`. B2-K đã commit/push/readback riêng tại `351afa2` trước khi sửa nguồn B2-L. [Work audit](2026-11-22-work-b2-j-idle-startup-audit.md) · [ChatGPT review](2026-11-22-work-b2-j-chatgpt-review.md).

## Startup-only và quyền admission

`h6_writer.py --b2-l-startup-fixture <root-fixture>` chỉ chấp nhận thư mục tạm riêng, UID/GID 0 và key IPC giả 0400. Entrypoint đăng ký duy nhất `health` v1 qua Unix SOCK_SEQPACKET, mutual SO_PEERCRED và HMAC challenge/ACK gắn request, dùng domain riêng. Schema phản hồi chỉ gồm version, healthy và enum. State idle có thể phục vụ health trước khi có permit. `STARTUP_ONLY`, `IDLE_NO_PERMIT`, `RECONCILE_REQUIRED` và `SETTLED` không cấp quyền admission; mọi admit/settle/snapshot đều bị từ chối, kể cả permit fixture hợp lệ. Đường `--b2-f-real` vẫn khóa ở build.

Health mở ledger và stable lock có sẵn bằng FD RO, `O_NOFOLLOW`, `O_NOATIME` và không `O_CREAT`. Kiểm UID/GID, mode, hardlink, ACL, device và pathname/FD inode trước và sau đọc. Pin inode lock trong vòng đời process. Shared flock có budget 200 ms. Ledger/lock vắng, sai schema hoặc drift trả `BLOCKED`; contention trả `UNAVAILABLE` và hồi phục sau giải phóng lock. Socket và singleton lock chỉ xuất hiện trong IPC directory của fixture. Code đọc ledger cũ tái sử dụng cùng hàm decode; giữ nguyên transaction P0 admit/settle.

## Kết quả local Linux

**9/9 test B2-L PASS.** Docker Desktop Linux, Python 3.12.16, rootfs RO, `network none`, ledger tmpfs root:root 0700/0600 và key giả. Tám test chạy cap-drop ALL. Test sai UID/GID chạy container riêng với SETUID/SETGID để tạo peer sai và xác minh bị từ chối ở IPC handshake. Hai cold starts, 20 authenticated health calls, bytes/device/inode/atime/mtime/ctime của ledger và lock khớp. Attempts 1, reserve giả USD 0.0035, actual 0, 0 file ledger mới và 0 fake POST. Khóa đang bận trả `UNAVAILABLE` rồi về idle. Các test còn lại kiểm no/valid/expired permit, request sai scope, ledger/lock vắng/sai mode/thay inode, kill switch sai, HMAC/domain sai, replay nonce và key thiếu.

Trong **chế độ admission giả riêng của test**, bốn admission có đúng một ACK hợp lệ và một fake POST ghi vào recorder local sau khi nhìn thấy consume/reserve đã commit. Terminal settle lặp khớp trả cùng ACK và giữ bytes, kết quả xung đột bị chặn.

| Cửa sổ lỗi | Trạng thái quan sát | Admit ACK / fake POST | Reserve giả |
| --- | --- | --- | --- |
| Trước rename | ready, bytes gốc | 0 / 0 | 0.0035 |
| Sau rename trước directory fsync | inflight, process restart cần đối soát | 0 / 0 | 0.007 |
| Sau fsync trước admit ACK | inflight | 0 / 0 | 0.007 |
| Sau ACK trước POST | inflight | 1 / 0 | 0.007 |
| Sau POST trước settlement | inflight, sau đó ghi unknown trong fixture | 1 / 1 | 0.007 |
| Sau settlement trước ACK | usage_recorded | 1 / 1 | 0.007 |
| Directory fsync trả EIO | inflight, không ACK và giữ fence | 0 / 0 | 0.007 |

Không có fake POST mới sau restart. Trước rename, restart startup-only đóng admission kể cả khi vẫn thấy permit ready. Các ca đã consume cũng bị từ chối khi replay trong chế độ admission giả. Lock inode giữ nguyên ở mọi trường hợp. Process fault trên tmpfs kiểm thứ tự commit/ACK và các trạng thái có thể quan sát; host power-loss/ext4 durability còn chờ phép thử riêng. Phép đo bất biến atime áp dụng cho health; legacy admission có thể cập nhật atime khi đọc.

Tái kiểm targeted Linux one-shot parser/atomic admission và B2-F invalid ledger/scope/lock/operation vì parser được tách để dùng trên FD. Giữ evidence B2-I, B2-K, TLS và callback cũ. [Source](../sandbox/p0-hermes-gate-a/h6_b2l_idle.py) · [Test](../sandbox/p0-hermes-gate-a/h6_b2l_idle_test.py) · [Evidence và lệnh chạy](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-l-idle-writer.json).

## Canary và rollback đề xuất

Sau ChatGPT review, canary nhỏ nhất là project KVM2 độc lập với fake ledger ext4 0700/0600, IPC riêng, key giả, UID 0/caps 0, rootfs RO và network none. Pin source/image, render đầy đủ để xác minh tên, bind và tài nguyên không trùng. Chỉ kiểm cold start/restart, health, deny admission và metadata fixture trước/sau. Không swap Guard, gắn key thật hoặc mount ledger thật. Rollback chỉ dừng/gỡ tài nguyên canary theo manifest, giữ evidence và trạng thái đã commit, không restore snapshot đè ledger. Nếu cần mở lại admission từ trạng thái không chắc chắn, chờ đối soát; health không chứng minh durability hoặc quyền permit.

**0 thao tác KVM2, production, real ledger/permit/key, provider API hoặc paid. USD 0.** Live `NO_GO`, real writer mount `BLOCKED_UID_OR_MOUNT`, paid `BLOCKED_PREFLIGHT`. `from_agent: codex`, `next_owner: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`.
