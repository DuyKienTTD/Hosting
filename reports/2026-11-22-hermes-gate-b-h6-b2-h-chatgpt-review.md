---
id: hermes-gate-b-h6-b2-h-chatgpt-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# H6 B2-H reviewer: accept read-only preflight, block live apply, open narrow B2-I mock contract delta

**DECISION: H6_B2_H_READ_ONLY_PREFLIGHT_ACCEPTED / LIVE_INTEGRATION_NO_GO / H6_B2_I_DEADLINE_CALLBACK_MOCK_AUTHORIZED / REAL_LEDGER_APPLY_NOT_APPROVED / GATE_B_PAID_BLOCKED_PREFLIGHT.**

## Evidence and independent review

- Codex read-only KVM2 probe source at commit `564a92879d5eafa5a0e2a65637df70143f4067ce`, handoff report/evidence at [71fdd40](https://github.com/DuyKienTTD/Hosting/commit/71fdd40a363bfc70ebbb618352118eef9d925215). Reviewer fetched report and JSON evidence, inspected commit diff, parent task, ADR, workflow §§7–10 and source `bridge.py`, `h6_provider.py`, `h6_b2h_preflight.py` and Compose references. The measurements remain **VERIFIED_LIVE_REPORTED_BY_CODEX**, not independently re-probed KVM2.
- Accepted within read-only scope: existing Guard source matches historical mock, 9 containers/11 networks, GATE A and production baseline preserved, H4 backup pair byte/render match, stable ledger/lock ext4 owner 0:0 and 0700/0600 rights, Guard root UID/caps0 with legacy **single-file RO ledger bind lacking sibling lock**, Level 2 directory bind RW but currently stopped; provider key Guard-only RO; internal Guard/proxy network; proposed Compose only changes Guard and adds writer, rendered twice with stable hashes. No KVM2 service recreate, no actual ledger/key/permit contents read, no provider API or paid attempt; production HTTP was **not** probed in B2-H (Docker running/restart0 only).
- B2-H measured read-only metadata for bridge 20s poll, 5s per-call socket, n8n published workflow call timeout 30,000 ms and retry disabled, callback bearer check and rejection 401 for unauthorized; published callback validator only accepts `hermes_mock_succeeded` and `paid=false`. Guard B2-F `RESPONSE_TIMEOUT=45` is not automatically an exact wall clock upper bound for complete end-to-end work; transport connection/IPC/settlement and buffering add latency. Hermes installed source default API timeout 1,800s plus provider/model override; **actual effective end-to-end Hermes SDK deadline remains UNKNOWN**.
- A bridge 20s poll window and n8n 30s HTTP wait can time out before a valid >20s Guard completion. This is a **hazard**, not proof every >20s call fails: a future asynchronous admission-and-callback arrangement can decouple deadlines. Current mock-only callback contract cannot carry paid success unchanged; do not mislabel paid as mock. n8n bearer presence does not prove actual live bearer match/end-to-end callback auth.
- Proposed root writer directory RW bind + private IPC key is **not** live validated or authorized to apply. Compose preview mentions `TTD_H6_PROVIDER_MODE=real` but source remains hard-locked; render is not a functioning deployment. Rollback H4 is dry-run only and must not restore prior ledger bytes over committed state.
- Independent Work B2-H assurance task `tasks/2026-11-22-work-independent-b2-h-assurance.md` was found `status: prepared`, no Work report/ACK was observed at review time. Do not present parallel Work audit as complete. When it arrives, reconcile its independent findings before any live-integrated changes.

## Delegated B2-I mock-only coordination decision (§10)

`task_id: ttd-hermes-gate-b-001`; `from_agent: chatgpt`; `to_agent: codex`; `owner: codex`; `reviewer: chatgpt`; `handoff_state: PREPARED_FOR_OWNER_FORWARD`, not SENT or ACK.

**Objective:** prove a robust completion contract between fake Hermes/bridge, fake Guard and fake n8n when provider response can outlast 20s poll/30s HTTP timeout, without changing running services. Prefer **202 asynchronous acceptance + externally stored idempotent job state + separately authenticated result callback** for slow work, rather than globally inflating timeout; test this choice before adopting it. If Hermès run API cannot be used this way, present an alternative precise state-machine design.

- `FIRST_ACTION:` read and ACK latest `AGENTS.md`, full `rules/AGENT_WORKFLOW.md` §§7–10, security, `STATE.md`, `CATALOG.yaml`, `agents/codex.md`, full parent task/ADR, B2-H report/evidence and this review; confirm current Git SHA and changed files. Examine exact published n8n validator shape through sanitized existing evidence, `bridge.py`, Hermes run API interfaces, source `h6_provider.py` deadline/settlement and HMAC/mock test harness.
- `ALLOWED:` narrow `sandbox/p0-hermes-gate-a/` code for **isolated fake-data contract fixture**, fake Hermes provider delay, fake n8n handler and mock bridge adapter. Offline Linux/Docker tests; optionally dedicated isolated KVM2 mock project only after explicit B1/B2-E-style pre-up render/collision/rollback gate, but prefer offline. No actual n8n workflow changes, no production bridge/Hermes/Guard replacement, no real provider endpoints or secrets, no real ledger/permit/IPC secret.
- `TEST_DELTA:` test run durations around 5s, >20s, >30s and >45s; admission 202 and stable job/correlation ID; n8n receiving callback after original request has returned/timed out; authenticate bearer or equivalent via synthetic key, bind callback to task/job/fingerprint, strict schema, distinguish `hermes_paid_succeeded`, failure, and `outcome_unknown` from mock; reject mock-to-paid downgrade, duplicate/out-of-order callbacks, incorrect bearer, mismatched task/run/digest and replays across restart. Callback must not trigger additional paid dispatch and must never refund an uncertain reserve. Show dead-letter/reconciliation behavior if callback fails, preserving one physical provider attempt. Test exact timeout ordering including measured Hermes SDK behavior **only in a simulated/injected fake-provider run**, not provider live.
- `INVARIANTS:` no actual provider key/API, no paid inference, no real P0 ledger/permit/kill-switch changes, no live n8n/Hermes/bridge/Guard mutating action, no DNS/firewall/ports, no production impacts. Reuse H3–B2-G unaffected PASS, rerun only changed contract timing and callback validation. No auto-retry of paid intent, and no arbitrary live paid success generated by a fake callback.
- `WRITE_SET:` only minimal isolated contract/test harness and optional proposed offline workflow JSON under `sandbox/p0-hermes-gate-a/`, sanitized `reports/` and `reports/evidence/`, append results to existing task and minimal STATE/CATALOG/CHANGELOG updates. `DO_NOT_TOUCH:` original parent task metadata, ADR, production n8n SQLite or workflow, Level 2, real P0 ledger/lock and secrets.
- `STOP:` anything requiring live webhook invocation, provider request, real credential, service recreate, real ledger/permit update or unbounded timeout. Continue source-only analysis on blocker.
- `ACCEPTANCE:` source-level exact contract and state machine, reproducible fake slow-run timeline, PASS/FAIL per synthetic duration and adversarial callback test, no duplicate dispatch/settlement, proposed minimal **separate future** sandbox integration/rollback and GO/NO-GO for deadline/callback contract. Codex must push/test/remote readback and hand over ChatGPT review. No Stage B2 live deployment or paid E2E claim.

## Parallel Work review

The previously prepared Work independent audit should read this newer H2-H evidence and produce only its separated read-only report/PR. It should not duplicate Codex's B2-I code changes or change parent task. ChatGPT will reconcile both lanes and preserve the live NO-GO until the two contract and mount gates pass.

**Gate statuses:** B2-H read-only preflight complete; live integration NO_GO; deadline and callback BLOCKED; real writer mount/IPC credential not applied; paid Gate B BLOCKED_PREFLIGHT. No new provider authorization created.
