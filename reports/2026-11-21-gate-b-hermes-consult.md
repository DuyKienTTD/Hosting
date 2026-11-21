---
id: gate-b-hermes-consult-2026-11-21
type: report
status: current
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
source: repository-code-review,provider-mock-tests,gate-b-existing-evidence
---

# GATE B — Hermes consult H2: runtime mismatch, canonical request và token-counting

## ACK / rule commit đã đọc

Đã đọc `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/hermes.md` và task `TTD-HERMES-GATE-B-001` tại commit quy tắc:

- `01aa77af581aa8eb0f6e3e44d43f7b764013c6d8`

Repo local khi bắt đầu H2 trỏ tới `main` ở commit trên. Báo cáo này chỉ dùng đọc mã, evidence sẵn có và **provider mock/offline tests**; không gọi inference trả phí, không bật tools, không đổi production.

## Tóm tắt kết luận

Kết quả: **H2_COMPLETE / READ_ONLY_MOCK_ONLY**.

1. `HERMES_RUNTIME_MISMATCH` hiện **không đủ bằng chứng để kết luận là mismatch live của Hermes runtime**. Trong mã hiện tại, cùng mã lỗi này có thể phát sinh thuần túy do **bridge replay trạng thái lỗi cũ theo `task_id` từ `bridge-tasks.json`**, không cần tạo một lượt `run_hermes()` mới.
2. Tầng cần khóa permit/hash cho GATE B là **provider-bound `/v1/responses` request sau guard**, không phải request `/v1/runs` mà bridge gửi vào Hermes auxiliary.
3. Canonical serialization hiện nằm ở `mock_contract.freeze()` và phải bind vào **forwarded bytes sau policy-enforcement**. Hash permit/capture authoritative là SHA-256 của **wire bytes** này.
4. Contract đếm token phải dùng `POST /v1/responses/input_tokens` với **cùng `model`, `instructions`, `input`, `tools`** như request inference; an toàn hơn là derive trực tiếp từ final forwarded request bằng cách chọn các trường ảnh hưởng input surface.
5. One-shot accounting đã PASS ở mock riêng (`mock_contract_test.py`, `one_shot_linux_test.py`, `one_shot_interop_test.py`). Callback + one-shot cùng một E2E đã từng PASS trong evidence remediation cũ, nhưng **sau checkpoint egress isolation hiện tại repo vẫn ghi `not_run`**, nên current preflight vẫn thiếu một combined rerun trên topology mới.

## Phạm vi và phương pháp

### Đã đọc

- `tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md`
- `reports/2026-11-21-hermes-gate-b-egress-isolation.md`
- `reports/2026-11-21-hermes-gate-b-preflight-recheck.md`
- `reports/2026-11-21-hermes-gate-a-mock-results.md`
- `reports/2026-11-21-hermes-gate-b-guard-remediation-results.md`
- `reports/evidence/2026-11-21-ttd-hermes-gate-b-egress-isolation.json`
- `reports/evidence/2026-11-21-ttd-hermes-gate-b-preflight-recheck.json`
- `reports/evidence/2026-11-21-ttd-hermes-gate-a-001.json`
- `sandbox/p0-hermes-gate-a/bridge.py`
- `sandbox/p0-hermes-gate-a/guard.py`
- `sandbox/p0-hermes-gate-a/mock_contract.py`
- `sandbox/p0-hermes-gate-a/mock_contract_test.py`
- `sandbox/p0-hermes-gate-a/one_shot.py`
- `sandbox/p0-hermes-gate-a/one_shot_linux_test.py`
- `sandbox/p0-hermes-gate-a/one_shot_interop_test.py`
- `sandbox/p0-hermes-gate-a/provider_mock.py`

### Mock/offline tests đã chạy trong phiên này

- `python3 sandbox/p0-hermes-gate-a/mock_contract_test.py` → **PASS**
- `python3 sandbox/p0-hermes-gate-a/one_shot_linux_test.py` → **PASS**
- `python3 sandbox/p0-hermes-gate-a/one_shot_interop_test.py ../p0-level2/adapter.py` → **PASS**
- local bridge replay harness với state file tạm → **PASS**, chứng minh reused `task_id` có thể replay `HERMES_RUNTIME_MISMATCH` từ persisted state, còn `fresh task_id` thì chạy PASS

