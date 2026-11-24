---
id: zalo-poc-02-s0-approved-handoff-2026-11-24
type: report
status: s0-approval-verified-handoff-prepared
updated_at: 2026-11-24
sensitivity: public-redacted
---
# ZALO-POC-02 — S0 approved offline remediation intake

**Approval:** [A0 delegated decision #7123763842](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7123763842), created 2026-11-24T06:16:27Z, author GitHub account `DuyKienTTD`. The comment expressly describes A0 delegation to the A0 Independent Advisor and `APPROVED_WITH_GATES`; it is not a signed GitHub comment personally authored by A0, not Agent ACK, and does not waive existing Hosting rules.

**Candidate source:** `vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561` (immutable baseline, 899 paths at source tree). Node `>=22.13`, pnpm pin `11.28.7` in package.json; `pnpm-lock.yaml` and `pnpm-workspace.yaml` present. pnpm v11 build-script whitelist `esbuild: true` present and MUST be reviewed; no installer/execution attempted by Coordinator. `pnpm eval` is forbidden (nonfake LLM). No verified rights to modify upstream. Hosting `main` S0 observed `d549564de52429e777c68daf9df7a93df5f22f27`, unchanged from accepted KNG-01 checkpoint; effective rules `AGENTS.md` blob `af42293a8ae7d3e864cd9f89442bc6861e85c080`, workflow `9dd6a1601e9b2a1b472f4a1ae89e9626ada05797`, security `c24d608036b11dcd3fafcaefbefa23fdb591990e`, STATE `d74e6f3e7cc8bad0192f4a025e25d70aaa83d708`, CATALOG `26e125296fd0c39d0e82d6c5438dcc1ca2d8947f`.

## Parallel owners / non-overlapping write sets

| Task | Primary owner | Purpose / handoff state | Hosting branch WRITE_SET |
|---|---|---|---|
| ZALO-POC-02-A1-SEND-GUARD | A1 | Patch fake-only send-time guards and negative queue/STOP tests / PREPARED_FOR_OWNER_FORWARD | `reports/2026-11-24-zalo-poc-02-a1-send-guard.md`; `experiments/zalo-poc-02/a1/**` |
| ZALO-POC-02-A2-DATA-PRIVACY | A2 | Patch group-origin memory isolation, storage versus response authorization and native SQLite negatives / PREPARED_FOR_OWNER_FORWARD | `reports/2026-11-24-zalo-poc-02-a2-data-privacy.md`; `experiments/zalo-poc-02/a2/**` |
| ZALO-POC-02-WORK-SANDBOX-QA | ChatGPT Work | Reproducible no-egress source/dependency sandbox, native build and tests, independent integrated QA on A1/A2 exact patches / PREPARED_FOR_OWNER_FORWARD | `reports/2026-11-24-zalo-poc-02-work-sandbox-qa.md`; `experiments/zalo-poc-02/work/**` |

**Four approved outcome gates in three parallel owner lanes:** environment and independent QA share Work owner to avoid a fourth owner for a third party unavailable; A2 owns group-memory and retention since they share ingress/privacy files; A1 owns send-time controls. Work must not author the patches it independently validates. All code changes are patches in individual isolated candidate copies, **never upstream** or Hosting main. A1/A2 start source/patch work concurrently with Work E0 sandbox preflight; Work integrated Q0 waits only for the patch artifacts, not for an arbitrary schedule.

## Acceptance and STOP

- E0: exact candidate source+lockfile; audited dependency install/lock, no untrusted project code with egress, Node/pnpm/TS versions; native build/typecheck/targeted unit tests with logs/exit codes. Offline fixtures use a single synthetic account.
- D1: X→Y group-memory read, error/no-match editing and delete denied by account+subject+group provenance; DM→group prevented; persisted SQLite/restart negative results.
- D2: `respond` and `retain` independently authorized, fail closed when unverified/revoked; no prohibited SQLite history/contact/media/cache/replay/summaries writes.
- S1: all send paths (DM/group, multipart, tool/reaction, scheduler and delayed) recheck consent/recipient ID/type, human takeover and STOP at dispatch, idempotent after replay/restart; all Fake Zalo only.
- Independent Work must test identical base+patch SHA with positive/negative/fault, publish failures and all residual UNKNOWN. Zero real outbound, zero paid provider, no other than one synthetic account; no real Zalo, QR/session/cookies, VPS/production, merge, or live launch.
- If dependency trust/network isolation, needed permission or path overlap cannot be demonstrated, STOP the unsafe action, report bounded blocker and proceed with safe reading. No automatic Codex/Hermes/Hostinger fallback.

## S0/S1/S2/S3 tracking

- **S0:** delegated decision independently fetched, main/security source pins read, candidate/test topology checked, 3 owner work orders prepared; no Agent ACK claimed.
- **S1:** each Agent actually ACKs task, validates source/runtime and starts independent safe work. As of this S0 report, `SENT=NOT_VERIFIED`, `ACK=NOT_VERIFIED`, `RUNNING=NOT_VERIFIED`.
- **S2:** A1/A2 patches with SHA and Work E0 native tests; Work then performs Q0 combined-code independent QA, not cherry-picked mock results.
- **S3:** Coordinator joins evidence/risks/cost and requests independent A0 review/decision. Even `OFFLINE_PASS` means `CANDIDATE_READY_FOR_NEXT_GATE`, not live or platform authorization.

**Next handoff:** A0/authorized sender forwards exact work-order links to A1/A2/Work chat sessions. Coordinator current GitHub/Browser access does not include a verified direct sender into those Agent conversations; preparing GitHub tasks does not dispatch them.

```yaml
PROJECT: ZALO-POC-02
APPROVAL: APPROVED_WITH_GATES_VERIFIED
CANDIDATE_SHA: 2dc09de31cd99306bc1ab18e57aa0aa872618561
WORK_ORDERS: PREPARED_3_OF_3
S0: SOURCE_PINNED
S1_ACK: NOT_VERIFIED
TEST_EXECUTION: NOT_STARTED
PLATFORM_SELECTION: NO_GO_CURRENT
REAL_ZALO: PROHIBITED
PAID_API_USD: 0
MAIN_MERGE: HOLD
NEXT_OWNER: A0_OWNER_FORWARD
```
