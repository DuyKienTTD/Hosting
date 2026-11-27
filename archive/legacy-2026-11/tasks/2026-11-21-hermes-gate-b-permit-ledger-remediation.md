---
id: ttd-hermes-gate-b-guard-remediation-001
type: task
status: complete
updated_at: 2026-11-21
sensitivity: public
owner: codex
support: [hermes, hostinger-agent]
depends_on: [ttd-hermes-gate-b-001]
paid_inference_approval_for_this_task: false
---

# TTD-HERMES-GATE-B-GUARD-REMEDIATION-001 — One-shot permit và shared-ledger reservation

## Lý do

[GATE B preflight](../reports/2026-11-21-hermes-gate-b-paid-results.md) / [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-001.json), commit `1b1cfcd0f9a13ee35883b7cde48acde5bbba95fb`: **BLOCKED_PREFLIGHT**, paid Hermes attempts mới = 0, chi phí mới = 0. Guard GATE A chỉ mount shared ledger read-only, bắt buộc `kill_switch=true`, forward đến provider mock. Chưa có atomic one-shot permit, pre-dispatch consume/relock hay worst-case reservation vào ledger. **Ledger/kill switch/production chưa được xác minh live trong phiên preflight này**; không gán lại trạng thái lịch sử thành live verified.

## Mục tiêu

Thiết kế, viết và kiểm thử **offline/provider-mock** hai tính năng còn thiếu, không thay production hoặc gọi paid API:
1. **Atomic scoped one-shot permit:** chỉ một `task_id` + `idempotency_key` đã duyệt, không mở global kill switch; permit phải được durable-consume **trước network dispatch**. Reuse, timeout, concurrent race, crash/restart và mismatch đều bị từ chối không tạo request thứ hai. `kill_switch` global vẫn ON.
2. **Shared P0 ledger admission:** đọc/ghi cùng ledger persistent hiện hữu (không copy/reset) theo giao thức đồng bộ tương thích với adapter trước đó; reserve worst-case trước dispatch dưới exclusive lock, bao gồm all billable attempts, hourly/daily/total caps nếu được dùng; kiểm tra ngưỡng cũ: ≤5 calls P0, ≤USD 0.05/day, ≤USD 0.05 total, ≤USD 0.01/job. Đặt riêng GATE B ≤1 physical paid attempt. Chỉ lấy snapshot/copy để chạy destructive concurrency tests.

## Phạm vi kỹ thuật được giao ngay

- Code review nguồn hiện có tại `sandbox/p0-level2/` và `sandbox/p0-hermes-gate-a/`; thiết kế API/contract/ledger file ownership, crash consistency và partial writes.
- Tạo patch/guard logic + tests chạy **offline/provider mock**, kiểm chứng event order `validate -> permit consume -> reserve -> durable commit -> dispatch` hoặc một atomic transaction tương đương; chỉ cho phép dispatch sau khi cả permit và reservation đã bền vững. Nếu crash tại giữa, ưu tiên fail-closed; không tự hoàn lại permit/ledger nếu không chứng minh được provider chưa nhận request.
- Mock tests cho concurrent requests, double dispatch, restart sau consume, callback timeout, wrong task/key, malformed input, wrong model, tools, oversize, price/upper bound, overspend, ledger mismatch, lock failure, read-only mount, secret permissions, network no-bypass, duplicate/retry. Global kill switch vẫn ON.
- Kiểm tra thiết kế an toàn để guard có **quyền ghi tối thiểu** vào shared ledger mà không cho phép runtime Hermes, bridge hay provider mock sửa trực tiếp; không thay N8N_ENCRYPTION_KEY, production credentials hay public exposure.
- Có thể chuẩn bị cấu hình sandbox và chạy preflight chỉ đọc; nếu phải thay running sandbox, chỉ làm khi không ảnh hưởng production, có backup/rollback và thật sự cần cho mock. **Không** nối paid provider hoặc unlock permit cho request trả phí.
- Không đụng production n8n/Hermes, U4S, firewall, DNS, public ports, business accounts; không tạo secret/proxy/billing mới ngoài scope đã duyệt.

## Điều kiện hoàn tất remediation

