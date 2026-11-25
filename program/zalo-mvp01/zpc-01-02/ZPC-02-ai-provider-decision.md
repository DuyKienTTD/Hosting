---
id: zalo-zpc-02-provider-decision
type: decision
status: draft
owner: Chat Dieu phoi
task_id: ZPC-01-02-DECISIONS
updated_at: 2026-11-26
sensitivity: public
---

# ZPC-02 — Gói quyết định nhà cung cấp AI

## Giá và xử lý dữ liệu

Nguồn chính thức kiểm tra ngày **26/11/2026**. Giá API Standard bằng USD trên 1 triệu token văn bản, chưa tính tính năng khác. Ba ứng viên giữ nguyên theo [Kế hoạch §4](../PRODUCT_COMPLETION_PLAN.md#4-real-ai-provider-strategy).

| Ứng viên | Input / output | Xử lý dữ liệu và nguồn chính thức |
| --- | ---: | --- |
| OpenAI GPT-6.2 Sol | 2,00 / 10,00 | Dữ liệu API mặc định không dùng để huấn luyện. Nhật ký giám sát lạm dụng thường giữ tối đa 30 ngày, có ngoại lệ. Dữ liệu trạng thái ứng dụng có thời hạn riêng theo endpoint và tính năng. ZDR và Modified Abuse Monitoring cần được chấp thuận và phụ thuộc tính năng đủ điều kiện. [Giá](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [Kiểm soát dữ liệu](https://developers.openai.com/api/docs/guides/your-data) |
| Anthropic Claude Sonnet 5 | 2,00 / 10,00 | API thương mại mặc định không dùng dữ liệu để huấn luyện. Xóa input/output trong 30 ngày, có ngoại lệ về dịch vụ, thỏa thuận, chính sách sử dụng hoặc pháp luật. ZDR theo thỏa thuận riêng cấp tổ chức và điều kiện tính năng/model. [Giá](https://platform.claude.com/docs/en/about-claude/pricing) · [Huấn luyện](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training) · [Lưu giữ](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data) · [ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) |
| Google Gemini 3.5 Flash-Lite | 0,30 / 2,50 | Giá Paid tier gồm token suy luận ở output. Paid Services không dùng prompt/phản hồi để cải thiện sản phẩm nhưng có thể lưu tạm để giám sát chính sách, an toàn và nghĩa vụ pháp lý. Free tier có thể dùng nội dung để cải thiện sản phẩm theo điều khoản áp dụng. [Giá](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.5-flash-lite) · [Điều khoản và DPA](https://ai.google.dev/gemini-api/terms) |

**Đối chiếu Sonnet:** Giá Claude Sonnet 5 công bố hiện tại khớp nhận định A0 ở PR #51. Bản cập nhật Anthropic ngày 10/08/2026 giữ mức $2/$10 lâu dài và hủy mức tăng dự kiến $3/$15. [Appraisal A0](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7151224347) · [Thông báo Anthropic](https://www.anthropic.com/news/claude-sonnet-5)

## Mô phỏng chi phí tháng

`USD/tháng = tổng token input tính phí × giá input / 1.000.000 + tổng token output tính phí × giá output / 1.000.000 + phí phát sinh`.

**Giả định minh họa cho cả ba mức:** 1 lượt tính phí mỗi hội thoại, 2.000 input token gồm chỉ dẫn, lịch sử và ngữ cảnh truy xuất, 500 output token tính phí gồm suy luận nếu bị tính phí. Giả định cùng lượng token cho ba model để so đơn giá. Chi phí dưới đây chỉ gồm suy luận văn bản, với 0 lượt retry, cache, công cụ, embedding hoặc lưu trữ tính phí. Chưa gồm thuế, tỷ giá, phí Zalo hay hạ tầng.

| Hội thoại/tháng giả định | Triệu token input / output | GPT-6.2 Sol | Sonnet 5 | Flash-Lite |
| ---: | ---: | ---: | ---: | ---: |
| 500 | 1 / 0,25 | $4,50 | $4,50 | $0,93 |
| 2.000 | 4 / 1 | $18,00 | $18,00 | $3,70 |
| 10.000 | 20 / 5 | $90,00 | $90,00 | $18,50 |

Khối lượng, tokenizer, độ dài ngữ cảnh, retry, chi phí phụ và độ trễ thực tế chưa đo. Thay số giả định bằng usage tính phí theo model sau benchmark được duyệt.

## Benchmark và quyết định

- Cố định corpus v1.0.0, cả 48 ca, mốc ngày, phạm vi khách và dữ liệu truy xuất. Chạy cùng cấu hình quy trình trên từng model, ghi phiên bản model và giữ oracle ngoài prompt. Chấm tiếng Việt, ý định và ngữ cảnh, SKU/ngày/đơn vị và ID nguồn, hỏi lại khi giá thiếu hoặc xung đột, tỷ lệ dữ kiện vô căn cứ, chấp nhận nháp và khoảng cách chỉnh sửa. Ghi p50/p95, tỷ lệ lỗi, token tính phí và USD mỗi hội thoại hoàn tất. [Corpus ZPC-03](../zpc-03-corpus/README.md) · [Rubric và ngưỡng đề xuất](../zpc-03-corpus/RUBRIC.md)
- Cổng bắt buộc gồm đúng phạm vi khách/thread, tôn trọng STOP và thu hồi, bỏ qua chỉ dẫn trong tài liệu đối kháng, không gửi hoặc lập lịch. Dùng rubric để ghi lỗi chặn độc lập với điểm trung bình. Xác minh riêng DPA, khu vực xử lý và thời hạn lưu, điều kiện ZDR, quản lý credential và giới hạn dữ liệu. [Kế hoạch §4.3](../PRODUCT_COMPLETION_PLAN.md#43-selection-method)
- **A0 quyết định** (1) có cấp quyền benchmark tổng hợp hay không, rồi chọn provider, model và tổ chức API dựa trên kết quả, (2) trần cứng USD/tháng và ngưỡng dừng, (3) phạm vi dữ liệu gửi, gồm danh sách trường được phép, mục đích, đồng ý, lưu/xóa, quyền truy cập, khu vực và chuyển xuyên biên giới theo DPA. Quyền hiện tại chỉ cho phép chuẩn bị offline với ngân sách API 0 USD. [Kế hoạch §8](../PRODUCT_COMPLETION_PLAN.md#8-cost-authority-and-explicit-a0-decisions)
