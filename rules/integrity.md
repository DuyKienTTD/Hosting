---
id: hosting-rule-integrity
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-25
sensitivity: public
---
[Workflow index](AGENT_WORKFLOW.md) — candidate; not effective until approved merge and verification.

## 6. Toàn vẹn dữ liệu và cập nhật (thay thế mục 8 cũ)

Tách tasks (đặc tả/quyền), reports/evidence (bằng chứng bất biến), rules (chính sách), inventory (snapshot), runbooks (thao tác), decisions (quyết định), references (tham khảo). Stable ID, nguồn, owner, verified_at và môi trường; một nguồn thẩm quyền mỗi sự kiện/trường. STATE là hiển thị dẫn xuất có provenance, CATALOG chỉ là registry tri thức dùng chung, không tự cấp quyền. Không đăng ký task, report hoặc evidence vào CATALOG hay các phân vùng của nó. Task ACK là sự kiện có ngày và receipt. Không trộn test với ledger live hoặc secrets. Lỗi cần component/environment/task/run/version, observed/expected, evidence, next owner; khử định danh.

Pre-change: fetch latest, đọc trọn file, pin base, write-set, invariants và rollback. Patch tối thiểu, review toàn diff kể cả phần xóa, metadata, quyền, ngân sách, STOP, source/evidence; kiểm diff, validators, links, secret. Không force-push, phá lịch sử, ghi đè stale hoặc ngoài write-set. Sau push kiểm remote SHA và nội dung bằng readback/diff/hash, không coi HTTP success/test exit 0 là nghiệm thu. Nếu sai, dừng phần phụ thuộc, phục hồi có chọn lọc và ghi changelog. Tuân thủ CONTRIBUTING và REPOSITORY_SECURITY; kiểm soát GitHub/CI chỉ được coi bật khi có bằng chứng thật.

Khi cập nhật canonical event/field, sinh STATE bằng công cụ đã kiểm chứng; cập nhật CATALOG chỉ khi tri thức dùng chung thay đổi, không sinh mục báo cáo từ sự kiện nghiệm thu. Bảo toàn marker và stable ID/path. Quy tắc mới cần A0 approval phù hợp, coordinator exclusivity, security QA, append-only evidence/changelog, cập nhật nguồn có thẩm quyền và các điểm đọc liên quan; không tự merge. Lịch sử phải xác minh theo commit gốc, không sửa hash cũ để tạo PASS.
