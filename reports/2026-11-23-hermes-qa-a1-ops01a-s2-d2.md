---
id: report-2026-11-23-hermes-qa-a1-ops01a-s2-d2
type: report
status: independent-qa-needs-a1-delta-comment-blocked
updated_at: 2026-11-23
owner: hermes-webui
next_owner: chatgpt
sensitivity: public-redacted
---
# QA-A1-OPS01A-S2-D2-HERMES — independent, pinned, offline

**ACK:** [assignment PR36 #7093565021](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7093565021). `PR36_HEAD=6838ca7d5e69b43f5272e5fe7f03ba5fff1d7222`, `PR24_BASE=e9c2d8f759850ea9c654de7e103549e041f66679`, `MAIN=e385c1bea2070973e3007e5717f7e980348d6ab3`. PR36 is open/draft, seven changed paths exactly as assignment; Hostinger PR24 remains at its pinned HEAD. A1 lifecycle source Git blob `6d138ab6e044fc85067b9bbf7f6ae0db8a50af78`, report `cddd48765d8877fc6599915c91a0ba60a327d6b0`, evidence `422621278670a04b3adf0593bbbfe011bcf78f32`; four A1 new source blobs and four PR24 baseline blobs matched ledger. No PR24 shared metadata diff. A1 31/31 author-test claim is **not** counted as our own tests. Work's [18 scenario groups on old D1 #7092910873](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7092910873) are background, not rerun.

Rules read at main: `AGENTS.md@cb6a8af9d2634cc4eb959132d6c3f2fafcbfaf35`, `AGENT_WORKFLOW.md@69ec0db902f457f06dd547dae171220331df0f5e` §§7–10; `REPOSITORY_SECURITY.md@c24d608036b11dcd3fafcaefbefa23fdb591990e`, `STATE.md@c8e8941aa1418f70ed9542063f0485a129739d25`, `CATALOG.yaml@719c9c5d2832382285d732b9ad21f55d8c163733`, `agents/hermes.md@618b8efce4738e242f54788d46d77068b8f747fa`. PR31 §11 remains unmerged; does not grant Codex/merge/production authorization. README/PROJECT/agents overview were read from pinned Git tree. No source, test, PR24, PR31 or shared metadata changed.

## Actual independent execution

CPython **3.14.10**, stdlib, pinned source import from detached read-only QA worktree. [Reproducer](evidence/2026-11-23-hermes-qa-ops01a-s2-d2-reproducer.py) and [21-case machine-readable expected/observed](evidence/2026-11-23-hermes-qa-ops01a-s2-d2-results.json). **21 independent scenario groups: 19 PASS, 2 FAIL, 0 exceptions**. No A1 31-case suite or Work old 18-case suite counted as ours. Reproducer invokes only `Lifecycle.ingest/snapshot/restore`; no API, real metrics, notification, paid provider, VPS or GitHub Actions.

- **F1 baseline PASS:** OPEN good×2 → trusted UNKNOWN → next good remains OPEN, three fresh goods recover. NORMAL and RECOVERED bad×2 → blocked → three fresh bads needed. Duplicate valid ID, stale timestamp, foreign resource/source/rule/version cannot break streak; interruption leaves `last_ts`, `seen`, `incident_seq`, notification timestamp and state unchanged. A replay after *watermark already advanced beyond interruption* is rejected as `NON_ADVANCING_TIMESTAMP` (not an EXACT_REPLAY), without resetting the newer streak.
- **F2 PASS:** list/dict/bytes/empty/overlength/non-ASCII ID sanitized to `INVALID_SAMPLE_ID` with null audit ID. Non-dict, NaN, Infinity, unserializable allowed field, cycle and unexpected field → `INVALID_PAYLOAD`, no TypeError/control mutation/raw payload in audit; corrected ID accepted, later conflicts rejected, restore preserves valid-ID replay.
- **F3/P PASS in synthetic scope:** wrong explicit rule with future timestamp and same ID cannot poison state; corrected matching rule reaches OPEN. Omitted rule accepted on synthetic single-rule v1 fixture only (not evidence of authentication). Replay-before-watermark and rule-before-replay ordering matches policy/source. `PinnedS1Evaluator` stays `S1_EQUIVALENCE_FIXTURE_ONLY`, not a live S1 import.
- **D1 regression PASS:** OPEN +899 suppresses notification; +900/+901 notify without changing incident 1 ID. RECOVERED +899/+900/+901 creates incident 2 with separate notification eligibility, all fixture-only.

## Blocking novel F1 — trusted interruption replay is not idempotent

Minimal reproducer with exact same sample ID and payload:

1. Open incident with synthetic bad at `00:00:00Z`, `:01Z`, `:02Z`. Ingest good `g1@00:00:10Z`, `g2@00:00:11Z` → `good_streak=2`.
2. Ingest correctly attributed `U@00:00:12Z`, `signal=unknown`. It resets streak but **does not** update `last_ts` or `seen`, by policy.
3. Ingest fresh good `g3@00:00:11.100000Z` and `g4@00:00:11.200000Z`. Both are accepted because `last_ts` was not advanced by U; `good_streak=2`, state OPEN.
4. **Replay identical U**. Its timestamp is still later than trusted watermark `:11.2Z`, and U was never recorded in `seen`. Observed: **another `TRUSTED_INTERRUPTION`, streak 2→0**; `g5@00:00:13Z` produces no RECOVERED. Expected: an already applied interruption must not reset subsequent good streak twice; a one-time replay record/dedicated dedupe policy should make g5 the third fresh good and RECOVERED.
5. Variant: after step 3 snapshot/restore, replay U with same ID and different stale payload. Observed **same second reset** instead of conflicting replay. Both novel cases FAIL in the attached test matrix. In-order replay after watermark advances is harmless but insufficient to prove idempotence.

This is a **material lifecycle regression** under a permitted timestamp sequence. The policy deliberately avoids advancing the trusted watermark and consuming valid `seen` IDs, so it needs an explicit, persisted **separate interruption replay/dedupe record** (or another reviewed policy with equivalent idempotence) and negative fixtures for exact and conflicting replay before/after snapshot restore. Decide semantics for later corrected valid sample with the same ID; do not silently treat diagnostic audit as a replay ledger. Re-test F1 plus F2/F3/P/cooldown targeted after A1 delta. Source lines: `sandbox/ops-monitoring-lifecycle/lifecycle.py` replay check `if sid in self.seen`, interruption branch resets streaks but does not record sid; `snapshot/restore` carries only `seen` and `audit`.

**VERDICT: `NEEDS_A1_DELTA`** — the three original Work findings largely behave as claimed, but the new replay-induced second reset blocks independent QA PASS. Author's 31/31 and this 19/21 cannot certify production safety. No merge, no production, paid, VPS, Codex or source edits. GitHub comment write unavailable in this Hermes session (no GitHub vault login; browser shows sign-in-to-comment). This isolated QA branch is fallback evidence **not a PR36 comment**; coordinator with authenticated GitHub must post this verdict/reproducer to PR #36 and read back comment, then assign A1 remediation and a fresh independent re-QA. `TASK=QA-A1-OPS01A-S2-D2-HERMES | AGENT=Hermes | ACK=ACKNOWLEDGED | PR36_HEAD=6838ca7d5e69b43f5272e5fe7f03ba5fff1d7222 | PR24_BASE=e9c2d8f759850ea9c654de7e103549e041f66679 | INDEPENDENT_TESTS=21:19 PASS,2 FAIL | NEW_PROBES=exact and conflicting unrecorded trusted interruption replay before watermark catch-up | F1=NEEDS_DELTA | F2=PASS_MOCK | F3=PASS_MOCK | P=PASS_MOCK | LIMITS=fixture-only, no live S1/notifications | VERDICT=NEEDS_A1_DELTA | EVIDENCE_URL=see blob link after push | NEXT_OWNER=ChatGPT Điều phối`.
