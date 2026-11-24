---
id: ttd-zalo-mvp01-dev-work
type: report
status: ready-for-independent-mvp-runtime-review
owner: ChatGPT Work
task_id: TTD-ZALO-MVP01-DEV
lifecycle: DURABLE
updated_at: 2026-11-25
sensitivity: public
---
# TTD Zalo Assistant — M0 Foundation handoff

TASK_ACKNOWLEDGED in recipient Work session. [Exact work order](https://github.com/DuyKienTTD/Hosting/blob/ab2eb39e657606a276d5bfe2dab03cae2fd1fc5e/tasks/2026-11-24-ttd-zalo-mvp01-dev.md) · [Execution authority](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7140477073) · [Approved-adjustments roadmap](https://github.com/DuyKienTTD/Hosting/blob/7e8d9b68715948bcfc53b2a2cf6543600e63db43/program/zalo-mvp01/ROADMAP.md).

Base remote main 097c080cc6d7fb3ca36b1849d9c10375d5cbd67f, tree e323aa0a1a8b2d89e4c353cdf77f32c853ab153e. Branch dev/ttd-zalo-mvp01 was absent at preflight. Source and tests only under app write-set. HEAD/tree pinned in handoff. M0 foundation is reusable product code. M1–M5 remain gated on M0 acceptance.

| Gate | Result |
|---|---|
| Toolchain and isolation | Node 24.22.3, npm 11.19.1, Linux x64. SQLite in-memory SELECT passed. unshare network namespace test to TEST-NET returned code 101 (ENETUNREACH). |
| Dependency/build | npm lock SHA-256 a7fd482841c3e1c50c92daa945d89ac358567b86b141e7da9a8b30c027aba9b3. All 104 non-root lock records include npm registry resolution and integrity. Install scripts disabled; Electron/esbuild are the flagged lifecycle packages. Both Electron archives matched upstream v40.0.0 SHASUMS256.txt. TypeScript typecheck and build exit 0. |
| Foundation | 5/5 native tests PASS (exit 0). Stable IDs, independent consent flags, denied defaults, wrong target/content, single fake receipt, SQLite reopen, STOP with separate connection during deferred preparation, opt-out, expiry, takeover, child exit after reservation and restart no replay. One fake receipt in positive test and zero in negatives. No real provider calls or charges. |
| IPC / Electron | Sender/main-frame/document/arity and input validation, isolated sandboxed preload, CSP, web request allowlist, blocked permissions/downloads and navigation in source. Runtime IPC rejection and UI smoke BLOCKED. |
| Linux desktop | Xvfb inside isolated namespace cannot establish Unix socket. Non-root Electron with headless Ozone fails at Chromium ProcessSingleton socket() EPERM. No sandbox disable flag used. No screenshot or UI PASS claimed. |
| Windows x64 package | Offline package script exit 0; ZIP test passed and stock Windows x86-64 PE executable verified. ZIP SHA-256 d35d078cffa1a0fddd5787da0ac2d195af8f414c1ba2e9bbfbd4533e96687b8f. No Windows-native launch verified. |
| Independent runtime | BLOCKED pending executable reviewer runner and ACK. Windows smoke instructions are in app README. |

**Disposition M0_PARTIAL / RUNTIME_ACCEPTANCE_BLOCKED.** Next owner Coordinator for a verified sandbox-capable desktop runner and independent Windows launch/review. Run existing UI smoke with Chromium sandbox enabled in a blocked-egress environment that allows local IPC sockets, and record exact package hash, Windows build and screenshot/IPC results. Preserve branch for continuation on the same tree. No POC rerun, real Zalo, paid APIs, production, merge or new infrastructure.

## M1–M5 — Integrated offline MVP delivery

TASK_ACKNOWLEDGED CONTINUATION in the Work session. [M0 acceptance and continuation](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7141667261) · [Independent M0 runtime receipt](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7141651032). Existing M0 limitations above reflect the original run; the Coordinator subsequently accepted M0 for offline continuation. M0 base b542486123b7eebe1b2a3cd0dbd2614c512d0ec0, tree fcac92bac892c27cf544021939b63e22e9c3e66a. Foundation shared code changed, so affected M0 cases were rerun. No upstream or POC execution. Reused A1 STOP/identity/idempotency scenarios and A2 consent, raw-store sentinel and scoped memory scenarios from the approved roadmap. M0 Windows receipt is historical evidence, not a pass for the new package.

| Scope | Delivered and evidence |
|---|---|
| M1 | Vietnamese conversation list/details, synthetic DM input, per-target retain/respond/send, STOP and takeover. Denied messages leave audit metadata only. Response-only retains dedup ID and timestamp, never raw body. |
| M2 | Source-linked customer memories from authorized retained messages and structured local TXT knowledge import/search. Same-name customers stay separated by stable IDs. No remote document reads or instruction execution. |
| M3 | Deterministic Fake LLM uses exact SKU evidence. Unknown price asks for clarification. Editable draft, exact target/content approval, revision and STOP recheck, one fake receipt per inbound event. |
| M4 | SQLite schema 1-to-2 migration preserves M0 receipts and policy. Durable unique reservation, STOP/revoke during deferred preparation, interrupted-attempt view and fail-closed restart. Content-free audit with no automatic retries. Previously lawfully retained text remains on disk, access gated on current retain permission. |
| M5 | Windows x64 portable ZIP, six functional screens in source, offline instructions and targeted automated smoke entrypoint. Independent exact-tree UI, real Windows launch and runtime IPC/sandbox QA remain open. |

### Work evidence

Node 24.22.3, npm 11.19.1, Electron 40.0.0. Lock SHA-256 a7fd482841c3e1c50c92daa945d89ac358567b86b141e7da9a8b30c027aba9b3 unchanged from M0. Egress probe 101 ENETUNREACH. In fresh network namespace: npm run typecheck exit 0; npm run build exit 0; npm test exit 0, 10/10 (5 new, 5 affected Foundation regressions). New cases cover positive fake DM/edit/approve/one receipt, wrong recipient, draft invalidation, duplicate intent/reopen, raw denial and ephemeral sentinels absent from SQLite, scoped provenance, unknown price, takeover after reserve, no retry and exact M0 schema migration. Real outbound 0, paid calls 0. The positive vertical-slice test directly executes integrated business methods against SQLite; it does not exercise Electron IPC or rendered UI.

Package script ran offline and verified Electron distribution checksum and ZIP integrity. TTD-Zalo-Assistant-MVP01-win-x64.zip SHA-256 a2f7651e3472fd6963ec7d3fe6e3e541634912768302eb8869d4b8a27a3cf0b7. No binary in Git. Executable extracted from pinned Windows x64 distribution with bundled app. Exact Linux runtime probe used non-root mapped user + isolated net + Chromium sandbox, but exited before IPC/UI at ProcessSingleton socket() EPERM. No final screenshot or fresh Windows run claimed.

**Disposition: MVP_DEVELOPER_BUILD_READY / INDEPENDENT_RUNTIME_QA_BLOCKED.** NEXT_OWNER Chat Điều phối. Schedule independent executable QA on isolated Windows x64 with final archive hash and exact branch commit/tree, following [application instructions](../apps/ttd-zalo-assistant/README.md). Verify launch, IPC rejection, positive and negative GUI journeys, persistence/restart and zero real outbound. Compare authorized UI and packaged behavior to native data-path tests. No real Zalo, paid APIs, deployment, production, merge or new infrastructure.

## 2026-11-25 — Final startup diagnostic review

**Disposition: ROOT_CAUSE_UNKNOWN · residual intermittent white window · no product patch.** Candidate `d49d795aca2550cb143957141aaf60ed304b28e0`, tree `81b4c0b86a1e9b67da6eddb47a52c9c8c5e167d1`, and the tested ZIP remain the evidence identities. This update records a review of GitHub receipts, without direct inspection of the private logs or screenshots.

- **Explorer launch rendered.** The disposable instrumented copy recorded first rAF timestamp +175.1 ms, first paint +187.7 ms, React commit +211.0 ms and FCP +227.7 ms. Final capture showed populated UI. First paint precedes React's marker and alone does not establish React content. FCP and the populated capture corroborate delivery of visible content. [Codex receipt](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7144606748)
- **Foreground at render remains unverified.** Win32 sampled Explorer at −8.7 ms and first matched app HWND/PID at +391.3 ms. This 400 ms gap covers window creation, both paints and React commit. Later 162 matching samples and document visible/hasFocus cannot establish foreground during that interval. Synchronous process-ancestry lookup in the sample loop is a diagnostic limitation, not a product-cause finding.
- **B remains valid at sampled points.** Cover confirmed 166/166, app non-minimized. React committed at +412.0 ms while document hidden. Paint/FCP/rAF unobserved through +8 s and final capture white. The earlier A had zero verified app-foreground samples. The latest positive launch leaves no valid foreground counterfactual for B. [A/B receipt](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7143547803)
- **Final QA remains evidence of exercised paths.** Prior successful launch and workflow prove the package can render and function in at least one condition. Differences in focus, timing or automation conditions prevent a startup-causality or stability claim. [Final QA](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7142182692)

Evidence supports no targeted source change. Close this diagnostic as UNKNOWN with residual risk preserved. Per [Coordinator receipt](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7144639539), the one-launch allowance is consumed. Firewall baseline restored per Codex; disposable scratch residue from the access-denied DLL remains locally. This review performed no extra tests, retries, cleanup or permission changes. **NEXT_OWNER: Chat Điều phối.**
