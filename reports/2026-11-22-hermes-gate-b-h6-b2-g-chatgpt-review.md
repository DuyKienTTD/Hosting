---
id: hermes-gate-b-h6-b2-g-chatgpt-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# H6 B2-G reviewer acceptance and B2-H real integration readiness decision

**DECISION: H6_B2_G_ACCEPTED / VERIFIED_KVM2_MOCK_REPORTED_BY_CODEX / ROLLBACK_PASS / H6_B2_H_READ_ONLY_INTEGRATION_READINESS_AUTHORIZED / LIVE_APPLY_NOT_APPROVED / PAID_GATE_B_BLOCKED_PREFLIGHT.**

## Source, evidence and inference boundaries

- Compared B2-G source/evidence Git commits `5ce1018`, `fbe3fa6`, `c3c233ad9a57c07d8f753aafeccd7e7dd746e30f` and reviewed full 350-line `h6_b2g_rehearsal.py`, 363-line `h6_b2g_fixture.py`, Codex [report](2026-11-22-hermes-gate-b-h6-b2-g-kvm2-fake-tls.md), and [JSON](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-g-kvm2-fake-tls.json). Runtime tests are Codex KVM2 measurements, **not independent ChatGPT KVM2 reruns**.
- B2-G runner pins original B2-F source and B2-E baseline helper, renders all-profile standalone Compose and compares full configuration and pre-existing Docker inventory again immediately before up; verifies 4 isolated containers, two internal gateway-mode isolated bridges with 0 external networks/ports and no source mount collisions; reader/writer and fake ledger/key/certs are isolated. Runtime checks namespaces, UID 0, cap sets 0, readonly rootfs and container mounts.
- Codex evidence shows 13 mock scenarios: 13 case CONNECTs plus one denied unapproved authority, 7 posts in the positive/error-application cases (including no-retry error cases), 6 network/TLS failures before POST, and specifically **one CONNECT and one 239-byte SHA-matched POST among four concurrent admissions**. Synthetic CA cert and hostname negatives fail before post, TLS 1.3 established in valid cases, slow-drip 0.816s with timer and 9 stub chunks, redirect/timeout/SSE failure retain reserved mock budget without retry/fallback. Two responses successful, 11 fail closed. These are not 13 real provider API calls.
- Rollback evidence: no remaining B2-G containers/networks/volumes/fixture directories; existing GATE A/production inventories and production HTTP 200/200 match preflight; metadata of real ledger/lock (not contents) unchanged; no real permit/key reads/mutations, no OpenAI API calls or paid charge. Review cannot assert actual real ledger byte identity because its contents were intentionally not read.

## Distinct unverified gates

- Source `h6_provider.LIVE_ENABLED=False`; B2-G uses test-only dependency injection to fake CONNECT/TLS. No real provider endpoint, certificate chain, project key quota or provider usage was exercised.
- Live Guard remains GATE A mock and has legacy single-file ledger RO mount, not writer IPC live setup. Root-only real ledger/lock parent requires controlled writer identity+directory mount; prior B2-B `BLOCKED_UID_OR_MOUNT` is not resolved by a fake ledger. Writer root UID with cap_drop ALL has write authority over the specific bind and can be damaged by an endpoint compromise; HMAC shared key is not a defense against a fully compromised Guard.
- Real Hermes and n8n callbacks were simulated; HTTP deadline/buffered SSE compatibility with real Hermes remains unknown. H5 candidate digest/count 723 differs from the B2-G test digest (239 bytes), so provider input count and reserve must be revalidated on final bytes before any live permit.
- Root Level 2 adapter shares P0 lock but lacks containing-directory fsync; avoid changes to existing Level 2 unless independently justified and approved in scope. Power-loss behavior not proven.
- Actual live IPC key requires private provisioning outside the public Git repository; owner involvement is required ONLY if key/account/secret rights cannot be obtained securely by agents already authorized. No live credentials are to be requested or pasted in chat.

## Delegated decision — H6 B2-H read-only live integration readiness

`task_id: ttd-hermes-gate-b-001`; `from_agent: chatgpt`; `to_agent: codex`; `owner: codex`; `reviewer: chatgpt`; `handoff_state: PREPARED_FOR_OWNER_FORWARD`, not SENT/ACK. Work remains in existing task and adheres to `rules/AGENT_WORKFLOW.md` §§7–10 and ADR-P0-003.

