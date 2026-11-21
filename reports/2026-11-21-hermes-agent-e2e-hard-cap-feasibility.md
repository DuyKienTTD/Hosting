---
id: hermes-agent-e2e-hard-cap-feasibility-2026-11-21
type: report
status: complete
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-e2e-hard-cap-001
result: go_for_separate_implementation_approval
---

# Khảo sát hard-cap cho Hermes Agent E2E

## Kết luận

**GO cho một đợt triển khai riêng có phê duyệt; chưa GO cho paid Hermes E2E.** Hermes Agent thật có thể được giữ nguyên và đặt sau một inference guard riêng. Guard là điểm egress duy nhất, sửa/ép request thành `model=gpt-6-luna`, `max_output_tokens=600`, không trường tools, rồi giữ lock và reserve vào **cùng ledger P0** trước khi gửi provider. Cấu hình/CLI Hermes upstream đơn thuần không đáp ứng hard-cap.

Không gọi lại GPT-6 Luna trong khảo sát này. Kill switch vẫn bật; số paid call mới là 0; không đổi container, mạng, secret, port, firewall, DNS hay production.

Hermes Agent E2E vẫn là `BLOCKED_COST_CONTROL` cho đến khi kiến trúc được phê duyệt, triển khai cô lập, rehearsal toàn tuyến bằng provider mock đạt và một paid test riêng được cho phép.

## Những gì đã xác minh

| Hạng mục | Trạng thái | Bằng chứng |
|---|---|---|
| Runtime Hermes thật | VERIFIED | Container chính chạy image Hostinger Hermes digest `sha256:0ea6...344f`, CLI `/usr/local/bin/hermes`, Hermes `0.22.5`, upstream commit `bf0203a7`; restart count 0. Image metadata và help được đọc trực tiếp, không thay runtime. |
| Hard-cap bằng CLI/config | BLOCKED | CLI one-shot không có `--max-tokens`; tài liệu upstream nói các cấu hình `model.max_tokens`, `HERMES_MAX_TOKENS` và provider output-cap cũ không còn được đọc. |
| Serializer Responses | VERIFIED_OFFLINE | Trên đúng image live, gọi `ResponsesApiTransport.build_kwargs` không tạo network: `gpt-6-luna`, `max_output_tokens=600`, không có `tools`, `store=false`. |
| Exact model | VERIFIED_OFFLINE | Model được pin trong request serializer; guard rehearsal từ chối model khác. |
| Tools disabled | VERIFIED_OFFLINE | Profile `platform_toolsets.cli: []` trả về zero toolset/zero tool definition trên image live; serializer bỏ hẳn trường `tools`. |
| Shared atomic budget gate | VERIFIED_AS_CONTRACT | Rehearsal secret-free bắt đầu từ bản sao ledger hiện tại: 1 attempt/USD 0.0035 reserved. Mười thread đồng thời chỉ admit 4, block 6, kết thúc 5 attempts/USD 0.0175. Kill switch và mọi request sai bị chặn mà ledger không đổi; stress test lặp 100 lần PASS. |
| Authenticated Hermes API | VERIFIED_UPSTREAM | API server upstream yêu cầu `API_SERVER_KEY`, hỗ trợ `POST /v1/runs`, idempotency, polling và SSE. Chưa triển khai trên VPS. |
| Authenticated callback n8n | PLANNED | Bridge sẽ poll/SSE run của Hermes và callback đúng webhook sandbox hiện có bằng bearer token dành riêng. Chưa triển khai. |
| Input ≤4K | BLOCKED_PENDING_REHEARSAL | Guard có thể áp envelope ASCII ≤4,000 byte, nhưng full serialized request gồm system prompt Hermes chưa được capture qua mock guard; nếu vượt phải STOP hoặc dùng runner/profile tối giản được phê duyệt. |

Evidence máy đọc được: [2026-11-21-ttd-hermes-e2e-hard-cap-001.json](evidence/2026-11-21-ttd-hermes-e2e-hard-cap-001.json). Rehearsal: [offline_guard_contract_test.py](../sandbox/p0-hermes-feasibility/offline_guard_contract_test.py).

## Cơ sở mã nguồn

Đã đối chiếu tag live `v0.22.5` với commit immutable `bf0203a794a07aac3ff764972ab9087baa4e4f4e`:

