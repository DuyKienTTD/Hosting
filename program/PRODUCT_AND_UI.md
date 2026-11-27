# DGN-1 — Product Charter & Operator Console design specification

**Artifact:** OPT-01 / DGN-1 · **Owner:** A2 (ChatGPT Standard) · **Status:** DESIGN_COMPLETE_NOT_IMPLEMENTED · **Date:** 2026-11-24 (Asia/Ho_Chi_Minh)  
**Source baseline:** merged `main@d549564de52429e777c68daf9df7a93df5f22f27`. **Design branch:** `a2/dgn1-product-operator-ui-2026-11-24`.  
**Authority:** A0 four-outcome directive PR43 #7108702342 and coordinator roadmap `ab0e728f6f1c698dc7d2fd8dcae6e8bad94dc125` (blob `17c7cf823090931eafa0109e7d43f44019115260`). Explicit DGN-1 authorization supersedes historic *planning hold only for design*; does not activate any operational G0/UC01/Ads/infra task, merge or product build. Design proposal, **not live capability or permission**.

## 1. Product charter and business outcomes (G0-01)

**Product:** TTD METAL AI Business Automation Platform with a human-operated, auditable **Operator Console** to convert authorized goals into evidence-based work across WordPress/WooCommerce/SEO, Ads/attribution, media/social, reporting and infrastructure dependencies. Existing ChatGPT Standard A1/A2, ChatGPT Work, Coordinator, independent A0 Assistant and external specialist sessions remain actors; they are not replaced with paid API replicas. **Session/Agent Controller is supporting capability, not a prerequisite for useful read-only business work.** n8n is runtime/orchestrator, **not** an AI Agent. GitHub is source/evidence store, not a live scheduler or real-time presence detector.

**Problem:** goals, task ownership, skills, approval/STOP, cost and artifact evidence are dispersed across GitHub/Agent sessions; an operator cannot reliably distinguish planned, dispatched, acknowledged, tested, approved and truly live. This increases duplication, stale status and risk of unauthorized side effects.

**Value hypotheses (not validated):** (O1) see one truthful next action per goal; (O2) reduce repeated reads, task recreation and status chases; (O3) make protected side effects impossible through UI without approval and independently observed receipts; (O4) prove usefulness with one read-only business audit before any paid or publishing workflow; (O5) reconcile accepted deliverables with measurable business outcomes.

**Primary non-goals for MVP:** agent autonomous session control, always-on service claims, executing plugins/VPS from UI, paid inference, live Ads bid changes, WordPress publication, automated merge, full marketing suite, social publishing, a simulated dashboard masquerading as production. This document defines **interfaces and test contracts only**.

### 1.1 Users/personas, decisions, and authorization

| Actor | Job-to-be-done | View scope | Proposed actions | Explicitly forbidden without separate gates |
|---|---|---|---|---|
| **A0 / Owner** | Prioritize outcomes and approve material risks | All authorized portfolio summaries, redacted evidence, spend | Submit/approve goals, set budget ceiling, grant bounded approval, issue STOP/revoke, sign roadmap-level acceptance | Implicit approval from UI state or GitHub document; automatic production action |
| **Chat Điều phối / Director** | One accountability chain and effective roadmap | Program, WBS, agent capabilities, approvals/evidence | Draft/scope/route work, reserve exclusive writer, propose assignment, request human review, record real handoff | Sign A0-only paid/production/merge approval; forge ACK |
| **A0 Assistant / Independent reviewer** | Challenge strategy/governance decisions | Read-only proposed design, provenance, acceptance | Record independent verdict and source-linked objections | Author same artifact under review, execute decisions or grant authority |
| **A1 / Technical execution** | Complete assigned source/metadata tasks | Own assigned tasks, pinned sources and sanitized evidence | ACK, propose code/doc changes in authorized branch, self-QA, handoff | Merge, change another sole-writer path, self-certify independent QA |
| **A2 / Product UX/data** | Define product, data and business acceptance | Own roadmap/artifacts, required sanitized business context | Draft charter, UI and data contract, evidence and roadmap status | Business account writes or claim installed tools unverified |
| **ChatGPT Work** | Multi-step integration/UX, independent QA when not author | Own assignments, approved UI feasibility/read evidence | Review, execute scoped tasks after ACK, record test evidence | Author source and independently grade that same artifact; unapproved live/paid |
| **Hostinger / Hermes / Codex (conditional)** | Specialized infra/runtime/technical work | Only explicitly granted read set | Scoped response after actual session ACK and clearance | Auto-activation from capability registry, historical HOLD, or GitHub event |
| **Business operator** | Review business progress and exceptions | Least-privilege assigned business module, sanitized aggregate KPIs | Submit drafts/request changes; approve only if specifically delegated | Provider secrets, cost ceilings, release/production/merge by default |
| **Security/auditor (future)** | Review why operations were accepted | Immutable decision/receipt and redacted audit history | Export authorized evidence, flag exceptions | Modify events or infer live state from historical snapshot |

