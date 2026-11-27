---
id: hermes-gate-b-h6-chatgpt-design-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# H6 design review — ChatGPT

**DECISION: H6_PREPARATION_ACCEPTED / ARCHITECTURE_CONDITIONALLY_ACCEPTED / SANDBOX_APPLY_NOT_APPROVED / GATE_B_PAID_BLOCKED_PREFLIGHT.**

Sources: Codex H6 [report](2026-11-22-hermes-gate-b-h6-preparation.md), [evidence](evidence/2026-11-22-ttd-hermes-gate-b-h6-preparation.json) and [commit f058c31](https://github.com/DuyKienTTD/Hosting/commit/f058c31fb59006626bda7fe47b004c4e0527177d), source code guard.py, one_shot.py and compose.yaml, H5 accepted review, task/ADR-P0-003 and AGENT_WORKFLOW §§7–9. Docker networking and bind-mount docs, Linux unix(7) SO_PEERCRED. Review is **reported-live + source-design**, not independent KVM2 runtime validation. H6 write proposal is not yet code or a tested implementation.

## Accepted H6 preparation evidence

Codex ACK'ed at 1563745. Guard remains live revision 1953a81 mock-only, Guard credential read-only and only mounted there, production HTTP 200/restart 0, 18/18 isolation reused with unchanged topology, backup Compose matches, ledger real baseline 1 historical attempt / 0 permits / kill switch ON. Guard ledger bind is a **file bind** read-only; Level 2 reasoner container is stopped but retains write-mount capability. H5 candidate on KVM2 matches its original 3,304-byte SHA-256; 723 input tokens, 600 output and USD 0.0035 reservation remain historical valid conditional evidence, not H6 transport evidence. H6 run: 0 provider calls, 0 new permits, 0 USD and 0 new paid attempts.

## Design judgment and mandatory corrections before sandbox apply

1. **Separate writer recommended**: a minimal writer with ledger directory write access, no provider secret, and `network_mode: none` (or provably equivalent no-interface/no-TCP posture). Guard is sole authorized Unix-domain socket client, no socket to bridge/Hermes/mock/production. Drop capabilities, no new privilege, readonly root FS and limit writable mounts. Use filesystem socket mode/owner/group plus authenticated peer identity (such as SO_PEERCRED with verified UID namespace mapping); container root or public socket must not imply trust. Limit message body, protocol, version and operation set; no generic JSON edit, ledger reset, permit creation or kill-switch change by request.
2. **Atomic pre-dispatch transaction**: writer validates task/idempotency/fingerprint/model, exact cap/quota and one ready owner-approved permit, and uses the same stable `.json.lock` as existing Level 2. Persist consume + reserve atomically (fsync file and directory) before positive admission response; Guard must not dispatch unless the writer acknowledged durability. Race and crash/timeout of admission must fail closed; Guard must not issue another dispatch for uncertain admission. Settlement cannot refund or re-enable unknown outcomes. Shared writer lifecycle and Level 2 concurrency must be tested even if Level 2 happens to be stopped now.
3. **File/inode correctness**: `one_shot.py` uses `os.replace` of the JSON path; Guard's present file bind may remain pinned to the prior inode. A new writer alone is insufficient if Guard reads stale state. Prove directory-based observation, writer-mediated snapshots, or another safe architecture that always resolves the current file path without giving Guard direct ledger write. Verify lock inode continuity, directory permissions and re-read of freshly replaced ledger across containers.
4. **Provider path**: exact outbound `POST /v1/responses` via allowlisted TLS-verified proxy from Guard only; no redirects, fallback, retries, tools, second requests or direct egress from Hermes/bridge. Freeze final request after enforcement and dynamic field normalization, send the SAME frozen bytes to the provider after durable admit. Validate response status/content-type, output limits, usage and response identity, handle unknown/truncated response by preserving consumed permit/reservation. No silent bypass to mock in a paid-intended state; fail-closed default and explicit mode separation.
5. **Testing and rollback**: on isolated fake ledger reproduce concurrent admission, replay, tamper, crash-before/after durable reserve, writer socket failure, old-inode/new-inode visibility, response truncation, timeout, callback auth, no-bypass and missing/restarted writer. H3/H4/H5 PASS remains historical and must be rerun only for changed code/topology. Compare rendered Compose and targeted network/mount tests before any runtime change, backup config/code, and dry-run rollback. Roll back code/containers without replacing or resetting the real ledger or consumed permits. Check production health/restarts before and after.
6. **Prepaid gate revalidation**: exact candidate digest e66603e05a4a9b0d7a4bbd7b9142a89e15e38176c2fe1fddbf3dd5764ff1a929 / 723 input tokens applies only if H6 final input-affecting bytes are equivalent. If not, freeze and recount using approved no-inference method before requesting paid permission. Verify current project, quota, pricing, P0 reserved/actual, single-use entitlement and live ledger at the moment of any future permit. H6 preparation acceptance alone is NOT live paid-route approval.

## Scope decision for business owner

**Recommend a two-stage decision, not a blanket H6 paid approval.**

- **Stage A (sandbox code + isolated mock):** accept the writer architecture with mandatory corrections above, authorize Codex to prepare source/Compose overlay and run isolated fake-data/mock tests. No touching real ledger, no service recreate, no provider operations, no paid calls or production changes. This is consistent with the current existing preparation scope.
- **Stage B (sandbox apply):** require an explicit owner approval **after** a reviewed minimal patch, code hash, rendered Compose delta, writer socket/permission layout, test evidence and actionable rollback. Limit apply to sandbox Guard + writer only; changing the real ledger write boundary and recreating services cannot be inferred from Stage A or prior Guard-only secret mount approval.
- **Stage C (paid):** separate future dispatch decision only after Stage B acceptance and revalidation of all ADR-P0-003 gates. Never retry a physical attempt. Keep global kill switch ON and one-shot scoped permit only after approval.

**Handoff:** ChatGPT reviewer decision `H6_PREPARATION_ACCEPTED`. Next owner for **Stage A code/mock preparation** Codex, but this review does not claim any new handoff was SENT or ACK'ed; business owner decides Stage B apply. Existing parent task stays `owner: codex`, `status: blocked`, `approval_scope: exactly_one_hermes_paid_attempt`, `paid_inference_approval: true`. No secret/real ledger/production/runtime change made by ChatGPT.

## Authoritative supporting docs

- https://docs.docker.com/compose/how-tos/networking
- https://docs.docker.com/reference/compose-file/container-spec/
- https://docs.docker.com/engine/storage/bind-mounts/
- https://man7.org/linux/man-pages/man7/unix.7.html
