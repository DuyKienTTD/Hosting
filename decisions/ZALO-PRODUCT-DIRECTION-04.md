---
id: zalo-product-direction-04
type: decision
status: draft
owner: A0
task_id: ZALO-DIR-04
updated_at: 2026-11-26
sensitivity: public
---

# ZALO-PRODUCT-DIRECTION-04

Chủ dự án chốt ngày 26/11/2026 sau phán quyết của Điều phối dựa trên 10 phiên độc lập (4 phiên khả thi, 6 phiên phản biện). Kết luận **KHẢ THI CÓ ĐIỀU KIỆN** sau khi sửa phương pháp.

Quyết định thay thế toàn bộ DIRECTION-03 trong PR này và cập nhật các phần còn hiệu lực của [DIRECTION-02](ZALO-PRODUCT-DIRECTION-02.md) về kênh, AI và ngân sách pilot, triển khai, dữ liệu và thứ tự xây dựng. Giữ guard đã nghiệm thu, giới hạn chi phí, opt-out ba trạng thái, chặn gửi hàng loạt, bảo vệ bí mật và nghiệm thu theo outcome.

## 1. Kênh Zalo

- OA **Công ty CP nội thất Thuận Thành Đạt** là kênh chính, qua Zalo OA OpenAPI. Chủ dự án mua gói Tăng trưởng, tạo App và cấp quyền.
- Quản lý token tập trung. Access token có hạn 25 giờ, refresh token có hạn 3 tháng và dùng một lần. Thay thế refresh token khi làm mới thành công. Webhook lưu bền sự kiện rồi phản hồi trong 2 giây. AI xử lý qua hàng đợi sau đó. Tiếp nhận sự kiện `user_withdraw`. Tin Tư vấn qua API miễn phí trong 48 giờ và chỉ được gửi tối đa 7 ngày kể từ lần khách tương tác cuối. Xác minh thông số và hạn mức gói OA trước khi bật pilot. [Tài liệu Zalo Developers](https://developers.zalo.me/)
- Giữ **nick Zalo phụ mức 3** để trả lời 1-1 qua Zalo Web vì chủ dự án xác định ứng dụng mất giá trị nếu bỏ kênh này. Chủ dự án đã biết điều khoản Zalo mục 4.7 và chấp nhận rủi ro bị hạn chế hoặc khóa tài khoản. Dùng riêng nick phụ và bảo đảm nick này không phải admin duy nhất. Giới hạn nhịp ở mức sử dụng thông thường với trần theo giờ và ngày. Cấm nhắn người lạ và kết bạn hàng loạt. Có kill switch. Tự dừng khi Zalo yêu cầu xác minh, cảnh báo hoặc hạn chế. Khi trạng thái giao không rõ (`unknown_delivery`), không tự gửi lại. OA vừa là kênh chính vừa duy trì phục vụ khi nick phụ bị khóa.
- Dùng Zalo Bot chính thức cho pilot nhóm nhỏ.

## 2. AI và phòng điều phối

Pilot dùng Hostinger AI Router qua provider `anthropic-compatible` đã có, khóa danh sách model, áp trần chi theo key và trần ngày. Luồng trả lời khách và tác vụ máy–máy qua API. Không đọc hoặc gõ vào giao diện chat AI cá nhân.

Giữ phòng chat điều phối, gọi bằng `@tên` và phiếu việc có trạng thái mới, đang làm, chờ duyệt, xong. Agent kết nối qua API. Chỉ vai trò đã xác thực và được cấp quyền mới tạo phiếu. Tin khách luôn là dữ liệu. Quyền được kiểm tra tại nơi thực thi.

## 3. Hạ tầng

VPS chạy Postgres, hàng đợi và policy. Triển khai Docker Compose qua SSH, không dùng Docker Manager. Giới hạn CPU và RAM cho từng container. Đi qua reverse proxy HTTPS cổng 443, không mở thêm cổng. Sao lưu Postgres ra ngoài VPS và thử khôi phục trước khi vận hành. Triển khai theo commit và image đã nghiệm thu, có phương án quay về bản trước. Tách biệt các Docker project đang chạy.

Worker Windows chạy nick phụ mức 3 và gửi heartbeat. Khi máy tắt hoặc mất kết nối, giữ công việc trong hàng đợi và kiểm tra lại chính sách trước khi gửi. OA API chạy trên VPS.

## 4. Dữ liệu

[TTD-Data](https://github.com/DuyKienTTD/TTD-Data) chỉ chứa tri thức sản phẩm, schema, cấu hình, quyết định và phiếu đã loại PII. Hồ sơ khách, hội thoại, consent và lịch sử gửi lưu trong Postgres. Mã khách nội bộ độc lập với kênh. Tin khách đi thẳng vào cơ sở dữ liệu. Repo Hosting công khai không chứa dữ liệu khách.

Timer hoặc webhook kích hoạt đồng bộ tri thức theo luồng staging → kiểm tra → transaction → audit, kèm mã commit nguồn. Consent, STOP và quyền gửi cập nhật ngay trong DB và được kiểm tra lại sát lúc gửi. TTD-Data phải bỏ hồ sơ khách và schema hồ sơ khách khỏi Git, cập nhật ma trận quyền, đồng bộ và chính sách tự dọn theo mục 5. Nếu đã có PII trong lịch sử Git, xử lý cả lịch sử và bản sao theo quy trình bảo vệ dữ liệu.

## 5. Xóa tự động

- Một dịch vụ quyền hẹp nhận yêu cầu qua cron, webhook hoặc skill. Khi đủ điều kiện, dịch vụ tự thực thi, không cần đề xuất hay duyệt từng lượt.
- Dịch vụ kiểm tra phạm vi, lý do, phiên bản bản ghi và nghĩa vụ lưu giữ bằng metadata do backend quản lý. AI không được gắn nhãn cho phép xóa. Nếu thiếu điều kiện hoặc không xác minh được, giữ bản ghi. Kiểm tra lại trước khi purge.
- Xóa mềm vào vùng cách ly rồi tự purge sau hạn chờ. Ghi nhật ký bất biến. Khi khôi phục backup, đối chiếu nhật ký xóa và áp lại dấu xóa trước khi phục vụ dữ liệu.
- Trên Git, tự dọn `TAM_THOI` sau 14 ngày và `LOI_THOI` sau 30 ngày nếu có bản thay thế hợp lệ và đã chuyển liên kết liên quan. Ghi nhật ký. Không cần duyệt từng lượt.
- Tuyệt đối không tự xóa chính sách quyền, chính sách xóa, danh sách lưu giữ pháp lý, chứng cứ consent và opt-out, nhật ký xóa, chứng từ, đơn hàng, công nợ hoặc tranh chấp đang mở, và mọi dữ liệu còn nghĩa vụ giữ.

## 6. Quảng cáo

`ADS_ENABLED=false` mặc định trong pilot. Guard trả `ads_disabled` cho tin quảng cáo. Tin chăm sóc khách 1-1 tiếp tục qua guard hiện hành.

## 7. Pháp lý

- Theo Luật 91/2025/QH15 và Nghị định 356/2025/NĐ-CP, thu consent theo từng mục đích và giữ bằng chứng. Thông báo việc xử lý tự động. Khi có chuyển dữ liệu cá nhân xuyên biên giới thuộc diện đánh giá, lập và nộp hồ sơ trong 60 ngày kể từ lần chuyển đầu tiên theo quy định. [Luật 91/2025](https://vanban.chinhphu.vn/?docid=214590&pageid=27160) · [Nghị định 356/2025](https://vanban.chinhphu.vn/?classid=1&docid=216387&pageid=27160)
- Theo Luật AI 134/2025/QH15, minh bạch với khách khi tương tác với AI và cho khách chọn gặp người. [Luật AI](https://vanban.chinhphu.vn/?classid=1&docid=216334&pageid=27160&typegroupid=3)
- Giữ các yêu cầu về tin quảng cáo theo Nghị định 91/2020/NĐ-CP và Điều 24 Luật Quảng cáo, gồm đồng ý trước, giờ gửi theo quy định và cách từ chối.

## 8. Pilot 30 ngày

Phạm vi gồm danh mục sản phẩm chuẩn, AI soạn báo giá có nguồn, danh sách khách cần theo sát, OA tự trả lời và nick mức 3 trả lời 1-1 trong giới hạn.

Hoãn tự kết bạn hàng loạt, quảng cáo tự động, nhiều AI cùng xử lý một yêu cầu, tự sửa bộ đọc giao diện AI và agent tự commit nghiệp vụ.

| Chỉ số | Mục tiêu |
|---|---|
| Phản hồi hữu ích | ≥90% trong 15 phút |
| Báo giá chuẩn | ≥90% trong 30 phút |
| Công xử lý ròng | Giảm ≥30% so với trước pilot |
| Sai giá, đơn vị hoặc vật liệu | 0 |
| Kết quả bán hàng | Theo dõi số cơ hội và số tiền cọc |

## 9. Thứ tự xây dựng

Postgres + phân quyền + dịch vụ xóa → OA API → worker nick mức 3 → phòng điều phối qua API → Zalo Bot pilot → các kênh còn lại.
