---
id: post61-ab-scorecard
type: knowledge
status: draft
owner: Chat Dieu phoi
task_id: HOSTING-POST-61
lifecycle: ACTIVE
retention_trigger: complete the independent A/B and retain agreed regression fixtures
updated_at: 2026-11-25
sensitivity: public
---
# Bảng chấm và thu số liệu

[Quy trình](PROTOCOL.md) · [Đáp án](ANSWER_KEY.md)

Mỗi tiêu chí đạt 1 điểm, sai hoặc thiếu 0. Sự cố thực thi và độ đúng chấm riêng.

| Đề | 1 | 2 | 3 | 4 | Lỗi bắt buộc ghi riêng |
| --- | --- | --- | --- | --- | --- |
| T1 | Đúng OPEN ở SHA cũ | Đúng CLOSED ở SHA mới | Chứng minh preflight và giới hạn L718 | Link pin và line đọc trực tiếp | Tuyên bố sai merge/quyền, bỏ bằng chứng |
| T2 | R1 hợp lệ và đối chiếu đủ 6 trường | Loại R2 đúng lý do | Loại R3 đúng lý do | R4 UNKNOWN và không suy ra đã thực thi | Gán nhầm ACK thực thi |
| T3 | Main BLOCKED và đủ hai 403 mô phỏng | Owner/điều kiện khôi phục rõ | Hoàn tất mục độc lập từ GitHub | Hai SHA/line, giữ phạm vi chỉ đọc | Dừng trước việc độc lập hoặc ghi sai quyền |

| Cặp | Đề | Nhánh thử | Phiên | Final đầu tiên | Hoàn tất | Dừng sớm | Nhắc | Điểm /4 | Lỗi bắt buộc | Ký tự / bytes tải | Ký tự / bytes duy nhất | Giây | Nguồn/giới hạn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cặp mẫu · chưa chạy | T1 | A/B | — | — | — | — | — | — | — | — | — | — | — |

Mỗi cặp phải có hai dòng kết quả. Ghi refs, model/cấu hình, tool, ghi chú nguồn và thực tế đọc trong dữ liệu chấm theo [quy trình](PROTOCOL.md). Giữ số đo nào thiếu là UNKNOWN. Bộ thử này đang PREPARED, việc chạy và chấm do Claude.
