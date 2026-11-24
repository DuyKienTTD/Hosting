---
id: openclaw-poc-01-a1
type: task
status: prepared-owner-forward
dispatch_eligible: false
owner: a1
updated_at: 2026-11-24
sensitivity: public
---
# OPENCLAW-POC-01-A1-SEND-TEST-DESIGN
WBS: OC-S01/S02
Required Skills: K-GIT,K-DOC,K-TEST,K-API,K-SEC,K-SCHEMA
MODE: OFFLINE_TEST_ONLY / source design for A1/A2
FIRST_ACTION ACK, read send-context.ts, send.handoff.test.ts, send.media-handoff.test.ts, zalo-js.ts and trace actual final transport, scheduler/tool/attachment/reaction paths. Design precise negative test matrix for cancellation after admission but before initiation (prior POC02 deferred callback defect), STOP scope vs individual abort, multipart, retries, recipient ID/type, concurrent unrelated calls and restart/idempotency. For each case identify existing native test or proposed fixture, assertion, source location and fake transport boundary. No application patch, no duplicated native execution, no claim runtime PASS. Send report to Work through coordinator; prioritize decisive cases. Historical A1 source expertise, current session source access must be checked. NEXT_OWNER Work.

## Authority and boundaries
User-forwarded OPENCLAW-POC-01 offline test plan dated 2026-11-24 explicitly permits source/dependency preparation, native offline tests and test-only harnesses. No separate GitHub approval receipt has been verified; this is the scope of the forwarded directive, not authority for other projects. Hosting main observed d549564de52429e777c68daf9df7a93df5f22f27. Read in full current AGENTS.md, rules/AGENT_WORKFLOW.md, rules/REPOSITORY_SECURITY.md, STATE.md, CATALOG.yaml, role profile (if missing, report), and this task. Record exact rule/source blobs, actual session ACK and capability preflight. All existing unrelated HOLDs remain. K skill IDs below refer to the DGN-2 candidate registry blob 6d79a1c5d11bab1ef03c55c68d2b8d55d32609bf, not activation of PR50 or effective new rules.
BASE_SHA: openclaw/openclaw@391dea93e0a97fff97f9f3d5e94eac992b247b09. Plugin @openclaw/zalouser 2026.11.7, zca-js 2.2.0, Node >=24.16.0 <25 or >=26.1.0, pnpm 12.15.0, Vitest 5.0.5, MIT, lockfile blob d625f6e977d222c3bbc540de9e7fd2215a4def17. No source SHA substitution. Source and verified locked dependencies may be downloaded during preparation only; audit lifecycle scripts, integrity, then deny egress before executing project or dependency code. No real Zalo, QR, credentials, cookies, real customer data, paid AI, new infra costs, live services, VPS, upstream writes, Hosting main/merge, business-code changes or new product roadmap. Exactly one synthetic account, 3 synthetic customer IDs (two same display names), 2 overlapping groups, fake transport and deterministic fake LLM, temp state. MAX_PAID_API_USD=0; MAX_NEW_INFRA_COST_USD=0. STOP unsafe operations and record blockers; preserve source. Evidence per case: SHA/harness hash, versions, command/exit, expected/observed, sanitized logs, repetitions, fake/real outbound counts, scope, PASS/FAIL/BLOCKED/NOT_RUN/FEATURE_GAP. Defect reproduction is not feature PASS. Handoff is PREPARED_FOR_OWNER_FORWARD until actual recipient ACK. No other agent edits your report. No Codex/Hermes/Hostinger activation.

READ_SET: pinned upstream and Hosting rules/task; related PoC01/02 reports and peer design reports.
WRITE_SET: reports/2026-11-24-openclaw-poc-01-a1.md and no code or other artifacts on a1/openclaw-poc-01-2026-11-24 only. No peer writes, no upstream changes. ACCEPTANCE: source-pinned report with case matrix and evidence boundaries, remote readback. Fallback: Coordinator can absorb source design if A1/A2 unavailable; native runner or independent reviewer cannot be assumed. Independent QA capability gap remains until real preflight and separate ACK.
