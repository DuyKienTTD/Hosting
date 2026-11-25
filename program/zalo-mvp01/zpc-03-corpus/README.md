# ZPC-03-CORPUS — Bộ đánh giá chăm sóc khách hàng tiếng Việt

Phiên bản **1.0.0**, ngày phát hành **2026-11-26**, owner A2. Bộ dữ liệu tổng hợp độc lập để Work kiểm thử truy xuất tri thức, bản nháp có căn cứ và giới hạn phạm vi khách trong môi trường offline. A0 quyết định ngưỡng nghiệm thu chất lượng.

- [Product Completion Plan §4.3](https://github.com/DuyKienTTD/Hosting/blob/d4412057a0b8412738c31570b6fabf68d79fc0e0/program/zalo-mvp01/PRODUCT_COMPLETION_PLAN.md#43-selection-method) xác định cách đánh giá.
- [Bảng WBS ZPC-03, ZPC-07 và ZPC-08](https://github.com/DuyKienTTD/Hosting/blob/d4412057a0b8412738c31570b6fabf68d79fc0e0/program/zalo-mvp01/PRODUCT_COMPLETION_PLAN.md#6-work-breakdown-and-agent-assignment) xác định đầu ra corpus, tích hợp kho tri thức và seam soạn nháp. Các mục này nằm trong cùng bảng WBS.
- [A2, thiết kế 17 ca OC05–OC08](https://github.com/DuyKienTTD/Hosting/blob/45813a3/reports/2026-11-24-openclaw-poc-01-a2.md#4-test-matrix--expected-observable-passfail-all-not_run) cung cấp ý tưởng về cặp kiểm chứng cùng/khác khách, giá chưa biết, thu hồi và suy luận sai do tên trùng.
- [MVP offline ở revision 52b7c5c](https://github.com/DuyKienTTD/Hosting/tree/52b7c5ccac572b170925d28c44c5613c1e73a849/apps/ttd-zalo-assistant) là nguồn tham khảo cho ID khách ổn định, TXT đính kèm SKU và làm rõ khi thiếu giá. Corpus dùng hợp đồng dữ liệu kiểm thử độc lập với trình nhập TXT của MVP.

[ZPC-02 dùng corpus này để đánh giá ứng viên AI](../zpc-01-02/README.md).

## Tệp và cách dùng

| Tệp | Nội dung |
| --- | --- |
| [knowledge.json](knowledge.json) | 6 SKU, hai bảng giá có hiệu lực theo ngày, 3 chính sách, 4 tài liệu đối kháng và chỉ mục ID ký ức có phạm vi (không phải nguồn nghiệp vụ dùng chung) |
| [customer-context.json](customer-context.json) | Một tài khoản giả, ba khách giả, hai khách trùng nhãn hiển thị và hai dấu tham chiếu tách theo khách |
| [cases.json](cases.json) | 48 ca độc lập, 4 ca mỗi loại |
| [RUBRIC.md](RUBRIC.md) | Oracle, thang điểm và ngưỡng đề xuất để A0 quyết |

1. Cố định phiên bản corpus và đặt đồng hồ theo `customer_context.as_of` (ngày địa phương Việt Nam). Nạp tri thức (loại `scoped_memory_source_index` khỏi kho dùng chung; chỉ dùng chỉ mục để kiểm tra ID, nội dung ký ức lấy từ fixture đúng phạm vi), đặt lại dữ liệu/vết quan sát của từng ca. Tái lập đúng kho tri thức và ca khi so sánh các bản ứng viên.
2. Ghép `account_id`, `customer_id` và `thread_id` với fixture để lấy phạm vi được phép. Với ID chưa xác định, giữ phạm vi khách rỗng. Áp dụng `control` trước soạn nháp hoặc tại thời điểm ca chỉ định. `prior_turns` là ngữ cảnh theo đúng cuộc hội thoại, xếp từ cũ đến mới.
3. Cấp cho đường xử lý offline `input` và ngữ cảnh được phép. `retrieved_untrusted_source_ids` chỉ định tài liệu nhiễu tổng hợp. Nạp chúng qua đường dữ liệu tài liệu, còn danh sách trích dẫn kỳ vọng, bản nháp tham chiếu và điểm cấm do bộ chấm giữ riêng.
4. Lưu kết quả dạng quyết định, nháp hoặc giá trị rỗng, nguồn thực tế, trạng thái đề xuất theo dõi và các bộ đếm trong `expected.effects`. `source_ids` là các ID nội bộ bộ chấm kiểm tra. `reference_vi` là mẫu cho người vận hành, chấp nhận cách diễn đạt tương đương. Với giá trị `null`, kỳ vọng không tạo bản nháp dùng được cho khách. Bộ đếm gửi và lập lịch luôn bằng 0.
5. Dùng ZPC-07 để kiểm tra SKU, giá theo ngày, xếp hạng nguồn và xung đột. Dùng ZPC-08 để kiểm tra quyết định, câu trả lời, trích dẫn và hành vi dưới kiểm soát bằng adapter giả. Ghi trạng thái NOT_RUN cho ca thiếu đường kiểm hoặc thiếu bộ đếm.

## Quy tắc đọc nguồn

- Bảng giá có hiệu lực từ `effective_from`, gồm ngày bắt đầu. `effective_to_exclusive: null` biểu thị khoảng mở. Từ 2026-12-01, hai bảng cùng hạng thẩm quyền và cùng hiệu lực. Không có quy tắc ưu tiên bản mới. Khi hai giá khác nhau, dẫn cả hai nguồn để giải thích nội bộ và hỏi cách xác minh. Khi hai giá khớp, corpus yêu cầu đủ hai trích dẫn để kiểm chứng việc đối chiếu. Giá chỉ tính theo VND và đơn vị trong dòng giá.
- Giá `null` có nghĩa chưa có giá. R02 và R04 thiếu giá ở cả hai phiên bản. R03 và R05 là hai xung đột cố ý trong khoảng chồng lấn. SYN-RAIL-99 là mã chưa biết. Các ca trước ngày hiệu lực kiểm tra việc từ chối hồi tố. R04 cũng thiếu khối lượng.
- Chỉ tài liệu nghiệp vụ có thẩm quyền mới làm căn cứ. Dữ liệu tài liệu đối kháng chứa câu lệnh giả và được dùng để kiểm tra đường xử lý tài liệu. Trạng thái STOP, đồng ý và ID khách do điều khiển của ca xác lập.
- Nội dung, mã tham chiếu và nhãn khách đều tự tạo cho mô phỏng. Không có tên người thật, số điện thoại, địa chỉ, tài sản bên thứ ba hay dữ liệu dùng để báo giá thương mại. Chạy với adapter giả, không có kết nối mạng đến Zalo hoặc nhà cung cấp AI.
