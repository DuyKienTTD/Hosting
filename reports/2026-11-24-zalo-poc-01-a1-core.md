---
id: zalo-poc-01-a1-core-report-2026-11-24
type: report
status: partial
updated_at: 2026-11-24
verified_at: 2026-11-24
sensitivity: public-redacted
---

# ZALO-POC-01 — A1 Core / Offline Feasibility Report

**TASK:** `ZALO-POC-01-A1-CORE` | **Agent:** A1 | **Actual receipt:** `TASK_ACKNOWLEDGED` in A1 chat, 2026-11-24 Asia/Ho_Chi_Minh | **Mode:** `OFFLINE_SYNTHETIC_READ_AND_TEST` | **Verdict:** **`PARTIAL_BLOCKED`** (read-only source assessment completed; repository executable tests not run). **NEXT_OWNER:** Chat Điều phối, S2/S3 synthesis. **External Agent ACK:** Not asserted.

## Source pins, authority and scope

- Hosting current main observed in S0 and A1 GitHub session: `d549564de52429e777c68daf9df7a93df5f22f27`. Coordinator S0 PR [#51](https://github.com/DuyKienTTD/Hosting/pull/51) HEAD `6cf2d87ca639217bdc169a222c23ff8c543e4032` at check.
- A1 order: [`tasks/2026-11-24-zalo-poc-01-a1-core-test.md`](https://github.com/DuyKienTTD/Hosting/blob/coordinator/zalo-poc-01-fast-track-2026-11-24/tasks/2026-11-24-zalo-poc-01-a1-core-test.md), blob `048b8d6ef013eb71fcdc18eb2651a413529a0329`.
- Upstream: [`vuhai2002/zalo-agent`](https://github.com/vuhai2002/zalo-agent/tree/2dc09de31cd99306bc1ab18e57aa0aa872618561) **exact candidate** `2dc09de31cd99306bc1ab18e57aa0aa872618561`. GitHub source content read through GitHub connector; no upstream writes or commit advancement. `package.json` blob `4f92c666d638d4fcf058822b3f2ff25d57f2058f`.
- Main rule blob IDs: `AGENTS.md af42293a8ae7d3e864cd9f89442bc6861e85c080`, `rules/AGENT_WORKFLOW.md 9dd6a1601e9b2a1b472f4a1ae89e9626ada05797`, `rules/REPOSITORY_SECURITY.md c24d608036b11dcd3fafcaefbefa23fdb591990e`, `STATE.md d74e6f3e7cc8bad0192f4a025e25d70aaa83d708`, `CATALOG.yaml 26e125296fd0c39d0e82d6c5438dcc1ca2d8947f`, `agents/a1.md e88a048b8c075db5a0c3ac0cbb810680be4b3fe5`.
- Report `WRITE_SET`: ONLY `reports/2026-11-24-zalo-poc-01-a1-core.md` on isolated `a1/zalo-poc-01-core-2026-11-24`; upstream, runtime, rules, roadmap, CATALOG, main, other Agent reports not changed.

## Real environment preflight (A1 local Linux container)

| ID | Exact read-only preflight command | Observed result / exit | Class |
|---|---|---|---|
| P01 | `node --version` | `v22.16.0`, exit 0; requirement `>=22.13` satisfied | VERIFIED_ENVIRONMENT |
| P02 | `pnpm --version` | `bash: pnpm: command not found`, exit 127 | BLOCKED_RUNTIME |
| P03 | `git --version` | `git version 2.47.3`, exit 0 | VERIFIED_ENVIRONMENT |
| P04 | `git ls-remote https://github.com/vuhai2002/zalo-agent.git HEAD` | `Could not resolve host: github.com`; no clone or source downloaded; no upstream mutation | BLOCKED_NETWORK_SOURCE_FETCH |
| P05 | `node -e "...require.resolve('tsx'),require.resolve('typescript'),require.resolve('zca-js')..."` | `tsx NOT_INSTALLED`; TypeScript available globally; `zca-js NOT_INSTALLED` | VERIFIED_ENVIRONMENT / BLOCKED_RUNTIME |
| P06 | `node -e "...require('node:sqlite').DatabaseSync..."` | `sqlite function`; Node prints experimental warning | VERIFIED_ENVIRONMENT_ONLY, NOT repo SQLite integration |
| P07 | `test -d /mnt/data/zalo-agent` | `CHECKOUT_ABSENT`; `getent hosts github.com` exit 2 | BLOCKED_RUNTIME |
| P08 | GitHub connector `fetch_file` with `ref=2dc09de...` | Pinned source successfully read, including tests and import setup | VERIFIED_SOURCE_READ |

**Preflight decision:** No `pnpm install`, no `corepack prepare/enable`, no package downloads, no GitHub Actions job, no whole-suite runner, no `pnpm eval`, no `src/index.ts`, no login/dashboard or network service. Although `corepack` binary exists, enabling pnpm could download software and is not authorized by this zero-install order. No native source tests ran. The absence of a project checkout and runtime dependencies means TypeScript build/typecheck and SQLite integration are **BLOCKED**, not FAIL and not PASS.

## Pinned source assessment and test matrix

The listed pre-existing tests are only **reviewed source**, not executed, despite their `it(...)` cases. Exact test command is `NOT_RUN` unless otherwise stated; expected assertions come from pinned test content, observed runtime remains `UNKNOWN`. All tests would require exactly one synthetic account, temporary `DATA_DIR`, no network and fake sends; the existing repository test corpus may use multiple accounts and **must not be bulk-run under this work order without case filtering**.

| Case | Code/test and fixture assessed | Expected / observed source facts | Result |
|---|---|---|---|
| A1-01 BUILD | `package.json`: `build = tsc -p tsconfig.build.json`; source blob `4f92c666...` | Build script declared; missing project deps/checkout. No exit code for build | BLOCKED_RUNTIME |
| A1-02 TYPECHECK | `typecheck = tsc --noEmit && tsc --noEmit -p web` | Script declared; cannot assert types compile | BLOCKED_RUNTIME |
| A1-03 UNIT | `test = node --import tsx --test ...`; `src/shared/test-env-setup.ts` blob `062a40e7...` | Test loader intentionally sets temp `DATA_DIR`, dummy model config, then dynamic DB imports; `tsx` unavailable. Overall suite not proven offline/network-free | SOURCE_REVIEW / BLOCKED_RUNTIME |
| A1-04 ONE-ACCOUNT routing | `src/zalo/incoming-message-router.ts` blob `02bd7dbe...`, `src/zalo/incoming-message-router.test.ts` blob `489afc78...` | Router queries account per message, parser, dedup then send receipt/contact/thread/history; test fixture defines one `ACC` and fake API; no live dispatch exercised | SOURCE_REVIEW, runtime UNKNOWN |
| A1-05 self/group/allowlist | `src/middleware/allowlist-filter.ts` blob `10467385...`, `src/middleware/allowlist-filter.test.ts` blob `e22ea647...` | Source rejects self, handles mention and passive group records; filtered senders outside allowlist are skipped in history; note contact collection occurs before `shouldRespond` — separate privacy QA | SOURCE_REVIEW, runtime UNKNOWN |
| A1-06 identities/parser | `src/zalo/zalo-message-parser.test.ts` blob `ad7bc7b8...` | Existing tests cover sender/thread/text/photo, mention, timestamp and missing raw data; no end-to-end wrong-recipient proof | SOURCE_REVIEW, runtime UNKNOWN |
| A1-07 dedup same/different | `src/conversation/khu-trung-tin-den.ts` blob `0c45d225...`, `history-store-khu-trung-tin-den.test.ts` blob `026d9bbe...` | SQL selects `account_id,thread_id` plus msg ID, fallback for old `msg_id IS NULL` uses sender and exact time. Test names cover identical, distinct ID, account/thread isolation, old rows, empty msg ID | SOURCE_REVIEW, runtime UNKNOWN |
| A1-08 WAL/persist | `src/conversation/database.ts` blob `7a3dec65...`, `database-pragma.test.ts` blob `7646bcc8...` | `new DatabaseSync(path.join(dataDir,'zalo-agent.db'))` at **module import**; `PRAGMA journal_mode=WAL`, `synchronous=NORMAL`, migrations; tests assert WAL, NORMAL and 50 rows readback | SOURCE_REVIEW, runtime UNKNOWN |
| A1-09 restart/rehydrate | DB module and `offline-replay-cursor-store.test.ts` blob `53e02d3a...` | Durable SQLite tables and cursor read functions exist. **No controlled actual process restart, kill/reopen, corrupted DB or recovery test was run** | BLOCKED_RUNTIME |
| A1-10 cursor dedup | `offline-replay-cursor-store.ts` blob `810d2f61...` | `BigInt` comparison prevents >2^53 precision loss, monotonic cursor, compare-and-delete conditional; static logic only | SOURCE_REVIEW, runtime UNKNOWN |
| A1-11 replay / lost messages | `src/zalo/offline-replay/lay-bu-cho-account.test.ts` blob `ed27cf00...`, `tiep-nhan-tin-lay-bu.test.ts` blob `ff6f0054...` | Existing synthetic WS stub `sendWs` and fixture parser/queue checks for 510/511, malformed frame, self, mention, duplicate, canceled message and old/future timestamps. No real reconnect/replay | SOURCE_REVIEW, runtime UNKNOWN |
| A1-12 transaction/rollback/corrupt | `database.ts` schema + test names screened | DB migrations/replay schema are documented, but no original-code rollback/corruption fault injection performed | BLOCKED_RUNTIME |
| A1-13 contacts activity | `contact-store.ts` blob `a270e3a5...`, `contact-store.test.ts` blob `71f5b3bc...` | `recordContactActivity` upserts by account/user, preserves nonblank name, increments message count. Tests cover delete/reappearance/search/account isolation; tests with multiple accounts **not eligible for one-account requirement** | SOURCE_REVIEW, runtime UNKNOWN |
| A1-14 friend events vs import | `friend-event-handler.ts` blob `ee08ca55...` | Friend requests tracked in pending store; `ADD/REJECT/UNDO` clears pending. **No remote full-contacts import/sync established by these functions** | SOURCE_REVIEW; remote CONTACT_SYNC = NOT_VERIFIED / NOT_IMPLEMENTED_IN_REVIEWED_PATH |
| A1-15 contact backfill negative | `contact-store.ts` `backfillContactsFromDirectMessages` | **FINDING A1-F01:** comment says only direct chat; actual SQL groups `messages` by account/thread and `HAVING COUNT(DISTINCT sender_name)=1`, **without join/filter on `threads.thread_type`**. Single-sender group thread can meet the predicate and be imported as a contact using group ID. Reproduce in safe future one-account synthetic DB; avoid treating comment as enforcement | SOURCE_REVIEW_FINDING / NOT_RUNTIME_CONFIRMED |

### A1-F01 — contact backfill may misclassify a group as a contact

- **Component:** `src/conversation/contact-store.ts`; SQL for `backfillContactsFromDirectMessages`.
- **Expected:** only private/direct threads become contact rows.
- **Observed source:** INSERT SELECT from `messages m` with `WHERE m.role='user'`, grouping `m.account_id,m.thread_id`; no `threads` join/condition. `COUNT(DISTINCT sender_name)=1` does not prove a thread is private.
- **Safe negative fixture (NOT_RUN):** one synthetic account, create group thread and one user-message row, empty contacts; call backfill; assert no `contacts.user_id = group_thread_id`. Also assert direct-thread backfill succeeds.
- **Severity/verification:** `NEEDS_TARGETED_OFFLINE_TEST`, not a proven runtime defect or live exposure; **no product-code repair permitted in this task**.
- **Proposed remediation after independent validation:** filter to proven direct `threads.thread_type` during backfill, verify legacy unknown type handling, negative tests; A0/Director must authorize separate implementation before changing upstream.

### A1-F02 — pre-response contact collection affects privacy interpretation

- **Component:** `src/zalo/incoming-message-router.ts`, `src/conversation/contact-store.ts`.
- **Observed source:** `recordContactActivity(...)` occurs **before** `shouldRespond`; therefore sender outside allowlist may still appear in contacts even when no history should be written. Source comments describe this as intentional auto-collection, so **do not classify as proven bug**.
- **Risk/gate:** privacy/retention requirement must be decided by A2 and independently assessed by Work; no blanket assertion of no storage from filtered users.

## Mandatory invariants / blockers

| Invariant | Outcome |
|---|---|
| `real_outbound_calls=0` | **VERIFIED_FOR_A1_ACTIONS**: no Zalo/API/LLM/client/test harness was invoked. Does **not** claim full product sender instrumentation |
| `synthetic_accounts=1` | **PLANNED_FIXTURE / NOT_RUN**: no account instantiated; existing reviewed fixtures with multiple accounts explicitly excluded from executable scope |
| `paid_api_usd=0` | No paid operations executed or initiated by A1; no provider invoice checked |
| No upstream write / no Hosting main merge | Maintained; only A1-owned Hosting report branch |
| `pnpm eval`, QR, `src/index.ts`, install, Docker, login | **NOT_RUN**; prohibited |
| Build/typecheck/unit/runtime SQLite tests | **BLOCKED_RUNTIME**: no checkout, no pnpm/tsx/zca-js, DNS source fetch fails |
| Wrong-recipient/opt-out/human-takeover | Work's separate safety QA; no A1 independent claims |
| Real account/consumer data | None accessed or created by A1 |

## Final A1 verdict and exact re-entry gate

**`PARTIAL_BLOCKED`**. Source inspection and environmental preflight are complete; there are **zero executed upstream test assertions** and no evidence for runtime build/typecheck PASS, SQLite restart, actual contact synchronization or safe Zalo deployment. This is not an overall project `PASS` or `NO-GO`.

**Blocked by technical environment**, not by Zalo account rights: `pnpm` and `tsx` absent, `zca-js` absent, checkout absent, GitHub DNS fails in local execution environment. Installing/downloading dependencies would violate current zero-install scope. A later offline run is permitted only in an isolated runner with **preloaded exact SHA checkout and approved dependency cache**, disconnected external network, verified fake-send interception, one synthetic account, temporary data dir, controlled import order and explicit negative cases; rerun only the missing case IDs, not a blanket eval/test suite. Preserve all earlier source evidence.

**Handoff:** Chat Điều phối can integrate this report with A2/Work at S2; A1 does not assign their status/ACK. A1-F01 should be targeted for future negative test; A1-F02 goes to privacy review. **No installation, production access, publish, external credential, paid API, merge or real Zalo action.**
