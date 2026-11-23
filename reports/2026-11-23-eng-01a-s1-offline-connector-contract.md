---
id: eng-01a-s1-offline-connector-contract-report
type: report
status: current
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
task_id: eng-01a-s1-offline-connector-contract
owner: codex
---

# ENG-01A-S1 — Hợp đồng connector offline

| TASK | AGENT | BASE_SHA | ACK | OBSERVED | EXPECTED | TEST_DELTA | EVIDENCE | VERDICT | BLOCKERS | NEXT_OWNER |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENG-01A-S1 | Codex | `e385c1b` | EXECUTE, 23/11/2026 ICT | Connector fake dùng SQLite tạm, bốn cửa sổ crash tiến trình đã đo | Tối đa một dispatch giả, một receipt mỗi job, unknown bất biến, callback đúng binding | 8/8 test, 11 mục evidence | [JSON](evidence/2026-11-23-eng-01a-s1-offline-connector-contract.json) | `ENG01A_S1_OFFLINE_CONTRACT_PASS` | Không có trong scope offline; `REAL_CONNECTOR_UNTESTED` | ChatGPT Điều phối |

ACK quy tắc tại `e385c1bea2070973e3007e5717f7e980348d6ab3`, Workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. Chỉ thị thực thi đã nhận qua yêu cầu chủ dự án dẫn comment `7090656024`. Đã fetch main/PR #6/#7, kiểm không trùng task hoặc PR và tạo nhánh S1 từ main. Lấy lại semantics digest/idempotency, callback binding và receipt commit trước ACK từ B2-N/O. Không chạy lại các suite lịch sử. [Chỉ thị](https://github.com/DuyKienTTD/Hosting/pull/7#issuecomment-7090656024) · [Task](../tasks/2026-11-23-eng-01a-s1-offline-connector-contract.md) · [Work O1–O4](https://github.com/DuyKienTTD/Hosting/commit/5a036fa8952b0dede7470579011a053bcdce51b1).

## Kết quả kiểm thử

| Ca | Kỳ vọng và quan sát |
| --- | --- |
| Schema và offline | Admission hợp lệ trả 202 và đúng digest. Request thiếu trường, sai approval, budget/deadline, kênh thật hoặc thêm endpoint/credential bị từ chối. Constructor từ chối endpoint, credential và kho ngoài fixture. Python audit hook chặn sự kiện socket cả trong tiến trình test và worker. |
| Success, failure, replay | Success `completed` và known failure `failed` đều một dispatch giả/một receipt. Replay trả cùng job/receipt với snapshot không đổi. Cùng key, payload hợp lệ đã đổi trả 409. |
| Deadline và kết quả muộn | Ở deadline logic 20 ms, job đang chạy chốt `outcome_unknown` với một dispatch. Kết quả và callback muộn mâu thuẫn bị từ chối. Replay giữ một dispatch/một receipt. Job hết hạn trước dispatch có 0 dispatch/một receipt unknown. |
| Callback identity | Ở `sending` trước commit receipt, thiếu callback ID bị 422. Thay digest rồi tính lại callback ID vẫn bị 409, snapshot giữ nguyên. Worker mới phục hồi callback hợp lệ và commit một receipt. |
| Crash trước/sau fake dispatch khi `working` | Worker cũ thoát mã 86. PID khác mở lại cùng SQLite. Trước dispatch giữ 0 dispatch. Sau dispatch giữ đúng 1. Cả hai về `outcome_unknown`, một receipt/job và replay không dispatch lại. |
| Crash trước/sau commit receipt khi `sending` | Worker mới dùng đúng callback đã lưu. Trước receipt, worker commit một receipt. Sau receipt và trước ACK, worker đọc lại receipt y hệt. Hai ca giữ một dispatch, một receipt và một ACK mỗi job. |
| Worker còn giữ lock | Attempt recovery bị từ chối, job giữ `pending` và 0 dispatch. |

```powershell
python -X utf8 -B sandbox/connector-contracts/test_offline_connector.py
```

Môi trường đo CPython 3.12.3, SQLite 3.45.1, Windows 11 AMD64. Evidence có từng cặp observed/expected, PID/exit code theo cửa sổ crash, chuỗi audit, Git blob và SHA-256 của source và môi trường. Adapter dùng standard library, `LIVE_ENABLED=False`, chỉ mở SQLite trong thư mục fixture tạm được đánh dấu. Fixture đếm fake dispatch, callback và receipt trong cùng DB qua các transaction riêng. Code không có listener hoặc transport. Bằng chứng crash là thoát tiến trình giữa các transaction đã commit. Deadline dùng đồng hồ logic. [Contract và giới hạn](../sandbox/connector-contracts/README.md).

Hợp đồng chung bao gồm idempotency/digest, trạng thái, budget/deadline, audit, outbox và receipt. Connector thật cần phê duyệt riêng về channel auth, OAuth scope, consent/retention, quota, rate limit, pricing và reconciliation. Phép thử không chứng minh tính chất exactly-once cho tác động bên ngoài hoặc lỗi mất điện. Callback fixture kiểm binding tại chỗ. Xác thực sender qua network thuộc bước triển khai riêng.

## Bàn giao AI-02

Đóng AI-02 phần local theo nghiệm thu `B2P_LOCAL_RENDER_PASS_ACCEPT_WITH_LIMITATIONS`. Projection và timer ở PR #5 có disposition `FIXED_IN_B2P_CANDIDATE_ONLY`; nguồn ACK là `ACK_PROVENANCE_CLARIFIED`. PR #5/#7 và evidence lịch sử giữ nguyên. KVM2 `BLOCKED_PREFLIGHT_INPUT / NOT_MEASURED`, fixture GO = NO. [Nghiệm thu AI-02](https://github.com/DuyKienTTD/Hosting/pull/7#issuecomment-7090656024).

Đã chuyển [INF-01 PR #9 tại `486afc2`](https://github.com/DuyKienTTD/Hosting/pull/9) cho ChatGPT Điều phối làm đầu vào đối chiếu identity/ownership/collision, image pins/cache, headroom, health/restarts và backup/rollback. Report INF-01 có phần đọc Docker bị thiếu và metadata backup. Quyết định cổng KVM2 vẫn thuộc lượt tổng hợp riêng.

**NEXT_OWNER:** ChatGPT Điều phối. Zero external-service/provider calls trong fixture, paid 0 USD, 0 thao tác KVM2 hoặc production. Live Gate B giữ `NO_GO`, paid giữ `BLOCKED_PREFLIGHT`.