**Permission model:** deny-by-default RBAC with scope/resource/action and risk attributes (ABAC), server-side enforcement; UI hiding alone is NOT authorization. `viewer`, `draft_editor`, `assigned_executor`, `independent_reviewer`, `director`, `owner_approver`, `auditor` may be combined only with explicit grants and segregation checks. Every side-effect request binds actor identity, resource, action, environment, cost cap, expiry, source pin, approval receipt and reason. Approval is not transferable, cannot be inferred from task text, and is revoked on source/target/cost drift.

### 1.2 Scope ranking, roadmap and dependencies

| Phase | Purpose / required design outcome | Dependency / release boundary |
|---|---|---|
| **M0 — Truthful governance foundation (P0)** | Authoritative source links, scoped roles, capability evidence, goals/WBS/roadmaps, read-only snapshot, receipts/STOP | This DGN-1 charter → DGN-2 capabilities → DGN-3 WBS → DGN-4 authorized assignment; design review gate |
| **M1 — Business read-only pilot (P1)** | Repeatable WordPress/Woo SEO gap audit, errors and UNKNOWN surfaced, evidence-linked recommendations | Explicit account read authorization, measured baseline and independent QA; **not activated now** |
| **M2 — Operator UI MVP (P1)** | Authenticated real-data dashboard/goal/queue/evidence/approval **read-only first**, later guarded write integration | Separate product-build permission, backend data contract, RBAC and independent usability/security QA |
| **M3 — Orchestration (P2)** | Actual session handoff/ACK, durable event/status, guarded retries and callbacks | Verified provider/session mechanics, source of truth, idempotency, recovery; no assumed always-on session |
| **M4 — Business expansion (P2)** | Ads attribution baseline, media/social approval drafts, multi-channel reporting | Consent, external permissions, privacy/measurement proof and separate publish/paid approval |
| **M5 — Reliable live operation (P3)** | Incident, monitoring, restore tests, SLO and out-of-band STOP | Real infra preflight, tested rollback, independent security/reliability evidence |

**MVP slice:** a signed-in operator can inspect a source-pinned goal, inspect owner/skills/dependencies/unknowns, propose a task, inspect *prepared vs actual ACK*, find acceptance evidence, and route a sensitive change to approval without executing it. Read-only synthetic seed data must be explicitly marked **DEMO**. The first valuable end-to-end *business* MVP outcome is one independently verified read-only audit, not completion of an Agent Controller.

### 1.3 KPI measurement contracts (all baselines UNKNOWN)

| KPI / outcome | Numerator/denominator or metric | Authoritative evidence / frequency | Missing-data behavior |
|---|---|---|---|
| O1 Decision findability | % sampled operator tasks locating correct owner+next-action+STOP in ≤3 navigational transitions | UX task test events / each usability study | `NOT_MEASURED`; don't claim target achieved |
| O2 Handoff integrity | actual `ACKNOWLEDGED` receipts / real `SENT` attempts (only verified) | Immutable handoff events with session IDs / daily if instrumented | Prepared tasks excluded; stale = UNKNOWN |
| O2 Cycle time | median and p90 from verified ACK to accepted evidence, by class | Event ledger timestamps / weekly | No receipt => no duration; report coverage |
| O3 Authorization safety | count of unapproved externally effective changes (goal **0**, not measured) | Independent audit trail + target provider reconciliation / per change | Missing audit = UNKNOWN/NO_GO, never zero |
| O4 Business audit utility | accepted actionable findings / independently reviewed findings; false positives | WP read-only source snapshots, reviewer decision / each pilot | Evidence/permissions absent => NOT_MEASURED |
| O5 Business impact | attributed qualified leads/conversions and cost per accepted result | GA4/GSC/Ads/CRM authoritative accessible data / agreed weekly window | No fabricated baseline, flag attribution gap |
| Cost | verified provider billed costs and forecast by scope | Invoice/API and immutable budget decision / daily when permitted | Distinguish estimate, approved ceiling, incurred billed, unknown |
| UX and accessibility | scripted task success rate, keyboard completion, contrast errors | Controlled tests / each major UI design release | DESIGNED_NOT_TESTED before build |
| Reliability/observability | freshness lag, unknown states, incidents, MTTR, backup restore evidence | Independent service telemetry / once enabled | Historical-only status NEVER live healthy |

