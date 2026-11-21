---
id: work-b2-j-chatgpt-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-work-b2-j-idle-startup-001
owner: chatgpt
---

# ChatGPT review — Work B2-J idle writer audit and Stage B2-L decision

**WORK_B2_J_SOURCE_DESIGN_ACCEPTED / PR_2_MERGED / B2_L_WRITER_IDLE_SOURCE_MOCK_AUTHORIZED / LIVE_INTEGRATION_NO_GO / PAID_GATE_B_BLOCKED_PREFLIGHT.**

## Evidence and scope

- Reviewed Work [PR #2](https://github.com/DuyKienTTD/Hosting/pull/2) at `65aa1905c0694868f2310c96732e50f9e61fc001`. One added 108-line report `reports/2026-11-22-work-b2-j-idle-startup-audit.md`, blob SHA `7b84a1037cc8d0eb8af35b3f63b33aa4fbb2c639`. Report read fully and compared with existing `h6_writer.py`, `h6_provider.py`, `h6_p0.py`, Guard and Level 2 source and B2-I report/evidence at `8ded770`. GitHub main changed by unrelated B2-I reviewer/index only since PR base, so report-only merge was safe. PR #2 merged `0d8c0f662dee4b203181cd3c0a73b69a928b1984` and remote report blob readback matched. The linked account is the PR author: GitHub cannot allow self-APPROVE; the reviewer posted [analytical acceptance comment](https://github.com/DuyKienTTD/Hosting/pull/2#issuecomment-7068619598) instead. Merge is documentation, not live/paid approval.
- Work found `serve_live_writer()` presently calls `require_ready` **before** it listens on HMAC IPC. A writer cannot independently be checked idle without a permit, even when Guard needs snapshot and there is no paid operation. Source design proposes separation of process liveness, read-only security/ledger readiness and permission for one scoped admission.
- Work designed `DISABLED`, `IDLE_NO_PERMIT`, `READY_PERMIT_VERIFIED`, `ADMISSION_COMMITTED`, `OUTCOME_UNKNOWN`, `SETTLED`, `BLOCKED` with blocked security prioritized and an independent startup-only capability fence. Its read-only authenticated status must not create/rename a ledger/lock, consume/extend permit, leak counts or credentials, or dispatch. Lock contention -> bounded unavailable, not a stale authorization. Health is not a grant to accept work.
- Work supplied a six-crash-window synthetic test matrix including `os.replace` after rename before directory fsync as an uncertain-durability fence, ACK loss and post-dispatch unknown; preserve consumed permit and budget, no paid resend or automatic rollback of ledger bytes. Work did **not** execute code/mock/KVM2 tests and does not prove host power-loss tolerance. Level 2 lacks parent-directory fsync; do not touch it or use its health endpoint to prove an immutable ledger.
- Prior B2-I `H6_B2_I_ASYNC_CONTRACT_MOCK_ACCEPTED` and independently scoped B2-K adapter cross-service mock remain valid; a successful async callback fixture does not prove writer startup.

## Delegated §10 direction — B2-L permitless writer startup source and fixture

**`from_agent: chatgpt`; `to_agent: codex`; `owner: codex`; `reviewer: chatgpt`; `handoff_state: PREPARED_FOR_OWNER_FORWARD` (not SENT/ACK).** No new top-level GATE B task. B2-K already authorized and independent; to avoid competing writes to parent task/STATE/CATALOG, Codex should execute B2-L in a separate isolated branch or sequence commits with freshly fetched blob SHAs, not concurrently edit shared coordination files. Keep B2-K isolated to `h6_b2k_*`; B2-L may change `h6_writer.py`, `h6_p0.py`, `h6_ipc_auth.py`, `one_shot.py` as minimally needed. Do not change existing Guard live config or old test baselines.

- `FIRST_ACTION:` ACK latest `AGENTS.md`, full `rules/AGENT_WORKFLOW.md` §§7–10, `rules/REPOSITORY_SECURITY.md`, STATE/CATALOG, Codex profile, parent task/ADR, exact Work B2-J report/ChatGPT decision, B2-I and existing B2-K handoff. Confirm pinned source hashes/diff and prove no concurrent edits to the same files.
- `OBJECTIVE:` in strictly disabled provider/test fixture mode, allow root UID writer to bind IPC and serve **read-only status** on valid fake ledger/lock while zero usable permit exists; admission must fail closed at all times in startup-only mode, even with a valid fixture permit. Real paid transport remains hard-disabled. Move permit/scope/time/amount eligibility checks into atomic admission under the stable lock, not a reusable health proof; retain mutual SO_PEERCRED/HMAC, byte-binding, one-shot reserve and durable ACK semantics.
- `HEALTH CONTRACT:` strict versioned, authenticated IPC op; enum-only sanitized result; no credential/permit/body/digest or counters; use O_NOFOLLOW, no O_CREAT, no file writes, no lock inode replacement, bounded shared lock and path-fstat consistency. No preexisting ledger/lock -> BLOCKED, not auto-create. A blocked or unavailable status cannot be treated as healthy or admission-ready.
- `ALLOWED:` minimal source and tests under `sandbox/p0-hermes-gate-a/` and standalone fake Unix socket/ledger/permit/IPC secrets. Offline Linux/Docker tests on synthetic root:root 0700/0600 fixture, no actual KVM2 live compose/restart, real provider/ledger/permit/key, production or paid operations. Compose offline render only if needed.
- `TEST_DELTA:` cold start/restart without permit, 20 read-only health calls with byte/inode/attempt/reserve equality, absent/malformed ledger or lock, valid/expired/consumed/scope-wrong fixture permit, wrong UID/GID/HMAC and replay, lock contention and stale inode, 4 simultaneous admissions with exactly one signed ACK and a single fake POST **only in a separate eligible mock admission mode**, startup-only always 0 dispatch; crash before rename, after rename before dir fsync, after fsync before ACK, after ACK before fake POST, after fake POST before settlement and after settlement before ACK; restart never repeats provider dispatch. For dir fsync faults, do not claim real power-loss guarantee.
- `INVARIANTS:` keep permit budget limits, 0 real P0 ledger/permit/credential access or mutation, global live kill switch unchanged, 0 real provider/API/paid attempts and USD0, no production/KVM2 runtime writes. If an existing mock fixture must be updated for changed source, rerun ONLY triggered Stage A/B2-A/B2-D/B2-F regressions and note triggers; do not rerun untouched TLS/callback suites.
- `WRITE_SET:` minimal writer/P0/IPC source + dedicated B2-L tests, redacted `reports/2026-11-22-hermes-gate-b-h6-b2-l-idle-writer.md` and `reports/evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-l-idle-writer.json`; append parent task and update STATE/CATALOG/CHANGELOG after tests only. Do not edit Work report/task, ADR, original task metadata, GATE A/production code.
- `STOP:` real permit mint/consume, real ledger mount/write/read, real credential, provider call, KVM2 live `up`, production mutation or unsafe shared file edit collision. Report blockers while continuing safe code analysis.
- `ACCEPTANCE:` actual source implementation (not only document), reproducible mock test matrix with exact bytes/inode/counters/fault timing, protected status endpoint and no side effects, future smallest isolated KVM2 fake-ledger canary proposal and rollback manifest. ChatGPT independently reviews before ANY KVM2 live mount/apply. `B2_L_SOURCE_MOCK_PASS` only; never infer paid E2E.
- `DEPENDENCIES:` B2-K cross-service mock is separate and does not block B2-L code fixture unless it changes an interface contract; if so submit change and review diff before integrating. When both pass, ChatGPT will combine B2-K/B2-L readiness for next narrow mock canary, not automatically authorize provider.

**No live approval:** `LIVE_INTEGRATION_NO_GO / REAL_LEDGER_BLOCKED_UID_OR_MOUNT / GATE_B_PAID_BLOCKED_PREFLIGHT`.
