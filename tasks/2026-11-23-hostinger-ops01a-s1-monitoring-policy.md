---
id: ttd-hostinger-ops01a-s1-offline-monitoring-2026-11-23
type: offline-monitoring-contract
status: completed-synthetic-pass
owner: hostinger-agent
next_owner: chatgpt
---
# OPS-01A/S1 Offline Monitoring Contract

Phạm vi: hợp đồng tín hiệu, policy cảnh báo và evaluator synthetic-only. Không có live monitoring, scheduler, webhook, email, paging, probe thật, Docker daemon, credential, log payload, paid API hoặc thay đổi production.

Inputs: INF-01B KVM2 preflight, SEC-02 F01-F07, Work WS-02 runbook tại PR #8 head `18e41d1`, và rules/AGENTS trên `main` `e385c1b`.

Acceptance: policy declarative; evaluator deterministic; UTC/sample/source/resource identity; `UNKNOWN` cho dữ liệu thiếu; duplicate/out-of-order/identity/source controls; open/recover/overdue/risk/blocked semantics; seven executed synthetic cases; no external transport; report/evidence remote readback.

Write set: policy schema, evaluator, fixtures/tests, README, report và redacted evidence trên branch riêng. Không sửa Work PR #8, Hostinger PR #17, rules, main, CATALOG, STATE hoặc CHANGELOG.
