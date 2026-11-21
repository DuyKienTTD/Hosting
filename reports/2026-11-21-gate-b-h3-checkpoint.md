---
id: gate-b-h3-checkpoint-2026-11-21
type: report
status: current
updated_at: 2026-11-21
sensitivity: public-redacted
source: hermes-gate-b-h3-preflight-2026-11-21
task_id: ttd-hermes-gate-b-001
owner: codex
---

# Checkpoint TTD METAL — GATE B sau H3

**Điểm tiếp tục:** H3 đã PASS mock toàn tuyến. GATE B trả phí vẫn `BLOCKED_PREFLIGHT / BLOCKED_CREDENTIAL`. Hồ sơ đang chờ chuyển cho ChatGPT để nghiệm thu, trạng thái `PREPARED_FOR_OWNER_FORWARD`. [Task gốc](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Báo cáo H3](2026-11-21-hermes-gate-b-h3-preflight.md) · [Evidence H3](evidence/2026-11-21-ttd-hermes-gate-b-h3.json).

## Bằng chứng dùng lại

| Hạng mục | Trạng thái tại lần kiểm tra H3 |
| --- | --- |
| n8n → Hermes → guard → mock → callback | **DONE_VERIFIED** trên KVM2. Webhook/callback HTTP 200, đúng 1 dispatch mock, permit và reservation đã ghi bền vững trước khi mock nhận, usage đã ghi, replay không dispatch thêm. |
| Cách ly proxy và rollback | **DONE_VERIFIED**. Guard truy cập được proxy, sáu container đối chứng bị chặn. Compose gốc giữ nguyên từng byte sau rollback. n8n/Hermes production HTTP 200, restart count 0. |
| Ledger thật | **DONE_VERIFIED** trước/sau H3. SHA-256 không đổi, 1 attempt lịch sử, 0 permit, kill switch ON. H3 có 0 lượt trả phí và 0 USD mới. |
| Credential OpenAI, billing và đếm input | **BLOCKED**. Guard chưa có credential provider riêng đã xác minh. Digest của fixture và của dữ liệu đếm token đã ghi trong evidence. Chưa có số input tokens từ OpenAI cho request cuối. |

Mã đã kiểm thử `fa320a2db83e805163e70b59689fa60aac807408`. Báo cáo/evidence H3 tại `2e7fa11a96d0bfbf60bc90d545bcdff3833add66`. Checkpoint chỉ tổng hợp bằng chứng hiện có. Khi tiếp tục, dùng lại kết quả nếu mã, cấu hình, topology và tiêu chí tương đương. Chỉ kiểm thử lại phần bị ảnh hưởng khi có thay đổi hoặc lỗi mới.

## Bước đầu tiên khi tiếp tục

1. ChatGPT nghiệm thu H3 từ báo cáo/evidence. Chủ dự án xác định credential của đúng project theo phạm vi đã duyệt và cấp qua secret mount chỉ đọc dành riêng cho guard. Không gửi giá trị key qua chat hay GitHub.
2. Khi credential sẵn sàng, Codex xác minh quyền Responses, project, billing và egress. Dùng phương thức đếm input miễn phí trên dữ liệu suy ra từ request cuối sau guard rồi lưu kết quả cùng SHA-256 của chính request đó. Tiếp tục dừng ở preflight nếu thiếu bằng chứng hoặc vượt giới hạn theo ADR. [ADR-P0-003](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md).

**Phạm vi checkpoint.** Commit quy tắc và base đọc `4722b2da4f6727ba5267a84d60ba9124875cdfd6`. Chỉ ghi checkpoint, danh mục và changelog. Task gốc, phê duyệt, evidence H3, cấu hình VPS và ledger là bất biến trong lần lưu này.
