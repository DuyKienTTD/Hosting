---
id: hermes-gate-b-h3-preflight-2026-11-21
type: report
status: blocked
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
---

# GATE B H3 — Nghiệm thu mock và trạng thái preflight

**H3 ACKNOWLEDGED → VERIFIED_MOCK / BLOCKED_PREFLIGHT.** Codex đã nhận H3 trực tiếp từ chủ dự án và đọc `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/codex.md` và đặc tả H3 tại commit `9f497608c65273f4ccf2dd9776042c8a3aa2ecf5`. Đối chiếu báo cáo H1/H2 trước khi thao tác. [Task gốc](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Evidence H3](evidence/2026-11-21-ttd-hermes-gate-b-h3.json).

| Hạng mục | Kết quả |
| --- | --- |
| **VERIFIED_LIVE** · Compose và rollback | Đối chiếu Compose đang chạy trên KVM2 với mã bridge, guard, mock contract và one-shot tại Git. Backup Compose và bridge state trước khi áp dụng overlay mock. Chỉ recreate guard và provider mock. Runner xác minh guard và proxy vẫn là hai thành viên duy nhất của mạng riêng trước test, sau recreate và sau rollback. File Compose gốc khớp byte với bản backup. Guard và mock healthy sau rollback. |
| **VERIFIED_MOCK** · Combined E2E | Chạy task giả mới qua n8n sandbox → authenticated bridge → Hermes auxiliary → guard enforcing one-shot → provider mock → authenticated callback. Webhook, callback và replay đều HTTP 200. Provider mock nhận đúng 1 request tổng cộng và tại thời điểm nhận đã thấy permit consumed, ledger inflight và reserve 0,0035 USD trên bản sao. SHA-256 của byte nhận khớp permit. Ledger kết thúc ở `usage_recorded`. Số usage và 0,0003321 USD từ fixture đều là mô phỏng. |
| **VERIFIED_MOCK** · Kiểm tra từ chối | Model sai HTTP 422, service auth sai 401, body bị sửa 503 và task sai 503. Provider nhận 0 request từ bốn ca này. Guard dẫn xuất mock idempotency hash từ task ID, không kiểm tra một provider key thật. Task mới không tái hiện `HERMES_RUNTIME_MISMATCH`. Chưa có chứng cứ xác định nguyên nhân lỗi lịch sử và không đổi metadata validation của bridge. |
| **VERIFIED_LIVE** · Network và production | Sau rollback, bridge, Hermes auxiliary, provider mock, n8n sandbox và hai container production đều bị chặn qua tên proxy và hai IPv4. Guard gọi health proxy HTTP 200. Các container H3 và proxy không publish host port. Production n8n/Hermes HTTP 200 sau test và restart count 0 trước/sau. |
| **BLOCKED_CREDENTIAL** · Strict guard-only | Kiểm tra metadata môi trường và mount trên guard, bridge, Hermes auxiliary, n8n sandbox và mock không thấy OpenAI provider key ở vị trí cấu hình đã biết. Khóa xác thực giữa các service dùng cho nội bộ theo hiện trạng. Chưa có provider key được cấp riêng để xác minh danh tính, quyền Responses, project, quota hoặc billing của guard. |
| **BLOCKED** · Provider token count và cost readiness | Bản gửi mock dài 3.345 byte, model `gpt-6-luna`, `service_tier=default`, output cap 600, không tools. Có digest của byte gửi và digest của projection count gồm model, input, instructions, reasoning lấy từ đúng body đó. Đây là mapping offline cho fixture mock. Chưa gửi endpoint count hoặc có số input tokens của OpenAI gắn với digest. Giá niêm yết và reserve tự thân không xác minh được billing của project. [OpenAI Count input tokens](https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count). |

## Cách kiểm thử và giới hạn

Mã đã chạy trên KVM2 tại `fa320a2db83e805163e70b59689fa60aac807408`. Sáu capture giả gần nhất có sáu giá trị `prompt_cache_key` khác nhau. Overlay chỉ trong H3 dùng cache key tổng hợp cố định để tái tạo bytes từ fixture đã thấy, thay marker bằng task/correlation mới rồi duyệt digest trước khi chạy webhook. Guard tiếp tục xác minh toàn bộ bytes thực gửi. Provider mock độc lập đếm lượt nhận và kiểm tra ledger đã commit. Overlay đã được gỡ. Fingerprint này áp dụng cho phép thử H3 và không cấp quyền sử dụng fixture cho paid inference. [Runner H3](../sandbox/p0-hermes-gate-a/run_h3_mock.sh).

Ledger thật giữ nguyên SHA-256 đầy đủ trước và sau, 1 attempt lịch sử, 0 permit, reserve 0,0035 USD, usage lịch sử ước tính 0,0000496 USD và kill switch ON. Phiên H3 có **0 paid calls và 0 USD chi phí mới**. Không có usage trả phí hoặc hóa đơn mới để đối soát.

## Bàn giao nghiệm thu

Task `TTD-HERMES-GATE-B-001`, từ `codex` tới `chatgpt`, trạng thái `PREPARED_FOR_OWNER_FORWARD`. ChatGPT đối chiếu combined E2E và rollback trong evidence H3 với H1/H2, xác nhận phần mock đủ nghiệm thu và giữ paid preflight blocked. Chủ dự án là owner gỡ blocker credential. Bước đầu tiên là chỉ định credential của đúng project qua secret mount chỉ đọc, chỉ guard truy cập được. Sau đó Codex kiểm tra quyền/billing và thực hiện count miễn phí cho bản cuối, lưu số đếm cùng digest trước khi báo readiness. Chủ dự án chuyển link GitHub cho ChatGPT nếu chưa có kênh trực tiếp đã xác minh.
