# Skill and Tool Registry — candidate routing matrix

Date: 2026-11-23 | **Distinguish evidence from possibility.** Tools are session-dependent; A0 states all available permissions granted, so do not run generic capability surveys. If a specific task tool fails, record exact `BLOCKED_TECHNICAL` or `BLOCKED_SECURITY` and continue independent work.

Skill states: `EVIDENCED` = demonstrated with report/PR, `REPORTED` = in that agent's survey, `INSTALLABLE` = candidate, not installed/enabled/verified, `GATED` = requires technical or risk clearance. “Full skills” means any applicable actually present tool, not permission to claim uninstalled tools exist.

| Capability family / examples | A1 Chat Standard | A2 Chat Standard | Work | Hostinger | Suggested installation/addition (not automatically installed) |
|---|---|---|---|---|---|
| GitHub read/write, PR, diff, commit and SHA | EVIDENCED PR32/36 | Applicable; A2 untested | EVIDENCED QA comments | REPORTED survey | GitHub Actions validators, GitHub rulesets after review |
| Document analysis, roadmap, dependency modelling | EVIDENCED | Assigned primary; not yet evidenced | EVIDENCED multi-step QA | REPORTED | Document/Sheets skills where accessible |
| Python/JS/JSON/YAML, schema/test fixtures | EVIDENCED A1 tests | Applicable with execution environment | EVIDENCED Linux testing | sandbox code reported | JSON Schema, PyYAML, pytest, Ruff, link checker, secret scanner |
| Knowledge indexing, context packs, retrieval | Agent-based design skill | Usability reviewer | End-to-end QA | infra data author | local grep/ripgrep, deterministic index generator; semantic/RAG only if measured need |
| Web/UI browser interaction, accessibility | Connector-dependent | Connector-dependent | Environment-dependent Work/Computer Use | hPanel tools | Playwright, axe-core, browser automation *only where executable* |
| Hostinger hPanel, VPS/SSH/Docker/network | Not evidenced | Not evidenced | Environment-dependent | EVIDENCED provider inventory | Compose tooling, health/backup monitoring; any installation after preflight |
| WP/Woo content read and SEO review | A1 self-report, coordinator actual live WP read | Assigned primary using available connection | Integration QA | Hostinger hosting side | WordPress/Jetpack connector already available; Woo-specific connector only if needed |
| GA4, Ads, UTM/lead analytics | A1 self-reported Ads read | Assigned business/data analysis | Integrated multistep if tool available | Hosting diagnostics only | Supermetrics, GA4 official connectors only for verified field gaps |
| Google Drive/Docs/Sheets/Calendar/Gmail | A1 self-reported | Connector-dependent | Work multistep | Not provider specialty | Native connected apps, Sheets integration/SQL reporting |
| Media design, voice, video, social | A1 reported Canva/HeyGen/vidIQ | Content/measurement lead | Media pipeline execution | Storage/worker infra | Canva, HeyGen, ElevenLabs, Kling, vidIQ; verify credits/cost/scope |
| n8n, callbacks, DB state, workflow monitoring | Design/validator | Business acceptance | Integration/test | VPS runtime/health owner | n8n nodes, Postgres migration, Prometheus/Grafana/Uptime Kuma (candidates) |
| Testing, security/backup, QA evidence | Offline tests | Business QA | Independent Linux/UX QA | hPanel/VPS audit | Trivy, Gitleaks, restore-test scripts, pytest, CI |
| Agent session UI dispatch | No persistent chat control evidenced | No persistent chat control evidenced | PoC candidate only | Not specialized | Windows Desktop Session Controller + UI automation, test before adopting |

## Role expectations
**A1 — Knowledge Engineering & automation quality:** Git/validator/code, context packing, metadata consistency, branch-scoped tests, reuse evidence. May use connected Workspace/WordPress/Ads/media tools when relevant; not restricted to documentation.
**A2 — Product/Data & business operations:** goals/UI requirements, WordPress/SEO audit, attribution/Ads/GA4, content quality, business KPIs, acceptance criteria; script or use connected apps as needed. Assigned role ≠ proof of any specific A2 connector.
**Work — Integration/Experience & test:** UI prototype and real workflows, cross-app integration, Linux QA, browser or computer-use when available, author code and build when useful; independent reviewer must be different from author.
**Hostinger — Infrastructure/operations:** VPS/hPanel/Cloud WordPress, DNS/TLS, backups, Docker/n8n, security and recovery. A0 has lifted *general* PAUSED; historical frozen work is not auto-reassigned.
**Chat Điều phối — Orchestrator:** portfolio decisions, source conflict resolution, dependency/acceptance at roadmap scale; can itself execute suitable connected source tasks, not just administrative forwarding.
**Hermes — restricted**: WebUI terminal, files, Git, browser, memory, skills, session search (survey), separated from VPS runtime; HOLD due cost.
**Codex — restricted**: Windows shell, code/Git/Computer Use (survey), exception-only due cost.

