---
id: hermes-gate-b-guard-mount-results-2026-11-22
type: report
status: complete
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
source: live-kvm2-web-terminal
task_id: ttd-hermes-gate-b-001
owner: codex
---

# GATE B — Nghiệm thu Guard-only mount

**GUARD_MOUNT_PASS** trên KVM2 sandbox ngày 2026-11-22 ICT. Codex thực hiện đúng một lần recreate service `guard` với overlay H4. Docker kiểm tra toàn bộ container và xác nhận chỉ Guard có bind mount credential, ở chế độ chỉ đọc. GATE B paid tiếp tục `BLOCKED_PREFLIGHT`. [Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-guard-mount.json).

## Phạm vi và preflight

Codex nhận chỉ thị `cc88484` qua chat và đối chiếu quy tắc mục 7–9, task, ADR cùng bằng chứng tại base `4253e0c6bf1b6de1aac3ce84bba45d2896179d3b`. Kết nối tab qua tiện ích Chrome đã khôi phục quyền thực thi Web Terminal và xác nhận đúng sandbox. Tái sử dụng H3 mock E2E, H4 fake-key và chỉ kiểm lại các cổng liên quan đến recreate. [H3](2026-11-21-hermes-gate-b-h3-preflight.md) · [H4](2026-11-21-hermes-gate-b-h4-key-input-preparation.md).

- Compose `v5.6.1`. Render toàn bộ base và base + overlay khớp sau khi loại đúng bind mount mới của Guard. Đối chiếu với container đang chạy qua project/service/config hash, image, entrypoint, command, mount, network, port và giới hạn tài nguyên. File staging là regular file root-owned mode `0600` và chưa có mount. Không truy cập nội dung credential.
- Backup base, overlay và metadata mount trong thư mục riêng trên VPS. Hai file Compose khớp backup từng byte. Dry-run apply và rollback chỉ nhắm Guard. So sánh lại file trước apply. Lệnh thực thi dùng `up -d --no-deps --force-recreate --no-build --pull never --wait` với đúng một service `guard`.
- Lượt probe HTTP đầu tiên thiếu dấu phân cách port và chạm nhầm loopback port 80. Lượt đo với đúng endpoint trả 200 cho cả hai production service trước recreate. Ledger dùng mount chỉ đọc, có 1 attempt, 0 one-shot permit và kill switch ON. Kiểm trên `one_shot_permits` và các task record.

## Nghiệm thu

| Hạng mục | Kết quả live |
| --- | --- |
| Mount và container | Một bind mount H4 chỉ đọc ở Guard. Các mount cũ giữ nguyên. ID Guard thay đổi, các container khác giữ nguyên ID, trạng thái running, thời điểm khởi động, restart count và port bindings. |
| Guard và proxy | Cả hai healthy. Guard nhận HTTP 200 từ proxy health. Mạng riêng vẫn internal, chỉ có Guard và proxy, cùng network IDs như baseline. |
| Cách ly proxy | Sáu container đối chứng bị chặn qua DNS alias và hai IPv4 của proxy, 18/18 phép thử mỗi lượt trước và sau. |
| Production | n8n và Hermes đều HTTP 200 trước và sau. Restart count 0 cho cả hai. |
| Compose và tài nguyên | Base và overlay khớp từng byte với backup. SHA-256 base trước/sau `c3a5234f556abaf531849fdd377c87815e6c39c8aed7afe55c364da9e324abb2f`. Guard giữ giới hạn CPU/RAM/PID, root filesystem chỉ đọc và không publish port. |
| Ledger và chi phí | Ledger khớp từng byte, 1 attempt lịch sử, 0 permit, kill switch ON. 0 provider requests và 0 USD phát sinh trong bước mount. |

Terminal trả `MOUNTED_INVARIANTS_PASS`, `NETWORK_PASS` và `GUARD_MOUNT_PASS`. Rollback đã dry-run và không cần áp dụng. Guard tiếp tục upstream mock. Project, quyền Responses, billing và input-token count thuộc bước provider preflight riêng.

**Bàn giao** cho ChatGPT nghiệm thu qua GitHub, `PREPARED_FOR_OWNER_FORWARD`.