- Mock test pass với evidence một physical request cho đúng task, zero cho mọi duplicate/race/failure ngoài gate; consume + reservation trước dispatch, durable qua restart.
- P0 global kill switch ON; shared ledger production-P0 giữ nguyên trong tests, đặc biệt baseline trước đây theo báo cáo: 1 attempt, USD 0.0035 reserved và USD 0.0000496 usage-based cost — **phải đọc lại live mới dùng**.
- No-bypass/least privilege/no-public-port và production pre/post health nếu có thao tác sandbox live.
- Không có paid API calls; zero incremental spend. Ghi rõ tests on copy/mock so với live verified; không tuyên bố paid Hermes E2E PASS.

## GATE B preflight lại

Sau khi sửa thành công, Codex cần kiểm tra **live** state/ledger/kill switch/production health, backup, provider model/account pricing/authorization, callback/egress/guard routing; báo cáo trạng thái trước khi dùng one-shot. Approval paid GATE B gốc chỉ còn áp dụng nếu **toàn bộ điều kiện của [ADR-P0-003](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md)** vẫn đạt. Không tự thực hiện paid call trong remediation task; tách paid execution thành bước chứng minh live preflight riêng và không vượt đúng một attempt đã được duyệt.

## Bàn giao

Codex push mã secret-free, test report và evidence đã khử bí mật, đề xuất tiếp tục/STOP, cập nhật task/STATE/CATALOG/CHANGELOG; không đưa secret, private endpoint, raw request chứa nhạy cảm hoặc token lên GitHub public.

## Kết quả phiên này

`CODE_DRAFT / MOCK_NOT_VERIFIED / BLOCKED`: có [module one-shot](../sandbox/p0-hermes-gate-a/one_shot.py), nhưng Linux mock test và live preflight chưa chạy được. Không có paid call hoặc live mutation. Xem [báo cáo](../reports/2026-11-21-hermes-gate-b-permit-ledger-remediation.md).

## Hướng khắc phục blocker môi trường — yêu cầu tiếp theo (2026-11-21)

**Chỉ mock/offline, không paid dispatch.** Ưu tiên sử dụng Linux native trên **KVM2 sandbox có sẵn** để chạy test với Python 3 và `fcntl`; nếu không được quyền vào KVM2, dùng runner Linux tách biệt chỉ với ledger copy và provider mock. **Không cần Docker Desktop Windows để chạy unit test `one_shot_test.py`**. Không tự cài mới daemon, nâng quyền, hoặc restart production để chữa lỗi môi trường.

1. Chạy `one_shot_test.py` trên Linux với **disposable ledger copy**. Ghi rõ kernel/distro/Python, commit, exit code, kết quả. Không chỉnh shared ledger thật; không tạo permit live.
2. **Bổ sung test `multiprocessing` / subprocess (≥10 tiến trình)** chia sẻ cùng file ledger và lock inode, vì bản nháp mới chỉ dùng `ThreadPoolExecutor`. Chứng minh đúng một admitted, mọi đối thủ rejected; restart/process crash không thể reuse.
3. Thử fault injection: kill giữa validate/commit/dispatch, `os.replace` và directory `fsync` failure, stale permit TTL, lock acquisition/read-only failure, wrong model/key/fingerprint, malformed ledger và over budget; reject fail-closed, không bao giờ phát physical mock call khi transaction chưa durable.
4. **Code-review đặc biệt**: xác minh schema/locking thực sự tương thích với `sandbox/p0-level2/adapter.py`; cả hai phải dùng cùng `<ledger>.lock` và không có lost update. Tính reserve worst-case theo giá live được xác minh ở một preflight riêng; dùng Decimal hoặc integer micro-USD thay float nếu thay đổi cần thiết, xác minh mọi trạng thái accounting.
5. **Không tích hợp guard vào paid upstream** cho tới khi các test trên PASS. Nếu mock chạy tốt: tích hợp guard vào **provider mock** và chạy sandbox E2E, kiểm tra private network/no-bypass, permissions của ledger mount, backup/rollback, production pre/post health. Ghi riêng unit PASS, mock E2E PASS và live preflight UNKNOWN/BLOCKED.
6. Báo cáo file+evidence GitHub redacted, cập nhật task & STATE. Nếu không thể chạy trên Linux runner/KVM2 an toàn: BLOCKED_ENVIRONMENT với thông tin cụ thể về quyền/truy cập; không hạ chuẩn nghiệm thu hoặc chuyển sang paid.

