---
id: zalo-poc-01-s0-readiness-2026-11-24
type: report
status: s0-source-verified-handoff-prepared
updated_at: 2026-11-24
sensitivity: public
---
# ZALO-POC-01 — S0 verified readiness and handoff

**Decision:** A0's 2026-11-24 FAST-TRACK approval covers only OFFLINE/MOCK feasibility, three parallel Agent slices and Coordinator synthesis. This is a new bounded priority decision; it does not authorize product execution, live Zalo, VPS, paid API, Codex/Hermes/Hostinger, rule changes, main merge or production.

## Source pins / authority

| Input | Exact source or status | Evidence class |
|---|---|---|
| Hosting main | `d549564de52429e777c68daf9df7a93df5f22f27` | VERIFIED_REMOTE at S0 |
| KNG-01 | `MAIN_VERIFIED` per previously accepted checkpoint; source snapshots still retain past status | ACCEPTED_HISTORICAL / NO_RERUN |
| PR #50 design | `cba933df7c3e9b642e15597019626348ecf3268e`, Draft/Open, unmerged | VERIFIED_REMOTE |
| Candidate repository | `vuhai2002/zalo-agent` ONLY | VERIFIED_REMOTE |
| Candidate main | `2dc09de31cd99306bc1ab18e57aa0aa872618561` | VERIFIED_REMOTE |
| Candidate licensing | package.json / repo declare MIT; this does not grant platform Zalo permission | DOCUMENTED |
| Personal Zalo API | `zca-js@2.3.0` unofficial | DOCUMENTED |
| Build/test runner | package.json Node>=22.13, pnpm 11.28.7 scripts; actual A1/A2/Work runtime not yet checked | DOCUMENTED / SESSION_UNKNOWN |
| Real messages / providers | 0 authorized; no live test run | NOT_RUN / HARD_STOP |

**Repository preflight:** candidate tree contains `evals/fake-zalo-api.ts`, `src/conversation/database.ts` (SQLite `node:sqlite`), `memory-store.ts`, `src/knowledge/kb-search.ts`, `src/middleware/allowlist-filter.ts`, test suites in `src/**/*.test.ts`, `web/src/**/*.test.ts`, `evals/**/*.test.ts`. These are source inventory, not behavioral PASS. Inbound allowlist and per-thread kill switch are visible at the source; the critical question whether a disabled thread can still emit an already-queued reply has NOT been tested.

**False-safe trap:** `evals/README.md` explicitly describes `pnpm eval` as real LLM model calls requiring network/API key and paid tokens. Although it injects Fake Zalo API, `pnpm eval` is forbidden by the 0 USD/no provider constraint. Unit tests must be inspected for entrypoint/import side effects and temp DATA_DIR before execution. No top-level app launch, QR login, real sessions, network install or live Zalo. All sends must be intercepted and counted, `real_outbound_calls=0`; exactly one synthetic account throughout.

## Work orders / separate writers

| Recipient | Task ID | Scope | Exclusive report WRITE_SET | State |
|---|---|---|---|---|
| A1 | ZALO-POC-01-A1-CORE | Typecheck/build, deterministic core routing, one mock account, SQLite/dedup/restart/contact-sync gap | `reports/2026-11-24-zalo-poc-01-a1-core.md` | PREPARED_FOR_OWNER_FORWARD |
| A2 | ZALO-POC-01-A2-MEMORY | Synthetic customer memory/provenance, DM/group privacy, KB import/search, no hallucinated price/policy | `reports/2026-11-24-zalo-poc-01-a2-memory-kb.md` | PREPARED_FOR_OWNER_FORWARD |
| Work | ZALO-POC-01-WORK-SAFETY | Independent safety negative/fault tests and downstream evidence review | `reports/2026-11-24-zalo-poc-01-work-safety.md` | PREPARED_FOR_OWNER_FORWARD |

Work owns safety QA and cannot rewrite A1/A2 source. A1 and A2 do not perform independent review of their own reports. No candidate upstream code changes authorized. All report artifacts will be in Hosting branches separate from `main`; sanitized public evidence only.

## Milestones (event driven)

- **S0:** pinned code/rules, preflight, work orders prepared. S0 source-only evidence complete.
- **S1:** actual recipient-session ACK plus Node/runner/fake/no-network preflight; status not claimed until evidence.
- **S2:** A1/A2/Work parallel test reports and reproducible logs; partial blockers retained without stopping other lanes.
- **S3:** cross-review and Coordinator final `PASS / CONDITIONAL / NO-GO` with critical gaps, minimal amendments, effort estimate and A0 decision request.

## Dispatch boundary / fallback

Only verified Browser connector capability in Coordinator session is tab listing/reading; it has no send-to-existing-chat or browser-control operation. No direct Agent message delivery was made. A0 should owner-forward each exact work-order URL into the recipient A1/A2/Work sessions and provide actual task ACK from each. GitHub commit/PR is `PREPARED`, not `SENT` or `ACKNOWLEDGED`. If A2 cannot execute tests, A2 completes source-grounded design/gap evidence; Coordinator may assign a separate isolated runner to A1 if current rights/ACK support it, but not the A2 owner deliverable or its authorship. If Work lacks runtime, preserve Work as independent static reviewer and escalate any unverified safety property as UNKNOWN/CONDITIONAL/NO-GO, never self-award a PASS. No Codex, Hermes or Hostinger activation.

## Initial acceptance gates

No real Zalo/message/session/QR, one synthetic account, no paid API, no raw customer data, no unauthorized output; identity and group privacy, opt-out/kill-switch, dedup/restart, KB provenance, missing/unknown product facts require case-level test/log evidence. Source inspection does NOT count as tested PASS. Any failure to prove real-send isolation is `BLOCKED_SAFETY` before executing tests; major recipient/opt-out/privacy leakage with tested evidence is candidate `NO-GO` until separately scoped remediation.

**Overall verdict:** `NOT_YET_TESTED`. No platform selection or product implementation approved.

**NEXT_OWNER:** Coordinator for recipient ACK and S1/S2 intake; A0 for manual forwarding because direct inter-session delivery is unavailable.
