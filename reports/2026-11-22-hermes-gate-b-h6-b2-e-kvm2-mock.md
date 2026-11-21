---
id: hermes-gate-b-h6-b2-e-kvm2-mock-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-E — rehearsal HMAC v2 trên KVM2

**ACKNOWLEDGED / H6_B2_E_KVM2_MOCK_PASS / VERIFIED_KVM2_MOCK / ROLLBACK_PASS.** Phê duyệt `bf99bf42d1c9fd7cf7871b0c279c0f747e774867`. ACK AGENTS, Workflow §§7–10, Repository Security, STATE, CATALOG, hồ sơ Codex, toàn bộ task và ADR-P0-003 tại `8ad3ce0991258822d99486ddf4f4b301a3f8bf1c`. Workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. Task blob trùng phê duyệt. [Review B2-D](2026-11-22-hermes-gate-b-h6-b2-d-chatgpt-review.md).

## Cổng pre-up và phạm vi

- Dùng Web Terminal KVM2 đã đăng nhập, Docker Engine `29.9.2`, Compose `5.6.1`. GATE A running, Level 2 thật stopped, production n8n/Hermes health `200/200`. Kiểm trực tiếp mode/owner/ACL và device/inode của parent, ledger và lock thật. Các phép đo phù hợp với B2-B. Chỉ đọc metadata, không mở ledger, permit hoặc credential thật. Hai file backup H4 khớp byte, render và hash cấu hình Guard hiện hữu.
- Guard, writer, auth module, test và Compose B2-D ghim từ `cf36e59`. [Runner](../sandbox/p0-hermes-gate-a/h6_b2e_rehearsal.py) và [test ext4/callback](../sandbox/p0-hermes-gate-a/h6_b2e_contract.py) chạy tại `d32aff1`. Xác minh runner SHA-256 và 12 Git blob được tải từ nguồn ghim. Python image của B2-D vắng trong cache KVM2, nên dùng image Hermes ghim digest đã dùng ở B1, ghi đè entrypoint bằng `python3 -B`, che volume mặc định của image bằng tmpfs riêng và đặt pull policy `never`.
- Render standalone tất cả profile cho đúng 4 service và 4 volume riêng. Không có network mới, external volume, port publish, credential provider hay bind của dự án cũ. Pre-up đối chiếu toàn bộ command/entrypoint, healthcheck, UID, capabilities, rootfs, env, volume/mount và propagation với danh sách cho phép, kiểm xung đột với inventory hiện hữu, rồi render lần hai và so sánh nguyên bytes trước khi start. Render SHA-256 của lần PASS được ghi trong [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-e-kvm2-mock.json).

## Kết quả trên KVM2

| Kiểm tra | Bằng chứng |
| --- | --- |
| Runtime và no-bypass | Guard và writer healthy. PID thật đều UID/GID `0:0`, CapEff/Prm/Inh/Bnd/Amb bằng 0, NoNewPrivs bằng 1, rootfs RO. Cả hai dùng `network_mode: none`, chỉ loopback, không default route. Writer có bind ledger giả ext4 `rprivate` với parent `0700`, ledger/lock `0600`. Guard không có mount ledger, key IPC `0400` mount RO, socket `0600` qua directory mount RO. Cả hai không thấy ledger thật, provider credential hoặc Docker socket trong namespace. |
| Peer và HMAC v2 | Guard thật nhận snapshot có chữ ký từ writer container. UID 0 sai GID bị chặn dù file khóa hiện diện. Sai khóa, thiếu socket, nonce replay, reflection, request bị sửa, sai phiên bản, gói quá cỡ và JSON sai bị từ chối. Guard từ chối proof writer sai và ACK thiếu chữ ký, kiểu cũ, bị sửa hoặc ký cho request khác. Challenge bỏ trống hết hạn. |
| Ext4 và Level 2 | Adapter Level 2 nguyên bản được chạy trên dữ liệu giả trong harness. Quan sát tranh chấp trên cùng device/inode lock, đúng **1/4 signed ACK**, hai cập nhật cùng tồn tại và trường chưa biết được giữ nguyên. Lock inode ổn định, ledger được replace, và fd cũ đọc đúng bytes cũ. Restart writer giả từ chối replay. |
| Crash và callback | Thoát trước rename và sau file + directory fsync đều mất ACK, trả 503 và có 0 lượt gọi stub. Ca trước rename giữ bytes cũ, ca sau fsync giữ bản ghi `inflight`. Đường HTTP hợp lệ chạy đúng bytes đã freeze và ký settlement. Ca callback dùng handler bridge thật, Hermes/n8n mô phỏng qua loopback, có đúng một mock dispatch và một webhook xác thực. Replay không phát thêm callback. |
| Rollback | Kiểm bytes và inode đã commit trên ledger giả trước khi dọn. Chỉ gỡ tài nguyên có tên, nhãn, ID và mount đã chứng minh thuộc B2-E. Không còn container, volume, network hoặc thư mục fixture. Inventory container, trạng thái, thời điểm start, restart count, mount, network, port và volume hiện hữu khớp pre/post. Production health vẫn `200/200`. Metadata, device/inode và ACL của ledger/lock thật khớp pre/post. |

Lần kiểm runtime đầu dừng và tự dọn vì cách kiểm từ host đi theo symlink tuyệt đối `/var/run` trỏ về `/run` của host. Runner cuối chuyển phép kiểm vào namespace mock và xác nhận cả hai đường dẫn Docker socket đều vắng. Topology giữ `network_mode: none`, nên bằng chứng no-bypass là trạng thái mạng và mount thực đo, không thực hiện lại các probe TCP của B1.

## Bàn giao

`from_agent: codex` · `next_owner: chatgpt` · `handoff_state: PREPARED_FOR_OWNER_FORWARD`. ChatGPT bắt đầu từ evidence và runner đã ghim. Phạm vi đã chứng minh là IPC, hành vi filesystem ext4, mock callback và rollback KVM2. Tính bền vững qua mất điện và đường thực qua Hermes/n8n/provider chưa được kiểm.

Live shared-ledger apply giữ `BLOCKED_UID_OR_MOUNT` và paid GATE B giữ `BLOCKED_PREFLIGHT`. Một gate tích hợp thật sau này cần diff riêng cho bind ledger RW chỉ ở writer, private IPC và khóa mới RO chỉ ở hai đầu, gỡ bind ledger của Guard, và xác minh lại UID/userns, chế độ lock, Level 2 restart, drift và backup H4 trước apply. Rollback phục hồi cấu hình đã duyệt và giữ nguyên dữ liệu ledger/lock đã commit. Với ACK mất, đối soát trước mọi hành động tiếp theo. Trong B2-E có 0 lần đọc nội dung hoặc sửa ledger/lock thật, 0 thao tác permit thật, 0 provider hoặc paid attempt và 0 thay đổi production.
