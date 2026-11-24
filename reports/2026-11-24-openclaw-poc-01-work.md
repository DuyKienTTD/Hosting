# OPENCLAW-POC-01 — Work native baseline

**TASK_ACKNOWLEDGED — OPENCLAW-POC-01-WORK-NATIVE** · 24/11/2026 · **NEXT_OWNER:** Coordinator for independent re-execution and S3. **Overall: PARTIAL / HOLD.**

Source `openclaw/openclaw@391dea93e0a97fff97f9f3d5e94eac992b247b09`; archive SHA-256 `a51bf3d0716c0b643c97ccb2681ed0903c4c622205e02ecb36afa9e87be4fff5`; lockfile blob `d625f6e977d222c3bbc540de9e7fd2215a4def17`. Work order at `2f5643d0bf4e89caa345fa1d673381ca56e195fd`, blob `42bab7d16cfeae1eed34d99d6adcd3cfc5416efc`. Hosting rules/profile blobs in AGENTS, workflow, repository security, STATE, CATALOG, profile order: `af42293a8ae7d3e864cd9f89442bc6861e85c080`, `9dd6a1601e9b2a1b472f4a1ae89e9626ada05797`, `c24d608036b11dcd3fafcaefbefa23fdb591990e`, `d74e6f3e7cc8bad0192f4a025e25d70aaa83d708`, `26e125296fd0c39d0e82d6c5438dcc1ca2d8947f`, `97071fc9e39d314791710a645868cd63878d5afb`.

Node 24.22.3, pinned native pnpm 12.15.0, Vitest 5.0.5, plugin 2026.11.7, zca-js 2.2.0. pnpm wrapper matched packageManager SHA-512 and executable tarball matched registry integrity. Preparation hit proxy tunnel errors and a 4.9 GB /tmp limit, recovered on workspace disk. Filtered install missed UI and markdown workspace links. Full frozen offline dependency linking succeeded, with lifecycle scripts disabled, and **only five targeted test files executed**. No approval of package skills. Tests used stock synthetic mocks and temporary state; custom fixed three-customer/two-group account scenario was not established. TCP probe to TEST-NET inside unshare -Urn returned ENETUNREACH. No real Zalo, paid API, live provider or upstream/Hosting main write. Real outbound 0 by sandbox boundary; no aggregate fake send counter asserted across stock suites.

| Case | Result | Evidence and limits |
|---|---|---|
| OC01 | PARTIAL / BLOCKED packaged build/load | Vitest loads plugin source modules and executes both configs. Targeted tsc command exit 2 with missing generated plugin-SDK declarations. No packaged build or production entrypoint load asserted. |
| OC02 | PASS mocked cancellation / BLOCKED policy fence | Original send suites verify cancellation during guarded DNS/SDK preparation and awaited callback. Physical initiation, authoritative STOP and cross-process policy races not demonstrated. |
| OC03 | PARTIAL | Stock text chunk, media, uploads and attachment-tool error dispatch cases pass. Reaction and scheduler excluded; full send manifest unverified. |
| OC04 | PARTIAL | Overlapping caller checks remain separate on same cached SDK client. Account-scope suite passes DM pairing-store scoping. No complete same-display-name/wrong-recipient or concurrent policy-cancellation matrix. |
| OC05 | FAIL native baseline case / PARTIAL recovery | Native durable-first case timed out after 5000ms waiting for completed verdict, observed on two invocations. Fresh drain recovery, duplicate rejection and stop/prune cases passed. True process-kill/restart exactly-once unverified. |
| OC06 | FEATURE_GAP, native evidence | Original group-gating test passes while asserting unmentioned skipped text appears in next processed InboundHistory. Pinned ingress serializes raw payload before downstream monitor dispatch. No independent retention consent demonstrated; transcript/log/cache/memory/media lifecycle and revocation not verified. |
| OC07 | BLOCKED | Session-scoped group history visible in source; no DM/X/Y shared workspace memory isolation proof. |
| OC08 | BLOCKED | No complete consented DM → identity → policy → allowed storage → synthetic KB → fake LLM → gated exactly-once send → opt-out/STOP and restart replay fixture. Existing partial tests cannot certify it. |

Native totals: send command 21/21 PASS, exit 0; ingress/group/account command 34/35 PASS, exit 1. Totals include successful assertion of existing history behavior and do not constitute retention acceptance. Preserve native timeout and retention findings for S3. No business source changes. Independent reviewer must be separate from Work. No live readiness or activation.