- `FIRST_ACTION:` Codex ACK current HEAD rules §§7–10, AGENTS/security/STATE/CATALOG/Codex role, entire parent task, ADR and this report. Reconfirm Git SHA, current KVM2 read-only Docker inventory, live source hash/H4 backup and rollback/health baseline; do not repeat B2-G tests without a change trigger.
- `OBJECTIVE:` produce an exact KVM2 **read-only** integration readiness matrix and a proposed minimal, reversible sandbox-only Guard/writer/IPC/proxy change set. Account for live real P0 ledger directory+lock root:root 0700/0600, legacy single-file Guard mount removal, writer UID0/caps0 with sole ledger-directory RW rprivate bind, IPC HMAC key readable only by Guard+writer through an existing secure mechanism, network egress Guard-to-approved proxy only, writer network none, production/Hermes unaffected.
- `READ_SET:` H4 mount evidence/backup, H5 account/preflight and frozen candidate, B2-B DAC inventory, B2-D/E/G code and evidence, `h6_provider.py`, `h6_p0.py`, `h6_writer.py`, `one_shot.py`, Compose base/H4 and proposed overlay, live Guard/Level2/n8n/Hermes runtime configuration metadata (never credential bytes), proxy hostname/routing/allowlist metadata, target Hermes HTTP timeout and n8n callback auth metadata.
- `ALLOWED_NOW:` KVM2 `docker inspect`/`compose config`/file `stat`/namespace metadata and safe reachability observation which **does not contact any real provider endpoint**; source/config diff and offline rendered Compose candidate; optional offline synthetic test for newly discovered UID/mount/deadline assumption only. Private key provider exists verification can use boolean/mode metadata WITHOUT reading, hashing or copying key values. Report precise path references redacted in public Git. Do not create real IPC credential in this phase.
- `DESIGN_GATES:` root owner and stable lock inode; Level2 sharing and writer file-rename propagation; Guard only IPC, no real ledger direct mount; TLS proxy allowlist and no-bypass given planned network; provider key Guard-only; scoped permit operator + immutable H5 evidence and final-count revalidation procedure; one-shot dispatch, unknown-outcome accounting, start/stop and rollback semantics; actual target Hermes HTTP deadline with buffered SSE and authenticated callback. Every proposed Compose service/network/mount/UID/secret/source build change must be identified with exact before/after render, including hidden external references, ports and orphan risk.
- `WRITE_SET:` minimum source-only proposed overlay/validation scripts if helpful, sanitized `reports/` + `reports/evidence/`, append results to same task and minimal STATE/CATALOG/CHANGELOG. Do not modify old evidence, historical acceptance or parent task metadata.
- `DO_NOT_TOUCH:` **no live Guard/writer/Level2 recreate or start**, no real ledger or lock write, chmod/chown/ACL, no real permit, kill switch remains ON, no generation/mount of live IPC secret, no provider key reads, no real OpenAI API call (including count/model metadata), no real paid inference, no production n8n/Hermes restart or new public port/firewall/DNS.
- `PASS:` classified inventory VERIFIED_LIVE / DOCUMENTED / UNKNOWN, exact proposed overlay render+diff with no existing-service collision or unintended runtime mutation, security/secret provisioning dependency map, Level2/Guard permissions and IPC layout, Hermes/n8n timeout compatibility, rollback and preservation of durable ledger, approved final request count and realistic limit revalidation plan, explicit STOP blockers and smallest next live gate. If evidence missing, report blocker while continuing safe independent subtasks. Do not claim `LIVE_LEDGER_READY` or `HERMES_E2E_PAID_PASS`.
- `STOP:` missing privilege to read metadata, secret or key needed, unsafe Compose collision, unverified rollback, provider request requirement or actual production dependency -> stop side effect and document precise owner. Do not disable kill switch or relabel B2-G mocks as live evidence.
- `HANDOFF:` Codex report/evidence sanitized with pinned Git/run SHAs, live metadata, proposed change boundary and a precise recommendation for next gate; push/re-fetch remote then hand over to ChatGPT reviewer. Next reviewer may autonomously approve a **separately scoped** future sandbox implementation only if every risk/control is demonstrated. No blanket B2 live apply in this review.

**Status: B2-G accepted within KVM2 fake TLS. B2-H read-only preflight authorized; live ledger integration BLOCKED_UID_OR_MOUNT, paid GATE B BLOCKED_PREFLIGHT.**
