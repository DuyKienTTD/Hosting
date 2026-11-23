# Git knowledge normalization and measurable context efficiency

Status: design/pilot required; NOT ALREADY OPTIMIZED. 2026-11-23.

## Initial document findings (read on PR31 head a770de80...)
- README currently ~3.2k chars; PROJECT ~5.5k; ROADMAP ~4.2k; AGENTS ~10.8k; STATE is a historical-heavy living document; AGENT_WORKFLOW is long with multiple overrides.
- Several current-vs-historical routing statements coexist across PROJECT/AGENTS/agent directory/master allocation and PR comments; seven status-related point-of-use fixes on PR31 D2–D7 demonstrate update amplification.
- This *proves a need for source-of-truth and loading-path improvement*, but does not prove user token savings, comprehension speed, hallucination/error rate, or that all current docs are redundant. Do not certify 'fully optimized' without A/B evidence.

## Canonical ownership of facts (proposed)
| Data | Canonical source | Secondary artifacts must do |
|---|---|---|
| Product goal and scope | `PROJECT.md` plus approved charter | Link, do not copy old priorities |
| Current user-facing feature scope | `program/PRODUCT_AND_UI.md` after adoption | Reference |
| Security/mandatory rules | effective `rules/*` on main | Short pointer, do not paraphrase to weaken |
| Per-agent work items and item status | `program/roadmaps/<agent>.md` after adoption | Link with exact item ID |
| Work dependencies and skill IDs | `program/WORK_BREAKDOWN.md` | Refer stable IDs |
| Agent skill/capability provenance | `program/SKILL_REGISTRY.md` | Link, do not duplicate install claims |
| Tested facts | immutable dated reports + source ref/sha | State summary links to evidence |
| Current integration state | minimized `STATE.md` snapshot derived from roadmaps + live checks | Never infer live from Git alone |
| Execution event history | per-run append-only evidence, git comments/commit history | No repeated status narrative |
| Runtime status | actual service/connector/ledger, with fresh timestamp | Git snapshots explicitly staleable |

## Context tiers
**T0 ~ short navigation:** program README + roadmap frontmatter + required effective security rules.
**T1:** just current item, immediate dependencies, source pins, required skills and approved acceptance.
**T2:** linked report/source diff only where material.
**T3:** legacy and chronological evidence on demand; no mass loading by default.
**Mandatory security text remains fully authoritative.** Context packs are navigational, not a loophole to ignore rules.

## Acceptance test for optimization
Measure a BEFORE baseline and AFTER experiment using at least three representative tasks: (1) normal content audit, (2) Git/docs code change, (3) security-sensitive VPS/production plan. Each agent must identify correct objective, owner, current action, prior evidence, STOP, allowed paths and restrictions using only documented entry path plus required rules.
Measure tokenized input size with same tokenizer/method or byte count as explicitly marked proxy; read steps/time; factual recall/decision correctness; false DONE, unsafe permission inference, duplicated execution and link-resolution failures. Avoid guessed '30–50%' savings. PASS only when measurable context reduction has **zero critical safety or state errors**, provenance preserved and independent test passes. Otherwise rollback pilot and report failure.

## Migration phases (no delete)
1. Inventory documents/paths/hashes, canonical ownership and duplicate claims. Include PR31 staged changes; preclude write collisions.
2. Build a compact entry point + one pilot task pack with exact SHA/links; keep original files untouched.
3. Test comprehension, task execution and QA against legacy; inspect diff, broken links, leakage, metadata/lost-evidence risk.
4. Only then propose minimal edits to README/PROJECT/STATE/AGENTS/CATALOG/effective workflow, by sole writer after PR31 QA and merge sequencing are resolved.
5. Retain history in dated reports and Git; no rewrite or loss of archive; confirm Git readback and targeted invariants.

## Open risks
Current source at PR31 HEAD still contains older PAUSED routing, while latest A0 directive resumes Hostinger. New roadmap describes prospective change; its *source* doesn't replace effective rules. The status migration must be atomic for point-of-use references to avoid stale text across seven files. 'Auto-update' means an agent actively writes to Git or through a verified service; a passive chat will not wake itself to change files.
