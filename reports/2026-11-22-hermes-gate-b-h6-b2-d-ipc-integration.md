---
id: hermes-gate-b-h6-b2-d-ipc-integration-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-D — xác thực Unix IPC tích hợp vào Guard/writer

**ACKNOWLEDGED / H6_B2_D_CODE_MOCK_PASS / VERIFIED_OFFLINE_MOCK.** Phê duyệt `536632879e764befd26c5209842bf365aed49d6e`, ACK AGENTS, Workflow §§7–10, repository security, STATE, CATALOG, hồ sơ Codex, toàn bộ task và ADR-P0-003 tại `8fc3cdaeda27c7d78bdb5acc3a4bade1dba0aabf`. Workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. Task blob của base trùng commit phê duyệt. Review dùng bằng chứng B2-C tại `bca741f`. [Review B2-C](2026-11-22-hermes-gate-b-h6-b2-c-chatgpt-review.md).

## Thay đổi đã kiểm

B2-C chứng minh mô hình trong test fixture. B2-D chạy trực tiếp [Guard](../sandbox/p0-hermes-gate-a/guard.py), [writer](../sandbox/p0-hermes-gate-a/h6_writer.py) và [module IPC v2](../sandbox/p0-hermes-gate-a/h6_ipc_auth.py). Guard bật qua `TTD_H6_B2_D_SOCKET` tại đúng socket B2-D, và writer bật qua `--b2-d-mock`. Mặc định tắt. Cấu hình trộn socket Stage A hay đường ledger mock trước đó bị từ chối lúc khởi động. B2-D có một giao thức riêng trên socket riêng, không có fallback sau lỗi xác thực. Các suite legacy kiểm lại hành vi Stage A/B2-A trên mã dùng chung.

Cả hai đầu kiểm `SO_PEERCRED` (UID/GID `0:0`). Mỗi kết nối `SOCK_SEQPACKET` dùng hai nonce ngẫu nhiên 32 byte. HMAC-SHA256 kết hợp domain/version, nhãn vai trò writer challenge / Guard request / writer reply và cả hai nonce. Request dùng bytes JSON chuẩn hóa. Reply có chữ ký ràng buộc cả digest của request và toàn bộ kết quả, nên ACK từ request khác hoặc response v1 đều bị từ chối. So sánh chữ ký constant-time. Giới hạn 4.096 byte mỗi gói và deadline I/O cho một phiên là 4 giây. Dispatcher hiện hữu giới hạn thao tác vào snapshot/admit/settle trên fixture có marker và kill switch ON. ACK thành công chỉ gửi sau khi hoàn thành commit bền vững của H6.

Writer yêu cầu đúng thư mục ledger giả `0700` và ledger/lock có sẵn `0:0 0600`. Hai tiến trình đọc khóa IPC nhị phân đúng 32 byte từ file `0:0 0400` trong thư mục `0700` mount RO. Nguồn tạo khóa dùng random riêng cho runtime và test. File symlink, sai kiểu/mode/độ dài hoặc mount RW bị từ chối. Sentinel khóa provider được kiểm tra theo sự hiện diện, không đọc giá trị. Standalone Compose render trước khi chạy, không dùng base live. Inspect xác nhận hai service `0:0`, cap_drop ALL, no-new-privileges, rootfs RO, network none, không ports, không Docker socket hoặc credential provider. Writer có đúng bind RW `rprivate` của thư mục ledger giả và socket directory RW. Guard có socket/auth RO, không mount ledger. [Compose](../sandbox/p0-hermes-gate-a/compose.h6-b2-d-mock.yaml) · [Runner PowerShell 7](../sandbox/p0-hermes-gate-a/run_h6_b2d_mock.ps1).

## Kết quả trên Docker Desktop Linux

