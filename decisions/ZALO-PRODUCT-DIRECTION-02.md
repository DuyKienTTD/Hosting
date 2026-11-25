---
id: zalo-product-direction-02
type: decision
status: current
owner: A0
task_id: ZALO-DIRECTION-02-RECORD
updated_at: 2026-11-26
sensitivity: public
---

# ZALO-PRODUCT-DIRECTION-02 — Quyết định A0 ngày 26/11/2026

[Kế hoạch MVP-01](../program/zalo-mvp01/PRODUCT_COMPLETION_PLAN.md) · [Roadmap V2](../program/zalo-mvp01/PRODUCT_V2_ROADMAP.md) · [Tracker lỗi vận hành Agent](../reports/agent-operational-issues.md)

## Bối cảnh

Quyết định này thay các chặn cũ của `HOSTING-ZALO-RESUME-01` về tài khoản Zalo thật, API tính phí, agent tự động trong runtime và việc dùng Zalo cá nhân qua bên thứ ba, trong phạm vi định hướng V2 dưới đây.

## Quyết định

- Dùng Zalo cá nhân của chủ dự án (đã có Zalo Business) qua Subiz sau khi chủ dự án nâng gói. Hệ thống tự tạo và quản lý nhóm. Chủ dự án đã đánh giá và chấp nhận rủi ro tài khoản.
- Tự động hóa toàn bộ ngay từ đầu bằng nhiều lớp agent, Claude điều phối chính, chạy 24/7 trên VPS. Mọi tác động phải đi qua Policy Core. Giữ các chặn cứng về STOP, thu hồi đồng ý, tiếp quản, cách ly dữ liệu, định danh người nhận và chống gửi trùng.
- Claude API chỉ dùng credit kèm gói Claude Ultra ($200/tháng, credit hết hạn cuối chu kỳ). Trần cứng $200/tháng và không vượt số credit khả dụng. Không gắn thẻ để trả thêm. Khi hết credit, hệ thống tự dừng gửi yêu cầu AI và chặn tin nhắn phụ thuộc AI.
- Cam kết của chủ dự án phải thành luật cứng. Không nhắn người lạ chưa đồng ý kết bạn. Không nhắn hàng loạt khách cũ. Tuân thủ Nghị định 91/2020/NĐ-CP và Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15. Tin quảng cáo cần có đồng ý trước, chỉ gửi 07:00–22:00 giờ Việt Nam và luôn có cách từ chối.
- A0 nghiệm thu theo outcome. Bảo vệ credential, API key, token và số điện thoại thật. Chỉ cấp bí mật trực tiếp trên VPS.

## Hệ quả và trạng thái triển khai

V2-01 kiểm chứng khả năng kết nối và phương án dự phòng trước khi triển khai. Quyết định ghi định hướng và giới hạn V2. Phiên ghi nhận chỉ cập nhật tài liệu, chưa kết nối Zalo/Subiz thật, chưa gọi Claude API thật và không đổi quyền Agent. PR Draft chờ A0 nghiệm thu.
