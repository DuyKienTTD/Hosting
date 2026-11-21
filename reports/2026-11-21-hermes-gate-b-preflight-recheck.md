---
id: hermes-gate-b-preflight-recheck-2026-11-21
type: report
status: blocked
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
---

# GATE B — Kiểm tra lại trước lượt Hermes trả phí

**BLOCKED_PREFLIGHT.** Dừng trước dispatch vì bridge kết nối được proxy Level 2 đang có egress, còn guard đang chạy chỉ dùng upstream mock. Quyền Responses của credential dành cho guard và số input tokens của request cuối qua provider cũng chưa được xác minh. Phiên này có **0 paid attempts và 0 USD chi phí API mới**. [Nhiệm vụ](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [ADR-P0-003](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md) · [Evidence đã khử bí mật](evidence/2026-11-21-ttd-hermes-gate-b-preflight-recheck.json).

| Điều kiện | Kết quả ngày 2026-11-21 |
| --- | --- |
| Model và giá niêm yết | **PASS** cho `gpt-6-luna` trên Responses API ở Standard. Giá USD trên một triệu tokens là 0,10 input thường, 0,01 input đọc cache, 0,125 ghi cache 30 phút và 0,50 output. Với 4.000 input và 600 output, mức cơ bản là 0,000700 USD và giới hạn bảo thủ là 0,000800 USD nếu toàn bộ input bị tính giá ghi cache 30 phút. Các phép tính áp dụng cho endpoint toàn cầu, request text, `service_tier=default`, không tools và không ghi cache 12 giờ. Reasoning đã nằm trong output. Reservation 0,0035 USD lớn hơn mức này và sẽ nâng tổng reserve từ 0,0035 lên 0,007 USD nếu admission hợp lệ. [Model](https://developers.openai.com/api/docs/models/gpt-6-luna) · [Pricing](https://developers.openai.com/api/docs/pricing) · [Caching](https://developers.openai.com/api/docs/guides/prompt-caching) · [Responses](https://developers.openai.com/api/reference/python/resources/responses/methods/create). |
| Quyền provider | **Xác minh một phần.** Dashboard hiển thị `gpt-6-luna` được phép tại project đã xem và một service-account key đang active, có quyền kế thừa, không có hạn chế riêng ở cấp key. Key của Level 2 từng gọi thành công. Chưa đối chiếu danh tính credential sẽ được mount vào paid guard, quyền Responses hữu hiệu, billing và quota của chính đường chạy đó. Không gọi API provider trong lượt kiểm tra này. [Evidence Level 2](2026-11-21-n8n-hermes-p0-level2-results.md). |
| Paid route và no-bypass | **FAIL** trên cấu hình live. Bốn container GATE A healthy, đúng image pin, không publish port. Hermes auxiliary chỉ join control/provider internal networks. Guard join provider/upstream internal networks, không có mount provider key và chỉ forward mock. Bridge trả HTTP 200 khi truy cập health của proxy Level 2 cũ qua mạng dùng chung. Proxy đó còn nối upstream ngoài mạng nội bộ. Phép kiểm tra chỉ gọi health nội bộ, không mở tunnel tới OpenAI. Dùng lại proxy đó theo topology hiện tại không đáp ứng yêu cầu chỉ guard có đường tới provider. |
| Fingerprint, cap và input | **PASS trên mock đích danh.** Guard chốt một chuỗi byte sau khi đặt `service_tier=default`, `max_output_tokens=600` và `store=false`. SHA-256 của cả body được đối chiếu với permit rồi guard gửi chính các byte đó. Mock thấy từng byte khớp. Sửa `instructions` khi giữ nguyên task marker bị chặn trước mock. Giới hạn 4.000 byte trong rehearsal chưa chứng minh số tokens do provider tính. Sau khi có route hợp lệ, đối chiếu kết quả từ endpoint đếm token miễn phí với digest đã duyệt trước khi cấp permit. [Đếm input tokens](https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens). |
| Ledger và one-shot | **PASS cho baseline live và transaction mock.** Ledger thật có 1 attempt, reserve 0,0035 USD, chi phí lịch sử ước tính từ usage 0,0000496 USD, kill switch ON, 0 permit. Dấu băm đối chiếu trước/sau không đổi. Mock thấy `consumed`, `inflight` và reservation đã bền vững trước lúc nhận request. Shared lock tương thích adapter. 20 tiến trình nhận đúng 1 admission và có 19 lượt bị từ chối. Hai crash boundary và 16 ca lỗi đều PASS, gồm loại bỏ cấu hình hai permit và ngân sách NaN. |
| Hạch toán response hoặc timeout | **PASS trên mock.** SSE hoàn chỉnh lưu model, tier, hash response ID và usage vào bản sao ledger. Mẫu 200 input, 20 output gồm 8 reasoning, 60 cache reads và 40 cache writes cho ước tính 0,0000256 USD. Timeout hoặc stream thiếu sự kiện kết thúc lưu `outcome_unknown`, giữ đủ reservation và permit đã consumed. Mỗi kịch bản nhận đúng một request tại provider mock, 0 lượt từ tamper hoặc replay. Chi phí thật và tổng `actual_usd` không tăng vì đây là usage giả. Chưa có settlement tích hợp cho paid live, đối soát hóa đơn, hoặc callback paid đã nghiệm thu. |
| Health và rollback | Production n8n/Hermes đều HTTP 200 trước/sau, restart count 0. Bốn service GATE A tiếp tục healthy. Test chạy qua loopback trên KVM2 với thư mục tạm và ledger fixture, không redeploy, restart hay rollback service. Live backup/rollback của tuyến paid chưa được chạy vì chưa triển khai tuyến đó. |

## Phạm vi bằng chứng mới

Mã kiểm thử `69dd952fa7954702aa389defed854380969d4e70` chạy bằng Python 3 trên KVM2, kernel `6.8.0-147-generic`, exit 0. Chỉ chạy kiểm thử liên quan tới các phần thay đổi của guard và ledger. Dùng lại bằng chứng GATE A về Hermes auxiliary và callback mock, cùng bằng chứng remediation tại `a7bc57f`. Không dùng kết quả loopback để chứng nhận full Hermes paid E2E hoặc n8n callback trên mã đã sửa. [Test fingerprint và settlement](../sandbox/p0-hermes-gate-a/mock_contract_test.py) · [Nghiệm thu remediation](2026-11-21-hermes-gate-b-guard-remediation-results.md).

## Điều kiện gỡ chặn

Tách frontend của proxy allowlist cho riêng guard và xác minh bridge, Hermes và n8n không kết nối được các đường proxy tới provider. Chứng minh đúng credential, quyền Responses và phạm vi billing của guard. Chốt và đếm input của request giả đã duyệt theo digest. Kiểm chứng hạch toán live và callback bằng bản sao ledger với provider mock trước khi cấp permit thật. Sau khi toàn bộ preflight đạt, ADR-P0-003 vẫn giới hạn tối đa một attempt trả phí, giữ kill switch ON và không paid retry.
