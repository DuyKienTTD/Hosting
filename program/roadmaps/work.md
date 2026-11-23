# ChatGPT Work — Roadmap UI, Integration & Independent Assurance

**Owner:** ChatGPT Work | **ROADMAP_STATUS:** `READY_FOR_ROADMAP_ACCEPTANCE` (roadmap integration only) | **READ_SET:** existing PR31 Work QA assignment, program docs, offline connector release evidence, current UI PR16 and relevant policy; **WRITE_SET:** own roadmap + independent UI/integration branch after task assignment; Work QA verdicts as PR comments. **STOP:** cannot control sessions, tool not present, source drift, bad provenance, unapproved live/paid/publish.

## Historical planning snapshot — superseded for current routing

| ID | Required skills | Task / measurable deliverable | Depends | Status | Evidence / UTC |
|---|---|---|---|---|---|
| EXIST-QA31 | K-QA,K-GIT,K-SEC | Complete already-assigned seven-file PR31 independent governance QA; do not rerun D7 unrelated suites | PR31 existing task | PLANNED | — |
| G1-04 | K-QA,K-DATA,K-TEST | Compare context pack vs original on content, Git-change and sensitive tasks; measure errors and token proxy | G1-02,G1-03 | PLANNED | — |
| UI-01 | K-UX,K-BROW,K-PY | Build/test interactive operator UI prototype from A2 spec, including empty/loading/UNKNOWN/error states | G0-02,G2-02 | PLANNED | — |
| UI-02 | K-UX,K-API,K-TEST,K-SEC | Connect UI to durable task/evidence state and approval indicators; demonstrate sandbox E2E | UI-01,INF-03 | PLANNED | — |
| CTRL-01 | K-BROW,K-AUTO,K-TEST | Test 2 original chat sessions with synthetic task dispatch, actual ACK, receipts and uncertainty dedupe | G2-01 | PLANNED | — |
| UC01-02 | K-WP,K-API,K-TEST,K-UX | Turn A2 real read-only gap audit into repeatable UI/worker flow, show bounded failures | UC01-01,UI-01 | PLANNED | — |
| GROW-03 | K-DATA,K-ADS,K-API,K-UX | Prove cross-channel reporting integration with sourced quality/freshness, distinguish mock vs live | GROW-01,UI-02 | PLANNED | — |

**KNG-01 priority override (2026-11-23):** All unrelated roadmap feature items are ON_HOLD_DEPENDENCY_KNG01 until Work independent QA, coordinator integration, A0-authorized merge and a new dispatch/actual ACK. Historical PLANNED items remain proposals, not current task orders.

**Completion:** a running prototype/workflow with clear environment, checks, actual receipts and independent QA for any Work-authored material code by another qualified agent. **A GitHub notification is not session ACK.** Complete existing PR31 QA before conflicting governance review, and independent UI development is now ON_HOLD_DEPENDENCY_KNG01; only scoped KNG QA may proceed after real session ACK.
## Cách tự cập nhật

Chủ roadmap cập nhật **chính file này** sau khi hoàn thành một đầu việc: chuyển `PLANNED → IN_PROGRESS → DONE_WITH_EVIDENCE`, ghi `EVIDENCE` (commit/PR/log/source link), `UTC`, kết quả PASS/FAIL và lỗi thực tế. Không yêu cầu A0/Điều phối nghiệm thu từng dòng. Chỉ thông báo một lần khi roadmap đạt `READY_FOR_ROADMAP_ACCEPTANCE` hoặc `ROADMAP_PARTIAL_BLOCKED`. Nếu còn công việc an toàn độc lập, phải làm tiếp. Không đẩy secret hoặc PII lên Git.

Nếu cuối roadmap có hạng mục thực sự không thể thực hiện sau các nỗ lực hợp lệ, phải sử dụng nguyên văn: **Đã làm hết công việc có thể làm, một số công việc chưa thể làm do "Bảo mật"/ "Giới hạn kỹ thuật".** Kèm từng lỗi, bước đã thử, bằng chứng và hướng khắc phục. Không suy diễn môi trường hay quyền chỉ từ tên tài khoản.

