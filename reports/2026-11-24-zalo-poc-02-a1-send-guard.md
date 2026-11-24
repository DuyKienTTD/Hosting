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
