---
id: hermes-gate-b-h6-b2-e-chatgpt-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# H6 B2-E reviewer acceptance and B2-F decision

**DECISION:** `H6_B2_E_ACCEPTED / VERIFIED_KVM2_MOCK_REPORTED_BY_CODEX / ROLLBACK_PASS`; `H6_B2_F_REAL_PATH_SOURCE_MOCK_AUTHORIZED`; `REAL_LEDGER_APPLY_NOT_APPROVED`; `GATE_B_PAID_BLOCKED_PREFLIGHT`.

## Review scope and provenance

- Source baseline `bf99bf42d1c9fd7cf7871b0c279c0f747e774867`; Codex final `e4269f012c5bab42f797459de35e71b4d61f9c7e`. GitHub compare shows runner and contract code plus sanitized B2-E report/evidence/task/catalog/state/changelog changes; intermediate commits fix healthcheck absence, source verification and namespace-relative no-bypass, final report acknowledges the initial failed probe and correction. No production/provider integration source modified in this change set.
- Reviewer read `sandbox/p0-hermes-gate-a/h6_b2e_rehearsal.py` (454 lines), `h6_b2e_contract.py` (92 lines), the full Codex report and JSON, existing B2-D Guard/writer/IPC and prior approval/task/ADR/workflow. Reviewer did **not** independently run KVM2 Docker. Physical runtime facts below are `VERIFIED_KVM2_MOCK_REPORTED_BY_CODEX`.
- B2-E runner pins downloaded source blobs and running images, checks all rendered service/mount/UID/network/entrypoint/healthcheck details, compares live inventory immediately before `up`, and stops on collisions. Rollback deletes only verified project-owned containers/volumes/fixture, then asserts pre/post inventory and production baseline equality.

## Results accepted at tested scope

Codex evidence: 4 services, 4 dedicated volumes, 0 networks or mount collisions; Guard/writer UID/GID 0:0, all capability sets 0, no-new-privileges, read-only rootfs, network_mode none, isolated ext4 rprivate fake ledger/lock root-only 0700/0600, read-only fake IPC key and no provider/real-ledger mounts. Signed snapshot, HMAC v2 wrong peer/key/replay/tamper/cross-request ACK denials; Level 2 adapter competing on synthetic ledger obtains one signed ACK out of four requests; two crash timings yield zero ACK/zero stub hits; mock callback uses actual bridge handler but Hermes/n8n are simulated, one authenticated webhook and no extra replay webhook. Runner removed B2-E resources, pre/post GATE A and production inventory matches, health 200/200, real ledger/lock *metadata* unchanged. No real ledger content read/hash in B2-E; real permit/provider/paid operations 0, USD0. Health/metadata evidence is not proof of byte-identical real ledger content or power-loss durability, and no claim of such direct proof is made here.

The failed initial host-side symlink probe against /var/run was fixed by checking /var/run/docker.sock and /run/docker.sock INSIDE container namespace. No repeat of unaffected B1/H5 tests is needed absent an input/topology change.

## Technical gaps

- Current `guard.py` still sets `MOCK_URL` and contains no real-provider Responses dispatch implementation. Current `h6_ipc_auth.py` and writer `--b2-d-mock` reject real provider key and require fixture-marked synthetic ledger. B2-E proves authenticated IPC mock functionality, **not** a real provider-bound transport or a real shared-ledger writer.
- A future real ledger mount requires redesigned runtime path/mount permissions including stable lock file, root-only directory access, no direct Guard ledger mount and a separately provisioned IPC key through a secure channel. Root UID zero despite cap_drop ALL still controls files within the selected writable bind.
- Real final provider-bound request may differ from H5 candidate SHA/723 input tokens; count and reserve must be revalidated on the exact final bytes. Unknown outcome must never trigger a physical retry. Actual Hermes/n8n callback and level2 restart interoperation remain untested.
- Real ledger is sensitive shared state. Test plan must use fake schema fixtures until an explicit safe live integration gate is proven; no setting the global kill switch OFF, no real permit, no provider metadata/count/inference call in the next stage. No operationally shared production stack changes.

## Delegated decision: B2-F source-level real-path integration, offline/mock only

