---
id: gate-b-chatgpt-provider-and-scope-review-2026-11-22
type: report
status: partial
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# GATE B — ChatGPT technical, provider, and scope review

**NO_GO_PAID / RESEARCH_PARTIAL_PROVIDER_IDENTITY_UNKNOWN.** Read-only review, no direct KVM2 shell, no inference/provider API calls or runtime changes. Based on GitHub main at e69c1901f288aca4ddc2d5bd0209e53533ea3212; rule blob c3c0ca06565b3c71f546bed3986dd814d26c90fd. Read AGENTS, workflow sections 7–9, security, PROJECT/STATE/CATALOG, agent profiles, GATE B task/ADR, H3/mount/H5 reports and evidence, Guard/one_shot/mock_contract/Compose source, official OpenAI docs and logged-in Platform Projects browser tab.

## Technical source review

- H5 reported live Guard matching 1953a81, mock-only without freeze/one-shot dispatch. GET model metadata HTTP 200 from temporary process in Guard is NOT evidence that the Guard application has a live paid path.
- Newer Git source guard.py at 69dd952/current main still posts to MOCK_URL. freeze() and admit_one_shot() are invoked only if TTD_MOCK_ONE_SHOT_LEDGER is configured. Merely updating live Guard from Git cannot establish paid readiness.
- Compose mounts real shared P0 ledger read-only in Guard; one_shot.admit() needs a durable locked write, scoped permit and reservation BEFORE provider dispatch. Do not simply change mount RW: safe shared-ledger writer boundary and least privilege must first be proven.
- mock_contract.freeze() hashes canonical wire bytes; the 4,000-byte size constraint is not the provider count <=4,000 input tokens. Final frozen provider-bound digest and matching input_tokens result absent. H3 combined callback/one-shot mock PASS is valid for H3 test configuration, not paid live equivalence.
- Guard mount PASS evidence remains applicable: guard-only readonly credential, 18/18 isolation, production HTTP 200/restart 0, real ledger 1 historical attempt/0 permits/kill switch ON, delta paid 0. This ChatGPT review did not repeat KVM2 probes.

## Provider rights

Read-only OpenAI Platform Projects tab displayed a Default project with Global geography and recorded spending; this does not establish identity or permissions of the Guard-mounted credential. Current browser tool can list and read tabs, not navigate to API Keys/Model usage/Billing/Limits. Project/key match, effective owner/service account role, Responses create scope, model policy, billing, quota/tier and enforcement are **UNKNOWN**. Model-read via H5 GET does not establish Responses-write permission. Do not read/hash/paste secrets or publish project IDs.

Official docs: API key scopes intersect effective role permissions; model policy, rate limits, spend controls and billing are separately configured. Spend alerts do not stop requests and even hard spend-limit enforcement is not instantaneous; internal shared atomic P0 ledger is mandatory. POST /v1/responses/input_tokens is a token-count method, not POST /v1/responses inference. Count only after final provider-bound request/digest and safe credential path are established. Published GPT-6 Luna Standard rates are $0.10/M input and $0.50/M output, so 4,000 input+600 output base uncached $0.0007; $0.0035 is only an existing reservation candidate, not approved for dispatch without actual project/tier/price verification.

## Decision, responsibility, handoff

- **GO now:** ChatGPT read-only code/evidence/vendor research and safe account metadata verification with the owner.
- **NO GO:** paid inference, live permit, changing Guard route/recreating container, ledger mount permissions or production. Any sandbox change without clear existing approval requires separate owner authorization; no new task or implementation specification was created.
- **ChatGPT/account owner next:** correlate Guard key with project without secret exposure; inspect project key effective Responses-write, GPT-6 Luna model policy, billing/credit, usage/rate/hard spend limits and processing tier/geography.
- **Codex later, after rights/scope decision:** assess runtime/source delta, fail-closed real-provider path, atomic shared-ledger admission/relock, exact post-enforcement digest, token-count projection and targeted mock fault/concurrency/callback/no-bypass/rollback. Reuse unaffected H3/H4 evidence.
- Existing TTD-HERMES-GATE-B-001 owner codex/status blocked/conditional exactly-one-paid approval unchanged. NO H6 execution handoff sent. This review is PREPARED for owner review. Paid Gate B stays BLOCKED_PREFLIGHT.

## Official sources reviewed 2026-11-22

- https://developers.openai.com/api/docs/models/gpt-6-luna
- https://developers.openai.com/api/docs/pricing
- https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count
- https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform
- https://developers.openai.com/api/docs/guides/api-keys
- https://developers.openai.com/api/docs/guides/rbac
