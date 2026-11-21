---
id: hermes-gate-b-h6-b2-i-chatgpt-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# H6 B2-I reviewer — isolated async contract accepted; next B2-K source/mock gate

**REVIEW DECISION:** `H6_B2_I_ASYNC_CONTRACT_MOCK_ACCEPTED / VERIFIED_OFFLINE_MOCK_REPORTED_BY_CODEX / LIVE_INTEGRATION_NO_GO / PAID_GATE_B_BLOCKED_PREFLIGHT`.

**NEXT DELEGATED DECISION (§10):** `H6_B2_K_CROSS_SERVICE_ADAPTER_OFFLINE_AUTHORIZED`, without any KVM2 live apply, production n8n/Hermes modifications, actual ledger/key/permit or provider paid operations.

## Evidence and source review

- Read full B2-I Codex report and JSON evidence from pinned commit [8ded770](https://github.com/DuyKienTTD/Hosting/commit/8ded7704ca8e72ef37cdb7a832ca9740b23e11a2), and all `sandbox/p0-hermes-gate-a/h6_b2i_async_mock.py` and `h6_b2i_async_mock_test.py`. Diff added only the two new mock-only source/test files, report/evidence and parent task/index updates, without changing production, existing Guard/provider/writer source or published n8n workflow. Verified file hashes against evidence. Measurements are Codex-run Windows Python 3.12/SQLite 3.45.1/loopback, **not independent ChatGPT reruns**.
- Accept at mock scope: POST /jobs 202 with SQLite committed admission; read-only GET status and same-envelope deduplication across restart; HMAC timestamp+exact JSON signed callback and job/task/correlation/fingerprint/outcome binding; unique receipt/settlement, bounded outbox delivery and dead-letter; no second paid dispatch on lost ACK, replay or unknown. 12/12 unit tests, 4/4 real-wall-clock simulated delays 5,21,31,46 seconds. 46-second fixture cutoff at 45s -> outcome_unknown, 0 settlement and held synthetic reserve. 8 concurrent admissions -> 1 logical job/dispatch/settlement, including redelivery after lost ACK.
- Important qualification: `paid_succeeded` is **synthetic=true fixture data**, not paid evidence. Envelope SHA is not the frozen final provider-bound request digest. One SQLite file drives both mock job and callback roles; it does not demonstrate real cross-service state synchronization, real Hermes run ID lifecycle, actual n8n callback authorization, production bridge 20s/n8n 30s/Guard 45s deadline resolution or real Hermes SDK timeout. The fixture records callback receipt after unknown; this is event receipt, **not** proof provider usage was settled. B2-J Work permitless-startup audit task is still `status: prepared` at review; no ACK/report visible.
- Reviewer did not infer true KVM2 live baseline from this offline run. Live shared-ledger mount/UID and real IPC credential remain blocked; no provider API (including count/model metadata), no paid attempt, production or real ledger/permit operations took place according to Codex evidence.

## Delegated next step — H6 B2-K cross-service adapter mock

- `task_id: ttd-hermes-gate-b-001`; `from_agent: chatgpt`; `to_agent: codex`; `owner: codex`; `reviewer: chatgpt`; `handoff_state: PREPARED_FOR_OWNER_FORWARD` (not SENT/ACK until a Codex session confirms receipt).
- `FIRST_ACTION:` acknowledge current GitHub SHA, AGENTS, complete AGENT_WORKFLOW §§7–10, security, STATE/CATALOG/Codex profile, full original task and ADR, B2-H Codex/Work reports, B2-I source/report/evidence and this review. Check for a newly delivered Work B2-J report before edits; do not presume Work B2-J is done.
- `OBJECTIVE:` prove the B2-I 202/status/HMAC-callback contract across **separate sandbox process and persistence boundaries** (adapter, simulated Hermes executor and independent callback receiver), with durable mapping job_id/task_id/correlation_id -> Hermes run ID, exact input fingerprint and one-shot state. Demonstrate restart/lost-ACK and out-of-order delivery behavior without depending on one shared SQLite DB and without changing any running service. If actual Hermes auxiliary source has a run API, inspect its current interface (and officially documented API if available); mark any unsupported run-id idempotency as BLOCKED/UNKNOWN rather than pretending a mock establishes it.
- `ALLOWED:` create separate B2-K mock-only adapter/executor/receiver test fixtures and their own disposable SQLite stores, loopback/private Docker test only; synthetic keys, fake ledger/provider data; separate standalone Compose proposal if useful. KVM2 read-only metadata checks only when a new assumption genuinely changes; **no live container startup** in this phase.
- `TEST_DELTA:` new independent data-store/process boundaries, 202 admission with stable job mapping, duplicate admission before/after restart, Hermes mock run-ID persistence and duplicate suppression, callback before/after original HTTP timeout, signed receipt after lost ACK, replay/out-of-order/mismatched fingerprint, recovery across adapter/receiver restarts, callback failed/dead-letter, unknown outcome and no retry/refund/settlement duplication. Distinguish callback redelivery from inference redelivery. Use injected clocks for fault matrix and targeted real waits only where cross-process behavior requires them; do not rerun unchanged 5/21/31/46 second tests just for confidence.
- `INVARIANTS:` all paid-sounding outcomes synthetic; one logical job -> at most one fake dispatch; no real P0 ledger or permit, no provider/key API, no production n8n/Hermes/Guard/bridge restart or workflow alteration, no public ports, no billing change. Work B2-J owns permitless startup design and writes only its separate report/PR; Codex must not alter writer startup `h6_writer.py`/`h6_p0.py` during this B2-K scope.
- `WRITE_SET:` minimum new `sandbox/p0-hermes-gate-a/h6_b2k_*` source, standalone test fixtures and sanitized `reports/2026-11-22-hermes-gate-b-h6-b2-k-cross-service.md` + `reports/evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-k-cross-service.json`; append result to the same GATE B task and minimal STATE/CATALOG/CHANGELOG indexes. No changes to Work B2-J task/report, original ADR or task metadata.
- `STOP:` any requirement for actual provider request, real permit/key/ledger, mutation of n8n published workflow, external network/public port, live Hermes/n8n/Guard recreation, or inability to prove end-to-end fake process isolation; continue safe source review and report exact blocker.
- `PASS:` reproducible tests showing disjoint SQLite ownership, run ID mapping, callback/receipt integrity and crash/restart recovery, one fake dispatch/settlement maximum, sound unknown-outcome accounting; implementation and evidence SHA, full mocked interface boundaries, smallest future sandbox adapter proposal with rollback, unresolved live Hermes effective deadline and actual callback credentials. Future live integrated path still NO_GO and paid GATE B remains BLOCKED_PREFLIGHT. Hand off to ChatGPT with remote Git readback.
- `PREVIOUSLY_VERIFIED:` B2-H read-only preflight, B2-F mock source, B2-G KVM2 fake TLS, B2-I 12/12 and 4/4 simulated timelines; re-run only changed code/interface delta with reason. Work B2-J remains independent and can run in parallel.

No paid dispatch authorization, real ledger mount approval, source build unlock, or production change is implied by this decision.