For every metric record `value|null, status(VERIFIED/REPORTED/ESTIMATED/UNKNOWN/NOT_MEASURED), unit, time_window, collected_at, observed_at, source_url_or_ref, source_sha_or_version, owner, denominator, filter, calculation_version`. Do not treat absence as zero. Targets and SLA require an A0 decision after baseline.

## 2. System boundary and information architecture (G0-02)

**Primary nav (desktop left rail / mobile compact navigation with breadcrumbs):**
`Overview → Goals → Tasks & Dependencies → Agent Roadmaps → Skills & Candidates → Assignments & Sessions → Approvals & STOP → Evidence & Status → Costs → Integrations → Business Modules (WP/SEO, Ads/GA4, Media/Social, Reports) → Settings/Access`.
Universal secondary actions: global search by ID, environment badge `DESIGN/DEMO/OFFLINE/STAGING/LIVE`, source-age indicator, active-goal breadcrumb, "Open source evidence", accessibility options, readonly mode and emergency STOP for authorized user.

**Data plane separation:** GitHub immutable commits/PRs/roadmaps and approval evidence; typed proposal/assignment status; actual authenticated session receipts (distinct from GitHub events); external service telemetry via authorized connectors; aggregate business KPIs with provenance; cost from verified invoice source; never create false fused "healthy" status. Design client never directly stores provider credentials. Read-only view is feasible from sourced snapshots; writes and real-time session operations are separate unbuilt backend capabilities.

### 2.1 Shared semantic state contracts

- **Evidence confidence:** `VERIFIED_LIVE`, `VERIFIED_OFFLINE`, `VERIFIED_MOCK`, `REPORTED`, `DESIGNED`, `UNKNOWN`, `STALE`, `BLOCKED_ACCESS`. Must display label + timestamp/source. No mock-to-live promotion.
- **Task lifecycle:** `PROPOSED→PREPARED→SENT→ACKNOWLEDGED→IN_PROGRESS→DONE_WITH_EVIDENCE→INDEPENDENT_QA(if risk)→READY_FOR_ROADMAP_ACCEPTANCE→ACCEPTED`; alternatives `NEEDS_OWNER_DECISION`, `BLOCKED`, `INTERRUPTED`, `CANCELLED`, `REJECTED`. `SENT` requires actual transport receipt; `ACKNOWLEDGED` requires **recipient session** receipt; `DONE` needs checked evidence; `ACCEPTED` needs actor-authorized decision; no timestamp backfill by inference.
- **Approvals:** `REQUESTED→UNDER_REVIEW→APPROVED|DENIED|EXPIRED|REVOKED`; approval includes scope, immutable candidate/version, cost max, expiry, actor, explicit recorded action. After drift => `REVALIDATION_REQUIRED`. A0 owns material exception; no approval inferred from content or author self-check.
- **Assignments:** `CANDIDATE→CAPABILITY_CHECKED→PROPOSED_OWNER→PREPARED_HANDOFF→ACTUAL_ACK`; exactly one accountable owner per active work item, candidate/fallback never auto-executes.
- **Unknown and errors:** `UNKNOWN` means evidence missing; `ERROR` is a verified failed attempt; `OFFLINE` is observed lost connectivity; `STALE` is dated old read. UI NEVER replaces unknown with "all green".
- **Concurrency:** require optimistic `version/etag` for mutations, dedupe operation ID, idempotent command semantics where supported; stale tab conflict displays changed fields/source and asks rebase, no silent last-writer-wins.
- **Access denial:** 403 shows action not permitted, not a technical outage; 401 redirects to re-auth without losing safe unsent draft; 409 conflict requires reload; timeout/5xx shows UNCERTAIN result and prohibits automatic non-idempotent retry.

### 2.2 Proposed logical entity dictionary (no deployed schema)

