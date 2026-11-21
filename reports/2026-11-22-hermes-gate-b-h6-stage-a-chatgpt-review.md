---
id: hermes-gate-b-h6-stage-a-chatgpt-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# H6 Stage A — ChatGPT source and evidence review

**Reviewer decision: H6_STAGE_A_ACCEPTED / VERIFIED_OFFLINE_MOCK (per Codex evidence) / STAGE_B_NOT_APPROVED / PAID_GATE_B_BLOCKED_PREFLIGHT.** No direct KVM2 or local Docker reexecution by ChatGPT, no paid inference.

## Inputs and change set

Pinned implementation [a411114](https://github.com/DuyKienTTD/Hosting/commit/a411114d0b485729a57d43eaf97fd2a5226d1585) and evidence handoff [5a70e3b](https://github.com/DuyKienTTD/Hosting/commit/5a70e3b253a7b2093cb513bfd18e725396d6ab8d). Compared changes against Stage A approval at cf72d4d: 11 files (5 code/overlay, 2 report/evidence, task/STATE/CATALOG/CHANGELOG). No production or runtime code deployment in these commits. Source inspected: guard.py, h6_writer.py, one_shot.py, compose.h6-stage-a.yaml, h6_stage_a_test.py; report/evidence read in full. Parent task and AGENT_WORKFLOW §§7–9 reviewed.

Codex H6 report/evidence: H6_STAGE_A_COMPLETE, eight distinct mock scenarios passed with 8 concurrent requests producing 1 mock dispatch; identity and Unix seqpacket protocol checks, exact wire/durable admission, replay/tamper rejection, before/after-commit writer death, truncated SSE/short body/timeout/redirect, authenticated mock n8n callback, isolated Linux two-container IPC and Compose offline render passed. Regression mock_contract, one_shot_linux and Level2 lock interop passed. 0 KVM2 operations, 0 real ledger/permit, 0 provider calls and USD0. These are **VERIFIED_MOCK_REPORTED_BY_CODEX**, not independent reruns.

## Source review

1. Guard H6 mode is opt-in by TTD_H6_STAGE_A_SOCKET and requires no MOCK_ONE_SHOT_LEDGER; no provider credential permitted in Stage A startup. Stage A freezes normalized payload and dispatches exact canonical bytes to MOCK_URL, after receiving writer admission ACK. It remains mock-only.
2. Writer is separate UID, SOCK_SEQPACKET, SO_PEERCRED mutual authentication, 4-KiB packet bound, limited snapshot/admit/settle protocol, mark-required mock-ledger path, no generic reset/permit creation. guard obtains current ledger state from writer, not original stale file bind. one_shot keeps stable lock-file inode and uses tempfile, fsync, atomic rename and directory fsync. Writer is not provider-aware; Stage A no-network overlay isolates it.
3. Compose H6 overlay declares mock-only three-service topology, provider-mock fixture token, no Hermes-aux or bridge service in that overlay, and writer network_mode none. This validates a narrow mock topology but DOES NOT validate the future Hermes real runtime path. Do not apply this overlay to KVM2 as an unreviewed live configuration.
4. H6 test harness simulates Hermes with fake_hermes while using the real bridge handler and fake n8n webhook. Therefore callback success is not proof of real Hermes-to-Guard interoperability under the future KVM2 configuration.
5. H6 request fixture digest differs from H5 3,304-byte candidate: H5 provider count 723 must NOT be assigned to H6 mock wire nor final future provider-bound bytes without a match/recount.
6. Runtime and code dependency remains: real provider transport, real settlement/accounting, real shared-ledger writer boundary, KVM2 mounts and UID mappings, rollback and no-bypass revalidation; no paid readiness established. The writer's mock-only fixture guard and absence of a paid route are positive Stage A limits, not defects to be bypassed.

## Boundary decision

**Stage A accepted as development and isolated mock evidence.** Stage B owner decision is separate; recommend Stage B1 only when patch/Compose rendering/rollback and UID topology are reviewed, initially sandbox mock rehearsals without real ledger/provider credential. Stage B2 (writer real ledger access and/or provider path) requires a further scoped approval after targeted evidence. Any paid dispatch is Stage C under ADR-P0-003 gates and no retry. H6 Stage A acceptance does not grant Stage B1, Stage B2 or Stage C.

Owner for engineering: Codex; ChatGPT reviewer. No new task opened, parent metadata status/owner/conditional approval unchanged. Handoff to business owner for next scope decision `NEEDS_OWNER_DECISION`; no Codex Stage B handoff SENT/ACKNOWLEDGED by this record.

References: reports/2026-11-22-hermes-gate-b-h6-stage-a.md, reports/evidence/2026-11-22-ttd-hermes-gate-b-h6-stage-a.json, task/ADR and reports/2026-11-22-hermes-gate-b-h6-chatgpt-design-review.md.
