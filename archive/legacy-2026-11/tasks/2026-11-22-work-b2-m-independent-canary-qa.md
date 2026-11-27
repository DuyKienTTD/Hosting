---
id: ttd-work-b2-m-independent-qa-001
type: task
status: prepared
approved_at: 2026-11-22
updated_at: 2026-11-22
sensitivity: public-redacted
owner: chatgpt-work
reviewer: chatgpt
depends_on: [ttd-hermes-gate-b-001]
---

# H6 B2-M — Independent Work security/rollback evidence review

## Mission and separation

**Work is an independent reviewer, not the canary operator.** Parallel to Codex's [B2-M isolated KVM2 startup canary](2026-11-21-hermes-gate-b-one-shot-paid-e2e.md), examine current source/design, specific KVM2 fake-ledger canary isolation proposal and expected acceptance evidence. Deliver actionable PASS/FAIL/UNKNOWN matrix, catch scope/rollback gaps **without asking Codex to rerun historical mock tests**. Work can review Codex's B2-M report after it appears, but does not claim a live pass from source-only evidence.

`FIRST_ACTION:` ACK latest Git SHA, full AGENTS.md, rules/AGENT_WORKFLOW.md §§7–10, Repository Security, PROJECT/STATE/CATALOG, agents profiles, full Gate B task and ADR-P0-003, Work B2-J merged design, ChatGPT B2-K/L reviewer, B2-L source/report/evidence and H4/H6 B2-E/G/H KVM2 isolation and rollback artifacts. Refresh GitHub HEAD before sourcing to avoid stale task/commit. Use official Docker/Linux references where interpretation changes safety.

## Work package — no runtime mutations

1. **Exact proposed B2-M topology check.** Independently derive a verification checklist from actual `h6_b2l_idle.py`, `h6_writer.py`, `one_shot.py`, `h6_ipc_auth.py` and B2-M Codex Compose/runner as files become available. Verify dedicated project/service/container and private fixture directory names; image/source hashes; all-profile Compose rendered mount sources/targets, UID/GID/caps, RO rootfs, no-new-privileges, `network_mode: none`, zero ports/external networks, no Docker socket, Guard legacy mount or real ledger/provider credential/IPC key. Any unresolved mount collision is **NO-GO for canary**, not permission to inspect sensitive contents.
2. **Permitless health state-machine and observational evidence.** Check test inputs and expected outputs: two cold starts without permit; 20 HMAC+SO_PEERCRED authorized health calls; byte, inode, device, atime/mtime/ctime invariants for *synthetic* ledger/lock; valid fake permit denied; missing/stale lock or ledger blocked, lock contention bounded; fake wrong identity/auth rejection. Health/readiness and permit/admission authority must remain separate.
3. **KVM2 rollback safety.** Prepare independent before/after inventory and exact owner-label manifest acceptance criteria. Require removal only of canary-owned resources, no Docker prune, no rollback of real ledger bytes or lock inode; production GATE A/Guard/n8n/Hermes restart/health preservation, and real ledger/lock **metadata only** unchanged. Confirm no provider API operation, actual key/permit reads, paid attempts or financial impact.
4. **Provenance and risk audit.** Mark every claim `VERIFIED_SOURCE`, `VERIFIED_OFFLINE_MOCK`, `VERIFIED_KVM2_REPORTED_BY_CODEX`, `UNKNOWN` or `BLOCKED`. Distinguish Docker Desktop tmpfs B2-L from KVM2 ext4, process crash from host power-loss and synthetic writer canary from real provider lane. Check any new unexpected external dependencies or route to paid provider; call out limits of UID0 caps0 and file bind rights. Check proposed future Hermes/n8n callback integration only as a separate dependency, do not expand B2-M.
5. **Prepare concise independent acceptance protocol:** at most five critical remaining checks, their owner and evidence path, exact STOP if data is missing, and a **conditional** `GO_FOR_REVIEW` or `NO_GO` when Codex evidence arrives. No review of real secrets or paid usage is required.

## Permissions

`ALLOWED:` public/connected GitHub **read** access, official docs, sanitized existing reports and GitHub PR comments; read new B2-M Codex report/evidence after publication, if available. If there is no B2-M code/evidence yet, complete prospective matrix and mark execution `PENDING_CODEX`, not PASS. No KVM2 access is required. If an authorized read-only KVM2 view is available independently, inspect only deployment metadata already permitted, never protected file contents, and record that evidence origin explicitly.

`WRITE_SET:` **only** `reports/2026-11-22-work-b2-m-independent-canary-qa.md` and optional `reports/evidence/2026-11-22-work-b2-m-independent-canary-qa.json` on a separate Work branch/PR. Do NOT edit any Codex source, parent GATE B task, CODEX B2-M report, STATE/CATALOG/CHANGELOG, old Work tasks, rules, original approvals or ADR. ChatGPT reviewer handles final merge/status integration.

`DO_NOT_TOUCH:` any KVM2 Docker command/Compose up/recreate/down/backup/restore; real P0 ledger/lock/permit, provider/IPC key or secret bytes/hash, OpenAI API, paid inference, real Hermes/n8n/Guard, production, DNS/firewall/ports and billing. Work must not review or merge its own PR as ChatGPT's independent decision, and must not claim Codex received this handoff.

`STOP:` on any unexpected real bind/credential, namespace/external network/public port, owner-label ambiguity, unverified rollback, access limitation or unapproved side effect. Stop unsafe action (none is authorized); finish remaining safe report sections. Do not create a competing B2-M task for Codex.

`PASS:` a source-linked independent matrix with specific observed and not-yet-observed evidence, KVM2 canary rollback and secret-isolation conditions, concise findings and explicit `GO_FOR_CHATGPT_REVIEW` or `NO_GO` solely for Codex evidence quality; live writer mount and paid provider remain **NO-GO** regardless of mock result. Show exact source SHA/PR diff and remote readback; handoff only once report is prepared. If Codex has not finished, conclude `SOURCE_QA_COMPLETE / RUNTIME_EVIDENCE_PENDING`.

`HANDOFF:` `from_agent: chatgpt-work`, `to_agent: chatgpt`, initial state `PREPARED_FOR_OWNER_FORWARD`, not SENT/ACK. ChatGPT cross-checks Codex B2-M report and Work's findings before approving any further scoped stage; no automatic live/paid authorization.
