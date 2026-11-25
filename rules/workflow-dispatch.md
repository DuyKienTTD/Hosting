---
id: hosting-rule-workflow-dispatch
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-26
sensitivity: public
---
[Workflow](AGENT_WORKFLOW.md)

# Đặc tả và giao việc

Lưu task trong tasks/, commit/push và gửi URL cố định theo commit + hướng dẫn ngắn. Đặc tả chỉ định đường dẫn báo cáo dự kiến hoặc nguồn roadmap quản lý kết quả; báo cáo dùng cùng TASK_ID, dẫn về đúng phiên bản đặc tả và bằng chứng. Điều phối cập nhật liên kết kết quả trong roadmap hoặc đặc tả thuộc quyền ghi; không yêu cầu Agent tìm nhiệm vụ/báo cáo trong CATALOG. B3 — Một outcome có một owner chịu trách nhiệm trọn vẹn; owner tự phân rã, sửa lỗi và kiểm thử trong phạm vi được cấp. Chỉ tạo work order hoặc chuyển owner khi outcome, phạm vi hoặc trách nhiệm thực sự thay đổi; QA độc lập trên đầu ra hoàn chỉnh và delta bị ảnh hưởng, không bỏ gate an toàn. Outcome phải hữu ích độc lập, có acceptance đo được; gộp đọc, sửa, test và cập nhật hành chính vào outcome, giữ riêng quyết định merge/STOP/chi phí dành riêng. Phân vai theo kỹ năng, công cụ, quyền thực tế, không theo danh xưng. Tự thu thập bằng chứng nếu có thể; tham vấn đúng chuyên môn khi cần, đối chiếu nguồn chính thức đúng phiên bản và evidence runtime, không coi tài liệu hãng là bằng chứng quyền live. Không giao Codex khảo sát lại đầu vào đã có.

Task phải nêu TASK_ID, SPEC_ID, OWNER, MODE, OUTCOME, FIRST_ACTION, BASE_REF (BASE_SHA khi pin Git), AUTHORITY, STATUS (tham chiếu trạng thái tổng hợp), READ_SET, PREVIOUSLY_VERIFIED, WRITE_SET, DO_NOT_TOUCH, DEPENDENCIES, TEST_DELTA, INVARIANTS, quyền/cost cap, STOP, rollback, ACCEPTANCE, EVIDENCE, NEXT_OWNER. Chỉ rõ môi trường, kỹ năng, tool, cách bắt đầu, positive/negative/fault cases, nơi nộp kết quả và fallback. Với task nhỏ có thể rút ngắn nhưng không bỏ owner, bước đầu, nghiệm thu, quyền và nơi bàn giao. Pin nguồn canonical, không sao chép quy tắc dài. Agent chỉ ghi kết quả/evidence trong write-set; Điều phối giữ owner, quyền và trạng thái tổng hợp. Một writer trên mỗi path/field; tư vấn H1/H2 chỉ ghi report/evidence và handoff được phép, không sửa owner/status/approval task mẹ.

Ưu tiên chi phí + thời gian + chất lượng + rủi ro. WHY_DELEGATE/COST_ROUTING ghi năng lực, công cụ, phương án rẻ hơn, quyền, reviewer và giới hạn.
