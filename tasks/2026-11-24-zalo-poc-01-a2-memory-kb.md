# ZALO-POC-01 — A2 Memory & Knowledge Test

**TASK_ID:** `ZALO-POC-01-A2-MEMORY`  
**FROM:** Chat Điều phối under A0 ZALO-POC-01 FAST-TRACK  
**TO:** A2, primary owner of synthetic memory/knowledge behavior audit  
**WHY:** A2 Product Charter/UI and business knowledge design have author-evidenced deliverables; Node/test-runner capability in A2's own session remains UNKNOWN until A2 checks it.  
**MODE:** OFFLINE_FIXTURE_TEST_OR_STATIC_VERIFIED_ANALYSIS; no live model inference.  
**FIRST_ACTION:** ACK exact scope; read mandatory rules; inspect `src/conversation/memory-store.ts`, `src/conversation/memory-edit-store.ts`, `src/agent/tools/save-memory-tool.ts`, `src/knowledge/kb-search.ts`, `src/knowledge/kb-agent-binding.ts`, `src/knowledge/kb-schema.ts`, and existing `*.test.ts` at pinned SHA.

**A0 authorization:** ZALO-POC-01 FAST-TRACK dated 2026-11-24; this authorizes ONLY isolated offline/mock feasibility research and testing, 0 USD paid APIs, no product implementation. This priority exception does not lift existing holds on Hostinger/Hermes/Codex, production, Git main or the DGN package.

**MANDATORY BOOTSTRAP:** Read the complete current `DuyKienTTD/Hosting@main` files: `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, your own role profile if it exists, and this exact work order. Record the actual latest main SHA and blob SHAs; `main@d549564de52429e777c68daf9df7a93df5f22f27` is the S0 observed baseline, not standing authority. Read the candidate source `https://github.com/vuhai2002/zalo-agent/tree/2dc09de31cd99306bc1ab18e57aa0aa872618561` pinned to the FULL SHA 2dc09de31cd99306bc1ab18e57aa0aa872618561 and do not silently advance it. Repository is read-only; DO NOT push to `vuhai2002/zalo-agent`.

**S0 verified by Coordinator:** GitHub candidate main HEAD was 2dc09de31cd99306bc1ab18e57aa0aa872618561. Package scripts from `package.json`: `test = node --import tsx --test...`, `typecheck = tsc --noEmit && tsc --noEmit -p web`, `build = tsc -p tsconfig.build.json`, `eval = tsx evals/run-eval.ts`. Node >=22.13 and pnpm 11.28.7 are declared, not verified installed for your session. `evals/fake-zalo-api.ts` exists, but `evals/README.md` explicitly says `pnpm eval` uses REAL LLM/network/paid tokens despite fake Zalo; it is PROHIBITED for this task. Personal account uses unofficial `zca-js` v2.3.0. MIT repository license is declared; it does not imply official Zalo platform authorization.

**GLOBAL INVARIANTS:** exactly one synthetic account in every test; synthetic contacts/groups, no user data, no QR, cookie/session/token, no real Zalo/LLM/website API, no network services, no VPS/production, no installed extensions or downloads involving expense, no publishing, no dependency updates, no upstream commit, no merge. `sendMessage`, all tool sends and queued sends MUST terminate in audited fake/stub; count `real_outbound_calls=0`. Never start `src/index.ts`, the dashboard/login, `scripts/login-account.ts`, `zalo-login`, `pnpm eval`, Docker/Compose or any system that could open a listener to a real external service. Existing unit suites may ONLY run after examining their setup/import paths and confirming an isolated temporary DATA_DIR, synthetic configuration, fake channels and a no-network guard. If runtime dependencies are unavailable, do static source/test analysis and report BLOCKED_RUNTIME, not invented PASS.

**EVIDENCE:** record exact command/test identifier, tool versions, environment, exit code, stdout/stderr excerpt with secrets scrubbed, fixture hash or description, expected/observed outcome, negative/fault case and immutable source SHA. Classify VERIFIED_MOCK vs SOURCE_REVIEW vs BLOCKED/UNKNOWN. `pnpm test` / `pnpm build` success alone is not end-to-end proof or authorization.

