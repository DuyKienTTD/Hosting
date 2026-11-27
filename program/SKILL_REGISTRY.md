# Agent Capability & Skills Directory — DGN-2 factual candidate

**TASK_ID:** `DGN-2-CAPABILITY` · **OWNER:** A1 (Capability & Skills Engineering) · **MODE:** `DESIGN_AND_EVIDENCE_ONLY` · **checked_at:** 2026-11-24 (Asia/Ho_Chi_Minh) · **source/main:** `d549564de52429e777c68daf9df7a93df5f22f27`.

**Status:** author-maintained capability/evidence candidate, **NOT** operating policy, automatic dispatcher, A0 approval or live assignment. Coordinator owns Operating Model, WBS and Assignment Matrix. This directory aids matching only; one real work order and separate recipient-session ACK are still required. Never infer owner authority from skill possession.

**Authority:** [main rules](../AGENTS.md) · [workflow](../rules/AGENT_WORKFLOW.md) · [security](../rules/REPOSITORY_SECURITY.md) · [WBS 32 original IDs](WORK_BREAKDOWN.md) · [pinned Coordinator PASS_WITH_CONDITIONS roadmap](https://github.com/DuyKienTTD/Hosting/blob/ab0e728f6f1c698dc7d2fd8dcae6e8bad94dc125/program/roadmaps/coordinator.md). Earlier KNG-only hold in main is a dated source snapshot; DGN-2 is explicitly user-ordered design/evidence work, not authorization for unrelated implementation or production.

## 1. Strict status vocabulary (do not collapse)

| Status / confidence | Meaning for matching |
|---|---|
| `VERIFIED_CURRENT_A1` | Direct A1 connector or safe test on **this** session; tool and environment named; only A1 claims this |
| `VERIFIED_HISTORICAL_AGENT` | Native report by the actual other Agent with bounded timestamp/env and reproducible evidence; **not** fresh verified capability |
| `REPORTED_SESSION_HISTORICAL` | Agent profile/self-report or prior handoff, current access untested |
| `TOOL_EXPOSED_UNTESTED` | Tool/skill entry available in A1 session but login, runtime, permission, job success or paid scope not tested |
| `INSTALLED_SKILL_LISTED` | Skill URI returned by A1 skill listing; instruction availability only, not an account connection |
| `CONNECTED_ACCOUNT_CONFIRMED` | Account identity/permission demonstrated by targeted read-only tool action, scoped to that connector/session |
| `INSTALLABLE_CANDIDATE` | Not installed/connected by this task; proposed only |
| `GATED` | Specific A0, owner, privacy, cost, risk or production approval needed |
| `BLOCKED` / `UNKNOWN` / `NOT_RUN` | Explicit blocker / no evidence / no test; **never treat as PASS** |

**Evidence boundary:** Historic `VERIFIED` in another Agent's own survey means verified *then, in its runtime*, not A1's independent verification today. All non-A1 Agent rows below require fresh self-confirmation at actual task receipt. `price=UNKNOWN` is not zero-cost; zero credits spent this DGN-2 task.

## 2. Stable canonical capability / skill IDs for WBS matching

| Skill ID | Required outcome and minimum tool | Proposed owner fit | WBS coverage (non-dispatch) | STOP / dependency |
|---|---|---|---|---|
| `K-GIT` | GitHub branches, blob SHA, diff, commit, PR, readback; GitHub connector, Git client | A1 / Work / Coordinator | G1-01,G1-02,G1-03,G3-02,G3-03,REL-01,G3-A1,EXIST-QA31 | write-set; no force/merge |
| `K-DOC` | Documents, decisions, traceability, report; Markdown, Docs, docx | Coordinator / A2 / A1 | G0-01,G0-02,G0-03,G2-01,G2-03,G3-01,GROW-02,REL-02 | no fabricated sources |
| `K-DATA` | Data cleaning, source checks, attribution limits; Python, Sheets, BigQuery read | A1 / A2 / Work | G0-01,G1-04,G3-01,G3-02,UC01-01,GROW-01,GROW-03,QA-U01 | PII; query cost |
| `K-PY` | Python, fixtures, deterministic code; Python 3, standard unittest | A1 / Work / Codex | G1-01,G1-03,G2-02,UI-01,UC01-02 | test environment required |
| `K-SCHEMA` | Typed schema, provenance, metadata; JSON/YAML, safe parser | A1 / Coordinator / Work | G0-03,G1-02,G1-03,G2-01,G2-02,G3-02,G3-03 | no self-ACK |
| `K-TEST` | Positive/negative, replay, recovery; unittest/pytest; isolated fixtures | A1 / Work / Codex | G1-03,G1-04,G2-02,INF-02,INF-04,UI-02,CTRL-01,UC01-02,G3-A1 | author != independent reviewer |
| `K-QA` | Independent acceptance, source readback; GitHub review, test runner, browser | Work / A0 Assistant / A1 on other owners' code | G1-04,G2-03,REL-01,QA-U01,EXIST-QA31 | no self-certification |
| `K-SEC` | Secrets, access control, STOP, rollback; repository rules, static scan | Work / A1 / Hostinger / Coordinator | G1-03,G2-01,G2-03,INF-01,INF-02,INF-03,UI-02,CTRL-01,GROW-01,REL-01,REL-02,SEC-H | approval for risky changes |
| `K-UX` | Operator journeys, screens, accessibility; A2 spec; Work browser | A2 / Work | G0-02,UI-01,UI-02,GROW-02,GROW-03 | design != functional UI |
| `K-BROW` | Browser/UI observation, computer use; Work Computer Use or tool-specific browser | Work / Hostinger hPanel | UI-01,CTRL-01 | session scoped |
| `K-AUTO` | Task/ACK automation design, scheduling; schema, workflow mocks | Work / Hermes / A1 | CTRL-01,G2-02 | no invisible autonomous dispatch |
| `K-API` | Safe APIs, connectors, auth and retries; Python/JS, API schemas, n8n | Work / Hermes / A1 | INF-04,UI-02,UC01-02,GROW-03 | live writes gated |
| `K-VPS` | Hostinger hPanel, VPS, Docker, DNS; hPanel, terminal | Hostinger Agent | INF-01,INF-02,INF-03,INF-04,SEC-H,WP-H | not A1 shell access |
| `K-BACKUP` | Backup snapshots, restore rehearsal; Hostinger backup, sandbox restore | Hostinger Agent | INF-02,SEC-H | restore preflight |
| `K-OBS` | Health/telemetry, outages, alerts; hPanel, monitoring endpoints | Hostinger Agent | INF-01,INF-03,WP-H | fresh live probes |
| `K-N8N` | n8n workflow, callback, idempotence; n8n sandbox/runtime | Hostinger/Hermes after approval | INF-04 | production MCP off in survey |
| `K-WP` | WordPress/WooCommerce content; WP connector, read-first | A2 / Work / A1 | UC01-01,UC01-02,WP-H | staging before production |
| `K-SEO` | SEO content and metadata QA; WordPress, Search Console | A2 / A1 | UC01-01,QA-U01 | verify source claims |
| `K-ADS` | Ads/GA4/attribution; Supermetrics, Ads, GA4 read | A2 / A1 / Work | GROW-01,GROW-03 | budget changes separately approved |
| `K-MEDIA` | Creative, social, video, voice; Canva, HeyGen, vidIQ | A2 / Hermes / A1 | GROW-02 | credits/publish gated |
| `K-ORCH` | Multi-agent dispatch/role matching; coordinator task contract + real ACK | Coordinator | G2-01,G3-03,REL-01 | not Git comment auto-trigger |
| `K-WBS` | Scope/dependencies, critical path; WBS source, deterministic graph | Coordinator | G0-03,G3-02,G3-03 | preserve original 32 IDs |

**Matching order:** task's required skill IDs → minimum actual executable tool/OS → same-session permission + cost + risk gate → evidence freshness → authorized writer → independent reviewer → fallback. Candidate skills alone never satisfy an executable assignment. Keep WBS owners in `program/WORK_BREAKDOWN.md` untouched; DGN-3 Coordinator will reconcile historical G3-01 owner and new DGN-2 responsibility. Human A0 `REL-02` is approval, not an AI skill inference.

## 3. Agent directory — provenance and capability boundaries

**Skill ID format:** `K-*` = canonical WBS capability, `N-*` = native platform surface, `C-*` = installed/connected tool or plugin capability, `I-*` = proposed installation. `N/C/I` never substitute for the canonical `K-*` IDs without a real skill test.

### AG-COORD — Chat Điều phối (separate session)
- **Role:** accountable portfolio director; requirements, evidence reconciliation, dependency routing, acceptance package, owner assignments and A0 escalation. **Suitable:** G0-03,G2-01,G2-03,G3-02,G3-03,REL-01,REL-02 preparation; **not** self-authorizing merge or independent QA of own decisions.
- **Native IDs:** `N-COORD-REASON` (reasoning), `N-COORD-WRITE` (task/roadmap documentation), `N-COORD-ROUTE` (work-order design). **K IDs:** K-ORCH,K-DOC,K-SCHEMA,K-WBS,K-GIT,K-QA,K-SEC.
- **Installed/connected:** GitHub read/write in historical profile `C-GH-COORD` (**REPORTED_SESSION_HISTORICAL**, not fresh checked); Google/browser/other connectors **UNKNOWN**.
- **Environment/permissions:** ChatGPT Coordinator **separate chat**, historical GitHub connector, authority is work-order governance only; GitHub comment alone is not SENT/ACK. **Cost:** model quota UNKNOWN; paid deployment and approval not inferred.
- **Proof:** [Coordinator agent profile](../agents/chatgpt.md), [PASS_WITH_CONDITIONS coordinator roadmap at immutable SHA](https://github.com/DuyKienTTD/Hosting/blob/ab0e728f6f1c698dc7d2fd8dcae6e8bad94dc125/program/roadmaps/coordinator.md). **Verification:** REPORTED_SESSION_HISTORICAL.
- **Gaps/fallback:** no persistent automatic control proven; hand off browser E2E to Work, provenance/validator to A1, hPanel to Hostinger; DGN-2 capability matrix is **not** a new Coordinator assignment. Install candidate: `I-GH-CI` / `I-JSON-SCHEMA` after authorization and need.

### AG-A0-ASST — Trợ lý A0 độc lập (NOT A0, NOT Coordinator)
- **Role:** independent A0-side design/portfolio reviewer; check completeness, traceability, permissions, risk/cost, QA author separation; issue recommendations to human A0 only. **Suitable:** independent DGN-1..4 package review and decision preparation, not authoring Coordinator Operating Model or any production acceptance.
- **Native IDs:** `N-A0-REVIEW` (analytical critique), `N-A0-TRACE` (cross-document review) — **PROPOSED role mapping, not tested runtime capabilities**. **K IDs:** K-QA,K-DOC,K-SEC,K-DATA.
- **Installed/connected IDs:** NONE CONFIRMED; `C-GH-A0-ASST` **UNKNOWN**, skill inventory **UNKNOWN**. **Environment:** separate ChatGPT agent session, OS/browser/connector **UNKNOWN**. **Permissions:** evidence review only until A0 delegates more; never impersonate A0; no source writer claim. **Cost:** UNKNOWN.
- **Proof:** [Coordinator DGN-2 role/independent acceptance contract](https://github.com/DuyKienTTD/Hosting/blob/ab0e728f6f1c698dc7d2fd8dcae6e8bad94dc125/program/roadmaps/coordinator.md). **Verification:** ROLE_ASSIGNED_ONLY; self-survey NOT_RECEIVED.
- **Limit/fallback:** until explicit session ACK and proof, Coordinator must present review request to A0 directly; Work can do source QA but may not pretend to be A0 Assistant. Install candidate: `I-DOC-QA` (only after self-confirmation).

### AG-A1 — A1, current ChatGPT ordinary session
- **Role:** Capability & Skills Engineering; Git/source/SHA auditing, skill inventory, provenance, data/schema/code tests and documentation. **Suitable:** G1-01/02/03,G2-02,G3-A1,QA-U01, DGN-2; never author-independent QA for own code.
- **Native IDs:** `N-A1-ANALYSIS`, `N-A1-CODE`, `N-A1-TOOLS` (current tool orchestration). **K IDs:** K-GIT,K-PY,K-DOC,K-SCHEMA,K-TEST,K-DATA,K-SEC,K-API,K-SEO.
- **Directly checked now:** `C-GITHUB-A1` GitHub read + branch creation on `DuyKienTTD/Hosting` (**VERIFIED_CURRENT_A1**, 2026-11-24, from main pinned SHA); repo permissions pull/push/admin visible in API (**permission metadata**, not unrestricted branch-protection bypass). `C-SKILLS-A1`: A1 skill listing returned **92** entries (5 first-party, 87 plugin skills), **INSTALLED_SKILL_LISTED** not all connected. Tool namespaces exposed: GitHub, Google Drive/Gmail/Calendar/Contacts, WordPress, Canva, HeyGen, Supermetrics, BigQuery, vidIQ, plugin management, with actual scopes varying; mark **TOOL_EXPOSED_UNTESTED** except direct GitHub check. Prior read-only BigQuery projects/vidIQ channel evidence in historic A1 session is **REPORTED_SESSION_HISTORICAL**, not rechecked here.
- **Runtime/permissions:** current ChatGPT tool orchestration plus container Python/Git for safe offline tests; no claim of local Windows, VPS shell, Cloud Shell, persistent desktop agent, or 24/7. GitHub branch-scoped write only for DGN-2 write-set. **Cost:** GitHub fetch/local deterministic QA zero requested paid actions; plugin API quota and HeyGen/vidIQ credit UNKNOWN today; no spending.
- **Proof:** [A1 profile](../agents/a1.md), [prior authored KNG PR43](https://github.com/DuyKienTTD/Hosting/pull/43) and **current DGN-2 branch remote readback to follow in PR**. **Verification:** current GitHub and skills listing, tool surfaces exposed; connected account scopes aside from GitHub NOT_CURRENTLY_PROVEN.
- **Limit/fallback:** shell runtime/connector may change, GitHub readback required; Work performs independent QA, Hostinger handles VPS, A2 handles product/UX. Installation: `I-JSON-SCHEMA`, `I-PYTEST`, `I-GITLEAKS` only if tests show need and consent permits.

### AG-A2 — A2, separate ChatGPT ordinary session
- **Role:** Product Charter, Operator UI Design, business actors/personas/KPIs, acceptance and traceability. **Suitable:** G0-01,G0-02,GROW-02,UC01-01,GROW-01 and DGN-1. **Not** Coordinator DGN-2 ownership or A1 skill registry author.
- **Native IDs:** `N-A2-REASON`, `N-A2-UX-SPEC` (role-fit only). **K IDs:** K-DOC,K-UX,K-DATA,K-WP,K-SEO,K-ADS,K-MEDIA.
- **Installed/connected:** `C-GH-A2`, `C-WP-A2`, `C-ADS-A2`, `C-CANVA-A2` = **UNKNOWN / SELF_CONFIRM_REQUIRED**. Do not infer A2's account from A1's connectors.
- **Environment:** distinct ChatGPT session; OS/browser/shell **UNKNOWN**; GitHub write only within assigned A2 branch and profile. **Cost:** UNKNOWN; no paid creative or Ads budgets from role assignment.
- **Proof:** [A2 roadmap](roadmaps/a2.md), [Coordinator pinned DGN-1 contract](https://github.com/DuyKienTTD/Hosting/blob/ab0e728f6f1c698dc7d2fd8dcae6e8bad94dc125/program/roadmaps/coordinator.md). **Verification:** task assignment evidenced; current connector availability unverified by A1.
- **Fallback:** Work read-only UX feasibility, Coordinator requirements review, A1 data validation only. Install candidates `I-AXE`/`I-PLAYWRIGHT` only if target environment and permission verified.

### AG-WORK — ChatGPT Work
- **Role:** independent Linux/source QA, browser/Computer Use/UX feasibility, real workflow trials and integration; distinct reviewer for A1/A2 authored code. **Suitable:** G1-04,EXIST-QA31,UI-01,UI-02,CTRL-01,UC01-02,GROW-03 and scoped DGN-1 feasibility.
- **Native IDs:** `N-WORK-COMPUTER`, `N-WORK-BROWSER`, `N-WORK-QA` — browser features **ENVIRONMENT_DEPENDENT**. **K IDs:** K-QA,K-TEST,K-BROW,K-UX,K-API,K-DATA,K-GIT.
- **Installed/connected:** historic GitHub QA read/post `C-GH-WORK` **VERIFIED_HISTORICAL_AGENT**; full checkout Linux validator tests evidenced on PR42. No guarantee current browser, SSH or all plugins. Other installed skill IDs **UNKNOWN** pending own session survey.
- **Environment/permissions:** Work cloud/browser/isolated runtime from dated tasks; no direct assumption about same persistent filesystem or Windows user's desktop. Work's review of its own authored code is **not independent**. **Cost:** model/session limits UNKNOWN; no paid infra.
- **Proof:** [Work roadmap](roadmaps/work.md), [Work PR42 full-checkout QA](https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7103815886), [PR43 independent QA discussion](https://github.com/DuyKienTTD/Hosting/pull/43). **Verification:** historical QA only, fresh self-survey required.
- **Fallback:** A1 executes isolated test/validator on others' changes; A2 reviews UX, Hostinger provides live hPanel facts. Installation `I-PLAYWRIGHT`/`I-AXE` optional after Work feasibility confirmation.

### AG-HOSTINGER — Hostinger Agent (hPanel)
- **Role:** provider account and VPS/hPanel/cloud/site/DNS/TLS/backups/WordPress resource state, safe diagnosis and recovery; **not** generic GitHub-orchestration replacement. **Suitable:** INF-01..04,SEC-H,WP-H with approval and fresh live probes.
- **Native IDs:** `N-HOSTINGER-HPANEL`, `N-HOSTINGER-VPS-READ`, `N-HOSTINGER-BACKUP`. **K IDs:** K-VPS,K-OBS,K-BACKUP,K-SEC,K-N8N,K-WP.
- **Connected/installed:** provider hPanel Agent account tools `C-HPANEL-AGENT` **VERIFIED_HISTORICAL_AGENT (2026-11-21)**; exact session read-only VPS/source, backups/Docker manager reported. GitHub read/write historically reported; no current session proof.
- **Environment:** Hostinger hPanel provider-side session; sandbox != VPS and permission per tool/action. **Permissions:** read-only diagnostics where exposed; restart/recreate/firewall/DNS/backup restore/change production **GATED** A0 and rollback. **Cost:** hosting subscription existing but live charges/credits UNKNOWN; new provisioned resource gated.
- **Proof:** [Hostinger agent profile](../agents/hostinger.md), [Hostinger account capability inventory](../reports/2026-11-21-hostinger-account-capability-inventory.md). **Verification:** dated historical, fresh self-confirmation required.
- **Limit/fallback:** provider shell cannot be assumed shared with A1; Work can QA docs and A1 can review configs offline, neither replaces live Hostinger authorization. Candidates `I-COMPOSE`, `I-UPTIME-KUMA` after sandbox/backups.

### AG-HERMES — Hermes WebUI agent
- **Role:** reasoning, content, media brief, tool-based research and isolated workflow/schema; not a proven 24/7 inference endpoint. **Suitable:** content research, GROW-02 pre-production, isolated mock/n8n contracts, source QA not authored by Hermes.
- **Native IDs:** `N-HERMES-SHELL`, `N-HERMES-SKILL-LIST`, `N-HERMES-MEMORY`, `N-HERMES-DELEGATE` and `N-HERMES-CRON` (surfaces per dated survey). **K IDs:** K-DOC,K-MEDIA,K-API,K-AUTO,K-TEST.
- **Installed/connected:** historic Hermes profile with **55 skills** returned by `skills_list` on 2026-11-21; list of exact names, activation today and account connection **UNKNOWN**. Git clone/push historically demonstrated in WebUI; `C-HERMES-GH` **VERIFIED_HISTORICAL_AGENT**. No Google Ads/WP/HeyGen production credential proven.
- **Environment:** WebUI shell separate from Hostinger VPS dashboard/container `0.22.5`. VPS dashboard healthy in historical observation, **live inference API not exposed**; n8n MCP disabled then. **Permissions:** safe analysis/own Git branch if authenticated; no production execution/paid inference. **Cost:** model/provider cost unknown, cost-control gate applies.
- **Proof:** [Hermes profile](../agents/hermes.md), [21 Nov survey](../reports/2026-11-21-hermes-capability-survey.md). **Verification:** historic bounded self-test only.
- **Fallback:** A1 offline code/QA, Work browser, Hostinger infrastructure; do not auto-route to Codex. Install candidates `I-HERMES-API` and `I-N8N-NODES` remain unproven and gated.

### AG-CODEX — Codex, exceptional task-specific
- **Role:** exceptional code/VPS architecture/integration work when A1/Work/Hermes/Hostinger cannot satisfy bounded constraints and A0 explicitly approves cost. **Suitable:** complex K-API/K-VPS/K-TEST infra or code *only after documented exception*; not default owner.
- **Native IDs:** `N-CODEX-SHELL`, `N-CODEX-GIT`, `N-CODEX-COMPUTER`, `N-CODEX-CODE` (dated Windows desktop survey). **K IDs:** K-PY,K-GIT,K-SCHEMA,K-TEST,K-SEC,K-API,K-VPS.
- **Installed/connected:** Windows PowerShell/Python/Git/ripgrep/Node/Computer Use historically **VERIFIED_HISTORICAL_AGENT (2026-11-21)**, with local Docker daemon blocked, `gh` credential degraded and direct VPS SSH untested. Exact installed ChatGPT skills in the current Codex session **UNKNOWN**.
- **Environment:** separate Windows desktop at survey time, **not** A1 container or active VPS. **Permission:** `CODEX_NOT_AUTHORIZED` by default; explicit A0 exception, scope, time/credit cap and audit required before invocation. **Cost:** UNKNOWN, treated nonzero/gated until quoted.
- **Proof:** [Codex profile](../agents/codex.md), [2026-11-21 native survey](../reports/2026-11-21-codex-capability-survey.md). **Verification:** dated historical; not invoked by DGN-2.
- **Fallback:** A1 Git/Python; Work UX/Linux; Hermes content; Hostinger hPanel. Install `I-CI` / `I-GITLEAKS` only if separate exception authorizes, never bootstrap Codex itself.

## 4. Current A1 skill inventory — declared IDs, not universal permissions

**A1 listing probe, 2026-11-24:** 92 skill URI entries: 5 base `docx,pdfs,spreadsheets,slides,skill-creator` and 87 plugin skills. Grouped observations: Supermetrics 14, vidIQ 14, HeyGen 22, OpenAI templates 20, Google Drive 5, other small tool/router categories. These numbers are **instruction catalogue entries**, not 92 authenticated services. The Plugin Management available *workspace* connection list returned **0**, which does **not** refute personal connectors, and it must not be reported as “all personal accounts disconnected.” Do not include account identifiers, OAuth, tokens, private assets or user PII in this public registry.

| Skill/tool ID | Source URI / namespace | A1 observed state | Minimum permission and safe proof | Scope/cost/STOP |
|---|---|---|---|---|
| `C-GITHUB-A1` | `mcp__GitHub__*` | **VERIFIED_CURRENT_A1** read, repo permission metadata, separate branch create | repo scoped `pull/push`; Git SHA + diff + readback | no main merge, public sanitized only |
| `C-DOCX` | `skills://docx` | INSTALLED_SKILL_LISTED | container test of harmless doc, render QA on demand | no private file upload |
| `C-PDFS` | `skills://pdfs` | INSTALLED_SKILL_LISTED | render, verify, edit on demand | redact secrets |
| `C-SPREADSHEETS` | `skills://spreadsheets` | INSTALLED_SKILL_LISTED | harmless workbook generation and QA | no private data |
| `C-SLIDES` | `skills://slides` | INSTALLED_SKILL_LISTED | PPTX generation and render QA | assets permission required |
| `C-SKILL-CREATOR` | `skills://skill-creator` | INSTALLED_SKILL_LISTED | read entrypoint, validated prototype only upon separate task | creation/install distinct operations |
| `C-GDRIVE` | `skills://plugins/google-drive/*`, `mcp__Google_Drive__*` | TOOL_EXPOSED_UNTESTED in DGN-2 | user-owned file scoped read only | file share/write gated |
| `C-GMAIL` | `mcp__Gmail__*` | TOOL_EXPOSED_UNTESTED | metadata-only query if specific task | no external send |
| `C-GCAL` | `mcp__Google_Calendar__*` | TOOL_EXPOSED_UNTESTED | read event permissions for specific task | no invites without approval |
| `C-WP` | `mcp__WordPress__*` / WordPress block skill | TOOL_EXPOSED_UNTESTED | staging read then controlled edit | live/publish gated |
| `C-SUPERMETRICS` | `skills://plugins/app-69a1247fceb88191a0fde719fd50920d/*` | INSTALLED_SKILL_LISTED, account connectivity NOT_RECHECKED | datasource/account discovery before data query | source permissions; costs and Ads writes gated |
| `C-VIDIQ` | `skills://plugins/app-69dd11f3e50c8191b1ca48d03cf7e2ad/*` | INSTALLED_SKILL_LISTED, prior channel **REPORTED_SESSION_HISTORICAL** | free profile/channel read before paid action | credits/publish gated |
| `C-HEYGEN` | `skills://plugins/heygen/*` | INSTALLED_SKILL_LISTED; render login/credit NOT_RECHECKED | model/cost quote and dry preview | no render or spend |
| `C-CANVA` | `skills://plugins/canva/*` | INSTALLED_SKILL_LISTED; project rights NOT_RECHECKED | asset list/read for scoped task | no external publish |
| `C-BIGQUERY` | `mcp__BigQuery__*` | TOOL_EXPOSED_UNTESTED in DGN-2; historic project list REPORTED | dry-run SQL / dataset listing | no billable query |
| `C-ADS-MCP` | `mcp__TTD_METAL_Google_Ads_MCP__*` | TOOL_EXPOSED_UNTESTED (verify naming/scope at task time) | list accounts read-only | no campaign edit |
| `C-ANALYTICS` | marketing tool/API connectors | TOOL_EXPOSED_UNTESTED | scoped source/query permission discovery | PII/privacy and cost gates |
| `C-PLUGIN-MGMT` | `mcp__Plugin_Management__*` | VERIFIED_CURRENT_A1 workspace connection *listing* (0 workspace links) | no install by this task | installation explicit owner action |

## 5. Installable capability backlog (never auto-install)

All rows below have **state `INSTALLABLE_CANDIDATE`**, not installed by DGN-2. No vendor billing account, plugin enablement, IAM, Docker image, GitHub workflow or production permission was changed. **Before any actual installation:** narrow WBS deficit; owner self-confirms OS/runtime/account; verify official source/license, pricing and security; approve required write/paid boundary; capture backup/lockfile; run sandbox test and rollback; record new evidence and unique installation decision. If these preconditions fail: `UNKNOWN` / `BLOCKED`, not "installed".

| Candidate skill ID | Capability added | Applicable agents / prerequisite | Required access | Cost / risk | Safe verification | Rollback / fallback |
|---|---|---|---|---|---|---|
| `I-PYTEST` | pytest fixture runner, focused parametric test/report | A1/Work; Python toolchain + pinned dependencies + isolated venv | local sandbox package install permission; no privileged pip | OSS license; install/network cost UNKNOWN, no vendor API | python -m pytest on harmless synthetic fixtures, compare unittest before/after | delete venv, restore lockfile; unittest remains fallback |
| `I-JSON-SCHEMA` | validate typed skills/task catalogs and metadata | A1/Coordinator; schema contract and parser need recorded | bounded Python/Node dependency and approved schema change | OSS; execution cost local, package supply-chain risk | schema validate valid/invalid catalog copies including duplicate IDs | revert schema/lock and keep existing deterministic validator |
| `I-GITLEAKS` | scan Git diff and history for secrets before PR | A1/Work; safe scan of public checkout, no secrets exposed in report | isolated executable; no GitHub secrets access | OSS; install/network and CI minutes UNKNOWN | dummy benign fake-secret fixture in isolated test tree; masked logs | remove binary/CI job; manual sanctioned secret review fallback |
| `I-GH-CI` | automated limited GitHub Actions checks for skill registry | A1/Coordinator; repo workflow rights, tested billing policy, scoped PR | A0/Coordinator approval for workflow creation; read-only repo token | GitHub Actions minutes/runner charges UNKNOWN | PR-only validator, no write credentials, fail closed on bad YAML | disable new workflow and revert YAML; keep manual checks |
| `I-PLAYWRIGHT` | repeatable browser UI smoke test/selector probe | Work; browser sandbox, consent, no account mutation | Work task-specific local executable and browser install | OSS browser download/runtime CPU; quota UNKNOWN | local static page accessibility/nav smoke test, no production login | remove test artifacts/browser install; Work manual visual QA |
| `I-AXE` | accessibility audit WCAG automated prompts/screens | A2/Work; approved UI test target, runner/browser working | read-only DOM in sandbox, no remote action | OSS core, integrations price UNKNOWN | synthetic screen with known issues gives findings | remove dependency; manual keyboard/screen-reader checklist |
| `I-TRIVY` | dependency/container vulnerability scan | Hostinger/Work; approved isolated source images or SBOM | read-only copy; never require prod Docker socket | OSS; CVE DB/network/storage cost UNKNOWN | scan inert SBOM and produce redacted finding | delete scanner/cache, restore prior SBOM workflow |
| `I-COMPOSE` | offline container compose/config validation | Hostinger; exact VPS/OS and safe staging compose source | Hostinger owner sandbox; any daemon production action separately approved | runtime disk/host costs UNKNOWN | docker compose config without deployment then sandbox health | delete sandbox stack and restore preflight; no production mutation |
| `I-UPTIME-KUMA` | uptime/health alert monitoring in approved sandbox | Hostinger; fresh infra inventory, private endpoints, alert privacy policy | Hostinger + A0 for paid/production or network exposure | self-hosted OSS; VPS compute/storage/alerts UNKNOWN | sandbox heartbeat with simulated outage and restore | remove sandbox/alerts, restore network configuration |
| `I-N8N-NODES` | safe n8n workflow connectors/idempotence | Hermes/Hostinger; workflow/schema approval, prod MCP status checked | sandbox only; production enable separately approved | community nodes may be paid/risky; UNKNOWN | mock webhook, replay/timeout/negative retries and receipts | disable/delete sandbox workflow; restore snapshot |
| `I-HERMES-API` | stable authenticated Hermes inference adapter | Hermes/Hostinger; prove real agent inference endpoint exists, privacy and auth | new exposed API/secret/network requires separate security approval | model tokens, compute and SLA UNKNOWN, likely metered | private sandbox mock then real opt-in low-cost probe with budget cap | disable adapter and revoke sandbox token; n8n mock fallback |
| `I-DOC-QA` | deterministic document traceability checker | A0 Assistant/Coordinator; A0 Assistant session confirms native tool availability | only public sanitized DGN docs; no credential assumed | local script $0 API if executed offline; runtime UNKNOWN | compare exact WBS/skill cross-refs, deliberately missing reference negative | remove optional script, manual A0 review retained |
| `I-SEO-READ` | read-only WP/GSC consistency report | A1/A2; owner grants read-only staging/source and data scopes | no WordPress write or indexing changes | connector quota/cost UNKNOWN | single preapproved record compare against known source with redaction | disconnect added connector or stop report; manual browser read |
| `I-MEDIA-REVIEW` | non-publishing video QA pipeline/metadata | A2/Hermes; approved source media/license and device/credits quote | local video probe only; paid render separately approved | FFmpeg OSS; video AI credits UNKNOWN | offline format/silence/subtitle check on harmless sample | remove temporary outputs; keep original assets |
| `I-VIDIQ-RESEARCH` | YouTube keyword/packaging analytics | A1/A2; vidIQ connected channel and credits available in actual session | read-only metadata and exact credit consent for metered call | credit pricing and remaining balance UNKNOWN today | free channel metadata first; optional authorized 1-call capped research | stop paid query, delete draft/watchlist changes with approval |
| `I-WORKSPACE-REPORT` | Drive/Sheets-based WBS capability dashboard | Coordinator/A1; actual file-level permissions and privacy approved | create file only in authorized folder, no sharing changes | Workspace plan/quota UNKNOWN | sandbox sheet with fake skills and formulas, view-only QA | delete test file with consent or archive; Markdown registry fallback |

**Prioritize:** First reuse native/tools already confirmed within a *specific owner session*. `I-JSON-SCHEMA`, `I-PYTEST`, `I-GITLEAKS` are lower risk candidates for isolated tests but remain uninstalled; `I-COMPOSE`, `I-HERMES-API`, `I-N8N-NODES`, `I-UPTIME-KUMA` need infrastructure security/cost gates; any credit-consuming creative/video operation requires a separate preflight quote and limit. This inventory is not a procurement order.

## 6. WBS-to-capability usage and reviewer/fallback rules

Use exact historical WBS IDs from [WBS](WORK_BREAKDOWN.md), *not* a newly activated task. Examples:

| WBS / deliverable | Skill requirement | Candidate primary / alternative | Minimum environment and evidence | Risk / reviewer |
|---|---|---|---|---|
| G0-01, G0-02 | K-DOC,K-DATA,K-UX | A2 / Coordinator for business cross-check | A2 actual session, product brief, referenced screen/actor spec | A0 Assistant package review; Work UX feasibility |
| G1-01 to G1-03 | K-GIT,K-PY,K-SCHEMA,K-TEST,K-SEC | A1 / Work if separate author | GitHub scoped branch, Python fixture and SHA readback | Work independent code QA |
| G1-04 | K-QA,K-TEST,K-DATA | Work / A0 Assistant for separate policy view | full source checkout and blind test protocol | author cannot grade own code |
| G2-01,G2-03,G3-02,G3-03 | K-ORCH,K-DOC,K-SEC,K-GIT | Coordinator / A1 evidence-only | explicit source authority and actual session ACK | A0 decision for merge, separate review |
| G2-02,G3-A1 | K-PY,K-SCHEMA,K-GIT,K-TEST | A1 / Work as fallback | safe offline fixtures, no service launch | Work review of A1 code |
| INF-01 to INF-04,SEC-H,WP-H | K-VPS,K-OBS,K-BACKUP,K-SEC,K-N8N | Hostinger / Work read-only audit fallback | hPanel actual session + backup/restore evidence | A0 gate for changes; independent QA |
| UI-01,UI-02,CTRL-01 | K-UX,K-BROW,K-API,K-TEST,K-SEC | Work / A2 UX specification fallback | Work actual Computer Use/browser + test receipts | privacy/real-session gate |
| UC01-01,UC01-02,QA-U01 | K-WP,K-SEO,K-PY,K-DATA,K-QA | A2 audit, Work integration, A1 independent sample | authorized WP read, evidence sample, staging | no live publish |
| GROW-01,GROW-03 | K-ADS,K-DATA,K-API,K-SEC | A2 analysis, Work dashboard, A1 data audit | permission-proven GA4/Ads source, freshness | no budget or bid writes |
| GROW-02 | K-MEDIA,K-DOC,K-UX,K-SEC | A2 creative spec, Hermes scripts, A1 QA | licensed source, preview, no paid render | human approval before publish |
| REL-01,REL-02 | K-QA,K-SEC,K-GIT,K-DOC | Coordinator synthesis / human A0 decision | independent verdict, exact SHA and readback | A0 authority retained |

**Do not transfer owner:** Directory gives *possible* match, not new WBS owner; Coordinator exclusively changes assignment policy and destination roadmaps. No task will be sent from this file.

## 7. Reproducible operator checklist (manual, read-only)

1. Read authoritative main rules; pin **current main SHA** and exact candidate source. Identify WBS ID, task's author and reviewer.
2. Resolve each `K-*` to the canonical table above; for selected Agent check **its own actual-session** skill list, account connection, OS/browser/CLI, permission, credential scope and cost **without testing paid operations**.
3. Require evidence URL/commit SHA or native tool result; distinguish `VERIFIED_CURRENT_A1`, historic `VERIFIED_HISTORICAL_AGENT`, `TOOL_EXPOSED_UNTESTED`, `INSTALLED_SKILL_LISTED` and `INSTALLABLE_CANDIDATE`. Query nobody's private account by assuming A1 OAuth extends to other Agents.
4. Run a safe mock or read-only acceptance probe. STOP if account/OS missing or public-Git privacy risk; record UNKNOWN and use fallback rather than falsely marking success.
5. Coordinator produces one accountable owner, actual work-order/ACK and independent reviewer on its own authorized source. A0 retains final approval. After actual installation, *that Agent* updates its survey with timestamp, version/URI/permission/credit test and rollback evidence; A1 does not verify for them.

## 8. Evidence provenance manifest (immutable refs and freshness)

| Evidence ID | Immutable source or direct probe | Evidence state / applicability |
|---|---|---|
| `E-MAIN-20261124` | main `d549564de52429e777c68daf9df7a93df5f22f27`, Git tree 297 entries | VERIFIED_CURRENT_A1 main source, not live production |
| `E-COORD-DGN` | [Coordinator accepted design roadmap @ab0e728](https://github.com/DuyKienTTD/Hosting/blob/ab0e728f6f1c698dc7d2fd8dcae6e8bad94dc125/program/roadmaps/coordinator.md) | pinned planning authority, **not** Agent session capability |
| `E-GH-A1-20261124` | GitHub get_repo pull/push and branch `a1/dgn2-capability-directory-2026-11-24` created from main | VERIFIED_CURRENT_A1 scoped Git operation |
| `E-SKILLS-A1-20261124` | skills list: 92 URIs / five first-party / 87 plugin skills; no skill invocation or app installation | INSTALLED_SKILL_LISTED |
| `E-CONNECTION-20261124` | Plugin Management workspace connections list: zero links | verified list of workspace links only; personal app connections untested |
| `E-AGENT-A1` | [A1 historical profile](../agents/a1.md) | REPORTED_SESSION_HISTORICAL; current Git read confirmed separately |
| `E-AGENT-COORD` | [Coordinator historical profile](../agents/chatgpt.md) | REPORTED_SESSION_HISTORICAL |
| `E-AGENT-A2` | [A2 roadmap](roadmaps/a2.md), no dedicated `agents/a2.md` as of main baseline | ROLE_ASSIGNED_ONLY; session self-survey MISSING |
| `E-AGENT-WORK` | [Work roadmap](roadmaps/work.md), [Work PR42 independent QA](https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7103815886) | VERIFIED_HISTORICAL_AGENT for specific QA, not current Work OS/connectors |
| `E-AGENT-A0-ASST` | Coordinator DGN independent-review contract | ROLE_ASSIGNED_ONLY; no dedicated profile nor live self-ACK |
| `E-AGENT-HOSTINGER` | [Hostinger historical survey](../agents/hostinger.md), [inventory](../reports/2026-11-21-hostinger-account-capability-inventory.md) | VERIFIED_HISTORICAL_AGENT for dated hPanel observations |
| `E-AGENT-HERMES` | [Hermes dated survey](../reports/2026-11-21-hermes-capability-survey.md), [profile](../agents/hermes.md) | VERIFIED_HISTORICAL_AGENT for dated WebUI session, no live inference |
| `E-AGENT-CODEX` | [Codex dated survey](../reports/2026-11-21-codex-capability-survey.md), [profile](../agents/codex.md) | VERIFIED_HISTORICAL_AGENT; `CODEX_NOT_AUTHORIZED` |
| `E-WBS-32` | [WBS original 32 IDs on main](WORK_BREAKDOWN.md) | historical assignment mapping, not active dispatch |

## 9. DGN-2 completion conditions / unresolved external evidence

**Author scope done when:** eight Agent rows present, all canonical WBS skill IDs mapped, skill state/URI/cost/permission/STOP explicit, every install candidate has verification/rollback, no other-Agent false VERIFIED, all links/IDs validate, independent Coordinator can consume directory for DGN-3/DGN-4. **Still independent:** own-session capability check by A0 Assistant/A2/Work/Hostinger/Hermes/Codex/Coordinator; A1 cannot force their session ACK or discover their private installed credentials. This is a **known validation dependency**, not grounds to invent active permissions. No production/paid calls, installation or merge from DGN-2.

**Fallback if an Agent cannot self-survey:** use historic profiles as `REPORTED_SESSION_HISTORICAL` for preliminary design routing; require **actual session tool proof** before making executable assignment. Coordinator may ask A0 for one package-level decision after full DGN review, never for each directory line.

