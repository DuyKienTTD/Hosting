---
id: zalo-poc-02-s2-coordinator-2026-11-24
type: report
status: s2-partial-blocked-patches-awaiting-integration
updated_at: 2026-11-24
sensitivity: public-redacted
---
# ZALO-POC-02 — S2 reconciliation and scoped corrective handoffs

**Coordinator delivery status:** `S2_PARTIAL_BLOCKED / A2_PATCH_APPLY_BLOCKED / A1_SEND_PATHS_NOT_WIRED`. This is a **bounded offline remediation in progress**, not product acceptance or S3. **Decision authority:** A0 delegated comment [#7123763842](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7123763842); base source `vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561`; Hosting main remains separate and protected.

## 1. Evidence readback, original owners preserved

| Owner | Receipt/author artifact | Remote proof and demonstrated result | Boundary |
|---|---|---|---|
| A1 | [PR #55](https://github.com/DuyKienTTD/Hosting/pull/55), head `5d6946449c5b7b9045aa7737c2f50ee749c5cb92`; report blob `328850f08647230363ebddbff0a3beed780a7303`; patch blob `b7352d2ddaab9d0cfdbebf3812c9502d5871293d` | Work independently applied A1 additive guard patch, 8/8 detached stub tests PASS | No original send path calls guard; policy source, durable store, late STOP race and actual restart not solved |
| A2 | [PR #56](https://github.com/DuyKienTTD/Hosting/pull/56), head `836d93dcf2a08357d1577e67b3c31ff88f1f8044`; report blob `9e238f5f86ac7f3bdf97c1b9c447d44effe68829`; patch blob `4674c6e1fa4385ec97986113207e7c7b413c57e5`; test blob `10bcc8eed9d87cf1b57a97435662fefe7e813d33` | Source-level candidate patch for group origin and consent; 5 SQL/contract cases authored but NOT_RUN | Work verified `git apply --check` fails on memory-store, allowlist-filter and incoming-message-router; no combined tree |
| Work | Report commit `b1f520be59353d9d0ec00e4ecd82a92478c093ac`; [report](https://github.com/DuyKienTTD/Hosting/blob/b1f520be59353d9d0ec00e4ecd82a92478c093ac/reports/2026-11-24-zalo-poc-02-work-sandbox-qa.md), blob `325329c3eef8dbbd20bb2e5cceef622a97fe2bcf`; log blob `29ca4a80f678b44a27fd2557e14e53f4499a4613` | E0 egress probe `ENETUNREACH`, pinned offline deps, native typecheck + build exit 0, 73/73 selected original tests PASS; 8/8 A1 guard tests PASS | Q0 integrated QA is `BLOCKED_PATCH_APPLY`; not whole project suite; no end-to-end privacy/STOP proof |

All three recipients reported their own `TASK_ACKNOWLEDGED` via owner-forward in actual Agent conversations. GitHub source readback is verified; Coordinator did not directly transmit messages or control Agent sessions. No new task-specific continuation ACK has yet been received after corrective comments below.

## 2. Exactly two priority blockers

**B1 — A2 patch format / context (immediate critical path).** Work's `qa.log` records combined `git apply --check` exit 1 against exact pinned source:
```text
patch failed: src/conversation/memory-store.ts:32
patch failed: src/middleware/allowlist-filter.ts:14
patch failed: src/zalo/incoming-message-router.ts:82
```
The original `privacy.patch` includes manually ordered +/- hunk lines around source contexts. Treat as **verified apply failure**, not a runtime logic verdict. A2, as sole author/owner, must regenerate clean unified patch from the exact source and supply identical altered intent, exact changed paths and independently verifiable SHA. Work applies; Coordinator does **not** modify A2's artifact.

**B2 — A1 guard only detached.** Work proved the 8 authored guard unit tests run; source inventory confirms no send callsite calls the new guard. Protecting message outputs requires final-send adapter for every path and durable SQLite-backed idempotency; two policy reads do not themselves serialize a concurrent STOP after last check. A1 retains code ownership and must wire and test the real fake-sender pathways, not claim full-system safety from a standalone test.

**Cross-owner input contract (Coordinator design decision, not runtime permission):**
- Every privacy/sending authorization query is keyed by `accountId + senderId + threadId + threadType + scope` (`respond`, `retain`, `outbound`), with verified provenance, explicit expiry/revocation and monotonic revision/fencing. Missing/unknown/expired/revoked = DENY. A `bot_enabled` bit alone does not establish consent or human takeover.
- A2 owns inbound retention decisions and group memory predicates; A1 owns outbound policy-reader adapter, send-time STOP and idempotency.
- Group memory edit tool caller `src/agent/tools/save-memory-tool.ts` needs a validated group `threadId`; this file is in A1 source-path scope; A1 must coordinate exact interface with A2 source author, without modifying A2 files.
- **No shared production consent store exists or is authorized by this contract alone.** Interface implementation/rights not proven => BLOCKED_INTEGRATION_INPUT. A2's existing router defaults to deny when missing consent; this is safe fallback, not a working application.

## 3. Corrective handoffs recorded on the original author PRs

- [A2 PR #56 corrective comment #7124437685](https://github.com/DuyKienTTD/Hosting/pull/56#issuecomment-7124437685): regenerate patch; source-aligned hunks, negative SQL/consent proof; preserve original author ownership; return revised source SHA and apply evidence.
- [A1 PR #55 corrective comment #7124438429](https://github.com/DuyKienTTD/Hosting/pull/55#issuecomment-7124438429): wire all actual send pathways, durable transactional send-attempt store, last-moment STOP coordination, and validated group thread ID caller interface; return patch and tests.
- **Status of these GitHub comments: `PREPARED_FOR_OWNER_FORWARD`**. These do not establish new A1/A2 recipient-session ACK. Owner/authorized sender must forward the comment URLs to the existing A1 and A2 chats. No new task ID or repeat research requested.

## 4. Work resumption gate (same existing task)

Work already completed E0 and accepted task `ZALO-POC-02-WORK-SANDBOX-QA`; do **not** repeat the 73 original tests solely to produce another PASS. Work Q0 may resume only on immutable revised A2 and A1 patches, all from exact upstream source and disjoint modified paths. Required QA order:
1. Hash exact patches, `git apply --check` on clean upstream; fail closed on malformed patch.
2. Apply each patch on separate clean copies, then both to a fresh identical baseline; record combined tree digest and all modified paths. Stop on conflicts.
3. Run native typecheck/build and only impacted old/new tests; verify 0 real egress and one synthetic account.
4. Test actual SQLite group X/Y read/edit/delete and consent denied persistence after restart; test actual send path wiring, wrong recipient, STOP/human takeover/opt-out post-queue including multipart/file/reaction and durable idempotency after **new process** restart; negative/fault outcomes cannot be inferred from source-only contract tests.
5. Report PASS/FAIL/BLOCKED case by case and any unresolved path or policy source. If missing consent resolver, all-inbound deny is safe but **not functional acceptance**. No product/platform PASS until the combined same-tree QA is independently verified.

**Work Q0 current state:** `AWAITING_REVISED_PATCHES`; no further Work action requiring code changes is authorized. This is a dependency wait, not a new Work order.

## 5. STOP and next delivery

- No real Zalo/QR/cookie/session, real customer data, external sends, paid APIs, production/VPS, upstream repo write, Hosting main merge or product/UI launch.
- No Codex, Hermes or Hostinger auto-activation. No increase in cost ceiling (0 USD).
- All reports preserve SOURCE_REVIEW vs VERIFIED_MOCK vs VERIFIED_OFFLINE, with exact baseline/patch evidence.
- Avoid uncontrolled parallel source edits; A1 and A2 own disjoint patch files; Work is independent verifier.

```yaml
PROJECT: ZALO-POC-02
S0: SOURCE_VERIFIED_APPROVED_WITH_GATES
S1: THREE_RECIPIENT_ACKS_REPORTED_AND_SOURCE_VERIFIED
S2: PARTIAL_BLOCKED
WORK_E0: VERIFIED_OFFLINE_73_OF_73_SELECTED_BASELINE
WORK_A1_GUARD: VERIFIED_MOCK_8_OF_8_DETACHED
A2_PATCH: FAILS_GIT_APPLY_CHECK
A1_SEND_WIRING: NOT_IMPLEMENTED_IN_PATCH
A1_PERSISTENT_IDEMPOTENCY: NOT_VERIFIED
A2_GROUP_PRIVACY_INTEGRATED: NOT_VERIFIED
COMBINED_TREE: NOT_ESTABLISHED
INDEPENDENT_INTEGRATION_QA: BLOCKED
S3: NOT_READY
NEXT_OWNER: A2_AND_A1_CORRECT_EXISTING_PATCHES
NEXT_QA_OWNER: WORK_ON_REVISED_PATCHES
A0_OFFLINE_APPROVAL: ACTIVE_SCOPE_ONLY
REAL_ZALO: PROHIBITED
MAIN_MERGE: HOLD
PLATFORM_GO: NO_GO_CURRENT
```
