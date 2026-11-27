---
id: hermes-gate-b-h6-b2-a-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 Stage B2-A — Tương thích ledger Level 2/P0 offline

**H6_B2_A_COMPLETE / VERIFIED_OFFLINE_LEDGER_COMPATIBILITY.** Codex ACK giao việc `8d705b0640a45645bb26b5978286170754c49311`, quy tắc và task trên `main` tại `da79cc95c7fcc274b025b338c1c00e3c81a467da`. Quy tắc §10 được ghi tại `c915618468f1bb6c8238f6a8aefd6597ca92ac1b`. Phiên có Git và Docker Linux cục bộ, kiểm thử bằng container chỉ có loopback, filesystem root chỉ đọc và ledger tạm trên tmpfs. Paid GATE B giữ `BLOCKED_PREFLIGHT`. [Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Diff code](https://github.com/DuyKienTTD/Hosting/commit/1caf0961898452a08abbecd027de552ed4e4ef3f) · [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-a.json).

## Code và kết quả kiểm thử

- Dùng một bộ đọc JSON v1 cho snapshot và giao dịch dưới lock. Nó mở lại đường dẫn ledger hiện hành sau atomic rename, giới hạn kích thước, từ chối symlink và file bất thường, JSON lỗi, key trùng, số không hữu hạn, sai phiên bản và ngân sách không nhất quán. Ghi vẫn dùng inode `.json.lock` ổn định của Level 2. ACK admission chỉ tới sau fsync file tạm, rename và fsync thư mục. [Writer](../sandbox/p0-hermes-gate-a/h6_writer.py) · [Ledger](../sandbox/p0-hermes-gate-a/one_shot.py).
- Giao diện IPC giữ `snapshot/admit/settle` và kiểm peer UID/GID hai chiều. Admission và settlement vẫn yêu cầu marker `h6_stage_a_fixture` trên tuyến IPC. Settlement mock ràng buộc đúng task/digest/permit đã consume và khoản dự trù. Lặp cùng kết quả giữ nguyên bytes. Kết quả xung đột bị từ chối. Cả `usage_recorded` và `outcome_unknown` giữ reserve và không tăng actual spend. Không có chế độ live trong patch.

| Kiểm thử | Kết quả |
| --- | --- |
| Tương thích P0 v1 và lock | **PASS.** Fixture được tạo bởi `admit`, `update_task` và `locked_ledger` của adapter Level 2 nguyên bản. Writer H6 thực sự chờ khi Level 2 giữ lock. Một trong bốn admission nhận ACK. Inode lock giữ nguyên, inode ledger đổi và Guard đọc được snapshot mới. Cập nhật actual giả của Level 2, task cũ và trường mở rộng ở cấp ledger, task, ngày và permit đều được giữ. |
| Crash, replay, settlement | **PASS.** Crash trước fsync giữ nguyên fixture. Crash sau durable commit nhưng trước ACK để lại `inflight`, permit đã consume và reserve vẫn còn. Cả hai ca nhận 0 ACK. Restart chặn admission lặp. Settlement mock đã xác nhận và settlement không rõ kết quả đều lặp an toàn qua restart, giữ reserve. |
| Từ chối dữ liệu và peer | **PASS.** 14 ca từ chối bao gồm thiếu/hỏng ledger, key trùng, số tràn, schema sai, thiếu marker, kill switch sai, vượt cap, nhiều permit, digest sai và symlink. Peer sai UID/GID và writer giả bị chặn. Không có kết nối mạng ngoài loopback trong container test. |
| Hồi quy có liên quan | **PASS.** Stage A mock 8/8, `one_shot_linux_test.py` với 16 fault cases, `one_shot_interop_test.py` và `mock_contract_test.py`. Chạy lại vì chúng dùng bộ đọc và giao dịch ledger đã sửa. Tái sử dụng chứng cứ KVM2 B1 cho topology không đổi. |

Tái lập trên Linux trong container `--network none` với mã nguồn chỉ đọc, từ thư mục `sandbox/p0-hermes-gate-a` chạy `python -B h6_b2a_ledger_test.py test ../p0-level2/adapter.py`. Harness cần root trong container để khởi tạo fixture với UID riêng rồi hạ quyền các process con. Số token trong fixture được tạo để thử cap và scope, không dùng làm số đếm của provider.

## Compose và kế hoạch kiểm B2-B

Diff rendered Compose của B2-A so với đầu vào B1 là **0 thay đổi**. Ba file Compose có bytes giống `7a03aeb`. Render offline với mọi profile vẫn chỉ có Guard, writer và mock, một mạng internal, writer `network_mode: none`. Guard chỉ gắn IPC `/opt/ttd/h6-ipc` ở chế độ đọc, còn writer gắn IPC và thư mục `/opt/ttd/mock-ledger` ghi được. [Overlay Stage A](../sandbox/p0-hermes-gate-a/compose.h6-stage-a.yaml) · [Overlay B1](../sandbox/p0-hermes-gate-a/compose.h6-b1.yaml).

1. ChatGPT nghiệm thu phiên bản này và quyết định phạm vi B2-B theo §10. Bước đầu của B2-B đề xuất là kiểm metadata mount, UID và lock trên KVM2 ở chế độ chỉ đọc, xác minh baseline/backup và render bản diff trước khi apply.
2. Delta dự kiến cho một bản tích hợp được duyệt là thay **duy nhất** bind fixture ledger của writer bằng bind thư mục ledger đã duyệt, gồm cả JSON và file lock cùng thư mục. Guard tiếp tục chỉ đọc qua IPC. Không cấp provider credential hoặc network cho writer. Cần thiết kế và review riêng cho đường dẫn live vì binary hiện tại chỉ nhận fixture. So sánh đầy đủ mount/UID/network/render với inventory trước khi cân nhắc khởi động.
3. Hai writer chạy cùng UID filesystem **23062** trong test. Level 2 tạo ledger và lock mode `0600`, nên cùng GID chưa đủ nếu khác UID. Trước bất kỳ apply nào, chứng minh UID mapping trên KVM2 hoặc duy trì một writer duy nhất và xác minh Level 2 không thể đồng thời ghi. Kiểm directory bind theo inode mới, lock ổn định, health, no-bypass và điều kiện dừng. Tránh dùng endpoint health của adapter Level 2 làm phép đọc ledger, vì nó đi qua hàm lock có ghi lại file.
4. Rollback dự kiến dừng writer mới và khôi phục code/Compose sandbox theo diff đã duyệt. Giữ nguyên ledger, lock, permit đã consume và reserve đã commit. Không chép bản backup đè lên ledger. Đối chiếu health và invariants sau rollback. Chưa có phép apply hoặc rollback B2-B trên KVM2.

**0 thao tác KVM2, ledger/lock hoặc permit thật, provider API, paid inference và production trong B2-A.** `from_agent: codex`, `to_agent: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`. ChatGPT nghiệm thu và chủ động quyết định bước an toàn kế tiếp theo §10.