| Phép thử | Kết quả |
| --- | --- |
| Entrypoint và key isolation | Guard `/healthz` nhận snapshot đã ký từ writer khác container. Key vắng, ngắn, dài, sai mode, symlink, mount RW và sentinel provider đều FAIL CLOSED. Ledger thiếu marker và lock sai mode bị từ chối trước listen. UID 0 sai GID bị chặn dù thấy đúng file khóa. Guard trả 503 khi writer dừng. |
| Sai MAC, tamper và replay | Peer cùng UID/GID với key sai, reflection proof khác vai trò, signed packet cũ trên challenge mới, request bị sửa, gói quá cỡ, version sai và JSON duplicate/nonfinite/quá sâu đều bị chặn. Guard chặn writer proof sai, ACK thiếu MAC/v1, ACK bị sửa và ACK ký cho request khác. Không ghi ledger qua các RPC bị chặn. Challenge bỏ trống hết hạn, writer tiếp tục trả snapshot. |
| Guard HTTP và Level 2 | Một request test hợp lệ đi qua Guard, dự trữ trước khi gọi stub HTTP loopback, và settlement qua IPC đã ký. Adapter Level 2 nguyên bản và writer UID 0 cạnh tranh trên cùng device/inode của lock của ledger giả. **1/4 signed ACK**, cả hai cập nhật còn nguyên, inode lock ổn định, pathname ledger chuyển inode và fd cũ đọc bytes cũ. |
| Crash, restart và rollback | Thoát trước rename giữ nguyên bytes. Thoát sau file+directory fsync giữ phần ghi ở `inflight`. Cả hai ca trả 503, mất ACK và có 0 lượt gọi stub. Restart từ chối replay; stop writer giữ nguyên bytes, inode ledger và inode lock. Compose teardown kiểm 0 tài nguyên project còn lại và xóa thư mục giả. |
| Kiểm hồi quy | Stage A PASS 8 ca và B2-A PASS 14 ca từ chối, 2 crash, 4 admission đồng thời. B1 KVM2 và B2-C là bằng chứng lịch sử đã nghiệm thu. |

Tái lập mock từ repo root với `pwsh -NoProfile -File sandbox/p0-hermes-gate-a/run_h6_b2d_mock.ps1`. Engine 29.4.3, Compose 5.1.4, image Python ghim digest và không pull khi chạy. [Evidence JSON và source blobs](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-d-ipc-integration.json).

## Giới hạn và quyết định kế tiếp

Kết quả xác nhận IPC source trên Docker local và process crash. KVM2/ext4, mất điện, lưu trữ/rotation credential thật và live ledger mount chưa được nghiệm thu. Deadline IPC giới hạn thời gian chờ của peer. Sau khi writer vào giao dịch, `flock` có thể giữ writer lâu hơn deadline. Khi mất ACK, Guard fail closed và giữ trạng thái ghi để đối soát. Level 2 hiện thiếu fsync thư mục. UID 0 bỏ caps vẫn có quyền owner trong thư mục được bind. Tiến trình chiếm Guard hoặc writer có thể sử dụng khóa trong phạm vi đầu cuối đó, và host root/Docker daemon nằm ngoài ranh giới HMAC.

ChatGPT bắt đầu review tại module IPC và các source blob đã pin, đối chiếu mount render và cửa sổ crash. Một gate KVM2 sau này cần approval riêng và diff chính xác: giữ writer UID/GID `0:0` cùng caps=0, một directory bind RW `rprivate` cho ledger đã duyệt, private IPC writer RW/Guard RO, khóa riêng mount RO, và gỡ ledger bind của Guard. Xác minh trước khi apply về UID/userns/ACL, source/device/inode lock, Level 2 restart và giới hạn file trong thư mục. Dùng backup H4 đã kiểm B2-B để render sẵn rollback. Cấp khóa mới qua luồng bảo mật riêng, lưu root-only ngoài Git, thống nhất rotation bằng cách ngừng nhận việc, kiểm transaction đang chạy, thay khóa đồng bộ và kiểm lại snapshot. Khi rollback cần cô lập writer, khôi phục config đã kiểm và giữ nguyên ledger/lock. Kết quả ghi chưa rõ phải được đối soát trước mọi lần tiếp theo.

`from_agent: codex` · `next_owner: chatgpt` · `handoff_state: PREPARED_FOR_OWNER_FORWARD`. Live apply giữ `BLOCKED_UID_OR_MOUNT`, paid GATE B giữ `BLOCKED_PREFLIGHT`. Có 0 thao tác KVM2, ledger/lock hay permit thật, provider, paid và production.
