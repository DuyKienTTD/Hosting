---
id: hermes-gate-b-h6-b2-i-async-contract-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-I — Hợp đồng hoàn tất bất đồng bộ trên fixture

**ACKNOWLEDGED / H6_B2_I_ASYNC_CONTRACT_MOCK_PASS / VERIFIED_OFFLINE_MOCK.** ACK phê duyệt `afb05732bfe17ea0f815d5b8fb9393150c90acc3`, AGENTS, toàn bộ AGENT_WORKFLOW gồm §§7–10, Repository Security, STATE/CATALOG, hồ sơ Codex, toàn bộ task mẹ và ADR-P0-003 tại `54eb352378dab23a4a3b0c9ac37f83122bdce75b`. Task blob khớp commit phê duyệt. Live vẫn `NO_GO`, paid Gate B vẫn `BLOCKED_PREFLIGHT`. B2-J writer startup thuộc lane Work. [Task mẹ](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Review B2-H](2026-11-22-hermes-gate-b-h6-b2-h-chatgpt-review.md) · [QA Work](2026-11-22-work-b2-h-assurance.md).

## Hợp đồng đã chạy

- **Admission và status.** `POST /jobs` yêu cầu bearer giả cùng schema v1 `synthetic=true`. Commit SQLite trước khi trả `202` và `Location`. Job ID, task ID, correlation ID và SHA-256 của envelope canonical được giữ qua restart. Cùng envelope trả cùng job (`202` khi đang chờ, `200` khi terminal). Đổi nội dung với task hoặc correlation đã dùng trả `409`. `GET /jobs/{id}` yêu cầu bearer và chỉ đọc.
- **Worker và settlement.** `accepted → reserved → running → terminal`. Reserve giả commit trước transition dispatch giả. Transaction terminal ghi settlement giả tối đa một lần và lưu callback vào outbox. Bốn outcome là `mock_succeeded`, `paid_succeeded`, `failed`, `outcome_unknown`; mọi event có `synthetic=true`. SHA ở đây gắn envelope job fixture, còn exact provider-bound bytes thuộc gate riêng. Khi IPC/transport/ACK không chắc chắn hoặc dispatch bị bỏ dở, outcome unknown giữ reserve và không mở lại dispatch.
- **Callback.** `POST /callback` kiểm HMAC trên timestamp và toàn bộ byte JSON bằng khóa giả tách bearer. Cửa sổ fixture 10 giây. Schema v1 nghiêm ngặt, sequence 1, job/task/correlation/SHA và outcome phải khớp event terminal đã commit. Receipt unique theo job. Replay khớp bị từ chối `409` kèm receipt để sender đối soát ACK mất. Hai lần gửi tối đa, lần hai do fixture operator gọi, chỉ gửi lại event khóa sẵn. Mất callback hoặc ACK đưa outbox vào `dead_letter`. Sau khi xác nhận sender cũ đã dừng, có thể đưa mục `sending` về `dead_letter` để đối soát. Receipt và settlement không tăng thêm.

[Adapter B2-I](../sandbox/p0-hermes-gate-a/h6_b2i_async_mock.py) · [Test B2-I](../sandbox/p0-hermes-gate-a/h6_b2i_async_mock_test.py) · [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-i-async-contract.json).

## Bằng chứng và deadline

**12/12 test fixture PASS, thêm 4/4 timeline có chờ theo thời gian thực.** HTTP chạy trên loopback Windows, provider/Hermes/n8n được mô phỏng, SQLite tạm tự dọn sau test. Trình kiểm thử dùng đồng hồ điều khiển cho deadline và kiểm lại bốn kịch bản với thời gian chờ thật. Thời gian đo từ HTTP POST tới `202` và từ dispatch giả tới callback nằm trong evidence.

| Độ trễ phản hồi giả | Callback tại mốc | Outcome synthetic | Dispatch / Settlement / Receipt | Reserve giả |
| --- | ---: | --- | --- | --- |
| 5 s | 5 s | `paid_succeeded` | 1 / 1 / 1 | settled |
| 21 s | 21 s | `paid_succeeded` | 1 / 1 / 1 | settled |
| 31 s | 31 s | `paid_succeeded` | 1 / 1 / 1 | settled |
| 46 s | 45 s | `outcome_unknown` | 1 / 0 / 1 | held, phản hồi giả tới muộn không đổi outcome |

B2-H xác minh bridge poll 20 s, n8n HTTP 30 s và contract callback live chỉ nhận mock. Fixture cho chúng kết thúc ở admission, còn tiến trình hoàn tất dùng deadline riêng. Test tại 20/30 s vẫn đọc được status `running` khi phù hợp. IPC 4 s, Guard connect 5 s, Guard response 45 s và callback socket 5 s là các budget riêng. SDK 60 s là giả định fixture, đã fault ở cả trước và sau dispatch. Khi callback ACK mất, test giảm socket timeout local xuống 150 ms để chủ động tái hiện lỗi. Tổng IPC/connect/response/settlement trên live và deadline HTTP thực của Hermes vẫn cần đo.

Test âm đã kiểm sai/hết hạn timestamp, sai khóa, bearer thiếu, tamper body, schema thiếu/thừa, callback trước terminal, sequence sai, đổi job/task/correlation/SHA/outcome, replay qua restart, tám admission đồng thời, mất `202` sau commit, IPC/connect/transport/settlement ACK timeout, callback unreachable, mất ACK sau receiver commit và recovery sender. Ca unknown chỉ có một dispatch giả hoặc không dispatch nếu chưa có ACK admission, giữ reserve và từ chối callback giả định lại outcome.

Lệnh chạy từ gốc repo: `python -B sandbox/p0-hermes-gate-a/h6_b2i_async_mock_test.py`. Chạy wall-clock từng kịch bản bằng cách thêm `--wall-clock FixtureTests.test_delay_05` (hoặc `test_delay_21`, `test_delay_31`, `test_delay_46`). Thay đổi duy nhất cần kiểm lại là async admission/completion và callback. Tái sử dụng evidence H3–B2-H cho các phần không đổi.

## Quyết định và bàn giao

GO cho ChatGPT review contract fixture. Sau review, thay đổi tối thiểu cần đặc tả riêng là adapter/workflow sandbox song song nhận `202`, lưu mapping job ↔ Hermes run ID, poll bằng worker có deadline, và receiver riêng xác thực callback, đối soát receipt và phục hồi qua restart. Cần chứng minh Hermes auxiliary thực giữ run ID/idempotency sau mất ACK, SSE buffered, deadline qua proxy/Guard/IPC, provisioning/rotation khóa callback và xác thực receipt qua transport. Fixture dùng một SQLite cho cả hai vai trò, nên lưu trữ độc lập và recovery giữa các service chưa được xác minh. B2-J vẫn là dependency riêng trước mọi live apply. [B2-J](../tasks/2026-11-22-work-b2-j-idle-startup-audit.md).

Rollback đề xuất sau một gate apply riêng là dừng admission của route mới, giữ records/outbox để drain hoặc đối soát job đã nhận, sau đó khôi phục workflow/adapter sandbox đúng phiên bản ghim. Không gửi lại job cho Hermes hoặc ghi đè P0 ledger. B2-I kết thúc bằng đóng socket loopback và dọn DB fixture. Có 0 thao tác KVM2, production, real ledger/permit/key, provider API hoặc paid, và 0 USD. `from_agent: codex`, `next_owner: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`.