## 1. Vị trí chính xác phát sinh `HERMES_RUNTIME_MISMATCH`

Trong `sandbox/p0-hermes-gate-a/bridge.py`, mã lỗi này chỉ được ném ở đúng hai điều kiện trong `run_hermes()`:

1. `runtime.requested.model != "gpt-6-luna"` hoặc `runtime.requested.provider != "openai-api"`
2. `runtime.model` hoặc `runtime.provider` là non-empty và khác cặp trên

Điều quan trọng:

- `bridge.py` còn có **persistent task state** ở `/opt/ttd/state/bridge-tasks.json`
- nếu một `task_id` đã có bản ghi `state == "failed"`, request cùng `task_id` sẽ **trả lại lỗi đã lưu** mà **không gọi lại** `run_hermes()`

### Kết quả local reproducer trong phiên này

Harness cục bộ với `STATE_PATH` tạm đã xác minh:

- lượt đầu: `run_hermes()` giả lập raise `HERMES_RUNTIME_MISMATCH` → bridge trả 502
- lượt hai với **cùng `task_id`** nhưng đã patch `run_hermes()` thành PASS → bridge vẫn trả 502 với cùng lỗi cũ
- lượt ba với **`fresh task_id`** → bridge trả 200 PASS

Điều này chứng minh triệu chứng “một task báo mismatch, task mới thì PASS” **có thể xảy ra hoàn toàn do replay của failed state**, không buộc phải do Hermes runtime đang mismatch ở lần gọi mới.

## 2. Đối chiếu metadata phiên lỗi và phiên PASS

### PASS semantics đã xác minh từ mã + evidence

Mẫu PASS mà bridge chấp nhận là:

- `runtime.requested.model == "gpt-6-luna"`
- `runtime.requested.provider == "openai-api"`
- `runtime.model` và `runtime.provider` có thể **rỗng / null / absent**
- nếu `runtime.model` hoặc `runtime.provider` có giá trị non-empty thì phải khớp chính xác cặp trên

Điều này phù hợp với báo cáo GATE A:

- upstream poll có thể chỉ trả đúng `requested` nhưng để trống served model/provider
- bridge chấp nhận trường hợp served fields trống

### Phiên lỗi ban đầu trong evidence hiện có

Evidence hiện tại chỉ còn:

- `initial_webhook_http = 500`
- `initial_error = "HERMES_RUNTIME_MISMATCH"`
- sau đó `fresh_task_webhook_http = 200`, `fresh_task_callback_http = 200`

**Không có raw runtime metadata của phiên lỗi ban đầu trong repo public**, nên không thể chứng minh live rằng lần lỗi thật sự có `runtime.requested` sai hay `runtime.model/provider` non-empty mismatch.

### Kết luận bảo thủ

- **VERIFIED_MOCK:** cùng thông điệp mismatch có thể là replay của failed state theo `task_id`
- **DOCUMENTED:** bridge chỉ fail ở hai nhánh metadata nêu trên nếu thực sự vào `run_hermes()`
- **UNKNOWN:** exact runtime metadata của phiên lỗi ban đầu trên KVM2

Vì vậy, H2 khuyến nghị **không dùng `initial_error = HERMES_RUNTIME_MISMATCH` như bằng chứng đủ để kết luận runtime Hermes live sai**, trừ khi có raw poll payload hoặc rerun với `fresh task_id` trên cùng topology cho thấy mismatch lặp lại.

## 3. Canonical serialized Responses request và SHA-256

## 3.1. Phân biệt hai tầng request

### Tầng A — bridge → Hermes auxiliary `/v1/runs`

Bridge tạo body `/v1/runs` trong `bridge.py`:

- có `input` là prompt text dài
- `model = gpt-6-luna`
- `provider = openai-api`
- `model_options.reasoning_effort = none`
- `model_options.service_tier = default`

Trong phiên này, với fixture local tối thiểu, body này có:

- bytes: **432**
- SHA-256: **`857c5f7cd0e09dd4e23120e7e156be9669605c50a4832ec13c43d909ea009b49`**

Đây **không** phải canonical provider-bound request dùng cho permit GATE B.

### Tầng B — guard → provider `/v1/responses`

