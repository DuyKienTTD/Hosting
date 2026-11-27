---
id: gate-b-chatgpt-provider-and-scope-review-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: chatgpt
---

# GATE B — ChatGPT technical, provider, and scope review

**NO_GO_PAID / H5_FOLLOWUP_REVIEWED / H6_SANDBOX_ROUTE_NOT_READY.** Read-only review, no direct KVM2 shell, no inference/provider API calls or runtime changes. Based on GitHub main at e69c1901f288aca4ddc2d5bd0209e53533ea3212; rule blob c3c0ca06565b3c71f546bed3986dd814d26c90fd. Read AGENTS, workflow sections 7–9, security, PROJECT/STATE/CATALOG, agent profiles, GATE B task/ADR, H3/mount/H5 reports and evidence, Guard/one_shot/mock_contract/Compose source, official OpenAI docs and logged-in Platform Projects browser tab.

## Technical source review

- H5 reported live Guard matching 1953a81, mock-only without freeze/one-shot dispatch. GET model metadata HTTP 200 from temporary process in Guard is NOT evidence that the Guard application has a live paid path.
- Newer Git source guard.py at 69dd952/current main still posts to MOCK_URL. freeze() and admit_one_shot() are invoked only if TTD_MOCK_ONE_SHOT_LEDGER is configured. Merely updating live Guard from Git cannot establish paid readiness.
- Compose mounts real shared P0 ledger read-only in Guard; one_shot.admit() needs a durable locked write, scoped permit and reservation BEFORE provider dispatch. Do not simply change mount RW: safe shared-ledger writer boundary and least privilege must first be proven.
- mock_contract.freeze() hashes canonical wire bytes; the 4,000-byte size constraint is not the provider count <=4,000 input tokens. Final frozen provider-bound digest and matching input_tokens result absent. H3 combined callback/one-shot mock PASS is valid for H3 test configuration, not paid live equivalence.
- Guard mount PASS evidence remains applicable: guard-only readonly credential, 18/18 isolation, production HTTP 200/restart 0, real ledger 1 historical attempt/0 permits/kill switch ON, delta paid 0. This ChatGPT review did not repeat KVM2 probes.

## Provider rights — superseding H5 follow-up read during this review

A concurrent repository update added reports/2026-11-22-hermes-gate-b-h5-preflight-followup.md and reports/evidence/2026-11-22-ttd-hermes-gate-b-h5-followup.json. It supersedes the earlier H5 UNKNOWN project/permission/count status. Codex reports VERIFIED_LIVE dashboard service account key active/inherited without key-level restriction, project GPT-6 Luna access, a safely masked Guard credential match, pay-as-you-go, positive credit, Standard tier, Global residency and configured model quota. Responses CREATE permission is supported by administrative configuration, NOT an actual Responses create call. Remaining rate-window capacity was NOT measured. The ChatGPT read-only Projects tab alone did not prove these; evidence provenance is Codex's H5 follow-up report.

The follow-up measured the candidate exact frozen digest e66603e05a4a9b0d7a4bbd7b9142a89e15e38176c2fe1fddbf3dd5764ff1a929 (3,304 bytes) with 723 provider input tokens, HTTP 200 at /v1/responses/input_tokens. The second count concerns a separate n8n mock probe and is not the H6 candidate. Mock loopback observed one exact-byte dispatch with pre-dispatch permit consumed and reserved, rejected tamper/replay, and callback 200. These are H5 candidate/mock readiness measurements, NOT proof the live Guard app dispatches to OpenAI. A future H6 path change requires digest revalidation and repeat count if any input-affecting bytes change.

Official docs: API key scopes/effective role and model permissions differ from inference execution; project spend controls do not substitute for atomic P0 ledger. Published GPT-6 Luna Standard text rates are $0.10/M input and $0.50/M output. Candidate cost for 723 input+600 output, without cache, is $0.0003723; existing $0.0035 reserve is a conservative candidate, not a license to dispatch. Responses create was NOT called, paid delta remains zero. Do not read/hash/paste keys or publish project IDs.