Quy trình và các giới hạn: [Operating Protocol](../OPERATING_PROTOCOL.md). Quy tắc hiện hành trên main luôn có hiệu lực cho tới khi candidate được tích hợp hợp lệ.

## DGN-FEASIBILITY — bàn giao thiết kế

**Session ACK:** `TASK_ACKNOWLEDGED — DGN-FEASIBILITY`. **Source main:** `d549564de52429e777c68daf9df7a93df5f22f27`. Các mục PLANNED/HOLD phía trên là lịch sử thiết kế và không được kích hoạt bởi nghiên cứu này.

| Phạm vi | Trạng thái | Kết quả / bước tiếp theo |
|---|---|---|
| DGN-1 · UI feasibility | DONE_WITH_EVIDENCE | Work Linux kiểm lại PR16 DOM contract 10/10 PASS, 7 kiểm tra bổ sung. A2 dùng ma trận màn hình, nguồn và acceptance để chốt đặc tả. Browser accessibility, RBAC và live data UNKNOWN. |
| DGN-2 · Giao việc và trạng thái | DONE_WITH_EVIDENCE cho phương án thủ công | Git/derive PASS, SQLite fixture PASS. Điều phối dùng owner-forward, ACK thật, receipt theo attempt, append-only evidence và STOP/rollback có đối soát. |
| Kết nối/dispatch/receipt tự động trên phiên hiện hữu | UNKNOWN · BLOCKED | Không có đích/kênh cross-session đã xác minh, STOP cấm điều khiển Agent khác. Giữ owner-forward cho đến khi có kênh hợp lệ và phép thử được giao riêng. |

**Bằng chứng và giới hạn:** [Báo cáo DGN-FEASIBILITY](../../reports/2026-11-24-dgn-feasibility-work.md), quan sát 23/11/2026 18:07 UTC. **NEXT_OWNER:** A2 tiếp nhận UI feasibility, Chat Điều phối tiếp nhận operating model. Giữ nguyên quyền tác giả của A2, A1 và Điều phối. Không kích hoạt UI/CTRL/M1 hoặc cấp quyền live.

**Đã làm hết công việc có thể làm, một số công việc chưa thể làm do "Bảo mật"/ "Giới hạn kỹ thuật".**

## Current Work assignments — DGN-3/DGN-4 integration

**Receipt:** `TASK_ACKNOWLEDGED — WORK-DGN-ROADMAP-INTEGRATION`, 24/11/2026 Vietnam time, in the Work session. The receipt covers roadmap maintenance. Product execution remains HOLD.

