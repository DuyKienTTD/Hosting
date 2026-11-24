---
id: zalo-poc-01-a2-memory-kb-report
type: report
status: author-source-review-partial-blocked-runtime
updated_at: 2026-11-24
sensitivity: public-redacted
---
# ZALO-POC-01 — A2 Memory, Group Privacy and Knowledge Base / S1

**TASK_ACKNOWLEDGED:** `ZALO-POC-01-A2-MEMORY` in actual A2 session, 2026-11-24 (Asia/Ho_Chi_Minh). **OWNER:** A2. **MODE:** `OFFLINE_FIXTURE_TEST_OR_STATIC_VERIFIED_ANALYSIS`. **VERDICT:** `ROADMAP_PARTIAL_BLOCKED / SOURCE_REVIEW_WITH_PRIVACY_FINDING`. **NEXT_OWNER:** Coordinator, then independent Work S2/S3. This is not independent security QA and not runtime/production acceptance.

## Authority and provenance

- Hosting main actual GitHub branch readback: `d549564de52429e777c68daf9df7a93df5f22f27`; `AGENTS.md` blob `af42293a8ae7d3e864cd9f89442bc6861e85c080`; `rules/AGENT_WORKFLOW.md` `9dd6a1601e9b2a1b472f4a1ae89e9626ada05797`; `rules/REPOSITORY_SECURITY.md` `c24d608036b11dcd3fafcaefbefa23fdb591990e`; `STATE.md` `d74e6f3e7cc8bad0192f4a025e25d70aaa83d708`; `CATALOG.yaml` `26e125296fd0c39d0e82d6c5438dcc1ca2d8947f`.
- [A2 work order](https://github.com/DuyKienTTD/Hosting/blob/coordinator/zalo-poc-01-fast-track-2026-11-24/tasks/2026-11-24-zalo-poc-01-a2-memory-kb.md) blob `a8daf0c77dc3b4e0271cde6886cf160b1f7e7604`; coordinator PR51 HEAD `6cf2d87ca639217bdc169a222c23ff8c543e4032`.
- Candidate source repository **read only**: [vuhai2002/zalo-agent commit 2dc09de](https://github.com/vuhai2002/zalo-agent/tree/2dc09de31cd99306bc1ab18e57aa0aa872618561). No upstream edits. Source snippets, not real user data.
- A2 role profile `agents/a2.md` was `NOT_FOUND` on main in previous same-day A2 bootstrap; no new role-profile file created.
- Local environment: command `node --version` exit 0 output `v22.16.0`; `pnpm --version` exit 127 output `pnpm: command not found`; `git --version` exit 0 `2.47.3`. Runtime declared Node >=22.13 thus available; package manager/dependencies not established. **No upstream test suite executed**, no pnpm install, no network test, no application startup, no paid inference.

## Case register: expected versus observed

| ID | Synthetic fixture / operation / expected | Observed immutable source evidence | Result |
|---|---|---|---|
| A2-01 | One mock account `acc-synthetic`; customer A DM-only fact should appear for A's DM and never for group X | `memory-store.ts` `directStmt` and `groupStmt`: group user facts require `learned_in_group=1`; `memory-store.test.ts` has explicit DM→group negative assertion. No runtime executed by A2 | `SOURCE_REVIEW`, plausible guard, `RUNTIME_NOT_RUN` |
| A2-02 | Same A, group X fact must **not** appear in group Y | **FINDING P1:** `groupStmt` predicate `(subject_id = threadId OR (subject_id = senderId AND learned_in_group=1))` does not require `learned_in_thread_id = current threadId`. A group-X learned user fact is therefore eligible when A speaks in Y; `memory-store.test.ts` covers group-1 only, not X→Y. | `SOURCE_REVIEW_FAIL` privacy boundary gap |
| A2-03 | In group X, customer B's message should not inject A's subject facts | `getMemoriesForContext` uses `senderId` in group predicate; existing `memory-store.test.ts` checks sender swap. This alone does not prevent X→Y fact bleed when sender remains A | `SOURCE_REVIEW`, runtime not run |
| A2-04 | Group user cannot edit/delete DM fact or leak it through error list | `memory-edit-store.ts` has filtered query `learned_in_group=1`; `save-memory-tool.ts` sets `chiFactHocTrongNhom=message.isGroup && about==='sender'`; `memory-edit-store.test.ts` has negative tests for change/delete and error list. **Same cross-group provenance gap remains:** query does not constrain `learned_in_thread_id` to group X and `PhamViSuaFact` has no thread ID | `SOURCE_REVIEW_PARTIAL_FAIL` group-to-group edits possible if same sender |
| A2-05 | A→B and account isolation, exact duplicate, correction, restart persistence | `memory-store.ts` INSERT has `account_id,subject_id,content,learned_in_thread_id,learned_in_group`; selects filter account+subject; duplicate equality trims; edit matches visible content but update/delete by id; SQLite file WAL per `database.ts`. Existing tests check account/user and correction; A2 has **not** verified actual restart or conflicting fact resolved semantically. `createdAt` exists, but correction has no explicit revised-at/version/source-quality field | `SOURCE_REVIEW`; restart and temporal consistency `UNKNOWN` |
| A2-06 | Unbound agent must get no KB result, bound agent only assigned source | `kb-search.ts` returns [] if `nguonCuaAgent` empty; `kb-agent-binding.ts` queries by agent; `kb-fts-query.ts` filters `source_id IN` inside SQL; existing tests cover positive and negative | `SOURCE_REVIEW`; guard is structurally present, runtime not run |
| A2-07 | Synthetic rail color/size/price/returns docs; FTS ranking, duplicates, delete/reimport/restart | `kb-schema.ts` defines FTS5, chunks, bindings; `kb-fts-query.ts` runs parameterized bm25; `kb-search.ts` RRF then normalized-content dedup with 3x overfetch. `kb-source-store.ts` deletes FTS/chunks/bindings/source transactionally. `kb-search-quality.test.ts` has duplicate and ranking fixtures; `kb-ingest-worker.test.ts` has recovery/fault cases. A2 did not import fixture or run tests. The 3x-overfetch has acknowledged extreme-duplicate recall risk | `SOURCE_REVIEW`; ranking, delete/restart not measured |
| A2-08 | Every retrieval includes evidence source ID/name/title; user-facing answer must cite exact source | `kb-search.ts` returns `sourceId,tenNguon,tieuDe,noiDung,diem`. `kb-search-tool.ts` formats `[Nguồn: name - title]` for **model tool output**, but formatting alone does not enforce or prove citations in actual final user-facing messages. | `INTERNAL_PROVENANCE_PRESENT`; `USER_FACING_CITATION_NOT_VERIFIED` |
| A2-09 | Unknown price/spec/policy must be UNKNOWN and clarification, never fabricated | Search returns empty on no sources/no hits, but no executed deterministic response-policy fixture or LLM output available in this review. No guarantee that model avoids hallucination just from retrieval; no paid/real LLM evaluations allowed | `MODEL_QUALITY_NOT_VERIFIED` |
| A2-10 | Missing/invalid group scope and cross-type namespace collision must fail closed | Memory API uses caller-provided `threadId,senderId,isGroup`; `getMemoriesForContext` has no visible input validation here. Group fact's subjectId equals raw threadId, no namespace enforcement in these functions. Runtime caller validation may exist elsewhere but was not proved in A2 review | `UNKNOWN` — require owner trace and negative fixture |

### P1 source finding — group X → group Y exposure and edit capability

**Minimal synthetic state:** account `acc-synthetic`; sender `customer-a`; group X `group-x`, group Y `group-y`. Store `{accountId:'acc-synthetic',subjectId:'customer-a',content:'customer-a prefers invented-color-X',learnedInThreadId:'group-x',learnedInGroup:true}`. Then request `getMemoriesForContext({accountId:'acc-synthetic',threadId:'group-y',senderId:'customer-a',isGroup:true})`. The current SQL selects the row because the sender matches and `learned_in_group=1`; group-X origin is not checked. A group Y invocation of `suaFactTheoDoanChu` / `xoaFactTheoDoanChu` can also target the same group-X fact via `chiFactHocTrongNhom=true` because the edit SQL checks group-learned flag only, not the current group ID. This is a **source-logic demonstration**, not a claimed runtime execution.

**Impact:** fact provided in a limited group context may enter an unrelated group prompt and/or be modified from another group. Group-sender identity remains the same, so current sender-swap tests cannot find it. The work order explicitly demands group-specific scope.

**Minimum recommended remedy for future A0-authorized source work:** agree whether group-learned person facts are globally public or group-specific; for group-specific contract, constrain retrieval and edit to `learned_in_thread_id = current threadId` and extend edit scope to carry the group ID. Add synthetic tests X→Y, A→B, group-scope mismatch, and no-match error-list non-disclosure; ensure same account only. Do not alter upstream source within this A2 work order.

**Further source caution:** `memory-store.ts` dedupe matches text across account+subject but ignores origin scope. If exactly same fact was first stored in DM, later saving identical content as learned-in-group returns `trung` without making it group-visible, and vice versa. This can lead to provenance/visibility surprises and deserves an isolated negative fixture. This is a design observation rather than proven exploit.

## Commands, execution boundary, and STOP

- Executed local read-only toolchain check only: `node --version` (0), `pnpm --version` (127), `git --version` (0).
- Reviewed pinned GitHub source through authenticated read-only fetch. Existing `src/shared/test-env-setup.ts` creates temp DATA_DIR, fake LLM key and temp data; **a test-specific fake env does not itself prove an outbound network block**. Until dependency/import audit plus an enforced no-network guard and fake channel are verified, do not run whole suite.
- **Commands NOT run:** `pnpm test`, `pnpm build`, `pnpm typecheck`, `pnpm eval`, `src/index.ts`, login, dashboard, Zalo API, model inference, account creation, outbound messages, package installation.
- **Actual outbound invocation through this PoC:** 0; **real_outbound_calls=0** for actions performed by A2 (GitHub read/write reporting is separate authorized evidence traffic, not Zalo/LLM outbound). **Synthetic account design count = 1**; no instantiated Zalo runtime account. **PAID_API_USD=0** for A2 task; no invoices checked.
- No caller with real Zalo session, QR, cookie, secrets, or group data accessed.

## Findings, gates and handoff

1. **P1 / NO-GO for group privacy claim until fixed and negatively tested:** current source allows same sender's group-X-learned fact to be selected in group Y. Source-author should add isolation at both retrieval and edit scopes under separate authorized task.
2. **P2 / Source-citation gate:** source metadata and model-tool labeling exist, but output-side citation enforcement and correctness remain unverified.
3. **P2 / Identity & provenance:** input validation, cross-group edit/error-list boundary, duplicate-across-scope, restart persistence, temporal correction and missing-source scenarios need controlled, network-denied fixture execution.
4. **P2 / Model quality:** cannot mark price/spec/policy truthfulness PASS without deterministic tested response contract or separately authorized semantic assessment; `MODEL_QUALITY_NOT_VERIFIED`.
5. **BLOCKED_RUNTIME:** pnpm and project dependencies not established in A2 runtime; test import path can touch env/worker/SDK and no proven no-network intercept exists. Do not install dependencies/download upstream for this task. Coordinator may route a separate safe offline runner after preflight, without duplicating A2's source findings.

**Acceptance result:** substantial `SOURCE_REVIEW` completed with one actionable P1 privacy finding. **No `VERIFIED_MOCK` assertions made by A2**, no runtime unit case executed, no evidence of end-to-end safety. A1's core and Work's independent safety investigations proceed separately. **NEXT_OWNER:** Coordinator to integrate source finding into S1/S2 and require exact negative test before S3 decision; Work independent privacy reviewer. A0's PASS/CONDITIONAL/NO-GO gate remains open.

**Final:** `ROADMAP_PARTIAL_BLOCKED`. Đã làm hết công việc có thể làm, một số công việc chưa thể làm do "Bảo mật"/ "Giới hạn kỹ thuật". The blocker is missing verified isolated runtime dependencies/no-network harness; safe fallback performed: pinned immutable source audit with explicit non-execution labels.