**DELIVERY:** write a clean report to your one permitted `reports/` path on your own branch of `DuyKienTTD/Hosting`, push, remote readback, link commit and report. If branch or execution tools are missing, provide results inline with `NOT_PUSHED`, list exact blocker and the smallest safe fallback. Reply to Coordinator in recipient session with `TASK_ACKNOWLEDGED` for this exact work order; a GitHub file alone is PREPARED, not SENT/ACK. No Agent edits another Agent's report or the Coordinator synthesis.

**Stop triggers:** any real credential request, login/QR, network outbound, unexpected non-test import that initializes a live client, more than one active account, real personal/company data, paid provider call, unauthorized file write, or test harness that cannot prove offline isolation. STOP only unsafe actions and finish permitted static evidence.

## Test slice (A2-only)
1. **Persistent memory provenance:** with invented customers A and B on ONE mock account, save/retrieve/edit facts; check `accountId`, `subjectId`, `learnedInThreadId`, `learnedInGroup`, source and temporal consistency, correction/conflicting fact behavior, persistence after restart.
2. **Private versus group:** test A's DM-only secret never enters group X prompt, even when group B asks about A; group-learned fact may be visible to that group's permitted context only. Test different group IDs, sender swaps and missing/invalid scope; no cross-identity retrieval.
3. **Synthetic business KB:** import only invented simple docs (e.g. rail color/size/price/returns), compare authorized agent binding vs unbound source (fail-closed), search ranking/FTS5, duplicate chunks, delete/reimport/restart, document provenance `sourceId/tenNguon/tieuDe`, import errors and missing source.
4. **Advice/no invented facts:** test a deterministic mock responder or source/contract checks. Unknown price/spec/policy must be labelled UNKNOWN and trigger clarification, not made-up figures. If true LLM semantic reliability cannot be tested under zero paid/network, report `MODEL_QUALITY_NOT_VERIFIED` and recommend future separately authorized test; do NOT run `pnpm eval`, send LLM calls or invent PASS.
5. Explain whether project supports source references in a **user-facing answer** versus only internal retrieval metadata; evidence must show actual linkage, not inferred from a field in KB.

**Relevant tests:** `src/conversation/memory-store.test.ts`, `memory-edit-store.test.ts`, `src/knowledge/kb-search.test.ts`, `kb-source-queries.test.ts`, `kb-agent-binding.test.ts`, `kb-ingest-worker.test.ts`, `kb-fts-query.test.ts`, `src/agent/tools/kb-search-tool.test.ts`. Check preflight and imports before running.

## Work isolation
- **READ_SET:** pinned candidate, Hosting main rules and this task.
- **WRITE_SET:** ONLY `reports/2026-11-24-zalo-poc-01-a2-memory-kb.md` on A2-owned Hosting branch; sanitized evidence optionally under `reports/evidence/zalo-poc-01/a2/`.
- **DO_NOT_TOUCH:** A1/Work reports, upstream repository, live documents/Google Drive, website/Ads, main/rules/CATALOG/roadmaps, real Zalo, production.
- **COST:** 0 USD; no model, install, provider or network call.

## Acceptance / evidence
Case IDs `A2-01...`: fixtures, expected vs observed, API/SQL/query, log/test artifact, safety assertion, pass/fail/blocked. Explicitly report identity isolation and DM→group no-leak negative tests, provenance of every KB result, no fictitious policy/price in demonstrated mock answer, and semantic-model performance UNKNOWN unless genuinely proven offline. Check `real_outbound_calls=0`, `synthetic_accounts=1`. Deliver report/commit/readback. If A2 lacks test runner, perform source-grounded gap analysis without claiming runtime PASS; flag `BLOCKED_RUNTIME` for Coordinator to route a **separate read-only runner** without duplicate reporting.

**NEXT_OWNER:** Chat Điều phối; Work later reviews independent evidence on S2/S3.
