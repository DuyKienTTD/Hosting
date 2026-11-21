---
id: hermes-gate-b-h6-b2-b-preflight-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-B — KVM2 preflight chỉ đọc

**H6_B2_B_READ_ONLY_PREFLIGHT_COMPLETE / BLOCKED_UID_OR_MOUNT cho apply.** Codex ACK task `2b53d7f2be5eae2c95117bbfa67c594d2d5015d6`, quy tắc và task trên main tại `a7dcc2246b9f9d64086a18a1681910e96cdf05ab`, mục 10 tại `c915618`. Phiên Web Terminal xác thực có quyền đọc metadata Docker trên KVM2. Quyết định vận hành dựa trên stat, ACL xattr, Docker inspect, và metadata process. [Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-b-preflight.json).

## Hiện trạng đã đo

| Hạng mục | Kết quả |
| --- | --- |
| Ledger và lock | Cả hai là regular file, `0:0` mode `0600`, mỗi file một hard link, hai inode riêng trên cùng device. Thư mục cha `0:0` mode `0700`, filesystem ext4 ghi được, chỉ có hai entry dự kiến. POSIX access ACL và default ACL đều vắng mặt. Không có entry khóa khớp inode tại thời điểm đọc `/proc/locks`. |
| Guard | Bind mount đúng một file ledger chỉ đọc. Device/inode thấy từ namespace Guard trùng file host tại thời điểm đo. Lock không xuất hiện cạnh ledger trong namespace Guard. Mã Guard khớp source đã đo ở H4/H5 và vẫn ở tuyến mock trước H6 IPC. |
| Level 2 | Resolve `P0_BUDGET_PATH` qua directory bind ghi được cho đúng file host và lock sibling. Container đang `exited`, restart count 0, policy `unless-stopped`. UID được cấu hình là root, userns ở chế độ mặc định. Không có PID để xác nhận process identity đang chạy. |
| UID/GID và userns | Docker rootful, không bật userns remap. Guard đang chạy UID/GID thực và hiệu dụng đều 0, cùng user namespace với host PID 1. Không có effective capabilities, `no-new-privileges` bật. Với ánh xạ này, UID 23062 và GID 23060 không có quyền traverse thư mục cha hay đọc/mở ghi hai file. Compose `rw` không cấp quyền DAC. |
| Ràng buộc Guard | Hai credential bind hiện có đều chỉ đọc và file thuộc `0:0` mode `0600`, không access ACL. Provider credential chỉ có một mount, tại Guard. Capture directory thuộc `0:0` mode `0700`. Đổi Guard trực tiếp sang UID 23061 sẽ mất quyền đọc credential và ghi capture với cấu hình hiện tại. |
| Runtime và postcheck | Guard, bridge, auxiliary Hermes và provider mock của GATE A đều running/healthy, restart 0. Production n8n và Hermes đều running/restart 0 theo Docker inspect. So sánh pre/post cho thấy trạng thái/start time/restarts/ports/network attachment và metadata ledger, lock, thư mục không đổi trong phép kiểm. Không gọi endpoint health của Level 2 hay production. |

**Kiểm chứng độc lập trên dữ liệu giả.** Docker Linux cục bộ `--network none` tái tạo ownership/mode tương đương. UID 23062/GID 23060 bị từ chối đọc ledger, mở lock để ghi và tạo file sibling, kể cả khi fixture cho phép traverse thư mục. Owner thay file bằng rename làm đổi inode ledger, giữ inode lock. Quyền thật trên KVM2 được kết luận từ metadata/DAC và test giả. Không chạy thử mở file hoặc khóa thật bằng UID đích.

## Render đề xuất và rollback

Compose 5.6.1 render base cùng H4 từ metadata project đang chạy. Hash cấu hình Guard khớp nhãn container. Render baseline rồi đọc lại qua stdin cho kết quả tương đương. Diff preview sau khi render toàn bộ profile có đúng các thay đổi sau.

| Đối tượng | Delta preview đã render |
| --- | --- |
| Guard | Bỏ bind file ledger chỉ đọc tại `/opt/ttd/ledger/level2-budget.json`. Thêm bind IPC riêng tại `/opt/ttd/h6-ipc` chỉ đọc, `create_host_path: false`. Các trường Guard còn lại khớp baseline. |
| `h6-writer-preview` | Thêm dưới profile `b2b-preview`; UID/GID `23062:23060`; cùng image Guard; entrypoint vô hiệu `/bin/false`; `network_mode: none`, root filesystem chỉ đọc, drop ALL và no-new-privileges. Hai bind ghi được gồm thư mục ledger chuyên biệt tại `/opt/ttd/p0-ledger` và thư mục IPC tại `/opt/ttd/h6-ipc`, đều đặt `create_host_path: false`. Tmpfs tại `/opt/data` xử lý volume mặc định của image. Không thêm port, network attachment, credential mount, environment hoặc env file. |
| Ranh giới khác | Không đổi service khác hoặc trường Compose cấp project/network/volume/port. Đường dẫn IPC preview chưa tồn tại. Preview được giữ trong bộ nhớ và không áp dụng. |

**Rollback đã kiểm ở mức cấu hình.** Hai file Compose trong backup H4 riêng khớp byte với các file hiện hành. Render trực tiếp từ bản sao trong context project cho cùng cấu hình với baseline. Đây là xác minh khả năng khôi phục cấu hình. Không chạy rollback hoặc recreate. Phương án rollback của lần apply được duyệt sau này phải dừng writer mới, phục hồi code/Compose đã pin và khôi phục đúng sandbox Guard. Giữ nguyên ledger, lock, permit và reserve đã commit qua rollback.

## Điều kiện chặn apply

1. **Writer 23062 chưa có quyền filesystem.** ChatGPT cần chọn mô hình một writer và chứng minh rằng Level 2 không thể ghi đồng thời, hoặc chứng minh hai writer tương thích với ownership sau mỗi `os.replace` và `fchmod(0600)`. Việc Level 2 đang dừng chỉ là trạng thái quan sát.
2. **IPC chưa sẵn sàng trên live Guard.** Cần bản Guard triển khai IPC và mô hình danh tính cho client/writer giữ quyền tối thiểu, đồng thời bảo toàn quyền credential/capture cần thiết. Writer hiện tại vẫn yêu cầu fixture. Không dùng tác vụ read-only này để nới mode/ACL, đổi owner, gắn directory thật hoặc thay code live.
3. **Kiểm lại trên fixture theo thiết kế được chọn.** Thử UID mapping và owner sau rename, IPC đúng và sai peer, stable lock, no-bypass và rollback giữ ledger. Level 2 vẫn thiếu fsync thư mục cha, nên cần ghi riêng giới hạn durability nếu phương án giữ writer Level 2. Bất kỳ bước thực hiện trên ledger thật nào chỉ sau khi ChatGPT xác lập phạm vi và kiểm đủ các gate.

**Phiên này có 0 thay đổi KVM2, 0 lần đọc nội dung ledger/lock hay credential, 0 thao tác permit, 0 provider calls, 0 paid attempts và 0 USD phát sinh.** Paid Gate B vẫn `BLOCKED_PREFLIGHT`. `from_agent: codex`, `to_agent: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`.
