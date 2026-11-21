---
id: hermes-gate-b-h6-b2-c-uid-model-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-C — quyền writer và xác thực Unix socket

**ACKNOWLEDGED / H6_B2_C_UID_MODEL_OFFLINE_PASS / VERIFIED_OFFLINE_MOCK.** Đề xuất writer UID/GID `0:0`, bỏ toàn bộ Linux capabilities, cùng khóa IPC riêng và xác thực hai chiều. Giữ trạng thái apply `BLOCKED_UID_OR_MOUNT` của B2-B và paid GATE B `BLOCKED_PREFLIGHT` cho đến quyết định riêng của ChatGPT.

## Phạm vi và nguồn đối chiếu

- Phê duyệt `f9ce46fbc234b5a554a27a78d759d99182156617`. Codex ACK toàn bộ task và bộ quy tắc tại `fa0b2bc926026761aa7b26b3fe5e5855071c95cc`, gồm AGENTS, Workflow §§7–10, Repository Security, STATE, CATALOG và hồ sơ Codex. Workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`, §10 ở commit `c915618`. Task tại base khớp blob tại commit phê duyệt.
- Dùng lại Stage A/B1/B2-A cho các phần ngoài thay đổi UID/IPC và phép đo KVM2 từ B2-B. Kiểm mới trên Docker Desktop Linux Engine 29.4.3, Compose 5.1.4, bằng dự án ngẫu nhiên riêng. Ba file triển khai chỉ dành cho fixture, gồm [Compose](../sandbox/p0-hermes-gate-a/compose.h6-b2-c-fixture.yaml), [test](../sandbox/p0-hermes-gate-a/h6_b2c_identity_test.py) và [runner PowerShell 7](../sandbox/p0-hermes-gate-a/run_h6_b2c_fixture.ps1). Lệnh tái lập tại repo root là `pwsh -NoProfile -File sandbox/p0-hermes-gate-a/run_h6_b2c_fixture.ps1`, dùng image ghim sẵn với `pull_policy: never`. [Review B2-B](2026-11-22-hermes-gate-b-h6-b2-b-chatgpt-review.md) · [Evidence B2-C](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-c-uid-model.json).
- Render trước khi start. Runner kiểm source RO theo từng file, bind đúng thư mục tạm Windows riêng và đúng project volumes. Thử ban đầu bằng volume Linux cũng PASS. Docker Desktop từ chối bind `rprivate` từ dưới daemon root và daemon không thấy thư mục tạm nội bộ của distro WSL. Phương án cuối đã chạy đủ matrix với bind RW `rprivate` của đúng thư mục ledger giả trên Docker Desktop. Nhánh thử ACL dùng volume Linux của project.

## Kết quả

| Kiểm tra | Đo được |
| --- | --- |
| DAC và isolation | Parent `0:0 0700`, ledger/lock `0:0 0600`, ACL vắng. Writer `0:0`, `CapInh/Prm/Eff/Bnd/Amb=0`, `NoNewPrivs=1`, rootfs RO, chỉ loopback, không ports, Docker socket hay provider secret. Các mount RW đúng một bind ledger `rprivate` và volume IPC. Khóa HMAC tạm được mount RO vào writer/Guard, độc lập với dữ liệu hay khóa provider. |
| Unix IPC | Guard giả chạy `0:0`, kết nối qua socket `0600` trong thư mục `0700` mount RO. Cả hai đầu kiểm `SO_PEERCRED`. Peer trùng UID/GID vượt qua kiểm kernel nhưng thiếu khóa nên bị chặn trước dispatch. Peer UID 0 sai GID bị từ chối dù có khóa. Container thiếu mount không tìm thấy socket. Guard từ chối khi proof writer không khớp. Gói đã bắt từ phiên trước bị từ chối với challenge mới. |
| Phạm vi request | HMAC-SHA256 dùng nhãn vai trò, nonce ngẫu nhiên hai phía và ràng buộc nội dung request. Dispatcher fixture hiện hữu từ chối `write` tùy ý, thêm `path` vào admission và sai fingerprint. Snapshot trước/sau các request sai giống nhau. |
| Lock / Level 2 | Hai container thực thi adapter Level 2 và dispatcher H6 hiện hữu. H6 thấy `flock(LOCK_NB)` bị chặn trên đúng device/inode Level 2 đang giữ. Sau khi nhả lock, đúng **1/4 ACK**. Cả hai cập nhật còn trong ledger. Lock inode giữ nguyên, pathname ledger trỏ inode mới, file descriptor cũ vẫn đọc bytes cũ. |
| Crash / replay / rollback | Hai fault injection thoát process trước rename và sau file+directory fsync đều mất ACK. Ca trước rename giữ bytes cũ và chỉ được nhận một lần ở bước recovery giả có chủ đích. Ca sau fsync giữ trạng thái `inflight`, replay bị từ chối và không đổi bytes. Restart writer thật trong fixture từ chối replay. Stop writer rồi chạy verifier Level 2 kiểm bytes/inodes vẫn khớp, sau đó dọn project, volumes, container và thư mục giả. |
| UID `23062` và ACL | Không ACL thì không traverse/read/open lock/create. ACL theo UID cho mở ledger/lock, đổi mode hiệu dụng từ `0700/0600` sang `0770/0660` do mask. Writer vẫn lỗi `fchmod` vì lock thuộc root. Level 2 vẫn giữ lock inode nhưng `fchmod(0600)` xóa quyền ACL hiệu dụng, và `os.replace` tạo ledger mới `0600`. Default ACL cũng mất hiệu lực với đường ghi hiện tại. |

## Đánh đổi và quyết định tiếp theo

UID 0 bỏ caps tương thích với quyền sở hữu hiện tại. Tiến trình bị chiếm quyền vẫn có quyền sửa các file trong chính thư mục ledger RW. Cần giữ allowlist mount/entrypoint, socket và khóa IPC chỉ hiện diện ở hai đầu, cùng giới hạn thao tác ở dispatcher. Guard bị chiếm quyền có thể dùng khóa IPC trong phạm vi Guard. Quyền host root hoặc quyền Docker daemon nằm ngoài mô hình cô lập. UID riêng với ACL đòi thay cả hợp đồng lock và publish giữa hai writer, bao gồm ownership từ `os.replace`, thiết kế mode/mask khi tạo file và tương thích Level 2. ACL-only bị loại cho phiên bản hiện tại.

Kết quả là bằng chứng trên Docker Desktop, gồm Windows-backed bind và POSIX ACL trên volume Linux. Chưa chứng minh KVM2/ext4 runtime, Guard binary live hay phục hồi mất điện. Nhận xét B2-A về Level 2 thiếu fsync thư mục vẫn áp dụng. Thoát tiến trình kiểm cửa sổ ACK, còn kiểm mất điện cần gate riêng nếu được yêu cầu. [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/) · [Docker volumes](https://docs.docker.com/engine/storage/volumes/).

**Rà soát trước khi đề nghị apply riêng.** ChatGPT bắt đầu từ JSON và ba Git blob của fixture. Nếu chấp nhận mô hình, duyệt riêng bản tích hợp Guard/writer và Compose diff chứa đúng writer UID 0, một bind RW thư mục ledger `rprivate`, socket riêng writer RW/Guard RO, khóa IPC RO riêng và bỏ mount ledger trực tiếp của Guard. Xác minh lại mount source, userns, UID/mode, lock device/inode, tập file trong thư mục, vùng ảnh hưởng, process/capabilities, đường IPC và trạng thái restart Level 2 ở gate phù hợp. Giữ hai Compose backup H4 đã kiểm từ B2-B và render diff roll-back trước apply. Nếu dừng sau một kết quả ghi thực tế chưa rõ, cô lập writer, giữ nguyên bytes và inode lock và đối soát trước mọi quyết định tiếp theo. Không chép snapshot cũ đè ledger đã ghi.

`from_agent: codex` · `next_owner: chatgpt` · `handoff_state: PREPARED_FOR_OWNER_FORWARD`. B2-C có 0 thao tác KVM2, ledger/lock thật, permit thật, provider, paid và production.