| Entity / stable key | Essential fields | Source of truth and trust limitation |
|---|---|---|
| `Goal(goal_id)` | owner, outcomes, KPI contract, scope, environment, priority, version, evidence | Owner decision + linked Git; proposal alone not approval |
| `WBSItem(wbs_id)` | outcome_id, feature_id, skills, prerequisites, risk, target_roadmap, acceptance | Coordinator-owned WBS and source SHA |
| `AgentProfile(agent_id,session_key)` | capability evidence, tool availability, environment, costs, last_verified | Agent self-survey; other Agent cannot assert VERIFIED |
| `Skill(skill_id)` | name, minimum_tool, native/connected/installable, rights, cost, proof, fallback | A1 evidence inventory, not a permission issuer |
| `Task(task_id)` | goal, WBS, owner, read/write sets, source_sha, stop, acceptance, lifecycle revision | Exclusive author task + immutable events |
| `Assignment(assignment_id)` | task, primary_owner, candidates, capability_ref, dispatch readiness | Coordinator decision, not session action |
| `HandoffReceipt(receipt_id)` | task, from/to session, channel, SENT/ACK state, signed/observed timestamp | Actual transport/session observation only |
| `Roadmap(roadmap_id)` | agent, items, status, source SHA, evidence links, next_action | Each agent owns its own roadmap |
| `Evidence(evidence_id)` | object, immutable URI/SHA, claim, confidence, timestamp, reviewer, redaction | Git/provider verifiable artifact; source-age policy |
| `Approval(approval_id)` | resource/action/version, environment, max cost, A0 actor, expiry, decision | Independent approval ledger; never UI-local toggle |
| `CostRecord(cost_id)` | source/provider, currency, estimate/approved/billed, time window, freshness | Provider invoice or verifiable billing; no inferred spend |
| `Integration(integration_id)` | service, permissions metadata, health/readiness, last observed, failure domain | Scoped connector observation, no credential values |
| `BusinessFinding(finding_id)` | audit scope, URL/object, source timestamp, issue, impact, recommendation, review status | Read-only WP/Ads source; identity/PII sanitized |
| `AuditEvent(event_id)` | who, when, what, object version, operation/result, evidence and correlation | Append-only tamper-evident service to be designed later |

All models need `schema_version`, `observed_at`, `recorded_at`, `source_version`, `confidence`, `environment` and provenance where meaningful. Event ingestion requires authenticated origin; client-side mock receipts are not accepted.

## 3. Screen-by-screen functional design & acceptance traceability

**Notation:** `G#` goal outcome O1–O5 above; `V` viewer; `D` director; `A0` owner; `X` assigned executor; `R` independent reviewer; `B` business operator. Each screen links outcome, actor/permission, navigation, data, action, state, KPI and test ID. Shared negative-state matrix §3.2 applies to every screen.

| ID / screen / outcome | Actor & permission | Entry → data source | Permitted actions → state effect | KPI / audit & concrete acceptance |
|---|---|---|---|---|
| **S01 Overview / O1,O3** | V read; D/A0 scope filter | Home; goals, evidence-index, verified receipts, cost/health snapshots | Drill to blocked goal or pending approval; no mutating external action | `T01`: for stale mocked source displays UNKNOWN and source age; no green LIVE label; find next action ≤3 hops in tested navigation; audit access optional |
| **S02 Goals / O1,O5** | A0 submit/approve; D draft; V read | Goals → goal record, KPI contract, decision events | Create DRAFT proposal; A0 authorizes scope; accepted goal version increments; no task automatically dispatched | `T02`: goal lacking owner/KPI source cannot become APPROVED; retain immutable goal approval event; metric UNKNOWN |
| **S03 Tasks & Dependencies / O1,O2** | D assign proposal; X own progress; V read | Goal → WBS/task detail, blockers, source_sha and acceptance | Draft task, pick linked WBS, see dependency DAG, propose status; actual ACK only from session receipt | `T03`: one accountable owner, blocked dependency stops dispatch, PREPARED not ACK; audit revision |
| **S04 Agent Roadmaps / O1,O2** | X edit own; D inspect; R assess; A0 accept milestone | Agent → own roadmap, item source and evidence | Own status with evidence + next_action; independent review; roadmap-level acceptance only | `T04`: other agent cannot edit; DONE cannot lack evidence; old HOLD item stays HOLD |
| **S05 Skills & Install Candidates / O2,O3** | V inspect; A1 source-author only on grant; D propose | Skills → self-survey proof and source SHA | Compare verified/native/connected vs installable; propose installation review (NOT install) | `T05`: unverified connector never shown INSTALLED; matching rejects unproven mandatory skill; source freshness visible |
| **S06 Assignment & Agent Sessions / O2,O3** | D propose; designated sender send if authorized; X actual ACK | Task → agent capability & handoff event store | Candidate match, reserve writer, prepare dispatch; show SENT and actual ACK only with separate receipts | `T06`: Git commit alone PREPARED, session not live=UNKNOWN, no invented automation; duplicate receipt detected |
| **S07 Approvals & STOP / O3** | A0 approve/deny/revoke; D request; V read | Risk queue → bounded proposal + decision ledger | Sign time/scoped approval or deny; emergency STOP prevents further permitted side-effects | `T07`: changed commit/target/cost invalidates approval; denied/expired never enables action; decision audit immutable |
| **S08 Evidence & Status / O1,O3** | V read scoped; R review; X attach own | Task → Git blob/PR/provider receipt and trust label | View/download authorized redacted proof, flag stale/contradiction, R record independent verdict | `T08`: evidence with missing SHA shows UNKNOWN not PASS; mock always tagged; author cannot self-approve |
| **S09 Costs / O3,O5** | A0 ceiling & approve; D draft; V read filtered | Costs → cost records by source/time | Compare forecast/ceiling/billed; proposal for budget change only | `T09`: absent provider invoice = UNKNOWN, not zero; currency/unit/window shown; limit breach blocks paid command |
| **S10 Integrations & Health / O3** | Admin integration view scoped; V sanitized read | Integrations → connector permission metadata, timestamps/health | Inspect scope, propose re-auth; no direct credential display or production restart | `T10`: stale heartbeat != healthy, health ≠ inference success, secrets never rendered or logged |
| **S11 Business Modules / O4,O5** | B analyst/view; X authorized scoped read; A0 publish gate | Business → WP/SEO, Ads/GA4, Media/Social, Reports; separate provenance | Inspect drafts/audit findings/attribution, request review; no publish/Ads write from design | `T11`: each finding source-linked and status-qualified; unsupported data UNKNOWN; publish button disabled absent future gate |
| **S12 Access & Settings / O3** | A0/authorized admin; V own preferences | Settings → role grants, audit and retention policy metadata | Request grant, change personal display prefs; permission grant itself needs approved admin action | `T12`: simulated privilege escalation denied server-side, sensitive values masked, audit retained |

