---
id: ttd-a1-gov02-qa01-validator-delta-2026-11-23
type: report
status: review_pending
updated_at: 2026-11-23
owner: a1
sensitivity: public
---

# A1-GOV02-QA01 — Cross-package document-ID validator delta

**Owner:** A1 (ChatGPT Standard) · **Mode:** EXECUTE safe offline fixture/code delta · **Next owner:** ChatGPT Điều phối → Work independent QA.

**Baseline/source:** PR #28 HEAD `6dafae50bd17bc1a18080b13b86c5b8c35573580`; main/rules `e385c1bea2070973e3007e5717f7e980348d6ab3`; PR #31 unmerged `f03dc7e8d9cd88f425b1f04ac7908a3de5d64060`. Work finding: PR #28 comment #7092060267. The baseline validator/test blobs were verified byte-for-byte against GitHub Git blob IDs `61494de3a5b4909a10a3ed46a02bf49b86129db9` / `6c2be47ac3bd7e726f20680717d223da9ca1243f`.

## Scope and implementation

**WRITE_SET:** `sandbox/repo-metadata-validator/validate.py`, `sandbox/repo-metadata-validator/test_validate.py`, this report, and the corresponding JSON evidence. **DO_NOT_TOUCH:** PR #28 branch, PR #30, main, STATE, CATALOG, CHANGELOG, production, paid APIs, GitHub Actions, merge.

The original `seen_ids` was reset per package. Added repository-audit-scoped `document_id_paths[id]` as a set of paths observed across all valid, readable package artifacts. Emit one `DUPLICATE_DOCUMENT_ID` review finding when one frontmatter ID maps to two or more *distinct* paths. The path set deduplicates sightings of the same path in different snapshots. Keep the previous within-package `DOCUMENT_ID_REUSED` diagnostic unchanged, and do not change task-ID, catalog-ID, blob/source SHA or approval logic. A within-package duplicate can produce both existing and new diagnostics; the new diagnostic is one finding per ID.

## Actual tests, expected vs observed

**Environment:** local Linux, CPython 3.13.5, Git 2.47.3. Network clone was unavailable (DNS); original exact source/test blobs were reconstructed locally and verified by Git object SHA before running synthetic *local Git* fixtures. GitHub connector used only to read/write repository objects and branch; no clone of the full 12-source corpus was possible.

**Before fix:** `python3 -m unittest -v test_validate.ValidatorTests.test_cross_package_document_id_collision` — expected 1 `DUPLICATE_DOCUMENT_ID`, observed 0; test FAILED with `AssertionError: 0 != 1` (exit 1).

**After fix:** targeted `python3 -m unittest -v` for four new tests plus the existing missing-source, SHA-drift and positive fixture tests — **7 run, 7 passed, exit 0** (0.617 seconds). `python3 -m py_compile validate.py test_validate.py` passed. Whitespace and added-line secret scan passed.

| Scenario | Expected | Observed |
| --- | --- | --- |
| Distinct package report paths with identical frontmatter report ID | `DUPLICATE_DOCUMENT_ID` once, severity `finding` | PASS; ID `report-sample`, both paths reported |
| Identical report path across different pinned snapshots | No false document collision | PASS; no document collision |
| Distinct report IDs | No duplicate finding | PASS |
| Duplicate task/report ID within one package | Preserve `DOCUMENT_ID_REUSED`; add scoped global finding | PASS |
| Missing report/evidence and missing referenced source | Existing missing diagnostics | PASS |
| Incorrect source tree/blob SHA and unavailable commit | Existing SHA/SOURCE diagnostics | PASS |
| Valid synthetic fixture | No findings, 3 sources, 3 artifacts | PASS |

**New source blobs:** validator `7fd6579cf3081385251ff1906177284c274d83e9`, tests `8efc3966134b2c88030b714fda4a718b624ee939`. Full historical corpus audit, historical 7/7 author suite and independent Work acceptance were **NOT_RUN**; original historical source findings and approvals remain unchanged.

**Verdict:** `A1_GOV02_QA01_SOURCE_AND_TARGETED_TESTS_PASS` — author-executed targeted tests only. **Acceptance gate:** other reviewer (prefer Work) must independently test the A1 code and assess stacked PR. No merge or production authority granted.

**Next owner:** ChatGPT Điều phối to dispatch independent Work QA.