- Upstream [loại bỏ các output-cap setting cũ](https://github.com/NousResearch/hermes-agent/blob/bf0203a794a07aac3ff764972ab9087baa4e4f4e/website/docs/integrations/providers.md#L1294-L1300). Vì vậy chỉ đặt config hoặc env không phải hard gate.
- Transport Responses [chuyển `max_tokens` thành `max_output_tokens`](https://github.com/NousResearch/hermes-agent/blob/bf0203a794a07aac3ff764972ab9087baa4e4f4e/agent/transports/codex.py#L869-L870), và API khởi tạo agent [nhận `max_tokens`](https://github.com/NousResearch/hermes-agent/blob/bf0203a794a07aac3ff764972ab9087baa4e4f4e/agent/agent_init.py#L2273). Đây là khả năng programmatic, chưa được expose bởi CLI one-shot hiện tại.
- Danh sách toolset được lưu rõ ràng, kể cả `[]`, là cấu hình hợp lệ theo [tools_config](https://github.com/NousResearch/hermes-agent/blob/bf0203a794a07aac3ff764972ab9087baa4e4f4e/hermes_cli/tools_config.py#L565-L581).
- `pre_api_request` và `pre_auxiliary_call` chỉ là observer, return bị bỏ qua theo [hook contract](https://github.com/NousResearch/hermes-agent/blob/bf0203a794a07aac3ff764972ab9087baa4e4f4e/website/docs/user-guide/features/hooks.md#L460-L463); plugin hook không thể làm spend gate.
- API server có [Bearer auth](https://github.com/NousResearch/hermes-agent/blob/bf0203a794a07aac3ff764972ab9087baa4e4f4e/website/docs/user-guide/features/api-server.md#L864-L870) và `/v1/runs` có [idempotency reservation](https://github.com/NousResearch/hermes-agent/blob/bf0203a794a07aac3ff764972ab9087baa4e4f4e/website/docs/user-guide/features/api-server.md#L553-L569).

## Các phương án

### A — Chỉ cấu hình/CLI upstream

Pin `--model gpt-6-luna`, đặt `platform_toolsets.cli: []`, chạy one-shot/API server và dùng usage file hậu kiểm.

- Ưu: không thêm proxy, ít mã vận hành.
- Nhược: không có supported hard output cap trước request; usage file là hậu kiểm; observer hook fail-open và không thể sửa/chặn request; retries/auxiliary calls có thể vượt admission gate.
- Kết luận: **NO-GO**. Không đạt yêu cầu chi phí.

### B — Hermes phụ nguyên bản + private inference guard

Chạy Hermes API server phụ, pin đúng image digest/tag và profile riêng. Hermes không giữ provider key và không có direct provider egress. Mọi provider request đi qua guard nội bộ; guard là thành phần duy nhất giữ provider key và có egress.

- Guard chỉ nhận `/v1/responses`; ép model/cap, từ chối tools, model/path khác, input quá giới hạn và request không hợp lệ **trước reservation**.
- Guard giữ exclusive lock, dùng đúng ledger P0 hiện có, idempotency key và worst-case USD 0.0035/call. Retry, fallback và auxiliary call không thể bypass vì Hermes không có đường mạng/provider credential khác.
- Bridge xác thực n8n, tạo `/v1/runs` với correlation/idempotency ID, poll/SSE, kiểm tra terminal state/model/usage rồi callback webhook sandbox có auth.
- Ưu: không fork Hermes, chặn được mọi physical provider attempt ở network boundary, rollback độc lập.
- Nhược: thêm hai thành phần nội bộ; phải chứng minh full Hermes prompt ≤4K và chặn mọi direct egress.
- Kết luận: **RECOMMENDED**.

### C — Minimal real-Hermes runner có patch

Khởi tạo `AIAgent(max_tokens=600, enabled_toolsets=[])` trực tiếp, bỏ context/memory/background review và vẫn đặt sau guard.

- Ưu: cap có defense-in-depth tại serializer, giảm prompt và auxiliary behavior.
- Nhược: phải duy trì wrapper/patch theo commit upstream; bề mặt khác CLI/API server chuẩn.
- Kết luận: dự phòng nếu API server chuẩn không giữ input dưới 4K; chỉ triển khai sau code review và pin source commit.

## Kiến trúc đề nghị

```text
n8n sandbox
  -> authenticated bridge
  -> Hermes 0.22.5 auxiliary /v1/runs (tools=[], one turn)
  -> private inference guard (policy + shared ledger lock)
  -> OpenAI Responses API
  -> bridge -> authenticated n8n callback
```

Chỉ guard được nối mạng egress và giữ provider credential. Hermes/bridge ở internal network, không publish host port. Profile Hermes riêng không mount production state, không context files, memory, MCP, skill, sub-agent, fallback model, background review hay recursive reasoning; max turn/iteration là 1. Guard chỉ cho đúng endpoint và exact model; không hỗ trợ endpoint phụ ngoài metadata cục bộ tối thiểu nếu runtime bắt buộc.

## Preflight và nghiệm thu không phí

1. Pin image digest và upstream commit; backup compose/config/ledger, ghi health/restart production.
2. Tạo root-only directory `700`, secret files `600`; không reuse/chạm production encryption key hay credentials.
3. Dùng provider mock capture full request. Assert một request duy nhất, exact model, `max_output_tokens=600`, không tools/tool choice, không fallback/auxiliary call và conservative input envelope ≤4,000 byte hoặc model tokenizer ≤4,000 tokens.
4. Chạy negative auth/schema/model/tools/path/oversize; callback auth, timeout, retry, idempotency conflict và terminal error.
5. Chạy concurrency từ **bản sao** ledger state 1 attempt; chỉ 4 admission. Chứng minh mọi network path khác bị deny.
6. Giữ kill switch bật trong toàn bộ rehearsal. Nếu bất kỳ bypass, extra request hoặc input >4K xuất hiện: STOP và rollback.
7. Chỉ sau một phê duyệt paid-test mới được unlock có kiểm soát cho đúng một task; paid result phải chứng minh đây là Hermes run, không phải adapter gọi thẳng provider.

## Ngân sách và tác động

- Ledger hiện tại: 1 paid attempt; USD 0.0035 reserved; USD 0.0000496 usage-based actual, hóa đơn chưa đối soát; kill switch bật.
- Còn tối đa 4 attempt theo approval cũ. Nếu mỗi attempt tiếp tục reserve USD 0.0035 thì tổng reserved tối đa là USD 0.0175, dưới trần USD 0.05. Con số này không tự cấp quyền gọi tiếp.
- Đề nghị giới hạn dự kiến: Hermes phụ 1.5 GB RAM/1 CPU, bridge+guard mỗi thành phần 256 MB/0.25 CPU, read-only root filesystem/capabilities dropped khi phù hợp. Phải đo memory pressure trước triển khai; không recreate production.
- Rollback: bật/giữ kill switch, stop/remove chỉ các container phụ, detach private networks, restore compose/config/ledger backup nếu integrity check thất bại. Không xóa evidence/state cho tới review.

## Các thay đổi cần phê duyệt

1. Triển khai Hermes auxiliary, bridge và inference guard trên private network, gồm resource limits và image/source pin.
2. Cho guard dùng cùng ledger P0 và là nơi duy nhất giữ provider credential; sửa sandbox compose/egress policy để Hermes không thể đi thẳng provider.
3. Tạo `API_SERVER_KEY` và guard service token mới bằng CSPRNG, lưu `700/600`; callback tiếp tục dùng đúng bearer của một webhook sandbox hiện hữu.
4. Một cửa sổ rehearsal offline/mock; chưa cần mở kill switch hoặc paid egress.
5. Sau khi mock PASS, phê duyệt riêng cho đúng một Hermes paid call, thời điểm unlock/relock kill switch và ngân sách reserve USD 0.0035. Không được suy diễn approval Mức 2 cũ thành quyền thực thi bước này.

## Điều kiện STOP

STOP nếu không chứng minh được exact image/model, full input ≤4K, no-tools, one-turn/no auxiliary request, shared ledger lock, no direct egress, authenticated callback hoặc health/rollback. STOP ngay nếu cần recreate/restart production, mở public port/firewall/DNS, dùng dữ liệu thật, thêm phí ngoài cửa sổ được duyệt hay ledger/kill switch không khớp.
