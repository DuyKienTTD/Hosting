---
id: zalo-product-direction-03
type: decision
status: draft
owner: A0
task_id: ZALO-DIR-03
updated_at: 2026-11-26
sensitivity: public
---

# ZALO-PRODUCT-DIRECTION-03

Chủ dự án chốt ngày 26/11/2026. Quyết định thay phương án kênh Subiz, mô hình chạy mọi thành phần trên VPS và lộ trình tích hợp của [DIRECTION-02](ZALO-PRODUCT-DIRECTION-02.md). Bổ sung cơ chế đa AI, điều phối, lưu dữ liệu và vòng đời tài liệu. Đây là định hướng sản phẩm chờ A0 nghiệm thu trên PR Draft, độc lập với PR #73.

## Kênh và triển khai

- Hủy Subiz. Nick Zalo phụ dùng thí nghiệm mức 3. Worker điều khiển chuột và bàn phím trên Zalo Web, tự gửi với giới hạn nhịp tương đương người dùng và qua guard. Chủ dự án chấp nhận rủi ro tài khoản. Phạm vi chỉ gồm những thao tác VNG không cấm tuyệt đối.
- OA **Công ty cổ phần nội thất Thuận Thành Đạt** đã xác thực, gói Cơ bản và liên kết zBusiness. Tích hợp qua API chính thức của Zalo OA. Hiện chưa có app được cấp quyền. Chủ dự án sẽ tạo app tại developers.zalo.me. OA phổ thông **Nẹp nội thất TTD** mở rộng sau.
- Một ứng dụng gồm các mô-đun nick, OA, zBusiness và nhóm/cộng đồng, có chỗ mở rộng Mini App và Ads.
- VPS `srv1722328` là bộ não và nơi lưu dữ liệu. Triển khai Docker project mới, độc lập với `hermes-agent-l7fe`, `n8n-nbqy`, `ttd-hermes-gate-a` và `ttd-p0-level1`. Worker chạy trên máy tính chủ dự án qua Chrome thật và kết nối ra VPS. Chủ dự án chấp nhận máy và Chrome phải mở. API OA chạy 24/7 trên VPS.

## Agent và phòng chat điều phối

- Claude điều phối. Mỗi agent dùng một cuộc chat thật trên nền tảng như Claude, ChatGPT hoặc Gemini. Nút đăng nhập trên màn hình **Cấu hình Agent** mở tab mới vào trang đăng nhập chính thức và gắn vào nhóm tab riêng để Claude thao tác. Chủ dự án tự đăng nhập. Agent cùng nền tảng dùng chung kết nối. Mỗi agent có nút chuyển sang API key. Điều khoản gói cá nhân của nền tảng AI có thể giới hạn truy cập tự động.
- **Phòng chat điều phối** phản chiếu trực tiếp tin từ tài khoản mỗi agent. Chủ dự án, A0, Claude và các agent gọi nhau bằng `@tên`. Mỗi lần gọi tạo phiếu việc có trạng thái mới, đang làm, chờ duyệt hoặc xong. Agent bàn giao kết quả lại cho điều phối.
- Nếu đọc giao diện lỗi, Worker đăng thay agent “@Claude, [agent] đang bị lỗi đọc giao diện, vui lòng cập nhật lại giúp tôi”. Claude dùng kỹ năng đọc trình duyệt để sửa bộ đọc rồi đăng “@[agent], giao diện đã cập nhật, vui lòng tiếp tục công việc được giao trước đó”. Giữ phiếu hiện tại trong khi chờ. Nếu lỗi xảy ra ở tab Claude, báo chủ dự án.

## Dữ liệu và vòng đời

- Agent xem, thêm, sửa và xóa qua Git theo quyền trong repo riêng tư [TTD-Data](https://github.com/DuyKienTTD/TTD-Data). Trên VPS, agent chỉ xem. Mọi bản sửa cần quyền và vẫn đi qua Git. Chủ dự án giữ quyền xóa trực tiếp. Tin khách đến từ Zalo đi thẳng VPS. Dữ liệu khách tuyệt đối không vào Hosting công khai.
- Khi đồng bộ, lưu mã commit và mã bản ghi VPS, xác nhận đã nhận, đổi liên kết tài liệu sang mã bản ghi VPS, sau đó xóa tệp Git đã nhận. AI đồng bộ mặc định hằng ngày hoặc theo yêu cầu. Cơ chế VPS tự quét hoặc webhook để điều tra sau.
- Header mỗi tài liệu có `id`, `lop`, `trang_thai`, `chu_so_huu`, `nguon`, `lien_ket`, `thay_the_boi`, `het_han`.
- `QUAN_TRONG` gồm hồ sơ khách, sản phẩm, quyết định và tri thức đã duyệt. Chỉ đồng bộ lên VPS khi `trang_thai=hieu_luc`.
- `TAM_THOI` gồm nháp, ghi chú phiên và kết quả trung gian. Không đưa lên VPS. Sau 14 ngày mặc định, tự khai tử khỏi Git nếu chưa được nâng lớp.
- `LOI_THOI` phải có `thay_the_boi`. Chuyển liên kết cũ sang bản thay thế. Giữ 30 ngày trước khi khai tử khỏi Git theo danh sách đề xuất được chủ dự án hoặc A0 duyệt. VPS chỉ đánh dấu lưu trữ. Xóa cứng do chủ dự án thực hiện hoặc theo yêu cầu xóa của khách theo Luật 91/2025/QH15.

## Các giới hạn giữ nguyên và thứ tự xây dựng

Giữ guard, ngân sách đã nghiệm thu, opt-out ba trạng thái, Nghị định 91/2020/NĐ-CP và các nghĩa vụ bảo vệ dữ liệu của DIRECTION-02. Chỉ lưu số thử nghiệm trong `.env` trên VPS. Nhánh này ghi quyết định và dựng khung dữ liệu giả lập.

Thứ tự triển khai là dữ liệu và phân quyền, phòng chat điều phối với @, cấu hình agent và đăng nhập, Worker nick Zalo Web, OA API, rồi các kênh còn lại. Chủ dự án duyệt bản phác màn hình trước khi viết mã.
