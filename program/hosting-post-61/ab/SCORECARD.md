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

## Kết quả 12 phiên ngày 25/11/2026

GPT-6.2 Sol, mức Vừa, dự án Hosting, Code Mode và quyền GitHub chỉ đọc trong các phiên thử. A dùng ref `097c080cc6d7fb3ca36b1849d9c10375d5cbd67f`. B dùng ref `c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb`. Cặp 1 chạy A → B và cặp 2 chạy B → A cho mỗi đề. Claude chạy và chấm, A0 hiệu chỉnh điểm. Theo kết quả Claude và A0 cung cấp, không phiên nào trích ANSWER_KEY hoặc SCORECARD.

| Cặp | Đề | Nhánh thử | Phiên | Giờ gửi (ICT) | Final đầu tiên | Hoàn tất | Dừng sớm | Nhắc | Điểm /4 | Lỗi bắt buộc | Ký tự / bytes tải | Ký tự / bytes duy nhất | Giây đến final đầu tiên | Số tệp nêu đã mở | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cặp 1 | T1 | A | [Phiên T1-A](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b81a-6d48-83ec-b369-8890b8d8e565) | 17:27:40 | Final nhận được | Có | 0 | 0 | 4/4 | Không | UNKNOWN | UNKNOWN | 46 | 6 | — |
| Cặp 1 | T1 | B | [Phiên T1-B](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b820-28ac-83ec-b72a-3fb9219fc9fe) | 17:27:45 | Final nhận được | Có | 0 | 0 | 4/4 | Không | UNKNOWN | UNKNOWN | 64 | 14 | — |
| Cặp 1 | T2 | A | [Phiên T2-A](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b826-6668-83ec-8f96-3ac46519c057) | 17:27:51 | Final nhận được | Có | 0 | 0 | 3/4 | Không | UNKNOWN | UNKNOWN | 20 | 4 | R1 không nêu time/source |
| Cặp 1 | T2 | B | [Phiên T2-B](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b82b-86f8-83ec-9521-de80c5c53393) | 17:27:57 | Final nhận được | Có | 0 | 0 | 4/4 | Không | UNKNOWN | UNKNOWN | 24 | 13 | — |
| Cặp 1 | T3 | A | [Phiên T3-A](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b831-4270-83ec-b1e3-c5e096edaea8) | 17:28:02 | Final nhận được | Có | 0 | 0 | 4/4 | Không | UNKNOWN | UNKNOWN | 40 | 7 | — |
| Cặp 1 | T3 | B | [Phiên T3-B](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b836-ea1c-83ec-a1b5-3ef3f6348ab2) | 17:28:08 | Final nhận được | Có | 0 | 0 | 4/4 | Không | UNKNOWN | UNKNOWN | 51 | 18 | — |
| Cặp 2 | T1 | B | [Phiên T1-B](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b8e8-8358-83ec-a804-d9f806ab1d3a) | 17:31:05 | Final nhận được | Có | 0 | 0 | 4/4 | Không | UNKNOWN | UNKNOWN | 44 | 14 | — |
| Cặp 2 | T1 | A | [Phiên T1-A](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b8ed-a774-83ec-9d2f-67c884c50987) | 17:31:11 | Final nhận được | Có | 0 | 0 | 4/4 | Không | UNKNOWN | UNKNOWN | 46 | 6 | — |
| Cặp 2 | T2 | B | [Phiên T2-B](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b8f2-da44-83ec-a838-0ed578a951fd) | 17:31:16 | Final nhận được | Có | 0 | 0 | 4/4 | Không | UNKNOWN | UNKNOWN | 25 | 12 | — |
| Cặp 2 | T2 | A | [Phiên T2-A](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b8f7-dfd4-83ec-924e-b77e649e1340) | 17:31:21 | Final nhận được | Có | 0 | 0 | 3/4 | Không | UNKNOWN | UNKNOWN | 20 | 4 | R1 không nêu time/source |
| Cặp 2 | T3 | B | [Phiên T3-B](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b8fc-dae0-83ec-b1f8-d47990e8ac27) | 17:31:26 | Final nhận được | Có | 0 | 0 | 4/4 | Không | UNKNOWN | UNKNOWN | 34 | 9 | — |
| Cặp 2 | T3 | A | [Phiên T3-A](https://chatgpt.com/g/g-p-6b011174489881919690d180e4c2d2a3-hosting/c/6b06b902-3304-83ec-897c-ddf1dea0cfc5) | 17:31:31 | Final nhận được | Có | 0 | 0 | 3/4 | Không | UNKNOWN | UNKNOWN | 27 | 6 | owner khôi phục chưa nêu rõ (A0 hiệu chỉnh) |

Nguồn là số đo Claude cung cấp và điểm đã được A0 hiệu chỉnh. Số tệp do từng phiên tự báo. Telemetry lượng đọc ở trạng thái PARTIAL: chưa có số ký tự hoặc byte thật, kể cả lượng đọc duy nhất. Xem [tổng hợp A/B](../../../reports/2026-11-25-hosting-post-61.md#post-03--tổng-hợp-ab-read_set).
