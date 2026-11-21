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

> Kết quả hiện hành là **`B2N_ACTIVE_RESTART_FAKE_PASS`**. Phần đầu ghi mốc PR #5 tại `253a795`. Phép thử restart khi run đang chạy ở cuối báo cáo.

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

## Follow-up tại `322a2c1` — provenance đã xác minh

**ACKNOWLEDGED / TARGET_PROJECTION_MATCH.** Theo đặc tả follow-up, dùng phiên Web Terminal đã có quyền và chạy probe ghim `dcf6854` trong bộ nhớ. Xác định đúng container qua tên, project và service trước khi lấy image ID, repo digest, platform và version từ package cài đặt. Chọn revision đang publish theo `activeVersionId → workflow_history` trong child có Landlock chặn ghi, SQLite `mode=ro` và `query_only`. Đọc hai lần khớp, rồi kiểm lại ID/image/PID/start time và version container. Không gọi webhook KVM2 hoặc đọc bảng credentials/executions. [Probe](../sandbox/p0-hermes-gate-a/h6_b2n_n8n_provenance.py).

- n8n sandbox **2.45.7**, linux/amd64, image ID và repo digest đều `sha256:9a8d8dcea75667496695d7810d7e1fe018a65efb36cc499d347f3931b3957b5d`. Đây là phép đo trực tiếp riêng trên sandbox.
- Fingerprint revision `a96860fa32efe5a3fa5bee7b9d72c9296765de9523f4bb2a63a52c6f0e428c95`. Digest projection chuẩn hóa của bản publish và candidate Git cùng là `08aa63bcfaf27f9ced2a5374ce67f4683877f615ed00dafea086f608321dde0d`. So toàn bộ tham số node và wiring, kể cả node type/version, auth, response mode, timeout/retry và code validator. So settings lấy từ workflow entity riêng. Bỏ vị trí, ghi chú UI và webhook ID. Chỉ thay literal bearer ở hai vị trí đã biết và host/path đã biết bằng placeholder. Phép đo đầu còn chênh tham số HTTP node. Probe mới xác nhận chênh lệch biến mất khi thay riêng bearer literal của HTTP node bằng placeholder. Không xuất workflow thô, bearer hoặc giá trị tham số khác nhau.

### Môi trường local

Project `ttd-b2n-local` render đủ profile với image Hermes/n8n ghim, năm dịch vụ và năm volume riêng. Chỉ bind RO thư mục fixture tự tạo. Rootfs RO, internal network không IPv6, không port host, driver không có default route. Verify Docker inspect so với render trước request. Hermes init chuẩn bị home riêng với CHOWN/SETUID/SETGID rồi chuyển sang user Hermes. Hai workflow n8n dùng cùng build. Baseline giữ auth/validator của revision đã so, đổi route chỉ tới fixture. Candidate chuyển riêng nhánh callback qua receipt service, giữ bearer của webhook và có bearer thứ hai trên đường nội bộ tới receipt. Receipt đối chiếu job/task/correlation/run/digest với binding đã ghi trước, commit trên SQLite riêng rồi mới trả ACK. Fake provider chỉ chạy trong project và có recorder riêng. [Runner](../sandbox/p0-hermes-gate-a/h6_b2n_runtime.py) · [Fixture](../sandbox/p0-hermes-gate-a/h6_b2n_runtime_fixture.py).

### Kết quả runtime local

**`B2N_ISOLATED_FAKE_RUNTIME_PASS` cho các ca đã chạy.** Dùng `python -X utf8 -B sandbox/p0-hermes-gate-a/h6_b2n_runtime.py --projection <digest>` với digest đã đo ở trên.

| Ca | Quan sát |
| --- | --- |
| Baseline n8n | Bearer sai trả 401. Hai lần gửi cùng callback mock hợp lệ đều được ACK qua workflow gốc; receipt store riêng có 0 bản ghi. |
| Mất ACK, restart Hermes | Client gửi POST rồi đóng kết nối trước khi đọc response. Recorder thấy đúng một dispatch. Replay trước restart trả 202 và run ID. Sau khi run hoàn tất và restart Hermes với cùng volume, cùng binding vẫn trả 202 và cùng run ID. Cùng key với body khác trả 409; recorder vẫn 1. |
| Fake provider chậm trong budget | Ca delay 31 s hoàn tất ở **31,412 s**, tính từ khi driver thấy recorder. Candidate ghi một receipt trước khi client timeout lúc chờ ACK. Từ chối bearer sai 401 và digest sai 409. Recorder 1. |
| Fake provider vượt budget | Ca delay 46 s chưa terminal khi driver chạm cutoff, ghi `outcome_unknown` ở **45,197 s**. Một receipt và một dispatch. Bearer sai trả 401, digest sai trả 409. |
| Restart receipt receiver và replay | Hai receipt đọc lại khớp chính xác qua n8n. Event đổi outcome bị 409. Có đúng hai receipt và recorder giữ **1/1/1** cho ba ca. |
| Rollback | Kiểm owner label của container, volume và network trước khi down, sau đó còn 0 tài nguyên project. Thư mục fixture local đã dọn. |

