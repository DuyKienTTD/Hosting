---
id: zalo-poc-01-work-safety
type: task
status: prepared-owner-forward
dispatch_eligible: false
owner: Work
updated_at: 2026-11-24
sensitivity: public
---

**HANDOFF_STATE:** `PREPARED_FOR_OWNER_FORWARD` — original task committed but no verified session delivery or ACK. Do not infer `SENT` from the GitHub PR.

# ZALO-POC-01 — Work Independent Safety QA

**TASK_ID:** `ZALO-POC-01-WORK-SAFETY`  
**FROM:** Chat Điều phối under explicit A0 FAST-TRACK  
**TO:** ChatGPT Work, independent safety reviewer and owner of negative/fault tests  
**WHY:** Work has independently source-verified offline Linux/SQLite/DOM testing in DGN feasibility; current runner/access must be rechecked, no assumption of autonomous background operation.  
**MODE:** OFFLINE_SYNTHETIC_NEGATIVE_QA; no live account or real send.  
**FIRST_ACTION:** ACK exact task; read mandatory Hosting rules; inspect pinned `evals/fake-zalo-api.ts`, `src/middleware/allowlist-filter.ts`, `src/zalo/deliver-chat-reply.ts`, `src/zalo/send-reply-in-parts.ts`, `src/zalo/message-turn-processor.ts`, `src/zalo/offline-replay/`, `src/scheduler/proactive-send-guard.ts`, `src/config/secret-cipher-core.ts` and existing related negative tests BEFORE invoking any runner.

**A0 authorization:** ZALO-POC-01 FAST-TRACK dated 2026-11-24; this authorizes ONLY isolated offline/mock feasibility research and testing, 0 USD paid APIs, no product implementation. This priority exception does not lift existing holds on Hostinger/Hermes/Codex, production, Git main or the DGN package.

**MANDATORY BOOTSTRAP:** Read the complete current `DuyKienTTD/Hosting@main` files: `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, your own role profile if it exists, and this exact work order. Record the actual latest main SHA and blob SHAs; `main@d549564de52429e777c68daf9df7a93df5f22f27` is the S0 observed baseline, not standing authority. Read the candidate source `https://github.com/vuhai2002/zalo-agent/tree/2dc09de31cd99306bc1ab18e57aa0aa872618561` pinned to the FULL SHA 2dc09de31cd99306bc1ab18e57aa0aa872618561 and do not silently advance it. Repository is read-only; DO NOT push to `vuhai2002/zalo-agent`.

**S0 verified by Coordinator:** GitHub candidate main HEAD was 2dc09de31cd99306bc1ab18e57aa0aa872618561. Package scripts from `package.json`: `test = node --import tsx --test...`, `typecheck = tsc --noEmit && tsc --noEmit -p web`, `build = tsc -p tsconfig.build.json`, `eval = tsx evals/run-eval.ts`. Node >=22.13 and pnpm 11.28.7 are declared, not verified installed for your session. `evals/fake-zalo-api.ts` exists, but `evals/README.md` explicitly says `pnpm eval` uses REAL LLM/network/paid tokens despite fake Zalo; it is PROHIBITED for this task. Personal account uses unofficial `zca-js` v2.3.0. MIT repository license is declared; it does not imply official Zalo platform authorization.

**GLOBAL INVARIANTS:** exactly one synthetic account in every test; synthetic contacts/groups, no user data, no QR, cookie/session/token, no real Zalo/LLM/website API, no network services, no VPS/production, no installed extensions or downloads involving expense, no publishing, no dependency updates, no upstream commit, no merge. `sendMessage`, all tool sends and queued sends MUST terminate in audited fake/stub; count `real_outbound_calls=0`. Never start `src/index.ts`, the dashboard/login, `scripts/login-account.ts`, `zalo-login`, `pnpm eval`, Docker/Compose or any system that could open a listener to a real external service. Existing unit suites may ONLY run after examining their setup/import paths and confirming an isolated temporary DATA_DIR, synthetic configuration, fake channels and a no-network guard. If runtime dependencies are unavailable, do static source/test analysis and report BLOCKED_RUNTIME, not invented PASS.

