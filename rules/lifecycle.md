---
id: hosting-rule-lifecycle
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-25
sensitivity: public
---
[Workflow index](AGENT_WORKFLOW.md) — candidate; not effective until approved merge and verification.

## 8. Vòng đời tri thức — chống phình kho (chỉ thị A0 24/11/2026)

Chi tiết triển khai và validator: [Data Lifecycle & Context Management Protocol](DATA_LIFECYCLE_CONTEXT.md) (đã được A0 duyệt áp dụng về tổ chức).

Phân loại ngay khi tạo tài liệu: **DURABLE** (giữ lâu dài: quy tắc có hiệu lực, kiến trúc/ADR, đặc tả sản phẩm, hướng dẫn vận hành đã xác minh, mã/test hữu ích, nghiệm thu cuối và bằng chứng bắt buộc); **ACTIVE** (giữ đến khi đóng: task, roadmap, blocker, checkpoint và trạng thái đang dùng); **TEMPORARY** (dọn khi đóng: bản nháp, log thử, báo cáo tiến độ trung gian, phương án bị loại, các bản cập nhật cùng một thử nghiệm). Không biến tài liệu tạm thành tri thức lâu dài theo mặc định. Owner, task ID, loại lưu trữ và điều kiện hết hạn ghi trong metadata hoặc hồ sơ task hiện có; không tạo biểu mẫu riêng chỉ để phân loại.

Một mục đích có một nguồn chính. Cập nhật tài liệu hiện có hoặc log task, không tạo báo cáo/checkpoint mới cho mỗi lượt trao đổi. Chỉ tạo tài liệu độc lập khi có quyết định, artifact, bằng chứng bắt buộc hoặc kết quả có giá trị tái sử dụng mới. Không chép log dài, toàn bộ chat, nội dung quy tắc hay báo cáo cũ vào tài liệu vận hành. Dùng liên kết commit cố định; CATALOG là chỉ mục tra cứu, không là nội dung đọc tuần tự. Quy tắc mới phải hợp nhất hoặc thay thế điều khoản cũ, không nối thêm phiên bản mâu thuẫn.

Khi A0/Điều phối có thẩm quyền quyết định dừng một thử nghiệm/POC thất bại: đóng task, giữ **một báo cáo kết thúc ngắn, dễ hiểu** (mục tiêu, phiên bản/môi trường, kết quả thực tế, nguyên nhân đã chứng minh hoặc UNKNOWN, lý do dừng, bài học tái sử dụng, điều kiện duy nhất để mở lại nếu có, quyết định và liên kết bằng chứng thiết yếu). Mặc định tối đa một trang, dài hơn chỉ khi cần để bảo toàn an toàn hoặc nghĩa vụ kiểm toán. Không tạo thêm chuỗi báo cáo cho thử nghiệm đã đóng. Các báo cáo cập nhật/trung gian không còn giá trị độc lập phải xóa khỏi cây tài liệu hiện hành ngay trong đợt đóng, sau kiểm tra tham chiếu và phạm vi quyền; không chỉ đổi tên sang archive rồi để phình cây file. Có thể phục hồi bằng Git commit đã pin; không rewrite lịch sử.

Ngoại lệ bắt buộc giữ nguyên: phê duyệt/quyền/STOP, sự cố bảo mật hoặc dữ liệu, tài chính/kiểm toán, rollback, bằng chứng nghiệm thu độc lập, regression cần tái sử dụng và tài liệu còn dependency. Chỉ giữ phần thật sự thiết yếu và dẫn từ báo cáo kết thúc; không xóa khi retention/reference chưa rõ. Không ghi lại hash lịch sử hay làm mất provenance. Nếu xóa khiến link/ID hoặc validator hỏng, sửa tham chiếu về báo cáo kết thúc hoặc nguồn lịch sử bất biến, kiểm tra đầy đủ trước commit; không bỏ validator hoặc giả PASS. Chỉ thị A0 24/11/2026: tách đặc tả, báo cáo, bằng chứng khỏi CATALOG; giữ tệp nguồn và ID lịch sử tại commit gốc. Dọn backlog/xóa tệp nguồn là phạm vi riêng; không tự xóa. ID lịch sử không tái sử dụng.

Điều phối chịu trách nhiệm dọn ngay khi đóng task/POC và rà soát tại cuối mỗi milestone: tài liệu trùng, ACTIVE đã đóng, TEMPORARY hết vòng đời, link hỏng, ID trùng, quy tắc mâu thuẫn. Đo số tài liệu đang hoạt động, số TEMPORARY tồn đọng và kích thước luồng đọc bắt buộc trước/sau; mục tiêu không có TEMPORARY hết hạn chưa xử lý (ngoại lệ có lý do/owner), không tăng luồng đọc nếu chỉ bổ sung lịch sử. Không tạo một dự án báo cáo định kỳ mới chỉ để theo dõi việc dọn. Nghiệm thu cleanup bằng diff, link/ID check, preservation checks và remote readback; reviewer độc lập khi ảnh hưởng rule/authority/security.