### 3.1 Detailed operator journeys / state changes

**J01 Goal-to-accepted-deliverable (MVP workflow):** A0 submits goal draft with business outcome/KPI/source → D maps to existing/new WBS and skill demand → matches evidenced capability (or flags gap as `NOT_VERIFIED`) → proposes sole owner + independent QA where needed → reserves authorized writer/read/write set and source HEAD → creates task `PREPARED` → human/verified channel `SENT` → recipient real session `ACKNOWLEDGED` → agent executes within scope and self-updates roadmap with time/evidence → independent R reviews risk-bearing output → D bundles roadmap acceptance → A0 approves material decision. **Exception:** without dispatch channel, stay `PREPARED_FOR_OWNER_FORWARD`; never fake ACK or DONE. **Evidence:** every boundary has event/ref/actor/UTC. **UI tests:** T02,T03,T04,T05,T06,T08.

**J02 Sensitive approval:** proposed paid/production/publish action opens approval request with exact target, commit SHA, scope/cost/expiry, impact and rollback → A0 can approve/deny/revoke → server revalidates effective grant at dispatch time → only a separately authorized future backend performs side effect → receipt captured. Any changed source/target/ceiling => `REVALIDATION_REQUIRED`; outage => `UNKNOWN`, not success. **Tests:** T07,T09,T10,T13.

**J03 Blocker and parallel continuation:** one task missing permission → show `BLOCKED_ACCESS` with owner/freshness/required grant; unrelated safe work retains independent active lane; D sees bottleneck and possible fallback without auto-reassignment. Escalate unresolved material exceptions at roadmap level; no per-item A0 microapproval. **Tests:** T03,T04,T14.

**J04 Business read-only pilot:** authorized scoped WordPress read (future) → source snapshot per page/product/post (URL/ID/date) → findings with severity/uncertainty/EN-VI source distinction → reviewer challenges false positives → read-only UI displays plan and evidence → potential edits only through later distinct approved task. **Tests:** T11,T15. No WordPress was read by this DGN-1 task.

**J05 Incident/STOP:** health signal stale/failed → display provenance and `UNKNOWN/DEGRADED` → authorized A0 STOP request → immutable event receipt and confirmation of actual enforcement checked separately; until confirmed show `STOP_REQUESTED_NOT_CONFIRMED`. No false safe state. **Tests:** T01,T07,T10,T16.

### 3.2 Mandatory screen states (apply S01–S12)

