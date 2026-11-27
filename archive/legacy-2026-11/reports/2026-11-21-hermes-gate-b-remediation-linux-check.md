---
id: hermes-gate-b-remediation-linux-check-2026-11-21
type: report
status: partial
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-guard-remediation-001
---

# GATE B remediation — kiểm thử Linux KVM2

Kết quả: **PARTIAL / LINUX_TRANSACTION_UNIT_PASS / GUARD_MOCK_E2E_PENDING**. Không có paid API call hoặc thay đổi production. Không tạo permit trên ledger thật.

Đã chạy mã tại commit `d08b7e5` trong thư mục tạm trên KVM2 Ubuntu 24.04.4, kernel `6.8.0-147-generic`, Python `3.12.3`. Test dùng ledger giả với baseline lịch sử 1 attempt, USD 0.0035 reserved và kill switch ON; không mở ledger thật cho test ghi. Lệnh `one_shot_linux_test.py` exit 0: 20 tiến trình tranh cùng file và lock inode, đúng 1 admitted, 19 rejected; reload/replay bị chặn, attempts 2 và reserved USD 0.007 trên **ledger copy**. Các ca kill switch OFF, vượt ngân sách, vượt attempts, lỗi `os.replace`, lỗi `fsync` trước replace và JSON hỏng bị từ chối. Bộ test không có network dispatch.

Thêm [crash test](../sandbox/p0-hermes-gate-a/one_shot_crash_test.py) tại commit `de4a98f`, chạy cùng Linux runner exit 0. Child process chết trước `os.replace`: ledger copy vẫn 1 attempt, lượt tiếp theo có thể admit. Chết ngay sau `os.replace`: ledger copy ghi 2 attempts và permit consumed, replay bị chặn. Đây là hai ranh giới transaction; chưa phải fault matrix cho mọi điểm hoặc chứng minh provider đã/không nhận request.

Preflight read-only live sau test: shared ledger thật vẫn ghi attempts 1, reserved USD 0.0035, actual USD 0.0000496 và `kill_switch=true`. Bốn service GATE A healthy. n8n production `/healthz` HTTP 200, Hermes production `/api/health` HTTP 200, restart count cả hai 0. Không kiểm thử paid route hay account authorization.

Giới hạn: crash test chỉ bao phủ trước/sau replace; chưa có lock interoperability thực nghiệm với adapter Level 2, negative policy/schema đầy đủ, kiểm tra quyền mount và provider mock E2E qua guard. Module one-shot vẫn chưa được nối vào guard đang chạy. Vì các gate này chưa PASS, trạng thái remediation và GATE B vẫn **BLOCKED**; không có cơ sở tạo paid permit.

Mã/test: [one_shot.py](../sandbox/p0-hermes-gate-a/one_shot.py), [Linux test](../sandbox/p0-hermes-gate-a/one_shot_linux_test.py). [Evidence JSON](evidence/2026-11-21-ttd-hermes-gate-b-linux-check.json).
