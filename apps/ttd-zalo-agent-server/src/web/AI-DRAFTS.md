# Z5-AI-DRAFT · Hợp đồng API nháp OA

Phiên cookie web và chính sách same-origin hiện có áp dụng cho cả ba route. Vai trò `owner` và `support` được đọc, tạo lại và duyệt.

| Method | Route | Request | Response 200 |
|---|---|---|---|
| GET | `/api/v1/conversations/{conversationId}/drafts` | — | `{ drafts: Draft[] }`, tối đa 50 mục, tin mới nhất trước |
| POST | `/api/v1/drafts/{id}/regenerate` | `{ version: number }` | `Draft` |
| POST | `/api/v1/drafts/{id}/approve` | `{ version: number, text?: string }` | `{ id, conversationId, version, text }` đã duyệt |

`Draft` gồm `id`, `conversationId`, `version`, `text`, `state`, `intent`, `reason`, `sourceIds` và `delivery`. State nhận `pending`, `generating`, `ready`, `needs_human`, `approved`. Intent nhận `price`, `technical`, `complaint`, `other` hoặc null. Reason nhận `mock`, `budget`, `consent`, `unavailable`, `no_knowledge` hoặc null. Các giá trị version đổi lúc nhận việc, hoàn tất hoặc duyệt. POST trả 409 khi version cũ hoặc trạng thái không cho phép và 404 khi nguồn không còn hiển thị.

Duyệt được nháp `ready` hoặc lời chuyển người khi `needs_human/no_knowledge`. Duyệt có thể nhận nội dung người vận hành đã sửa, ghi dấu người duyệt và khóa nội dung trong cùng thao tác. Duyệt chỉ trả nội dung bất biến; bước này chưa gửi OA. Để gửi, gọi `POST /api/v1/conversations/{id}/approve` hiện có với `{ text, version }` đúng kết quả vừa duyệt, trong đó `id` là mã nháp. Handler gửi đi qua Guard; nội dung sửa hoặc version sai trả 409. Nút gửi và nút duyệt do UI gọi riêng theo hợp đồng này. Chi tiết `GET /api/v1/inbox/{id}` trả nháp mới nhất qua `InboxDraftReader`. Chi phí soạn nháp ước tính theo ngày Việt Nam (`estimatedAiUsdToday`) chỉ trả cho owner.

Khi OA nhận tin và quyền lưu còn hiệu lực, runtime tạo một nháp theo sự kiện. Router phân loại, support/sales chọn câu đã dựng từ mục tri thức hiện hành trong catalogue TTD-Data hoặc lời chuyển người. API gửi lại nội dung đã duyệt. Hai lượt dùng cùng ledger và giới hạn ngày/tháng. Audit chi phí nằm trong ledger với khóa `oa-draft:<id>:<version nhận việc>:route|compose`, model, input/output/cache token và chi phí ước tính bằng phần tỉ USD. Nội dung không nằm trong ledger. Mock và lượt bị chặn bởi ngân sách không gọi Router.

DB hiện hữu cần chạy `postgres/012-ai-drafts.sql` sau migration web 009/010 và trước khi đổi runtime. Image mới áp dụng migration khi khởi tạo DB. Nháp AI tham chiếu tin nguồn, ẩn khi tin nguồn bị cách ly và được xóa cùng tin nguồn khi purge.
