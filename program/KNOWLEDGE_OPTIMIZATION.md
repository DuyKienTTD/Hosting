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

[Canonical inventory](kng/inventory.json) lists old Git blob IDs and KEEP/MERGE/ARCHIVE/DELETE with recoverability. [Migration registry](kng/migration.json) provides concrete point-of-use edits for README/PROJECT/STATE/AGENTS/CATALOG/workflow, **applied on the director-authorized isolated D2 integration branch**, sourced from PR31 for five shared paths and original main for README; no main/PR31 branch writes. No irreversible deletion now. Git history and evidence remain intact.

## Actual A1 measurement method

1. Work Q0 fixed baseline at [#7097774156](https://github.com/DuyKienTTD/Hosting/pull/39#issuecomment-7097774156): use the exact nine common full-file inputs and frozen task-specific suffixes. Integrated D2 reads the nine corresponding complete files plus the new 2,751-byte typed current route, then **the identical suffix files**. Count full UTF-8 blob bytes; no invented tokenizer output.
2. Exact Q0 tasks: R WS-04 SEO backlog 11/149,148 B → **12/124,752 B**; G WS-01 docs-only proposal 12/151,686 B → **13/127,290 B**; S WS-02 safe n8n readiness triage 15/197,424 B → **16/173,028 B**. All three save 24,396 UTF-8 B with one extra full read; source list/blob SHAs in [machine evidence](../reports/evidence/2026-11-23-a1-kng01-d2-q0-metrics.json). No Work blind-comprehension result claimed.
### Q0 R WS-04 evaluation-only role binding

```yaml
scenario_id: Q0_R_WS04
simulated_brief_preparer: Work
actual_ws04_dispatch: false
status: EVALUATION_ONLY_KNG_ONLY_HOLD
program_owner: Chat Điều phối
comprehension_reviewer: Work
role_precedence: explicit scenario assignment over generic capability
```

The Work brief-preparer role above exists **only inside the frozen Q0 R simulation**. Actual WS-04 remains **ON_HOLD_DEPENDENCY_KNG01**: no live assignment, WordPress/Ads permission, new standing SEO role, or real Agent ACK follows. Work as `comprehension_reviewer` is the independent scoring function, separate from the simulated brief-preparer role. Do not derive this scenario's role from the generic [Agent capability directory](../agents/README.md). Evidence: [Work frozen Q0 definition](https://github.com/DuyKienTTD/Hosting/pull/39#issuecomment-7097774156) and [A2 role-routing finding](https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7102698883). The sealed A2 17/18 result remains unchanged.

3. Independently graded comprehension/routing belongs to **Work**. A1 drafts scenarios/rubric only. Any false permission, wrong current owner, missing STOP/security full read, stale task or evidence loss is critical FAIL even if size falls.
4. Exact Q0 four hypothetical changes: technical routing 3 files/4 fields→**1/2**; WS-02 real-ACK 4/5→**1/2**; WS-02 paper report acceptance 4/5→**2/4**; new secret handling rule 4/4→**2/2**. These are **proposed manual authoritative edit targets**, not timed changes; [derive.py](kng/derive.py) renders STATE/CATALOG mirrors from typed source, but PR31 nonshared legacy paths remain and Work must test interpretation. See evidence for exact per-field map.

**Current implementation scope:** point-of-use KNG candidate links/registries/validator/tests are real branch changes; six common README/PROJECT/STATE/AGENTS/CATALOG/workflow files are **changed on isolated D2 branch** using full PR31 applicable source; main still unchanged. No claim that Git read-cost is fully optimized while main remains unchanged. Work to run blind baseline vs candidate independently after A1 commits the source.
