---
id: report-2026-11-23-a1-kng01-pr42-d5-corrective
type: report
owner: a1
status: author-targeted-d5-source-ready-for-independent-qa
updated_at: 2026-11-23
sensitivity: public-redacted
---

# KNG-01 PR42 D5 — provenance result pin and fail-closed task candidate selector

**TASK/ACK:** `A1-KNG01-PR42-D5-CORRECTIVE`, ACKNOWLEDGED by A1 in actual conversation. **PR:** #42, existing isolated branch `a1/kng01-pr31-nonshared-integration-2026-11-23`. **SOURCE:** `e897ac40fb9121991ee8cdb133d7d63ec14a270f`. **NEXT_OWNER:** Chat Điều phối → Work targeted re-QA. Read [Director D5 grant](https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7102477821) and [Work source QA](https://github.com/DuyKienTTD/Hosting/pull/42#issuecomment-7102397253). No merge, paid operation, production, Codex, or main/PR41/PR31 write.

## F1 — precise integrated CATALOG result pin

- Only `program/kng/migration.json` result assertion for `CATALOG.yaml` changed: `result_blob` **`bf24d5726c8518617f02777aec6d271723946358` → `a611919b6ef42e16e30d14aa650c43fb9bbbe681`**; this equals the actual unchanged PR42 CATALOG Git blob reported by GitHub at source HEAD. `base_blob` PR31 **`60f56a30524f330c51621592b63d6cc626025fc0`** stays unchanged.
- Separate `previous_result_blob` and `previous_result_ref=PR41-D4@b446bce1aa2def210251f41283b96276dbc8fa1c` preserve the historical D4 result pin. `validate.py` still recalculates the current CATALOG blob using Git blob hashing and rejects `INTEGRATED_BLOB_MISMATCH`; it was not modified.
- Added `test_integrated_catalog_result_pin_must_match_actual_blob` to the official suite: a syntactically valid stale result SHA must be rejected even with other fields intact. The positive fixture includes the new file links and selector source/tests, retaining the existing negative tests.
- Actual GitHub comparison: `CATALOG.yaml` source blob `a611919b6ef42e16e30d14aa650c43fb9bbbe681` = updated migration result pin; old PR31 base and prior D4 result pins separately preserved. **Full official Python suite on real Hosting Git checkout NOT_RUN by A1** because the Linux session cannot resolve github.com (`git ls-remote` exit 128). Work earlier observed 29 PASS, 1 FAIL on stale source; this must be rerun by Work on D5 HEAD.

## F2 — runnable *candidate* discovery, never dispatch authority

- **New single-entrypoint:** `program/kng/select_task.py --root .`. Reads CATALOG.yaml through PyYAML SafeLoader with duplicate-key rejection. Returns `CANDIDATES_ONLY_NOT_AUTHORIZATION` and a list of IDs/paths, not a request, job, task assignment, or ACK. **Not deployed** to any automatic dispatcher.
- Only an explicit YAML boolean `dispatch_eligible: true`, `type: task`, nonarchived `ready-for-dispatch-review` or `candidate-for-dispatch-review` and safe existing file path passes. Empty result is valid: no existing tasks need to be promoted merely to make the test green.
- Missing/unknown/`false` eligibility never yields candidates. Invalid YAML/schema, duplicate mapping keys/IDs/paths, wrong eligibility type, malformed unsafe or missing source path, conflict between archived status and `true` => **STOP, exit 2 and `candidates: []`**. Invalid inputs do not yield a partial candidate set. Symlink paths are resolved and constrained beneath root. The original archived PR31 task remains byte-exact, `dispatch_eligible: false`, unselected.
- Existing [program entry](../program/README.md), [operative candidate handoff protocol](../program/OPERATING_PROTOCOL.md), and [agent directory](../agents/README.md) now route manual Git candidate discovery through the selector and forbid bypass via raw `tasks/` glob or `type: task` scan. Only a **separate actual Director work order**, assignment permissions and real-chat Agent ACK may activate an executable task. No task owner is inferred from the output. The operative real dispatch integration is **NOT_DEPLOYED**; no active automated selector or service claimed.

## Actual A1 Linux execution (scoped, not independent reviewer QA)

Linux Python **3.13.5**, Git **2.47.3**, PyYAML **6.0.3**. Ran:

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s /mnt/data/kng_d5 -p test_select_task.py -q` → **15/15 PASS, exit 0**.

`python3 -m py_compile /mnt/data/kng_d5/select_task.py /mnt/data/kng_d5/test_select_task.py` → **PASS**.

Tests include one actual synthetic eligible task, exact historical archive negative, explicit false, missing eligibility, string/integer masquerading as YAML bool, archive with explicit true conflict, unsupported status, duplicate ID/path, missing/unsafe file, malformed YAML, duplicate YAML key, unsupported schema, empty-result success and read-only no-file-write check. CLI invalid => exit 2; CLI positive => exit 0. Test fixtures do **not** assert production dispatch or real Agent ACK.

**Still NOT_RUN in A1:** official `python3 -m unittest discover -s program/kng -p test_validate.py -q`, default Git provenance `validate.py --root . --json` and `derive.py --root .` on an actual complete checkout. GitHub connector confirms pin/blob and exact remote files but cannot replace a complete local Git graph. Work must verify those gates.

## Preserved evidence and measured reading delta

- No edits to `CATALOG.yaml`, its 130 original unique IDs or 130/130 existing targets, the seven PR31 restored source files except a navigational paragraph in `agents/README.md`, three historical PR31 byte-exact blobs, `program/current.json`, `derive.py`, D4 files/security/ACK or six source migrations; only migration result assertion, selector/tests, bounded protocol/readme/directory linking and author test fixture.
- **Q0 fixed Work full-file reading path:** PR42 source R `12/123589` B, G `13/126127` B, S `16/171865` B. `agents/README.md` gains **619 UTF-8 bytes** (4,604→5,223); unchanged nine other common files and frozen suffixes yield D5 R **12/124208 B**, G **13/126746 B**, S **16/172484 B**. `program/README.md` and `program/OPERATING_PROTOCOL.md` grew **399 B** and **1269 B** respectively, outside those three frozen common/suffix sets; task-specific new readers may incur extra reads. No claim of token or comprehension savings.
- No modification or automatic invocation of production/Ads/VPS/paid, no new PR or main merge, no claims of an operational task dispatch service. Existing Work D4 independent QA stands; only F1/F2 delta requires re-QA.

**AUTHOR VERDICT (conditional on final push/readback):** `KNG01_A1_PR42_D5_READY_FOR_TARGETED_REQA`; this means code/evidence ready for Work review, NOT final acceptance and NOT effective main. Independent Work must run full real checkout, official test suite, selector against actual CATALOG, stale-pin negative, archive exclusion, synthetic eligible positive and malformed/duplicate STOP before closing F1/F2. A0 retains merge authority.
