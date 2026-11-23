---
id: report-2026-11-23-a1-ops01a-s2-d2-lifecycle
type: report
status: author-delivered-pending-independent-qa
updated_at: 2026-11-23
owner: a1
sensitivity: public-redacted
---

# A1-OPS01A-S2-D2 — D2 offline remediation delta and actual tests

**OWNER:** A1. **ACK:** `A1-OPS01A-S2-D2`. **BASE:** PR #24 `e9c2d8f759850ea9c654de7e103549e041f66679` / lifecycle blob `c5f5db8cfff48563e9f8d2640d0a910c4d56af25`. Main/rules `e385c1bea2070973e3007e5717f7e980348d6ab3`. Work 18 independent negative groups [#7092910873](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7092910873) gave `NEEDS_HOSTINGER_DELTA`. A0 withdrew Hostinger D2 assignment and transferred ownership to A1 [#7093346631](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7093346631); Hostinger must acknowledge when service recovers to prevent dual writers. The Hostinger PR #24 source and historical D1 report/evidence have **not** been modified.

## Implementation and bounded decisions

- **F1:** Valid trusted synthetic `UNKNOWN`, stale or blocked observation from correct resource/source/rule version (and matching explicit rule, if supplied) with a valid strictly later UTC timestamp interrupts both bad/good streaks. **Only** `bad_streak` and `good_streak` may reset to zero, plus `TRUSTED_INTERRUPTION` audit entry. Do not advance `last_ts`, consume sample ID, change state/incident/notification fields. A later single good cannot recover; only **three new** qualifying good samples can. Invalid foreign source/resource/rule, malformed payload, exact/conflicting replay and non-advancing UTC leave entire control snapshot untouched. This is an explicit conservative synthetic policy, not production identity validation.
- **F2:** `sample_id` is a nonempty, 1–128-character bounded ASCII string with `A–Z/a–z/0–9/_.:-` characters; reject list/dict/float/bytes/null/empty/oversize/invalid chars with deterministic `INVALID_SAMPLE_ID` and null audit ID. Disallow unsupported extra keys; JSON canonicalization rejects non-JSON objects, NaN/Infinity and cyclic inputs with `INVALID_PAYLOAD` before seen-ID/time/streak changes. Only bounded safe IDs (or null) enter audit; no raw payload or PII recorded. Preserve exact and conflicting replay and synthetic snapshot/reload.
- **F3:** Optional `rule` is **backward-compatible absent** for *single-rule synthetic v1 fixtures only*. If present it must equal `N8N_READINESS` configured rule, else `RULE_MISMATCH` before trusted control mutation. It is **not server authorization** or a real trusted source identity.
- **P:** Source checks sample ID / required and allowed fields / finite canonical JSON / scalar types / UTC parse / resource-source-version-optional-rule / replay **before** strict UTC watermark / trusted status / state transition. Policy JSON and README now match. `PinnedS1Evaluator` remains a local hand-authored stand-in: **S1_EQUIVALENCE_FIXTURE_ONLY**, not PR22 runtime import or real integration.

## Expected / observed — actual local Python execution

| Group | Expected | Observed |
| --- | --- | --- |
| F1 3 interruption causes | UNKNOWN/stale/blocked after two goods break streak; next one good NOT RECOVERED | PASS for 3 targeted tests; `TRUSTED_INTERRUPTION`, streak reset and OPEN retained |
| F1 recovery after interruption | Three new consecutive goods to RECOVERED | PASS; no early recovery |
| F1 bad streak NORMAL/RECOVERED | Bad ×2 then trusted interruption requires fresh bad ×3 to OPEN | PASS in both states |
| F1 foreign inputs | Foreign resource/source/version/wrong rule cannot reset good streak | PASS; identical control snapshot, audit only |
| F2 IDs/payload | Reject invalid list/dict/float/non-string/empty/oversize/NaN/Infinity/cycle/unknown field; no exceptions/poisoning | PASS; `INVALID_SAMPLE_ID` or `INVALID_PAYLOAD`, bounded audit and corrected input accepted |
| F3 rule | Wrong explicit rule blocked; exact rule allowed; absent allowed only in synthetic v1 | PASS |
| Policy order | Replay precedes watermark, rule identity precedes replay | PASS, source and JSON policy aligned |
| D1 invariants | OPEN +899 suppressed; +900/+901 notification only, same incident ID; RECOVERED fresh incident; UTC/replay/snapshot isolation | PASS, related 10 D1 + 2 extra D2 regression methods |

**Actual command:** `python3 -m unittest discover -s sandbox/ops-monitoring-lifecycle/tests -p test_lifecycle.py -v`. **Observed:** 31 tests, 0 failures, 0 errors, exit 0; **21 D2 new** and **10 D1 existing** related regression methods. Python 3.13.5, Git 2.47.3, Linux offline synthetic. `python3 -m py_compile` and JSON policy parse succeeded. All 4 original source files were reconstructed from exact GitHub contents and independently verified against their original Git blob IDs before changes; local Git blob hash of each new file recorded in evidence JSON. GitHub DNS clone was blocked, GitHub connector is used for branch/PR write/readback. No previous Work 18 QA tests rerun; no full historic S1 suite.

**LIMITATIONS:** This proves only authored offline fixture behavior, not independent Work QA, real S1 composition, production monitoring, real alert delivery, durable storage, security controls or consent. Hostinger service pause remains a dispatch event, not a Git branch state. **No live VPS/production/paid action, no Codex, no merge.**

**AUTHOR VERDICT:** `A1_OPS01A_S2_D2_AUTHOR_TESTS_PASS_OFFLINE_PENDING_WORK_QA`. Next owner: **ChatGPT Điều phối**, dispatch Work for independent QA on exact A1 stacked PR HEAD. Release/merge authority: **NOT_GRANTED**.
