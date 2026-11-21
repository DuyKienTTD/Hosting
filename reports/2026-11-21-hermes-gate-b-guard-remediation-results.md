---
id: hermes-gate-b-guard-remediation-results-2026-11-21
type: report
status: complete
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-guard-remediation-001
---

# GATE B guard remediation — nghiệm thu mock

**Kết quả: MOCK_INTEGRATION_PASS; paid GATE B chưa chạy.** Chỉ kiểm thử bằng provider mock và dữ liệu giả trên KVM2. Paid calls mới **0**, chi phí API mới **USD 0**. Global kill switch vẫn ON. Mọi thao tác ghi ledger trong lượt này dùng bản sao riêng; không tạo permit hay reservation trên ledger P0 thật.

## Thực thi và bằng chứng

- Ubuntu 24.04.4, Linux `6.8.0-147-generic`, Python 3.12.3. Linux transaction test exit 0: 20 tiến trình cùng ledger/lock, 1 admitted, 19 rejected; replay sau reload bị chặn. Tổng 14 fault cases gồm wrong task/key/fingerprint/model, permit hết hạn, vượt cap/attempt, JSON hỏng, lock/read-only failure, `os.replace`, file `fsync`, directory `fsync`. Với directory `fsync` failure sau replace, hàm trả lỗi và permit đã consumed trong file nên retry không thể dispatch. [Crash boundary test trước đó](2026-11-21-hermes-gate-b-remediation-linux-check.md) chứng minh child chết trước/sau replace.
- Shared-lock interop với adapter Mức 2 trên cùng ledger copy: cùng inode `<ledger>.json.lock`, không lost update, attempts 2/reserved USD 0.007, paid calls 0; exit 0. Xem [test interop](../sandbox/p0-hermes-gate-a/one_shot_interop_test.py).
- Backup `guard.py` và `compose.yaml` sandbox trước khi đổi. Guard được nạp với one-shot admission và mock ledger riêng mode directory 700/file 600. Ledger P0 thật tiếp tục mount read-only. Provider upstream chỉ là mock trên Docker internal network; cấu hình không khai báo public port. [Guard](../sandbox/p0-hermes-gate-a/guard.py), [override](../sandbox/p0-hermes-gate-a/compose.mock-one-shot.yaml).
- Full E2E từ authenticated n8n webhook → bridge → Hermes auxiliary → guard → provider mock → authenticated callback: first HTTP 200, callback HTTP 200, `mode=hermes_mock`, `paid_inference=false`. Replay HTTP 200 với `replayed=true`; test exit 0. Mock ledger tăng từ 1 lên 2 attempts, reservation từ USD 0.0035 lên USD 0.007, permit `consumed`, kill switch vẫn true. [E2E script](../sandbox/p0-hermes-gate-a/one_shot_e2e_test.py).
- Rollback sandbox bằng đúng hai file backup (`cmp` exit 0), guard/bridge đều healthy. Production n8n và Hermes health HTTP 200, restart count 0 trước/sau. Ledger P0 thật sau test: 1 attempt, USD 0.0035 reserved, USD 0.0000496 actual usage estimate, kill switch true, 0 one-shot permits; không đổi so với trước test.

[Evidence đã khử bí mật](evidence/2026-11-21-ttd-hermes-gate-b-guard-remediation.json) lưu kết quả và ranh giới kiểm chứng. Không lưu token, raw request hoặc private endpoint.

## Giới hạn và bước kế tiếp

Đây là **mock integration PASS**, không phải paid Hermes Agent E2E hay paid readiness. Chưa có kiểm tra live mới về provider/account pricing, authorization, callback/egress cho paid route và một permit paid trên ledger thật; guard hiện đã rollback về cấu hình GATE A. Fingerprint hiện ràng buộc marker dữ liệu giả của bridge; trước paid dispatch cần đối chiếu contract fingerprint của toàn request thực tế và đảm bảo accounting sau kết quả/timeout. Lệnh Docker inspect chi tiết network bị lỗi template; kết luận no-public-port dựa trên compose và mount quan sát được, chưa phải kiểm tra live đầy đủ network graph. Vì vậy paid GATE B vẫn **BLOCKED_PREFLIGHT**. Không tự tạo permit hay gọi API trong task remediation này.
