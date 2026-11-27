---
id: hermes-gate-b-h6-b2-f-chatgpt-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# H6 B2-F reviewer acceptance and B2-G isolated CONNECT/TLS decision

**DECISION: H6_B2_F_SOURCE_MOCK_ACCEPTED / VERIFIED_OFFLINE_MOCK_REPORTED_BY_CODEX / H6_B2_G_KVM2_ISOLATED_FAKE_TLS_AUTHORIZED / REAL_LEDGER_APPLY_BLOCKED_UID_OR_MOUNT / PAID_GATE_B_BLOCKED_PREFLIGHT.**

## Review and provenance

- Commit [b670a65](https://github.com/DuyKienTTD/Hosting/commit/b670a65f90ae762a8270176978cf46edb4d50b9c), added `h6_provider.py`, `h6_p0.py`, `h6_b2f_test.py`, offline Compose and modified `guard.py`, `h6_writer.py`, `h6_ipc_auth.py`, `one_shot.py`. Reviewed full Codex report and evidence and the entire source of transport and P0 transactional modules, relevant Guard paths and IPC code. Parent task/ADR/workflow §§7–10 checked. No ChatGPT-run Docker/KVM2 test; Codex evidence classification is `VERIFIED_OFFLINE_MOCK`.
- Codex recorded 13/13 offline PASS on Docker Desktop Linux. Offline source is default locked via immutable `LIVE_ENABLED = False`, and a proposed real mode cannot activate without code review. Writer enforces root-only existing ledger+lock, HMAC domain separation, 0:0 peer, durable scoped P0 v1 consume/reserve and signed acknowledgement. Guard sends frozen post-enforcement wire only on validated signed ACK and uses a one-shot HTTP path. Four requests cause one signed admit/one loopback stub POST with exact bytes; concurrent Level 2 adapter sees shared lock inode; replay/invalid scopes rejected. JSON/SSE usage and idempotent settlement, HTTP failures/redirect/timeout/truncation/outcome_unknown, crash before and after fsync, callback fake and regressions PASS according to evidence.
- Architectural strength: source includes real TLS CONNECT design through pinned proxy+provider host; no redirects/retries/fallback, reservation persists on ambiguous outcome; real provider key is Guard-only by design; writer remains no-network.
- **Remaining gaps:** `connect_live()` TLS CONNECT to a genuine proxy has NOT been executed. The offline test uses injected fake/loopback transport, not a real TLS certificate/hostname chain or actual KVM2 proxy route. The fixture's 723 input tokens and USD 0.0035 reservation are test inputs and cannot be promoted to production final-count approval. Actual host mount/UID and IPC production secret provisioning are not approved. Hermes and n8n in callback tests are simulated. No real credential, permit, provider request or ledger operation has happened.
- `h6_p0.require_ready` expects a pre-authorized scoped permit/quote created through a separate approved process; current source neither creates a valid live permit nor independently attests the owner-approved `approval_sha256` against a trusted immutable account record. This separation must be verified at the later real-permit gate, not bypassed with a fixture value.
- `h6_provider.Lane.run` uses a 45-second response transport deadline before authenticated settlement; verify future Hermes/bridge deadline compatibility, especially streamed SSE buffering. Response may represent outcome_unknown even if provider accepted the single request; never retry physical dispatch, refund unknown spend or rearm the permit.
- Local 13/13 is NOT a KVM2 TLS E2E, provider success, real shared-ledger acceptance or paid Hermes E2E.

## Delegated next action — H6 B2-G: isolated KVM2 TLS CONNECT mock

`owner: codex`, `reviewer: chatgpt`, `from_agent: chatgpt`, `to_agent: codex`, `handoff_state: PREPARED_FOR_OWNER_FORWARD` (not SENT or ACKNOWLEDGED). No new task, existing `ttd-hermes-gate-b-001`.

- `FIRST_ACTION:` ACK latest AGENTS.md, rules/AGENT_WORKFLOW.md §§7–10, repository security, STATE.md/CATALOG.yaml, agents/codex.md, full parent task, ADR-P0-003, B2-F source/report/evidence and this review. Recheck exact Git source/diff, KVM2 read-only Compose inventory/baseline and prior B2-E rollback identity before starting any container.
- `OBJECTIVE:` exercise the changed provider CONNECT/TLS transport on KVM2 Linux through an ISOLATED fake CONNECT proxy and fake TLS provider with locally generated short-lived CA/cert. Reuse real `post_once` implementation via injected fake-only connection configuration; never set `LIVE_ENABLED=True` in any deployable code, never point at genuine provider, never use actual provider key. Include isolated fake P0 v1 ledger and separate mock-only IPC secret, writer and Guard test actors as necessary.
- `PRE_UP_GATE:` enumerate rendered all-profile Compose, unique project/container/volume/network/bind names, no external networks/public ports, no mount collision with GATE A/production, no real provider egress, no existing H4 credential/ledger/lock/IPC source. Pin image/source hashes, mock endpoint names and fixture certificate paths; verify backup/rollback. Separate internal test network between test Guard and fake proxy/provider; writer `network_mode: none`. Any need to join existing `provider-egress` or production network is a STOP, not an exception.
- `ALLOWED:` create/start/stop/remove only dedicated isolated B2-G mock containers/volumes/networks and synthetic private fixture directory on KVM2 after render isolation PASS. Create ephemeral test-only certificates and keys OUTSIDE public Git and delete solely verified fixture artifacts on safe teardown. Test only with fake authentication strings, synthetic ledger and no provider operations of any kind.
- `TEST_DELTA:` one CONNECT tunnel + exactly one POST with exact frozen bytes and validated local CA/hostname, wrong CA, wrong hostname, expired/invalid cert, proxy CONNECT reject, proxy drop, TLS handshake timeout, redirect status, slow-drip response deadline, malformed/chunked SSE, body truncation, no retry/fallback and ambiguous usage settlement fail-closed. Exercise one-shot concurrency and durable reserve only when changed wire/transport coupling requires it; reuse already validated B2-A through B2-F unchanged ledger/code tests. Add no-bypass checks for this **new** isolated test network, not an unspecific six-probe ritual.
- `INVARIANTS:` live Guard/GATE A/n8n/Hermes and production health/restarts unchanged, real ledger/lock/permit/kill switch unchanged, no provider key touched/read/hash/mounted, zero OpenAI endpoints called (including GET models and input_tokens), zero physical paid attempts, USD0. Check real ledger metadata read-only and Docker inventory/production baseline before and after without reading protected bytes.
- `ROLLBACK:` teardown only exact B2-G-owned resources verified by labels/source paths; do not remove other stacks or restore a stale ledger over any committed transaction. If resource ownership ambiguous, isolate and report instead of deleting.
- `WRITE_SET:` minimal sandbox-only test runner/Compose/test fake cert generator (no secret content) under `sandbox/p0-hermes-gate-a/`, redacted `reports/` and `reports/evidence/`, append Stage B2-G outcome to existing task and minimal STATE/CATALOG/CHANGELOG updates after actual execution.
- `DO_NOT_TOUCH:` real P0 shared ledger/lock, live owner/mode/ACL, real permit and IPC credential, real OpenAI API/guard provider key, live Guard/Level2 or production Docker, firewall/public ports/DNS, original ADR and task metadata. No build-unlock or actual paid dispatch.
- `STOP:` any render collision, trust-chain bypass, real egress, secret exposure, unproven rollback, budget or production drift; do not elevate unverified TLS mock into provider permission. Continue safe independent source analysis on blocker.
- `ACCEPTANCE:` exact mock KVM2 rendered Compose and source hashes, local fake CA/cert validation and negative cases, one CONNECT/POST, no retry, one-shot state preserved on unknown response, no-bypass, rollback plus production/real-ledger invariants, sanitized remote Git evidence. Report PASS/FAIL/BLOCKED; ChatGPT independently reviews and decides next narrow technical gate. No live real ledger/provider or paid E2E claim.

**Status boundary:** B2-F accepted as source/mock. B2-G KVM2 isolated fake TLS authorized. Real shared-ledger apply remains `BLOCKED_UID_OR_MOUNT`, paid GATE B remains `BLOCKED_PREFLIGHT`.