[Native log](../experiments/openclaw-poc-01/work/native.log) · [Sandbox runner](../experiments/openclaw-poc-01/work/sandbox.sh) · [Source-only fixture](../experiments/openclaw-poc-01/work/source-check.mjs). Runner SHA-256 `823b8cc1b6603909ee1e1e8e68533d8d66c87b63a5ed56a5a6cdaa6a7fda84fa`; source fixture SHA-256 `26501ef7755965d6260f6bfbb3b518e5752955eaf35afb05cad163668997bd82`.

## Final bounded S2 — 24/11/2026

**TASK_ACKNOWLEDGED CONTINUATION — OPENCLAW-POC-01-WORK-NATIVE. NEXT_OWNER Coordinator. Verdict PARTIAL / HOLD.** [S2 directive](https://github.com/DuyKienTTD/Hosting/blob/f3ca095fdadb57a95cb583f8937008e04b2a52ca/reports/2026-11-24-openclaw-poc-01-coordinator.md).

Same upstream SHA, lock blob, Node, pnpm and Vitest as S1. Existing runner SHA-256 823b8cc1b6603909ee1e1e8e68533d8d66c87b63a5ed56a5a6cdaa6a7fda84fa. Fresh clean environment and temporary state per invocation, network namespace with TCP denial, no paid services or real outbound. Stock synthetic account per fixture. No edits to product code. Prior passed suites were not rerun. A1/A2 branches checked with no peer design reports surfaced in comparison.

| Case | Final disposition |
|---|---|
| OC01 | PARTIAL / BLOCKED packaged build: S1 source-module load evidence retained; generated SDK declaration gate untouched. |
| OC02 | PASS at fake transport boundary / BLOCKED authoritative STOP. S1 stock test explicitly counted zero requests when canceled during effect preparation and one when first dispatched, canceled, then allowed to finish. In S2 a new synthetic STOP during SDK cookie wait caused 0 stopped DM requests, with 1 allowed group request. No claim that real or cross-process business STOP reaches that cancellation signal. |
| OC03 | PARTIAL: stock multipart/media/attachment evidence retained. Reaction/scheduler excluded. |
| OC04 | PASS bounded same-ID type/cancellation fixture: canceled user:201 and allowed group:201 on same cached SDK client. Asserted single group transport request with grid=201, correct body, no DM request. Broader identity authorization matrix not established. |
| OC05 | FAIL/PARTIAL from S1. Recovered/drained and dedup passed in S1, durable-first timeout twice. S2 raw enqueue fixture passes, without asserting exactly once through actual process restart. No timeout inflation or diagnostic rerun, because consent blocks OC08 independently. |
| OC06 | FEATURE_GAP. Native parsed stock schema preserves allowlist and historyLimit=0 and strips proposed independent consent keys. Source schema exposes no separate per-sender retention/response controls. New broker-backed fixture captures raw payload accepted by real test queue before downstream decision seam; this is a queue instrumentation result, not a denied DM/group end-to-end scenario. S1 native stock group fixture demonstrates skipped no-mention text reaching subsequent InboundHistory. No transcript/cache/media/memory consent lifecycle established. |
| OC07 | BLOCKED: no DM/X/Y shared-workspace isolation proof. |
| OC08 | BLOCKED_FEATURE_GAP: stock configuration lacks consent primitive required by slice. No fabricated policy, KB/LLM success or restart claim. |
| OC-Q01 | BLOCKED: Work authored and executed fixtures; no independent reviewer runner/ACK evidence. |

New unique assertions: schema 1 PASS; same-ID fake transport 1 PASS (exit 0); broker-backed raw queue 1 PASS (exit 0, previously passed schema skipped). First raw queue attempt in non-broker Vitest shard failed with Shared-state admission requires the host broker. First wrapper selected no files because extensions dir expects a relative include; exit zero there was not evidence. Corrected test-only config uses broker and disables passWithNoTests. Log includes both diagnostic attempts.

[Native log](../experiments/openclaw-poc-01/work/s2-native.log) · [Test-only fixtures and invocation](../experiments/openclaw-poc-01/work/s2-fixtures.md). Fixture SHA-256 (send, schema/queue, config): `397842f1c93387dd267fcdc67716b7216d91861c5f71a93cd71b1fa4b9fab598`, `ec8bc13148955cb61cfeef777085055553c319aec0d4ac0b40458645105ac4bb`, `58ed0609dc9cafa543b5c31481f46f8488f929668d7850d21aa99c886a82bf4d`. No production, merge, upstream or live account changes.
