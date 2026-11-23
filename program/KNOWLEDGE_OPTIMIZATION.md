# KNG-01 — canonical Git context and measured maintenance (CANDIDATE)

**Only active priority: KNG-01.** This file documents A1 author candidate, not independent Work QA or an effective main change. Source pins and authority are in [current.json](current.json); full mandatory rules remain read from effective main (see [entry](README.md)). Do not treat proposed state as live.

## Source ownership, not duplicate status text

| Fact | Canonical owner/effective source | Candidate behavior |
|---|---|---|
| Mandatory safety/security | `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md` on main | Read fully; never replace with summary |
| Business goal | `PROJECT.md` on main | Link durable goal; separate current priority |
| Current factual evidence | dated reports and immutable PR/commit hashes | Link; do not relabel historical snapshot LIVE |
| Current priority and approved dispatch | A0 + coordinator decisions on PR39 | Route through `program/current.json` after approved integration |
| Candidate task owner/dependency | WBS and agent-owned roadmap | Status changes only by assigned writer and actual ACK |
| Effective catalog | `CATALOG.yaml` on main, PR31 pending | No dual-write without coordinator exclusive lease |

[Canonical inventory](kng/inventory.json) lists old Git blob IDs and KEEP/MERGE/ARCHIVE/DELETE with recoverability. [Migration registry](kng/migration.json) provides concrete point-of-use edits for README/PROJECT/STATE/AGENTS/CATALOG/workflow, held **PREVIEW_ONLY** until PR31 conflict resolution and authorized shared writer. No irreversible deletion now. Git history and evidence remain intact.

## Actual A1 measurement method

1. Freeze main/PR31/PR39 SHA, compare exact UTF-8 byte lengths of files on a fixed reading path, with no invented tokenizer output. Full five required main documents are an equal mandatory constant in before and after.
2. Three tasks: business routine content audit; Git validator/code edit; security-sensitive VPS request. The before candidate navigation reads the whole initial PR39 program set; after reads this entry/current routing/A1 roadmap and only relevant WBS/skill or task evidence. Record all file paths and sizes rather than headline % alone.
3. Independently graded comprehension/routing belongs to **Work**. A1 drafts scenarios/rubric only. Any false permission, wrong current owner, missing STOP/security full read, stale task or evidence loss is critical FAIL even if size falls.
4. Write amplification: count *canonical manual file edits* for role change, task status, evidence acceptance and rule supersession. Candidate targets one record owner per fact and generated/linked summaries; legacy multi-file simultaneous edits held for coordinator migration.

**Current implementation scope:** point-of-use KNG candidate links/registries/validator/tests are real branch changes; production `main` README/PROJECT/STATE/AGENTS/CATALOG/workflow changes are **preview only**. No claim that Git read-cost is fully optimized while main remains unchanged. Work to run blind baseline vs candidate independently after A1 commits the source.