| State | UI pattern | Action/side-effect rule | Test |
|---|---|---|---|
| LOADING | skeleton with explicit loading/time limit; previous snapshot labelled old | No destructive action queued silently | T17 |
| EMPTY | actionable 'No sourced records yet', not zero KPI | Offer create draft only with permission | T18 |
| ERROR | retry-safe diagnostic category, correlation ID; sanitized | No automatic non-idempotent retry | T19 |
| UNKNOWN / STALE | neutral status and source timestamp; explicit why unknown | Cannot enable paid/prod/publish | T20 |
| BLOCKED_ACCESS / PERMISSION_DENIED | exact missing permission category, no sensitive detail | Forbidden controls inaccessible in backend | T21 |
| OFFLINE | cached read-only view with last-fetched time; mutation disabled | No fabricated ACK/approval, no offline side-effect queue | T22 |
| CONFLICT / DUPLICATE | previous/current version diff and idempotency/reference | No overwrite, no duplicate real command | T23 |
| MOBILE / KEYBOARD / ASSISTIVE | 320–1280 responsive layout, semantic labels, visible focus; no hover-only affordance | All approvals/STOP have accessible confirmation | T24 |

**Accessibility specification:** WCAG 2.2 AA target; keyboard full path, skip-to-main, semantic heading/landmarks, focus order and error announcements, adequate contrast, text resizing to 200%, reduced motion, descriptive status not color-only, tap targets ≥24×24 CSS pixels with spacing, locale Vietnamese UTF-8/diacritics and locale-aware date/currency, UTC timestamp available. Validate with real users and assistive technologies after build, not asserted PASS today.

**Responsive:** desktop two/three-panel with persistent left rail and detail sidepanel; tablet collapsible rail; mobile bottom/overflow nav + single column, sticky visible critical STOP/approval context, expandable tables and no horizontal trap. Empty/error/UNKNOWN remain visible at all breakpoints; do not hide risk notices in overflow menus.

## 4. Cross-cutting nonfunctional/security requirements

1. **Authorization:** server-side per object/action, source-bound approval, least privilege, no dangerous affordance based only on CSS. Separate read-only anonymous demo from authenticated real console. Isolation per tenant/resource and independent reviewer segregation.
2. **Secrets and privacy:** never commit/render API keys, cookies, bearer tokens, internal hostnames/IP, customer PII or raw logs in public Git; only sanitized aggregate IDs, ref links and permission metadata. Define retention/deletion in future security spec, record current value UNKNOWN.
3. **Trust/observability:** source SHA, observed vs recorded time and evidence type everywhere; data older than configured freshness threshold STALE, threshold requires measured baseline. Independent monitoring channel and clear uptime UNKNOWN.
4. **Durability:** save drafts only in an approved future service; opt-in state persistence and idempotency contract, backup/restore exercised before declaring live. Git README/STATE is not an append-only execution ledger.
5. **Performance targets (design hypotheses):** p95 list navigation ≤2 s and detail ≤3 s under specified network/device fixture; backend read p95 TBD; source freshness per integration TBD. No claim of measured latency until tests.
6. **Internationalization:** Vietnamese first, English-ready terms, consistent translation keys, timezone/units configurable, no hard-coded locale in stored timestamps.
7. **Safety/STOP:** no product build, deploy, WordPress/Ads/media write, paid API, production access, merge or historical HOLD reactivation from this design. All these remain `NOT_AUTHORIZED`.

### 4.1 Proposed API/action contract for future implementation (not endpoints deployed)

`GET /goals|tasks|roadmaps|agents|skills|evidence|approvals|costs|integrations` returns scoped records with `source_version, observed_at, confidence, next_cursor`. Command-shaped actions (e.g. `POST /drafts`, `POST /handoffs/prepare`, `POST /approvals/request`) must be versioned, authenticated, idempotent where supported and produce signed/verifiable receipts. **No dispatch endpoint is assumed.** `POST /handoffs/ack` only from verified recipient channel; `POST /decisions` requires owner-signed authority. Every side-effect command requires preflight, explicit risk/approval, bounded cost, external reconciliation and independent QA; design-only system has NONE of these operations.

## 5. Acceptance verification plan (DESIGNED_NOT_RUN)

**Trace contract:** every S01–S12 row explicitly maps `OUTCOME→ACTOR/PERMISSION→ENTRY/NAV→DATA_SOURCE→ACTION/STATE→KPI→AUDIT/EVIDENCE→TEST`. Shared states cover loading/empty/error/UNKNOWN/blocked/offline/permission-denied/mobile. `T01–T24` are design test IDs, **0 executed**.

