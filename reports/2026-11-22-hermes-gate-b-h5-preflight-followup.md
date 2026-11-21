---
id: hermes-gate-b-h5-preflight-followup-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
source: live-kvm2-web-terminal,openai-project-dashboard,repository-mock,official-openai-docs
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H5 Provider Preflight — Kết quả Codex

**PROVIDER_PREFLIGHT_PASS**, chờ ChatGPT nghiệm thu H5. Gate B paid tiếp tục `BLOCKED_PREFLIGHT` đến khi tuyến thực thi H6 được duyệt và xác minh. H5 phát sinh 0 paid inference, 0 USD chi phí inference và 0 permit thật.

**ACKNOWLEDGED** từ chủ dự án. Quy tắc và task đã đọc tại commit `e69c1901f288aca4ddc2d5bd0209e53533ea3212`. Tái sử dụng H3 callback, hạch toán và fault tests cùng H4 Guard mount và isolation. Báo cáo này xử lý các điểm còn thiếu của lần đo H5 trước. [Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Lần đo trước](2026-11-22-hermes-gate-b-h5-provider-preflight.md) · [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-h5-followup.json).

| Điều kiện | Bằng chứng |
| --- | --- |
| Project, model và quyền Responses | Dashboard OpenAI xác thực hiển thị service-account key Active, Inherited và không có hạn chế riêng ở cấp key. Hậu tố hiển thị đã che khớp key đang mount qua phép so sánh trong Guard chỉ trả boolean. Project cho phép `gpt-6-luna`. GET model với project/org headers đã đối chiếu trả HTTP 200 và exact model. Quyền create dựa trên cấu hình quản trị và quyền mặc định read/write của project service account. Bằng chứng live cho Responses là HTTP 200 ở endpoint đếm token. Create endpoint chưa được thực thi trong H5. [OpenAI Project management](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform). |
| Billing và quota | Dashboard ngày 2026-11-22 ICT cho thấy Standard tier, Global residency, billing Pay as you go, số dư tín dụng dương và quota GPT-6 Luna có cấu hình ở tổ chức. Số quota còn lại trong cửa sổ rate limit không được đo. [Model](https://developers.openai.com/api/docs/models/gpt-6-luna) · [Pricing](https://developers.openai.com/api/docs/pricing). |
| Callback và request ứng viên | Một probe n8n sandbox riêng trả webhook và callback HTTP 200 qua bridge → Hermes → Guard → mock. Với task ID ứng viên khác, hai lượt chạy Hermes dùng cùng input và correlation, mỗi lượt có idempotency key thử riêng. Sau khi loại `prompt_cache_key` động và freeze sau enforcement, hai capture cho cùng 3.304 bytes. Task ID ứng viên chưa có record trong live bridge tại lúc đo. Không tái sử dụng probe n8n đã qua bridge làm ứng viên H6. |
| Digest và token count | SHA-256 ứng viên `e66603e05a4a9b0d7a4bbd7b9142a89e15e38176c2fe1fddbf3dd5764ff1a929`. Guard xác minh digest trước khi chiếu `model`, `input`, `instructions`, `reasoning` vào endpoint đếm token. Qua proxy allowlist và TLS xác minh, OpenAI trả HTTP 200 và **723 input tokens**. Dùng request giả cho cả hai lần đếm. Số 719 của probe n8n chỉ dùng để kiểm tra phương pháp. Ứng viên có một turn, không tools, `reasoning.effort=none`, `store=false`, `service_tier=default` và hard cap 600 output tokens gồm reasoning. [Token counting](https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens) · [API reference](https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count). |
| Chi phí | Standard USD 0,10/1M input và 0,50/1M output. Ước lượng tối đa USD 0,0003723 cho 723 + 600 tokens không cache, hoặc USD 0,000390375 nếu tính toàn bộ input theo giá ghi cache 30 phút USD 0,125/1M. Tại trần 4.000 + 600 tokens và cùng giả định cache, mức tương ứng tối đa USD 0,000800. Phép tính dùng Global, không tools và không cache 12h. Reserve ứng viên USD 0,0035 dưới cap USD 0,01/job. Cộng reservation đã ghi nhận USD 0,0035 cho kết quả USD 0,007, dưới cả cap ngày và P0 USD 0,05. Tổng attempts dự kiến 2/5 nếu thêm một lượt. [Pricing](https://developers.openai.com/api/docs/pricing). |
| One-shot và exact bytes | Guard từ mã repo đã đối chiếu hash gửi đúng bytes ứng viên trong một test HTTP loopback với ledger độc lập. Mock quan sát permit `consumed` và task `inflight` cùng reserve đã ghi trước khi nhận request. Request sửa instructions và replay đều HTTP 503, không dispatch. Lượt hợp lệ trả 200 và ghi mock usage. Lần thử đầu gọi enforcement trước khi fixture được khởi tạo nên dừng do thiếu file ledger. Chạy qua HTTP harness khởi tạo đúng ledger và phép thử đạt. |
| Bất biến live | Guard vẫn dùng mã Gate A `1953a81` và upstream mock. Guard/proxy healthy, Compose, membership mạng và Guard-only mount chỉ đọc khớp baseline. Dùng lại 18 phép thử cách ly đã PASS. Production n8n/Hermes HTTP 200, 0 restart. Ledger thật khớp từng byte, 1 historical attempt, 0 permits, kill switch ON. Phiên này có 1 GET metadata, 2 lần đếm token và 0 create request đến OpenAI. |

## Bàn giao H6

`from_agent: codex`, `to_agent: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`. ChatGPT nghiệm thu report/evidence và dùng các mẫu H3 hiện hành để chốt đặc tả delta H6 trong cùng task.

1. Duyệt phiên bản sandbox Guard tích hợp transport provider qua proxy đã duyệt, dùng key chỉ trong Guard và hạch toán thật. Mã live hiện chỉ có mock. Kiểm thử atomic reserve/consume với exact digest, khóa replay, hạch toán thành công và giữ reserve khi outcome không xác định. Kill switch luôn ON. Xác minh rollback và ranh giới egress trước phê duyệt triển khai.
2. Đối chiếu bytes cuối **qua đúng tuyến H6** sau enforcement và chính sách chuẩn hóa `prompt_cache_key`. Xác minh lại task/idempotency chưa dùng, digest, budget và quota trước mọi permit thật. Nếu bytes đổi, khóa digest mới và đếm lại đúng request. Candidate JSON được giữ riêng với quyền đọc root. H6 tìm bản theo digest trong thư mục private do H5 tạo và kiểm lại hash trước khi dùng.
3. Chỉ tiến tới một paid attempt sau nghiệm thu và đủ quyền theo task. Mỗi mismatch hoặc timeout cần giữ trạng thái fail-closed. Áp dụng quy tắc không retry, xác minh callback, usage/hạch toán và rollback trong H6.
