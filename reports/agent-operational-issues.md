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

## Sự kiện

| Incident ID | Thời điểm | Agent / Session | TASK_ID | Phiên bản | Expected | Observed | Evidence | Impact | Recovery | Root cause |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Nhóm lỗi theo dõi

Đọc thiếu, đọc sai phiên bản, quên chỉ thị, không thực hiện nhiệm vụ, dừng sớm, phân công sai, gán sai ACK, thao tác trùng và lỗi công cụ.

## Quy tắc ghi nhận và xử lý

- Mọi Agent báo sự kiện cho Điều phối để cập nhật bảng. Dẫn bằng chứng đã khử định danh và ghi tác động, cách khôi phục thực tế.
- Ghi Root cause là `UNKNOWN` khi nguyên nhân chưa được chứng minh. Không suy diễn nguyên nhân từ một sự kiện đơn lẻ.
- Không ghi dữ liệu nhạy cảm, credential hoặc log thô. Không tạo sự cố nhân tạo.
- Chỉ đề xuất điều chỉnh khi có đủ dữ liệu để tái lập lỗi, phân biệt các nguyên nhân khả dĩ, chứng minh nguyên nhân và xác định biện pháp có kết quả đo được.
- Xử lý ngay sự cố liên quan đến bảo mật, mất dữ liệu, vượt quyền, chi phí hoặc production.
