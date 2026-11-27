---
id: hermes-gate-b-paid-results-2026-11-21
type: report
status: blocked
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
---

# GATE B — preflight dừng trước paid inference

Kết quả: **BLOCKED / 0 paid Hermes attempts trong nhiệm vụ này**. Không có request trả phí nào được dispatch.

Đã đối chiếu task, ADR-P0-003, GATE A report/evidence và mã triển khai trên `main`. Guard GATE A hiện chỉ mount shared P0 ledger read-only, kiểm tra `kill_switch=true`, giới hạn exact `gpt-6-luna`, `max_output_tokens=600`, full serialized request ≤4.000 ASCII bytes và chuyển cố định tới provider mock. Mã không có scoped one-shot permit, thao tác atomic consume/relock, reservation vào ledger hay paid upstream. Vì vậy preflight mục 3 và 4 của task chưa PASS. Không thể xem approval là permit đã triển khai.

Giá Standard GPT-6 Luna đối chiếu trên [tài liệu model chính thức](https://developers.openai.com/api/docs/models/gpt-6-luna) là USD 0,10/triệu input tokens và USD 0,50/triệu output tokens. Với 4.000 input và 600 output, phép tính token cơ bản là USD 0,0007; đây chưa phải chứng minh đầy đủ các thành phần billing, tài khoản, tier và reservation live. Không dùng con số này để cho phép dispatch.

Chưa xác minh live trong lần preflight này: trạng thái runtime/ledger mới nhất, quyền API của credential, provider route, health production và khả năng callback. Các kết quả GATE A là bằng chứng lịch sử, không thay thế preflight live. Ledger và kill switch không bị thao tác trong lần này; trạng thái live sau cùng chưa được xác minh.

Để tiếp tục trong phạm vi approval hiện có, cần triển khai và kiểm thử offline/mock one-shot permit trên chính shared atomic ledger: khóa liên tiến trình, reserve worst-case, consume bền vững trước dispatch, chống concurrency/restart/retry, giữ global kill switch ON; sau đó xác minh route/auth/no-bypass, backup, production health, giá và account access live. Chỉ khi toàn bộ gate PASS mới gửi tối đa một fake-data request qua Hermes. Không có GATE B paid E2E PASS tại thời điểm báo cáo.

[Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [ADR](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md) · [Evidence](evidence/2026-11-21-ttd-hermes-gate-b-001.json)
