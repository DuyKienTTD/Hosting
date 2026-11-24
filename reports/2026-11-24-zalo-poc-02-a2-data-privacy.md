---
id: zalo-poc-02-a2-data-privacy
type: report
status: patch-ready-awaiting-work-verification
updated_at: 2026-11-24
sensitivity: public-redacted
---

# ZALO-POC-02 — A2 data privacy / retention remediation

**TASK_ACKNOWLEDGED — ZALO-POC-02-A2-DATA-PRIVACY** (actual A2 chat receipt, 2026-11-24 Asia/Ho_Chi_Minh). **Verdict:** `PATCH_READY_AWAITING_WORK_VERIFICATION` (NOT product PASS). **NEXT_OWNER:** Work for independent isolated SQLite/integration QA; Coordinator for S3.

## Pinned sources, authorization, environment

- Hosting remote main verified `d549564de52429e777c68daf9df7a93df5f22f27`. Rule blobs: AGENTS `af42293a8ae7d3e864cd9f89442bc6861e85c080`; AGENT_WORKFLOW `9dd6a1601e9b2a1b472f4a1ae89e9626ada05797`; REPOSITORY_SECURITY `c24d608036b11dcd3fafcaefbefa23fdb591990e`; STATE `d74e6f3e7cc8bad0192f4a025e25d70aaa83d708`; CATALOG `26e125296fd0c39d0e82d6c5438dcc1ca2d8947f`.
- Task blob `784c10460a951859c2bd6dbaa21ede11ca621478`. A0 delegated approval verified directly via GitHub issue-comment `7123763842` on PR51, 2026-11-24 06:16:27Z.
- Source `vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561`; checked GitHub file blobs: memory-store `5b0bfda92887cb549ac6d784fe7690d66c98ac8d`, memory-edit-store `7bdbd56c51bf8e868c539906218ce78db6c04de8`, allowlist-filter `1046738507933c2907535c8f1172b62b6e9f81bd`, incoming-message-router `02bd7dbebea7a66a0d4d1022fb28e76e16503655`, pnpm-lock `98e51d3b8c59e8af7c00ce89fe685eb01f1d8358`.
- Local `node --version`: v22.16.0 (exit 0); `pnpm --version`: command not found; `git --version`: 2.47.3. `git clone --filter=blob:none --no-checkout https://github.com/vuhai2002/zalo-agent.git` exit 128 `Could not resolve host: github.com`. Thus no isolated full checkout, no verified lockfile installation, no project runtime test; **no network-denied sandbox proof**. GitHub connector was used to read immutable pinned source and push documents only. No package/project code executed.
- WRITE_SET only `experiments/zalo-poc-02/a2/**` and this report on `a2/zalo-poc-02-data-privacy-2026-11-24`. Upstream unchanged. Single synthetic account `acc-synthetic` in proposed tests; real account count = 0, real Zalo/LLM outbound = 0, paid API USD = 0.

## Artifacts / proposed scope

1. `experiments/zalo-poc-02/a2/privacy.patch`: unified patch against exact pinned source; modified-path targets confined to A2 ownership: `memory-store.ts`, `memory-edit-store.ts`, `allowlist-filter.ts`, `incoming-message-router.ts`. **Patch is an integration candidate, not an applied/executed build.**
2. `experiments/zalo-poc-02/a2/privacy-sql.test.mjs`: dependency-free `node:sqlite` tests reading SQL predicates from a separately patched checkout. Requires `ZALO_PATCHED_SOURCE_ROOT`; must run in independently verified no-egress sandbox. Test fixture uses one synthetic account, person A, group X/Y, no real data.

## D1: Group-scoped source repair

