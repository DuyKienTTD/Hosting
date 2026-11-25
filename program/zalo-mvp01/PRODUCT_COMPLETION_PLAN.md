---
id: zalo-product-completion-01
type: decision
status: active-offline-execution
authority: HOSTING-ZALO-RESUME-01
owner: Chat Dieu phoi
task_id: ZALO-PRODUCT-COMPLETION-01
lifecycle: ACTIVE
updated_at: 2026-11-26
sensitivity: public
---
# TTD Zalo Assistant — Product Completion Plan

**Decision ID:** ZALO-PRODUCT-COMPLETION-01\
**Authority:** HOSTING-ZALO-RESUME-01 · A0, 26/11/2026\
**Owner:** Chat Dieu phoi\
**Implementation owner:** ChatGPT Work (single app source writer for the offline scope on `dev/ttd-zalo-product-01`)\
**Independent review:** Codex Windows runtime; A1 security/test design; A2 customer/knowledge UX data (each only after task-specific ACK and authority)\
**Plan baseline:** main `097c080cc6d7fb3ca36b1849d9c10375d5cbd67f`; accepted offline product `dev/ttd-zalo-mvp01` candidate `d49d795aca2550cb143957141aaf60ed304b28e0`, tree `81b4c0b86a1e9b67da6eddb47a52c9c8c5e167d1`; current report-only update `52b7c5ccac572b170925d28c44c5613c1e73a849`.\
**Plan state:** Active offline execution.

## Trạng thái 26/11/2026

Checkpoint theo báo cáo Điều phối: các phiên chế độ Công việc bị chặn bởi thông báo hết lượt sử dụng đến 29/11/2026 04:06 ICT. IN_PROGRESS chỉ biểu thị việc đang hoàn thiện, không xác nhận phiên đang chạy hoặc outcome đã hoàn thành.

| Công việc | Trạng thái | Phạm vi hoặc điều kiện |
| --- | --- | --- |
| ZPC-01 | IN_PROGRESS | Làm lại ở chế độ Trò chuyện; chưa có kết quả trên GitHub tại checkpoint. Chủ dự án tự gửi thư hỏi Zalo. |
| ZPC-02 | IN_PROGRESS | Làm lại ở chế độ Trò chuyện; chưa có kết quả trên GitHub tại checkpoint; không gọi API. |
| ZPC-03 | IN_PROGRESS | Có 1 commit trên `a2/zalo-zpc-03-corpus`; đang hoàn thiện ở chế độ Trò chuyện. |
| ZPC-04 | IN_PROGRESS | Làm lại ở chế độ Trò chuyện; chưa có kết quả trên GitHub tại checkpoint. |
| ZPC-06 / ZPC-07 / ZPC-08-seam / ZPC-10-offline | BLOCKED_USAGE_UNTIL_2026-11-29 | TTD-ZALO-P1-OFFLINE chưa có commit trên `dev/ttd-zalo-product-01`; chờ hạn mức. ZPC-08-seam chỉ là giao diện adapter và mock, ZPC-10-offline dùng luồng mô phỏng. |
| ZPC-05 | BLOCKED | Cần Windows runner và quyền chạy mới cho kiểm tra startup. |
| ZPC-09 | BLOCKED | Cần văn bản cho phép của Zalo và phạm vi tích hợp được duyệt. |
| ZPC-11 | BLOCKED | Cần bản tích hợp, Windows runner, phê duyệt chạy QA và các điều kiện kết nối Zalo, paid API. |
| ZPC-12 | BLOCKED | Cần nghiệm thu QA và phê duyệt pilot riêng. |
| ZPC-13 | BLOCKED | Cần nghiệm thu pilot và quyết định production riêng. |

Chỉ dùng dữ liệu tổng hợp. Cấm production, paid API, gọi nhà cung cấp AI thật, tài khoản Zalo thật, gửi tin thật và dữ liệu khách thật. Dùng lại kết quả đã nghiệm thu của M0–M5, POC-01/02 và OpenClaw.

[Theo dõi lỗi vận hành Agent](../../reports/agent-operational-issues.md)

## 1. Product outcome