**Source pins:** rules/profile on main `d549564de52429e777c68daf9df7a93df5f22f27`. [Work order](https://github.com/DuyKienTTD/Hosting/blob/80dfb3b854025691c19257f31644b624aa60e7d4/tasks/2026-11-24-work-dgn-roadmap-integration.md) blob `1e3bb5fa56407814b3acdd123bad39c1959a41e2`; [WBS](https://github.com/DuyKienTTD/Hosting/blob/80dfb3b854025691c19257f31644b624aa60e7d4/program/WORK_BREAKDOWN.md) blob `11261e92d520e720d4798087d89f8269f8c19b20`; [Assignment Matrix](https://github.com/DuyKienTTD/Hosting/blob/80dfb3b854025691c19257f31644b624aa60e7d4/program/ASSIGNMENT_MATRIX.md) blob `248947cd9d05bcfcd39e6e3ba12f298da57a1f3a`. Use the detailed WBS and corrected matrix for the rows below. Coordinator roadmap blob readback is `9930a86b5a768f79194e6433b28f5f88232e4e4a`; the work order cites `469c215d0147a9daee6e6335cad607520be98954`. Coordinator to reconcile that pin and the legacy G3-A1 owner wording during integration.

**Branch and permissions:** This maintenance task writes only `program/roadmaps/work.md` on `work/dgn-feasibility`, preserving the feasibility report. Each future write requires an explicit task-scoped Work branch and WRITE_SET; exact future refs are pending separate assignments. Stop on source drift, unexpected writes or unapproved live, paid, deploy or external activity. Revert scoped changes with a new commit if rollback is required; preserve historical evidence.

**Browser evidence:** Playwright Python and Node modules were observed in Work Linux at 2026-11-23 18:07 UTC (`AVAILABLE_IN_WORK_ENVIRONMENT`). axe-core is `UNKNOWN_NOT_VERIFIED`. Browser accessibility and screen-reader tests remain unexecuted. See [DGN-FEASIBILITY evidence](https://github.com/DuyKienTTD/Hosting/blob/4309773bfc20a43970a6b773f352999ef09b77cf/reports/2026-11-24-dgn-feasibility-work.md).

### G1-04 — HISTORICAL_COMPLETE_PER_KNG01_CHECKPOINT; not reopened.

- **Owner and deliverable:** Work (historical). Independent evaluation of context pack and validator; retain historical verdict and measurements.
- **FIRST_ACTION:** Open the prior PR43 review at its recorded SHA if lineage is needed.
- **Dependencies and READ_SET:** G1-02,G1-03. Read PR43/source-pinned KNG harness.
- **WRITE_SET:** None.
- **Skills and tools:** K-QA,K-TEST,K-DATA,K-GIT. GitHub and offline harness (historical).
- **Environment and data:** Offline QA only.
- **Permissions, cost, STOP and rollback:** No rerun of historical PASS absent change trigger; reviewer differs from author. Read-only historical lookup; no new spend; Coordinator records lineage.
- **Acceptance and evidence:** Verdict bound to exact candidate SHA; source integrity and safety preserved. KNG-01 PR43; 61/61 Work QA per checkpoint. Future evidence belongs with the separately assigned task and must record source SHA, observed time and verdict.

### EXIST-QA31 — HISTORICAL_ASSIGNMENT_PRESERVED; verify only if needed.

- **Owner and deliverable:** Work (historical). Preserve already-assigned PR31 Work QA history; no recreation/re-run absent explicit change trigger.
- **FIRST_ACTION:** Locate the exact historical PR31 review and verdict if lineage is needed.
- **Dependencies and READ_SET:** PR31 pinned assignment. Read PR31 diff and review history.
- **WRITE_SET:** None.
- **Skills and tools:** K-QA,K-GIT,K-SEC. GitHub PR history.
- **Environment and data:** Read-only GitHub evidence.
- **Permissions, cost, STOP and rollback:** No new task ACK or duplicate QA; no repeat of historical PASS without material change. Read-only historical lookup; no new spend; Coordinator records lineage. Exact locations without evidence stay UNKNOWN.
- **Acceptance and evidence:** Exact prior review comment/commit/verdict/scope linked; otherwise UNKNOWN. PR31/PR42/PR43 review history. Future evidence belongs with the separately assigned task and must record source SHA, observed time and verdict.

### UI-01 — HOLD_PRODUCT_BUILD; planned only.

- **Owner and deliverable:** Work (proposed; product build HOLD). Build interactive sandbox prototype from A2 spec with source-linked tasks, roadmaps, skills, approvals, evidence and mobile layouts.
- **FIRST_ACTION:** Open A2 PR44 and the task schema at approved SHAs. Confirm synthetic fixtures and sandbox scope before prototyping.
- **Dependencies and READ_SET:** G0-02,G2-02,G2-03. Read PR44, G2-02/G2-03 and PR16 fixtures.
- **WRITE_SET:** Sandbox prototype and evidence in separate task WRITE_SET.
- **Skills and tools:** K-UX,K-BROW,K-PY,K-TEST,K-SEC. Playwright Python/Node observed in Work Linux; axe-core UNKNOWN_NOT_VERIFIED.
- **Environment and data:** Offline/mock or isolated sandbox; no live provider data.
- **Permissions, cost, STOP and rollback:** Product build not authorized by design gate; tool/CI cost UNKNOWN. STOP before external writes, live data or deployment. Separate A0 product-build release, Work ACK and sandbox write permission. Remove/revert prototype changes on STOP. Next: A1 independent QA and A2 product acceptance.
- **Acceptance and evidence:** All 12 screens represented; all loading/empty/error/UNKNOWN/offline/403/409/timeout/mobile states; run T-cases only after build approval. A2 PR44; Work PR16 DOM contract is historical fixture, not prototype; S-UX-E2E candidate. Future evidence belongs with the separately assigned task and must record source SHA, observed time and verdict.

### UI-02 — HOLD_PRODUCT_BUILD / live RBAC UNKNOWN.

- **Owner and deliverable:** Work (proposed; product build HOLD). Connect approved UI to durable task/evidence state, server RBAC/ABAC, approval ledger, freshness and scoped integrations.
- **FIRST_ACTION:** Read the approved UI and state/approval contracts. Check sandbox test identities and restore point before connecting anything.
- **Dependencies and READ_SET:** UI-01,G2-02,G2-03,INF-03. Read UI-01, G2-02/G2-03 and INF-03 contracts.
- **WRITE_SET:** Sandbox integration, migrations and evidence in separate task WRITE_SET.
- **Skills and tools:** K-UX,K-API,K-TEST,K-SEC,K-SCHEMA,K-GIT. SQLite fixture verified historically; authenticated backend, API and identity tooling unverified.
- **Environment and data:** Sandbox first, synthetic data.
- **Permissions, cost, STOP and rollback:** RBAC/live integration UNKNOWN; costs UNKNOWN. STOP on privilege bypass, unbounded spend or missing rollback. Separate A0 build release, Work ACK and sandbox API/DB permission. Roll back migration or restore sandbox snapshot on STOP. Next: independent reviewer assigned by Coordinator.
- **Acceptance and evidence:** Server rejects unauthorized action independent of UI; expiry/revocation/source drift fail closed; audit/readback and rollback verified in sandbox. A2 T07,T12–T16,T21,T23; Work RBAC UNKNOWN; S-AGENT-CONTROL not installed. Future evidence belongs with the separately assigned task and must record source SHA, observed time and verdict.

### CTRL-01 — BLOCKED_CHANNEL_UNKNOWN / NOT_DISPATCHED; manual owner-forward fallback.

- **Owner and deliverable:** Work (proposed; channel UNKNOWN). After a supported channel is verified, prove two consenting test sessions receive unique synthetic work, issue real ACK and return exact-attempt receipts.
- **FIRST_ACTION:** Read the manual handoff contract and verify the proposed channel, consent, session identity and receipt provenance through documentation and authorized read-only inspection.
- **Dependencies and READ_SET:** G2-01,G2-02,G3-03; separate A0 test authorization. Read G2-01/G2-02/G3-03, authorized channel docs and test identities.
- **WRITE_SET:** Synthetic attempt log and QA evidence in separate task WRITE_SET.
- **Skills and tools:** K-BROW,K-AUTO,K-TEST,K-SEC,K-API. No verified adapter or destination; GitHub for evidence only.
- **Environment and data:** Isolated test sessions only; no business payload.
- **Permissions, cost, STOP and rollback:** Channel UNKNOWN; no auto-dispatch authorization. STOP if destination, identity, consent, receipt, cost or kill switch unverified. Separate A0 test authorization and Work ACK, with consent and verified test channel. On STOP use kill switch, preserve attempt log and reconcile before retry. Coordinator handles manual owner-forward. Next: independent reviewer.
- **Acceptance and evidence:** Correct/wrong session tests, actual recipient ACK, completion correlation, duplicate idempotency, timeout UNKNOWN and STOP; source/time evidence. Work DGN-FEASIBILITY; S-AGENT-CONTROL candidate only. Future evidence belongs with the separately assigned task and must record source SHA, observed time and verdict.

### UC01-02 — HOLD_BUSINESS_PILOT / fixtures only.

- **Owner and deliverable:** Work (proposed; build HOLD). Transform UC01-01 findings into reproducible report/evidence consumed by Console with bounded failures and provenance.
- **FIRST_ACTION:** Open the approved UC01-01 findings and map one redacted synthetic fixture to the versioned schema.
- **Dependencies and READ_SET:** UC01-01,UI-01,G2-02. Read UC01-01 findings, UI-01 and G2-02 schema.
- **WRITE_SET:** Sandbox worker/report/fixtures and evidence in separate task WRITE_SET.
- **Skills and tools:** K-WP,K-PY,K-API,K-TEST,K-UX,K-DATA. Python/SQLite fixtures previously demonstrated; WP connector and worker permissions unverified for this task.
- **Environment and data:** Offline fixture/sandbox; read-only source only after approval.
- **Permissions, cost, STOP and rollback:** Live WP/backend scope UNKNOWN; cost UNKNOWN. STOP on writes, missing trace or unbounded retry. Separate A0 build/pilot release, Work ACK and approved read-only source. Disable worker and revert sandbox artifacts on STOP. Next: independent reviewer, with A2 defining acceptance.
- **Acceptance and evidence:** Input→normalized finding→report→UI trace; malformed/missing source and duplicate tests; independent QA. Work feasibility; A2 S11/T15; A1 K-API/K-SCHEMA. Future evidence belongs with the separately assigned task and must record source SHA, observed time and verdict.

### GROW-03 — HOLD_REPORTING_INTEGRATION; mock design only.

- **Owner and deliverable:** Work (proposed; live data UNKNOWN). Aggregate validated business/operational metrics with provenance, freshness, currency, cost state and UNKNOWN semantics.
- **FIRST_ACTION:** Open the GROW-01 KPI contract and map one synthetic metric through the approved import schema.
- **Dependencies and READ_SET:** GROW-01,UI-02,G2-02. Read GROW-01 definitions, UI-02 and G2-02 schema.
- **WRITE_SET:** Sandbox import, dashboard fixtures and evidence in separate task WRITE_SET.
- **Skills and tools:** K-DATA,K-ADS,K-API,K-UX,K-SEC. GitHub for provenance; reporting connectors and live billing unverified for this task.
- **Environment and data:** Mock fixtures first; later authorized read-only connectors.
- **Permissions, cost, STOP and rollback:** Live sources/billing APIs UNKNOWN; subscription/compute cost UNKNOWN. STOP if UNKNOWN becomes zero or data crosses tenant. Separate A0 integration/build release, Work ACK and read-only source authorization. Disable import and restore last valid sandbox snapshot on STOP. Next: independent reviewer, with A2 defining KPIs.
- **Acceptance and evidence:** Every metric has source, observed/collected time, window, currency/unit, formula/version/confidence; stale/missing shows UNKNOWN; reconcile to provider. A2 KPI contracts; Work Evidence/Costs; A1 K-DATA/K-ADS. Future evidence belongs with the separately assigned task and must record source SHA, observed time and verdict.

### G3-A1 — PLANNED_NOT_ACKED; may be included in package assurance.

- **Owner and deliverable:** Work (independent QA owner candidate). Sample A1 directory claims against reproducible evidence; flag unsupported current-session/permission claims without repeating inventory.
- **FIRST_ACTION:** Pin PR46 HEAD and select a sample of capability claims against linked evidence after the separate ACK.
- **Dependencies and READ_SET:** G1-03,G3-01. Read PR46, G1-03/G3-01 and linked evidence.
- **WRITE_SET:** QA verdict/evidence only in separately specified handoff location.
- **Skills and tools:** K-GIT,K-TEST,K-QA,K-SEC. GitHub pinned-source reads verified in this session; review harness subject to task preflight.
- **Environment and data:** Read-only PR/source review.
- **Permissions, cost, STOP and rollback:** A1 cannot self-certify; Work DGN feasibility report is not automatically QA of PR46; separate ACK required. Separate review assignment and Work ACK; read-only access to pinned sources; no paid smoke test. Stop if source drifts or independence is compromised. A1 responds to factual questions. Next: Coordinator; A0 Assistant reviews the integrated package.
- **Acceptance and evidence:** Sampled claims have verdict/source/time/confidence; no other-Agent VERIFIED without own-session receipt. PR46; A1 roadmap says other-Agent checks external pending. Future evidence belongs with the separately assigned task and must record source SHA, observed time and verdict.

**NEXT_OWNER for this integration:** Coordinator, for roadmap and package integration. Package acceptance and execution release remain pending.
