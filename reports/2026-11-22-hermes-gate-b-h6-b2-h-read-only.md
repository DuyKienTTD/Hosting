---
id: hermes-gate-b-h6-b2-h-read-only-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-H — KVM2 read-only integration readiness

**ACKNOWLEDGED / H6_B2_H_READ_ONLY_PREFLIGHT_COMPLETE / LIVE_INTEGRATION_NO_GO.** Các blocker xác định được là `BLOCKED_DEADLINE_AND_CALLBACK_CONTRACT` và `BLOCKED_UID_OR_MOUNT`. Paid GATE B giữ `BLOCKED_PREFLIGHT`. ACK phê duyệt `08bc6398145df81ca91938b4ded34bb4c46f3e4f`, AGENTS, Workflow §§7–10, Repository Security, STATE/CATALOG, Codex profile, toàn bộ task và ADR-P0-003 tại `938019bc8d830c0c3404b19ff17a649fe8f505a7`. Đã đọc lại delta STATE/CATALOG ở `90c9131` về luồng Work độc lập. Workflow và parent task giữ nguyên nội dung phê duyệt. [Review B2-G](2026-11-22-hermes-gate-b-h6-b2-g-chatgpt-review.md).

## Live metadata và giới hạn phép đo

| Phần | Bằng chứng |
| --- | --- |
| Inventory, source và backup | **VERIFIED_LIVE.** 9 container, 11 network, không còn container/network B2-G. Production n8n/Hermes đều running, restart 0/0 theo Docker. Hai file backup H4 khớp byte, render và hash cấu hình Guard đang chạy. Source Guard trùng blob lịch sử `1953a81` và khác B2-F `b670a65`. Source bridge, Level 2 adapter và CONNECT proxy khớp file Git. Inventory pre/post bằng nhau. Đợt này không dùng HTTP health production. |
| P0, Level 2 và userns | **VERIFIED_LIVE metadata.** ext4, parent `0:0 0700`, ledger/lock `0:0 0600`, mỗi file một hard link, không ACL. Ledger/lock cùng device, inode khác nhau. Guard bind trực tiếp một file RO, inode nhìn từ Guard khớp host tại thời điểm đo, lock cạnh file vắng. Process Guard `0:0`, cap sets bằng 0, NNP bật, cùng userns host, daemon rootful không remap. Level 2 cấu hình root, stopped với restart `unless-stopped`, có directory bind RW trùng parent ledger. Không mở hoặc khóa file thật. |
| Provider mount và proxy | **VERIFIED_LIVE metadata.** Provider credential mount RO duy nhất tại Guard, metadata `0:0 0600`, không ACL. Mạng proxy riêng chỉ nối Guard và proxy, internal, IPv6 tắt. Alias `provider-egress` khớp B2-F, Guard/proxy không publish port, không có service đang chạy khác trên các mạng proxy đã thấy. Source proxy chỉ cho CONNECT OpenAI :443 qua port nội bộ 8888, socket connect budget 10 s và idle select 30 s. Không gửi request tới proxy hoặc provider; reachability lúc apply thuộc gate riêng. |
| Hermes và bridge | **VERIFIED_LIVE metadata.** Aux Hermes cấu hình route tới Guard; bridge dùng POST/poll Hermes với timeout socket 5 s, cửa sổ poll 20 s, callback timeout socket 5 s và đọc bearer từ file reference. Source Hermes cài đặt có API-call default 1.800 s và cho override theo model/provider. Không thấy các key timeout được tìm trong cấu hình chính hoặc hai biến timeout được kiểm trong Docker env. **UNKNOWN** số đo deadline thực của request streamed qua Hermes/SDK và cấu hình hợp nhất của process; default source không thay cho số đo. |
| n8n sandbox | **VERIFIED_LIVE published configuration.** SQLite WAL đọc bằng kết nối RO trong child bị kernel cấm ghi filesystem. Chỉ chiếu timeout, cờ và kiểm tra cấu trúc của published revision; không chọn credential data, raw nodes hoặc giá trị auth. Workflow active, gọi bridge với timeout 30.000 ms, retry off. POST callback khớp sandbox webhook; nhánh bearer kiểm trước callback, unauthorized cấu hình 401. Validator chỉ chấp nhận `hermes_mock_succeeded` và `paid=false`. **UNKNOWN** việc khớp giá trị token và HTTP callback live end-to-end; không gọi webhook. [SQLite WAL read-only](https://sqlite.org/wal.html#readonly) · [Landlock](https://docs.kernel.org/userspace-api/landlock.html). |

[Probe read-only ghim](../sandbox/p0-hermes-gate-a/h6_b2h_preflight.py) chạy tại `564a928` bằng source đã xác minh SHA-256, trong bộ nhớ. [Evidence với source hashes](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-h-read-only.json).

## Compose before/after đề xuất

Thực hiện `docker compose config` với project/file H4 thực, tất cả profile, overlay stdin và không tạo staging trên KVM2. Before `95d1ac6195639c19fe874937be7f87d1c6ad0202c49baa0032ef8bab9198f08f`, after `a940e88e5bce761c4719e4f095075b5fd1ce2aaa40a111d88c34d95059e4c53c` là SHA-256 của JSON render chuẩn hóa. Render mỗi bản hai lần khớp. Kiểm tên writer và các path reference dự kiến không trùng. Không thay đổi top-level resource hay định nghĩa network. `bridge`, `hermes-aux`, `provider-mock`, proxy, Level 2 và production nằm ngoài delta.

| Service | Toàn bộ delta render |
| --- | --- |
| `guard` | 6 trường đổi: `entrypoint`, `environment`, `networks`, `tmpfs`, `user`, `volumes`. Đặt UID/GID `0:0`, entrypoint `python3 -B /opt/ttd/h6-src/guard.py`, env `TTD_H6_PROVIDER_MODE=real` chỉ xuất hiện trong preview. Giữ `gate_provider` và `gateb_guard`, rời `gate_upstream` của mock để bỏ đường fallback. Giữ healthcheck hiện có. Thêm tmpfs `/opt/data` 8 MiB để che volume mặc định của image. |
| Mount `guard` | Bỏ legacy ledger RO, capture RW và hai code bindings cũ; live bridge không tham chiếu capture trong source. Giữ hai mount RO hiện có cho Guard service authentication và provider. Thêm bundle RO `/opt/ttd/h6-src`, IPC directory RO `/opt/ttd/h6-b2f-live-ipc`, key directory RO `/run/h6-b2f-live-auth`. Guard không có direct ledger bind. |
| `h6-writer` mới | Profile `b2h-preview`, tên chưa tồn tại, image ghim cùng Guard, pull policy never. Entrypoint `python3 -B /opt/ttd/h6-src/h6_writer.py --b2-f-real`, UID/GID `0:0`, cap_drop ALL, NNP, rootfs RO, network none, 0 port, 48 PID, 128 MiB, 0,25 CPU, tmpfs `/opt/data` 8 MiB. Bind RW `rprivate` đúng parent ledger vào `/opt/ttd/p0-ledger` và IPC directory riêng vào `/opt/ttd/h6-b2f-live-ipc`. Bundle và IPC key directory RO như Guard. Không provider mount, env file hay secret definition. Bind mới đều `create_host_path: false`. |

Bundle và IPC path hiện là reference chưa tồn tại. Sau duyệt riêng, bundle phải ghim B2-F source, socket parent `0:0 0700`, socket `0600`, key IPC riêng 32 byte từ kênh bảo mật, file `0:0 0400` trong parent `0700`, chỉ Guard/writer thấy. Build hiện tại hard-disabled và writer startup yêu cầu permit hợp lệ, nên render không thể được xem là kế hoạch khởi động khả dụng.

## NO-GO và rollback

1. **Deadline/callback, Codex sau review ChatGPT.** Bridge 20 s và n8n 30 s ngắn hơn budget phản hồi 45 s của B2-F trước ACK settlement. Guard buffer SSE, và proxy có idle 30 s. Cần kiểm lại thứ tự deadline Hermes/SDK, proxy, Guard/IPC, bridge và n8n dưới fake slow stream, đồng thời kiểm contract callback riêng, đúng phase/auth/schema/idempotency. Bridge và validator hiện chỉ mô tả mock. Không gắn nhãn kết quả provider là mock thành công.
2. **Mount, credential và permit, ChatGPT điều phối gate riêng.** Writer chưa có live directory mount hoặc IPC key được phê duyệt. Kiểm lại source bundle, owner/ACL và bind boundaries trước mọi apply. Giữ Level 2 nguyên trạng và giải quyết cạnh tranh/restart trong thiết kế; adapter Level 2 thiếu directory fsync, power-loss chưa chứng minh. Giữ hard-disable trong gate kế tiếp.
3. **Final count/cost, gate riêng.** H5 count 723 thuộc SHA ứng viên cũ. Freeze, pin SHA đúng byte cuối và tái xác minh model/tier/quota/pricing/count, reserve và phạm vi permit qua quy trình được phê duyệt sau đó. Không tái dùng quote fixture hoặc biến B2-G thành bằng chứng provider thật.

**Rollback dry-run PASS.** Backup H4 và round-trip render khớp. Khi một apply riêng được duyệt, có thể cô lập writer và khôi phục đúng Guard bằng config H4 và source ghim đã kiểm, giới hạn service đích. Không dùng project-wide down hoặc prune. Giữ ledger/lock và mọi phần ghi đã commit, không chép snapshot cũ. Khi mất ACK hoặc chưa rõ outcome, tiếp tục khóa dispatch đến khi đối soát. B2-H không chạy rollback live.

`from_agent: codex` · `next_owner: chatgpt` · `handoff_state: PREPARED_FOR_OWNER_FORWARD`. ChatGPT đối chiếu evidence này với audit Work độc lập. Bước kế tiếp nhỏ nhất là kiểm deadline/callback với fixture, trước mọi đề nghị chạm live ledger. Trong B2-H có 0 up/recreate, 0 lần đọc nội dung hoặc ghi ledger/lock/permit/provider-key thật, 0 OpenAI API, 0 paid và 0 production mutation.