Canonical provider-bound request được đóng băng ở:

- `sandbox/p0-hermes-gate-a/mock_contract.py::freeze()`
- guard gọi `record_capture()` trên body raw và forwarded body đã qua `enforce()`

`freeze()` làm các việc quan trọng:

- chỉ chấp nhận whitelist fields
- ép `service_tier = default`
- ép `max_output_tokens = 600`
- ép `store = false`
- serialize bằng JSON **ASCII**, `sort_keys=True`, `separators=(',', ':')`, không whitespace dư
- tính SHA-256 trên **wire bytes cuối cùng**

### 3.2. Canonical authoritative hash phải bind vào forwarded request

Ở guard có hai dạng body:

1. **raw body** agent gửi vào guard
2. **forwarded body** sau `enforce()` — đây là body thực sự đi tới `/v1/responses`

Permit / capture authoritative phải bind vào **forwarded bytes**, vì đây là request đã:

- bị loại bỏ `tools`, `tool_choice`, `parallel_tool_calls`
- bị ép cap `max_output_tokens=600`
- bị ép `service_tier=default`
- bị ép `store=false`

Nếu bind vào raw body hoặc `/v1/runs` body, hash sẽ không bảo vệ đúng request outbound thực tế.

### 3.3. Hash đã tính lại trong phiên này

#### Test fixture từ `mock_contract_test.py`

Canonical test body hiện có trong repo cho `/v1/responses` cho ra:

- bytes: **253**
- SHA-256: **`2806c39b34fe015dba9985897ad3efe000d885eb4271d58e07673736b79ca6bf`**

Serialized wire string:

```json
{"input":[{"content":"task_id=gate-b; correlation_id=fake; channel=ads; spend=25.00; clicks=7","role":"user"}],"instructions":"Reviewed fake instructions","max_output_tokens":600,"model":"gpt-6-luna","service_tier":"default","store":false,"stream":true}
```

#### Live candidate đã được ghi trong evidence cũ

Evidence egress isolation ghi một candidate khác:

- bytes: **3308**
- SHA-256: **`6a12a6786371b683bed0229a2c95c8c222dacb1083a219f5d29a7a02810cf643`**

Do raw capture không nằm trong repo public, H2 chỉ có thể xếp giá trị này là **REPORTED_FROM_EXISTING_EVIDENCE**, không tái tính độc lập từ source tree hiện tại.

## 4. Token-counting contract cho `/v1/responses/input_tokens`

Theo tài liệu OpenAI, endpoint đếm input là:

- `POST /v1/responses/input_tokens`

Mục tiêu H2 không phải suy đoán token từ byte count, mà là **ràng buộc token count với đúng request inference sẽ được dispatch**.

### Contract tối thiểu bắt buộc phải giống inference request

H2 khuyến nghị count request phải được derive từ **forwarded request cuối cùng** bằng cách giữ nguyên các trường ảnh hưởng input surface:

- `model`
- `instructions` (nếu có)
- `input`
- `tools` (nếu có; ở GATE B hiện phải vắng mặt)
- `include` (nếu có)
- `prompt_cache_key` (nếu có)
- `reasoning` (nếu có)
- `service_tier` (giữ `default` để tránh drift cấu hình)

### Trường không nên dùng làm canonical token-count surface

- `stream`
- `store`
- `max_output_tokens`

Các trường này không phải phần input semantic cần model tokenize; `max_output_tokens` là cap output, không phải input surface. Tuy nhiên **hard-cap 600 vẫn phải kiểm ở guard**, chỉ là không nên nhầm nó với token-count input contract.

### Kết luận contract

Canonical flow đúng cho count là:

1. tạo **forwarded request** cuối sau `guard.enforce()`
2. freeze + SHA-256 body đó
3. derive `responses/input_tokens` request bằng projection chỉ giữ input-surface fields như trên
4. ghi lại `count_input_tokens` result cùng **digest của forwarded request**
5. chỉ khi digest count và digest permit trỏ cùng một forwarded request thì mới xem preflight token-count là hợp lệ

## 5. One-shot accounting và callback

### Đã VERIFIED_MOCK trong phiên này

#### `mock_contract_test.py`

PASS cho ba mode:

- `complete` → `usage_recorded`
- `timeout` → `outcome_unknown`
- `truncated` → `outcome_unknown`

