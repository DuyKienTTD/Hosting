---
id: zalo-poc-02-a1-send-guard-2026-11-24
type: report
status: source-patch-prepared-blocked-integration-input
updated_at: 2026-11-24
sensitivity: public-redacted
---

# ZALO-POC-02-A1-SEND-GUARD — offline outbound safety patch

**Agent:** A1 | **Receipt:** TASK_ACKNOWLEDGED in A1 chat | **Scope:** sandbox-only isolated candidate copy | **Verdict:** `SOURCE_PATCH_PREPARED / BLOCKED_INTEGRATION_INPUT`; **not** integrated runtime PASS or safe product. **NEXT_OWNER:** Work independent targeted offline QA; Coordinator for integration and missing shared-interface decision.

## Authority / provenance
- Work order: [Coordinator exact task](https://github.com/DuyKienTTD/Hosting/blob/coordinator/zalo-poc-02-offline-remediation-2026-11-24/tasks/2026-11-24-zalo-poc-02-a1-send-guard.md), blob `be052c1c02083c667f8ffcdf9fc51d3251874a60`.
- Approval source: [PR #51 comment 7123763842](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7123763842) as pinned by order; this report does not elevate approval to live or main.
- Hosting `main` readback at task: `d549564de52429e777c68daf9df7a93df5f22f27`. Coordinator POC02 branch observed `390468da16ab1aab672b333baf32b53d7708d657`.
- Mandatory rule/source blobs from last verified main: AGENTS `af42293a8ae7d3e864cd9f89442bc6861e85c080`; workflow `9dd6a1601e9b2a1b472f4a1ae89e9626ada05797`; security `c24d608036b11dcd3fafcaefbefa23fdb591990e`; STATE `d74e6f3e7cc8bad0192f4a025e25d70aaa83d708`; CATALOG `26e125296fd0c39d0e82d6c5438dcc1ca2d8947f`; A1 profile `e88a048b8c075db5a0c3ac0cbb810680be4b3fe5`.
- Candidate immutable source: [vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561](https://github.com/vuhai2002/zalo-agent/tree/2dc09de31cd99306bc1ab18e57aa0aa872618561). Original source read with GitHub connector; upstream unmodified. `pnpm-lock.yaml` exists in pinned tree, but dependency installation and integrity of a full local checkout were **not tested**.

## Environment and execution
- Container preflight: `node --version` => **v22.16.0**, exit 0; `pnpm --version` => **not found**, command exit 127. No approved complete checkout/dependencies available; original project native build/typecheck **NOT_RUN**.
- A1 wrote an independent, dependency-free TypeScript **source-only candidate**: `experiments/zalo-poc-02/a1/src/agent/tools/send-dispatch-guard.ts` and matching test file. Prepared unified additive patch `experiments/zalo-poc-02/a1/a1-send-guard.patch` for Work to apply in **offline isolated checkout** only. Candidate path remains within A1-owned outbound tool helper scope; **no original implementation call site was changed**.
- First local prototype test command: `node --experimental-strip-types --test /mnt/data/zalo_poc02_patch/new/src/agent/tools/send-dispatch-guard.test.ts`, exit 0, TAP `tests 8, pass 8, fail 0`. **This result is for the first local prototype**, not a verified test execution of the exact GitHub-staged files. Work must run staged patch tests and native TypeScript checker before acceptance. All sends were synthetic closure counters; no real API/LLM/Zalo services started.
- Patch staged on GitHub is a subsequent semantically matching compact source version, but **not byte-identical** to the local prototype. This difference prevents claiming `VERIFIED_OFFLINE` for the staged revision without a separate exact-artifact rerun. No npm/pnpm install or paid download was performed.

## Outbound pathway inventory (pinned source inspection; not exhaustive certified coverage)

| Path | Observed dispatch | Guard integration status |
|---|---|---|
| `src/zalo/send-reply-in-parts.ts` blob `09f0bbf860760e772bc57d89420aacbd86df845b` | `sendOne` queues `target.guiMotDoan`; multipart, error/retry and technical fallback `notifyTechnicalError` share this path | **NOT_WIRED** |
| `src/zalo/deliver-chat-reply.ts` blob `a0cb93bea476cb668c0391e8d3b8a978152af678` | Calls multipart sender; history after send | **NOT_WIRED** |
| `src/zalo/message-turn-processor.ts` blob `e8fb91fc16a649f77e1288a5d0594322304f0be9` | Tool sends happen during agent execution; provider failure invokes technical fallback | **NOT_WIRED** |
| `src/scheduler/proactive-send-queue.ts` blob `c0588d92311178740f14d28f5773463865112ce3` | Global proactive and per-thread chain; delay between enqueue and send | **NOT_WIRED** |
| `src/scheduler/proactive-send-guard.ts` | Existing guard checks running/thread and daily slot, **not explicit consent, takeover, late policy version** | **NOT_WIRED** |
| `src/scheduler/scheduled-job-send.ts` blob `98b38a248d0d6a6f4f51e9ed02072d4bbdedb2e6` | `deliverProactively`→multipart and special post-send accounting; retry ambiguity risk | **NOT_WIRED** |
| `src/agent/tools/send-attachment-with-caption.ts` blob `065a9e9a362b5cbe83a96c54146cce8b89a0e387` | `enqueueSend` then `api.sendMessage` and style fallback | **NOT_WIRED** |
| `src/agent/tools/send-file-tool.ts` blob `41131145ac3b391e172cb93580c9c00cb84b1e9d` | Uses attachment helper, URL download may happen before send | **NOT_WIRED** |
| `src/agent/tools/add-reaction-tool.ts` blob `1f61211df4b555d3b486807f06c52dd4092fde12` | Direct `api.addReaction` | **NOT_WIRED** |
| `src/agent/tools/tag-member-tool.ts` blob `eec8dbfc730afc28a94b9518f1faba3b39596884` | `enqueueSend` direct `api.sendMessage` | **NOT_WIRED** |
| `src/agent/tools/create-image-tool.ts` blob `9b9156ea7bcb9ce6864ef7f49fa6175ffd0c8f24` | `enqueueSend` image send and separate retry notice | **NOT_WIRED** |
| `src/zalo/kenh-ca-nhan.ts` blob `e243d0a5b95746d6cf66a277ebfe49622d8c1692` | Auto reaction and typing/seen | **NOT_WIRED** |
| `src/zalo/message-receipts.ts` blob `c6e94e92308b0c59a0cfbaa139c390cefa0f6a78` | Delivered/seen receipt APIs; requires explicit classification of non-message side effects | **NOT_WIRED** |

**Coverage disclaimer:** The tool catalog has additional sends (document-generation, video, notifications and channel-specific Bot API). The listed paths do not establish a complete audited all-channel inventory. Do not publish blanket `all_sends_guarded`.

## Candidate contract and cases

- `Destination`: account + thread + recipient + `dm/group`, compared against immutable `expected`; reject malformed IDs, missing/unknown policy and DM recipient mismatch.
- Fresh `Authorization` checks consent `opt_in`, explicit non-takeover, global/thread STOP off, running true, destination binding/version; a changed policy version is denied even if consent remains true.
- `AttemptStore.reserveOnce` must be **durably atomic** across crashes/processes; a duplicate key or unavailable store fails closed. A send rejection with uncertain delivery remains `unknown` and cannot auto-retry. A send receipt failure also remains `unknown`.
- Two policy reads: initial read and a fresh read immediately before injected send closure. Each multipart segment needs its own intent/key/check.
- The staged files contain eight tests: success, fail-closed states, wrong recipient/group target/malformed IDs, revoke while queued, STOP mid-multipart, retry/restart with shared reservation, version drift and policy/idempotency read failures. **Mock only**, one synthetic account `synthetic_1`.
- `real_outbound_calls=0` for all executed A1 tests; `paid_api_usd=0` in this activity; **no live provider call**.

## Required integration blockers / security limitations (do not claim product PASS)

1. **BLOCKED_INTEGRATION_INPUT:** No approved shared **durable consent/opt-out/human takeover/global STOP authority** is exposed by current AccountConfig/Thread status. A2 owns privacy schema; cannot invent or edit it. Require Coordinator-approved read-only policy interface with version/freshness semantics and explicit secure default; missing fields must deny.
2. **BLOCKED_INTEGRATION_INPUT:** No provider-independent, immutable destination binding is plumbed through `ReplyTarget`, tool contexts and Bot API channels. Current unguarded paths listed above bypass this new module entirely. Must be wired at *every final outbound transport* including error replies, reaction, files and scheduled jobs, with a source-discovered manifest and negative bypass test.
3. **BLOCKED_ATOMICITY:** Two checks separated from the real send remain susceptible to a **TOCTOU** revocation immediately after final read, unless policy mutation and outbound admission are serialized under a shared gate or provider-side revocation semantics. In-process closures alone do not guarantee no sends after a concurrent STOP. Work must prove atomicity/fencing with same-store semantics.
4. **BLOCKED_RESTART_IDEMPOTENCY:** The test `AttemptStore` is an in-memory mock and cannot prove crash/restart durability. A real transactional store, collision-safe stable keys for each part/attachment/reaction, state machine and recovery policy need separate approved integration. Reserved-but-not-sent keys are fail-safe but can drop messages.
5. **BLOCKED_PROJECT_COMPILE:** No complete approved isolated source checkout, no pnpm/node modules, no native build/typecheck. The additive patch uses Node 22 type stripping for standalone synthetic tests, not the upstream project build. Work must verify patch applies and `pnpm build/typecheck` in an offline isolated runner without external egress.
6. **BLOCKED_PATH_COVERAGE:** No changes to A2-owned memory/consent paths, `incoming-message-router.ts`, allowlist, contact/history; no original send call site patched. An assertion that current system sends are guarded would be false.

## Reproduction / independent reviewer instructions

1. Obtain **exact** immutable candidate SHA and verify full lockfile, approved offline dependencies, network-disabled runtime, no real configs or secrets. Do not run `pnpm eval`, `pnpm start`, `pnpm dev`, real Zalo login or any paid provider.
2. Apply only `a1-send-guard.patch` to an isolated candidate copy, validate patch exactly matches staged source/test, then run `node --experimental-strip-types --test src/agent/tools/send-dispatch-guard.test.ts`. Document exit code and full TAP counts on this exact revision.
3. Compile/typecheck as dependency availability permits; run deliberate wrong-recipient, delayed revoke, multipart, error fallback, scheduler, attachment/reaction and cross-thread bypass tests. A detached unit test alone cannot prove these routes are wired.
4. Return independent findings and whether a narrow shared interface is approved; unresolved input means `BLOCKED_INTEGRATION_INPUT`, not PASS. No merge/live activation.

**A1 final status:** `SOURCE_PATCH_PREPARED / BLOCKED_INTEGRATION_INPUT`. The code/tests and unified patch are a reproducible **candidate for review**. A0/Coordinator controls any interface or later implementation authorization; Work provides independent QA. No real Zalo, paid API, deployment or Hosting main merge.


---

## CONTINUATION — Coordinator corrective receipt and integrated candidate (2026-11-24)

**ACTUAL SESSION ACK:** `TASK_ACKNOWLEDGED — ZALO-POC-02-A1-SEND-GUARD / CONTINUATION`. Exact instruction [PR #55 comment 7124438429](https://github.com/DuyKienTTD/Hosting/pull/55#issuecomment-7124438429), issued by repository OWNER; does **not** open new WBS, grant production or permit A2-owned writes. **Readback:** Hosting main `d549564de52429e777c68daf9df7a93df5f22f27`, PR55 former HEAD `5d6946449c5b7b9045aa7737c2f50ee749c5cb92`; candidate `vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561` frozen.

### Deliverable pins and scope

- **Unified 14-file candidate patch:** `experiments/zalo-poc-02/a1/a1-send-guard.patch`; Git blob `1fa7e1ef70630c29685e70f923bac42590d463fb`, consolidated by commit `4ac271400b5dec49ee433f28bac5765e41c80760`.
- **Eight upstream-path modifications in isolated copies (no upstream mutation):**
  1. `src/zalo/send-reply-in-parts.ts` — enqueue-time closure now calls `sendWithOutboundGuard` for each segment and technical error, requiring deterministic per-segment/technical key; fallback also requires its own guarded key.
  2. `src/zalo/message-turn-processor.ts` — stable chat intent based on account/thread/**original incoming msgId**; missing msgId fails closed (not turnId, which changes on restart).
  3. `src/scheduler/scheduled-job-send.ts` — scheduler intent keyed by job ID and scheduled-for timestamp, routed through multipart guard.
  4. `src/agent/tools/send-attachment-with-caption.ts` — guards attachment and style-fallback calls after queue; absent requestId fails closed.
  5. `src/agent/tools/send-file-tool.ts` — supplies intent from synthetic context message ID and file/caption digest, no real URL call in tests.
  6. `src/agent/tools/add-reaction-tool.ts` — wraps reaction API with guarded dispatch and stable message/reaction key.
  7. `src/agent/tools/tag-member-tool.ts` — wraps direct send and hashes member/text into intent; missing message ID fails closed.
  8. `src/agent/tools/create-image-tool.ts` — wraps advance-notice, retry notice and generated-image attachment; NO generation/paid provider invoked.
- **Six add-only modules/tests:** `src/agent/tools/send-dispatch-guard.ts`, `send-dispatch-guard.test.ts`, `durable-attempt-store.ts`, `durable-attempt-store.test.ts`, `outbound-guard-runtime.ts`, `outbound-guard-runtime.test.ts`.
- **Current integration form:** candidate original-path edits and tests stored as `experiments/zalo-poc-02/a1/source/**`, modules in `experiments/zalo-poc-02/a1/src/**` and corresponding unified patch. No real `zalo-agent` repository edited; no activation. Intermediate `parts/patch-1..3.diff` are build fragments; unified patch above is the canonical artifact.

### Executed sandbox tests — expected / observed (Node 22.16.0, no Zalo / network / paid)

| Case | Exact local command / target | Expected / actual | Status |
|---|---|---|---|
| A1-POC02-R01 | `node --experimental-strip-types --test /mnt/data/zalo_poc02_followup/durable-attempt-store.test.ts` | SQLite `INSERT OR IGNORE` unique reservation, sent receipt, no duplicate; exit 0, 3/3 PASS | `VERIFIED_OFFLINE_LOCAL_ADAPTED` |
| A1-POC02-R02 | Same invocation, process-restart subtest | Close SQLite, spawn a **new Node process**, reopen same temp on-disk DB; reserved key still rejected; exit 0 | `VERIFIED_OFFLINE_LOCAL_ADAPTED` |
| A1-POC02-R03 | `node --experimental-strip-types --test /mnt/data/zalo_poc02_followup/runtime-integration.test.ts` | Initial test stopped at `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX` (constructor parameter property), fixed in adapter; rerun exit 0, 4/4 PASS | `VERIFIED_OFFLINE_LOCAL_ADAPTED` |
| A1-POC02-R04 | Runtime integration suite, one synthetic account `synthetic_1` | One fake send then durable duplicate blocked (fake outbound counter=1); late thread STOP, opt-out, human takeover and unknown/mismatched destination all block (counter=0) | `VERIFIED_OFFLINE_LOCAL_ADAPTED` |
| A1-POC02-R05 | Pinned patch text generated from immutable upstream and isolated copies | The **eight modified files** were each replayed from patch hunks and compared line-for-line to its staged source copy; all 8/8 exact source comparisons matched | `VERIFIED_SOURCE_PATCH_REPLAY` |
| A1-POC02-R06 | Original full project `pnpm build`, `pnpm typecheck`, original sender suites, combined A2 tree | Not executed by A1: no pnpm/tsx/full checkout in this session. Work previously verified **baseline** native build/typecheck/73 tests and exact previous detached patch 8/8, not this 14-file revision | `BLOCKED_RUNTIME / PENDING_INDEPENDENT_WORK` |

**Key evidence nuance:** The local test runner uses local `.ts` import paths for Node's built-in type stripping; GitHub staged modules use upstream-conventional `.js` import specifiers and added tests are **not byte-identical to locally executed adapted tests**. Therefore do not label exact merged/native patch `VERIFIED_OFFLINE` until Work runs that exact checkout. Node's experimental `node:sqlite` warning was observed; no provider egress was used.

### STOP/idempotency protocol and limitations

- Guard defaults `DENY` when `setOfflineOutboundGuardRuntime` has no authoritative policy + attempt store. This **prevents live sends** for wired paths without integration but also means no successful real-mode functionality is claimed.
- Late policy read occurs **inside the actual per-thread queue callback**, after queuing/delay. Checks exact account/thread/recipient/type, `opt_in`, explicit `humanTakeover=false`, STOP flags false, running true, version unchanged and stable key; a revoked/unknown state blocks.
- Durable attempt implementation uses an on-disk SQLite file, `journal_mode=WAL`, `synchronous=FULL`, UNIQUE attempt key and `INSERT OR IGNORE`. A reserved/sent or uncertain key cannot be automatically retried; uncertainty returns fail-closed. **The running-process mock's positive send is a fake closure only.**
- **ATOMIC_STOP_UNRESOLVED:** the policy read and transport do not share an atomic lock/fencing transaction with the A2 policy writer. A STOP committed immediately after last policy read could race with actual send. Do **not** claim `NO_POST_STOP_SEND` in all interleavings; require Coordinator/A2-authorized atomic admission or single shared lock and Work race tests.
- **CONSENT_SOURCE_NOT_WIRED:** no approved real consent/opt-out/human-takeover store or epoch resolver is connected, by design. A2 owns inbound/group/privacy source; A1 only injected test policy and may not edit A2's paths. Unknown means block, not surrogate `bot_enabled`.
- **SOME_PATHS_FAIL_CLOSED_NOT_FUNCTIONAL:** scheduler cap-notice and other callers constructing `ReplyTarget` without `sendGuardRequestId` now deny, as do document tools using `guiFileKemCaption` without `requestId`. These routes are not approved functional sends; supply stable context keys with new scoped approval.
- **OTHER_OUTBOUND_BYPASSES_UNVERIFIED:** auto reaction, typing, seen/delivered receipts, busy-wait and other direct provider calls outside allowed modified set, especially `src/zalo/kenh-ca-nhan.ts`, `src/zalo/message-receipts.ts`, `src/zalo-bot/**` and `src/scheduler/scheduled-job-cap-guard.ts` remain outside A1's candidate WRITE_SET. A non-message side-effect manifest and shared lower transport boundary require Coordinator authorization. No "all sends guarded" assertion.
- **RETRY/FENCING:** reservation-per-side-effect blocks duplicate stable keys across restart; different keys can still represent the same logical send if caller identity is wrong. No durable ack from real Zalo and no real network retry was tested. A2 memory edit/delete group `threadId` interface remains a separate A2/Work combined-tree integration dependency.

### Author QA, STOP and NEXT_OWNER

- **PR #55 remains draft**, no merge. This A1 continuation changes only `reports/2026-11-24-zalo-poc-02-a1-send-guard.md` and `experiments/zalo-poc-02/a1/**`; no A2 paths, provider, external account, main or paid actions. `real_outbound_calls=0` for A1 and `synthetic_accounts=1` per executed fixture; `paid_api_usd=0`.
- **Current verdict:** `INTEGRATED_SOURCE_CANDIDATE_PARTIAL_BLOCKED` — patch is no longer just a detached guard, but it is **not** functionally integrated with authoritative privacy policy and not verified in upstream build/E2E. No product PASS or Zalo GO.
- **NEXT_OWNER:** Work independently applies this exact new 14-file patch on pinned upstream in offline no-egress checkout, runs native TypeScript and negative/race/fault/restart tests; Coordinator resolves shared policy/fencing and out-of-scope transport interface (and reviews A2 patch separately). Without those gates, HOLD.


---

## A1 continuation: TS5097 exact import-only correction (2026-11-24)

**TASK_ACKNOWLEDGED — ZALO-POC-02-A1-SEND-GUARD / TS5097-FIX.** Owner-forwarded [Coordinator comment 7124889257](https://github.com/DuyKienTTD/Hosting/pull/55#issuecomment-7124889257) received in this A1 chat. **Same task, same A1 branch/PR; no new work order.**

**Work's prior independent Q0 (reported by Coordinator, NOT A1 re-executed):** on immutable upstream `vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561`, prior patch Git blob `1fa7e1ef70630c29685e70f923bac42590d463fb`, `git apply --check` PASS, native build PASS, targeted tests **15/15 PASS**, but typecheck FAIL TS5097 at `src/agent/tools/send-dispatch-guard.test.ts:3:39`. Preserve this as **previous-patch evidence**; do not transfer its status to revised patch.

**Correction (exactly two test-import lines, no behavioral edits):**
- `experiments/zalo-poc-02/a1/src/agent/tools/send-dispatch-guard.test.ts`, old blob `763361e1dba82bc17b651a46496f59f3ea3525a2` → new blob `6e270c1b7c35b5c5eda1c437513e244ee7f47ead`. Lines 3 and 4 both changed `from './send-dispatch-guard.ts';` to `from './send-dispatch-guard.js';`. This matches project TypeScript NodeNext ESM import convention; all other test content is identical.
- Updated `experiments/zalo-poc-02/a1/parts/patch-3.diff` blob `a7044a977fed869c9e7c07ce408e4c67e2616fee` and canonical unified `experiments/zalo-poc-02/a1/a1-send-guard.patch` blob **`65ad964d1c371b3124b7d09b3ba81320044e7a4f`**, replacing old unified blob `1fa7e1ef70630c29685e70f923bac42590d463fb`. No `tsconfig` or guard runtime/behavior modified.
- **Remote readback QA:** both test import specifiers are now `.js`; the canonical 14-file unified patch equals concatenation of three patch parts; patch's exact added-test content matches staged test line-for-line; scanner detects **0** added import specifiers ending `.ts`. Other two newly added tests had **0** such imports before correction.
- **A1 compile/typecheck:** `NOT_RUN_A1` (native pnpm/project checkout unavailable in A1 environment). This is a source-only correction. **Do not claim TS5097 resolution proven by native typecheck** until Work runs exact new patch.
- **Next Work action:** apply **new exact patch blob** to same pinned candidate in existing blocked-egress sandbox; run native `pnpm typecheck` and *targeted affected tests only*. Keep prior 15/15 evidence attributed to old patch; new patch gets its own report.
- **Unchanged blockers:** authoritative consent/STOP/takeover policy source, atomic STOP/send fence, remaining outbound side effects and combined-tree privacy/retention QA. Project remains `PARTIAL_BLOCKED`, not product PASS/GO. No real Zalo, paid service, upstream or Hosting main writes, merge or A2 edits.

**A1 handoff verdict:** `IMPORT_FIX_PUSHED_READY_FOR_WORK_RECHECK`; **NEXT_OWNER: Work**, then Coordinator for S2 synthesis. Remote GitHub readback verified; no claim of new native test success.


---

## P0 CONTINUATION — Work-confirmed post-STOP race remediation (2026-11-24)

**Session ACK:** `TASK_ACKNOWLEDGED — ZALO-POC-02-A1-SEND-GUARD / P0-CONTINUATION` upon actual A0 handoff. **Source:** [Coordinator comment #7125611629](https://github.com/DuyKienTTD/Hosting/pull/55#issuecomment-7125611629); Work observed `stopped=true`, `fakeSendsAfterStop=1`, `status=sent` in [independent fixture](../experiments/zalo-poc-02/work/q0-combined.mts) on prior combined source tree `4970b45336c9dd67b389ca434e79bcb1794bde15` and [Work report](2026-11-24-zalo-poc-02-work-sandbox-qa.md) from commit `96aa50c41fa195f9418579ff164a81562a5908e6`. Candidate source remains **exact** `vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561`. Current Hosting main at preflight `d549564de52429e777c68daf9df7a93df5f22f27`. A1 changed only original A1 WRITE_SET.

### P0 patch state / exact object pins

- **Canonical unified patch:** [`experiments/zalo-poc-02/a1/a1-send-guard.patch`](../experiments/zalo-poc-02/a1/a1-send-guard.patch), Git blob **`22cba3430a569a9bdcafd0e205a11725b3f004ad`**, generated on this A1 branch by commit **`c28037201e425afc6acf8b08b4a9385e1d42d0e9`**.
- **17 upstream candidate paths:** 9 isolated modified copies (all prior 8 plus `src/agent/tools/save-memory-tool.ts`) and 8 add-only modules/tests (prior 6 plus atomic admission + atomic tests); all are represented in the patch. No actual `vuhai2002/zalo-agent` writes.
- New `src/agent/tools/atomic-send-admission.ts` (synthetic SQLite authority): same on-disk SQLite database, `BEGIN IMMEDIATE` transactional revision-bound policy updates and transport admission; `WAL`, `synchronous=FULL`, durable UNIQUE idempotency attempt key. Source SHA and patch content are Git blob-pinned; **this is not a real consent resolver**.
- `src/agent/tools/outbound-guard-runtime.ts` now **only** delegates to `AtomicAdmissionPort.dispatch`. It has no old `setOfflineOutboundGuardRuntime` read-then-send path. Without an explicitly installed synthetic atomic authority, sends deny by default. Group sender cannot be fabricated from group thread ID; missing real sender denies.
- `src/agent/tools/send-dispatch-guard.ts` old `dispatchWithLateGuard()` now **always blocks** even valid opt-in; the Work-reproduced direct read-then-send path cannot send. Eight existing detached tests remain and were updated to assert fail-closed behavior, not weaken negative tests. Positive-send coverage now lives in the separate atomic tests.
- `src/zalo/send-reply-in-parts.ts` and `message-turn-processor.ts` carry `senderId` for group chat; file attachment, reaction, tag and image tool stubs carry it from the validated `ctx.message` (no A2 edits). Scheduler group jobs without validated sender fail closed, pending source binding.
- **A1-owned memory caller fix:** `src/agent/tools/save-memory-tool.ts` now checks missing group `threadId` / `senderId` and passes `threadId: message.isGroup ? message.threadId : undefined` into A2's `PhamViSuaFact` for group edit/delete. No write to A2's `memory-edit-store.ts`.
- **A1↔A2 contract:** [`consent-atomic-interface.md`](../experiments/zalo-poc-02/a1/consent-atomic-interface.md) and actual [PR #56 comment #7125844091](https://github.com/DuyKienTTD/Hosting/pull/56#issuecomment-7125844091) request one consent source containing account/thread/type/**sender**, separate `respond,retain,passiveGroup,outbound` permissions, monotonic revision, expiry and STOP/opt-out/takeover writer using **the same admission lock**. This is **SENT_AS_GITHUB_COMMENT**, **A2_ACK_NOT_VERIFIED**, not approval of live policy wiring.

### P0 executable checks (accurate scope)

| Case | Evidence | Result |
|---|---|---|
| P0-S1 | Standalone `node --experimental-strip-types --test` synthetic SQLite atomic test; six scenarios: STOP microtask before admission, already-admitted in-flight, opt-out/takeover/expiry/default-deny, true child-process restart, revision/type, concurrent mutation | **6/6 PASS**, `VERIFIED_LOCAL_ADAPTED`, exit 0 |
| P0-S2 | Same suite + fake transport wrapper tests for durable duplicate refusal, STOP race and missing sender/binding | **9/9 PASS**, `VERIFIED_LOCAL_ADAPTED`, exit 0 |
| P0-S3 | Legacy route source inspection: `dispatchWithLateGuard` has no call to the supplied `_send`; wrapper uses atomic interface only | `SOURCE_REVIEW_FAIL_CLOSED`; Work must rerun its original race fixture on new exact patch |
| P0-S4 | A2 source interface review: [PR56 patch](https://github.com/DuyKienTTD/Hosting/pull/56) blob `419e290d75304f7d6602a51f650a9115d1ba6cf7`, no authoritative outbound STOP writer and no group memory caller `threadId` | `SOURCE_REVIEW`; bounded A1 caller patch added |
| P0-S5 | Native full candidate `pnpm typecheck`, `pnpm build`, all original tests, combined-tree Work QA, full network-disabled replay | `NOT_RUN_A1`, **no PASS claim**: pnpm/project checkout unavailable locally; Work independently controls no-egress runner |
| P0-S6 | [Sanitized local evidence](../experiments/zalo-poc-02/a1/p0-local-evidence.md) includes commands, exit codes, fixture properties and local source SHA-256 | `AUTHOR_EVIDENCE`, not native exact-patch QA |

**Test environment caveat:** Node v22.16.0 locally, `node:sqlite` experimental; no external Zalo/API/paid calls. Local tests used `.ts` import paths for Node strip-types; GitHub patch files use `.js` ESM paths. Local fixtures are semantically equivalent but **not byte-identical** to exact pinned GitHub revision. Also A1 did not independently establish a zero-egress network namespace; only synthetic, no-network code was executed. **Work must run exact patch in verified sandbox**. Do not carry Work's historical 15/15 over to this changed revision.

### Single consolidated blocker register — **outside A1 WRITE_SET**

| ID / status | Exact paths / missing interface | Required decision; no silent bypass |
|---|---|---|
| **B01 CRITICAL — NO_AUTHORITATIVE_POLICY** | `src/middleware/allowlist-filter.ts` and `src/zalo/incoming-message-router.ts` are A2-owned and define inbound `PrivacyConsent` only; authoritative consent writer/resolver + opt-out, global STOP, human takeover and expiry not specified in a permitted shared module | A2/Coordinator to ACK one **real but read-only until authorized** account/thread/sender/type/revision/expiry policy boundary, independent outbound scope; no synthetic opt-in for real user |
| **B02 CRITICAL — SHARED_FENCING_NOT_WIRED** | Policy mutation currently cannot be proven to use `atomic-send-admission.ts` transaction/DB; baseline account/thread flags and independent async policy stores do not share lock | Coordinate ownership and actual STOP writer path/transaction; test cross-process contention, expired/revoked before admission, already-admitted in-flight distinction. Reject async transport that defers dispatch beyond admission fence |
| **B03 CRITICAL — EXTRA PROVIDER SIDE EFFECTS** | `src/zalo/kenh-ca-nhan.ts` auto-reaction + typing; `src/zalo/message-receipts.ts` delivery/read receipts; `src/zalo/typing-indicator.ts`; `src/zalo-bot/kenh-bot.ts` Bot API action; `src/zalo/busy-wait-notice.ts` additional reply; `src/scheduler/scheduled-job-cap-guard.ts` daily cap notice | These paths were **not edited** under A1 original permitted modified set; explicitly classify whether each side effect needs outbound STOP control and grant exact write scope if so. Some common reply paths now fail closed when missing stable key, but native E2E not proven |
| **B04 HIGH — MORE TOOL PATHS** | `src/agent/tools/create-document-tools.ts` calls `guiFileKemCaption` without stable `requestId`; `src/agent/tools/tai-video-tool.ts` uses separate `api.sendVideo` route. Other tool helper/notification paths need corpus-wide source scan | Document-tool calls currently **fail closed**, not functional. Video transport **NOT_GUARDED**, not cleared for product use. Need explicit path grant and targeted fake test; do not infer coverage from file tool or multipart |
| **B05 HIGH — GROUP/SCHEDULER BINDINGS** | `src/zalo/reply-target-tu-kenh.ts`, `src/scheduler/scheduled-job-cap-guard.ts`, scheduler job target factories, `src/zalo-bot/kenh-bot.ts` lack globally verified sender/recipient/intent key | A1 guard denies when group sender absent. Need trusted identity binding and immutable attempt ID at each source. Never substitute group ID as sender or reuse a key across different segments/attachments/reactions |
| **B06 HIGH — A2 TYPECHECK/LEGACY TESTS** | Work previous combined-tree `src/conversation/memory-edit-store.ts:77:39` TS2769, plus nine legacy `src/middleware/allowlist-filter.test.ts` assertions expecting auto consent | A2 owner/Work to reconcile typed `threadId` optional overload and updated consent test semantics; A1 may not edit these sources |
| **B07 HIGH — RETENTION/REPLAY/RESTORE** | `src/conversation/contact-store.ts`, `history-store.ts`, summaries/cache/media, offline replay cursor and inbound replay routines; A2 privacy report documents missing authority/retention revocation | STOP admission alone cannot prove deletion, replay suppression, no passive retention, cache invalidation or historical data retention; distinct A2/Coordinator decision and independent Work SQLite/restart QA |
| **B08 HIGH — REAL PROVIDER DELIVERY + ALLOWLIST** | zca-js/Bot API transport internals and real network delivery state; no approved live Zalo auth or provider dry run | Provider calls are strictly prohibited. A sent/admitted attempt may complete after STOP, but **no new admission** may start after committed STOP under the defined shared-lock protocol. Uncertain delivery must never auto retry |
| **B09 RUNTIME / COST / REVIEW GATE** | A1 env lacks original checkout/pnpm; Work has prior immutable no-egress baseline and review harness, but has not reviewed this new 17-file patch | Work to run `git apply --check`, native `pnpm typecheck/build`, targeted prior 15 + new atomic cases, the Work microtask race and combined A2 tree before acceptance. Do not rerun unrelated 73 test suite just to count tests |

**Patch scope:** The canonical patch includes only approved upstream target file paths in `src/zalo/{send-reply-in-parts,message-turn-processor}.ts`, `src/scheduler/scheduled-job-send.ts`, and `src/agent/tools/**`. All source copies, tests, logs and this report live under the original A1 Hosting WRITE_SET. Actual additional paths above are **reported but not edited**.

**P0 status:** `P0_ATOMIC_ADMISSION_CANDIDATE_READY_FOR_INDEPENDENT_QA / INTEGRATION_BLOCKED`. The exact Work-reproduced non-atomic legacy path is disabled, and new synthetic atomic mechanism is written and locally tested. Real STOP writer, all side effects and combined-tree acceptance remain **BLOCKED**. **NEXT_OWNER:** Work independent negative/fault/restart/native QA on patch SHA `22cba3430a569a9bdcafd0e205a11725b3f004ad`; Coordinator/A2 handle B01–B09 gates. No merge, live, paid, agent activation or production.
