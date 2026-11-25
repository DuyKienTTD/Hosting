---
id: hosting-rule-dispatch
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-25
sensitivity: public
---
[Workflow index](AGENT_WORKFLOW.md) — candidate; not effective until approved merge and verification.

## 3. Đặc tả và giao việc

Lưu task trong tasks/, commit/push và gửi URL cố định theo commit + hướng dẫn ngắn. Đặc tả chỉ định đường dẫn báo cáo dự kiến hoặc nguồn roadmap quản lý kết quả; báo cáo dùng cùng TASK_ID, dẫn về đúng phiên bản đặc tả và bằng chứng. Điều phối cập nhật liên kết kết quả trong roadmap hoặc đặc tả thuộc quyền ghi; không yêu cầu Agent tìm nhiệm vụ/báo cáo trong CATALOG. B3 — Một outcome có một owner chịu trách nhiệm trọn vẹn; owner tự phân rã, sửa lỗi và kiểm thử trong phạm vi được cấp. Chỉ tạo work order hoặc chuyển owner khi outcome, phạm vi hoặc trách nhiệm thực sự thay đổi; QA độc lập trên đầu ra hoàn chỉnh và delta bị ảnh hưởng, không bỏ gate an toàn. Một owner chính cho mỗi deliverable; phân vai theo kỹ năng, công cụ, quyền thực tế, không theo danh xưng. Tự thu thập bằng chứng nếu có thể; tham vấn đúng chuyên môn khi cần, đối chiếu nguồn chính thức đúng phiên bản và evidence runtime, không coi tài liệu hãng là bằng chứng quyền live. Không giao Codex khảo sát lại đầu vào đã có.

Task phải nêu TASK_ID, OWNER, MODE, mục tiêu/outcome, FIRST_ACTION, BASE_SHA, READ_SET, PREVIOUSLY_VERIFIED, WRITE_SET, DO_NOT_TOUCH, DEPENDENCIES, TEST_DELTA, INVARIANTS, quyền/cost cap, STOP, rollback, ACCEPTANCE, EVIDENCE, NEXT_OWNER. Chỉ rõ môi trường, kỹ năng, tool, cách bắt đầu, positive/negative/fault cases, nơi nộp kết quả và fallback. Với task nhỏ có thể rút ngắn nhưng không bỏ owner, bước đầu, nghiệm thu, quyền và nơi bàn giao. Một writer trên mỗi path/field; tư vấn H1/H2 chỉ ghi report/evidence và handoff được phép, không sửa owner/status/approval task mẹ.

Handoff ghi task_id, from_agent, to_agent, why_this_agent, objective, first_action, inputs_and_urls, constraints_and_approval, acceptance, deliverable_path, next_owner_or_decision, handoff_state. PREPARED là tài liệu đã ghi; SENT cần kênh gửi thực; B2 — ACKNOWLEDGED chỉ khi cùng một receipt chứng minh TASK_ID, recipient, session, event/phạm vi, thời điểm và nguồn truy xuất được. ACK review khác ACK thực thi; commit chuẩn bị và bằng chứng task/Agent khác không phải ACK. Thiếu định danh phiên hoặc thuộc tính khác thì giữ PREPARED/UNKNOWN đối với tuyên bố chưa xác minh, không bịa UUID; IN_PROGRESS/DONE cần bằng chứng. Không có kênh thì PREPARED_FOR_OWNER_FORWARD; không giả định Agent chạy nền hoặc GitHub comment tự dừng runtime. Chuyển tiếp chính xác URL, không tạo task trùng.
