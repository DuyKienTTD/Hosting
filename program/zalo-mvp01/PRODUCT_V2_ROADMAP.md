---
id: zalo-product-v2-roadmap
type: knowledge
status: draft
owner: Chat Dieu phoi
updated_at: 2026-11-26
sensitivity: public
---

# TTD Zalo Assistant — Roadmap V2

[Quyết định A0 ngày 26/11/2026](../../decisions/ZALO-PRODUCT-DIRECTION-02.md) · [Kế hoạch MVP-01](PRODUCT_COMPLETION_PLAN.md)

Owner trong bảng là phân công đề xuất, chờ giao việc theo phạm vi được duyệt. A0 nghiệm thu từng outcome theo bằng chứng.

| ID | Outcome | Owner | Phụ thuộc | Tiêu chí xong |
| --- | --- | --- | --- | --- |
| V2-01 | Kênh kết nối Zalo cá nhân qua Subiz | Điều phối | Quyết định A0, tài liệu Subiz/Zalo, môi trường thử được duyệt | Có ma trận và bằng chứng kiểm thử Subiz API/webhook cho nhận sự kiện, định danh người nhận, gửi và đối soát. Kiểm chứng Zalo Bot cho nhóm và khả năng tạo/quản lý nhóm. Có phương án dự phòng nếu thiếu tính năng hoặc mất kết nối, kèm tiêu chí chọn và giới hạn. |
| V2-02 | Runtime Docker trên VPS | ChatGPT Work | Policy Core MVP-01, hợp đồng tích hợp V2-01 | Docker chạy Claude điều phối và các lớp agent. Kiểm thử cổng Policy Core, STOP, consent, từ chối, cách ly và chống gửi trùng. Giới hạn cứng $200/tháng và credit khả dụng, dừng AI khi hết credit, không trả thêm. Kiểm thử khởi động lại và lỗi nhà cung cấp. |
| V2-03 | Triển khai lên VPS | ChatGPT Work | V2-01, V2-02, A0 hoàn tất các mục bên dưới | Bản Docker triển khai đúng phiên bản. Kiểm tra quyền tối thiểu, bí mật trên VPS, health check, kết nối và rollback. A0 nhận bằng chứng đã khử định danh. |
| V2-04 | Bật chạy thật 24/7 có theo dõi | Điều phối | V2-03 và A0 nghiệm thu cho phép bật live | Xác minh luồng thật từ nhận đến gửi, đối soát kết quả, giám sát lỗi và credit, cảnh báo, tự phục hồi và dừng khẩn cấp. Ghi bằng chứng vận hành và người xử lý sự cố. |
| V2-05 | Nhóm và tăng trưởng | Điều phối | V2-01 xác minh năng lực nhóm, V2-04 ổn định, A0 duyệt phạm vi | Tự tạo/quản lý nhóm qua kênh đã xác minh. Đo số người tham gia có đồng ý, phản hồi và tăng trưởng theo mục tiêu A0. Kiểm chứng opt-out và chặn nhắn hàng loạt khách cũ. |

## Phần chủ dự án tự thực hiện

- Mua Claude Ultra và liên kết credit API với Claude Console. Không gắn thẻ trả thêm.
- Nâng gói Subiz/Zalo Business và tự kết nối Zalo vào Subiz bằng quét QR.
- Cấp API key/token trực tiếp vào VPS và cấp quyền truy cập VPS.
