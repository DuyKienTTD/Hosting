---
id: hosting-rule-workflow-kng
type: rule
status: draft
owner: Chat Dieu phoi
parent: rules/AGENT_WORKFLOW.md
updated_at: 2026-11-26
sensitivity: public
---
[Workflow](AGENT_WORKFLOW.md)

# Định tuyến và release gate KNG

KNG-01 routing: đọc [source snapshot](../program/current.json) và [release-state gate](../program/kng/release_state.py). Chỉ coi KNG effective sau phê duyệt A0 đúng candidate SHA/tree, merge method merge và independent authenticated remote main readback đúng merge commit/tree/hai parent theo thứ tự. Thiếu/mâu thuẫn/stale: NOT_EFFECTIVE, STOP new dispatch; nguồn main có hiệu lực trước đó vẫn kiểm soát. Source snapshot KNG_ONLY, A1 scoped author, Work source QA đã hoàn thành, không phải ACK nhiệm vụ mới. Không suy diễn quyền từ báo cáo lịch sử.

Đọc thêm [STATE](../STATE.md) và authority live. Nếu định tuyến ngoài KNG hoặc cập nhật trạng thái tổng hợp, đọc [routing](workflow-routing.md). Nếu có release, thực thi thao tác hạn chế hoặc giao việc, cộng các nguồn theo Workflow.