Mốc 45 s là cutoff của driver local, chưa đo deadline hiệu lực ở Guard/Hermes trên tuyến KVM2. Ca Hermes restart ở trạng thái đã hoàn tất; chưa thử restart khi inference còn chạy. Tini có cảnh báo chuyển tín hiệu trong lượt restart. Run ID vẫn được đọc lại từ cùng volume sau khi tiến trình lên lại. n8n có truy vấn DNS catalog mặc định bị chặn trong network cô lập. Không chạy provider thật, không phát sinh chi phí và không ghi trên KVM2. `LIVE_INTEGRATION_NO_GO / BLOCKED_UID_OR_MOUNT / BLOCKED_PREFLIGHT`. Giao ChatGPT đối chiếu với Work trên PR #4, giữ kết quả ở phạm vi local fake-only.

## Delta tại `6b0508e` — restart Hermes khi run đang chạy

**ACKNOWLEDGED / `B2N_ACTIVE_RESTART_FAKE_PASS`.** ACK main `6b0508e840ff9c1dbe6da2cf992f1e02cc0e63aa` cho AGENTS, Workflow §§7–10, security, STATE/CATALOG, hồ sơ Codex, task và ADR-P0-003. Đối chiếu lại B2-H, report/evidence của Codex tại PR #5 `a19765f` và review Work PR #4 tại `c265340`. Dùng lại provenance n8n, các image pin và fixture B2-N. Chạy riêng ca restart đang hoạt động. [Evidence JSON](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-n-offline-contract.json).

```text
python -X utf8 -B sandbox/p0-hermes-gate-a/h6_b2n_runtime.py --projection 08aa63bcfaf27f9ced2a5374ce67f4683877f615ed00dafea086f608321dde0d --case active-restart
```

Render đủ profile và kiểm lúc chạy trên Docker Desktop. Năm service dùng năm volume riêng và một bind chỉ đọc cho fixture. Network nội bộ, không IPv6, không host port, driver không có default route. Hermes đọc và ghi trong volume fixture `/b2n-state`. Runner so ID, image, entrypoint, mount và môi trường auth trước/sau. Chọn SIGKILL trực tiếp trên container fixture vì Tini từng báo không chuyển được tín hiệu khi restart mềm. Docker xác nhận exit 137 và PID của tiến trình init đổi từ 94385 sang 94974. [Docker kill](https://docs.docker.com/reference/cli/docker/container/kill/) · [Hermes Runs API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server#runs-api-streaming-friendly-alternative).

| Mốc UTC ngày 2026-11-21 | Quan sát |
| --- | --- |
| 21:12:26.826–21:12:27.002 | POST trả 202. Recorder commit chính xác một dispatch. Hermes trả `running` khi fake provider đang giữ phản hồi. Driver quan sát sau 4,177 s tính từ lúc submit. |
| 21:12:27.197–21:12:27.554 | Docker dừng bằng SIGKILL rồi khởi động lại cùng container và datastore. Từ lúc gửi lệnh kill tới inspect sau start mất 0,672 s. |
| Sau restart | Hermes trả `unknown` cho run cũ. Replay cùng body, Idempotency-Key và auth trả HTTP 202 với `replayed: true` và đúng run ID sau 10,686 s tính từ submit. Recorder vẫn 1. |
| 21:12:37.920–21:12:38.124 | n8n candidate ghi một receipt `outcome_unknown` trước khi driver mở khóa phản hồi. Fake provider thử ghi lên kết nối cũ và gặp kết nối đã đóng. Hermes vẫn `unknown`. Driver gửi riêng callback thành công đến muộn, có cùng job/task/correlation/run/digest, qua n8n và nhận 409. Bearer sai nhận 401. Replay `outcome_unknown` nhận 200 với cùng receipt. SQLite vẫn đúng một receipt, recorder vẫn đúng một dispatch. |

Trong fixture này, driver gọi Hermes trực tiếp và chủ động gửi callback đến n8n candidate. Lượt sau có thể nối H6 Guard và bridge vào cùng project giả, truyền run ID và request digest qua từng đoạn, ghi mốc monotonic ở admission, dispatch, deadline/unknown, callback và commit receipt. Sau đó thử phản hồi sát hoặc vượt từng budget để tìm thành phần cắt trước. Deadline xuyên tuyến và KVM2 chưa đo ở lượt này.

Rollback đã kiểm owner label trước khi xóa. Còn 0 container, volume hoặc network của project. Lượt này truy cập KVM2, production, ledger/permit/key thật và provider API đều 0. Paid 0, USD 0. `LIVE_INTEGRATION_NO_GO / BLOCKED_UID_OR_MOUNT / BLOCKED_PREFLIGHT`. Giao ChatGPT nghiệm thu qua PR #5, `PREPARED_FOR_OWNER_FORWARD`.
