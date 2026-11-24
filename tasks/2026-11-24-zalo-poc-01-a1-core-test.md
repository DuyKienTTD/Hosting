# ZALO-POC-01 — A1 Core Test

**TASK_ID:** `ZALO-POC-01-A1-CORE`  
**FROM:** Chat Điều phối, under explicit A0 FAST-TRACK authority  
**TO:** A1, primary owner for deterministic build/core and persistence checks  
**WHY:** A1 has historical Python/Git/source-engineering and test evidence, but must re-verify own session's Node/pnpm/test runner; no inferred shell authority.  
**MODE:** OFFLINE_SYNTHETIC_READ_AND_TEST; no implementation/feature development.  
**FIRST_ACTION:** ACK this exact task; read mandatory rules; inspect pinned candidate `package.json`, `src/shared/test-env-setup.ts`, `evals/fake-zalo-api.ts`, `src/zalo/incoming-message-router.ts`, `src/conversation/database.ts`, `src/conversation/khu-trung-tin-den.ts` and relevant `*.test.ts` before executing ANY command.

**A0 authorization:** ZALO-POC-01 FAST-TRACK dated 2026-11-24; this authorizes ONLY isolated offline/mock feasibility research and testing, 0 USD paid APIs, no product implementation. This priority exception does not lift existing holds on Hostinger/Hermes/Codex, production, Git main or the DGN package.

**MANDATORY BOOTSTRAP:** Read the complete current `DuyKienTTD/Hosting@main` files: `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, your own role profile if it exists, and this exact work order. Record the actual latest main SHA and blob SHAs; `main@d549564de52429e777c68daf9df7a93df5f22f27` is the S0 observed baseline, not standing authority. Read the candidate source `https://github.com/vuhai2002/zalo-agent/tree/2dc09de31cd99306bc1ab18e57aa0aa872618561` pinned to the FULL SHA 2dc09de31cd99306bc1ab18e57aa0aa872618561 and do not silently advance it. Repository is read-only; DO NOT push to `vuhai2002/zalo-agent`.

**S0 verified by Coordinator:** GitHub candidate main HEAD was 2dc09de31cd99306bc1ab18e57aa0aa872618561. Package scripts from `package.json`: `test = node --import tsx --test...`, `typecheck = tsc --noEmit && tsc --noEmit -p web`, `build = tsc -p tsconfig.build.json`, `eval = tsx evals/run-eval.ts`. Node >=22.13 and pnpm 11.28.7 are declared, not verified installed for your session. `evals/fake-zalo-api.ts` exists, but `evals/README.md` explicitly says `pnpm eval` uses REAL LLM/network/paid tokens despite fake Zalo; it is PROHIBITED for this task. Personal account uses unofficial `zca-js` v2.3.0. MIT repository license is declared; it does not imply official Zalo platform authorization.

**GLOBAL INVARIANTS:** exactly one synthetic account in every test; synthetic contacts/groups, no user data, no QR, cookie/session/token, no real Zalo/LLM/website API, no network services, no VPS/production, no installed extensions or downloads involving expense, no publishing, no dependency updates, no upstream commit, no merge. `sendMessage`, all tool sends and queued sends MUST terminate in audited fake/stub; count `real_outbound_calls=0`. Never start `src/index.ts`, the dashboard/login, `scripts/login-account.ts`, `zalo-login`, `pnpm eval`, Docker/Compose or any system that could open a listener to a real external service. Existing unit suites may ONLY run after examining their setup/import paths and confirming an isolated temporary DATA_DIR, synthetic configuration, fake channels and a no-network guard. If runtime dependencies are unavailable, do static source/test analysis and report BLOCKED_RUNTIME, not invented PASS.

**EVIDENCE:** record exact command/test identifier, tool versions, environment, exit code, stdout/stderr excerpt with secrets scrubbed, fixture hash or description, expected/observed outcome, negative/fault case and immutable source SHA. Classify VERIFIED_MOCK vs SOURCE_REVIEW vs BLOCKED/UNKNOWN. `pnpm test` / `pnpm build` success alone is not end-to-end proof or authorization.

