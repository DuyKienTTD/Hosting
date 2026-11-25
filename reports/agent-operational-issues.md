---
id: agent-operational-issues
type: report
status: current
owner: Chat Dieu phoi
task_id: ZALO-RESUME-01-GOV
lifecycle: DURABLE
updated_at: 2026-11-26
sensitivity: public-redacted
---
# Theo dõi lỗi vận hành Agent

Đây là tài liệu duy nhất để ghi nhận lỗi vận hành Agent phát sinh trong công việc thực tế.
Điều phối dùng bằng chứng tích lũy để xác định nguyên nhân và đề xuất điều chỉnh có thể kiểm chứng.

[Đặc tả ZALO-RESUME-01-GOV](https://github.com/DuyKienTTD/Hosting/blob/951ae78b85ae5a4ff474fe6d2b35f51e6d5ead81/tasks/zalo-resume-01-gov.md)

[Quyết định ZALO-PRODUCT-DIRECTION-02](../decisions/ZALO-PRODUCT-DIRECTION-02.md)

## Sự kiện

| Incident ID | Thời điểm | Agent / Session | TASK_ID | Phiên bản | Expected | Observed | Evidence | Impact | Recovery | Root cause |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INC-2026-11-26-01 | 26/11/2026 ~02:30 ICT | 4 phiên ChatGPT Công việc; GPT-6.2 Sol, Vừa | TTD-ZALO-P1-OFFLINE; ZPC-03-CORPUS; ZPC-04-SECURITY; ZPC-01-02-DECISIONS | UNKNOWN | Hoàn thành outcome theo giao việc | Lỗi công cụ: dừng sau 5–7 phút do thông báo hết lượt | Báo cáo Điều phối 26/11; UI báo hết lượt đến 29/11 04:06 | Outcome sản phẩm chưa có commit; ZPC-03 có 1 commit; ZPC-04 có nhánh rỗng | Tài liệu chuyển sang Trò chuyện; phát triển chờ hạn mức | Hạn mức nền tảng theo thông báo UI; mức sử dụng chi tiết UNKNOWN |
| INC-2026-11-26-02 | 26/11/2026 ICT | ChatGPT Trò chuyện; hai phiên; model/cấu hình UNKNOWN | ZPC-04-SECURITY; ZPC-01-02-DECISIONS | UNKNOWN | Đạt XONG KHI hoặc blocker thật | Dừng sớm sau 32 giây và 14 giây; chưa đạt XONG KHI, không có blocker thật | Báo cáo Điều phối 26/11 | Chưa có kết quả GitHub tại checkpoint | Điều phối nhắc tiếp tục | UNKNOWN |
| INC-2026-11-26-03 | 26/11/2026 ICT | Điều phối Claude qua trình duyệt; model/cấu hình UNKNOWN | UNKNOWN | UNKNOWN | Nhập lệnh vào ô soạn tin | Lỗi công cụ/thao tác: chèn nhầm lệnh vào khối tài liệu chỉnh sửa trong chat 1-Trợ lý | Báo cáo Điều phối 26/11 | Không có | Gỡ trước khi gửi; khôi phục nguyên trạng; chọn ô soạn tin trong form | Bộ chọn chọn phần tử chỉnh sửa hiển thị đầu tiên |
| INC-2026-11-26-04 | 26/11/2026 ICT | Phiên ChatGPT ZALO-RESUME-01-GOV; model/cấu hình UNKNOWN | ZALO-RESUME-01-GOV | UNKNOWN | Ghi đúng phạm vi và liên kết hợp lệ | Lỗi công cụ: kiểm duyệt tự động từ chối ghi gộp vì báo vượt phạm vi STATE.md; 3 liên kết tương đối trả 404 | Báo cáo Điều phối 26/11; [PR #64](https://github.com/DuyKienTTD/Hosting/pull/64) | Cần thao tác khôi phục trước khi nghiệm thu | Ghi riêng STATE.md; đổi liên kết sang commit lịch sử | UNKNOWN |

## Nhóm lỗi theo dõi

Đọc thiếu, đọc sai phiên bản, quên chỉ thị, không thực hiện nhiệm vụ, dừng sớm, phân công sai, gán sai ACK, thao tác trùng và lỗi công cụ.

## Quy tắc ghi nhận và xử lý

- Agent / Session = agent, phiên, model và cấu hình; Phiên bản = commit quy tắc và đặc tả áp dụng. Ghi UNKNOWN nếu chưa xác minh. Không đặt chỉ tiêu số lượng sự cố.
- Không tổ chức vòng kiểm thử nhỏ lẻ chỉ để đánh giá hành vi Agent; không mở điều tra mới sau mỗi sự cố; không sửa quy tắc khi chưa có bằng chứng nguyên nhân; không tạo tài liệu quản trị trùng mục đích.
- Ưu tiên khôi phục an toàn và phát triển sản phẩm; vẫn giữ đầy đủ kiểm thử sản phẩm, bảo mật, regression và nghiệm thu bắt buộc.

- Mọi Agent báo sự kiện cho Điều phối để cập nhật bảng. Dẫn bằng chứng đã khử định danh và ghi tác động, cách khôi phục thực tế.
- Ghi Root cause là `UNKNOWN` khi nguyên nhân chưa được chứng minh. Không suy diễn nguyên nhân từ một sự kiện đơn lẻ.
- Không ghi dữ liệu nhạy cảm, credential hoặc log thô. Không tạo sự cố nhân tạo.
- Chỉ đề xuất điều chỉnh khi có đủ dữ liệu để tái lập lỗi, phân biệt các nguyên nhân khả dĩ, chứng minh nguyên nhân và xác định biện pháp có kết quả đo được.
- Xử lý ngay sự cố liên quan đến bảo mật, mất dữ liệu, vượt quyền, chi phí hoặc production.
