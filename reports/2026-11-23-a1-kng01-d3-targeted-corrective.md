---
id: report-2026-11-23-a1-kng01-d3-targeted-corrective
type: report
owner: a1
status: author-d3-targeted-corrective-partial-full-checkout-suite-blocked
updated_at: 2026-11-23
sensitivity: public-redacted
---

# KNG-01 D3 — A1 targeted corrective, Work D2 findings F1/F2/F3

**Task unchanged:** `A1-KNG01-GIT-NORMALIZATION-D1` · **Phase:** `D3-TARGETED-CORRECTIVE` · **ACK:** A1 ACKNOWLEDGED in actual session · **OWNER:** A1 · **NEXT_OWNER:** Chat Điều phối → Work targeted QA when full-checkout test gate is available.

## Authority / exact baseline and findings

- Source PR41 HEAD at start: `666a32f54bd55cebb88117725a5f8c7c6208ffd0`; base PR40 `68780956eab29581bd3dab5acc6924093c4019a7`, PR31 `a770de80a2467ca1789c820b63416209cf53b7d1`, effective main `e385c1bea2070973e3007e5717f7e980348d6ab3`.
- [Director D3 instructions](https://github.com/DuyKienTTD/Hosting/pull/41#issuecomment-7099943838); [Work independent D2 findings](https://github.com/DuyKienTTD/Hosting/pull/41#issuecomment-7099819982). Work independently recorded full-checkout `validate.py --root . --json` **PASS**, four D1 negative repairs PASS and Git fsck PASS on old SHA, but the shipped Python suite was **28 PASS / 1 FAIL** (positive fixture missing declared files); `derive.py` falsely trusted claim-shaped WS02 ACK/report.
- Sole source writer A1 on existing PR41 branch `a1/kng01-shared-integration-d2-2026-11-23`. **No new PR/task**, no shared-six-file change, no merge/main/production/paid/Codex.

## F1 — correct positive fixture (author implementation)

Updated `program/kng/test_validate.py` `RELS`: include real root `README.md`, `program/kng/derive.py` and `reports/evidence/2026-11-23-a1-kng01-d2-q0-metrics.json` when constructing isolated candidate. Original negative fixtures remain untouched; replaced previously unsafe positive acceptance assertions for `derive.py` with rejection of unverified claims. Explicit negative check for stale Work D2 task binding. Expected positive suite PASS on full checkout, **not independently observed in A1 container**, as direct Linux GitHub clone fails DNS. Work must rerun actual 31+ suite before closing F1. No synthetic fixture test may substitute for this proof.

## F2 — fail-closed derived evidence, real Git object resolution

Updated `program/kng/derive.py`:
- Git commit/path/blob triple must exist and match `git rev-parse <commit>:<path>` and `git cat-file -t` via `GitObjects.verify`. Nonexistent commit/blob/path => explicit `PROVENANCE_UNVERIFIED`, never trusted label. The URL is bound to the exact immutable commit+path when supplied; `https://example.invalid/no-receipt` is rejected even if its shape looks plausible.
- WS02 ACK requires `source_task=tasks/2026-11-22-work-ws02-monitoring-and-triage.md`, `task_id=WS-02`, `actor=Work`, `event=ACK`, `status=ACKNOWLEDGED`, `authorized_task_id=source_task`; immutable Git receipt JSON contents must match each field and exact URL. A receipt when status is not ACK is rejected.
- WS02 paper-report index requires `review_state=ACCEPTED_PAPER_EXERCISE` and real immutable Git report blob; `task_id=WS-02`, `actor=Work`, `disposition=ACCEPTED_PAPER_EXERCISE`, report path and `evidence_ref` must match the **source contents** (structured JSON or Markdown YAML-like frontmatter). UNKNOWN/absent/wrong disposition or wrong actor/task are rejected. A syntactically valid 40-zero SHA can never count as an accepted report.
- `derive.run` validates **both** state and catalog and all evidence **before its first write**. CLI check/write errors exit 1 with a reason; no partial writes on validation failure. Genuine synthetic Git objects used in positive tests demonstrate deterministic output and idempotent second writes.

## F3 — actual Work D2 task binding

`program/current.json.work_ack_task_id` corrected from `WORK-KNG01-TARGETED-D2-REQA` to actual dispatched `WORK-KNG01-D2-TARGETED-INDEPENDENT-REQA`. `validate.py` and `derive.py` both reject stale task binding. Historic Work D2 ACK/verdict recorded as **historical only** with [Work comment](https://github.com/DuyKienTTD/Hosting/pull/41#issuecomment-7099819982), source SHA `666a32f54bd55cebb88117725a5f8c7c6208ffd0`. The field `work_ack=UNKNOWN` and `work_ack_receipt=null` explicitly **do not** assert a Work D3 reviewer ACK; a Work D3 ACK requires its own actual session receipt and authorization. Top-level Work ACK claims with no pinned receipt or pending state fail closed.

## Linux tests actually executed (author, not Work QA)

Linux Python **3.13.5**, Git **2.47.3**. Exact authored local `derive.py` and `test_derive_d3.py` contents independently matched their GitHub `git hash-object` values. Commands:
- `python3 -m py_compile program/kng/derive.py program/kng/test_derive_d3.py` ⇒ **PASS** (no syntax failure).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s program/kng -p test_derive_d3.py -q` ⇒ **14/14 PASS**, 0 failures/errors on isolated local implementation/fixture.
- Negative cases: (1) fake URL ACK; (2) unresolved Git object; (3) wrong task/actor/event/status; (4) stale D2 task ID; (5) top-level Work ACK without evidence; (6) nonexistent report; (7) UNKNOWN review_state; (8) incorrect acceptance disposition; (9) real Git blob with forged acceptance claim in *source body*; (10) CLI check/write rejection. Every relevant fail case asserts pre/post STATE.md and CATALOG.yaml **identical bytes**.
- Positive cases: baseline idempotence, legitimate synthetic Git ACK receipt, legitimate synthetic Git JSON accepted report, legitimate Git Markdown frontmatter accepted report. Second `--write` yields byte-identical files; `--check` PASS.
- **UNRUN, NOT PASS:** full checked-in `python3 -m unittest discover -s program/kng -p test_validate.py -q` on a complete Hosting Git checkout; and default Git-object validator on new HEAD. A1 Linux cannot DNS-resolve `github.com`; GitHub connector can read/write Git blobs but cannot import entire object graph into that runtime. Work D2 previously ran complete checkout on older SHA and found F1; Work D3 must rerun on new SHA. Do not turn author's isolated 14/14 into full-suite certification.

## Preserved D2 findings and safety boundaries

No changes to six shared files, business/technical migration, 32 WBS IDs/Gate/Deliverable, CATALOG stable IDs, links, provenance source pins, or Q0 measured byte inputs except small `current.json` binding update (Q0 legacy numbers remain pinned to D2 and must not be presented as D3 remeasurement). Work independently passed old four D1 fail-open mutations on PR41 before D3; no broad unrelated retest. The KNG-only priority, independent QA, least privilege, paid/production/merge/Codex STOPs and seven PR31 nonshared integration blockers remain.

**Author status:** `KNG01_D3_PARTIAL_BLOCKED_FULL_CHECKOUT_SUITE_UNVERIFIED` until an actual full Hosting checkout run reaches 0 FAIL. Candidate is pushed for **Work targeted technical re-QA**, but do not mark `KNG01_A1_D3_READY_FOR_TARGETED_REQA` as a fully-proven author test gate until suite execution. Work cannot self-certify A1 code; Director decides next gate. **NEXT_OWNER:** Chat Điều phối → Work.