**Ranh giới GATE B:** phê duyệt một paid attempt theo ADR-P0-003 không cho phép bỏ qua bất kỳ bước kiểm thử nào. Remediation vẫn **0 paid calls**, kill switch global ON, không thay đổi production.

## Kiểm thử Linux tiếp theo

Đã có [Linux transaction unit PASS](../reports/2026-11-21-hermes-gate-b-remediation-linux-check.md) trên KVM2: 20 tiến trình, 1 admitted/19 rejected, hai crash boundary PASS, ledger copy bền vững và read-only live health/ledger PASS. Full crash matrix, adapter shared-lock interop và guard mock E2E còn thiếu; trạng thái task vẫn `blocked`. Không có paid call hoặc live permit.

## Tiếp tục trên chính task này — sau Linux unit PASS

Bằng chứng mới: [Linux check](../reports/2026-11-21-hermes-gate-b-remediation-linux-check.md) / [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-linux-check.json), commit `c0f3e50b1821e87d9edb5c7a39c8600f8a7aee27`. **BLOCKER_ENVIRONMENT RESOLVED; LINUX_TRANSACTION_UNIT_PASS; GUARD_MOCK_E2E_PENDING.** Các câu trước đây nói Linux test chưa chạy chỉ là lịch sử. Ledger live được xác minh read-only là 1 attempt, USD 0.0035 reserved, USD 0.0000496 usage estimate, kill switch ON; n8n/Hermes production HTTP 200, restart 0 (thời điểm báo cáo 2026-11-21).

**Hãy tiếp tục hoàn thiện trong task hiện có, không lập thêm nhiệm vụ con và không dừng chỉ để bàn giao từng test.** Codex chủ động chọn cách triển khai Linux hiệu quả trong phạm vi sandbox/mock đã cấp quyền, lặp sửa–kiểm thử cho đến nghiệm thu hoặc blocker thật sự cần chủ dự án xử lý. Ưu tiên:

1. Hoàn thiện các fault/crash cases có rủi ro double dispatch hoặc ledger corruption, xác nhận fail-closed và đúng thứ tự durable commit trước request.
2. Test liên tiến trình **shared-lock interoperability** với adapter Level 2 trên **ledger copy duy nhất**, không tạo lost updates, không cấp hai admission hoặc phá baseline. Review file ownership, atomic replace và `fsync`.
3. Tích hợp `one_shot.py` vào **guard sandbox trỏ provider mock**, không cấp paid API credential hoặc tạo paid permit. Kiểm thử full n8n → Hermes → guard → provider mock → authenticated callback, duplicate/replay/timeout/concurrency, no-bypass và phí mới 0.
4. Backup/rollback và pre/post production health khi cần thay sandbox; shared ledger thật phải được bảo vệ. Phân biệt rõ test ledger copy và live read-only; không ghi permit hoặc reservation giả vào ledger thật.
5. Push **một** báo cáo nghiệm thu tổng hợp với evidence redacted: `MOCK_INTEGRATION_PASS` hay `BLOCKED` kèm nguyên nhân còn lại. Không coi unit PASS là paid readiness; GATE B paid attempt vẫn chờ preflight live toàn bộ theo ADR-P0-003.

**Không gọi API trả phí trong remediation, không đổi production, giữ kill switch ON.**

## Nghiệm thu cuối phiên

**MOCK_INTEGRATION_PASS / remediation complete.** Shared-lock interop, 14 fault cases, 20-process race, full n8n→Hermes→guard→provider mock→callback, replay và rollback đã PASS trên KVM2; ledger thật không đổi, kill switch ON, paid calls mới 0. Xem [báo cáo nghiệm thu tổng hợp](../reports/2026-11-21-hermes-gate-b-guard-remediation-results.md) và [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-guard-remediation.json). **Paid GATE B vẫn BLOCKED_PREFLIGHT** cho đến khi preflight live riêng hoàn tất; không coi mock PASS là quyền dispatch trả phí.