Đồng thời xác nhận:

- `exact_wire_digest_match = true`
- `pre_dispatch_consume_observed = true`
- `tamper_dispatched = false`
- `replay_dispatched = false`

#### `one_shot_linux_test.py`

PASS:

- 20 contenders
- 1 admitted / 19 rejected
- replay rejected
- 16 fault cases

#### `one_shot_interop_test.py`

PASS:

- shared lock inode compatibility với adapter Level 2
- attempts = 2
- reserved_usd = 0.007

### Trạng thái “callback + one-shot trong cùng một run”

- **Lịch sử đã có PASS** ở `reports/2026-11-21-hermes-gate-b-guard-remediation-results.md` và evidence companion: mock E2E qua n8n → bridge → Hermes → guard → provider mock → callback, đồng thời ledger mock tăng attempts/reserved và permit `consumed`
- **Checkpoint egress isolation mới hơn** lại ghi rõ:
  - `combined_one_shot_accounting_and_callback = not_run`

### Kết luận hiện tại

- **VERIFIED_HISTORICAL_MOCK:** combined callback + one-shot từng PASS trước đó
- **NOT_RERUN_ON_CURRENT_CHECKPOINT:** sau thay đổi topology egress isolation, combined test chưa được rerun theo evidence mới nhất

Do đó, trước bất kỳ preflight paid nào, next owner nên yêu cầu **một rerun combined mock** trên topology hiện tại để đóng lại khoảng trống này.

## 6. Patch suggestion cho owner tiếp theo

1. **Hạ bridge severity của mismatch cũ bằng fresh task discipline**
   - luôn dùng `fresh task_id` khi kiểm tra sau thay đổi topology
   - nếu cần replay forensics, phân biệt rõ `persisted_failed_state` với `live_runtime_check`

2. **Nếu muốn chẩn đoán live metadata thật sự**
   - log redacted `runtime.requested`, `runtime.model`, `runtime.provider`, `route_source` ngay khi `run_hermes()` poll xong, trước khi state được ghi `failed`
   - lưu hash/log tóm tắt, không lưu secret/body nhạy cảm vào Git public

3. **Khóa canonical digest ở tầng guard forwarded request**
   - không dùng `/v1/runs` digest cho permit hoặc count binding
   - permit, capture và token-count phải cùng tham chiếu digest của forwarded `/v1/responses` body

4. **Thêm combined mock rerun sau egress isolation**
   - rerun mock E2E có callback + one-shot accounting trên topology mới trước paid preflight
   - acceptance: callback 200, attempts +1 trên mock ledger copy, permit `consumed`, replay delta 0

## 7. Kết luận để ChatGPT tổng hợp trước khi giao Codex

- `HERMES_RUNTIME_MISMATCH` **chưa chứng minh** là lỗi metadata live của Hermes trong checkpoint hiện tại.
- H2 chứng minh có một lời giải thích rẻ hơn và phù hợp evidence hơn: **bridge replay failed state theo `task_id`**.
- Canonical request cần khóa cho GATE B là **forwarded `/v1/responses` wire bytes sau guard**, không phải body `/v1/runs`.
- Hash fixture repo hiện tại: **`2806c39b34fe015dba9985897ad3efe000d885eb4271d58e07673736b79ca6bf`** (253 bytes).
- Candidate hash từ evidence live cũ: **`6a12a6786371b683bed0229a2c95c8c222dacb1083a219f5d29a7a02810cf643`** (3308 bytes), currently **reported-only**.
- Token-counting contract phải bind vào **cùng forwarded request digest** và dùng `POST /v1/responses/input_tokens` với cùng `model/instructions/input/tools`.
- One-shot accounting mock đã PASS; callback + one-shot together **đã từng PASS lịch sử nhưng chưa rerun ở checkpoint egress-isolation mới**.

## Next owner

- `next_owner: chatgpt`
- `handoff_state: DONE`
- `recommended_next_action: ChatGPT tổng hợp H1/H2, rồi giao Codex một bước bắt đầu cụ thể: fresh task id, rerun combined mock callback+one-shot trên topology cô lập hiện tại, khóa count-request vào forwarded digest, chỉ sau đó mới đánh giá lại GATE B preflight.`
