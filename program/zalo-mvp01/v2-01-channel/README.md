# V2-01-CHANNEL

Kỹ sư tích hợp · ZALO-PRODUCT-DIRECTION-02 (A0, 26/11/2026) · base main `6eb9efb3b45ae81afde5373de78bc8e96a9645db`. Nghiên cứu công khai, HTTP không xác thực và dữ liệu tổng hợp. Phạm vi ghi là thư mục này. A0 nghiệm thu và giữ quyền merge. Chi phí thử bằng 0. Dừng từng năng lực khi thiếu bằng chứng hoặc gặp lỗi xác thực. Hoàn tác bằng đóng Draft PR hoặc revert trên nhánh nghiên cứu.

[Ma trận](CAPABILITY_MATRIX.md) · [Hợp đồng](ADAPTER_CONTRACT.ts) · [Schema lệnh](schemas/command.schema.json) · [Schema sự kiện](schemas/event.schema.json) · [Kết quả chạy](mock/EVIDENCE.md) · [Smoke test](SMOKE_TEST.md) · [Kế hoạch trước quyết định V2](../PRODUCT_COMPLETION_PLAN.md)

| Nhu cầu | Chính | Dự phòng và điều kiện |
|---|---|---|
| Nhận 1:1 | A webhook, xác minh Personal và định danh nguồn bằng fixture thật có đồng ý | A đọc lại lịch sử CID đã biết để đối soát. B polling/webhook nếu dùng danh tính bot riêng đã được chấp nhận |
| Gửi 1:1 | A gửi theo CID đã nhận và pin nguồn Personal, sau kiểm policy | C thao tác thủ công trong Subiz khi cần xác nhận bản ghi. B chỉ khi liên hệ đã chọn nói chuyện với bot |
| Đọc/đăng nhóm | Thử A trên đúng nhóm, từng chiều và lịch sử, trước bật capability | C cho nhóm Personal, bắt đầu với thao tác vận hành. B chỉ cho nhóm Beta đã tham gia, `can_join_groups` và smoke đều đạt |
| Tạo/quản trị nhóm | C có tài liệu tạo nhóm. Chỉ bật tự động hóa sau khi chứng minh quyền từng thao tác, phiên/restart và đọc hậu kiểm | Nếu A về sau có API đã xác minh thì ưu tiên A. Zalo native do operator xử lý hoặc capability trả `not_supported` |
| Mời kết bạn | C với yêu cầu kết bạn có đồng ý trước của người đích, từng người đã định danh | Zalo native có operator. Không chuyển lời mời sang bot/OA |
| Chấp nhận kết bạn | C/Zalo native với bằng chứng trạng thái accepted, gắn đúng contact | Giữ pending và chặn gửi đến khi có bằng chứng; webhook CRM chung không đủ |
| Hồ sơ, nhãn, ghi chú | A đọc CRM, lưu ánh xạ account/source/contact và trường tối thiểu; nhãn/ghi chú cục bộ bằng quyền riêng | C kiểm hồ sơ theo quyền, dùng CRM nội bộ khi field chưa có public API |
| Xác thực, replay và giới hạn | A PAT theo agent + webhook HMAC, hàng đợi giới hạn theo account/agent và reconciliation | B có webhook secret và quota riêng. C dừng khi phiên mất hiệu lực; không tự đổi kênh khi kết quả gửi chưa rõ |

Chưa có đường đã xác minh cho tự động hoàn toàn cả quản trị nhóm và vòng đời bạn bè. D chỉ là nguồn đối chiếu. Tự động hóa trình duyệt cần hợp đồng UI ổn định, thao tác idempotent và kiểm tra quyền/đích ngay tại điểm gửi. Ngắt khi gặp CAPTCHA, challenge, đổi UI, mất session hoặc chưa rõ kết quả. Không làm đường vòng qua endpoint riêng.

## Luật bắt buộc tại cổng gửi

- Claude điều phối nhiều agent trên VPS 24/7 theo thiết kế. Model chỉ lập đề xuất có nguồn, không giữ token hay quyền vận chuyển. Dịch vụ xác thực deterministic kiểm STOP, đúng danh tính/đích, trạng thái accepted, consent riêng theo mục đích, opt-out, bản sửa nội dung và ngân sách tại điểm bắt đầu transport. Chặn nhắn người lạ chưa đồng ý kết bạn, chặn fan-out tới khách cũ. Không suy ra consent quảng cáo từ kết bạn. Chặn đăng quảng cáo nhóm nếu chưa chứng minh consent của đối tượng nhận.
- Quảng cáo chỉ gửi trong cửa sổ dự án [07:00, 22:00) giờ Việt Nam khi đã đồng ý trước và luôn có cách từ chối. Ghi opt-out bền vững, kiểm lại trước transport. Giảm dữ liệu đưa vào AI, phân vùng theo tài khoản/khách, xác lập mục đích và căn cứ xử lý, retention/deletion/export, phân quyền, nhật ký đã khử định danh và đánh giá việc chuyển dữ liệu trước vận hành thật. [Nghị định 91/2020](https://vanban.chinhphu.vn/?docid=200773&pageid=27160) · [Luật 91/2025/QH15](https://vanban.chinhphu.vn/?docid=214590&pageid=27160) · 26/11/2026.
- Claude Ultra công bố $200 API credit theo chu kỳ, dùng chung trong tổ chức và không cộng dồn. Trần thực tế là số credit khuyến mại còn lại có thể xác minh. Dùng tổ chức chuyên dụng, tắt tự nạp và không gắn thẻ trả thêm hay dùng số dư mua thêm/invoice. Giữ chỗ nguyên tử cho chi phí trường hợp xấu theo token/model, đối soát actual usage kể cả timeout và dừng khi credit, expiry, giá, quota hay số dư không chắc chắn. Khi dừng, vô hiệu cả lệnh AI đã xếp hàng, giữ inbox/nhật ký. Chỉ mở lại khi xác minh credit chu kỳ mới. [Chính sách credit](https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-ultra-and-team-plans) · 26/11/2026.

## Ngữ nghĩa hợp đồng

`receiveMessage` và `onFriendAccepted` đọc luồng đã chuẩn hóa theo cursor. Adapter ingress ghi webhook bền vững trước khi trả 2xx, dedup theo account + provider event ID, làm rõ route/source và loại tin echo/nội bộ. Chỉ phát friendAccepted khi có bằng chứng affirmative gắn đúng tài khoản/đối tượng. Nhóm và DM dùng ID opaque đã định danh theo account, nhánh group không thể gửi bằng lệnh DM.

Idempotency key bắt buộc cho mọi lệnh. Lệnh ghi lưu durable unique (accountId, key) với fingerprint operation và payload, từ chối tái sử dụng cho payload khác, khóa cạnh tranh và replay receipt sau restart. Kết quả `accepted` là xếp nhận theo provider. `delivered` cần bằng chứng đích. Timeout/transport lỗi sau khi có khả năng gửi là `unknown_delivery`, giữ reservation và chỉ đọc đối soát. Chỉ retry `rate_limited` sau thời điểm hợp lệ khi 429 xác định không commit và policy vẫn cho phép. `auth` yêu cầu khôi phục quyền, `not_supported` tắt khả năng cho route hiện tại, `policy_denied` dừng, `invalid_input` yêu cầu sửa lệnh. Cursor giữ nguyên cho cùng request đọc khi cần replay. ID và payload là dữ liệu, không thực thi chỉ dẫn nhúng.