- `task_id: ttd-hermes-gate-b-001`; `from_agent: chatgpt`; `to_agent: codex`; `owner: codex`; `reviewer: chatgpt`; `handoff_state: PREPARED_FOR_OWNER_FORWARD`. GitHub record does not prove Codex ACK.
- `FIRST_ACTION`: ACK current AGENTS, rules/AGENT_WORKFLOW.md §§7–10, repository security, STATE/CATALOG, agents/codex.md, full task and ADR-P0-003; review B2-D/E source+reports+evidence and B2-B real DAC/mount diagnosis; confirm latest code SHA and actual KVM2 baseline **read-only only if change triggers it**.
- `OBJECTIVE`: produce real-path-capable but **disabled-by-default** Guard provider transport and dedicated writer protocol for actual P0 v1 ledger schema in source. Separate mock vs future real mode by hard fail-closed configuration; never let a test fixture flag select a real ledger; never let a real provider key be used in mock mode. For future real path, require final frozen provider bytes after all policy enforcement, exact request SHA/fingerprint, scoped one-shot permit consumed and conservative reserve committed+fsynced before single physical dispatch, no redirects/retries/tools/fallback, provider response/usage settlement and authenticated Hermes/n8n callback contract. No provider request may be emitted in B2-F tests.
- `SECURITY REQUIREMENTS`: real-mode config must fail closed unless an independently reviewed secure IPC credential reference and narrowly approved ledger directory are present; do not create or use either in B2-F. Restrict real writer with SO_PEERCRED + separate HMAC domain and role/nonces/request binding, no network/provider credential, no arbitrary ledger edits, caps all dropped, readonly rootfs, exact future bind/lock semantics. Guard can read provider key only in separately approved real mode; do not embed secrets, key hashes or private paths in public Git. Do not use a single mock IPC key as production credential.
- `SOURCE/TEST SCOPE`: minimal isolated `sandbox/p0-hermes-gate-a/` source/Compose proposals and synthetically keyed mock/fault tests; dedicated B2-F offline Docker test project or B1-style separate KVM2 **mock-only** project only after full render/collision/rollback gate. Prefer offline due topology unchanged. No real provider/API (including token count/model GET), real ledger/permit, KVM2 live Guard/Level2/production recreation or permissions changes. Keep all historical H5/B1/B2-A through B2-E PASS in their original scopes; rerun changed code path only.
- `DELTA TESTS`: no accidental mock-to-real switch; real-mode missing key/ledger/permit refuses start; correct authenticated IPC and same-fingerprint reserve/dispatch with fake provider stub and mock ledger using real v1 schema (not fixture-only shortcut); concurrent/replay/malformed/cross-request ACK rejection; writer crash before/after commit and after dispatch; unknown-outcome retained/inflight; safe settlement with authentic usage structure; test n8n/Hermes fake callback contract and no double-delivery; no fallback to default `MOCK_URL`; no hidden provider request. Include tests that prove wrong/disabled modes cannot access live ledger/key.
- `PREAPPLY PROPOSAL`: compose/rendered delta for KVM2 with exact service identities, scopes, root UID 0 + cap_drop ALL and peer protocol, mount/IPC key provider design, before/after live health/ledger metadata/backup/rollback, hard STOP and data retention for unknown outcome. Propose distinct live integration gate only after source/mock result reviewed. Do not apply any real overlay now or produce real IPC secret without authorized secure mechanism.
- `WRITE_SET`: changed sandbox code/tests/overlay, sanitized `reports/` and `reports/evidence/` for results, append existing task and index STATE/CATALOG/CHANGELOG. `DO_NOT_TOUCH`: real ledger+lock, real IPC and provider key, live permit, global kill switch, production n8n/Hermes, actual Guard/Level2 runtime, firewall/ports/DNS, billing/ADR and task parent metadata.
- `ACCEPTANCE`: source code plus exact diff and hashes, reproducible deterministic offline/mock test evidence for changed transport and real-schema writer IPC, KVM2 future compose preview/rollback, remaining project/token/pricing/gate checks. If unavailable stop side effects and report blocker while completing safe work. The result can only be `B2_F_SOURCE_MOCK_PASS`, NEVER `LIVE_PROVIDER_E2E_PASS` or `HERMES_E2E_PAID_PASS` in this stage. ChatGPT reviews and makes next scoped decision under §10.

**No owner reapproval requested for this bounded source/mock phase under delegated workflow §10. Live shared-ledger mount and physical paid inference remain STOP.**
