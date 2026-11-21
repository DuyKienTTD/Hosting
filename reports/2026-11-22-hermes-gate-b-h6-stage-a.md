---
id: hermes-gate-b-h6-stage-a-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 Stage A — Guard và ledger writer chạy mock

**H6_STAGE_A_COMPLETE / VERIFIED_OFFLINE_MOCK.** Codex ACK phê duyệt `c1fe91caa60904578c39b46bcb0cdeb1d5ee7319` theo quy tắc và task tại `cf72d4dc1b1d58b13a2d9c22818d5b43286cb93e`. Kiểm thử trên Docker Desktop Linux cục bộ, dùng Python 3.12 và ledger giả. Paid GATE B giữ `BLOCKED_PREFLIGHT`. [Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Thiết kế đã review](2026-11-22-hermes-gate-b-h6-chatgpt-design-review.md) · [Evidence và SHA-256 từng file](evidence/2026-11-22-ttd-hermes-gate-b-h6-stage-a.json) · [Diff đầy đủ của source](https://github.com/DuyKienTTD/Hosting/commit/a411114d0b485729a57d43eaf97fd2a5226d1585).

## Thay đổi được kiểm thử

- Guard ở chế độ Stage A chỉ gửi tới mock. Guard khóa đúng một turn văn bản, bỏ `prompt_cache_key` động, áp cap 600 và đóng băng canonical bytes. Scope kiểm task, mock idempotency hash, model, digest và số input tokens giả đã gắn với permit. Guard chỉ gửi đúng một buffer sau ACK durable. Mất ACK thì fail closed. [Guard](../sandbox/p0-hermes-gate-a/guard.py) · [Admission](../sandbox/p0-hermes-gate-a/one_shot.py).
- Unix socket dùng thư mục `0750`, socket `0660` và `SO_PEERCRED` hai chiều với UID riêng cho Guard và writer. Protocol v1 giới hạn packet 4 KiB và ba thao tác `snapshot`, `admit`, `settle`. Writer chỉ nhận ledger có đánh dấu fixture. Writer giữ nguyên inode của lock, fsync file tạm, atomic rename, fsync thư mục rồi mới ACK. Guard lấy snapshot mới từ writer thay cho bind mount theo file. [Writer](../sandbox/p0-hermes-gate-a/h6_writer.py).
- Overlay dành cho mock tách biệt. Guard chỉ mount IPC đọc, writer có quyền ghi IPC và thư mục ledger giả, `network_mode: none`, root filesystem chỉ đọc, không capabilities. Mock không thấy IPC. Render với mọi profile vẫn chỉ có Guard, writer và mock trên topology cô lập. Overlay đòi đường dẫn fixture riêng và không publish port. [Compose overlay](../sandbox/p0-hermes-gate-a/compose.h6-stage-a.yaml).

## Kết quả

| Phép kiểm | Kết quả |
| --- | --- |
| IPC và ranh giới container | **PASS.** Kiểm mode, UID/GID và peer hai chiều. UID sai cùng nhóm bị writer từ chối, nhóm sai bị quyền filesystem chặn, Guard từ chối writer giả trước khi gửi. Version sai, packet quá 4 KiB, key trùng, thao tác reset và trường ngoài contract đều bị từ chối. Hai container riêng với mạng `none` xác nhận kết nối đúng UID qua mount IPC chỉ đọc, UID khác bị chặn và client không thấy ledger. |
| Admission và exact bytes | **PASS.** Tám request đồng thời tạo đúng một dispatch mock. Mock thấy permit đã consume, task `inflight` và reserve tổng 0,007 USD trên fixture khi nhận đúng bytes. Tamper, replay, HTTP thiếu auth, tools, nhiều turn, content tool và số đếm giả trên cap bị chặn. Một phép đọc giữ inode cũ trong khi snapshot qua writer thấy inode mới. Hồi quy với adapter Level 2 xác nhận cùng lock inode và bảo toàn transaction của adapter. |
| Crash và kết quả không rõ | **PASS.** Writer chết trước commit làm 0 dispatch và attempts giữ 1. Writer chết sau fsync trước ACK làm 0 dispatch, giữ permit đã consume và reserve. Với thiếu terminal SSE, HTTP body ngắn, timeout hoặc HTTP 302, mỗi fixture ghi đúng một lượt mock, giữ reserve, báo `outcome_unknown`, không theo redirect và không retry. |
| Callback và phục hồi | **PASS.** Handler bridge thật gọi Guard qua Hermes giả rồi nhận HTTP 200 từ webhook n8n giả có xác thực. Callback thiếu auth trả 401. Replay bridge không tạo callback thứ hai. Restart writer trên cùng fixture giữ nguyên bytes ledger đã commit và tiếp tục chặn replay. Đây là rehearsal trên ledger giả. |
| Compose và hồi quy | **PASS.** Render offline bằng Compose 5.1.4, kiểm dịch vụ, UID, mounts, quyền và topology. Thiếu fixture root làm render thất bại. `mock_contract_test.py`, `one_shot_linux_test.py` và `one_shot_interop_test.py` PASS vì Guard/admission có delta. Tái sử dụng bằng chứng H3/H4/H5 ngoài phạm vi đó. |

Tái lập ma trận từ checkout trên Linux với Python 3.12 trong môi trường chỉ có loopback, chạy `python -B h6_stage_a_test.py` từ `sandbox/p0-hermes-gate-a`. Test cần harness root trong container để tạo process với UID khác nhau. Render bằng `docker compose -p h6-stage-a -f compose.yaml -f compose.h6-stage-a.yaml config` với `TTD_H6_FIXTURE_ROOT` trỏ đến fixture riêng. Bản render dùng image Hermes đã pin trong repository. Kiểm thử IPC chạy bằng image Python cô lập, không khởi động stack Compose Hermes.

## Bàn giao Stage B

**Đề xuất để chủ dự án quyết định sau ChatGPT review:** trước tiên chỉ apply Guard/writer sandbox cho diễn tập mock đã pin mã và overlay. Chốt ownership các thư mục fixture, đối chiếu UID mapping, render diff và dry-run chỉ service được duyệt, rồi kiểm no-bypass và health trước/sau. Thiết kế chuyển sang writer trên ledger thật, provider TLS transport/settlement thực và kiểm chứng digest H5 qua runtime đích cần thay đổi và nghiệm thu riêng. Stage A dùng digest của fixture mới, số đếm giả và webhook giả. Số 723 từ H5 vẫn thuộc request H5.

Rollback Stage B đề xuất vô hiệu tuyến mới, dừng writer theo phạm vi được duyệt, khôi phục source/Compose Guard đã backup và chỉ recreate Guard nếu được phê duyệt. Giữ nguyên ledger và toàn bộ permit/reserve đã ghi qua rollback. Kiểm lại health, mount cách ly và ranh giới mạng trước khi bàn giao. Dry-run và kiểm runtime KVM2 thuộc Stage B.

Stage A có **0 provider operations, 0 paid attempts, 0 permit thật, 0 USD phát sinh**. KVM2, ledger thật và production nằm ngoài môi trường đã thao tác. `from_agent: codex`, `to_agent: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`.
