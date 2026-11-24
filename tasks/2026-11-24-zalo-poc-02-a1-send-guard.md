---
id: zalo-poc-02-a1-send-guard-2026-11-24
type: task
status: prepared-owner-forward
dispatch_eligible: false
owner: A1
updated_at: 2026-11-24
sensitivity: public
---

# ZALO-POC-02 / A1 — Outbound safety patch (send-time control)

**TASK_ID:** `ZALO-POC-02-A1-SEND-GUARD` · **PRIMARY_OWNER:** A1. **MODE:** isolated candidate-copy coding, no live calls. **WHY A1:** prior pinned source/core audit and deterministic TS/safety contract skills; build tooling blocked in A1's last environment, so **Work** will provide independent runnable verification; no local compile PASS may be invented.

**FIRST_ACTION:** ACK; read required sources; inspect candidate `src/zalo/{send-reply-in-parts,deliver-chat-reply,message-turn-processor}.ts`, `src/scheduler/{proactive-send-queue,proactive-send-guard,scheduled-job-send}.ts`, all related `src/agent/tools/` send/reaction/attachment helpers and existing *test.ts paths. Inventory **all outbound pathways**, including multipart, delayed queued, proactive/scheduler, tool sends, attachments, reaction and technical fallback. Supply that inventory in the report; do not assume one call site.

## Binding authorization and rules
A0-delegated approval is GitHub issue comment **7123763842** on PR #51, dated 2026-11-24: https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7123763842 . Approval covers *only* offline isolated source copies/branches, dependency preparation, patch development, test execution, and evidence for ZALO-POC-02. It is not a Zalo live, product, production, paid API, upstream write, Hosting main merge or official Zalo connection approval.

FIRST read **in full** the current Hosting `main` versions of `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, your role profile, and this order. Record actual HEAD and rule blobs. S0 observed Hosting main `d549564de52429e777c68daf9df7a93df5f22f27` (historical pin, verify current). Candidate code MUST be sourced only from immutable `vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561`, with `pnpm-lock.yaml` verified before use. No other candidate/upstream version.

**Common safety:** exactly ONE synthetic account, fake contacts/chats/groups, no Zalo QR/login/cookie/session, no real user data, no outgoing Zalo, LLM or provider calls, no `pnpm eval`/`pnpm start`/`pnpm dev`/`zalo-login`, no VPS, production, ads, public listener, paid service, main merge or CodeX/Hermes/Hostinger activation. Downloads, when necessary, restricted to approved source/dependencies with checksum/lockfile validation; examine lifecycle scripts first; ensure network egress is disabled **before** executing dependency/project code. Any action not proved to be in a blocked-network sandbox must STOP. Avoid real `.env` and secrets. Expense ceiling: **0 USD**.

**Shared evidence contract:** each case ID records baseline SHA + exact patch SHA, current Node/pnpm versions, commands, exit codes, fixture hash/description, reproducible expected/observed outcome, sanitized logs and explicit test status (`VERIFIED_OFFLINE`, `VERIFIED_MOCK`, `SOURCE_REVIEW`, `BLOCKED`), zero real outbound and one synthetic account. A successful test that reproduces a privacy violation is **defect evidence**, not product PASS. Positive/negative/fault and restart/race cases matter. Stop after hard blocker with evidence; continue independent safe tasks.

**Session handoff:** owner-forward the exact GitHub task URL to the indicated Agent chat; the Agent must return `TASK_ACKNOWLEDGED` with source SHA and FIRST_ACTION. A committed work order = `PREPARED_FOR_OWNER_FORWARD`, not SENT or ACK. End with report, branch/commit, remote readback and next owner. Do not edit another Agent's file or upstream repo.

## Deliverable / exact execution design
Produce an auditable minimal patch and synthetic tests that enforce a **single late dispatch policy** on every outbound fake send: resolve account/thread/recipient ID and DM/group type, verify current opt-in/consent, opt-out, human takeover, per-thread/global STOP and account running state; fail closed if UNKNOWN, revoked or changed after queueing. Define cancellation/idempotency on queue retry, delayed work and crash/restart. Ensure a second consent/STOP check **immediately before** final Fake API call, not merely at inbound filter. Testing should capture no wrong-recipient, duplicate, post-STOP, cross-thread group target or bypass by tool/reaction/attachment sends; include revoke-mid-multipart and queued-before-STOP/sent-after-STOP cases.

Do NOT edit A2-owned privacy/memory paths, `src/zalo/incoming-message-router.ts`, `src/middleware/allowlist-filter.ts` or contact/history storage. If a true shared interface is required, expose a narrow interface specification and `BLOCKED_INTEGRATION_INPUT` to Coordinator rather than competing writes.

**Candidate modified-path ownership (inside isolated checkout):** `src/zalo/{send-reply-in-parts,deliver-chat-reply,message-turn-processor}.ts`, `src/scheduler/{proactive-send-queue,proactive-send-guard,scheduled-job-send}.ts`, outbound tool helpers under `src/agent/tools/`, and matching outbound-only tests. No modifications to upstream repository: export a unified patch, include file hashes and patch SHA. If more paths are needed, STOP and report exact conflict before editing.

**Hosting Git WRITE_SET:** `reports/2026-11-24-zalo-poc-02-a1-send-guard.md` and `experiments/zalo-poc-02/a1/**` *on A1-owned branch only*. **READ_SET:** Hosting rules, PR #51 S3, decision, pinned candidate, Work environment preflight when available. **DO_NOT_TOUCH:** Hosting main/rules/CATALOG, A2/Work artifacts, upstream/production. No feature UI/new product.

**Acceptance:** native compile/tests where runner available; else `SOURCE_PATCH_PREPARED` and Work executes verified offline isolated integration with same patch. Tests: opt-out/STOP/handoff mid-queue and mid-multipart, malformed recipient IDs/type, retry/restart, group vs DM, all 0 real sends and exactly 1 synthetic account. Human takeover is explicit authorized state, not merely `bot_enabled=false`. Document the **unverified** remaining paths, no blanket PASS.

**EVIDENCE:** patch under `experiments/zalo-poc-02/a1/`, case log in report. **NEXT_OWNER:** Work for independent negative/E2E validation, Coordinator for synthesis. Preserve prior A1 POC01 results, no rerun of unrelated tests.
