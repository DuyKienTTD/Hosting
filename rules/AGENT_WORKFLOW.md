---
id: multi-agent-handoff
type: rule
status: draft
updated_at: 2026-11-24
sensitivity: public
---

# Quy tắc vận hành Agent

Bản tinh gọn theo chỉ thị A0 ngày 24/11/2026; chỉ là candidate cho đến khi được tích hợp hợp lệ. Không tự cấp quyền. [Lịch sử và bằng chứng](../references/history/README.md).

## Subject index
- [1. authority](authority.md)
- [2. coordination](coordination.md)
- [3. dispatch](dispatch.md)
- [4. execution](execution.md)
- [5. evidence](evidence.md)
- [6. integrity](integrity.md)
- [7. handoff](handoff.md)
- [8. lifecycle](lifecycle.md)

Read modules in full; requirements are cumulative, not alternatives. Always read Core, role, task and module 1.

| Operation | Additional mandatory modules |
|---|---|
| Coordination/dispatch | 2–5, 7 |
| Review/appraisal | 2, 4, 5, 7; add 6 for Git changes/diff, 3 for dispatch/ACK |
| Any Git write/shared write | 2, 4–6; add 3, 7 for task/handoff |
| Paid/production/VPS/destructive/release/merge | 2–7, exact authority, preflight and rollback |
| Governance data lifecycle | 6, 8 and [protocol](DATA_LIFECYCLE_CONTEXT.md) |

Git operations also require [Security](REPOSITORY_SECURITY.md) and [CONTRIBUTING](../CONTRIBUTING.md); routing/STOP/release requires [STATE](../STATE.md) and applicable live authority/KNG gates per Core. If uncertain, read all eight and all triggered safety sources. [MKOE](HOSTING-MKOE-01.md). Historical section numbers map to modules above. No change to reserved authority.

[Gate B historical navigation](GATE-B-INDEX.md).
