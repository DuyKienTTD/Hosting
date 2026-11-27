---
id: n8n-hermes-p0-level2-results-2026-11-21
type: report
status: current
result: partial
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
source: live-hostinger-terminal-tests,openai-responses-usage,official-openai-model-documentation
task: ttd-ai-p0-level2-001
---

# P0 Mức 2 — GPT-6 Luna và nghiệm thu Hermes E2E

## Kết luận

| Acceptance độc lập | Trạng thái | Kết luận |
|---|---|---|
| `PROVIDER_E2E` | **PASS** | n8n sandbox → private adapter → OpenAI GPT-6 Luna → authenticated callback → n8n đã chạy live bằng fake data |
| `HERMES_E2E` | **BLOCKED_COST_CONTROL** | không gọi model qua Hermes Agent vì CLI/runtime thật chưa chứng minh được hard output-token cap trước request và chưa có private callback inference route |
| P0 tổng thể | **PARTIAL / BLOCKED** | Provider đạt; không dùng Provider PASS để thay bằng chứng Hermes |

Bằng chứng máy đọc: [JSON đã khử bí mật](evidence/2026-11-21-ttd-ai-p0-level2-001.json). Mã triển khai secret-free: [sandbox/p0-level2](../sandbox/p0-level2/README.md).

## GATE 0 và giới hạn chi phí

- Tài liệu chính thức xác nhận [`gpt-6-luna`](https://developers.openai.com/api/docs/models/gpt-6-luna), Responses API và structured outputs. `GET /v1/models/gpt-6-luna` bằng API key được cấp trả HTTP 200 trước paid call.
- Giá standard đã dùng để đối soát: USD 0,10/1M input token và USD 0,50/1M output token. Không khai báo tool, không web search/grounding/media, `service_tier=default`, `reasoning.effort=none`, `store=false`.
- Upper bound được duyệt 4.000 input + 2.000 output tương ứng USD 0,0014/call theo giá standard. Ledger reserve USD 0,0035 trước mỗi attempt, tức 2,5 lần upper bound standard; năm reservation là USD 0,0175, thấp hơn cap USD 0,05.
- Request live dùng hard `max_output_tokens=600`, thấp hơn cap 2.000. Prompt + JSON schema có ceiling 2.500 byte ASCII trước gửi; response thực tế chỉ dùng 131 input token.
- Admission control dùng `flock`, ghi atomic bằng `fsync` + `replace`, persistent ngoài container. Mọi attempt được reserve trước dispatch; không provider auto-retry; replay cùng `task_id` dùng ledger và không tạo call mới.
- Sau nghiệm thu, kill switch persistent được bật. Request mới nhận HTTP 429 `P0_KILL_SWITCH`; task đã hoàn tất vẫn replay read-only. Ledger cuối: 1 attempt, USD 0,0035 reserved, USD 0,0000496 usage-based actual.

Không có API provider billing endpoint phù hợp trong quyền hiện tại để xác nhận số tiền đã chốt trên hóa đơn. `actual_usd` là phép tính trực tiếp từ usage trả về và đơn giá chính thức; billing dashboard/invoice có thể cập nhật trễ. Live inference thành công đồng thời xác nhận credential, model access và account authorization thực tế.

## Provider E2E — PASS

Route live:

```text
n8n sandbox authenticated webhook
  → ttd-p0-reasoner (private, no published port)
  → allowlist CONNECT proxy
  → api.openai.com:443 / Responses API / gpt-6-luna
  → structured JSON Schema result
  → authenticated callback
  → n8n callback schema validation HTTP 200
```

| Thuộc tính | Kết quả |
|---|---|
| Paid attempts | **1** |
| Model request / response | `gpt-6-luna` / `gpt-6-luna` |
| Input / cached input | 131 / 0 token |
| Output / reasoning | 73 / 0 token |
| Usage-based actual cost | **USD 0,0000496** |
| Worst-case reservation | USD 0,0035 |
| Authenticated callback | HTTP 200, schema PASS |
| Result hash | `2619668a01837c789366ef581d5009f0f053db2279781374fc5eeb67baed946d` |
| Provider response-ID hash | `e2b6af8620674547a656dc17713c986c91706b0422926b8fb31ce86c5aa35459` |

Test không tốn thêm call: thiếu auth 401; sai auth 401; input schema sai 422; replay 200; idempotency conflict 409; ledger vẫn đúng 1 attempt. Bộ test admission concurrent cho 10 task chỉ admit 5, block 5 và reserve USD 0,0175; kill switch block task mới trước provider.

Adapter không phải Hermes Agent. Process của nó là Python `/opt/ttd/adapter.py`; vì vậy kết quả này chỉ nghiệm thu `PROVIDER_E2E`.

## Hermes Agent E2E — BLOCKED_COST_CONTROL

Điều tra read-only xác nhận image có Hermes CLI thật và one-shot `hermes -z/--oneshot`, nhưng:

- CLI one-shot chỉ expose model/tool/safe-mode/usage-report controls; không expose `max_output_tokens` hoặc `max_tokens` hard limit.
- `--usage-file` chỉ ghi usage sau khi run, không phải admission gate trước paid request.
- Help mô tả one-shot tự bypass approval và vẫn nạp tools/memory/rules theo mặc định; có thể giảm bề mặt bằng safe-mode/toolsets nhưng không giải quyết output cap.
- Default config trong container cô lập chỉ cho thấy model `(auto)`; chưa có bằng chứng config nào ép GPT-6 Luna và truyền hard max output xuống provider cho one-shot.
- Hermes production vẫn là dashboard/runtime chính, không expose private inference callback API. Không restart/recreate/sửa config Hermes chính.

Theo stop condition, không dùng paid call thứ hai để thử CLI khi upper bound chưa chứng minh được. `HERMES_E2E` có 0 paid call và không được ghi PASS.

## Isolation, backup và production safety

- Thêm đúng một auxiliary egress proxy; proxy là attachment duy nhất trên network egress và chỉ chấp nhận CONNECT tới `api.openai.com:443`. Probe `example.com` bị chặn. Không mở inbound/public port.
- Ba auxiliary container cuối đều `healthy`; n8n sandbox chỉ có `5678/tcp` nội bộ. Internal P0 network vẫn `internal=true`.
- Secret file và ledger mode `600`; thư mục state mode `700`; không phát hiện bearer token/API key trong 200 dòng log cuối của adapter/n8n.
- Backup pre-change root-only có source, env và n8n data. Rollback script qua `sh -n`; rollback Level 2 không được diễn tập sau live call để giữ ledger/evidence, trong khi rollback/restore Level 1 đã PASS trước đó.
- n8n và Hermes production cuối cùng running, restart count 0; n8n readiness HTTP 200; Hermes dashboard HTTP 200. Không thay production credential, encryption key, DNS, firewall, public port hoặc business account.

## Thay đổi và blocker

Đã thay chỉ runtime phụ: provider adapter, persistent ledger/kill switch, egress allowlist proxy và callback validator của workflow sandbox. Mọi secret vẫn ngoài Git.

Để bỏ blocker Hermes cần một thay đổi kỹ thuật riêng: runtime Hermes phụ đã pin/kiểm chứng phải có hard `max_output_tokens<=2000`, model exact `gpt-6-luna`, tools disabled, atomic budget reservation trước provider và authenticated callback n8n. Chưa được phép coi wrapper gọi OpenAI trực tiếp là Hermes.
