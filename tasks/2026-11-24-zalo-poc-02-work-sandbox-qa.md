---
id: zalo-poc-02-work-sandbox-qa-2026-11-24
type: task
status: prepared-owner-forward
dispatch_eligible: false
owner: Work
updated_at: 2026-11-24
sensitivity: public
---

# ZALO-POC-02 / Work — Reproducible offline sandbox + independent integrated QA

**TASK_ID:** `ZALO-POC-02-WORK-SANDBOX-QA`. **PRIMARY_OWNER:** Work. **MODE:** isolated Node/pnpm sandbox, native tests and independent validation of A1/A2 patches; no business code authoring. **WHY:** POC01 Work had Node v24.22.3, isolated `unshare -Urn` and 5 executed fixture checks, unlike A1/A2 whose pnpm/dependencies were missing. Verify current session afresh.

**FIRST_ACTION:** ACK; read rules; verify pinned candidate `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `package.json`, `src/shared/test-env-setup.ts`, `evals/README.md` and all test entrypoint/import side effects. Check current local Node, pnpm, package cache, disk/shell/network-namespace capability and whether dependency archive can be obtained **under approved preparatory-only network rules**. Before any dependency/project code runs, establish egress denial with independent negative network probe. If isolation cannot be demonstrated, `BLOCKED_SANDBOX` and continue source/fixture-only analysis.

## Binding authorization and rules
A0-delegated approval is GitHub issue comment **7123763842** on PR #51, dated 2026-11-24: https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7123763842 . Approval covers *only* offline isolated source copies/branches, dependency preparation, patch development, test execution, and evidence for ZALO-POC-02. It is not a Zalo live, product, production, paid API, upstream write, Hosting main merge or official Zalo connection approval.

FIRST read **in full** the current Hosting `main` versions of `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, your role profile, and this order. Record actual HEAD and rule blobs. S0 observed Hosting main `d549564de52429e777c68daf9df7a93df5f22f27` (historical pin, verify current). Candidate code MUST be sourced only from immutable `vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561`, with `pnpm-lock.yaml` verified before use. No other candidate/upstream version.

**Common safety:** exactly ONE synthetic account, fake contacts/chats/groups, no Zalo QR/login/cookie/session, no real user data, no outgoing Zalo, LLM or provider calls, no `pnpm eval`/`pnpm start`/`pnpm dev`/`zalo-login`, no VPS, production, ads, public listener, paid service, main merge or CodeX/Hermes/Hostinger activation. Downloads, when necessary, restricted to approved source/dependencies with checksum/lockfile validation; examine lifecycle scripts first; ensure network egress is disabled **before** executing dependency/project code. Any action not proved to be in a blocked-network sandbox must STOP. Avoid real `.env` and secrets. Expense ceiling: **0 USD**.

**Shared evidence contract:** each case ID records baseline SHA + exact patch SHA, current Node/pnpm versions, commands, exit codes, fixture hash/description, reproducible expected/observed outcome, sanitized logs and explicit test status (`VERIFIED_OFFLINE`, `VERIFIED_MOCK`, `SOURCE_REVIEW`, `BLOCKED`), zero real outbound and one synthetic account. A successful test that reproduces a privacy violation is **defect evidence**, not product PASS. Positive/negative/fault and restart/race cases matter. Stop after hard blocker with evidence; continue independent safe tasks.

**Session handoff:** owner-forward the exact GitHub task URL to the indicated Agent chat; the Agent must return `TASK_ACKNOWLEDGED` with source SHA and FIRST_ACTION. A committed work order = `PREPARED_FOR_OWNER_FORWARD`, not SENT or ACK. End with report, branch/commit, remote readback and next owner. Do not edit another Agent's file or upstream repo.

## Workstream E0: sandbox / native test baseline
- Immutable checkout at exact candidate commit; verify checkout HEAD/lockfile hashes. Node>=22.13; package manager pin `pnpm@11.28.7`. Check pnpm v11 build-script allowlist and dependency installer lifecycle (esbuild and other dependencies). Never execute untrusted lifecycle hooks with network access. Download only reviewed pinned sources and deps. Use lockfile-frozen installation with controlled scripts; do not run `pnpm eval` or any command importing the real LLM/customer/account runtime.
- Verify exactly one synthetic account, tempfile DB and DATA_DIR, no secrets, fake/stub every Zalo/tool/scheduler send, no listeners, blocked network. Isolate process/runtime env. Record actual Node/pnpm/tsx/TS versions, SHA, checksum and exit code. Run `pnpm typecheck`, `pnpm build` and selected native unit tests only when import graph and test config are safe. If full native suite can be safely run, record suite count by class; otherwise report precisely what was excluded.
- Report baseline failures separate from A1/A2 patch regressions. Preserve prior Work POC01 fixture evidence but do not overstate it.

## Workstream Q0: independent QA — after patches are available
- Fetch **A1 and A2 immutable patches** from their own Hosting branches; validate exact baseline sha, patch hash and disjoint modified paths. Apply both to a **fresh local checkout** under `--network none` or equivalent; no upstream write, no merge. Re-run typecheck/build/targeted tests for the **exact combined tree**, record tree/patch digest. If patches conflict, stop and report file-level conflict; never silently auto-resolve authored product changes.
- Verify A2's group X/Y read/edit/delete and retention authorization by temp SQLite and restart, including denied contact/history/cache/replay/summaries. Verify A1's actual last-moment STOP/opt-out/human takeover/wrong-recipient/idempotent queue and scheduler, including multiple send paths, multipart and reaction under fake API. Include negative/race/restart/failure cases. **0 real outbound calls**, **one synthetic account** in all cases, and logs without PII.
- Do not edit A1/A2 product patch files or their reports. Independent QA verdict must be per-case, against observed behavior; author self-tests alone do not qualify. The same Work Agent who authored sandbox scripts may self-report sandbox setup, but must distinguish this from independent review of A1/A2 authored changes.
- If A1/A2 evidence not yet available, deliver runnable E0 first and mark Q0 `AWAITING_PATCHES`. Continue review when artifacts appear, no arbitrary three-day delay.

**Hosting Git WRITE_SET:** `reports/2026-11-24-zalo-poc-02-work-sandbox-qa.md` and `experiments/zalo-poc-02/work/**` on Work branch only. **READ_SET:** rules/decision, pinned source, A1/A2 patch+reports after submission. **DO_NOT_TOUCH:** A1/A2 owned paths, Hosting main, upstream, production, real account, paid provider.

**Acceptance:** demonstrate reproducible import/setup, safe native build/typecheck/tests; negative outbound no-egress guard; integrated **same-code** tree with exact patch SHAs, native SQLite persistence/restart and all critical negative/fault tests. Distinguish `PASS` versus `BLOCKED`; any P1 privacy or post-STOP safety failure = `FAIL/NO_GO_CANDIDATE`. No live Zalo or commercially permitted API claim.

**EVIDENCE:** sanitized report + portable harness scripts/checklists under Work WRITE_SET, environment/fixture hashes, command logs and remote readback. **NEXT_OWNER:** Coordinator for integrated offline gate, then delegated A0 Independent Advisor for separate review/owner decision.
