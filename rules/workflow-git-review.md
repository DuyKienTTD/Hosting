---
id: hosting-rule-workflow-git-review
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-26
sensitivity: public
---
[Workflow](AGENT_WORKFLOW.md)

# Git review và provenance

Tách tasks (đặc tả/quyền), reports/evidence (bằng chứng bất biến), rules (chính sách), inventory (snapshot), runbooks (thao tác), decisions (quyết định), references (tham khảo). Stable ID, nguồn, owner, verified_at và môi trường; một nguồn thẩm quyền mỗi sự kiện/trường. STATE là hiển thị dẫn xuất có provenance, CATALOG chỉ là registry tri thức dùng chung, không tự cấp quyền. Không đăng ký task, report hoặc evidence vào CATALOG hay các phân vùng của nó. Không trộn test với ledger live hoặc secrets. Lỗi cần component/environment/task/run/version, observed/expected, evidence, next owner; khử định danh.

Khi review diff, kiểm cả phần xóa, metadata, quyền, ngân sách, STOP, source/evidence, invariant, phạm vi ghi, link, validators, bí mật và provenance. Kiểm quyền xóa/đổi quyền và phiên bản hiện hành khi có tác động hoặc chỉnh đồng thời.

Tuân thủ [CONTRIBUTING](../CONTRIBUTING.md) và [Security](REPOSITORY_SECURITY.md). Lịch sử phải xác minh theo commit gốc, không sửa hash cũ để tạo PASS.
