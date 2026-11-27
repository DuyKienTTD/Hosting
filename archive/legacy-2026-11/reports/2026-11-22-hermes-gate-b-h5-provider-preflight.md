---
id: hermes-gate-b-h5-provider-preflight-2026-11-22
type: report
status: blocked
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
source: live-kvm2-web-terminal,repository-code,official-openai-docs
task_id: ttd-hermes-gate-b-001
owner: codex
---

# GATE B H5 — Provider preflight

**MODEL_METADATA_PASS / BLOCKED_FINAL_REQUEST_AND_PROJECT_VERIFICATION.** Guard truy cập được metadata GPT-6 Luna qua proxy đã duyệt. H5 còn thiếu một forwarded request có thể khóa digest vào đường thực thi sẽ dùng và bằng chứng quản trị của project tương ứng. Gate B paid tiếp tục `BLOCKED_PREFLIGHT`. [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-h5.json).

**ACKNOWLEDGED** từ chủ dự án cho `H5_PROVIDER_PREFLIGHT`. Rule và task commit đã đọc `9067ccd21f8b7a939e93b511da8cb825b0740918`. Tái sử dụng H3 mock accounting/callback và H4 mount/isolation theo topology đã nghiệm thu. Kiểm tra mới tập trung vào hash mã thực thi, mount metadata, health, ledger và quyền metadata model. [Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Guard mount](2026-11-22-hermes-gate-b-guard-mount-results.md).

| Điều kiện | Kết quả |
| --- | --- |
| Mount và egress | `PRESENT`, mode `0600`, mount chỉ đọc duy nhất tại Guard. Guard/proxy healthy, Guard tới proxy health HTTP 200. Xác nhận membership và network IDs vẫn khớp baseline mount. Tái sử dụng 18 phép thử cách ly đã PASS ở cùng topology. |
| Model access | Một `GET /v1/models/gpt-6-luna` từ process tạm bên trong Guard qua allowlist CONNECT proxy và TLS verification trả HTTP 200, exact model ID. Credential chỉ dùng trong bộ nhớ process để tạo header xác thực. Không đưa credential vào CLI args, env, log hoặc output. |
| Project, Responses, billing/quota | `UNKNOWN`. Kết quả GET chứng minh quyền đọc metadata cho credential đang mount. Không có tab dashboard OpenAI đang mở trong phiên Chrome đã chọn hoặc bằng chứng quản trị đối chiếu key với project đích, quyền Responses create, billing và quota. Dữ kiện provider từ Level 2 dùng credential khác hoặc chưa chứng minh là cùng credential. |
| Guard runtime và final digest | `BLOCKED_RUNTIME_CONTRACT`. SHA-256 của `guard.py` đang mount khớp mã tại `1953a81`, khác bản repo hiện tại `69dd952`. Đối chiếu AST và mã lịch sử xác nhận runtime chỉ gửi đến mock, không có `freeze()` hoặc one-shot handler. Bản repo có các cơ chế này cho mock và H3 xử lý giá trị cache key động qua overlay thử nghiệm đã rollback. Chưa có final digest gắn với một đường chạy provider đã xét duyệt. Không dùng body `/v1/runs`, capture từ mock live hoặc fixture H3 làm bằng chứng thay thế. |
| Token counting | `NOT_RUN`. Hãng xác nhận endpoint đếm miễn phí và trả số token của input đầy đủ. Hai điều kiện còn thiếu là xác minh project và final digest có thể tái tạo. [Token counting](https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens) · [API reference](https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count). |
| Budget phương án | Đối chiếu ngày 2026-11-22 ICT. Standard USD 0,10/1M input và 0,50/1M output. Với 4.000 input và 600 output gồm reasoning, trần token cơ bản USD 0,000700, hoặc USD 0,000800 nếu toàn bộ input tính theo 30m cache write ở USD 0,125/1M. Nếu áp phụ phí vùng 10%, kịch bản sau là USD 0,000880. Giả định Standard, không tool, không cache write 12h. USD 0,0035 là reserve ứng viên từ bằng chứng trước, dưới cap từng job USD 0,01. Hai reservation như vậy tổng USD 0,007, dưới các cap USD 0,05. Project tier, quota/billing, charge policy cuối và số token theo digest còn thiếu để duyệt reserve chính thức. [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) · [Pricing](https://developers.openai.com/api/docs/pricing). |
| One-shot và callback | Có bằng chứng nguyên tử/durable và callback trên mock H3. Ledger thật đang mount read-only và Guard runtime không có admission one-shot. H5 có 0 permit, 0 one-shot task record, 1 historical attempt, kill switch ON. |
| Bất biến trước/sau | n8n/Hermes HTTP 200 và restart 0. Guard source SHA, real ledger SHA, trạng thái Guard/proxy, mount, network IDs và Compose khớp baseline. Không recreate. Một GET metadata, 0 token-count calls, 0 paid inference attempts và 0 USD phát sinh từ inference. |

## Bàn giao

`from_agent: codex`, `to_agent: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`.

ChatGPT nghiệm thu từng kết quả H5 và phối hợp chủ dự án đối chiếu project/key record, quyền Responses, tier, billing và quota từ dashboard quản trị bằng metadata đã khử nhạy cảm. Bước kỹ thuật kế tiếp cần phạm vi sandbox riêng để chốt đường freeze thực tế trước provider, kiểm tra tính tái lập trên request giả mới và chứng minh one-shot/admission qua mock ở đúng cấu hình sẽ dùng. Từ chính bytes chốt sau enforcement, tạo projection để gọi token count qua Guard, lưu count cùng digest và tính reserve theo tier đã xác nhận. Chỉ xem xét H6 sau khi các điều kiện còn thiếu được nghiệm thu.
