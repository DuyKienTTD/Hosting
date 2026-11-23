# Chat Điều phối — Roadmap Portfolio & Release Governance

**Owner:** Chat Điều phối | **ROADMAP_STATUS:** `PLANNED_NOT_ACKED` | **READ_SET:** master project/rules, PR31/PR6 and program docs, all four Agent roadmaps | **WRITE_SET:** own coordinator roadmap, nonconflicting integration/decision document and PR comments. **STOP:** author/reviewer conflict, stale pins, no owner ACK, invalid paid/release gates.

| ID | Required skills | Task / measurable deliverable | Depends | Status | Evidence / UTC |
|---|---|---|---|---|---|
| G0-03 | K-DOC,K-SCHEMA | Produce dependency graph and milestones M0–M5 reconciled with A2 product charter | G0-01,G0-02 | PLANNED | — |
| G2-01 | K-DOC,K-SCHEMA,K-SEC | Implement candidate roadmap-level self-progress and single roadmap acceptance policy | product/wbs | PLANNED | — |
| G2-03 | K-SEC,K-QA,K-DOC | Propose risk-tier QA, approval and rollback invariants, with no per-item management review | G2-01 | PLANNED | — |
| G3-02 | K-GIT,K-DATA | Reuse PR31 34-PR classification, prioritize outcome-by-dependency, resolve owner clashes | G0-03 | PLANNED | — |
| G3-03 | K-GIT,K-SCHEMA | Issue scoped per-agent roadmaps to actual sessions; record real ACK only, no false dispatch | G2-01,G3-02 | PLANNED | — |
| REL-01 | K-QA,K-SEC,K-GIT | Collect agent roadmap-level handoffs and issue integrated factual verdict | all ready roadmaps | PLANNED | — |
| REL-02 | K-SEC,K-DOC | Present owner A0 one portfolio decision and approvals only for material exceptions | REL-01 | PLANNED | — |

**KNG-01 priority override (2026-11-23):** All unrelated roadmap feature items are ON_HOLD_DEPENDENCY_KNG01 until Work independent QA, coordinator integration, A0-authorized merge and a new dispatch/actual ACK. Historical PLANNED items remain proposals, not current task orders.

**Completion:** one compact integrated portfolio milestone report and only evidence-backed remaining blocker list. Do not replicate every agent's per-item status in seven different files. A0 and coordinator never need to accept safe routine roadmap items separately.
## Cách tự cập nhật

Chủ roadmap cập nhật **chính file này** sau khi hoàn thành một đầu việc: chuyển `PLANNED → IN_PROGRESS → DONE_WITH_EVIDENCE`, ghi `EVIDENCE` (commit/PR/log/source link), `UTC`, kết quả PASS/FAIL và lỗi thực tế. Không yêu cầu A0/Điều phối nghiệm thu từng dòng. Chỉ thông báo một lần khi roadmap đạt `READY_FOR_ROADMAP_ACCEPTANCE` hoặc `ROADMAP_PARTIAL_BLOCKED`. Nếu còn công việc an toàn độc lập, phải làm tiếp. Không đẩy secret hoặc PII lên Git.

Nếu cuối roadmap có hạng mục thực sự không thể thực hiện sau các nỗ lực hợp lệ, phải sử dụng nguyên văn: **Đã làm hết công việc có thể làm, một số công việc chưa thể làm do "Bảo mật"/ "Giới hạn kỹ thuật".** Kèm từng lỗi, bước đã thử, bằng chứng và hướng khắc phục. Không suy diễn môi trường hay quyền chỉ từ tên tài khoản.

Quy trình và các giới hạn: [Operating Protocol](../OPERATING_PROTOCOL.md). Quy tắc hiện hành trên main luôn có hiệu lực cho tới khi candidate được tích hợp hợp lệ.