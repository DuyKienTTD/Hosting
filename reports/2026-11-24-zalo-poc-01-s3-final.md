---
id: zalo-poc-01-s3-final-2026-11-24
type: report
status: completed-no-go-for-platform-selection
updated_at: 2026-11-24
sensitivity: public-redacted
---
# ZALO-POC-01 — S2/S3 integrated offline feasibility verdict

**Date:** 2026-11-24. **Coordinator:** Chat Điều phối. **A0 directive:** ZALO-POC-01 FAST-TRACK, isolated single-account synthetic/offline PoC. **Final verdict: `NO-GO` for selecting or deploying current candidate as Personal Zalo Automation foundation.** This verdict rejects **current release/selection readiness**, not the possibility of independently approved future remediation/re-evaluation. No A0 platform-choice decision is inferred or preempted.

## 1. Exact source and receipt provenance

- **Candidate:** `vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561` (sole authorized candidate; never advanced).
- **Hosting main S0:** `d549564de52429e777c68daf9df7a93df5f22f27`; KNG-01 prior independent `MAIN_VERIFIED` retained, other HOLDs remain.
- **Coordinator S0:** [PR #51](https://github.com/DuyKienTTD/Hosting/pull/51) at `6cf2d87ca639217bdc169a222c23ff8c543e4032`, draft; includes three separate owner work orders and S0 evidence.
- **A1:** recipient own-session `TASK_ACKNOWLEDGED — ZALO-POC-01-A1-CORE`; [PR #53](https://github.com/DuyKienTTD/Hosting/pull/53), head `95f193f57f7029543880e1e9cd9ddf88e0cd92be`; [report](https://github.com/DuyKienTTD/Hosting/blob/95f193f57f7029543880e1e9cd9ddf88e0cd92be/reports/2026-11-24-zalo-poc-01-a1-core.md), blob `e9d102dfcaf6b87f32e86482483e98f349feef1e`.
- **A2:** recipient own-session `TASK_ACKNOWLEDGED — ZALO-POC-01-A2-MEMORY`; [PR #52](https://github.com/DuyKienTTD/Hosting/pull/52), head `ae5adc9f4f3875714ddb1272738b7b29e8f587b7`; [report](https://github.com/DuyKienTTD/Hosting/blob/ae5adc9f4f3875714ddb1272738b7b29e8f587b7/reports/2026-11-24-zalo-poc-01-a2-memory-kb.md), blob `fc7a7848ea7a4954638a84685742ce622897ee21`.
- **Work:** recipient own-session `TASK_ACKNOWLEDGED — ZALO-POC-01-WORK-SAFETY`; [report + reproducible fixture](https://github.com/DuyKienTTD/Hosting/blob/1660546426d33bc067d9f310932d0c506dd60096/reports/2026-11-24-zalo-poc-01-work-safety.md), blob `7291b5c953778076bd180fbe796f6d08dd646a95`; report commit `1660546426d33bc067d9f310932d0c506dd60096`. Work's review of A1/A2 remained `AWAITING_EVIDENCE` **at the time of Work's report**; Coordinator directly read both later reports and source, but does not mislabel this as independent Work re-review.
- **PR relationships:** #52 targets main; #53 is stacked on #51; Work report is a separate immutable commit. None merged.

## 2. What was actually run

A1 environment (Node v22.16.0, pnpm unavailable, checkout/dependencies missing and local Git DNS failed): read-only tool/environment checks only, **zero native project unit/build/typecheck/SQLite-restart assertions executed**.

A2 environment (Node v22.16.0, pnpm unavailable): pinned source review only; **zero project memory or KB runtime assertions executed**.

Work environment (Node v24.22.3, isolated `unshare -Urn` network namespace, cleared env, temp DATA_DIR): **5 standalone synthetic unit fixtures**, unchanged copied upstream modules; fixture SHA-256 `63137fca25596a887f4f35e930cbe91ff2e32aa6d7d11bbe578ca93522072123`. Fake Zalo API recorded `fake_attempts=2` (one message, one reaction), `real_outbound_calls=0` and `synthetic_accounts=1` for Work's fixture. The W-03 `PASS` means *the assertion reproduced the undesired behavior*, not that the privacy requirement passed.

**No real Zalo/QR/cookie/session, actual customer dataset, paid provider, VPS, production, product UI/build, upstream writes, Git main merge or network eval.** Project-wide send/no-data-loss assurances cannot be inferred from a 5-fixture subset.

## 3. Case-level evidence register

| ID | Target behavior | Actual observed evidence | Status |
|---|---|---|---|
| W-01 | Same display name, different IDs; allowlist intake | Work synthetic fixture accepted allowed ID and rejected denied ID | VERIFIED_MOCK_PASS (intake only) |
| W-02 | Group @mention/disabled behavior | Work fixture demonstrated mention/passive/listening branch and disabled-thread no-reply | VERIFIED_MOCK_PASS (limited) |
| W-03 | Do not store messages outside permitted policy | Work fixture: non-allowlisted non-mentioned group sender with passive listen and bot-disabled thread returned `respond=false,record=true` | VERIFIED_MOCK_POLICY_DEVIATION; history persistence NOT_RUN |
| W-04 | Cipher primitive | Work fixture AES-GCM synthetic roundtrip, wrong-key/tag rejection | VERIFIED_MOCK_PASS (cipher core only) |
| W-05 | Fake output isolation | Work stub recorded exactly 1 sendMessage + 1 reaction | VERIFIED_MOCK_PASS (stub only) |
| A1-01 / -02 | Build/typecheck | `pnpm`, dependency tree and checkout unavailable | BLOCKED_RUNTIME |
| A1-03 through -12 | Native tests, routing, SQLite WAL/dedup/restart/rollback and replay | Pinned test/source inventory and logic reviewed; no native execution | SOURCE_REVIEW / NOT_RUN |
| A1-13/-14 | Contact collection and remote contacts sync | Contact store and friend event logic found; full remote contact sync NOT_PROVEN | SOURCE_REVIEW / NOT_VERIFIED |
| A1-15 | Only DM thread backfill creates contacts | SQL lacks thread type condition despite comment claiming direct-chat only | SOURCE_REVIEW_RISK, runtime negative case NOT_RUN |
| A2-01 | DM-only fact not visible to group | Group SQL checks `learned_in_group=1` for user facts | SOURCE_REVIEW_GUARD, NOT_RUNTIME_VERIFIED |
| A2-02 | Group X fact cannot appear in group Y | `groupStmt` matches `subject_id=senderId AND learned_in_group=1` without `learned_in_thread_id=current_group` | SOURCE_REVIEW_FAIL_P1 |
| A2-04 | Group X fact cannot be edited/deleted from group Y | `factNhinThayTrongNhomStmt` checks learned_in_group but no source thread group | SOURCE_REVIEW_FAIL_P1 |
| A2-05 | Memory accuracy, dedup, edit and restart | SQL design present; runtime restart and provenance conflict checks not run | SOURCE_REVIEW / UNKNOWN |
| A2-06/-08 | KB binding/search/provenance | Agent binding fail-closed in source, FTS5/BM25/RRF, source metadata available internally; user-facing citations not proven | SOURCE_REVIEW / UNKNOWN |
| A2-09 | No invented prices/policy | No deterministic semantic test and no real model evaluation | MODEL_QUALITY_NOT_VERIFIED |
| W-06/-10 | Wrong recipient, queued send, late STOP/opt-out, human takeover, all-send interception | Incomplete end-to-end dependency/test harness closure | UNKNOWN / BLOCKED_RUNTIME |

**Source cross-check completed by Coordinator:** at exact candidate SHA, `src/conversation/memory-store.ts` blob `5b0bfda92887cb549ac6d784fe7690d66c98ac8d` contains the cross-group selection predicate; `src/conversation/memory-edit-store.ts` blob `7bdbd56c51bf8e868c539906218ce78db6c04de8` lacks origin-group constraint; `src/middleware/allowlist-filter.ts` blob `1046738507933c2907535c8f1172b62b6e9f81bd` returns passive recordOnly before allowlist and kill-switch checks; `src/zalo/incoming-message-router.ts` blob `02bd7dbebea7a66a0d4d1022fb28e76e16503655` calls `ghiTinDenVaoHistory` on `decision.record=true` and collects contacts before filtering; `src/conversation/contact-store.ts` blob `a270e3a56c06c53bf92d9e1c8ee74b93784c459d` has a backfill query without thread_type join. These prove **control flow / query logic**, not observed application E2E writes.

## 4. Feature inventory: works / unproven / absent in reviewed scope

**Observed working in Work's synthetic fixture only:** predicate-level allowlist for explicitly mentioned messages, group passive/disabled reply choices, AES-GCM primitive, fake send and reaction recording.

**Implemented in source but not verified at runtime in this PoC:** account/thread storage, history, WAL, dedup, replay and restart, customer memory, edit/delete, knowledge source binding, import/search and KB provenance.

**Unverified or deficient for the requested product:** group-to-group private-context isolation; group fact edit authorization; retention/consent policy on passive listening and contact auto-collection; post-queue revocation and stop-at-send; recipient-id/type validation; human takeover; actual full contact synchronization; user-facing citations; final advice accuracy; native test/build health; maintenance/operational support under unofficial Zalo API.

## 5. Prioritized risks, minimal corrections, residual gates

**P1 — source-supported privacy leak (NO-GO):** current memory query allows group-X-learned sender fact in group Y and group-origin-unbounded edit/delete. Minimum future correction (NOT authorized in this PoC): define whether group facts are group-private; if yes, constrain both context retrieval and edit/error listing to exact origin group and subject/account, account for DM/public policy explicitly, handle dedup/provenance across scopes; add one-account synthetic X→Y, Y→X, edit/delete and no-match-list negatives and test prompt injection path. Never call current behavior a proven live leak.

**P1 policy decision + potential privacy deviation:** passive group branch returns `record=true` before allowlist/disabled-thread guard, and ingress code does perform history store on `record=true`. Auto-collection also runs before allowlist. A0/product owner must decide separate permissions for `respond`, `retain`, group passive read and opt-out. If opted out or allowlist governs retention, enforce fail-closed before any history/contact write (including replay), and prove with SQLite fixtures. No assumptions about real customer consent.

**P1 safety readiness:** at final send time, consent, bot_enabled, recipient ID/type, queue cancel/scheduler and late STOP must be re-validated; comprehensive fake/stub tests required. No end-to-end verified human takeover. A thread-level intake kill switch alone does not establish immediate stop of queued messages.

**P2 contact integrity:** backfill SQL uses `HAVING COUNT(DISTINCT sender_name)=1`, not verified direct-thread type; add explicit DM type condition and single-sender-group negative fixture, with legacy unknown handling.

**P2 knowledge quality:** document imports, source binding, provenance, user-facing citation requirement and no-hallucination on unknown prices/spec/policy need one-account fixtures and separately authorized semantic test approach. MIT copyright applies to repository files with notice; **MIT is not permission to use Zalo's unofficial personal-account connection.** Reliance on `zca-js` introduces policy/protocol/lockout uncertainty. No live Zalo legal/commercial compatibility verified.

**STOP unchanged:** real Zalo, QR, session/cookie, customer data, paid LLM, production/VPS, product build, unauthorized download or installation, upstream modifications and merge remain forbidden. `pnpm eval` invokes real LLM/paid calls despite Fake Zalo API; do not run.

## 6. Illustrative remaining work estimate — NOT an execution authorization

Estimate is engineering **person-days (effort)**, not a scheduled delivery date, based on review scope and missing tests. Assumes an existing offline checkout at the exact SHA, pinned dependency cache, no-network isolation and a qualified TypeScript tester. The actual numbers require re-estimation after runnable preflight.

| Required workstream | Estimate | Prior gate |
|---|---:|---|
| Reproducible sandbox: exact source, pinned deps, deny-network/fake all-sends, test import audit | 1–3 person-days | New scoped A0 rights for dependency environment |
| Memory group read/edit/provenance correction + negative tests | 2–5 person-days | A0 approves isolated source modification; product privacy policy |
| Passive recording, contact retention and opt-out policy + tests | 1–3 person-days | Privacy decision |
| Queue/scheduler/recipient/STOP/human-takeover negative harness | 3–6 person-days | Prior no-network preflight |
| Contact backfill integrity, restart/SQLite robustness, native build/test baseline | 1–3 person-days | Runners available |
| KB/user-facing citation and truthfulness contract checks | 2–4 person-days | Synthetic business corpus |
| **Estimated total (non-additive uncertainty)** | **10–24 person-days** | Parallel work possible; no paid API authorized |

Estimate is provisional and excludes real Zalo integration validation, long-term maintenance, platform API policy/legal diligence, UI, productization and deployment. Without an official or approved personal-account API, even passing offline tests would not establish permitted commercial use.

## 7. S0–S3 milestones and decision

- **S0:** complete. Rules/main and candidate source pinned, 3 work orders prepared, PR #51 Draft, no inferred ACK.
- **S1:** complete at evidence-scope level. 3 agent recipient-side ACKs passed via owner; A1/A2 tool constraints; Work isolated fixture environment preflight.
- **S2:** complete with bounded partial results. A1 and A2 source audits, Work 5 synthetic fixture tests; full native E2E BLOCKED. A1/A2 report remote readback checked by Coordinator. Independent Work cross-review of their late-arriving reports remains UNKNOWN/AWAITING_EVIDENCE.
- **S3:** completed feasibility decision at current authorized scope. A0 required outcomes were not achieved; further implementation/fixture environment creation exceeds the current task's rights. Existing source evidence provides a high-priority confidentiality concern even before full runtime tests. No repeated parallel micro-orders authorized to chase inaccessible tooling.

```yaml
POC_ID: ZALO-POC-01
CANDIDATE_SHA: 2dc09de31cd99306bc1ab18e57aa0aa872618561
S0: COMPLETE_SOURCE_VERIFIED
S1: COMPLETE_WITH_RUNTIME_BLOCKERS
S2: COMPLETE_PARTIAL_EVIDENCE
S3: EVIDENCE_SYNTHESIS_COMPLETE
A1: PARTIAL_BLOCKED
A2: PARTIAL_BLOCKED_PRIVACY_FINDING
WORK: PARTIAL_VERIFIED_MOCK
WORK_A1_A2_CROSS_REVIEW: NOT_VERIFIED
GROUP_TO_GROUP_MEMORY_PRIVACY: SOURCE_REVIEW_FAIL_P1
PASSIVE_ALLOWLIST_RECORDING: VERIFIED_MOCK_POLICY_DEVIATION
NATIVE_BUILD_TEST: BLOCKED_RUNTIME
FULL_SAFETY_E2E: NOT_VERIFIED
VERDICT: NO_GO_FOR_CURRENT_CANDIDATE_SELECTION
A0_DECISION: PENDING
PRODUCT_EXECUTION: HOLD
REAL_ZALO: PROHIBITED
PAID_API_USD: 0
MAIN_MERGE: HOLD
```

**Coordinator recommendation to A0:** **NO-GO to select/implement current candidate as the product platform now.** Preserve this repo as a potentially remediable technical reference only. If A0 later wishes to reconsider, authorize a distinct bounded offline remediation/re-test with privacy policy and dependency sandbox, plus an official-platform legality check; such a follow-on would be **new approval**, not an auto-open roadmap or standing instruction. The final A0 owner platform-selection decision is still pending.
