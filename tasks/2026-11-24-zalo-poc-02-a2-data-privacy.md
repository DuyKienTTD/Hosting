---
id: zalo-poc-02-a2-data-privacy-2026-11-24
type: task
status: prepared-owner-forward
dispatch_eligible: false
owner: A2
updated_at: 2026-11-24
sensitivity: public
---

# ZALO-POC-02 / A2 — Group memory isolation + retention versus response

**TASK_ID:** `ZALO-POC-02-A2-DATA-PRIVACY`. **PRIMARY_OWNER:** A2. **MODE:** offline isolated candidate-copy patch and fixtures. **WHY:** A2 identified precise privacy flaws in POC01; Work independently tests the patch with runnable SQLite, no A2 self-approval.

**FIRST_ACTION:** ACK; read current rules; examine pinned `src/conversation/{memory-store,memory-edit-store,history-store,contact-store}.ts`, `src/middleware/allowlist-filter.ts`, `src/zalo/incoming-message-router.ts`, pertinent tests; reproduce source predicates at exact baseline before proposing patch.

## Binding authorization and rules
A0-delegated approval is GitHub issue comment **7123763842** on PR #51, dated 2026-11-24: https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7123763842 . Approval covers *only* offline isolated source copies/branches, dependency preparation, patch development, test execution, and evidence for ZALO-POC-02. It is not a Zalo live, product, production, paid API, upstream write, Hosting main merge or official Zalo connection approval.

FIRST read **in full** the current Hosting `main` versions of `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, your role profile, and this order. Record actual HEAD and rule blobs. S0 observed Hosting main `d549564de52429e777c68daf9df7a93df5f22f27` (historical pin, verify current). Candidate code MUST be sourced only from immutable `vuhai2002/zalo-agent@2dc09de31cd99306bc1ab18e57aa0aa872618561`, with `pnpm-lock.yaml` verified before use. No other candidate/upstream version.

**Common safety:** exactly ONE synthetic account, fake contacts/chats/groups, no Zalo QR/login/cookie/session, no real user data, no outgoing Zalo, LLM or provider calls, no `pnpm eval`/`pnpm start`/`pnpm dev`/`zalo-login`, no VPS, production, ads, public listener, paid service, main merge or CodeX/Hermes/Hostinger activation. Downloads, when necessary, restricted to approved source/dependencies with checksum/lockfile validation; examine lifecycle scripts first; ensure network egress is disabled **before** executing dependency/project code. Any action not proved to be in a blocked-network sandbox must STOP. Avoid real `.env` and secrets. Expense ceiling: **0 USD**.

**Shared evidence contract:** each case ID records baseline SHA + exact patch SHA, current Node/pnpm versions, commands, exit codes, fixture hash/description, reproducible expected/observed outcome, sanitized logs and explicit test status (`VERIFIED_OFFLINE`, `VERIFIED_MOCK`, `SOURCE_REVIEW`, `BLOCKED`), zero real outbound and one synthetic account. A successful test that reproduces a privacy violation is **defect evidence**, not product PASS. Positive/negative/fault and restart/race cases matter. Stop after hard blocker with evidence; continue independent safe tasks.

**Session handoff:** owner-forward the exact GitHub task URL to the indicated Agent chat; the Agent must return `TASK_ACKNOWLEDGED` with source SHA and FIRST_ACTION. A committed work order = `PREPARED_FOR_OWNER_FORWARD`, not SENT or ACK. End with report, branch/commit, remote readback and next owner. Do not edit another Agent's file or upstream repo.

## Two separately testable deliverables, one A2 owner

**D1 Group confidentiality (P1):** confine group-sourced memory facts to origin `accountId + subjectId + learnedInThreadId=currentGroupId`; isolate DM-only knowledge from group retrieval. Apply same constraints to memory edit/delete/search/no-match suggestions and duplicate matching (so same text from independent groups does not incorrectly suppress legitimate new facts). Handle a sender in groups X/Y, sender ID collisions, missing/invalid thread type, unknown origin and restart. Default deny on ambiguous provenance, not global sharing by accident. Preserve intentional private DM recall only in authorized DM context.

**D2 data policy (P1):** separate `respond` and `retain` authorization. Group passive listening may be processed or stored only with affirmative in-scope permission; absence/withdrawal of consent must fail closed. Retention consent must govern **SQLite history, contact collection, caches, summaries, replay, message/media persistence**; tests inspect the actual temp DB to prove prohibited data is not stored. Do not merely modify a filter predicate while `incoming-message-router` still writes contacts before filter. Explicit consent and opt-out rules in synthetic fixtures; no real customer data. Avoid hidden implicit opt-in or auto-collection.

**Candidate modified-path ownership (isolated checkout ONLY):** `src/conversation/{memory-store,memory-edit-store,history-store,contact-store}.ts`, `src/middleware/allowlist-filter.ts`, `src/zalo/incoming-message-router.ts`, any matching privacy-only tests. Do not edit A1's send/queue/scheduler files or Work's harness. Interface needs outside these paths must be recorded as narrow `INTEGRATION_BLOCKER` rather than cross-writer mutation.

**Hosting Git WRITE_SET:** `reports/2026-11-24-zalo-poc-02-a2-data-privacy.md` and `experiments/zalo-poc-02/a2/**` on A2 branch only. **READ_SET:** rules and decision, POC01 A2/Work evidence, pinned upstream, Work environment preflight when available. **DO_NOT_TOUCH:** Hosting main/rules/CATALOG, A1/Work artifacts, upstream, real accounts.

**Acceptance:** (a) group-X learned fact cannot be retrieved, edited, deleted or echoed into group Y; group-Y facts remain readable in Y; (b) DM-only fact never appears in a group; (c) missing/withdrawn consent cannot persist into history/contacts/cache/replay/summaries, confirmed by native SQLite readback and restart; (d) authorized retention and response are separately testable and behave as defined; (e) no regression in one-account personal chat behavior. Positive/negative/fault tests and traceable source+patch SHA. Where runtime unavailable, mark `PATCH_READY_AWAITING_WORK_VERIFICATION`, not PASS.

**EVIDENCE:** unified patch + tests in `experiments/zalo-poc-02/a2/`, precise case register and SQL assertions in report. **NEXT_OWNER:** Work for independent integrated SQLite QA; Coordinator for decision packet.
