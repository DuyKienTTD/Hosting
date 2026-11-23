# Hosting — Operating Model v3 (CANDIDATE)

Status: `DRAFT_FOR_INDEPENDENT_REVIEW` | Owner: A0-delegated coordination | Date: 2026-11-23
Branch: `a0/operating-model-roadmaps-20261123`
Baseline main: `e385c1bea2070973e3007e5717f7e980348d6ab3`.
**This candidate does not supersede effective main rules until reviewed and integrated.** No production/paid/merge rights are granted here.

## Read this in order
1. **Agent:** read this entry (short), [your own roadmap](roadmaps/), [operating rules](OPERATING_PROTOCOL.md), and the applicable effective security rules in `rules/REPOSITORY_SECURITY.md`. Read exact pinned task/evidence only when work demands it. Current main rules still apply until changed through approved governance.
2. **Product context:** [Product Charter + UI](PRODUCT_AND_UI.md).
3. **Task-to-skill map:** [Work Breakdown](WORK_BREAKDOWN.md); [Skills Registry](SKILL_REGISTRY.md).
4. **Authority:** [Single-source status policy and measurement](KNOWLEDGE_OPTIMIZATION.md).

## Responsibility split
- A0: portfolio-level objective, risk/exception and roadmap-level acceptance; no routine item-by-item approval.
- Chat Điều phối: priorities, dependencies, integration and roadmap-level acceptance, not approval for every subtask.
- A1 / A2 / Work / Hostinger: distinct outcome-focused roadmap owners; may execute all safe independent items and self-record evidence.
- Hermes: `HOLD_NO_NEW_TASKS`; Codex: `NOT_AUTHORIZED` unless A0 changes their restrictions.
- Hostinger is resumed for new hosting/infra work by A0 2026-11-23, replacing the earlier general PAUSED order; previously frozen PR24/29 work is **not** automatically reopened. Explicit reownership required.

## Truthfulness and status
- `PLANNED → IN_PROGRESS → DONE_WITH_EVIDENCE` for each owned item.
- Other item statuses: `BLOCKED_SECURITY`, `BLOCKED_TECHNICAL`, `NOT_APPLICABLE`. All with `observed`, `attempted`, `evidence`, `next_safe_action`.
- Roadmap terminal states: `READY_FOR_ROADMAP_ACCEPTANCE` or `ROADMAP_PARTIAL_BLOCKED`. Only coordinator/A0 can record their **roadmap acceptance verdict**.
- Nothing is `LIVE_VERIFIED` merely because offline tests pass. A GitHub comment/PR is not delivery to another chat.

## Completion behavior
The executing agent works uninterrupted through its own roadmap, updates each item in its own roadmap, and requests **one** roadmap-level acceptance on completion. Do **not** stop for individual status ACK. If a security or technical boundary blocks an item, work through all other independent safe items first, then report exactly:
> Đã làm hết công việc có thể làm, một số công việc chưa thể làm do "Bảo mật"/ "Giới hạn kỹ thuật".
Include a per-item table with evidence and precise reasons. Do not use this sentence when unattempted independent safe work remains.

## Protected invariants
No secrets/private customer data in public repo; read-full-before-write; branch scoped; diff/readback; independent QA for material changes (may be batched at roadmap boundary); no unverified access/capability assumptions; no unsafe effects, paid calls, budget increases or publication without applicable approvals and actual technical gates. Workload-level autonomy is not a bypass of security.
