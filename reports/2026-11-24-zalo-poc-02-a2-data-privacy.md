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
