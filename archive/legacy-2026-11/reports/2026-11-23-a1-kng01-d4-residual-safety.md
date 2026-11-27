---
id: report-2026-11-23-a1-kng01-d4-residual-safety
type: report
owner: a1
status: author-d4-verified-targeted-pending-independent-qa
updated_at: 2026-11-23
sensitivity: public-redacted
---

# KNG-01 D4 — F4/F5 residual safety corrective

**TASK (continuation):** `A1-KNG01-GIT-NORMALIZATION-D1 / D4-RESIDUAL-SAFETY`; A1 ACK in current session. **Scope:** existing PR #41, `program/kng/derive.py`, `program/kng/test_derive_d3.py` regression adaptation, `program/kng/test_derive_d4.py`, this author evidence. Work D3 independent finding: [#7100992593](https://github.com/DuyKienTTD/Hosting/pull/41#issuecomment-7100992593); director grant [#7101315242](https://github.com/DuyKienTTD/Hosting/pull/41#issuecomment-7101315242). Source head at start: `22887822af3db35cd87a289b0475cc0a21f91450`; PR40 `68780956eab29581bd3dab5acc6924093c4019a7`, main `e385c1bea2070973e3007e5717f7e980348d6ab3`.

## F4 — outer state and transition validation

`derive._validate_outer` requires WS-02 handoff state in `{UNKNOWN, PREPARED_FOR_OWNER_FORWARD, ACKNOWLEDGED}` and report review state in `{UNKNOWN_NEW_REPORT, PENDING_REVIEW, REJECTED_PAPER_EXERCISE, ACCEPTED_PAPER_EXERCISE}`. Invalid/empty/null values fail with `WS02_STATUS_INVALID` or `WS02_REVIEW_STATE_INVALID`. A frozen historical pre-KNG handoff cannot transition to ACKNOWLEDGED. Pending/rejected review records cannot expose an accepted evidence row. These checks execute in `verified_views` **before** either generated view or any write. Both `--check` and `--write` return nonzero for invalid status and leave STATE/CATALOG bytes unchanged.

## F5 — Git object presence is not sufficient authorization

**Trust boundary:** actor names, Git commit author metadata, JSON body fields, plausible URLs, full SHA values and a self-published approval object are all untrusted claims. `derive.TRUSTED_DECISIONS` is an **empty, default-deny, code-reviewed trust root**; it cannot be sourced from `program/current.json` or any unreviewed Git object. A future authorized immutable decision must be independently checked by A0/Chat Điều phối and source-reviewed before its **exact event ID + subject commit/path/blob + distinct approval commit/path/blob + reviewer** pin may be added under a separately granted approval. No such WS-02 operational decision was provided, so NO real ACK or accepted report can be emitted today.

`_authorized` validates exact independent registry pins, immutable event ID, reviewer role (`A0` or `Chat Điều phối`), distinct approval object and approval JSON binding to *kind, event, task, actor, decision and exact subject*. `_git_evidence` validates the Git subject and approval object blobs; acceptance also requires `evidence_ref` as a real resolvable nonempty Git blob, not a self-matching string. Synthetic trusted-positive tests use explicitly injected local test-only anchors and genuine local Git commits to check conditional behavior. **They are not proof of an actual A0/Work acknowledgement or approval.** Default execution with real-looking fixture Git objects lacking an independently pinned decision fails `AUTHORITY_UNVERIFIED` and does not write.

## Actual Linux author tests

Linux `Python 3.13.5`, `Git 2.47.3` in `/mnt/data/kng_d4`, isolated synthetic Git repositories only. Source code loaded from the prior D3 worktree and modified in scope. No network git clone (GitHub DNS unavailable). Executed:

| Command | Expected | Observed |
| --- | --- | --- |
| `python3 -m py_compile derive.py test_derive_d3.py test_derive_d4.py provenance.py` | exit 0 | **PASS** |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p test_derive_d3.py -q` | 14 PASS | **14/14 PASS**, 0 failures/errors |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p test_derive_d4.py -q` | all pass (includes 14 inherited D3 tests twice through unittest discovery/import) | **41/41 PASS**, 0 failures/errors |
| `git hash-object derive.py test_derive_d3.py test_derive_d4.py` | exact source blob IDs | `bad477a5c4c628f39b5cf1590de7f1843c5139ed`, `e7bbc8b7793d6197bb3805bad5e67d6d42da8e64`, `04b587689c4fec2fefdc1ea75e3853eaa09e8fca` |

**Specific negative probes:** F4 wrong outer status or review status including `INVALID_STATUS`/null; frozen pre-KNG ACK transition; pending report with evidence; F5 forged actor name/Git author metadata; valid Git receipt plus unapproved authority; fake reviewer and rejected decision; source-and-claim matching nonexistent evidence; approval pinned in a test but unresolved report evidence. Both CLI modes explicitly tested with exit nonzero and byte-for-byte unchanged STATE.md and CATALOG.yaml. Positive synthetic tests verify a reviewed-pinned ACK/report can render, a real evidence ref must resolve, check-mode PASS after write and repeated `--write` is idempotent. No production event manufactured. D3 prior positive-shaped but **unapproved** test cases were correctly updated to negative tests; equivalent *authorized synthetic* positives are exercised in the D4 suite.

**LIMIT:** Full official `test_validate.py` suite and default Hosting Git graph validation **NOT_RUN** by A1 because GitHub is not resolvable from this Linux runtime. Work D3 independently verified 30/30 official + 14/14 D3 and old default validator PASS on the predecessor SHA, but these do not certify the new code. Other D2 source/migration/WBS/Q0 findings remain unchanged; this D4 change does not touch six shared migration files or `program/current.json`.

## Author handoff and STOP

**AUTHOR VERDICT:** `KNG01_A1_D4_READY_FOR_TARGETED_QA` **for source available for Work independent review**, with **FULL_CHECKOUT_TEST_NOT_RUN** explicitly outstanding. Work must independently test both F4/F5 against a pinned complete checkout, verify default-deny approval mechanism and rejected mode byte equality, audit conditional synthetic positive against the external-authority boundary, then issue its own verdict. No false `KNG_ACCEPTED`/production readiness. No PR31/main/PR40/PR39 writes, merge, branch rewrite, paid API, VPS, Codex or external dispatch.

**NEXT_OWNER:** Chat Điều phối → Work independent D4 targeted QA.