- **Baseline defect (source repro):** `groupStmt` selected a group-learned sender fact without checking `learned_in_thread_id`; edit/delete `factNhinThayTrongNhomStmt` likewise checked group flag but not origin. Same text across group X/Y was deduped by `account_id,subject_id,content`, causing cross-origin suppression.
- **Candidate patch:** require `learned_in_group=1` and `learned_in_thread_id=currentGroupId` for group reads; scope group edit lookup to same origin group; require explicit `PhamViSuaFact.threadId` for group edit and return empty on missing scope; dedupe by account+subject+content+thread+group; reject missing identity/thread parameters on saves and reads.
- **INTEGRATION_BLOCKER D1:** existing `src/agent/tools/save-memory-tool.ts` caller constructs `PhamViSuaFact` without `threadId`. It is outside authorized candidate modified paths. Group edits therefore fail closed until owner-approved interface handoff adds `threadId: message.threadId` and validates thread type. Also the baseline old `memory-store.test.ts` expectation that group-learned facts appear in all DM contexts needs review against intended policy, and existing `memory-edit-store.test.ts` fixtures must be updated to pass group thread ID. Neither is silently counted PASS.
- **Legacy/ambiguous provenance:** group facts missing origin are denied; DM recall retains original account/subject behavior for equal sender/thread ID. A hard account-independent namespace/type guarantee is still unverified in upstream callers; source alone cannot establish secure caller-verified identities.

## D2: Response vs retention contract

- **Baseline defect:** `shouldRespond` used `recordOnly` for passive group listening and disabled-thread cases without a distinct verified retention consent; router invoked `recordContactActivity`, `recordThreadActivity`, `sendDeliveredReceipt`, and group-name API lookup **before** evaluating `shouldRespond`. An opted-out sender could still be collected even if later filtered.
- **Candidate patch:** optional explicit `PrivacyConsent {verified:true, respond:boolean, retain:boolean, passiveGroup:boolean}` parameter, default deny when absent; separate return flags; passive record requires both retention and group-specific passive consent; router calls filter before any contact/thread/history/receipt/network side effect. When both false returns immediately. A response-only `respond=true,retain=false` currently returns `bo` deliberately (safe STOP) instead of dispatching through unaudited persistence/replay/summary paths.
- **INTEGRATION_BLOCKER D2 (critical):** There is no proven, independently validated consent resolver with account+sender+thread+expiry and revocation. Router currently does **not pass** this new consent object, so the integrated candidate defaults to **deny all inbound**. This is intentional secure fallback, **not functional acceptance**. Need separate approved wiring, plus review of all cache, media, replay, summaries, queue and outgoing handlers; retention revocation must remove/stop already durable data and block replay, not simply prevent new rows. `history-store.ts` and `contact-store.ts` were read but do not themselves enforce consent at the public insert entrypoints; safe usage depends on gating all callers. Historical persisted data is not deleted by this patch. This is NOT yet retention compliance.
- **Dependency caveat:** newly introduced `KetQuaGhiNho` reason `pham_vi_khong_hop_le` may be treated by existing tool as generic duplicate: caller adjustment is beyond A2 modified-path grant. Mark as integration issue, not silent test PASS.

## Case register (all NOT RUN in real patched repository)

| Case | Expected fixture / oracle | State and evidence |
|---|---|---|
| A2-D1-01 | Group X person fact remains in X, not in Y; DM secret never group | `SOURCE_REVIEW`; `privacy-sql.test.mjs` test A2-01 prepared |
| A2-D1-02 | Group Y cannot see/edit/delete X fact or echo it as no-match suggestion | `SOURCE_REVIEW`; test A2-02 SQL selection prepared; **actual tool edit path not run** |
| A2-D1-03 | Identical fact in group X/Y does not collide in dedupe | `SOURCE_REVIEW`; test A2-03 prepared |
| A2-D1-04 | Missing IDs/group provenance, group/DM ID collision, restart and sender swapping default deny | `SOURCE_REVIEW_PARTIAL`; no integrated restart or malformed-type test run |
| A2-D2-01 | Absent/withdrawn consent rejects both respond and retention before contact/history | `SOURCE_REVIEW`; A2-04 static ordering and A2-05 independent policy fixture prepared, not actual router SQLite test |
| A2-D2-02 | Approved retain-only passive group message stores in actual SQLite; respond-only sends no persistent record | `BLOCKED_INTEGRATION`; consent resolver and downstream audit missing, respond-only deliberately stops |
| A2-D2-03 | No data in SQLite messages/contacts/cache/summary/replay/media after opt-out or restart | `BLOCKED_INTEGRATION`; A2-05 fixture is a policy-contract demonstration, **not** actual router assertion |
| A2-D2-04 | Fault/race/expiry and consent withdrawal flush cached queues/replay | `BLOCKED_INTEGRATION`; multiple paths outside A2 modified WRITE_SET |

