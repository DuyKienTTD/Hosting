---
id: hermes-gate-b-h6-stage-b1-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 Stage B1 — Diễn tập mock trên KVM2

**H6_STAGE_B1_PASS / VERIFIED_KVM2_MOCK / ROLLBACK_PASS.** Codex ACK phê duyệt `6e5ee58c2f1d0ceec84c8effbc749de1f2e20c97`, quy tắc và task tại `5a068eee7870044a55753cdf875a594187f64e02`. Phiên Chrome Web Terminal có quyền chạy Docker trên KVM2. B1 sử dụng đúng phạm vi Compose mock riêng, với ledger/token/IPC giả. Paid GATE B tiếp tục `BLOCKED_PREFLIGHT`. [Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-h6-stage-b1.json).

## Cổng kiểm trước khi chạy

- Stage A runtime source giữ ở `a411114d0b485729a57d43eaf97fd2a5226d1585`. Runner đối chiếu SHA-256 của 10 file nguồn trước khi import hoặc render. KVM2 dùng Docker Engine 29.9.2 và Compose 5.6.1. Image Hermes đã pin digest có sẵn, không pull hoặc rebuild. Overlay B1 dùng tmpfs cho `/opt/data` vì image khai báo VOLUME tại đó. [Runner tại commit đã chạy](https://github.com/DuyKienTTD/Hosting/blob/7a03aeb8bd04745dfb9d928efeba5ed7f931ce9f/sandbox/p0-hermes-gate-a/h6_b1_rehearsal.py) · [Overlay B1](../sandbox/p0-hermes-gate-a/compose.h6-b1.yaml) · [Manifest nguồn](../sandbox/p0-hermes-gate-a/h6_b1_source.json).
- Render tất cả profile cho project `ttd-h6-b1-t_ajwp9k`. Kết quả đúng ba service Guard/writer/mock, một network internal mới, writer `network_mode: none`, 13 bind mount chỉ trong fixture/source B1, một tmpfs `/opt/data` cho mỗi service và không publish port. Đối chiếu source, target, mode, cấu hình service, entrypoint, healthcheck, UID/GID, cấu hình image và tên project/container/network/volume với inventory. Không trùng với chín container và 11 network hiện hữu. Kiểm hash render và baseline lại ngay trước `up`.
- Hai điểm tương thích làm dừng các phép kiểm trước `up`: Compose 5.6.1 giữ khóa extension YAML trong JSON, còn image inspect bỏ hẳn trường `ExposedPorts` khi trống. Đã sửa phép kiểm cho hai biểu diễn này và xác minh lại. Chỉ có một lần `up` sau khi tất cả cổng đạt.

## Nghiệm thu mock và rollback

| Hạng mục | Kết quả |
| --- | --- |
| Render so với runtime | **PASS.** Docker inspect khớp image, entrypoint, healthcheck, UID, network và bind mount đã duyệt. Chỉ Guard và mock thuộc network B1. Writer chỉ có loopback, socket `23062:23060` mode `0660`. Guard có mount IPC chỉ đọc. |
| No-bypass | **PASS.** Mỗi service bị chặn tới hai địa chỉ của proxy hiện hữu, tổng 6/6 phép thử TCP âm tính. Guard và mock không có IPv4 default route. Cả ba service không thấy provider credential hay ledger thật. Writer không thấy cả token giả. Mock không thấy socket. |
| Guard/writer/mock trên Compose | **PASS.** Tám request đồng thời tạo đúng một HTTP 200 và bảy từ chối, mock ghi nhận đúng một lượt. ID phản hồi mock khớp hash của canonical wire. Request thiếu auth, tamper và replay bị từ chối. File descriptor cũ vẫn đọc fixture trước replace trong lúc file theo đường dẫn hiện hành ghi usage, reserve 0,007 USD và permit đã consume. Restart writer giữ nguyên bytes fixture sau commit và tiếp tục chặn replay. |
| Ma trận lỗi và callback | **PASS 8/8** trong container B1 riêng `--network none` trên cùng KVM2, dùng cùng source/image. Shared lock trên ledger giả, IPC peer, concurrent dispatch, crash trước commit và sau commit trước ACK, thiếu terminal SSE, short body, timeout, redirect và replay đều đạt. Hai ca crash gửi 0 lượt. Callback HTTP 200 dùng handler bridge thật với Hermes giả và webhook n8n giả có xác thực. Lượt replay không sinh callback thứ hai. |
| Rollback và kiểm sau dọn | **PASS.** Dọn đúng ID container và network B1 theo nhãn, tên và mount đã đối chiếu. Xóa fixture và các thư mục staging B1 riêng. Kiểm lại không còn runtime B1 hay volume mới. So sánh snapshot pre/post xác nhận container, mount, network, cổng và restart của stack hiện hữu giữ nguyên. Production n8n/Hermes HTTP 200/200, restart 0/0. Ledger thật khớp từng byte với baseline, 1 attempt lịch sử, 0 permit live và kill switch ON. |

Terminal ghi `B1_RENDER_GATE_PASS`, `B1_MOCK_RUNTIME_PASS`, `B1_ROLLBACK_PASS`, `B1_POSTCHECK_PASS` và exit code 0. B1 có **0 lượt gọi provider, 0 paid attempts, 0 thao tác permit thật, 0 USD phát sinh**.

## Bàn giao

`from_agent: codex`, `to_agent: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`. ChatGPT review kết quả B1 mock. B2 cần phê duyệt riêng cho thay đổi ledger thật hoặc provider transport. Stage C cần quyết định riêng và các gate của ADR-P0-003. B1 kiểm Guard/writer/mock và callback mô phỏng, chưa diễn tập Hermes đích, writer ledger thật hoặc tuyến provider.
