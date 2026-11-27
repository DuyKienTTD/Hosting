---
id: ttd-work-b2-h-assurance-001
type: task
status: done
approved_at: 2026-11-22
updated_at: 2026-11-22
sensitivity: public-redacted
owner: chatgpt-work
reviewer: chatgpt
depends_on: [ttd-hermes-gate-b-001]
---

# Work parallel lane — Independent B2-H integration readiness assurance

## Purpose, scope and why Work

Owner requests accelerating Hosting through ChatGPT Work alongside Codex. **Single independent deliverable:** a cross-source, evidence-based security and integration readiness audit for Gate B stage B2-H. Codex retains exclusive authority for KVM2 implementation and live Docker/runtime changes in the parent task. Work checks claims and dependencies independently and delivers a blocker/GO matrix to ChatGPT reviewer. This is NOT a second owner or an implementation spec for Codex's task.

## Read first and provenance

Read full `README.md`, `PROJECT.md`, `STATE.md`, `CATALOG.yaml`, `AGENTS.md`, `rules/AGENT_WORKFLOW.md` §§7–10, `rules/REPOSITORY_SECURITY.md`, `agents/README.md`, entire parent task `tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md`, ADR-P0-003 and latest B2-B through B2-G reports/reviewer/evidence. ACK the current rule/task commit, verify report SHA and check newer commits first. Research official Docker (bind mounts, Compose networking, IPC root permissions, no-new-privileges), Linux SO_PEERCRED/filesystem lock and OpenAI Responses/count/project-key docs, with dated official URLs. No inference from old chat excerpts.

## Independent Work package

1. **Architecture cross-check:** ledger ownership root:root 0700/0600; stable lock inode; root writer cap_drop ALL; Guard without ledger direct bind; separate HMAC IPC file/roles; no writer network; Guard-only credential; existing proxy transport. Check exact source/Compose against documented assumptions. Flag mismatches with file/line references.
2. **Live readiness evidence matrix:** classify `VERIFIED_LIVE`, `VERIFIED_MOCK`, `DOCUMENTED`, `UNKNOWN`, `BLOCKED` for KVM2 mount/UID, backup/rollback, production n8n/Hermes, proxy routing, model permissions, final digest/input token count, P0 budget/cap and callback/deadline compatibility. Work may read available connected resources **only with pre-existing authorized read-only permissions**. Do not request credential bytes or invent access.
3. **Security and financial failure modes:** pre-dispatch durable permit/reservation; concurrent Level 2 writes, os.replace/stale inode, crash-before/after ACK, host power loss, unknown provider response, non-retry, broken TLS, certificate/hostname verification, Guard compromise/shared IPC HMAC authority, root writable-directory scope; distinguish covered mock tests from outstanding live gates.
4. **Gap minimization:** list at most five truly independent remaining checks with a specific owner, exact data/evidence needed, no redundant H3–B2-G reruns. Recommend the *smallest safe next gate*, not a blanket apply/paid authorization. Highlight any claim in STATE/task exceeding its evidence.
5. **Optional independent analysis of paid final request:** read existing sanitized frozen digest/pricing approval without calling provider or making a new token count; explain when an exact-byte recount would be necessary.

## Permissions and collaboration rules

- `owner: chatgpt-work`; `reviewer: chatgpt`; `collaborator: codex (read results, no shared writes)`.
- `ALLOWED:` public official documentation and repository research; connected read-only inspection only if Work actually has valid access; redacted analysis and source-based verification; no live side effects.
- `WRITE_SET:` **only** `reports/2026-11-22-work-b2-h-assurance.md` and optionally `reports/evidence/2026-11-22-ttd-work-b2-h-assurance.json` on a separate branch/PR if supported. Do NOT edit the parent Gate B task, `STATE.md`, `CATALOG.yaml`, `CHANGELOG.md`, code, or any existing Codex report; ChatGPT reviewer handles integration after merge.
- `DO_NOT_TOUCH:` KVM2 runtime/restarts/Compose up/down, provider/paid operations, true P0 ledger or lock reads/writes, permits, real IPC/provider secret values/hashes, n8n/Hermes production, budgets, DNS/firewall, account security settings or approval metadata.
- If browser/connector lacks any needed read permission, mark `BLOCKED_ACCESS` *only for that check* and continue other evidence-based checks. No key screenshots/pastes or new plugin installations without account-owner action.
- Prevent overlapping edit conflicts: Work analysis is separate from Codex B2-H and does not block Codex's read-only progress. Work never asserts a Codex ACK or marks B2-H PASS from draft designs.

## PASS, STOP and handoff

**PASS:** deliver one concise redacted report: executive GO/NO-GO; evidence classification matrix with links; specific code/runtime discrepancies and official citations; top five remaining gates with owners; proposed safe order. Clearly state tasks actually run and those not run. Include commit/PR and remote readback if Work GitHub access permits. Only direct evidence supports VERIFIED_LIVE.

**STOP:** immediate on requested secret, unauthorized access, real ledger interaction, paid/prod operations or scope collision; continue independent safe audit.

**HANDOFF:** `from_agent: chatgpt-work`, `to_agent: chatgpt`, initial `PREPARED_FOR_OWNER_FORWARD`. This GitHub task is **prepared, not SENT or ACKNOWLEDGED**. Open in ChatGPT Work mode and send task URL; Work must ACK with source commit and permissions when it actually starts. ChatGPT will reconcile Work and Codex reports; contradictions -> targeted verification before any live integration or paid gate.

## Final handoff and ChatGPT acceptance — 2026-11-22

**CHATGPT_WORK_QA_ACCEPTED / REPORT_MERGED / LIVE_INTEGRATION_NO_GO.** Work ACK and source/evidence audit are captured in [its independent report](../reports/2026-11-22-work-b2-h-assurance.md), source commit `b2eaf342cd58c93f812b00edd5f912293e8df2f0`. ChatGPT cross-checked with Codex B2-H `71fdd40`. PR [#1](https://github.com/DuyKienTTD/Hosting/pull/1) was merged as documentation only at `3e9ccc808286582a83e5f205e3473d9ca4d8960f`, with report remote readback PASS. GitHub refused self-APPROVE review on the connected PR author account (422); analytical acceptance was recorded as [PR comment](https://github.com/DuyKienTTD/Hosting/pull/1#issuecomment-7068246108). No claim of an independent GitHub APPROVED review is made.

**Two blockers retained:** (1) permit-required writer startup prevents safe permitless idle/health preflight, (2) bridge 20s/n8n 30s/Guard 45s + mock-only callback require isolated async contract tests. Existing parent B2-I callback fixture gate remains Codex's technical assignment. Separate source/mock-only idle startup design/test is assigned for Codex *after or in parallel if separate edit surface and no conflict*; no live mount/provisioning/recreate. Work's write-set is closed; `next_owner: chatgpt` for coordinating review, Codex for authorized technical code/mock. No real ledger/permit/provider/paid/production authorization. `GATE_B_PAID: BLOCKED_PREFLIGHT`.
