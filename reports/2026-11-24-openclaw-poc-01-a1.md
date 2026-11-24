---
id: openclaw-poc-01-a1-send-test-design
type: report
status: author-source-design-complete-independent-qa-pending
task_id: OPENCLAW-POC-01-A1-SEND-TEST-DESIGN
owner: A1
updated_at: 2026-11-24
sensitivity: public-redacted
---

# OPENCLAW-POC-01 — A1 outbound send-context / STOP negative-test design

**Actual A1 ACK:** `TASK_ACKNOWLEDGED — OPENCLAW-POC-01-A1-SEND-TEST-DESIGN` in the A1 chat after owner-forwarded work order. **WBS:** OC-S01/S02. **MODE:** `OFFLINE_TEST_ONLY / SOURCE_DESIGN`; **NEXT_OWNER:** Chat Điều phối → Work independent harness execution. **Verdict:** `SOURCE_PINNED_TEST_MATRIX_READY / NATIVE_NOT_RUN`; this is neither an app patch nor a runtime safety PASS.

## 1. Authority, provenance and capabilities

| Evidence | Exact immutable pin / observation |
|---|---|
| Hosting work order | [task](https://github.com/DuyKienTTD/Hosting/blob/18bbfe61ca375beddb22cfbe22a2397887590b60/tasks/2026-11-24-openclaw-poc-01-a1.md), blob `5c5bc1bfac681f263aabace6ac5aa4b8e9ba2776`; status in source `prepared-owner-forward`; actual owner forwarding/ACK in THIS session, not inferred for Work |
| Hosting document commit | `18bbfe61ca375beddb22cfbe22a2397887590b60`; main HEAD observed separately `d549564de52429e777c68daf9df7a93df5f22f27` |
| Upstream candidate | [openclaw/openclaw@391dea93e0a97fff97f9f3d5e94eac992b247b09](https://github.com/openclaw/openclaw/tree/391dea93e0a97fff97f9f3d5e94eac992b247b09) — immutable source pinned, no SHA substitution |
| Declared runtime/dependencies | Task states @openclaw/zalouser `2026.11.7`, zca-js `2.2.0`, Node `>=24.16.0 <25 || >=26.1.0`, pnpm `12.15.0`, Vitest `5.0.5`, lockfile blob `d625f6e977d222c3bbc540de9e7fd2215a4def17`; **REPORTED_BY_TASK**, not installed/runtime-verified |
| A1 local runtime preflight | `node --version` → `v22.16.0` (below requirement); `pnpm --version` → command not found; `git --version` → `2.47.3`; `/mnt/data/openclaw` checkout absent. Native tests and locked dependency integrity **NOT_RUN / BLOCKED_RUNTIME** |
| Required Hosting rules read | `AGENTS.md` `af42293a8ae7d3e864cd9f89442bc6861e85c080`; `rules/AGENT_WORKFLOW.md` `9dd6a1601e9b2a1b472f4a1ae89e9626ada05797`; `rules/REPOSITORY_SECURITY.md` `c24d608036b11dcd3fafcaefbefa23fdb591990e`; `agents/a1.md` `e88a048b8c075db5a0c3ac0cbb810680be4b3fe5`; `STATE.md` `d74e6f3e7cc8bad0192f4a025e25d70aaa83d708`; `CATALOG.yaml` `26e125296fd0c39d0e82d6c5438dcc1ca2d8947f` |
| Task permissions | Exactly ONE document, `reports/2026-11-24-openclaw-poc-01-a1.md`, on `a1/openclaw-poc-01-2026-11-24`; no app-code edits, peer writes, upstream changes, paid operations, customer data, QR/login/credentials, live Zalo or merge |

**No test executed here.** Source read by GitHub connector; no exact checkout, install, lifecycle script, native runner, app/test harness or fake HTTP fetch was started. The source review below is `VERIFIED_SOURCE_READ`, **not** `VERIFIED_MOCK`.

## 2. Source-pinned decisive path and native harness

| File | Blob | Source-level finding and boundary |
|---|---|---|
| `extensions/zalouser/src/send-context.ts` | `f46d05e1421a8096f03bdc295c3fc2ed613154ec` | `AsyncLocalStorage` per caller, `active` retirement; `assertCurrent` checks active/signal/`assertDirectAdapterHandoff` at lines 15–21; `fetchWithZaloSendContext` at 44–68 awaits `onPlatformSendDispatch` for matching visible POST, then `effect.initiate(() => assertCurrent(); fetchImpl(...))`. **Final exact fake transport initiation** is entering `fetchImpl`, not simply callback return or promise settlement |
| `extensions/zalouser/src/send.handoff.test.ts` | `f482881116e7eeea4b923717e2ada9789db8676d` | Existing suites: effect-preparation gate, canceled/retired after cookie wait or dispatch callback, multipart progress, two concurrent callers same cached SDK, upload failures/redirects, audio/voice dispatch, optional tool cancellation. Good native basis, **not a global STOP semantics test** |
| `extensions/zalouser/src/send.media-handoff.test.ts` | `346752b1a30d4b9304896901b8709f69cc5e57a9` | Existing media guard DNS dispatcher/proxy and cancellation while resolving pinned DNS; GET/HEAD/upload are distinct from recipient-visible message POST |
| `extensions/zalouser/src/send.handoff.test-support.ts` | `9ed70685d62bf8a68c2f2e379bc9bdd1c6f9a685` | `SendHarness.fetch` (lines 174–178) appends every fake network initiation to `requests`; `gate()`, `holdCookie()`, fake SDK `API`, synthetic URL and async upload callback are already available. `harness.requests` is the decisive fake network start counter |
| `extensions/zalouser/src/zalo-js.ts` | `fccc93d26637fd22344198e04bad6aeaebfd08fb` | `withZaloApi` lines 402–425 checks caller, shares cached API and enters `withZaloSendContext` if `handoff`; `sendZaloTextMessage` 752–767; link 838–872. **Direct typing/reaction/delivered/seen functions at 770–836 have no `ZaloSendHandoff` parameter** → not proven bound to this handoff; classify as additional side-effect coverage `FEATURE_GAP/PENDING_SCOPE` |
| `extensions/zalouser/src/send-api.ts` | `904a8349422dbee9f04d678f0de19e46a7b723cb` | Text/media path `api.sendMessage` at 78–82,126–134; audio first caption then upload then `api.sendVoice` at 76–123. Upload and HEAD may occur before visible send; any resume must recheck gate |
| `extensions/zalouser/src/send.ts` | `3a56dfa3897cb6066171f097c9d09eba1bca2ea1` | Multipart iterates chunks at 47–72, persists per-part progress `onDeliveryResult`; partial result represented by `createChannelPartialDeliveryError`, not license to retry already emitted segments |
| `extensions/zalouser/src/tool.ts` | `05a6e19caa2848ece9a1c3f17ec756023788f9d1` | Tool `send/image/link` at 116–152; target resolution at 75–100 combines explicit `threadId` and ambient target. Must assert identity and type from normalized structured target, not display names |
| `extensions/zalouser/src/types.ts` | `e9051aa0d9e0b3a0374aa73ca6a9ebcaa6a38f2f` | `ZaloSendHandoff` picks `signal`, `assertDirectAdapterHandoff`, `onPlatformSendDispatch` (64–66). **No explicit global/account/thread STOP token, policy revision or durable idempotency contract in this handoff type** |

### Send-path chain / coverage boundaries

```text
Channel message.send.text/media | outbound.sendText/sendMedia/sendPayload
  -> extensions/zalouser/src/send.ts (optional multipart)
  -> zalo-js.ts sendZaloTextMessage -> withZaloApi(profile, handoff)
  -> withZaloSendContext / AsyncLocalStorage
  -> zca-js SDK request / fetchWithZaloSendContext
  -> await onPlatformSendDispatch for selected visible POST paths
  -> captureEffectAuthority().initiate(() => assertCurrent(); fetchImpl(...))
  -> fake request recorded at SendHarness.fetch

Tool action send/image -> sendMessageZalouser / sendImageZalouser
Tool action link -> sendZaloLink -> api.sendLink -> same handoff if option supplied
Direct typing/reaction/receipts -> zalo-js.ts functions without handoff option
Scheduler/proactive/cron -> upstream caller must be traced to registered outbound
  or tool and classified by entrypoint; this source review alone is NOT
  proof all scheduler notifications use registered handoff.
```

**Failure model:** Cancellation after a high-level admission decision, but *before* the actual transport starts, can leak a send if the last decision is cached or an SDK callback starts work after scope retirement. The prior Hosting ZALO-POC-02 result is a **historical failure-mode analogy**, not proof that OpenClaw currently has that defect. Conversely `assertCurrent` after `onPlatformSendDispatch` is a positive source defense, **not proof that cross-caller global STOP or bypassing direct APIs is implemented**.

## 3. Deterministic fixture and instrumentation contract (for Work)

- One **synthetic account** `account_1`. Three fictional customer IDs: `user:201`, `user:202`, `user:203`; customers 201 and 202 share the exact display name `Nguyen Van A` but are **different recipients**. Two overlapping groups: `group:300` has 201+202; `group:301` has 202+203. No real Zalo IDs or address book.
- Use already-existing `createSendHarness()` from `send.handoff.test-support.ts` and controlled `gate().entered/release` promises; `FakeTransport` is `harness.fetch` and records `{path,method,params}` immediately on invocation. Filter **visible POST** using `MESSAGE_REQUEST_PATH` from `send-context.ts` and separately record uploads/HEAD/GET/redirects.
- Extend **test-only harness** (not application code) with a synthetic `STOP authority` having scopes `caller | thread | account | global`, monotonic revision and explicit time of STOP commit. Inject its `assertCurrent` into `assertDirectAdapterHandoff`; `onPlatformSendDispatch` is a deterministic gate that can pause before initiation. Work must not falsely treat per-caller `AbortController` as a global STOP implementation.
- Each fixture logs `seq` event order: `ENQUEUED → DISPATCH_HOOK_ENTER → STOP_COMMITTED → HOOK_RELEASED → FETCH_ENTERED / DENIED`; avoid clock sleeps and wall-time races. Check `fetchEnteredCount`, `visibleSendCount`, recipient/type and `onDeliveryResult` IDs; expected ZERO visible sends **that start after a STOP commit**. Already-started fake send may complete after STOP and must be marked `IN_FLIGHT_PRE_STOP`, not a new leak.
- Synthetic accounts = exactly **1**; real outbound = 0; paid API USD = 0; new infrastructure USD = 0. Network disconnected before code execution, mocked DNS and HTTP, fake LLM; temporary state only. Use only pinned lockfile with audited lifecycle scripts/integrity if independent runner needs dependencies. Do not run an unfiltered full suite or AI eval.
- Evidence per case: `candidate SHA, lockfile SHA, harness/test SHA, Node/pnpm/Vitest versions, exact command+exit, expected, observed, 2+ deterministic repetitions for P0 cases, number of visible fake POSTs initiated after STOP, all HTTP request count, prohibited real calls, normalized recipient/thread type, result status and sanitized timeline`.

## 4. Prioritized **negative** test matrix — Work execution plan

**Legend:** `NATIVE_EXISTING` means pinned test with similar behavior exists but not necessarily all demanded assertions; `PROPOSED_TEST_ONLY` is a new fixture design; `FEATURE_GAP` means source currently does not prove a required product property. All cases below are **NOT_RUN_A1**.

| ID / priority | Native anchor and deterministic injection point | Setup / failure injected | Decisive assertions at **transport initiation** | Scope / expected evidence status |
|---|---|---|---|---|
| **OC-N01 P0** | `send.handoff.test.ts` existing `stops a retired caller after dispatch notification`; inject `onPlatformSendDispatch` gate at `send-context.ts:58` | Caller for `user:201` passes initial admission; pause dispatch hook; commit synthetic **THREAD STOP** (revision+1); release callback while signal remains NOT aborted | `harness.requests.filter(visible POST).length=0`; `fetchEnteredAfterStop=0`; rejected for STOP; **detects cached high-level approval** | `PROPOSED_TEST_ONLY`, THREAD_STOP not supplied by native API |
| **OC-N02 P0** | `send-context.ts:62–67` `effect.initiate`; `effect-preparation.test-support` gate | Dispatch hook has returned; block **effect preparation** before fetch closure; commit ACCOUNT or GLOBAL STOP; unblock | No `fetchImpl` entered after STOP; if the existing `assertCurrent` only checks caller, document **FEATURE_GAP** rather than invent global policy | `PROPOSED_TEST_ONLY`; source defense needs injected STOP authority |
| **OC-N03 P0** | Existing `send.handoff.test.ts` effect preparation, cookie gating | Caller `user:201` is canceled after admission, but before cookie SDK fetch starts; control second `user:202` on same cached API | A: 0 visible POST; B: 1 visible POST to `202`, `type=User`; A abort does **not** cancel B | `NATIVE_EXISTING` overlapping-caller case + STOP extension |
| **OC-N04 P0** | Existing `keeps overlapping caller checks separate` | Commit GLOBAL STOP while A paused, attempt B concurrently; then independently abort A after STOP | Both A and B: zero **new** visible POST after global STOP; distinguish global-stop from caller cancellation; capture which scope is actually implemented | `PROPOSED_TEST_ONLY / FEATURE_GAP` |
| **OC-N05 P0** | `send.ts:47–72` and existing chunk-progress test | Send 2001 chars (2 chunks); after first visible POST and progress callback, commit thread STOP while second chunk queued | Exactly one text message initiated pre-STOP; second not initiated; `onDeliveryResult` preserves first ID and partial result, no automatic replay of chunk 1 | `NATIVE_EXISTING` chunk cancellation analogous, global/thread STOP proposed |
| **OC-N06 P0** | `send-api.ts:76–123`, native upload/voice fixture | Audio caption sent, then hold `uploadAttachment` callback or voice HEAD; commit STOP before `/forward` visible send | Captured pre-STOP caption receipt; NO `/forward`/voice send after STOP; uploading non-visible media is separately classified; no duplicate caption | `NATIVE_EXISTING` media handoff + STOP extension |
| **OC-N07 P0** | `send.handoff.test.ts` `retires cookie-waiting upload requests`; `send.media-handoff.test.ts` guarded DNS | Pause DNS, cookie, upload completion or HEAD; commit STOP, resume asynchronous callback | Zero new visible POST; distinguish allowed **pre-STOP** upload/HEAD from forbidden **post-STOP** message send; no callback escaping retired ALS scope | `NATIVE_EXISTING` cancel guard; STOP variant proposed |
| **OC-N08 P0** | `send-context.ts:12–13` visible-route matcher; fake fetch path log | Exercise each DM/group visible POST variant: `sms,sendmsg,link,sendlink,photo_original/send,asyncfile/msg,gif,forward`; STOP between last hook and fake fetch | For every path, exactly 1 dispatch hook when eligible and 0 fake visible POST after STOP; report unmatched sends; ensure media `/upload` is not mistaken for visible delivery | `PROPOSED_TEST_ONLY`, 8-route parameterized |
| **OC-N09 P0** | `zalo-js.ts:838–872`, `tool.ts:94–152` | `tool action=link`, explicit wrong `threadId` vs ambient group; same display name 201/202; malicious or malformed `isGroup`/recipient binding | Fail closed on scope/type mismatch; no `toid=wrong`; display name must never resolve identity; valid group maps `grid=300`, not `user:300` | `PROPOSED_TEST_ONLY`; current code target override may be intended feature, so **policy mismatch** must be explicit |
| **OC-N10 P1** | `zalo-js.ts:770–836` direct `sendTypingEvent/addReaction/sendDeliveredEvent/sendSeenEvent` | STOP before these calls, synthetic fake API enabled, no handoff provided | Count zero **side-effect** calls if STOP scope includes these actions; otherwise classify `UNGUARDED_PATH_FEATURE_GAP` rather than PASS for message-send-only hook | `FEATURE_GAP`, direct APIs not covered by `ZaloSendHandoff` |
| **OC-N11 P1** | Scheduler/cron entrypoint → registered outbound/tool: needs specific caller-source readback by Work | Queue due job for group:300; revoke group/account at dispatch hook; next job group:301 remains active | No group:300 visible POST post-STOP; group:301 continues unless global STOP; no fallback to raw client send; report exact route and scheduler owner | `PROPOSED_TEST_ONLY`; **SCHEDULER_ENTRYPOINT_NOT_VERIFIED** |
| **OC-N12 P1** | `send.ts` partial receipt + existing failure/redirect suite | First platform POST accepted, transport receipt lost or `503` after side effect; restart caller/test process, replay same logical intent | No duplicate visible send for same intent; preserve accepted message IDs and ambiguous state; if no durable attempt key/store in API, mark `IDEMPOTENCY_FEATURE_GAP`, not native PASS | `PROPOSED_TEST_ONLY / FEATURE_GAP` |
| **OC-N13 P1** | `send.handoff.test.ts` redirect behavior | Initial visible POST accepted pre-STOP, returns 302; STOP before redirect follow-up and retry/fallback | No new user-visible POST initiated after STOP; classify GET redirect separately; ensure authorization not silently inherited by independent follow-up call | `NATIVE_EXISTING` redirect cancel; STOP/retry proposed |
| **OC-N14 P1** | `send-context.ts` ALS and `harness.createApi` same profile | Parallel 201/202 DM and groups 300/301, two same names, overlapping members; A canceled, group 300 stopped | Every request has exact intended ID/type; unaffected scopes continue; no transfer of A context into B; no auto escalation group STOP→global | `NATIVE_EXISTING` caller-isolation base + added identity/scope negatives |
| **OC-N15 P1** | `send.media-handoff.test.ts` guarded runtime dispatcher | Ambient fetch ignores passed dispatcher; remote media returns redirects or private/changed DNS | Only pinned guarded dispatcher may initiate media download; on cancellation/STOP no later message POST; no real DNS or egress | `NATIVE_EXISTING` DNS tests; STOP extension proposed |
| **OC-N16 P1** | `send.handoff.test.ts` tool optional callback; `tool.ts:112–152` | Tool send/image/link canceled after tool resolves target but while `withZaloApi` restores cached session; ensure asynchronous dispatch stage reached | Zero fake visible sends after cancel; next unrelated tool call succeeds; no stale tool signal or thread binding retained | `NATIVE_EXISTING` for send; image/link proposed |
| **OC-N17 P2** | `send-context.ts:70–80` media fetch without message dispatch hook | User cancels during media GET/HEAD vs global STOP; same group recipient | Media fetch may have begun but visible send must not; assert separately `downloadCount`, `visibleSendCount`; do not classify GET as outgoing message | `PROPOSED_TEST_ONLY` |
| **OC-N18 P2** | `send-context.ts:9–42` ALS active flag, parallel `Promise.all` race | One parallel SDK upload errors and retires context; another callback continues asynchronously | Zero additional visible sends from retired context; unrelated context unaffected; test `active=false` after operation finally | `NATIVE_EXISTING` comparable race test |

### Mandatory P0 decision rules

A **successful** cancellation/STOP test must satisfy BOTH: (1) intentional *no more admissions after STOP* in the modeled authority, and (2) **no fake recipient-visible transport invocation starting after STOP**, with exact event ordering. A rejected Promise alone is **NOT PASS**. Distinguish:
- `caller aborted` → only that caller retired; unrelated caller still sends;
- `thread STOP` → same thread blocked across callers;
- `account/global STOP` → every applicable thread/caller blocked;
- `IN_FLIGHT_PRE_STOP` → already initiated transport may complete and is separately counted;
- `FEATURE_GAP` → OpenClaw source has no proven shared STOP writer/epoch or restart-durable intent store; a test-only STOP authority does not create real application behavior.

Stop after **first decisive P0 reproduction** if code leaks, preserve sanitized timeline and request count, then run only the narrowest next disambiguating test. Do not widen into unrelated application patching. Do not reuse historical ZALO-POC-02 PASS/FAIL as OpenClaw measurements.

## 5. Work exact re-entry procedure / acceptance

1. Validate pinned source `391dea93e0a97fff97f9f3d5e94eac992b247b09`, package/lockfile SHA and installed versions; inspect npm/pnpm lifecycle scripts *before* installing; lock outbound egress before running any project/dependency code. **Never** use real Zalo, QR, tokens or actual customer data.
2. Confirm native fixture can run with exactly one synthetic account/three fake customers/two intersecting groups. Start with **OC-N01, N02, N04, N05, N08**; these decide whether a STOP performed after admission is enforced at actual transport initiation.
3. Run the already-pinned native cancellation suites as targeted comparisons, not to duplicate all prior tests. For proposed cases, create **test-only** controlled `STOP` authority/harness on Work-owned branch; never amend application code through this A1 report.
4. Capture version/hash and each test's `command, exit, fake requests, fake visible POST initiated after STOP, real outbound count=0, expected/observed, repetition, scope, PASS/FAIL/BLOCKED/FEATURE_GAP`. Native suite not runnable due Node/pnpm/lockfile/egress limitations → `BLOCKED_RUNTIME`, no inferred result.
5. Handoff Work's findings to Coordinator. A1 only provides source-pinned design; Work independently determines whether the native plugin blocks the modeled STOP under its actual handoff contract and where non-handoff direct APIs bypass it. **No product GO / live activation**.

## 6. Consolidated limitations and handoff

- **L01 — current A1 runtime mismatch:** Node `22.16.0` below declared requirement, pnpm unavailable, checkout absent; native Vitest not executed. Plugin dependency/lockfile integrity not independently reproduced.
- **L02 — semantic boundary:** `signal` and `assertDirectAdapterHandoff` are per-caller. Current `ZaloSendHandoff` type lacks global/thread STOP policy, epoch and durable idempotency. A synthetic fixture can show what an integration should guarantee but cannot prove OpenClaw implements an app-wide STOP.
- **L03 — outbound bypass:** typing/reaction/receipts are direct API paths lacking handoff in the inspected signatures; scheduler/cron caller mapping requires separate Work readback. Media downloads/HEAD must be counted separately from visible sends.
- **L04 — idempotency gap:** `onDeliveryResult` and partial-receipt handling are available; no demonstrated durable reservation keyed by stable attempt ID across restart. Do not label retry safe.
- **L05 — scope:** No code edits, no native test execution, no account access, no provider network and no paid calls. This report is the only authorized A1 output and must not be interpreted as sending the instruction to Work automatically.

**Final status:** `READY_FOR_COORDINATOR_HANDOFF / TEST_DESIGN_ONLY`. **NEXT_OWNER:** Chat Điều phối forwards this source-pinned design to Work; `WORK_SENT=NOT_VERIFIED`, `WORK_ACK=NOT_VERIFIED`, `WORK_QA=NOT_STARTED`.
