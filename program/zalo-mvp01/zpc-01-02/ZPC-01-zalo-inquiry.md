---
id: zalo-zpc-01-inquiry
type: reference
status: draft
owner: Chat Dieu phoi
task_id: ZPC-01-02-DECISIONS
updated_at: 2026-11-26
sensitivity: public
---

# ZPC-01 — Thư hỏi Zalo để A0 tự gửi

**Tiêu đề thư** — Hỏi về tích hợp chính thức cho một tài khoản Zalo cá nhân

Kính gửi bộ phận hỗ trợ Zalo,

TTD METAL đang đánh giá một ứng dụng Windows của bên thứ ba hỗ trợ chăm sóc khách hàng trên **một tài khoản Zalo cá nhân**. Ứng dụng dự kiến tiếp nhận hội thoại một-một và hỗ trợ người vận hành soạn, duyệt từng phản hồi trước khi gửi. Xin Zalo xác nhận bằng văn bản liệu mô hình này có được phép và cung cấp tài liệu hoặc điều khoản chính thức cho tám nội dung sau.

1. API, SDK hoặc chương trình đối tác chính thức nào hỗ trợ tích hợp này? Loại tài khoản và ứng dụng nào đủ điều kiện?
2. Có sự kiện tin nhắn đến một-một không? Sự kiện cung cấp danh tính người gửi và ID ổn định nào cho hội thoại, tin nhắn?
3. Được đọc những hội thoại và lịch sử nào, trong cửa sổ đồng bộ bao lâu? Xóa, sửa và thu hồi tin nhắn được biểu diễn thế nào?
4. Có được gửi phản hồi một-một không? Hỗ trợ loại nội dung nào và quy định trạng thái đã giao, thất bại hoặc chưa rõ kết quả ra sao?
5. OAuth, phạm vi quyền, đồng ý, xét duyệt ứng dụng, cấp quyền của chủ tài khoản và thu hồi quyền được thực hiện thế nào?
6. Giới hạn tốc độ, hạn mức, quy tắc chống spam, độ tin cậy hoặc SLA và biểu phí áp dụng là gì?
7. Nghĩa vụ xử lý, lưu giữ, chuyển dữ liệu xuyên biên giới và bảo mật là gì?
8. Có điều khoản hay giới hạn nào cấm trường hợp chăm sóc khách hàng bằng tài khoản cá nhân như mô tả trên không?

Xin chuyển yêu cầu đến bộ phận phụ trách tích hợp hoặc đối tác nếu cần. Trân trọng, đại diện TTD METAL.

## Short English version

Dear Zalo Support, may a third-party Windows customer-care app connect **one personal Zalo account** to receive one-to-one conversations and send operator-approved replies? Please confirm in writing and share official documentation covering (1) API/SDK/partner programme and eligible account/app types, (2) inbound events, sender identity and stable conversation/message IDs, (3) permitted history and sync window, edits/deletion/recall, (4) one-to-one sends, content types and delivered/failed/unknown receipts, (5) OAuth/scopes, consent, app review, owner authorization and revocation, (6) limits, quotas, anti-spam, SLA and prices, (7) data processing, retention, cross-border transfer and security, and (8) any restriction that prohibits this use case. Thank you, TTD METAL.

## Gửi và xử lý phản hồi

- A0 có thể tự gửi email tới `hotro@zalo.me` và đề nghị chuyển đến bộ phận tích hợp/đối tác. Zalo công bố đây là kênh hỗ trợ chung. Trang liên hệ là phương án chính thức khác. Đã kiểm tra ngày **26/11/2026**. [Kênh hỗ trợ Zalo, mục 3](https://help.zalo.me/huong-dan/chuyen-muc/chinh-sach-cong-dong-zalo/chinh-sach-vng-ve-bao-ve-quyen-loi-cho-khach-hang-de-ton-thuong/) · [Liên hệ Zalo Help](https://help.zalo.me/lien-he/) · [Danh mục Open APIs](https://docs.zaloplatforms.com/docs/OA)
- A0 lưu thư đã gửi, ngày giờ, mã yêu cầu nếu có, phản hồi gốc và tài liệu kèm theo ở nơi hạn chế truy cập. Trong repo công khai chỉ ghi trạng thái và tóm tắt đã khử định danh theo tám mục. Thư chỉ hỏi về quyền và khả năng tích hợp, không yêu cầu cấp truy cập tài khoản hay đính kèm thông tin xác thực hoặc dữ liệu khách hàng.
- **Có văn bản cho phép đủ phạm vi:** Điều phối đối chiếu tài liệu, quyền, điều khoản và chi phí, rồi trình A0 duyệt phạm vi tối thiểu của ZPC-09. **Đang chờ hoặc phản hồi thiếu:** giữ ZPC-09 `BLOCKED` và ghi chính xác mục còn thiếu. **Zalo từ chối:** giữ `NO-GO` và trình A0 chọn chờ, tìm đối tác được phép hoặc duyệt thay đổi mục tiêu sản phẩm. [Kế hoạch §3.2](../PRODUCT_COMPLETION_PLAN.md#32-one-official-clarification-request--no-generic-poc) · [Điều khoản Zalo](https://zalo.me/zalo/dieukhoan/)
