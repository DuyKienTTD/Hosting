---
id: data-lifecycle-context-management
type: rule
status: candidate
updated_at: 2026-11-24
sensitivity: public
---
# Data Lifecycle & Context Management Protocol

Phạm vi: dữ liệu quản trị HOSTING trên GitHub, không phải chính sách lưu dữ liệu khách hàng hoặc quyền thao tác production. Kế thừa [quyết định A0](https://github.com/DuyKienTTD/Hosting/pull/59#issuecomment-7136686998). Protocol này là candidate; không cấp thêm quyền. [Workflow](AGENT_WORKFLOW.md) và [Security](REPOSITORY_SECURITY.md) giữ nguyên các gate.

## 1. Một nguồn chính cho mỗi thông tin
- rules/: quy tắc; agents/: vai trò/năng lực; program/: roadmap, owner và tiến độ; tasks/: đặc tả; reports/: kết quả; reports/evidence/: bằng chứng; decisions/: quyền/quyết định; knowledge/: bài học tái sử dụng; checkpoints/: điểm tiếp tục phiên.
- CATALOG chỉ tri thức dùng chung, không chứa task/report/evidence. Các phân vùng là bản đọc dẫn xuất, không phải nguồn ghi thứ hai.
- TASK_ID ổn định xuyên đặc tả, báo cáo, evidence; report trỏ URL đặc tả pin commit và evidence; roadmap/task do writer hợp lệ cập nhật backlink kết quả. Không tạo registry vận hành thứ hai.

## 2. Vòng đời
| Loại | Giữ đến | Khi đóng |
|---|---|---|
| DURABLE | còn giá trị, nghĩa vụ hoặc dependency | giữ bản chuẩn; review khi thay đổi |
| ACTIVE | task/milestone kết thúc | giữ đặc tả, quyết định, kết quả cần thiết; chuyển phần tạm sang kiểm tra dọn |
| TEMPORARY | hết mục đích hoặc task đóng | đề xuất dọn, không xóa tự động |
Metadata mới khi phù hợp: lifecycle, owner, task_id, review_on (YYYY-MM-DD) hoặc retention_trigger, protected_reason nếu cần giữ. Không sửa hàng loạt hồ sơ lịch sử để ép schema. ACTIVE/TEMPORARY thiếu owner hoặc trigger là lỗi cho hồ sơ mới. Quá hạn là cảnh báo cần xử lý, không tự xác định quyền xóa. Không đặt TTL chung cho bằng chứng.
Quyền, STOP, an toàn, tài chính, kiểm toán, rollback, QA độc lập, regression và dependency còn dùng phải giữ. Trước xóa: owner có quyền, kiểm tham chiếu ngược và nguồn ngoài repo khi cần, xác nhận retention, pin commit phục hồi, diff/QA và readback. Không rewrite Git history. Không coi xóa file là thu hồi bí mật.

## 3. Context theo nhiệm vụ
Bắt đầu: xác minh main HEAD, quyết định mới nhất, đọc đủ rules/security/STATE/hồ sơ vai trò/đặc tả chính xác; CATALOG chỉ đọc mục cần. Nguồn dùng để ra quyết định phải đọc đủ; nếu truncation, chia khoảng dòng liên tục theo cùng SHA, kiểm đầu/cuối; PARTIAL_READ nếu thiếu. Không nạp toàn bộ báo cáo lịch sử hoặc toàn kho theo mặc định.
Trong task: READ_SET theo dependency, pin nguồn; dùng evidence tương đương, không rerun nếu không có change trigger. Tách facts, assumptions, authority, evidence và open blockers. Context ngắn gồm mục tiêu, quyền/STOP, SHA, trạng thái, evidence links, next action; không chép toàn chat. Không tự đặt giới hạn token khiến bỏ sót bảo mật. Đo byte/tài liệu thực tế; byte không đồng nghĩa token hoặc chi phí.
Khi chuyển phiên: checkpoint tối thiểu trong nguồn đang dùng hoặc file riêng nếu cần, chỉ rõ completed, pending, first action, next owner và links; không tạo thêm checkpoint khi không có thay đổi. PREPARED không phải SENT/ACK.

## 4. Kiểm soát tự động
Chạy `python scripts/validate-data-integrity.py --root . --base <trusted-base-commit> --json` và `python -m unittest discover -s scripts -p 'test_data_integrity.py'`. Bộ kiểm tra read-only, không network, không API, không tự xóa hay sửa. Kiểm tra CATALOG/phân vùng, ID/path, link Markdown tương đối, metadata/lifecycle của file mới hoặc sửa, liên kết task/report mới, đường dẫn bị cấm, mẫu credential, file bị xóa và context read-set. Các kiểm tra cấu trúc là bổ sung cho KNG provenance và security QA, không thay thế chúng.
Exit 0: không phát hiện lỗi trong scope; exit 1: lỗi; exit 2: thiếu prerequisite/scope không thể xác minh. WARN: cần owner xử lý; lịch sử không phù hợp schema mới không được tự sửa. Không tuyên bố PASS toàn repo nếu chỉ kiểm subset. Không in giá trị bí mật hoặc raw payload.
Before push: review diff, kiểm tra script và phạm vi; after push: exact remote readback. CI chỉ được coi active khi có run thực tế. Quyền merge, production, paid, real data và independent QA không thay đổi.
