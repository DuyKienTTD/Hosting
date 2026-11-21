---
id: multi-agent-handoff
type: rule
status: current
updated_at: 2026-11-21
sensitivity: public
---

# Quy ước chung: giao việc và bàn giao qua GitHub

Áp dụng cho Codex, ChatGPT Work và mọi tác nhân có quyền truy cập repository. Mục đích: **GitHub là nơi lưu tài liệu làm việc và kết quả có thể truy xuất**, còn tin nhắn giao việc chỉ cần ngắn gọn và dẫn link. Không áp đặt kỹ thuật triển khai, cấu trúc code hay checklist cứng khi không cần.

## 1. Nguồn chính, không dựa vào lịch sử chat

- Bắt đầu từ [README](../README.md) -> [PROJECT](../PROJECT.md) (mục tiêu) -> [STATE](../STATE.md) (tiến độ) -> [CATALOG](../CATALOG.yaml) (danh mục) -> [AGENTS](../AGENTS.md) (quy tắc).
- Chỉ đọc tài liệu chi tiết của công việc đang được giao. Nếu thiếu dữ liệu, tìm trong repository, rồi xác minh tại hệ thống live nếu có quyền.
- GitHub phản ánh lần kiểm tra/báo cáo cuối; trạng thái thực của VPS, WordPress, n8n, Hermes, Google Ads... phải kiểm tra lại khi có thay đổi theo thời gian.
- Không tự suy diễn rằng quyền truy cập GitHub cũng là quyền thay đổi các hệ thống production.

## 2. Giao nhiệm vụ: tài liệu đầy đủ trên Git

- Người tạo nhiệm vụ lưu **đặc tả đầy đủ** vào `tasks/` (ví dụ `tasks/2026-11-21-n8n-hermes-integration-audit.md`), commit/push rồi gửi **URL trực tiếp + hướng dẫn một đến hai câu** cho tác nhân nhận việc.
- Không cần gửi lại nguyên văn đặc tả trong chat nếu đường dẫn truy cập được.
- Tối thiểu trong task: mục tiêu/kết quả mong muốn, bối cảnh/link nguồn, phạm vi/giới hạn quyền, tiêu chí nghiệm thu có thể kiểm chứng, nơi nộp kết quả. Các bước kỹ thuật chỉ là gợi ý trừ khi là ràng buộc bắt buộc.
- Tác nhân có quyền tự chọn công cụ, phương pháp và thứ tự tối ưu; chủ động giải quyết vướng mắc không trọng yếu. Không xem danh sách phương pháp là khóa cứng.
- Nếu không thể đọc link, nói rõ bị chặn và yêu cầu quyền hoặc phương án truy xuất khác; không bịa nội dung.

## 3. Khi tác nhân làm việc

- Xác nhận branch/commit của tài liệu nhận việc và trạng thái hiện hành; tránh ghi đè kết quả tác nhân khác.
- Phân biệt **đã đo/đã làm**, **đề xuất**, **chưa kiểm chứng**, **bị chặn** và **không thực hiện**.
- Được thực hiện công việc trong phạm vi đã giao. Các thao tác có thể phá hủy dữ liệu, làm gián đoạn dịch vụ, thay đổi chi phí/ngân sách hoặc xuất bản phải có ủy quyền cụ thể.
- Nếu phát hiện thiếu quyền hoặc phụ thuộc bên ngoài, ghi BLOCKED rõ nguyên nhân, bằng chứng và hướng xử lý; vẫn hoàn thành phần độc lập có thể làm.
- Tránh thiết kế thêm quy trình hành chính, biểu mẫu và phê duyệt không đem lại lợi ích thực tế.

## 4. Bàn giao: báo cáo được push lại GitHub

- Lưu **báo cáo có bằng chứng** trong `reports/` với ngày và mã task liên quan. Các tài sản kết quả (code, script, cấu hình mẫu, artifact phù hợp Git) lưu ở thư mục tương ứng và dẫn link từ báo cáo.
- Báo cáo tối thiểu: task/link; thời điểm; phạm vi thực tế; thay đổi đã thực hiện và nơi triển khai; kết quả kiểm thử (PASS/FAIL/BLOCKED); bằng chứng/log đã làm sạch; rủi ro còn lại; bước tiếp theo.
- Cập nhật `STATE.md` khi trạng thái dự án đổi, `CATALOG.yaml` khi thêm tài liệu có thẩm quyền, `CHANGELOG.md` khi có thay đổi đáng kể. Đừng viết lại báo cáo lịch sử để che dấu lỗi.
- Commit và push lên repository/nhánh được giao, xác minh đã xuất hiện trên remote. Nếu không được quyền push, cung cấp bản vá/tài liệu và ghi trạng thái `NOT_PUSHED`.
- Tin nhắn bàn giao chỉ cần: **kết quả ngắn + link báo cáo + link commit/PR + việc còn vướng**. Không cần dán lại toàn bộ báo cáo.

## 5. Cập nhật đồng thời và xung đột

- Mỗi tác vụ nên có file task và report riêng; ưu tiên branch/PR khi nhiều tác nhân cùng sửa hoặc thay đổi mã vận hành.
- Trước khi push, lấy trạng thái mới của nhánh, kiểm tra diff và hòa giải xung đột. Không force-push ghi đè công việc người khác.
- Khi xung đột thông tin, tài liệu có bằng chứng xác minh mới hơn và hệ thống live được ưu tiên, nhưng phải lưu vết thay đổi.

## 6. Bảo mật và tính linh hoạt

- Tuân thủ [quy tắc repository](REPOSITORY_SECURITY.md); thông tin nhạy cảm đã được chủ sở hữu quản lý, nhưng mọi dữ liệu **mới** trước khi commit phải được rà soát.
- Không tự ý đưa bí mật hoặc dữ liệu cá nhân chưa được xử lý lên repository public.
- Được đề xuất sửa quy ước nếu gây cản trở thực tế; giải thích lý do trong commit/report. Quy tắc này đặt **đích đến và tiêu chuẩn chứng cứ**, không áp đặt một lối làm việc duy nhất.

## Mẫu lời giao việc cực ngắn

> Đọc https://github.com/DuyKienTTD/Hosting/blob/main/README.md và tài liệu task tại [URL]. Thực hiện trong giới hạn nêu ở task; đẩy báo cáo, bằng chứng và cập nhật trạng thái lên GitHub. Trả lại các URL kết quả.

## Mẫu lời bàn giao cực ngắn

> Task: [mã]. Kết quả: [PASS/PARTIAL/BLOCKED]. Báo cáo: [URL]. Commit/PR: [URL]. Việc cần quyết định: [nếu có].