## Installation decision rule
Prefer already connected tools. Install a skill/plugin/tool only if a specific work item demands a missing capability, data protection and costs are bounded, installation/environment can be rolled back, and permission is real. Record `SKILL_ID, provider, reason, status, cost, granted_scope, test_evidence`; never claim candidates already installed.


---

# DGN-2 — Agent Capability & Skills Directory (A1 authored candidate)

**TASK_ID:** DGN-2-CAPABILITY | **Snapshot:** 2026-11-24 (Asia/Ho_Chi_Minh) | **Evidence baseline main:** \`d549564de52429e777c68daf9df7a93df5f22f27\` | **Author:** A1 | **Environment:** ChatGPT Standard with GitHub connector | **Authority:** inventory/design, not dispatch or live deployment.

## Semantics and source discipline

- A **skill ID** identifies a capability, **not** a plugin installation, entitlement, identity, permission, cost approval or live SLA. WBS \`K-*\` IDs are canonical assignment vocabulary. Additional \`S-*\` IDs below identify *specific implementation surfaces*.
- \`VERIFIED_THIS_SESSION\`: direct successful observation by A1 in this session, with exact scope/evidence. \`EVIDENCED_HISTORICAL\`: dated remote commit/QA or report, not current session assurance. \`REPORTED_BY_AGENT\`: claims from that agent's profile/survey; A1 cannot verify another agent's session. \`CONNECTED_VISIBLE_UNTESTED\`: connector exposed to A1 now without an end-to-end read/write test. \`DOCUMENTED\`: provider documentation describes function but instance capability unknown. \`INSTALLABLE_CANDIDATE\`: not installed by this task. \`BLOCKED\`: specific permission/environment gate. \`UNKNOWN\`: no sufficient evidence. \`ON_HOLD\`: governance, not a technical capability result.
- Two independent axes **capability_state** and **authorization_state** must be checked. Even \`VERIFIED_THIS_SESSION\` never means permitted for an arbitrary WBS. Each assignment checks task ACK, write-set, scopes, current service state and cost cap.
- Source freshness: A1's connected GitHub repository metadata and remote read of baseline on **2026-11-24**; other Agent profiles/surveys are **historical 2026-11-21–23**. Dates are evidence observation dates, not guarantees of runtime continuity. No Agent other than A1 was contacted or ACKed by this inventory.
- **Status precedence:** current task-specific A0/Director authorization and effective main rules > actual agent session receipt > historical survey > installable/documented candidate. The repository's KNG source warns against self-activation; this document neither overrides \`program/current.json\` nor reopens on-hold roadmaps.
- **Cost notation:** \`0 incremental observed for read-only connector calls\` only means no paid operation was invoked here; it does *not* establish provider invoices, contract price or unrestricted quota. \`UNKNOWN_VERIFY\` requires billing/plan/credits inspection before any paid operation. Codex/Hermes are additionally governance cost-gated.
- **Access rule:** a connector being present is not the same as having usable scopes; \`read\` is not \`write\`; GitHub admin metadata is not repository branch policy bypass authorization. No secret/PII/credential or paid smoke test permitted in this task.

## Stable skill ID dictionary for assignment

| Skill ID | Definition; minimum acceptance proof |
|---|---|
| K-GIT | GitHub source, branches, diff, commit/PR, compare SHA; verify remote readback |
| K-DOC | Read full authoritative docs and produce versioned requirements/decisions |
| K-DATA | Data integrity, sourced metrics, unknown/error/null semantics |
| K-SCHEMA | Stable IDs, typed schema, compatibility and negative tests |
| K-PY | Python/JS/shell code or scripts actually executed with reproducible logs |
| K-TEST | Positive/negative unit, integration, fixture and source-boundary tests |
| K-QA | Reviewer independent of author, scoped findings and reproducible verdict |
| K-SEC | Least privilege, secrets/redaction, risk gates and rollback validation |
| K-UX | Operator journeys, accessible responsive UI and validated edge states |
| K-BROW | Real browser/UI navigation with scoped session evidence |
| K-WP | WordPress/Woo content audit with authoritative read-only source |
| K-SEO | SEO content/metadata/structure and source-linked audit |
| K-ADS | Ads/GA4 conversions, spend and attribution via scoped live read |
| K-MEDIA | Asset selection, editing, video/audio/social pipeline with credit gate |
| K-API | Auth, scope, error handling, idempotency and integration contract |
| K-AUTO | Task dispatch, receipts, retries, scheduling; proven live mechanism |
| K-VPS | Hosting/VPS/Docker/network diagnosis with safe runtime evidence |
| K-BACKUP | Backup inventory plus independently demonstrated safe restore |
| K-N8N | n8n workflow states/nodes/queue and tested integration |
| K-OBS | Monitoring/telemetry/alerting with measured freshness and health |
| S-A1-GITHUB | A1 GitHub connector, branch, write/readback surface |
| S-CHAT-DOC | Native reasoning/document authoring; *no* running service implied |
| S-WORK-COMPUTER | Work cloud browser/computer-use candidate; session-dependent |
| S-HOST-HPANEL | Hostinger Agent hPanel account-tool operations; historical evidence |
| S-HERMES-WEBUI | Hermes WebUI skills/tools/memory; historical self survey |
| S-CODEX-LOCAL | Codex coding/Windows shell/Git tests; historical survey |
| S-A1-WORKSPACE | A1 connected Google Drive/Gmail/Calendar connector surfaces |
| S-A1-MARKETING | A1 connected Supermetrics/Google Ads/vidIQ surfaces |
| S-A1-MEDIA | A1 Canva/HeyGen connector surfaces |
| S-WP-CONNECTOR | A1 WordPress connector surface, no live mutation tested |
| S-CI-SAFETY | Proposed CI validator+secret scanner; not yet enabled |
| S-UX-E2E | Proposed Playwright/axe smoke and accessibility suite |
| S-OBS-STACK | Proposed monitoring/restore stack for VPS/n8n |

## Agent directory — authority, surfaces and assignments

| Agent / primary role | Native skills / WBS fit | Installed or connected **as evidenced** | Environment; permission; cost | Verification, limits and fallback |
|---|---|---|---|---|
| **Chat Điều phối** — portfolio authority, roadmap synthesis, risk-tier dispatch, conflict arbitration and roadmap acceptance; does not replace A0 | K-DOC,K-GIT,K-SCHEMA,K-QA,K-SEC,K-DATA; G0-03,G2-01,G2-03,G3-02,G3-03,REL-01 | S-CHAT-DOC; historical GitHub connector usage in \`agents/chatgpt.md\`. Actual connector list **for Coordinator's own current chat UNKNOWN** | Interactive ChatGPT; GitHub write only when checked per session; no implied 24/7; marginal tool charges UNKNOWN_VERIFY | \`REPORTED_BY_AGENT/EVIDENCED_HISTORICAL\`, profile \`agents/chatgpt.md\` (2026-11-21); cannot independently verify current Coordinator session. Fallback A1 read-only source preparation with Director as owner; never fabricate Coordinator ACK |
| **Trợ lý A0 độc lập** — private owner-side decision support, independent business critique, drafts/analysis, exception recommendations; *not* same as Điều phối or A0 approval authority | K-DOC,K-DATA,K-QA,K-SEC; owner-side review and acceptance preparation, not default sole writer | Native ChatGPT conversation only \`DOCUMENTED\`; **no distinct authenticated session/profile/installed-skill inventory evidenced** | Environment/account/connector/identity \`UNKNOWN\`; cannot approve or act on behalf of A0 without explicit owner event; cost UNKNOWN_VERIFY | \`UNKNOWN\`; require its own real session capability statement/receipt. Fallback Chat Điều phối prepares options for A0 decision |
| **A1** — source/metadata integration, technical inspection, validators, bounded connector analysis and author QA; separate from independent reviewer | K-GIT,K-PY,K-SCHEMA,K-TEST,K-DOC,K-SEC,K-DATA; G1-01/02/03 and this DGN-2 inventory | **S-A1-GITHUB \`VERIFIED_THIS_SESSION\`**: repo read, \`main\` SHA, GitHub repository push/admin metadata, branch creation. S-A1-WORKSPACE, S-A1-MARKETING, S-A1-MEDIA, S-WP-CONNECTOR exposed in available connector catalog; action-level scope **CONNECTED_VISIBLE_UNTESTED** in this task. Historical A1 survey is \`REPORTED_BY_AGENT\` | ChatGPT Standard + connected GitHub; no live VPS shell established by GitHub access; read source and isolated branch write permitted here; no paid operations; actual billing UNKNOWN_VERIFY | GitHub main \`d549564...\` and branch \`a1/dgn-2-capability-2026-11-24\`, 2026-11-24. Code runner not used to verify external systems in this task. Fall back Work for independent review/UI, Hostinger after authorization for hPanel, A2 for business review |
| **A2** — Product/Operator UX, customer journey, business data, WP/SEO, attribution requirements and content quality; WBS owner where actually assigned | K-UX,K-DOC,K-DATA,K-WP,K-SEO,K-ADS,K-MEDIA; G0-01/02,G3-01,UC01-01,GROW-01/02 | Distinct ChatGPT Standard surface described in \`program/roadmaps/a2.md\`; **no current-session connected inventory, permission smoke test or individual Agent self-certification in this A1 task** | Separate chat, credentials and quota UNKNOWN; no production/publish authority; cost UNKNOWN_VERIFY | \`UNKNOWN/REPORTED_BY_AGENT\` only for role/roadmap; current capability requires A2 direct read-only checks and ACK. Fallback A1 technical documentation / Work UI test, Director retains assignment |
| **Work** — multi-step integration, independent source/UX/browser QA, operator prototype and bounded E2E | K-QA,K-TEST,K-BROW,K-UX,K-API,K-PY,K-AUTO; G1-04,UI-01/02,CTRL-01,UC01-02,GROW-03 | Work/browser/Linux source-QA historical evidence, \`program/roadmaps/work.md\`, PR #42 independent QA. **Current Work browser, connectors, shell and session scopes untested here** | ChatGPT Work session or computer-use when enabled; workspace/system access per session; no automatic session control or deployment permission; cost UNKNOWN_VERIFY | \`EVIDENCED_HISTORICAL\` source-QA, \`UNKNOWN\` current session; PR42 comment \`7103815886\`. Fallback A1 author-only tests + separately assigned reviewer; never self-certify independent QA |
| **Hostinger Agent** — hPanel specialist, account and VPS health, DNS/SSL/hosting, backup/recovery and operational design | K-VPS,K-SEC,K-BACKUP,K-OBS,K-WP,K-N8N; INF-01/02/03/04,SEC-H,WP-H | S-HOST-HPANEL historical 2026-11-21 account survey in \`agents/hostinger.md\`, \`reports/2026-11-21-hostinger-account-capability-inventory.md\`; live account access **not retested** | hPanel provider agent; account-scoped tools, some allowlisted diagnostics; no unrestricted SSH/root inference; changes approval gated; plan/API cost UNKNOWN_VERIFY | \`REPORTED_BY_AGENT/EVIDENCED_HISTORICAL\`, current \`ON_HOLD\` until real resumption/ACK. Fallback A1 designs runbooks; Codex only on separately authorized exception; never assign infra write based on profile |
| **Hermes** — AI reasoning, tools, memory, content analysis and potential n8n reasoning layer | K-DOC,K-DATA,K-SCHEMA,K-API,K-MEDIA; plans/analysis and mock only until real backend proven | S-HERMES-WEBUI survey \`skills_list=55\`, session search, tools and Git SSH per \`agents/hermes.md\`; **55 names/versions not enumerated here**, do not mint plugin skill IDs | Distinguish Hermes WebUI from KVM2 dashboard runtime; production inference API and n8n MCP unproven; governance \`ON_HOLD\`, paid-model token billing UNKNOWN_VERIFY | \`REPORTED_BY_AGENT\` (2026-11-21) and historical audit only; no new Hermes ACK. Fallback A1 offline reasoning/tests or Work E2E; never claim 24/7 |
| **Codex** — exceptional complex code, Docker/integration, tests and hardening when others objectively lack capability | K-PY,K-TEST,K-SCHEMA,K-API,K-VPS,K-SEC,K-N8N; exception-only specialized remediation | S-CODEX-LOCAL historical Windows/Git tests and sandbox source per \`agents/codex.md\`, \`reports/2026-11-21-codex-capability-survey.md\`; Docker daemon historically blocked, some API scopes unknown | External Codex session; exact current toolchain, app plan and per-task charges UNKNOWN_VERIFY; \`CODEX_NOT_AUTHORIZED\` absent A0-specific exception | \`REPORTED_BY_AGENT/EVIDENCED_HISTORICAL\` only; no new Codex ACK. Fallback A1/Work/Hermes for smaller offline source changes, Hostinger for provider operations after approval |

**Additional non-agent component:** n8n is a workflow engine, not a ninth Agent. Historical n8n healthy with zero production workflows and disabled MCP at 2026-11-21 survey; present-day state \`UNKNOWN\`. Do not route autonomous agent responsibility to n8n without a separately proven and authorized workflow.

## WBS resolution procedure (use per item, not by agent title)

1. Read the exact WBS row's \`Required skills\`, dependencies/gate and acceptance in [WORK_BREAKDOWN](WORK_BREAKDOWN.md); resolve every \`K-*\` using the dictionary above. A missing skill ID is \`UNKNOWN\`, not silently ignored.
2. Match eligible Agent capability **and** actual session surfaces; check current \`program/current.json\` only under independently verified activation plus effective main rules and explicit Director work order. An \`ON_HOLD\` row cannot be activated by this directory.
3. Capture \`task_id, owner, required_skill_ids, proposed_surface_id, capability_state, evidence_url, observed_at, environment, actual_read_scope, actual_write_scope, authorization_state, cost_model, maximum_spend, fallback, reviewer\`. Missing current permission/credit/ACK means \`NOT_VERIFIED\` or \`BLOCKED\`, not \`READY\`.
4. Safe gate before execution: read-only synthetic smoke → scoped negative/error tests → author evidence → separate reviewer for material changes → remote readback. For any live/publish/paid step require task-specific approval, cap and rollback *in addition* to evidence.
5. Fallback by missing component: no Git connector → create patch and \`NOT_PUSHED\`; no UI control → report mock/read-only not E2E; no Ads/WP scope → sourced static analysis labelled non-live; no provider access → advisory only; no paid approval → use fixtures, not charged API. Do not substitute mock PASS for LIVE PASS.

## Installable candidates — **NONE installed by DGN-2**

| Candidate skill ID | New capability / reason | Environment and prerequisite | Required rights / cost | Safe acceptance and rollback |
|---|---|---|---|---|
| S-CI-SAFETY | GitHub Actions validator, \`gitleaks\` or equivalent secret scan, markdown link/ID checks; block unsafe diffs | Repo CI policy review, isolated PR and known benign positive/negative fixtures | CI/workflow write + A0/Director policy approval, Actions minutes/storage billing **UNKNOWN_VERIFY**; no secret scopes for basic checks | Run on synthetic branch, prove false-positive handling and deliberate fake-secret detection; inspect Actions bill; rollback revert workflow PR and remove permissions, preserve evidence |
| S-UX-E2E | Playwright + axe-core keyboard/responsive/accessibility and UI regression | Work/A2 isolated sandbox or test-only browser with stable fixtures | Test browser installation permission; test account read scopes only; CPU/CI minutes UNKNOWN_VERIFY | Test static mock with disabled network mutations and failed selectors/error states; rollback remove package and lockfile changes on sandbox branch |
| S-OBS-STACK | Uptime Kuma/Prometheus/Grafana or equivalent real health/alert visibility | Hostinger/KVM2 staging topology, backup, resource/capacity baseline | VPS/container/network/notification scopes; recurring storage and compute UNKNOWN_VERIFY | Offline Compose validation and synthetic endpoint; later separately approved staging outage/restore, no prod; rollback stop/remove staging stack and restore baseline |
| S-SCHEMA-TEST | PyYAML/pytest/JSON Schema/Ruff and reproducible source validation | Isolated Python virtual environment or existing local runner, pinned versions | Local install rights; packages generally no license fee, compute/source audit still needed | Offline pinned fixture tests and malformed-input negative suite; rollback delete isolated venv/lock changes; no production dependencies changed |
| S-WP-READ | WordPress/Woo read-only exporter/plugin only if connected WordPress tools cannot cover required audit fields | Staging account, minimal API key, test records, retention policy | Site admin approval for install; actual read-only access and data minimization; hosting/plugin fees UNKNOWN_VERIFY | Staging export of synthetic IDs with deny-write tests and log redaction; rollback revoke key/uninstall staging component and delete test exports |
| S-ADS-GA4 | Supermetrics or official GA4/Ads reporting integration for missing measured attribution fields | A2/Work scoped reporting service and data dictionary, business account | OAuth read-only reporting scopes, privacy review, query/quota/subscription cost UNKNOWN_VERIFY | One bounded historical read, compare with UI totals and preserve null/error semantics; rollback disconnect/revoke read scope, remove scheduled sync |
| S-MEDIA-GEN | Canva/HeyGen/vidIQ/voice/video tools for missing media production features (Kling/ElevenLabs only as candidates) | Approved storyboard/source assets, license/consent, sandbox preview, current pricing | Account/media rights, image/voice consent, publish scopes separately, credits/subscriptions UNKNOWN_VERIFY | Use non-paid draft/mock first, quote credit estimate and explicit cap before render; rollback delete unapproved draft and revoke connector, credits may be non-refundable |
| S-AGENT-CONTROL | Two-session dispatch/ACK UI controller, not a presumed ChatGPT background API | Work computer-use pilot, two consenting test sessions, state/receipt store and kill switch | Session access, security/privacy review, API/runtime costs UNKNOWN_VERIFY | Two synthetic tasks with real individual ACK and duplicate/failure cases; rollback terminate pilot, revoke sessions, preserve minimal redacted receipts |
| S-GITHUB-RULES | Branch protection/rulesets, mandatory PR review and source-integrity checks | Separate governance approval; ensure admins and emergency recovery path | Repository admin, impact to all writers; pricing/feature plan UNKNOWN_VERIFY | Dry-run audit, staged ruleset, negative bypass/recovery test; rollback disable newly staged ruleset by approved admin, not ad hoc bypass |

**Installation request contract:** \`candidate_skill_id, target_wbs, missing_feature_evidence, provider/version, operating_system, required_scopes, data_classification, payer/account, price_and_quota_source_checked_at, maximum_cost, safe_test_plan, rollback_owner, approval_id\`. If any material field is absent, remain \`INSTALLABLE_CANDIDATE\`, not \`INSTALLED\`.

## Provenance index (immutable/historical versus live)

- Direct GitHub A1 inspection, **2026-11-24**: \`main=d549564de52429e777c68daf9df7a93df5f22f27\`; repo metadata reports \`pull=true,push=true,admin=true\`; separate \`a1/dgn-2-capability-2026-11-24\` branch created. This proves only the current GitHub session surface and isolated branch creation.
- A1 historical authored source / independent reviewer: [PR32](https://github.com/DuyKienTTD/Hosting/pull/32), [PR36](https://github.com/DuyKienTTD/Hosting/pull/36). Profile [agents/a1.md](../agents/a1.md).
- Independent KNG source review: [Work PR42 QA](https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7103815886); not a current Work capability/ACK.
- Other agent profiles: [Coordinator](../agents/chatgpt.md), [Hostinger](../agents/hostinger.md), [Hermes](../agents/hermes.md), [Codex](../agents/codex.md); their observation dates and limits are preserved.
- Other roadmaps: [A2](roadmaps/a2.md), [Work](roadmaps/work.md), [Coordinator](roadmaps/coordinator.md), plus A1; roadmap intent ≠ available installed tool.
- KNG governance: [AGENTS](../AGENTS.md), [workflow](../rules/AGENT_WORKFLOW.md), [security](../rules/REPOSITORY_SECURITY.md), [STATE](../STATE.md), [CATALOG](../CATALOG.yaml), [release source](current.json), [WBS](WORK_BREAKDOWN.md).
- **Not verified by A1:** A0 private-assistant identity, A2 live connectors, Work current computer-use scope, Hostinger current hPanel, Hermes current 55-skill enumeration, Codex current session, actual billing rates/remaining credits, paid provider performance, production state. Each needs its own Agent read-only session receipt. These unknowns are **not** grounds to falsify a capability as installed.

**Security & rollback:** This is document-only on an A1 branch; reversal is revert the isolated docs commits/close PR, not mutate any system. No agent installation, external API spend, quota-consuming render, live account write, production change, \`main\` merge or new agent dispatch occurred.