### Testing and QA boundaries

- No `pnpm eval`, `pnpm test`, source startup, Zalo login, model inference, network egress, paid API, production, upstream write or merge occurred.
- To test safely: Work must obtain immutable source+lockfile, apply patch on isolated copy with `git apply --check && git apply`, verify actual diff and import graph; check offline egress controls, then set `ZALO_PATCHED_SOURCE_ROOT` and run `node --test experiments/zalo-poc-02/a2/privacy-sql.test.mjs`; follow with targeted real native tests and integration SQLite tests, negative, fault and restart, on A0-approved sandbox. Existing old tests may require legitimate interface adaptations; fail/STOP instead of rewriting source outside owner scopes.
- The A2 SQL fixture has no full router integration, no temp on-disk SQLite restart check. If Work observes PASS, only the SQL-contract checks passed; it is **not** proof of no unauthorized persistence.
- **Security gate:** until full consent resolution and downstream source integration, retain fail-closed behavior; never ship this patch as a product-ready fix or merge into live code.

## Result and next handoff

**A2 author source work:** candidate patch + offline test file prepared, with known dependency and integration limitations. **Verifier:** Work independently runs patch and executable negative tests, including DB readback and multi-path race/restart. **Coordinator:** reconcile cross-writer interfaces and future approved patch boundaries. **A0:** decides after S3, no automatic merge or live Zalo.

**FINAL VERDICT:** `PATCH_READY_AWAITING_WORK_VERIFICATION`. No `VERIFIED_OFFLINE` or `VERIFIED_MOCK` claim. **STOP:** no live or paid actions, no main merge.

## Corrective continuation — 2026-11-24 / Coordinator comment 7124437685

**FOLLOW_UP_ACKNOWLEDGED:** Same task `ZALO-POC-02-A2-DATA-PRIVACY`; no new work order or PR. Coordinator independently found invalid `git apply --check` in Work blocked-egress test, on original patch blob `4674c6e1fa4385ec97986113207e7c7b413c57e5` (memory-store:32, allowlist-filter:14, incoming-message-router:82). Original generator wrote additions before deletions and split adjacent edits into overlapping hunks; not a valid source-aligned unified diff.

**Corrective action:** Read original pinned source for all 4 A2 paths via GitHub file API; match each proposed change against exact source context; regenerate unified hunks using a line-by-line sequence alignment, ordering context/deletions/additions correctly; merge overlapping 3-line contexts; calculate consistent original/target ranges. Reconstruct the complete patched text from corrected diff against source contents and compare byte-for-byte with the intended candidate representation for every path. No intended D1/D2 source logic changed.

**New patch commit:** `ecb04dfe665f05c10f1e2825ab0c8d92f450f1f8`; **new patch blob:** `0a78460efa7110526a70983a6b47c2929ca8a3c0`.
**Pinned source blobs / regenerated hunk counts / source reconstruction:**
- `src/conversation/memory-store.ts`: `5b0bfda92887cb549ac6d784fe7690d66c98ac8d`; 4 hunks; in-memory patch reconstruction MATCH.
- `src/conversation/memory-edit-store.ts`: `7bdbd56c51bf8e868c539906218ce78db6c04de8`; 3 hunks; reconstruction MATCH.
- `src/middleware/allowlist-filter.ts`: `1046738507933c2907535c8f1172b62b6e9f81bd`; 4 hunks; reconstruction MATCH.
- `src/zalo/incoming-message-router.ts`: `02bd7dbebea7a66a0d4d1022fb28e76e16503655`; 2 hunks; reconstruction MATCH.

**Tool verification:** `git ls-remote https://github.com/vuhai2002/zalo-agent.git HEAD` exit 128 `Could not resolve host: github.com`; immutable checkout remains unavailable in local sandbox. **`git apply --check` NOT_RUN / UNVERIFIED_IN_A2_ENVIRONMENT**, not claimed PASS; exact check requires Work's isolated checkout at pinned SHA. Source roundtrip in GitHub tool orchestration is a **syntactic source-alignment check**, not executable git apply, typecheck, unit, integration, offline SQLite or security QA. Existing `privacy-sql.test.mjs` is unchanged and its five contract tests remain NOT_RUN.

