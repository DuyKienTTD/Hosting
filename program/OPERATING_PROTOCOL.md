# KNG-01 scoped operating protocol (release-source snapshot; verified activation required)

**Before merge, NOT_EFFECTIVE:** KNG-01 is the only proposed source-development lane under A0's pinned [routing snapshot](current.json), not an automatic assignment. Work PR42 source QA is complete; no new Work task or D2 ACK is pending. All other roadmap G0, G2, G3, G4, UC01, UI, media, infrastructure, and Ads work is **ON_HOLD_DEPENDENCY_KNG01**. Safety/incident response may continue under separate existing authorization. Never infer that a GitHub comment wakes an agent or marks an ACK.

A1 owns implementation in its own branch. Work owns independent baseline/final QA, not A1 source. Chat Điều phối is Program Director, resolves PR31 integration and grants an exclusive write-set for shared files; A0 approves final merge. A2/Hostinger optional only if distinct KNG evidence is requested. Hermes HOLD_NO_NEW_TASKS, Codex NOT_AUTHORIZED.

## Effective authority and control

**Read full mandatory main rules:** [AGENTS](../AGENTS.md), [workflow](../rules/AGENT_WORKFLOW.md), [security](../rules/REPOSITORY_SECURITY.md), [STATE](../STATE.md). CATALOG is a machine-validated registry; read only relevant entries. PR31 history and PR43 Draft do not override them. Work PR42 source QA is [completed](https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7103815886), with no new ACK implied. No paid, production, VPS, live connector, merge or destructive history rewrite. **Historical D2 exception:** six common files were changed on an isolated branch under [dated director grant](https://github.com/DuyKienTTD/Hosting/pull/40#issuecomment-7098528192); that grant is NOT a new permission to write main/production.

## Data lifecycle

- Canonical fact status/owner should be written **once** by authorized writer, with source SHA and evidence, then linked by summaries.
- Before ARCHIVE/DELETE review all incoming references, legal/security retention, historic evidence, rollback, and accepted canonical ID. No deletion unless all independent gates clear.
- On concurrent source drift, abort only conflicting write and continue separate safe tests. Do not force-push.
- A1 validator and measurements are author evidence; independent Work tests are a separate gate.
- Do not mark KNG effective from this source snapshot. Before merge: NOT_EFFECTIVE. After A0 exact candidate/tree approval and a merge commit: use the read-only [release-state assessment](kng/release_state.py) with independently verified immutable A0 decision, remote main tree and parent SHAs. Only a fully authenticated result can be EFFECTIVE_IF_VERIFIED; stale main, wrong tree, absent approval, failed readback or mismatched parents remain NOT_EFFECTIVE. The simulation tests are not merge or A0 permission.

For reproducible candidate scope, see [migration plan](kng/migration.json), [validator](kng/validate.py), [tests](kng/test_validate.py) and [candidate entry](README.md).

## Pre-dispatch Git task candidate filter (D5, candidate-only)

Use the **single fail-closed read-only interface** `python3 program/kng/select_task.py --root .` ([source](kng/select_task.py), [negative/positive tests](kng/test_select_task.py)) before interpreting any `tasks/` file, CATALOG `type: task`, or old proposal as a possible task candidate. The selector accepts only explicit YAML boolean `dispatch_eligible: true`, `type: task`, a supported review-ready non-archived status and an existing safe path. Archive, `dispatch_eligible: false`, absent/unknown eligibility are never candidates; malformed/ambiguous input **STOPs with exit 2**, not partial results. An empty candidate list is valid. **Never bypass with a raw task glob or status text.** PyYAML must be installed; a missing dependency is a STOP, not an empty false PASS.

**This is not a dispatcher.** A candidate is never executable authorization. Only the Director's **explicit work order**, authorized scope/owner, then the receiving Agent's real-chat **ACK** can activate a task; this process remains external, **NOT_DEPLOYED** as an automated runner. No script should create ACK, select a task owner, send a request or perform work based on this output. A0 retains merge/production/paid rights.