| Test | Hypothetical fixture and assertion | Required future evidence |
|---|---|---|
| T01 | Old snapshot cannot display LIVE green; owner+next_action found in ≤3 UI hops | Screens/interaction trace + timestamp |
| T02 | KPI-less goal rejected from APPROVED; approval event actor/version retained | API fixture + audit event |
| T03 | Missing dependency and duplicate owner stop dispatch | State diff + rejected transition |
| T04 | Other actor fails roadmap update, DONE without evidence blocked | RBAC negative test + Git/source ref |
| T05 | Installable/unverified skill cannot satisfy verified-capability requirement | Matching result/provenance |
| T06 | Git PREPARED ≠ SENT/ACK; actual recipient receipt required | Fake vs real receipt negative test |
| T07 | Approved but changed target/commit/cost/expired grant blocks execution | Approval version checks |
| T08 | Unverifiable or MOCK proof cannot become independently accepted LIVE evidence | Reviewer segregation test |
| T09 | No provider billed row shows UNKNOWN not 0, currency/window retained | Cost data fixture |
| T10 | Healthy dashboard is not inference success; stale health flagged | Mixed health fixtures |
| T11 | WP/Ads/social outputs remain read-only without publish authorization | UI/API negative tests |
| T12 | Viewer cannot elevate permissions through UI or direct API | 403 trace + auth audit |
| T13 | Denial/revocation effective after prior approval | Replay a previously approved command |
| T14 | Blocked task does not halt independent safe work or auto-reassign | Dependency/queue fixture |
| T15 | Missing EN/VI source or ambiguous lead attribution = UNKNOWN | Sample business finding data |
| T16 | STOP requested but unconfirmed remains visibly unconfirmed | Transport loss fixture |
| T17 | Slow network shows loading then timeout with nondeceptive status | Responsive screen recordings |
| T18 | Empty record displays source absence and safe next action | Empty dataset fixture |
| T19 | Timeout after command shows UNCERTAIN, not automatic retry | Network injection + log |
| T20 | Stale and missing evidence statuses never map to PASS | Null/freshness matrix |
| T21 | Unauthorized user sees denied state, protected API rejects | Role matrix negative test |
| T22 | Offline navigation read-only with timestamp, mutations disabled | Offline browser replay |
| T23 | 409 stale version and duplicate request preserve single authoritative result | Concurrent mutation test |
| T24 | Keyboard, screen reader, 320px mobile, 200% text and contrast checks | axe/manual accessibility matrix |

**Design-only self-QA gate:** verify all 12 screens have nonempty outcome/actor/data/action/state/KPI/test; all 24 test IDs unique; every feature maps to an M0–M5 stage and downstream WBS proposal; no claimed live implementation. Future Work reviewer validates independent feasibility; A0 Assistant checks cross-gate consistency. This is NOT test execution.

### 5.1 Feature → WBS handoff mapping for Coordinator DGN-3

| Product demand / screen(s) | Existing WBS | New WBS demand for Coordinator (PROPOSED; no IDs allocated) |
|---|---|---|
| Charter, goals, personas & KPI / S02 | G0-01, G0-03 | KPI source dictionary + approval policy |
| UI navigation, global statuses / S01,S12 | G0-02, UI-01 | Accessibility and provenance UI tests |
| Task/roadmap, single owner / S03,S04 | G2-01,G2-02,G3-03,UI-02 | Actual-ACK integrity and durable receipt ledger |
| Capability catalog & matching / S05,S06 | G3-01,G3-02,CTRL-01 | Explicit skill evidence freshness policy |
| Approval/STOP/independent review / S07,S08 | G2-03,REL-01,REL-02 | Grant revocation / uncertainty reconciliation |
| Cost/Integrations / S09,S10 | INF-01,INF-03,GROW-01 | Verified billing provenance + auth-integrations test |
| WP/SEO & business audit / S11 | UC01-01,UC01-02,QA-U01 | Read-only business KPI review fixture |
| Ads/GA4 / S11 | GROW-01,GROW-03 | Consent and attribution quality gate |
| Media/social / S11 | GROW-02,GROW-03 | Publication approval state machine |
| Backup/secure operations / S07,S10 | INF-02,SEC-H,REL-01 | Out-of-band monitoring and restore evidence |

Coordinator owns final unique WBS IDs, dependency DAG and assignment. This design **does not modify WBS or activate HOLD items**.

## 6. Actual A2 session capability / skill survey (DGN-1 use, not DGN-2 global inventory)