**Expected baseline test deltas / integration risks remain:** Old memory test expecting group-learned facts from any group in A's DM remains design-policy dependent; group edit fixture without `threadId` now must fail closed and test must pass scoped thread ID for authorized edit; old allowlist filter tests expecting default automatic response/passive retention must now expect deny without verified consent. Missing validated consent source and revocation/expiry, `src/agent/tools/save-memory-tool.ts` threadId handoff (A1 write set), cache/media/replay/summary enforcement remain integration blockers, not solved by patch formatting. Work should now rerun clean `git apply --check`, then actual negative SQLite and integration tests in verified blocked-egress environment.

**Status after patch-regeneration:** `PATCH_READY_AWAITING_WORK_VERIFICATION` / `GIT_APPLY_CHECK_NOT_RUN_A2`; no production use. **NEXT_OWNER:** Work QA, Coordinator integration.

## P0 continuation — consent and TypeScript compile corrective handoff (2026-11-24)

**FOLLOW_UP_ACKNOWLEDGED:** `ZALO-POC-02-A2-DATA-PRIVACY`; Coordinator directive [PR56 comment #7125612392](https://github.com/DuyKienTTD/Hosting/pull/56#issuecomment-7125612392). Work observed `TS2769` at `memory-edit-store.ts:77:39` and nine affected legacy allowlist tests in an offline combined tree; this is Work's QA evidence, **not A2 runtime measurement**. Scope remains five A2-owned upstream paths (the previous four plus `allowlist-filter.test.ts`) packaged in the sole existing `experiments/zalo-poc-02/a2/privacy.patch`.

**Remediation in new patch:**
- `memory-edit-store.ts`: Validate `pham.threadId` in the group branch, save it in a narrowed `const threadId: string` through normal TypeScript control flow before passing to `factNhinThayTrongNhomStmt.all`. Missing/empty group thread returns `khong_khop` with an empty suggestion list; no cast-to-string, broad compiler settings, or scope relaxation. All group X/Y and group-origin SQL filters and dedupe protections preserved.
- `allowlist-filter.ts`: Establish optional `PrivacyConsent` contract with `verified:true, accountId,senderId,threadId,threadType,revision,expiresAt,revoked,humanTakeover,stopped,respond,retain,passiveGroup`. Reject absent consent, expired snapshots, revoked/STOP/human takeover, invalid revision or account/sender/thread/type mismatch before history decisions. Move allowlist check **before group passive-listen** so unlisted senders cannot be retained. This is a **snapshot consumer**, NOT a consent resolver or trusted policy storage. A caller-supplied object alone can be forged: only a separately authorized resolver may construct it.
- `allowlist-filter.test.ts`: Existing baseline behavior tests now supply a clearly named `syntheticConsent(account,msg)` fixture, exact scoped identity/type and explicit `respond/retain` flags; no blanket allowlist bypass. Preserve all historical negative tests. Add 8 new negatives/positives for absent consent, respond-only, retain-only, deny-both, expired/revoked/human takeover/STOP/invalid revision, cross-account/sender/thread/type, passive group consent, and allowlist blocks passive storage.
- `memory-store.ts` and `incoming-message-router.ts`: previous group isolation and fail-closed defaults retained in this P0 patch; no assertion that the router currently resolves consent.

**Evidence scope:** Regenerated unified diff from immutable original five GitHub file blobs; source-aligned in-memory application checked against exact intended candidate content and hunk line counts for each. `git apply --check`, native `tsc`, native tests, actual SQLite router storage, restart/revocation tests remain **NOT_RUN_A2** in this session due unavailable independent pinned checkout + verified network isolation. Work must perform these checks in its blocked-egress environment. Do not promote source construction to `VERIFIED_OFFLINE`.

### Single consolidated outside-WRITE_SET integration blocker register (do not edit without separate owner grant)

| Blocker | Exact other-owner/source path and interface | Consequence / next responsible owner |
|---|---|---|
| IB-01 trusted consent truth | No verified resolver/current policy source in pinned checkout; existing `src/config/account-store.ts` account policy flags are **not consent**. Required keyed `accountId,senderId,threadId,threadType`, revision monotonicity, expiry, revoked, human takeover and STOP. Snapshot must be rechecked by A1 at final send. | **Coordinator/A1 policy-interface alignment:** decide owner/read API for authoritative snapshot and expiry/revocation events. A2 currently defaults to deny without trusted resolver; cannot activate respond or retain. |
| IB-02 group edit caller | `src/agent/tools/save-memory-tool.ts` creates `PhamViSuaFact` without `threadId`. Must pass validated current `message.threadId` and confirm correct group thread type, otherwise group edit fails closed by design. | **A1**, scoped tool caller change and tests; do not change A2 guard. |
| IB-03 replay cursor and capture | `src/zalo/incoming-message-router.ts` calls `layBuCuaAccount(...).khiTinTrucTiep(msg)` for all returns except `trung`, including `bo`. `src/zalo/offline-replay/tiep-nhan-tin-lay-bu.ts` reenters `nhanVaGhiTinDen`. Need ensure denied/withdrawn scope cannot advance, retain or replay private content. | A2 router/writer + **A1 replay subsystem**; verify full expiry/revoke race and durable cursor cleanup in Work QA. |
| IB-04 persisted messages, media, summaries, contacts | `src/zalo/record-incoming-message.ts` calls `appendMessage` and `persistBatchImages`; `src/conversation/media-store.ts` has filesystem `writeFileSync`; `src/zalo/message-turn-processor.ts` writes assistant messages and creates summaries; `src/conversation/thread-store.ts` persists thread activity and summary. `history-store.ts` and `contact-store.ts` have independently callable unguarded DB entrypoints. No retention snapshot is passed to all writers. | **Coordinator assigns narrow cross-module integration owner**, Work validates zero prohibited durable DB/media/cache/replay data including after restart and opt-out. |
| IB-05 respond-only semantics | Current A2 router explicitly refuses `respond=true/retain=false` until its downstream message processor, batch/queue, media fetch and summary code can be proved nonpersistent. The pure `shouldRespond` contract correctly returns `respond:true,record:false` for scoped consent, but integrated response is deliberately blocked. | **A1 outbound processor + Coordinator** to define strictly ephemeral response path and send-time revocation/STOP/human-takeover checks. No default opt-in and no false functional PASS. |
| IB-06 consent lifecycle | Expiry, revocation and revision are consumed as fields but have no verified durable source, atomic read/compare, cache invalidation or cleanup of prior lawful retention. Need tests for revoked consent after queuing, restart, stale revision, cached policy and cleanup. | **Coordinator/A1** for shared trusted policy lifecycle, **Work** for independent race/restart tests. |
| IB-07 memory save authority | `src/agent/tools/save-memory-tool.ts` may write fact without independently checking `retain` consent at the tool boundary; also its duplicate-result prose treats new invalid-scope result as a duplicate. | **A1** under tool writer ownership; demand authorized `retain` snapshot + corrections to invalid-scope result handling. |
| IB-08 native testing gate | Node/pnpm checkout with blocked egress not available in A2 session; Work's harness exists separately. Test updates may expose other existing caller assumptions. | **Work** re-run `git apply --check`, `tsc --noEmit`, targeted allowlist tests and SQLite integrated tests with immutable source+combined patches; report exact pass/fail. |

**Interface message to A1/Coordinator (prepared, not delivered to another session):** Agree on a single validated, monotonic, thread-type-specific policy snapshot with fields from `PrivacyConsent`. A2 consumes it at inbound retention; A1 consumes **the same authoritative revision** at end-of-queue delivery. Distinguish `respond` from `retain`; both false by default, and never treat `bot_enabled`, allowlist membership, or mere account existence as user consent. Missing/mismatched/expired/revoked/STOP/human takeover `=> deny`. No automatic renewal or opt-in. A1 must supply `threadId` for group memory edits. Request explicit recipient-session handoff; Github report is not a verified cross-chat ACK.

**Current result:** `P0_PATCH_UPDATED_AWAITING_WORK_NATIVE_QA`; intended tests and source patch are available, no independent runtime PASS and no product/live authorization. **NEXT_OWNER:** Work then Coordinator/A0.
