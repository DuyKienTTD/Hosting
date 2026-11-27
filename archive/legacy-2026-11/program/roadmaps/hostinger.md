# Hostinger Agent — Roadmap Infrastructure & Reliability

**Owner:** Hostinger Agent | **ROADMAP_STATUS:** `PLANNED_NOT_ACKED`. Historical PR39 snapshot: A0 previously resumed general tasks, now **superseded by KNG-01-only hold**; old PR24/29 frozen branches remain frozen pending exact reownership. **No Hostinger dispatch while KNG gate is open.** **READ_SET:** inventory/current-vps-state, existing Hostinger survey, backup/security findings, OPS/SEC evidence; **WRITE_SET:** own roadmap, dated sanitized infra reports and approved sandbox/infra scoped changes in separate branch. **STOP:** no backup/rollback, private key exposure, public access drift, production disruption, missing explicit task-level risk gate.

| ID | Required skills | Task / measurable deliverable | Depends | Status | Evidence / UTC |
|---|---|---|---|---|---|
| INF-01 | K-VPS,K-SEC,K-OBS | Fresh read-only Hostinger/cloud/VPS/WordPress health and failure inventory; distinguish runtime U4S vs KVM2 | existing VPS evidence | PLANNED | — |
| INF-02 | K-VPS,K-BACKUP,K-TEST,K-SEC | Verify backup integrity and safe restore in non-production, publish recovery time/result | INF-01 | PLANNED | — |
| INF-03 | K-VPS,K-OBS,K-SEC | Add approved safe monitoring/alert plan and smoke test, no public secrets or ports | INF-01 | PLANNED | — |
| INF-04 | K-VPS,K-N8N,K-API,K-TEST | Sandbox-only orchestration infrastructure and durable health/recovery path with rollback | INF-02,INF-03 | PLANNED | — |
| SEC-H | K-SEC,K-VPS,K-BACKUP | Risk-ranked hardening work package for root SSH, exposed ports, firewall, version pins, backups | INF-01 | PLANNED | — |
| WP-H | K-VPS,K-WP,K-OBS | Diagnose read-only source of product HTTP500/errors if reproduced; no destructive changes | UC01-01 observations | PLANNED | — |

**KNG-01 priority override (2026-11-23):** All unrelated roadmap feature items are ON_HOLD_DEPENDENCY_KNG01 until Work independent QA, coordinator integration, A0-authorized merge and a new dispatch/actual ACK. Historical PLANNED items remain proposals, not current task orders.

**Completion:** evidence-backed backup/restore and monitoring operations, remaining unsafe changes precisely gated; no automatic paid Gate B, no production deployment from general owner authorization alone.
## Cách tự cập nhật

Chủ roadmap cập nhật **chính file này** sau khi hoàn thành một đầu việc: chuyển `PLANNED → IN_PROGRESS → DONE_WITH_EVIDENCE`, ghi `EVIDENCE` (commit/PR/log/source link), `UTC`, kết quả PASS/FAIL và lỗi thực tế. Không yêu cầu A0/Điều phối nghiệm thu từng dòng. Chỉ thông báo một lần khi roadmap đạt `READY_FOR_ROADMAP_ACCEPTANCE` hoặc `ROADMAP_PARTIAL_BLOCKED`. Nếu còn công việc an toàn độc lập, phải làm tiếp. Không đẩy secret hoặc PII lên Git.

Nếu cuối roadmap có hạng mục thực sự không thể thực hiện sau các nỗ lực hợp lệ, phải sử dụng nguyên văn: **Đã làm hết công việc có thể làm, một số công việc chưa thể làm do "Bảo mật"/ "Giới hạn kỹ thuật".** Kèm từng lỗi, bước đã thử, bằng chứng và hướng khắc phục. Không suy diễn môi trường hay quyền chỉ từ tên tài khoản.

Quy trình và các giới hạn: [Operating Protocol](../OPERATING_PROTOCOL.md). Quy tắc hiện hành trên main luôn có hiệu lực cho tới khi candidate được tích hợp hợp lệ.