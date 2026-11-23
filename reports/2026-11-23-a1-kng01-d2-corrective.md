---
id: report-2026-11-23-a1-kng01-d2-corrective
type: report
owner: a1
status: author-d2-isolated-candidate-awaits-independent-work-qa
updated_at: 2026-11-23
sensitivity: public-redacted
---

# KNG-01 D2 — A1 corrective implementation and independent re-QA handoff

**TASK (unchanged):** `A1-KNG01-GIT-NORMALIZATION-D1` · **PHASE:** `D2-CORRECTIVE` · **ACK:** A1 ACKNOWLEDGED · **MODE:** Offline code + exclusive six-path branch integration · **NEXT_OWNER:** Chat Điều phối → Work targeted independent QA. This is an **author handoff only**, not owner acceptance.

## Authority / exact pins

- Main `e385c1bea2070973e3007e5717f7e980348d6ab3`; PR31 `a770de80a2467ca1789c820b63416209cf53b7d1`; PR39 `22d741e3f1dd325540932dea63c3a6da635113c3`; PR40 `68780956eab29581bd3dab5acc6924093c4019a7`; all verified unchanged before D2 branch creation.
- [Director exact D2 grant](https://github.com/DuyKienTTD/Hosting/pull/40#issuecomment-7098528192); [Work original QA finding](https://github.com/DuyKienTTD/Hosting/pull/40#issuecomment-7098400020); [Work Q0 frozen baseline](https://github.com/DuyKienTTD/Hosting/pull/39#issuecomment-7097774156). Main effective rules remain binding until an A0-approved main merge.
- Branch **`a1/kng01-shared-integration-d2-2026-11-23`** forked **exactly from PR40 HEAD**, not main or PR31, with six common paths integrated **on this branch only**. No PR31/39/40 branch modified, no force/merge/production/paid/Codex.

## FIX A — four original false accepts: fail closed

| Work reproducer: independent mutation | Expected | Author observed |
| --- | --- | --- |
| `current.json.work_ack=ACKNOWLEDGED` without task/owner/immutable receipt; Work D2 pending | reject `ACK_RECEIPT_MISMATCH` | PASS negative regression |
| `inventory.facts[0].source_sha` syntactically valid all-zero SHA | reject `SOURCE_PIN_MISMATCH` | PASS negative regression |
| `inventory.facts[1].recovery_ref=PR39@000…` | reject `SOURCE_PIN_MISMATCH` / `RECOVERY_REF_INVALID` | PASS negative regression |
| `migration.proposed_updates[0].base_blob` valid-looking but wrong | reject `MIGRATION_BLOB_MISMATCH` | PASS negative regression |

**Mechanism:** [`validate.py`](../program/kng/validate.py) checks a versioned [source pin lock](../program/kng/provenance-lock.json) with immutable `main/PR31/PR39` commits, exact `source_path`, `recovery_ref`, `Git blob SHA`, migration base commit/blob, and Work D2 ACK receipt consistency. Default `GitObjects.verify` resolves `commit^{commit}` → `commit:path` → `cat-file -t blob` locally. Missing local Git commits/trees cause explicit `PROVENANCE_UNVERIFIED` and nonzero exit; no fake successful status. Source and lock cannot simply mutate to the same nonexistent blob and pass a genuine Git-graph check. New guard rejects duplicate catalog IDs and integrated target blob drift.

**Actual author unit execution:** Linux CPython **3.13.5**, Git **2.47.3**; `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s program/kng -p test_validate.py -v` → **29/29 PASS**, 0 FAIL/ERROR, exit 0; Python `py_compile` PASS. Original 18 regression cases preserved; 11 new/expanded cases include four Work findings, missing lock/graph, pinned ref mutation, duplicate catalog ID, generated mirror idempotency, and **actual synthetic local Git commit/blob positive + negative**. These unit fixtures use minimal placeholder copies of unchanged main files, **not** a real Hosting full clone; no claim full-repository integrated CLI PASS.

**Separate real hosted source-object verification:** authenticated GitHub connector resolved original **12 inventory** `commit:path` plus **6 main migration base** paths, and all **18/18 observed Git blob SHAs matched** expected. This checks actual remote Git objects, but is **not** a full local `git fsck` or complete commit-tree checkout. Full Linux GitHub clone in this runtime fails DNS. Work with verified full checkout must run default CLI and reject any missing source/commit.

## FIX B — actual semantic shared-source integration (isolated branch, no main change)

- `README.md`: compact KNG-only entry, mandatory complete rules and concrete source links; remove duplicate quick-start security clause wording.
- `PROJECT.md`: retain actual long-term business objectives; current KNG execution priority explicit. Historical PR31 full business/infra status is accessible at its immutable PR31 blob, not repeated as live facts.
- `STATE.md`: replace roughly 35KB of mixed historic status with a **bounded current KNG checkpoint** and pinned links to full PR31 `STATE` blob `53d6d79aa6fd9a952ea6ceab8679104da77a597c` and main `c8e8941aa1418f70ed9542063f0485a129739d25`; preserve every historical item through unmodified immutable Git source, never delete original reports. Generated checkpoint block derives from `program/current.json` using [`derive.py`](../program/kng/derive.py).
- `AGENTS.md`: replace duplicated pre-KNG operative status/OPS chronology with concise current KNG assignment, mandatory full-read and STOP/ACK/security requirements. Full earlier PR31 AGENTS content remains at immutable blob `ecdb1fbaefd06448e3f7734c5eb2deea70a471d4`.
- `CATALOG.yaml`: preserve **all** PR31 existing stable document records and append **two unique KNG document entries** and typed entrypoint; no existing ID renamed/dropped. Generated report index markers enable `derive.py` to emit future WS02 accepted-report entry without manual re-copy, while current prior report statuses stay dated snapshots.
- `rules/AGENT_WORKFLOW.md`: start from complete PR31 source, keep all original §1–§12 controls, relabel previous assignments/priority sections as historical (not deleted) and add explicit bounded **§13 KNG-only precedence**, candidate-only current source ownership and limits. No full safety/STOP/cost/merge rule removed; PR31 original blob `3412e222364489e290be012f073f98f3ed77e3d3` linked.
- Candidate routers `program/README.md`, `program/KNOWLEDGE_OPTIMIZATION.md`, `program/OPERATING_PROTOCOL.md` updated to stop claiming shared edits merely preview-only; Hostinger/Work/A2/Coordinator roadmap headers explicitly distinguish hold and Work D2 QA pending; `program/current.json` supplies typed technical routing and WS02 historical ACK/acceptance slots.
- [Migration map](../program/kng/migration.json) binds each of six **actual output blob SHA IDs** to original main/PR31 base SHA and exclusive grant; [12-path PR31 reconciliation matrix](evidence/2026-11-23-a1-kng01-d2-pr31-reconciliation.json) marks **five shared PR31 paths used as source**, and **seven nonshared PR31 paths still untouched at PR31** for future coordinator integration, not silently overwritten. README source is main. No physical deletion, history rewrite or loss of 12 inventory IDs.
- Original WBS `32/32` IDs preserve **Gate, Deliverable, Required Skills, Owner, Dependencies, Acceptance** exactly against PR39 original Git blob `60beab3ad23abf7c67adf288dc0c213c14befcfe`, plus candidate current KNG route as seventh informational field. All non-KNG work remains held.

## FIX C — same Work Q0 input paths, measured before/after

Work frozen **9 common complete file reads / 139,996 UTF-8 bytes**, then fixed R/G/S suffix in exact Q0 order. Candidate D2 reads corresponding **9 full integrated files / 112,849 bytes**, **plus 1 full `program/current.json` / 2,751 bytes** to bind new authority, then **same exact suffix Git blobs**. No shortened section slices, tokenizer estimates or substituted candidate evidence.

| Q0 fixed task | BEFORE steps / bytes | Candidate AFTER steps / bytes | Byte delta | Author comprehension |
| --- | ---: | ---: | ---: | --- |
| R WS-04 read-only SEO backlog | 11 / 149,148 | **12 / 124,752** | −24,396 (−16.36%) | **NOT_SCORED** |
| G WS-01 Git/docs proposal | 12 / 151,686 | **13 / 127,290** | −24,396 (−16.08%) | **NOT_SCORED** |
| S WS-02 n8n readiness/production STOP | 15 / 197,424 | **16 / 173,028** | −24,396 (−12.36%) | **NOT_SCORED** |

Full source path/ref/blob/byte ledger and unchanged Q0 suffixes in [machine Q0 evidence](evidence/2026-11-23-a1-kng01-d2-q0-metrics.json). This **source byte improvement** is author measurement, not an independent 18/18 comprehension pass, not a change in effective main. Work must do a fresh blind 3×6 decision/rubric and 0 critical wrong-authority/STOP errors.

**Four Work Q0 identical semantic maintenance fixtures, proposed manual authoritative fields** (not elapsed effort or actual WS02 ACK):
- General technical + platform/API/VPS preferred routing: **3 files / 4 fields → 1 / 2** in `program/current.json. Historical roles in PR31 agents directory do not become active permission; coordinator integration of nonshared directory remains a gate.
- WS02 `PREPARED → ACK` with **real receipt**: **4 / 5 → 1 / 2**, typed WS02 status and receipt only; `derive.py` generates bounded STATE, task/CATALOG pre-KNG statuses remain immutable dated snapshots.
- WS02 new paper-exercise report review-ready (not live): **4 / 5 → 2 / 4**: new dated report disposition/evidence (2 fields), typed acceptance index review state/evidence ref (2 fields). STATE and CATALOG accepted-report index derived; no real report acceptance performed.
- Add public-Git secret handling clause affecting quick-start: **4 / 4 → 2 / 2**: operative `REPOSITORY_SECURITY.md` rule clause plus dated evidence/changelog event; README merely links full rule, CATALOG stable security ID/scope remains unless changed scope requires an additional field. This is a **hypothetical** change; security rule not modified.

See [machine Q0 evidence](evidence/2026-11-23-a1-kng01-d2-q0-metrics.json) for exact field maps and caveats; these are **modeled authorized manual edit targets** backed by actual deterministic derived-view script tested synthetically, NOT actual future multi-agent cost savings. Do not conflate generated status with authentic external ACK. Work must independently challenge every scenario.

## STOP / Author verdict

**Proposed author outcome:** `KNG01_A1_D2_READY_FOR_TARGETED_INDEPENDENT_REQA` **only after exact branch HEAD/13+ paths/diff and remote readback**; no self-approval or KNG accepted status. **Still NOT_RUN:** full default provenance CLI against complete Hosting Git commit graph in this Linux container (DNS), Work blind 18/18 and Work final D2 targeted QA; seven PR31 nonshared files are not integrated into this isolated candidate. The coordinator must reconcile final PR31 vs KNG integration, then obtain A0 merge authorization. The historical D1 misleading 7.1%/6.6%/4.5% proxy and 4/4/4/5 write model are **withdrawn** as noncomparable Q0 evidence.

**Protection:** source PR31/39/40 and main branches unchanged, no force push, no deployment/production/paid/Codex/secret changes. A GitHub comment is not a real Work session ACK. **NEXT_OWNER:** Chat Điều phối → Work targeted independent re-QA.