| Skill ID / tool | State observed in THIS A2 session | Actual use / proof | Boundary and fallback |
|---|---|---|---|
| `K-DOC,K-UX,K-DATA` — model-native analysis/specification/acceptance | **AVAILABLE_NATIVE / employed** | Authored this traceable charter, role matrix, IA/screens and tests | Model prose is design, not formal usability validation or runtime evidence |
| `K-GIT` — connected GitHub | **VERIFIED_CONNECTED** | Authenticated repo HEAD `d549564d...`, read file/blob SHA, repo push permission; created isolated A2 branch | No main merge, no editing other writers, only two scoped files |
| `K-SEC` — policy/source review | **DOCUMENT_REVIEW_VERIFIED** | Fetched full main mandatory rules and repository security; screen security contracts mapped | Cannot claim a penetration test, live authorization or branch protection |
| `K-SCHEMA,K-TEST` — logical state/test design | **DESIGNED_ONLY** | Entity dictionary and T01–T24 fixtures | No program/harness/test runtime invocation; independent QA later |
| Canva design connector | **AVAILABLE_TOOL_CANDIDATE / NOT_USED** | Tool namespace discoverable; no design generation or proof of account/session write rights | UI design is text-only; Canva export/render would require specific future task and permission |
| Browser/Computer Use/Playwright/axe | **UNTESTED_NOT_INVOKED** | No UI exists to inspect under DESIGN_ONLY | Work read-only feasibility review and future build-test task |
| `docx`, `slides`, `spreadsheets`, `pdfs` artifact skills | **AVAILABLE_CANDIDATES_NOT_USED** | Skill catalog present, not needed for two Markdown Git files | Do not claim installed external app or use paid credits |
| WordPress/Woo, Ads/GA4, HeyGen, Hostinger, VPS | **NOT_TESTED_THIS_TASK** | Historical repository evidence only, no account access | Operational side effects expressly prohibited |
| Installable candidates (axe-core, Playwright, JSON Schema validator, Figma/Canva design workflow) | **NOT_INSTALLED_NOT_TESTED** | Possible future QA/visual design options, not adopted | Require environment/tool availability, security and cost review; prefer free/offline QA |

**Skill selection decision:** GitHub connector and native product/UX reasoning suffice for DESIGN_ONLY. No plugin installs or paid APIs justified. Actual Agent-specific inventory and DGN-2 capability matching remain A1/Coordinator-owned. `agents/a2.md` was NOT_FOUND on main; no profile invented or written outside authorized paths.

## 7. Provenance, unresolved decisions and handoff

**Pinned sources actually read:**  
- `main@d549564de52429e777c68daf9df7a93df5f22f27`: `AGENTS.md` blob `af42293a8ae7d3e864cd9f89442bc6861e85c080`; `rules/AGENT_WORKFLOW.md` `9dd6a1601e9b2a1b472f4a1ae89e9626ada05797`; `rules/REPOSITORY_SECURITY.md` `c24d608036b11dcd3fafcaefbefa23fdb591990e`; `STATE.md` `d74e6f3e7cc8bad0192f4a025e25d70aaa83d708`; `CATALOG.yaml` `26e125296fd0c39d0e82d6c5438dcc1ca2d8947f`; `agents/README.md` `b94d61fe4d92ad0d5d063a3bebabb8a3edf43e5a`; `PROJECT.md` `32ce49173f4ffaa0a940c1324af267a7b22bd74e`.
- Product origin `program/PRODUCT_AND_UI.md` `1064114e6754d40fbbddf12f709912c5d6ebf71a`; A2 roadmap `program/roadmaps/a2.md` `dc661415531619ffab704d5270366e69ff604ee1`; WBS `program/WORK_BREAKDOWN.md` `0d800afb4531e4db65f81f19431c3afde8dab4b6`; skill registry `program/SKILL_REGISTRY.md` `1e92e4ba6cfa42e764ecf52c75f409f10d83792c`.
- Coordinator accepted source commit `ab0e728f6f1c698dc7d2fd8dcae6e8bad94dc125`, roadmap blob `17c7cf823090931eafa0109e7d43f44019115260`; task-linked A0 outcome authorization at PR43 #7108702342. Historical snapshots are not live task receipts.
- `agents/a2.md` absent (404) on pinned baseline; A1 DGN-2 to reconcile, A2 does not edit absent profile.

**Open for post-design A0/Coordinator decisions (not blockers for design):** final authentication stack, hosting topology, selected live data stores and metric freshness windows, user grants and data retention, budget ceilings, integration permissions, distinct Reviewer and A0 approval UX, time-bound SLO and test environments. These are deliberately not silently decided from historic source.

**Acceptance & release:** this document fulfills **DGN-1 design contract only**, awaiting independent package review. No UI screens were rendered or deployed; no accounts changed; no paid calls; no merge; no historical HOLD task activated. Next owner **Chat Điều phối** incorporates feature→WBS links after A1 skill matrix, Work separate feasibility review and package gate. A2 owns only its two scoped files and will update roadmap to `READY_FOR_ROADMAP_ACCEPTANCE` with Git SHA/readback. 