**DELIVERY:** write a clean report to your one permitted `reports/` path on your own branch of `DuyKienTTD/Hosting`, push, remote readback, link commit and report. If branch or execution tools are missing, provide results inline with `NOT_PUSHED`, list exact blocker and the smallest safe fallback. Reply to Coordinator in recipient session with `TASK_ACKNOWLEDGED` for this exact work order; a GitHub file alone is PREPARED, not SENT/ACK. No Agent edits another Agent's report or the Coordinator synthesis.

**Stop triggers:** any real credential request, login/QR, network outbound, unexpected non-test import that initializes a live client, more than one active account, real personal/company data, paid provider call, unauthorized file write, or test harness that cannot prove offline isolation. STOP only unsafe actions and finish permitted static evidence.

## Test slice (A1 owns, no overlap with A2 or Work)
1. Preflight `node --version`, `pnpm --version`, dependency availability, no environment secrets, no real-account config; classify verified vs unavailable. Never run install scripts/downloads without separate approval. `pnpm --offline` only if package cache and install behavior verified harmless; otherwise STOP.
2. Inspect isolated test loader's module import order so SQLite cannot open a real DB. If safe, run existing targeted **offline unit tests** and typecheck/build using locally installed deps; report complete commands and exit codes. Do not run all evals. For `pnpm test`, independently screen every selected test path for real providers/listeners before running.
3. Synthetic **one-account** personal/group message routing: sender/thread identity, self-message rejection, allowlist, group mention/passive mode, exact target routing. These are CORE semantics; Work separately checks safety/failure enforcement.
4. SQLite: message persistence, exact-duplicate vs distinct messages, account/thread/sender identity, restart/rehydrate with temp DB and WAL, transaction/rollback, corrupted or missing DB behavior, offline-replay cursor/dedup where existing fixtures allow.
5. Contacts synchronization: distinguish `recordContactActivity`/contact store, friend events and UI list from actual remote contacts import/synchronization. Mark gaps NOT_IMPLEMENTED or UNVERIFIED rather than inferring functionality from naming.

**Relevant source/test shortlist:** `src/zalo/incoming-message-router.ts`, `src/zalo/message-turn-processor.ts`, `src/conversation/{database,history-store,contact-store,khu-trung-tin-den,offline-replay-cursor-store}.ts`, `src/zalo/offline-replay/*.test.ts`, `src/middleware/*.test.ts`, `src/config/account-store.test.ts`, `src/zalo/zalo-message-parser.test.ts`. Adapt exact file list to pinned Git tree; existing tests preferred; **no product feature code**.

## Work isolation
- **READ_SET:** pinned candidate + effective Hosting rules, this work order.
- **WRITE_SET:** ONLY `reports/2026-11-24-zalo-poc-01-a1-core.md` on A1-owned Hosting branch; optional scrubbed test output under `reports/evidence/zalo-poc-01/a1/` only if approved/non-secret.
- **DO_NOT_TOUCH:** candidate upstream repository, runtime/deployment/config, other Agents' reports, `main`, production, Catalog/rules/roadmaps.
- **COST CEILING:** 0 USD, no paid calls, no online install.

## Acceptance / evidence
Matrix by case ID `A1-01...`: test name, source path, command, fixtures, expected/observed, pass/fail/blocked, log/exit code. Explicitly distinguish BUILD/TYPECHECK_PASS from runtime behavior; document contact-sync gaps and all disabled channels. Verify `real_outbound_calls=0` and `synthetic_accounts=1`. Report restart/recovery without claiming true network reconnect. Final A1 verdict `PASS/PARTIAL_BLOCKED/FAIL` for **A1 test slice only**; never declare total Zalo platform GO. Deliver report and immutable commit, then Coordinator consumes in S2/S3.

**NEXT_OWNER:** Chat Điều phối for integrated verdict; Work independent QA compares evidence only after both reports exist.