**EVIDENCE:** record exact command/test identifier, tool versions, environment, exit code, stdout/stderr excerpt with secrets scrubbed, fixture hash or description, expected/observed outcome, negative/fault case and immutable source SHA. Classify VERIFIED_MOCK vs SOURCE_REVIEW vs BLOCKED/UNKNOWN. `pnpm test` / `pnpm build` success alone is not end-to-end proof or authorization.

**DELIVERY:** write a clean report to your one permitted `reports/` path on your own branch of `DuyKienTTD/Hosting`, push, remote readback, link commit and report. If branch or execution tools are missing, provide results inline with `NOT_PUSHED`, list exact blocker and the smallest safe fallback. Reply to Coordinator in recipient session with `TASK_ACKNOWLEDGED` for this exact work order; a GitHub file alone is PREPARED, not SENT/ACK. No Agent edits another Agent's report or the Coordinator synthesis.

**Stop triggers:** any real credential request, login/QR, network outbound, unexpected non-test import that initializes a live client, more than one active account, real personal/company data, paid provider call, unauthorized file write, or test harness that cannot prove offline isolation. STOP only unsafe actions and finish permitted static evidence.

## Independent safety slice (Work-only, may start alongside A1/A2)
1. **Wrong recipient / duplicates / blocked sending:** adversarial synthetic IDs (same display name, distinct IDs; same ID in different account/thread; group vs DM); wrong target/type; retransmit, queue/reconnect and late reply; disabling thread or account **after** batching but before send; opt-out and missing/withdrawn consent. Record if guard exists at send time vs only at intake. A source-only absence is a GAP, not runtime FAIL unless reproduced.
2. **Group mention and halt:** no @mention vs mention, passive listen, group disabled, owner/employee takeover and kill switch. Distinguish current per-thread `bot_enabled` from **human handoff workflow**; test whether takeover/STOP persists through queued sends/schedules/restart. If unsupported, explicitly mark missing.
3. **Privacy/session:** DM-only memory/historical content must not appear in group; log and dashboard exposure; credential encryption at rest and session handling on synthetic fixtures; error paths, malformed payload, unexpected exception and partial retry. No real secret/cookie inspection, no QR or external network.
4. **Defense in depth:** ensure all outgoing tools (`sendMessage`, attachment, reaction, scheduled send, proactive send, delayed reply) reach FakeZaloApi/stub; record all attempted fake calls. Verify cases where `allowlist`/thread disabling before queue differs from state at actual send.
5. **Review A1/A2 independently after their evidence appears:** compare claims to source pins and test artifacts, sample negative cases; no edits to their artifacts, no self-certification of a test Work authored. If they are not yet ready, deliver independent findings and mark cross-review `AWAITING_EVIDENCE` rather than blocking unrelated testing.

**Known review points (not assumptions of failure):** `shouldRespond` checks group and allowlist at intake; check later send-time revocation. `memory-store.ts` has asymmetric DM/group queries; verify through tests. Candidate supports multiple accounts in production, but this PoC MUST use exactly one synthetic account; tests involving second real or mock active account are out of scope.

## Work isolation
- **READ_SET:** pinned candidate source, A1/A2 finished reports when available, main Hosting rules, this task.
- **WRITE_SET:** ONLY `reports/2026-11-24-zalo-poc-01-work-safety.md` on Work-owned Hosting branch; sanitized evidence optionally `reports/evidence/zalo-poc-01/work/`.
- **DO_NOT_TOUCH:** A1/A2 reports, all product code, real credentials/data/accounts, upstream, other Agent roadmaps, main/rules/CATALOG, production or infra.
- **COST:** 0 USD, no paid inference and no downloads/installs with expense.

## Acceptance / evidence
Case IDs `W-01...` with positive/negative boundary, reproducible fixture, expected and observed behavior, trace of fake send attempts (zero real), evidence path and FAIL/UNKNOWN. Record `hard_stop_breaches` separately from missing features; a STOP/opt-out or wrong-recipient failure is NO-GO candidate unless safely resolved in separately approved scope. Report `real_outbound_calls=0`, `synthetic_accounts=1`, no private-to-group leak. Human takeover must be evidenced end-to-end to PASS; a thread kill-switch alone is not takeover. Audit dependency/protocol risks (MIT != Zalo platform authorization; `zca-js` unofficial). Provide independent QA verdict for Work slice and sampled A1/A2 findings, without approving overall platform.

**NEXT_OWNER:** Chat Điều phối for S2/S3 synthesis and recommendation to A0 only.
