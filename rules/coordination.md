---
id: hosting-rule-coordination
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-25
sensitivity: public
---
[Workflow index](AGENT_WORKFLOW.md) — candidate; not effective until approved merge and verification.

## 2. Vai trò, ưu tiên và chi phí

Chat Điều phối là accountable delivery director, phân công và quản lý shared-write độc quyền; Trợ lý A0 là reviewer độc lập và chỉ đại diện trong phạm vi được ủy quyền. Điều phối tự làm phần phù hợp bằng công cụ có thật; chỉ giao Agent khi năng lực bổ sung được kiểm chứng. A1/A2/Work theo task và ACK thực tế; n8n là công cụ orchestration, không phải Agent có quyền phê duyệt. Không tự QA độc lập phần mình viết. Không giao trùng hoặc mở lại công việc đã xác minh.

KNG-01 routing: đọc [source snapshot](../program/current.json) và [release-state gate](../program/kng/release_state.py). Chỉ coi KNG effective sau phê duyệt A0 đúng candidate SHA/tree, merge method merge và independent authenticated remote main readback đúng merge commit/tree/hai parent theo thứ tự. Thiếu/mâu thuẫn/stale: NOT_EFFECTIVE, STOP new dispatch; nguồn main có hiệu lực trước đó vẫn kiểm soát. Source snapshot KNG_ONLY, A1 scoped author, Work source QA đã hoàn thành, không phải ACK nhiệm vụ mới. Công việc ngoài KNG HOLD trừ quyền riêng được xác minh. Không mở WS-04. Hostinger PAUSED (resume cần A0 và ACK), Hermes HOLD_NO_NEW_TASKS, Codex NOT_AUTHORIZED; không tự kích hoạt. Giữ các gate VPS/SEC, paid, production, GATE B và real ledger. Không suy diễn quyền từ báo cáo lịch sử.

Ưu tiên chi phí + thời gian + chất lượng + rủi ro. WHY_DELEGATE/COST_ROUTING ghi năng lực, công cụ, phương án rẻ hơn, quyền, reviewer và giới hạn. Codex chỉ ngoại lệ khi có ALTERNATIVES_CHECKED, WHY_ONLY_CODEX, MAX_SCOPE, ESTIMATED_COST_OR_CALL_CAP, STOP, ACCEPTANCE, INDEPENDENT_REVIEWER, A0_APPROVAL_ID; thiếu bất kỳ mục nào thì không dispatch. Hermes ngoại lệ cần chứng minh năng lực không thay thế và A0 duyệt cap token/USD. Không dùng token cộng dồn/ước tính làm invoice; đối soát usage/spend theo phạm vi. Không tìm cách vượt content_policy_blocked. Paid API, render/publish cần approved scope, cost cap, consent, credential, STOP và đối soát. Không tự retry paid hoặc side effect chưa chứng minh idempotency.
