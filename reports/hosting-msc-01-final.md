---
id: hosting-msc-01-final-work
type: report
status: ready-for-independent-review
owner: ChatGPT Work
task_id: HOSTING-MSC-01
lifecycle: DURABLE
updated_at: 2026-11-25
sensitivity: public
---
# HOSTING-MSC-01 — Work implementation handoff

TASK_ACKNOWLEDGED in the Work session. [Exact work order](https://github.com/DuyKienTTD/Hosting/blob/5ec9663b6ac72335952033ce4e5b11d71290a0cf/tasks/2026-11-24-hosting-msc-01.md). Baseline main c15ab834ae841e274c7e8dd8e17ecb6849b00365, tree 31565f5b4c861d982822baf11af81d3a52952b7c. Candidate SHA and tree are recorded in the PR, since a tracked report cannot include its own containing commit digest. MSC-08 remains independent; this is Work self-evidence.

## Cold-start measurement

Compare the same synthetic task envelope for each role with the baseline/current read rules. Count each unique complete UTF-8 blob once via byte length, excluding conditional docs and the lookup index. Baseline common = AGENTS 2,218 + workflow 15,440 + security 1,310 + STATE 4,512 = 23,480 bytes, plus one role profile. Candidate common = AGENTS 4,296 plus the corresponding role profile. Baseline five governance documents, candidate two. The unchanged task is the separate third group after migration. To show task-inclusive arithmetic consistently, add the same 12,547-byte exact MSC envelope as a workload proxy to both sides; it grants no authority to roles other than Work.

| Role | Profile | Governance old → new | Reduction | With unchanged task proxy |
|---|---|---:|---:|---:|
| A1 | agents/a1.md | 32039 → 4980 | 84.46% | 44586 → 17527 |
| A2, A0, Trợ lý A0, Điều phối, Work (each) | agents/chatgpt.md | 28423 → 5284 | 81.41% | 40970 → 17831 |
| Codex | agents/codex.md | 31344 → 5009 | 84.02% | 43891 → 17556 |
| Hermes | agents/hermes.md | 28454 → 4950 | 82.60% | 41001 → 17497 |
| Hostinger | agents/hostinger.md | 33307 → 4979 | 85.05% | 45854 → 17526 |
| n8n execution component (conservative profile comparison) | agents/n8n.md | 25165 → 4901 | 80.52% | 37712 → 17448 |

Reduction = 100 × (before − after) / before. These are initial governance bytes, not whole-task reads or measured token/cost reductions. Triggered policy is additive per scenario. Warm reuse can avoid retransmission of verified unchanged policy; the live authority and state checks still run. No quantified warm savings.

## Preservation map

| Baseline source | Candidate canonical location and trigger |
|---|---|
| AGENTS initial and scope; workflow §§1–3 | AGENTS initial groups, capability preflight, scope and truth of ACK. Workflow §§2–3 remains detailed for routing, one writer, rights and handoff. |
| Workflow §§2,4–5 and STATE release snapshot | AGENTS preflight, risk, STOP/HOLD and safe continuation. Workflow + STATE + applicable authority and KNG release gate on routing/risk, with exact SHA/tree/ordered parents/live readback. |
| Workflow §§5–7; CONTRIBUTING | AGENTS diff, validation, write lease, honest evidence and author-different review. Workflow and CONTRIBUTING triggered for detailed review/Git actions. |
| Security | AGENTS no secret/PII/dumps/IP disclosure and rotate response. Full security on Git writes, credential or sensitive work. |
| Lifecycle §§1–7; workflow §8 | Lifecycle and authorized reference sources triggered for management of data, preserves retention/approval, dedup, canonical authority, impact checks and no automated deletion. |
| Role profiles and capability directory | Role-specific condensed profiles, full old version pinned per role. Historical capabilities preserved in Git, live capability verified per task. |
| Operating protocol, STATE, README, KNG current.json and validator | Entrypoints direct to AGENTS. KNG snapshot and provenance checks preserved byte-for-byte. Program README explicitly separates historical must_read from current MSC policy and preserves cross-branch Zalo task authority. |
| CATALOG/partitions | Existing canonical shared registry and complete partition equality retained; no task/report/evidence indexing. |

## Synthetic decision walkthroughs

Work applied the initial trio to each case and opened the indicated policy as a triggered source. These are manual case executions with no external side effects and no independent behavioral guarantee.

| Input / trigger | Expected and observed decision |
|---|---|
| Work, current scoped work order, available read-only local clone | Proceed to read/measure and collect evidence. No production action. PASS. |
| A1, valid sole-writer branch task / workflow, security and contributing | Permit only scoped branch write after preflight. A missing write grant denies same action. PASS. |
| Hostinger PAUSED / state and authority | Deny VPS action; allow scoped offline documentation if separately authorized. PASS. |
| Reporter notices credential-bearing log / security | Do not include log. Pause exposure, route redaction/rotation and continue safe calculation. PASS. |
| Work author asked to accept own delta / workflow | Self-test allowed. Independent acceptance routed to different reviewer. PASS. |
| Scoped data edit and subsequent merge request / lifecycle, workflow, Git | Data edits within assigned write-set may proceed. Merge held absent MSC-08 and applicable authority even if tests are green. PASS. |
| Same accessible, complete blob with matching role, task and authority | Reuse content after ref check; reload changed blob or invalidated scope. Missing authority or expired live state blocks dependent effect. PASS. |
| Partial document or superseding STOP / applicable source and state | Recover contiguous same-blob ranges or hold. Revalidate live STOP immediately before risk; continue independent safe work. PASS. |

## Execution evidence and handoff

Full-history local clone, Python 3.12.14, Git 2.56.1, no paid AI/new infrastructure. Run KNG unittest, integrity unittest, provenance validator, derive, catalog partition validator, trusted-base repository delta and git diff check. Legacy PowerShell runner unavailable here; Python integrity covers changed scope, not full equivalence. PR links exact final CI evidence and reviewer handoff. No production, agent activation, protected deletion or task-authority changes. NEXT_OWNER Chat Điều phối and Trợ lý A0 for MSC-08. Final activation and main verification depend on independent acceptance, exact merge authority and successful verified postmerge CI.
