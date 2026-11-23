# Hướng dẫn Agent — KNG-01 current authority

**Effective after separate approved merge only.** The original full PR31 AGENTS guidance and history are retained verbatim by Git at [PR31 `a770de80`](https://github.com/DuyKienTTD/Hosting/blob/a770de80a2467ca1789c820b63416209cf53b7d1/AGENTS.md), blob `ecdb1fbaefd06448e3f7734c5eb2deea70a471d4`. Dated OPS/SEC/Cost-first decisions there are historical evidence, **not** current permission for new dispatch.

## Before every task (mandatory)

Read **in full** `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, agent profile and exact task; pin source/rules SHA. Preserve actual role ACK and evidence. [PROJECT](PROJECT.md) is long-term goal, [README](README.md) quick navigation, [current routing](program/current.json) is candidate source once approved.

## Current priority / ownership

**KNG-01 ONLY** until independent Work QA, coordinator conflict resolution and **A0-authorized merge**. Chat Điều phối = project/program director; A1 = sole KNG implementation writer; Work = independent reviewer (current D2 re-QA ACK pending); A2/Hostinger/Hermes = hold new unrelated tasks; Codex = NOT_AUTHORIZED. Hostinger prior resumption, old Codex routing, A1 OPS ownership and historical work statuses are **past-snapshot facts**, not current task permissions. [Pinned A0/director roadmap](https://github.com/DuyKienTTD/Hosting/pull/39#issuecomment-7097692066), [D2 write grant](https://github.com/DuyKienTTD/Hosting/pull/40#issuecomment-7098528192).

## Execution, evidence and STOP

Each task needs `TASK_ID, OWNER, MODE, FIRST_ACTION, BASE_SHA, READ_SET, WRITE_SET, DO_NOT_TOUCH, TEST_DELTA, INVARIANTS, STOP, ACCEPTANCE, EVIDENCE, NEXT_OWNER`. Branch-specific exclusive writer, no overlap or surprise source edits; read full changed source, compare exact diff, run targeted positive/negative tests, push and verify GitHub remote SHA. Do not self-certify author code as independent QA. A GitHub PR/comment is PREPARED, not external Agent SENT/ACK unless separately evidenced. Never claim real runtime state from offline test/dated report.

Security rules and risk gates are binding: no secrets/private data in public Git; no production/VPS, paid API, Ads budget, deployment, account permission or publication without task-specific approval, preflight and rollback. STOP conflicting operations, continue unrelated safe work. No automatic merge, force-push, destructive history rewrite or Codex dispatch. KNG roadmap-level QA does not waive security/release gates. The operative [full workflow](rules/AGENT_WORKFLOW.md) and [repository security](rules/REPOSITORY_SECURITY.md) remain required.

## Data ownership and update amplification

Single candidate routing register: [program/current.json](program/current.json). Task ACK/receipt is an immutable dated event; source task and CATALOG entries become indexed snapshots, not independent manually maintained current status after approved KNG integration. `STATE.md` displays the current program snapshot plus provenance, not a second authoritative history. CATALOG keeps stable IDs and paths. Rules are authoritative in `rules/`; quick-start only links to them without copying clause text. Preserve all evidence through immutable PR/source SHA and append-only dated reports.

Change effective rules only with coordinator exclusivity and A0's applicable approval. NEVER infer new permissions from status or a document index. For historical detailed workflow and prior required read/update rules see pinned PR31 source above; the current §13 in `rules/AGENT_WORKFLOW.md` clarifies approved KNG routing precedence.
