---
id: hermes-gate-b-h6-b2-n-offline-contract-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-N — Đối chiếu hợp đồng Hermes auxiliary và n8n

**ACKNOWLEDGED / HERMES_SOURCE_PARITY_MATCH / BLOCKED_TARGET_PARITY.** ACK tại `08f3d18097e761311ac1aadaa524fa7ef77b438f`, scope B2-N tại `ef21231`, với AGENTS, Workflow §§7–10, security, STATE/CATALOG, hồ sơ Codex, task/ADR-P0-003, B2-H, B2-K và B2-M Codex/Work. B2-N do Codex thực thi trên branch riêng, ChatGPT nghiệm thu và tích hợp trạng thái. [Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [B2-H](2026-11-22-hermes-gate-b-h6-b2-h-read-only.md) · [Work QA B2-M](2026-11-22-work-b2-m-independent-canary-qa.md).

## Đã đối chiếu

| Hạng mục | Kết quả |
| --- | --- |
| Hermes auxiliary | Pull image linux/amd64 ghim `sha256:0ea63377bd672cb76de6a8510aaaef619fe2a045558b771656c072ef527c344f` vào Docker Desktop, với OCI build label `bba80c6`. Trích file bằng Dockerfile chỉ có `FROM` và `COPY`, không chạy tiến trình image. SHA-256 của `run_agent.py`, `api_server.py` và `api_server_openai_routes.py` khớp 3/3 với file cài đặt trong B2-H. `api_server_runs.py` được ghim thêm bằng hash từ image. B2-H chưa ghi hash file này. |
| Run ID và idempotency | Trong module Runs của image, `_handle_runs` kiểm store trước giới hạn concurrency, reserve trước `create_task`, trả `202` với run ID cũ cho replay và `409` khi fingerprint xung đột. API có namespace theo profile/credential. Đây là đối chiếu source. Chưa đo cấu hình/state store thực, mất ACK hoặc restart trên tiến trình. [Hermes Runs API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server#runs-api-streaming-friendly-alternative). |
| Bridge và deadline | `bridge.py` khớp hash B2-H. POST `/v1/runs` có Idempotency-Key, sau đó poll theo run ID. B2-H ghi bridge poll 20 s, HTTP n8n 30 s, Guard response budget 45 s và proxy idle 30 s. Mặc định 1.800 s ở source Hermes là giá trị fallback có thể override theo route. Deadline thực và hành vi khi response không có byte hoặc phát heartbeat chưa đo. |
| n8n mục tiêu | B2-H xác nhận đọc đúng published revision theo quan hệ `activeVersionId` và workflow history, nhưng evidence chỉ giữ các trường chiếu. Không có version ID/digest của revision, export đã khử nhạy cảm hoặc digest image/version xác minh riêng cho instance sandbox. Lịch sử `2.45.7` và digest trong platform audit thuộc n8n production. Sandbox Compose dùng tag `latest`. |
| Candidate n8n công khai | Dựng từ seed Level 1 và transform GATE A có trong Git. Hash ứng viên và validator có trong JSON. Chạy 10 assertion bằng Node trên hai đoạn JS và request giả, không khởi động n8n. Auth router từ chối thiếu/sai bearer. Validator chấp nhận mock success, từ chối paid/unknown và hash sai định dạng. Cùng callback vẫn hợp lệ qua hai lần gọi validator. Callback với task/correlation/run khác và hash đúng dạng cũng hợp lệ ở riêng đoạn validator. Các phép thử này chưa xác nhận branch runtime, unique receipt hoặc downstream dispatch trên bản publish. [n8n Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/). |

[Source check](../sandbox/p0-hermes-gate-a/h6_b2n_source_check.py) · [Evidence và lệnh đọc nguồn](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-n-offline-contract.json).

## Cổng còn thiếu và cách gỡ

**Dừng trước `up`.** Candidate từ Git tái tạo được các dấu hiệu B2-H, nhưng các dấu hiệu đó không xác nhận cùng revision. Chưa chạy fake-provider E2E, chưa có runtime trace cho run ID/restart, deadline, callback hoặc số receipt/dispatch. Tái sử dụng bằng chứng B2-K cho mock ba tiến trình.

1. ChatGPT cần provenance của **n8n sandbox đích** qua một bước chỉ đọc được duyệt riêng. Ghi version và image digest, kèm hash hoặc ID đã khử định danh của published revision. Cung cấp export/fixture đã khử hoàn toàn bearer, credential reference, host/path riêng và dữ liệu vận hành, hoặc digest của cùng projection chuẩn hóa để so với fixture. ACK metadata B2-H hiện có không đủ để thay thế export tương đương.
2. Khi parity đạt, render đủ profile project local. So khớp project, image pin, bind/volume, network và zero public ports. Dùng network nội bộ, no Internet/provider, dữ liệu và khóa giả, datastore riêng cho Hermes/adapter/receiver. Trước khi up, chuẩn bị manifest cleanup theo owner và kiểm đường ra chỉ tới recorder giả trong project.
3. Với recorder fake, thu admission 202 và run ID, cắt ACK sau commit, restart với đúng datastore/scope, rồi gửi lại cùng request. Yêu cầu cùng run ID, một dispatch giả và `409` khi đổi binding. Chạy ca >30 s nhưng <45 s và ca vượt 45 s; ghi mốc admit, dispatch, terminal/unknown, callback và settle. Kiểm bearer/HMAC sai, binding sai, replay, số receipt; unknown giữ reserve giả. B2-H dùng để đối chiếu deadline, không để suy ra ngưỡng đo sẵn.
4. Cleanup chỉ project và datastore local thuộc B2-N. Nếu ACK/kết cục chưa rõ, giữ trace đã khử định danh để đối soát, không phát lại inference. Đợt source-check đã dọn thư mục trích tạm. Image ghim được lưu ở cache Docker local để tái sử dụng.

`LIVE_INTEGRATION_NO_GO / BLOCKED_UID_OR_MOUNT / BLOCKED_PREFLIGHT`. 0 thao tác KVM2, 0 production, 0 provider API, 0 real ledger/permit/key, 0 paid, USD 0. `next_owner: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD` để đối chiếu với Work QA.
