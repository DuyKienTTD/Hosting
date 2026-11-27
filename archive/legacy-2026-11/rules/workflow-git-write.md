---
id: hosting-rule-workflow-git-write
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-26
sensitivity: public
---
[Workflow](AGENT_WORKFLOW.md)

# Ghi Git

Pre-change: fetch latest, đọc trọn file, pin base, write-set, invariants và rollback. Patch tối thiểu, review toàn diff kể cả phần xóa, metadata, quyền, ngân sách, STOP, source/evidence; kiểm diff, validators, links, secret. Không force-push, phá lịch sử, ghi đè stale hoặc ngoài write-set. Sau push kiểm remote SHA và nội dung bằng readback/diff/hash, không coi HTTP success/test exit 0 là nghiệm thu. Nếu sai, dừng phần phụ thuộc, phục hồi có chọn lọc và ghi changelog. Tuân thủ CONTRIBUTING và REPOSITORY_SECURITY; kiểm soát GitHub/CI chỉ được coi bật khi có bằng chứng thật.

Quy tắc mới cần A0 approval phù hợp, coordinator exclusivity, security QA, append-only evidence/changelog, cập nhật nguồn có thẩm quyền và các điểm đọc liên quan; không tự merge.

Khi ghi đặc tả hoặc ghi dùng chung cho task, áp dụng ownership và write-set trong [dispatch](workflow-dispatch.md). Khi cập nhật trường/sự kiện canonical, đọc thêm [routing](workflow-routing.md).
