# ZALO-POC-02 — A1 ↔ A2 synthetic consent/admission boundary (P0 proposal, not approved live wiring)

**Observed A2 patch:** PR #56 / `privacy.patch` blob `419e290d75304f7d6602a51f650a9115d1ba6cf7`, introducing `PrivacyConsent { verified:true, respond,retain,passiveGroup }` in `src/middleware/allowlist-filter.ts` but **no authoritative outbound/STOP writer**. A1 is sole editor of this note; A2 implementation and ACK remain separately required. **No actual customer consent is inferred or granted.**

## Proposed authoritative policy record (one synthetic account for QA)

`{ accountId, threadId, senderId, threadType:'dm'|'group', verified, respond, retain, passiveGroup, outbound, optedOut, takeover, stopped, running, revision, expiresAtMs }`

- `respond`, `retain`, `passiveGroup` and `outbound` are **separate scopes**. A2 `PrivacyConsent` cannot imply outbound permission.
- Fail closed on absent, revoked, expired, mismatched or unverified policy. `bot_enabled=false` does **not** mean explicit human takeover.
- Group sender ID must be a validated identity, independent of group thread ID; DM sender/recipient binding validated before any side effect.
- STOP, opt-out and takeover mutations **must** increment monotonic revision under the *same durable SQLite transaction discipline and database lock* used by transport admission. No independent `await readPolicy` check can guarantee the race.
- Linearization point is admission/start of synchronous transport initiation under `BEGIN IMMEDIATE`, not eventual provider delivery. STOP committed before admission denies; if STOP commits after admission an already in-flight send is not retractable. Delivery/receipt uncertainty retains reserved attempt key and forbids automatic retry.
- If a client API defers actual transport until a later microtask, the adapter must move the admission lock to the actual transport initiation point, not merely to an asynchronous wrapper. Work must inspect runtime call graph and validate with adversarial fixture before approval.
- The current `openSyntheticAtomicAdmission` writes a **test-only** policy table, never real verified consent. Connecting its `mutatePolicy` API to production requires A2/Coordinator authorizing the source of truth, persistence/retention and writer access; no constructor should silently fabricate opt-in.

## A2 / Coordinator exact outstanding interface questions

1. Which approved writer path commits STOP/opt-out/takeover and consent expiry? Current A2 owned `src/middleware/allowlist-filter.ts` has a read contract, not a durable writer. Need one explicit approved cross-owner entry point or shared module and a lock/fence protocol; **BLOCKED_OUTSIDE_WRITE_SET** until ownership granted.
2. How is `senderId` authenticated for bot/group/scheduled sends and reflected in account/thread/recipient bindings? A1 group send defaults deny if unknown.
3. Which adapter reports global STOP, account running, group membership changes and retractable queued work? These must be checked or mutation-fenced at dispatch, not inferred from inbound allowlist.
4. How do `respond` and `retain` consent changes cancel replay/caches/summary/media and pre-queued jobs? This is not guaranteed by outbound admission; A2/Coordinator needs separate retention and cancellation design.
5. Can `src/zalo/kenh-ca-nhan.ts`, `src/zalo/message-receipts.ts`, `src/zalo-bot/**`, `src/scheduler/scheduled-job-cap-guard.ts`, document/video tool sends and provider-bound queue helpers be included in a future shared transport WRITE_SET? Without that explicit owner permission, they are **UNVERIFIED_OR_BLOCKED**, not protected.

**A1 owned caller fix:** `src/agent/tools/save-memory-tool.ts` now forwards `threadId: message.isGroup ? message.threadId : undefined` into `PhamViSuaFact`; group message without thread/sender identity returns an error. A2's group edit/delete SQL retains its own independent authorization.

**Status:** `INTERFACE_PROPOSED_AWAITING_A2_COORDINATOR_ACK`; no real consent resolver, no live policy storage, no product GO.


## Coordinator section 8 binding update — 2026-11-24

**Authority:** [immutable Section 8](https://github.com/DuyKienTTD/Hosting/blob/bfa196c4216815e5ea5c7353c4e1f7a53f11bc2a/reports/2026-11-24-zalo-poc-02-s2-integration.md). **Sole policy writer = A1**; **A2 consumes `ReadOnlySyntheticPolicy.readSnapshot` only**. Neither author may maintain a second policy table or write path. This is a synthetic QA authority, not real user consent.

Canonical interface implemented in `src/agent/tools/atomic-send-admission.ts`:

```ts
const authority = openSyntheticAtomicAdmission(pinnedTestDbPath);
const readonlyPort = authority.readOnly;
const snapshot = readonlyPort.readSnapshot({ accountId, threadId, senderId, threadType }, nowMs);
// A2 maps verified && unexpired && !optedOut && !takeover && !stopped
// && !globalStopped && !accountStopped && running to its own scopes;
// NEVER infer outbound from retain/respond, nor treat missing snapshot as consent.
```

- Scoped record: `accountId, senderId, threadId, threadType, verified, respond, retain, passiveGroup, outbound, optedOut, takeover, stopped, running, revision, expiresAtMs`. Global and account STOP are separate monotonic-revision mutations under the same lock.
- `readSnapshot` is a **read-only frozen point-in-time value**, not an authorization to dispatch. Use fresh time/expiry and exact identity each call; do not cache beyond its revision/expiry. A2 retention replay must inspect new snapshot independently at each write gate.
- `dispatch` reserves and **commits** the idempotency attempt before any external initiation, then obtains a fresh policy under `BEGIN IMMEDIATE`, checks global/account/thread STOP, and initiates transport synchronously while that writer lock is held. STOP committed earlier denies; already admitted operations may complete later. If COMMIT fails after initiation, durable reservation still prevents retry. Provider deferred-initiation behavior remains a Work verification gate.
- All scopes default deny for missing/mismatched/expired records, including group sender identity. A2 must not use an independent `policyWriter` and must not modify A1 module.
- A2's `PrivacyConsent {verified:true, respond,retain,passiveGroup}` can be projected from this snapshot only when identity, expiry and STOP/revocation checks pass. The caller must **not** synthesize `verified:true` from `allowlist`, `bot_enabled`, account running, or source profile.

**Interface maturity:** `IMPLEMENTED_AS_SYNTHETIC_CANDIDATE / A2_CONSUMER_NOT_YET_VERIFIED`. Work owns integrated negative QA. No live binding or customer opt-in.
