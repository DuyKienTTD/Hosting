---
id: hermes-gate-b-permit-ledger-remediation-2026-11-21
type: report
status: blocked
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-guard-remediation-001
---

# GATE B permit/ledger remediation — kết quả tạm thời

**BLOCKED / CODE_DRAFT / MOCK_NOT_VERIFIED.** Không có paid API call, không thay runtime live, production hay ledger thật trong phiên này.

Đã đối chiếu [adapter Level 2](../sandbox/p0-level2/adapter.py) và [guard GATE A](../sandbox/p0-hermes-gate-a/guard.py). Adapter dùng lock `<ledger>.lock`, `flock`, atomic replace và reservation USD 0.0035 trước dispatch; guard chỉ mount ledger read-only và dùng provider mock. Tạo [module one-shot](../sandbox/p0-hermes-gate-a/one_shot.py) cùng [test ledger copy](../sandbox/p0-hermes-gate-a/one_shot_test.py). Module kiểm tra kill switch ON, task/key fingerprint/model/TTL, cap và ghi permit consumed cùng reservation trong một file commit trước khi trả quyền dispatch. Nó chưa được tích hợp vào guard hoặc deploy.

Kiểm thử local chưa chạy được: Windows Python thiếu `fcntl`; Docker Desktop daemon không khả dụng. Vì chưa có Linux mock run, crash/fault injection, no-bypass live hay kiểm chứng shared lock cùng adapter, **không chứng nhận atomic one-shot hoặc mock PASS**. Không có bằng chứng live mới về ledger, kill switch, health production, account/model access và callback. Các số baseline cũ chỉ là lịch sử.

Trước deploy cần chạy test trên Linux với ledger copy và provider mock, bổ sung test crash trước/sau commit, disk-write failure, timeout, >=10 concurrent processes, policy negative cases, rồi review quyền mount ledger directory và shared lock. Cần backup/rollback sandbox, pre/post production health và kiểm tra live ledger/kill switch. Không được tạo permit paid hoặc dispatch tới OpenAI trong task remediation.

Kết luận: **GATE B vẫn BLOCKED_PREFLIGHT**. Mã hiện là bản nháp có thể review, không phải bản triển khai an toàn.
