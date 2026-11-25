---
id: zalo-zpc-04-security
type: knowledge
status: draft
owner: A1
task_id: ZPC-04-SECURITY
updated_at: 2026-11-26
sensitivity: public
---
# ZPC-04-SECURITY — independent security acceptance design

Design only; no application code or runtime tests. Authority: HOSTING-ZALO-RESUME-01, owner instruction 2026-11-26, offline only. Baseline [product plan](https://github.com/DuyKienTTD/Hosting/blob/d441205/program/zalo-mvp01/PRODUCT_COMPLETION_PLAN.md#6-work-breakdown-and-agent-assignment), [MVP source/tests](https://github.com/DuyKienTTD/Hosting/tree/52b7c5ccac572b170925d28c44c5613c1e73a849/apps/ttd-zalo-assistant). Plan ZPC-04 names the deliverable and ZPC-06/08/09/11 consume it; ZPC-07 consumes the knowledge controls. These are bidirectional logical cross-references; the pinned plan is immutable and absent from main at base 6dea328, so no reverse hyperlink was inserted into that plan. Coordinator may add the concrete reverse link when integrating the plan, without changing its authority. Work packages: [ZPC-06/07/08/09/11](https://github.com/DuyKienTTD/Hosting/blob/d441205/program/zalo-mvp01/PRODUCT_COMPLETION_PLAN.md#6-work-breakdown-and-agent-assignment). ZPC-11 independent Windows acceptance remains separate.

- [Threat model](THREAT_MODEL.md)
- [Negative/fault/race matrix](TEST_MATRIX.md): 40 cases, 10 with existing direct baseline test (including one source smoke subcase), 30 without full matching test. Source presence is not a new PASS.
- Use stable test name `ZPC04-Nxx <slug>` in Vitest or existing node:test; do not migrate framework merely for this design. Work maps to its actual seams, A1/Codex review exact candidate. No runtime authorization is conferred.

No production, real customer data, real Zalo, real provider calls, paid API, permission change, merge or repetition of accepted POCs. Rollback for this document-only delta: reviewer may revert its commit on branch; do not delete history. NEXT_OWNER Coordinator/Work; independent review A0.