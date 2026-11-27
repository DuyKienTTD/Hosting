---
id: hermes-gate-b-h6-b2-c-chatgpt-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# H6 B2-C — ChatGPT review and next bounded engineering decision

**H6_B2_C_UID_MODEL_OFFLINE_ACCEPTED / VERIFIED_OFFLINE_MOCK_REPORTED_BY_CODEX / B2_D_IPC_INTEGRATION_OFFLINE_AUTHORIZED / LIVE_APPLY_BLOCKED_UID_OR_MOUNT / PAID_GATE_B_BLOCKED_PREFLIGHT.**

## Evidence audit

- Pinned [commit bca741f](https://github.com/DuyKienTTD/Hosting/commit/bca741f16365a235fb6cd98cf6a411145aa52f4b), single commit after `fa0b2bc`, 9 changed files. New sources are `compose.h6-b2-c-fixture.yaml`, `h6_b2c_identity_test.py`, `run_h6_b2c_fixture.ps1`; remainder reports/evidence/task and status files. No changes to existing `guard.py`, `h6_writer.py`, `one_shot.py` or live Compose in this commit.
- Read source and controls, report `reports/2026-11-22-hermes-gate-b-h6-b2-c-uid-model.md`, evidence JSON, prior B2-B DAC preflight, B2-A Level 2 interop, rules §§7–10 and current task. Codex Docker Desktop evidence, not a ChatGPT-run independent Docker test or KVM2 runtime measurement.
- Accept: synthetic root:root 0700 parent + ledger/lock 0600; candidate writer UID 0 with all capability sets zero, no-new-privileges, read-only rootfs, network_mode none, rprivate isolated fake directory bind, dedicated IPC volume, no provider key/socket/docker sock; root Guard fixture client only IPC+test HMAC key. SOCK_SEQPACKET SO_PEERCRED alone accepts equal-UID peer but HMAC-SHA256 challenge, role-separated proofs, fresh nonces and exact message binding reject same-UID missing/wrong key, replay, wrong GID, wrong server proof and disallowed commands. 1/4 concurrent admissions ACK, stable lock inode and Level 2 preservation, two crash timings no ACK, replay rejected on restart, rollback keeps committed bytes. ACL-only UID 23062 does not work with root-owned lock fchmod and Level 2 atomic rename/fchmod. Evidence is scoped to Docker Desktop, not KVM2/ext4/live Guard.
- Important source distinction: new HMAC and UID-0 peer protocol are implemented in the **fixture test module only**, not the deployable `h6_writer.py` IPC `serve/call` or `guard.py` H6 client. The actual Stage A code still checks Guard_UID=23061/WRITER_UID=23062. No H6 real ledger/real provider path has been implemented. B2-C proves feasibility of a fixture prototype, not production-ready integration.
- Risk: root UID 0 with zero Linux capabilities is still root DAC owner for the expressly mounted ledger directory, so compromise can write within that mount. Keep writer without network, secret, Docker socket, privileged flags, and with minimum writable bind; IPC shared key is a bearer-style authority inside Guard and writer, not a protection against compromise of either endpoint. A separate threat model and key generation/storage/rotation policy are mandatory. Level 2 lacks parent directory fsync; its durability must not be generalized from H6 tests.

## Chosen architecture

Prefer a dedicated writer UID 0/GID 0, cap_drop ALL, no-new-privileges, network_mode none, read-only rootfs, exact ledger directory bind with rprivate and private IPC path; preserve real host root:root 0700/0600 and avoid ACL/chmod/chown experiments on live ledger. Require HMAC-SHA256 mutual challenge and exact canonical message binding IN ACTUAL GUARD/WRITER CODE, plus SO_PEERCRED and socket mount constraints. No live application decision until an exact implemented/verified change set exists. The fixture's HMAC secret is synthetic only and must never be repurposed as production IPC secret.

## Delegated next step: H6 B2-D (source/mock integration only)

- `from_agent: chatgpt`; `to_agent: codex`; `owner: codex`; `reviewer: chatgpt`; `handoff_state: PREPARED_FOR_OWNER_FORWARD` (not SENT/ACKNOWLEDGED). Keep parent task `ttd-hermes-gate-b-001`; no new task.
- `FIRST_ACTION:` Codex ACK latest `AGENTS.md`, all `rules/AGENT_WORKFLOW.md` §§7–10, security, `STATE.md`, `CATALOG.yaml`, `agents/codex.md`, complete task, ADR and B2-C report/evidence plus reviewer; read all current Guard/writer/HMAC fixture and rendered Compose source at HEAD, and inspect diff before edits.
- `OBJECTIVE:` integrate tested mutual HMAC nonce/role/request binding into deployable `guard.py` and `h6_writer.py` in a hard-disabled-by-default **mock/test mode**; provide synthetic secret injection as a read-only file to only Guard/writer, safe secret absence and invalid length rejection, bounded packets and timings, challenge uniqueness, canonical request MAC, SO_PEERCRED UID/GID as deployed, no message replay, no request/response downgrade and idempotency after crash. Maintain no generic writer operation or kill switch/permit editing and no paid dispatch; keep existing fixture-only checks for Stage A paths.
- `ALLOWED:` minimal sandbox source/test/standalone mock Compose candidate and synthetic fixtures; offline Linux/Docker or KVM2 isolated B1-style MOCK only if preflight shows no overlap and no actual ledger, provider credentials or existing service. Reuse unchanged B1/B2-A/B2-C proof; rerun just changed IPC/auth/mock source and security regressions. Write only source/tests in `sandbox/p0-hermes-gate-a/`, redacted `reports/` and `reports/evidence/`, and append task/status indexes. Never commit any actual IPC or provider secret.
- `TEST_DELTA:` real Guard and writer source with fixture keys and UID 0 root DAC on fake 0700/0600 ledger, wrong/missing/short key, same UID wrong HMAC, wrong GID correct key, absent socket, wrong server proof, stale nonce/replayed signed packet, wrong protocol version, oversized/duplicate key packet, request body rewrite, concurrent one ACK, crash before/after durable admission, Level 2 lock/rename and rollback preserving bytes; validate network/caps/mount topology via offline rendered Compose and scoped Linux fixture. All scenarios fail-closed and unchanged paid gates.
- `STOP:` KVM2 live Guard recreation, real ledger/lock/permission/permit, production, provider endpoint (including GET/count), credential read or mount, network/egress, real paid call, or uncertain IPC key protection. Stop only blocked side effects and report; no blanket runtime approval.
- `ACCEPTANCE:` minimal real source diff with deployable IPC auth (not fixture-only), targeted mock tests and evidence, complete proposed KVM2 source/overlay/secret handling, unchanged production/real ledger, exact reversible Stage B2 apply plan, risks and open gates. `H6_B2_D_CODE_MOCK_PASS` is source readiness only. ChatGPT then reviews under §10 and decides narrowly scoped future live sandbox phase; `HERMES_E2E_PAID_PASS` cannot be claimed.
- `DO_NOT_TOUCH:` current task owner/status/conditional paid scope, ADR, real ledger/lock/ACL/mode, production/Guard runtime, provider secret, real permit, global kill switch and network/firewall. 0 provider operations, paid attempts and USD in this stage.

**Decision limits:** B2-C offline accepted; B2-D source/mock authorized; B2 live KVM2 apply and Stage C paid are NOT authorized. `BLOCKED_UID_OR_MOUNT` retained for live apply until complete source/permission/backup/rollback revalidation.