## Decision, responsibility, handoff

- **GO now:** ChatGPT read-only code/evidence/vendor research and safe account metadata verification with the owner.
- **NO GO:** paid inference, live permit, changing Guard route/recreating container, ledger mount permissions or production. Any sandbox change without clear existing approval requires separate owner authorization; no new task or implementation specification was created.
- **ChatGPT review result:** H5 follow-up provides project/key identity, dashboard entitlement, billing, tier, candidate digest and count. Remaining uncertainty is effective create-path behavior, live rate-window capacity, and equivalence to a future H6 paid route. Do not repeat already verified H5 steps without a change trigger.
- **Codex next only after explicit approved sandbox scope:** assess runtime/source delta, fail-closed real-provider path, atomic shared-ledger admission/relock, exact post-enforcement digest, count revalidation on changed bytes and targeted mock fault/concurrency/callback/no-bypass/rollback. Reuse unaffected H3/H4/H5 evidence.
- Existing TTD-HERMES-GATE-B-001 owner codex/status blocked/conditional exactly-one-paid approval unchanged. No H6 execution handoff is sent by this review. A future H6 mock-first sandbox implementation/change needs scope/approval review; paid remains BLOCKED_PREFLIGHT. This report is PREPARED for owner review.

## Official sources reviewed 2026-11-22

- https://developers.openai.com/api/docs/models/gpt-6-luna
- https://developers.openai.com/api/docs/pricing
- https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count
- https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform
- https://developers.openai.com/api/docs/guides/api-keys
- https://developers.openai.com/api/docs/guides/rbac

## ChatGPT formal H5 acceptance — 2026-11-22

**H5_ACCEPTED / PROVIDER_PREFLIGHT_PASS (scope-limited) / GATE_B_PAID_BLOCKED_PREFLIGHT.** Reviewer compared pinned Codex commit 1d9a604a574e5feb37e85b87d22f4a3c264b25ea including full six-file diff, H5 follow-up report and JSON evidence against task TTD-HERMES-GATE-B-001, ADR-P0-003, and prior H3/mount evidence. Diff added H5 report/evidence and catalog references, inserted a result section into existing task, and updated STATE/CHANGELOG; no change to task metadata owner/status/approval_scope/paid_inference_approval and no code/runtime change in that commit. This review is evidence-based, not an independent KVM2 re-probe.

Accepted H5: dashboard key/project/model and administrative Responses scope; model GET HTTP 200; provider input_tokens HTTP 200 returning 723 for frozen candidate SHA256 e66603e05a4a9b0d7a4bbd7b9142a89e15e38176c2fe1fddbf3dd5764ff1a929; max_output_tokens=600; conservative candidate reserve USD 0.0035 within USD 0.01/job; mock one-shot consume/reserve before exactly one mock dispatch, tamper/replay denial, n8n callback; guard-only mount/production/ledger invariants and 0 paid delta. Distinguish **VERIFIED_LIVE_REPORTED_BY_CODEX**, **VERIFIED_MOCK**, and **DOCUMENTED_ADMIN**; no direct paid Responses create or live remaining rate-window quota verification.

Not accepted as H6 ready: live Guard still 1953a81 mock-only, real ledger mounted read-only, no end-to-end actual provider transport/admission and no exact-final-wire proof on an H6 paid path. If H6 changes input-affecting bytes, digest and token count must be rebound to new final bytes. H5 mock PASS persists under the documented conditions; do not rerun it gratuitously.

**Decision:** H5 reviewer DONE; next phase H6 sandbox integration requires scope/owner approval review before changing runtime, and paid dispatch remains STOP. No H6 handoff SENT or ACKNOWLEDGED by this acceptance; owner of task remains Codex, status blocked, ADR conditional paid approval unchanged.