Build on the accepted MVP-01 Windows desktop into a practical customer-care assistant for **one personal Zalo account**, connected only through an integration Zalo has developed, licensed, authorized or explicitly approved. It must receive/manage permitted inbound conversations, resolve the correct customer/thread, use customer-scoped memory and business knowledge, produce grounded AI-assisted drafts, and support controlled outbound replies. Preserve the operator's control and the existing Policy Core. Do not substitute Zalo OA or manual copy/paste as the product target.

Business outcomes to measure in a supervised pilot:
- Median and p95 time from inbound event to operator-ready draft and to approved response.
- Operator handling minutes per conversation and proportion of repetitive work removed.
- First-response time, unanswered/overdue conversations and follow-up completion.
- Factual grounding/citation rate and human correction rate.
- Conversion attribution only where an authorized sales outcome source exists.
- Safety invariants: zero wrong-recipient sends, zero duplicate sends, zero sends after STOP/revocation/takeover, zero cross-customer memory disclosure, zero unsupported claims of delivery.

No business baseline or target percentages are invented here. Measure a pre-pilot baseline, then A0 sets target thresholds from actual operator volume and business economics.

## 2. Existing product and gap analysis

Source of truth: accepted candidate and [current developer report](https://github.com/DuyKienTTD/Hosting/blob/52b7c5ccac572b170925d28c44c5613c1e73a849/reports/ttd-zalo-mvp01-dev.md) at `52b7c5ccac572b170925d28c44c5613c1e73a849`; [MVP task](https://github.com/DuyKienTTD/Hosting/blob/f812ba4ada6a17f51e3c0d7c9879ed8917f552b9/tasks/2026-11-24-ttd-zalo-mvp01-dev.md); [M0–M5 roadmap](https://github.com/DuyKienTTD/Hosting/blob/f812ba4ada6a17f51e3c0d7c9879ed8917f552b9/program/zalo-mvp01/ROADMAP.md); [A0 final appraisal](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7142260412); [Codex final QA](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7142182692).

| Capability | Existing verified product | Gap to requested product | Status |
|---|---|---|---|
| Desktop/operator experience | Windows x64 Electron/React, six Vietnamese screens: conversations, messages, customer profile, knowledge, review/send, permissions/activity. Exact MVP package passed independent Windows QA. | No live personal-account connection/sync state, real inbound inbox, provider health or live operator metrics. | FOUNDATION ACCEPTED; live operations NOT IMPLEMENTED |
| Zalo Personal Channel | Synthetic account/customers, fake inbound and Fake Channel only. No personal account connector in source. | Officially permitted personal-account authorization/API for inbound events, conversation/history access, sender/thread identity and outbound one-to-one replies. | BLOCKED ON PLATFORM AUTHORIZATION |
| Customer Intelligence | Stable synthetic IDs distinguish same-name customers; per-customer sourced memory; retain/respond/send consent separation; SQLite migration/restart. | Map Zalo's authorized account/user/thread/message IDs; lifecycle, tags/stages, needs, follow-up and deletion/export controls for real customer records. | PARTIAL — synthetic identity only |
| Business Knowledge | Local structured TXT import (SKU/title/summary), source-linked draft and clarification when price is missing. | Document catalogue/versioning, supported formats, effective dates, product/price/policy conflict handling, semantic/hybrid retrieval and source freshness. Current lookup is substring matching on SKU/title, not semantic search. | PARTIAL — narrow local catalogue |
| Real AI Engine | Deterministic Fake LLM only; no real provider/model call. AI has no transport authority. | Provider adapter, Vietnamese intent/context reasoning, grounded drafts, clarification, confidence/abstention, evaluation and cost controls. | NOT IMPLEMENTED |
| Controlled Communication | Exact destination/content approval, edits invalidate approval, separate consent, STOP/revoke/takeover, durable reservation/dedup, no automatic retry on unknown state; fake receipt only. | Authorized real channel adapter, provider receipt mapping, rate/quotas, inbound cursor/sync, live send state and reconciliation. | POLICY FOUNDATION ACCEPTED; LIVE CHANNEL NOT IMPLEMENTED |
| Reliability/security | SQLite schema migration, restart, fault/STOP/revoke tests, sandboxed renderer/narrow IPC, no real Zalo or paid calls in QA. | Live network failure/reconnect, webhook verification, cursor replay, credential lifecycle, data-at-rest and cross-provider data governance. | OFFLINE RELIABILITY ACCEPTED; LIVE RELIABILITY NOT IMPLEMENTED |
| Startup stability | MVP accepted with condition. Intermittent white-window symptom remains `ROOT_CAUSE_UNKNOWN`; no evidence-backed source fix. | A future stable/general operator release needs a separately authorized, evidence-based resolution or explicit residual-risk decision. | OPEN RESIDUAL RISK; diagnosis episode closed |

**Reuse, do not reopen:** M0–M5 and Codex QA-01–QA-08 are accepted for offline MVP use. The earlier `vuhai2002/zalo-agent` personal automation candidate was `NO-GO` for current platform/product selection; do not repeat that POC or reuse its unapproved connector. Reuse only its already accepted test ideas and lessons. See [POC-01 coordinator NO-GO](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7123578643), [A0 personal-channel direction](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7145241136) and [A0 correction](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7145316253).

## 3. Zalo Personal integration feasibility — first critical gate

### 3.1 Current evidence and conclusion

Official Zalo Platform documentation currently describes Open APIs for **Zalo Official Account (OA)** and ZBS template messages. Its OA OpenAPI supports OAuth 2.0, OA follower/message operations and webhooks. The official OA guide explicitly describes integrating a business's OA with its internal system. These are not evidence of a personal-account chat API. The published catalogue reviewed did not identify a documented personal-account messaging API for reading personal conversations, subscribing to personal inbound messages or sending personal-account replies.

Zalo's current Terms of Use, updated 28 August 2026, clause 4.7 prohibits logging in/using Zalo through third-party compatible software or systems not developed, licensed or approved by Zalo. Zalo Help also lists use of third-party software not issued by Zalo for an automated account among common reasons for temporary account deactivation. This is a material account and platform risk, not merely a technical obstacle.

**Feasibility verdict:** `PERSONAL_API_NOT_VERIFIED · WRITTEN_ZALO_AUTHORIZATION_REQUIRED`. This is not proof that no private partner programme or non-public permission exists. It means no public official personal-chat API/permission has been verified in the sources reviewed. No connector implementation can start until Zalo confirms the precise permitted route in writing or provides verifiable official documentation and credentials/scopes.

Official sources reviewed 2026-11-25:
- [Zalo Platform Open APIs catalogue](https://docs.zaloplatforms.com/docs/OA) — OA and ZBS categories, OAuth 2.0 and webhooks.
- [Zalo OA OpenAPI setup and authorization guide](https://oa.zalo.me/home/documents/guides/Khoi-tao-ung-dung-va-cap-quyen_117071366476220195) — explicitly describes OA operations and OA App authorization.
- [Zalo Terms of Use](https://zalo.me/zalo/dieukhoan/) — clause 4.7 and related account/security restrictions.
- [Zalo Help: temporary account deactivation](https://help.zalo.me/huong-dan/chuyen-muc/quan-ly-tai-khoan-zalo/loi-thuong-gap/tai-khoan-zalo-bi-tam-thoi-vo-hieu-hoa/) — third-party software for automated accounts listed as a common reason.
- [A0 direction and correction](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7145316253) — preserve personal-account objective; no OA substitution, scraping, private endpoints, reverse engineering or unofficial client.

### 3.2 One official clarification request — no generic POC

Coordinator prepares one written request for the project owner to send through Zalo's official developer/support contact route. It must ask specifically whether Zalo authorizes a third-party Windows desktop companion to connect **one personal account** and, if yes, obtain written details for:
1. Official API/SDK/partner programme and eligible account/app type.
2. Inbound one-to-one message events, sender and stable conversation/message identifiers.
3. Permitted conversation/history read and sync window; deletion/edit/recall semantics.
4. Outbound one-to-one send, supported content types, delivery/failed/unknown receipts.
5. OAuth/scopes, consent, app review, account-owner authorization and revocation.
6. Rate limits, quotas, anti-spam rules, reliability/SLA and pricing.
7. Data processing, retention, cross-border transfer and security obligations.
8. Whether any restrictions prohibit this personal-account customer-care use case.

**Decision branch:**
- If Zalo confirms a documented/authorized personal integration: Coordinator verifies the exact scope, technical docs, legal terms and cost; then submits a minimum connector work order to A0 for execution authority.
- If Zalo says no, or does not provide adequate written authorization: keep the personal connector `BLOCKED/NO-GO`; present the exact answer and options to A0. Do not silently pivot to OA or manual copy/paste as the product target. A0 must explicitly decide whether to wait, pursue an authorized partner, or change the product requirement.
- No QR/session/cookie extraction, private endpoint, reverse-engineered protocol, unofficial client/library, desktop DOM/UI scraping/click automation, background account access or auto-send.

No message is sent to Zalo as part of this planning task.

## 4. Real AI provider strategy

### 4.1 Architecture decision

Preserve the existing desktop, SQLite, Policy Core and Channel Adapter seam. Add a provider-neutral `AIAdapter` in the trusted main/application layer; renderer never receives provider credentials and the model never receives a transport/send tool. The AI path is:

`authorized inbound → identity resolution → consent/retention gate → customer-scoped context + knowledge retrieval → AIAdapter → structured draft + source IDs → policy/grounding validation → operator edit/approval → exact destination/content approval → Outbound Gateway rechecks STOP/consent/revision/idempotency → authorized ChannelAdapter`.

The model may classify intent, summarize, retrieve/consume allowed context, draft and suggest follow-up. It cannot call `send`, access Zalo credentials, change consent, remove STOP, alter customer identity or persist memory directly. All side effects remain deterministic application commands behind Policy Core.

Provider adapter contract should normalize: model ID/version, request/response schema, timeout/cancellation, token usage, estimated/actual cost, refusal/error categories, structured output validity and trace ID. Provider switching must not change Policy Core or Channel Adapter contracts. Do not implement autonomous agents or multi-agent orchestration inside the customer-facing runtime.

### 4.2 Shortlist — planning comparison, not provider selection

Public list prices observed 2026-11-25 (USD per 1M text tokens; reference only, reverify before procurement — chỉ tham chiếu, xác minh lại trước khi mua):

| Candidate | Input / output | Data handling signal | Planning role |
|---|---:|---|---|
| OpenAI GPT-6.2 Sol | $2 / $10 | API data not used for training by default; abuse-monitoring logs up to 30 days by default, distinct from endpoint-specific application-state retention. Modified Abuse Monitoring/ZDR require prior approval and feature/endpoint eligibility. | Balanced benchmark candidate |
| Anthropic Claude Sonnet 5 | $2 / $10 | Commercial API inputs/outputs not used for training without express permission; standard API inputs/outputs deleted within 30 days, subject to documented exceptions. ZDR is a separately approved organization arrangement subject to feature/model eligibility. | Quality/long-context benchmark candidate |
| Google Gemini 3.5 Flash-Lite | $0.30 / $2.50 | Paid tier states content is not used to improve products; Free tier states content may be used to improve products. | Low-cost benchmark candidate; do not send real customer content on Free tier |

Official pricing/data sources:
- [OpenAI API pricing](https://developers.openai.com/api/docs/pricing) · [GPT-6.2 Sol model](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [OpenAI API data controls](https://developers.openai.com/api/docs/guides/your-data)
- [Claude Sonnet 5 announcement, updated 2026-08-10: $2/$10 permanent](https://www.anthropic.com/research/claude-sonnet-5) · [Anthropic API pricing](https://platform.claude.com/docs/en/about-claude/pricing) · [commercial data retention](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data) · [Anthropic API retention/ZDR](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) · [commercial data use](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)
- [Gemini API pricing and Free/Paid data-use distinction](https://ai.google.dev/gemini-api/docs/pricing)

These prices are token list rates, not a monthly operating estimate. Monthly AI cost formula:
`(input_tokens / 1,000,000 × input_rate) + (output_tokens / 1,000,000 × output_rate) + embeddings/tools/storage/other billable items`.
Actual volume, average context, caching, retry rate, model tier, tax/FX and Zalo/platform charges are unknown; therefore no monthly cost is claimed.

### 4.3 Selection method

A2 prepares a synthetic, non-customer evaluation corpus based on the approved product catalogue and operator scenarios. After A0 authorizes provider calls and a cost cap, benchmark the same fixed cases against the shortlist. Score:
- Vietnamese comprehension, politeness and context continuity.
- Correct customer/thread scoping and intent classification.
- Exact source-grounded SKU/spec/policy answers and citation correctness.
- Correct abstention/clarification when price/spec/policy is missing or conflicting.
- Hallucination and unsupported-claim rate.
- Draft usefulness and operator edit distance/acceptance.
- p50/p95 latency, failure rate, token usage and cost per completed conversation.
- Data handling, region/retention, DPA/terms and credential controls.

Do not choose solely on token price or generic model benchmark claims. Use only synthetic/anonymized data until A0 approves real-data transfer and provider terms. No free tier may receive real customer data if its terms permit use to improve models. No provider call, API key, paid trial or account activation is authorized by this plan.

## 5. Target architecture — extend, do not rebuild

| Component | Preserve / extend | Boundary |
|---|---|---|
| Windows Desktop UI | Existing six-screen React/Electron application. Add connection/sync health, AI status, source/confidence display, customer timeline and operator follow-up only as needed. | UI does not hold secrets or directly call providers/channels. |
| Main process / IPC | Existing sandboxed renderer, context isolation, narrow validated IPC. | Validate sender, frame, document, schema and permission on every command. |
| Policy Core | Existing separate retain/respond/send, STOP, takeover, expiry/revision, exact approval and dispatch fence. | Mandatory gate for inbound persistence, AI context and outbound initiation. AI cannot bypass/change it. |
| SQLite / Customer Intelligence | Preserve migrations and stable IDs; add authorized account/user/thread/message mapping, tags/stages, needs and follow-up with source provenance. | Customer/group/thread isolation, retention and deletion/export semantics; no cross-customer retrieval. |
| Knowledge Engine | Extend current structured SKU import into versioned product/price/policy catalogue and document ingestion with source/effective date. | Start with SQLite FTS5/BM25 and exact structured filters. Add embedding/hybrid semantic ranking only if a measured retrieval evaluation justifies it; keep vectors in SQLite if adequate. No separate vector DB/service by default. |
| AI Adapter | New provider-neutral module in existing app process. | Provider credential from Windows protected storage; data minimization; structured output; timeout/cancel/cost ledger. No direct tools for sending. |
| Channel Adapter | Keep current Fake Channel for tests; implement Personal Zalo adapter only after written Zalo authorization. | OAuth/scopes and webhook/polling only as officially documented. Verify webhook signature, event IDs, cursor, sender/thread mapping, quotas and delivery states. |
| Outbound Gateway | Keep one send boundary and exact approval. | Recheck identity, recipient, consent, STOP, takeover, approval revision and idempotency at final initiation. Unknown result is reconciled, never blindly retried. |
| Audit / Reliability | Extend content-minimal audit, inbox/outbox state, connection errors and sync checkpoints. | No raw denied/ephemeral content in durable storage; no secrets in logs; no automatic retry unless idempotency is proven. |

A public webhook may require a reachable HTTPS endpoint; a Windows desktop alone may not be reachable from Zalo. Prefer an officially supported desktop/pull mechanism if available. If official personal API requires a webhook, evaluate the smallest single-purpose relay only after docs and A0 infrastructure approval. Do not create microservices or infrastructure pre-emptively.

## 6. Work breakdown and Agent assignment

The table describes the full product scope and its dependencies. The 26/11/2026 status above defines the parts in offline execution. Live platform, paid API, real-data and production work require separate authority. Each work order must pin the exact base, read/write set, budget, STOP/rollback and acceptance; actual recipient ACK is required.

| ID | Work package / outcome | Sole owner | Skills required | Dependency / READ_SET | WRITE_SET / permissions | Acceptance / NEXT_OWNER |
|---|---|---|---|---|---|---|
| ZPC-01 | Obtain written Zalo personal-account API/partner authorization answer; capability and terms matrix. | Chat Điều phối | Official platform research, integration/security/legal scoping | Official Zalo docs/terms; POC-01 NO-GO and A0 direction/correction | No product code. Draft only for the project owner to send; no account login/data. | Written answer covers inbound, history, identity, outbound, scopes, limits, price and data terms; otherwise status remains BLOCKED. NEXT A0. |
| ZPC-02 | AI provider decision package and cost/data comparison; no live calls. | Chat Điều phối | API architecture, pricing, privacy/data handling, cost modelling | This plan's official provider sources and existing Fake LLM seam | Planning docs only; no API key/account/call. | A0 receives ranked benchmark candidates, data terms, formula and explicit unknowns. NEXT A0. |
| ZPC-03 | Synthetic Vietnamese customer-care benchmark corpus, product facts, missing/conflicting-price cases and operator scoring rubric. | A2 (proposed) | Product data, Vietnamese UX, customer journeys, knowledge provenance | Accepted catalogue/source facts; no real customer data | Independent synthetic fixtures/spec only; no app source. | Versioned synthetic corpus and scoring rubric; no unsupported facts. NEXT Work/Coordinator. |
| ZPC-04 | AI/channel privacy threat model and negative/fault acceptance matrix. | A1 (proposed) | Security architecture, privacy, IPC, race/idempotency testing | Current Policy Core, A0 boundaries, official provider/channel terms | Test design/evidence only; no app source. | Covers prompt/data minimization, tenant/customer isolation, secret storage, prompt injection, STOP/revoke, provider failure, channel replay and unknown delivery. NEXT Work/Coordinator. |
| ZPC-05 | Startup residual disposition and stability gate. | ChatGPT Work (existing sole writer) | Electron/Windows lifecycle, React rendering, Windows runtime diagnostics | Existing diagnostic report and Codex receipts; candidate d49d795 | No additional Windows launch under consumed authorization. Any new run needs a fresh narrow A0 grant; product source only within existing app write-set if evidence justifies a fix. | Either evidence-backed fix with targeted Windows confirmation, or documented UNKNOWN with explicit residual-risk acceptance. Required before stable general rollout. NEXT Coordinator/A0. |
| ZPC-06 | Extend Customer Intelligence and data lifecycle for an authorized account. | ChatGPT Work | TypeScript/SQLite migrations, identity resolution, provenance, privacy | ZPC-01 permission shape; ZPC-04 policy; existing customer memory | `apps/ttd-zalo-assistant/**` on existing dev branch only after execution grant; no real data in development. | Stable account/user/thread/message mapping; per-customer source provenance, consent, retention, delete/export, migration/restart tests. NEXT A1/Codex QA. |
| ZPC-07 | Business Knowledge Engine: versioned catalogue, documents, hybrid retrieval and citations. | ChatGPT Work | SQLite FTS5, document parsing, retrieval evaluation, TypeScript | ZPC-03 corpus; existing local knowledge and source schema | Same app write-set; synthetic docs only; no new vector service by default. | Versioned sources, effective dates, deterministic exact SKU/price lookup, tested semantic retrieval if justified, citations and abstention on conflicts/missing data. NEXT A2/A1. |
| ZPC-08 | Real AI Adapter and grounded drafting. | ChatGPT Work | Provider API, structured output, prompt/RAG, Vietnamese evaluation, cost/telemetry | ZPC-02 provider decision and A0 paid/data approval; ZPC-03/04/07 | Same app write-set; no provider calls until explicit API budget, account, data scope and key-handling approval. | Provider swap without changing Policy Core; grounded structured drafts with source IDs; no send tools; quality, latency and per-conversation cost meet A0 thresholds. NEXT A1/A0. |
| ZPC-09 | Authorized Personal Zalo Channel Adapter and sync. | ChatGPT Work | OAuth/API/webhook, event processing, Windows networking, rate-limit/reconciliation | ZPC-01 written permission and exact API docs; A0 connector/data approval | Same app write-set only after explicit scope. No cookies/QR/session extraction, unofficial libraries, scraping or private endpoints. | Official auth, inbound event/history scope, correct IDs, webhook signature/cursor/replay handling, approved outbound, receipts and reconnect tests. If no permitted API, remain BLOCKED; no OA/manual substitution. NEXT Codex/A1. |
| ZPC-10 | Operator workflow, connection health and follow-up. | ChatGPT Work | React UX, accessibility, state modelling, operator workflow | ZPC-06–09; A2 synthetic UX acceptance | Same app write-set. | Six existing screens evolve into connected inbox, source-aware draft, review/approve, status/errors and customer follow-up; operator tasks measured. NEXT A2/Codex. |
| ZPC-11 | Integrated Windows QA and supervised pilot readiness. | Codex (review only); A1/A2 support scoped tests | Windows x64, Electron, IPC/security, integration/fault testing | Exact integrated candidate from Work; ZPC-03/04 test contracts | No source writes. Exact Windows runner/artifact and each QA task require explicit approval/ACK. No real Zalo until separate pilot grant. | Independent exact-build positive/negative/fault tests, security, data lifecycle, sync/reconnect, cost telemetry and rollback; verdict to A0. NEXT A0. |
| ZPC-12 | Controlled pilot and business outcome evaluation. | A0 decision authority; Coordinator delivery owner | Operations, privacy, support, metrics, incident response | ZPC-11 PASS; Zalo/provider/data approvals | Real account/data and any costs only under explicit A0 pilot grant. | One-account supervised pilot with baseline and thresholds; zero critical safety violations; cost and conversion/time outcomes reported. NEXT A0 for production decision. |
| ZPC-13 | Production/release readiness (separate decision gate). | Chat Điều phối plan; Work implementation if authorized; A0 decision | Windows release, signing/update, backup, monitoring, support, compliance | Pilot acceptance and separate production authority | Production, publication, new infra, live credentials and spending require explicit A0 approval. | Signed/reproducible package, incident/rollback, retention/deletion, support and business metrics; A0 explicit production decision. NEXT A0. |

### Capability and assignment notes
- **ChatGPT Work:** existing accepted M0–M5 developer and sole writer for `apps/ttd-zalo-assistant/**`; current capability for live Zalo/API or paid provider integration is not established and does not follow from offline acceptance.
- **Codex:** independently executed Windows x64 MVP QA; use as reviewer for exact future candidates only under task-specific grant. No product source writes.
- **A1:** existing independent security/test design outputs from MVP; proposed for security matrix and review, not app implementation.
- **A2:** existing customer/knowledge/UX design and test outputs; proposed for synthetic evaluation corpus and operator acceptance design, not app implementation.
- **Chat Điều phối:** accountable for Zalo official inquiry, provider comparison, cost/permission gates, task routing, dependency and evidence.
- **A0:** retains all reserved decisions for platform permission, paid budget, real data, new infrastructure, pilot, production and release.
No role name or historical test receipt constitutes current session ACK or permission. No Agent is activated by this plan.

## 7. Milestones, dependencies and release gates

| Milestone | Deliverable | Parallelism | Gate to continue |
|---|---|---|---|
| P0 — Plan appraisal and decision requests | A0 accepts plan; Zalo official inquiry scope; AI/data decision package | ZPC-01 and ZPC-02 can be prepared in parallel; ZPC-03/04 independent synthetic/test design | A0 confirms which external inquiry may be sent and which execution/cost/data scopes are granted. |
| P1 — Product readiness and offline capability extensions | Startup residual disposition; Customer Intelligence and Knowledge improvements on existing offline foundation | ZPC-05/06/07 can be planned in parallel; Work serializes app writes in one branch | Targeted acceptance; no real provider/channel. |
| P2 — Real AI capability | Provider adapter, grounded drafting, cost/privacy telemetry | Can proceed after provider and data approvals; does not depend on Zalo connector API | A0 approves provider, API budget cap, data processing terms and real/synthetic scope; benchmark passes. |
| P3 — Personal Zalo integration | Official personal account connection, inbound sync, controlled outbound | Only after P0 platform gate; connector and UI integration share Work's single source tree | Written Zalo authorization and exact official API scopes/terms. If unavailable, STOP connector; A0 decides product path. |
| P4 — Integrated reliability and operator workflow | End-to-end personal Zalo → customer context → AI draft → approval → outbound receipt; reconnection and audit | ZPC-10/11 join after P2 and P3 | Exact candidate Windows QA PASS, no critical security/data/send defects, stable startup gate resolved or explicitly accepted by A0 for limited scope. |
| P5 — Controlled pilot | One-account, supervised internal pilot and business baseline | No parallel live account rollout | Separate A0 grant for account, real data, provider spend and pilot operations; explicit consent and incident/rollback. |
| P6 — Production decision | Production-ready Windows product and operational support | After pilot evidence | Separate A0 production, infrastructure, publication, legal/security and budget approval. |

**Critical path:** ZPC-01 written personal-account permission → ZPC-09 connector → ZPC-11 integrated QA → ZPC-12 pilot → ZPC-13 production decision. AI branch can progress independently after ZPC-02/A0 provider and data approval, but full product acceptance requires both AI and authorized channel. Startup residual is a stable-distribution gate; it does not invalidate the already accepted offline MVP.

## 8. Cost, authority and explicit A0 decisions

### Current rights (do not infer more)
- Work is the sole app source writer for the resumed offline scope on `dev/ttd-zalo-product-01`. The accepted MVP and its developer report remain baseline evidence.
- Existing offline budget: paid AI/API **0 USD**, new infrastructure **0 USD**.
- No real Zalo login, live inbound/outbound, real customer data transfer, paid AI, new service/infrastructure, production, public release or main merge is authorized.
- `HOSTING-ZALO-RESUME-01` authorizes only the offline items listed in the 26/11/2026 status. Future live work requires a separate decision from A0.

### Decisions required before the dependent work
1. **Zalo:** written confirmation of a permitted personal-account API/partner route. If denied/unavailable, A0 chooses wait, authorized partner route or explicit product-goal change; Coordinator cannot substitute OA/manual workflow.
2. **AI:** select provider only after same-corpus Vietnamese benchmark; approve API organization/account, model(s), data region/retention/DPA and hard monthly USD cap. Provider pricing above is reference only, not a purchase or cost approval.
3. **Data:** approve real customer data fields, purposes, consent, retention/deletion, backup, export, access control, cross-border transfer and vendor processing terms after legal review.
4. **Infrastructure:** if official Zalo webhooks require public HTTPS, approve or reject the smallest relay/hosting option with exact cost, region, access and rollback. No infrastructure is assumed.
5. **Pilot:** approve one account, named operator, limited customer scope, duration, incident contact, support and stop criteria.
6. **Production:** separate explicit decision after pilot; no production rights arise from pilot acceptance.

### Cost model
AI variable cost is token-based (see §4.2) plus embedding, tools and any billable provider features. Monthly estimate cannot be made honestly until baseline conversation volume, tokens/conversation, retrieval size, retry rate and provider are measured. Zalo API/partner/OA charges and any webhook hosting cost are **UNKNOWN pending Zalo's written answer**. The plan deliberately does not insert invented monthly amounts.

Cost controls at implementation: per-request input/output caps; retrieval top-k and context budget; no automatic expensive retry; usage/cost ledger by provider/model/conversation; daily/monthly hard cap; alerts and STOP at cap; no fallback to a different paid provider without approval.

## 9. Acceptance criteria for the completed product

1. **Personal Zalo connection:** one personal account connected through an explicitly permitted official integration; accurate inbound sender/thread/message mapping; permitted history and event sync; authorized outbound one-to-one replies; documented quotas and receipt semantics.
2. **Customer Intelligence:** correct account/customer/thread isolation; sourced history/memory; consent and retention enforced; export/deletion and revocation behavior verified.
3. **Business Knowledge:** versioned product/price/policy sources; exact and semantic/hybrid retrieval evaluated; citations on material claims; no fabricated or stale price/spec; clarification when missing/conflicting.
4. **Real AI:** selected provider meets Vietnamese benchmark, quality/latency/cost thresholds set by A0; structured drafts and follow-up suggestions; abstains safely; provider-independent adapter; no send authority.
5. **Controlled communication:** exact recipient/content approval, revision invalidation, STOP/revoke/takeover fence at final initiation, idempotency, unknown-delivery reconciliation and no blind retries.
6. **Operator UX:** usable connected inbox, customer profile/timeline, source visibility, editable draft, review/send controls, connection/error/recovery and follow-up.
7. **Reliability/security:** Windows startup stability condition addressed or explicitly dispositioned by A0; credential protection, secure IPC, audit, backup/restore, network and data isolation, signed/reproducible package and independent Windows QA.
8. **Business value:** pre-pilot baseline and measured reduction in handling time/response time, fewer missed follow-ups and quality/conversion measures. A0 approves targets; safety invariants remain zero-tolerance.
9. **Operational/legal readiness:** documented Zalo authorization, provider data terms, privacy/legal review, retention and support/incident process.
10. **Separate production decision:** final acceptance does not itself authorize live service, publication or production.

## 10. Immediate next actions

[ZPC-01/02 decision packages and dependencies for ZPC-08/09](zpc-01-02/README.md).

1. **Coordinator:** prepare the Zalo inquiry for the project owner to send and the provider comparison for A0, using public documentation and zero API calls.
2. **A2 / A1 / Work:** carry forward the offline items in the 26/11/2026 status within their work orders. Work remains the sole app source writer.
3. **A0:** decide separately on any Windows runner access, live Zalo integration, provider calls or spend, pilot and production after the applicable evidence and gates.
4. **Reuse:** carry forward accepted evidence for M0–M5, POC-01/02 and OpenClaw.
