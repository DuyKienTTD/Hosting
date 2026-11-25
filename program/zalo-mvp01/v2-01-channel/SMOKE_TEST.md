---
id: v2-01-smoke
type: runbook
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# Smoke test 10 phút

Chuẩn bị trước đồng hồ. Gói Subiz đã bật Zalo cá nhân, quyền tích hợp/webhook và một agent quyền tối thiểu đọc khách/hội thoại/lịch sử và gửi đúng hội thoại thử. Chủ dự án mở Tích hợp → Zalo Cá nhân → Thêm, dùng điện thoại Zalo đang đăng nhập để quét QR và cấp quyền, kiểm Hoạt động. Tạo PAT đúng workspace, có hạn, và lấy secret từ cấu hình webhook sau khi lưu. Chủ dự án nạp PAT và secret vào secret store trên VPS, cấp account ID và định danh nguồn Personal (đối chiếu webhook/conversation với inbox); không ghi vào repo hoặc chat. Cần một người thử đã kết bạn, một người thử riêng đồng ý nhận lời mời nhưng chưa kết bạn, và nhóm thử riêng với thành viên đồng ý, chủ tài khoản có quyền quản trị. Chuẩn bị một nhóm có sẵn và các thành viên thử cho nhóm mới. Chuẩn bị HTTPS endpoint, đường log đã che định danh, cổng STOP, giới hạn số lệnh, fallback tắt và Claude giả lập.

Khi thử B riêng, A0 tạo bot tại Bot Creator, nạp Bot Token, cấp webhook shared secret riêng và HTTPS endpoint, xác nhận bot có quyền nhóm qua `getMe.can_join_groups` và cho bot tham gia nhóm thử. Khi thử C riêng, A0 cấp agent đã có quyền tương ứng và tự đăng nhập phiên trình duyệt dành riêng. D chỉ là khảo sát; không cần cookie hay QR cho thư viện. E nếu cần mục tiêu OA riêng: ứng dụng OA được cấp quyền, OA ID, access/refresh token và cấu hình webhook tương ứng. Claude thật nằm ngoài smoke kênh. Một lượt xác minh Claude riêng cần đúng tổ chức Console đã claim credit, xác minh số dư/expiry/cơ chế không top-up, và API key giới hạn workspace đặt trên VPS.

| Phút | Chạy và tiêu chí |
|---|---|
| 0–1 | `GET /4.1/me` hợp lệ và đúng agent/account. Kiểm kết nối Personal hoạt động, webhook chỉ subscribe sự kiện cần thiết, chính sách thử chỉ cho phép tài khoản/nhóm tổng hợp của pilot. |
| 1–3 | Người thử đã kết bạn gửi nonce văn bản 1:1. Xác nhận HMAC raw bytes, nguồn Personal, CID, actor, event ID và loại hội thoại. Kiểm history theo CID. Replay fixture đã ký trong luồng thử, đúng một event được lưu. |
| 3–5 | Gửi đúng một phản hồi tới CID vừa quan sát. So sự kiện API, history và màn hình người nhận. Lặp cùng key từ client phải trả receipt cũ, số lần người nhận thấy bằng một. Đối chiếu câu trả lời 200 với xác nhận ở đích. |
| 5–7 | Một tin từ nhóm thử và một phản hồi vào đúng nhóm nếu định tuyến đã được xác minh. Kiểm đọc/lịch sử nhóm. Chỉ thử tạo/đổi tên/thêm hoặc bỏ thành viên thử khi UI có thao tác và quyền cụ thể. Ghi riêng nguồn (API/UI), kiểm hậu trạng thái, giữ những quyền chưa thử ở CHƯA RÕ. |
| 7–9 | Từ UI gửi một lời mời tới người thử đã đồng ý, kiểm sender/recipient. Trong pending, yêu cầu nhắn tin bị policy chặn. Người thử chấp nhận, kiểm bằng chứng affirmative ở UI; chỉ ghi event API nếu có payload chứng minh. Đối chiếu hồ sơ và một nhãn/ghi chú tổng hợp nếu quyền có sẵn. |
| 9–10 | Bật STOP; chạy lệnh hợp lệ qua seam thử và xác nhận zero provider call. Giả lập budget hết, khóa cả AI queued. Dừng automation, xuất kết quả đã khử định danh từng capability, thu hồi PAT test, tháo webhook test và dọn nhóm thử theo lịch pilot. |

Dừng khi có sai danh tính/đích, trùng tin, quyền không khớp, nhầm OA/bot với Personal, lỗi xác thực, challenge hoặc kết quả không rõ. Giữ `unknown_delivery` cho đến khi đọc lại và xác nhận. Không ép thử quota live hoặc purge dữ liệu để tạo ca lỗi. PASS từng chức năng yêu cầu evidence từ đúng kênh và đúng người/nhóm được phép.
