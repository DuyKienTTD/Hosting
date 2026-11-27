---
id: hostinger-mig-hermes-s1-readiness-2026-11-23
type: migration-readiness-assessment
status: complete
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
task_id: MIG-HERMES/S1
source: pr11-execute-comment,remote-repo-snapshots,official-hostinger-docs,official-hermes-docs,previous-hostinger-evidence
---

# MIG-HERMES/S1 — Source/target identity, compatibility and non-destructive migration assessment

## 1. ACK thực thi

- **TASK:** `MIG-HERMES/S1`
- **ACK_EXECUTE:** `EXECUTE MIG-HERMES/S1`
- **Instruction source:** <https://github.com/DuyKienTTD/Hosting/pull/11#issuecomment-7090870590>
- **Base branch reviewed:** `origin/main@e385c1bea2070973e3007e5717f7e980348d6ab3`
- **Referenced acceptance source:** SEC-02/S1 report at commit `142f6dc5dbc033554bd0b43e3444ea0d59f60d96`
- **Agent executing this assessment:** Hermes WebUI
- **Owner in existing repo task:** `hostinger-agent`
- **NEXT_OWNER:** `chatgpt`
- **Mode actually used:** read-only + design/draft only
- **No side effects performed:** no archive download/open/import, no backup creation/renewal, no restore, no VPS change, no source shutdown, no secret readout, no production mutation.

## 2. Scope note and evidence boundary

Đặc tả gốc giao work package này cho **Hostinger Agent** với kỳ vọng có phép đọc control-plane trực tiếp. Trong phiên hiện tại, Hermes WebUI **không có** hPanel/Hostinger control-plane live read đã được xác minh, nên assessment này dùng:

1. **remote repo snapshots đã có sẵn**,
2. **báo cáo Hostinger Agent trước đó**,
3. **tài liệu chính thức Hostinger**,
4. **tài liệu chính thức Hermes Agent**.

Vì vậy, trường nào phụ thuộc **fresh control-plane read ngay trong phiên này** được đánh dấu `REPORTED` hoặc `UNKNOWN`, không thổi phồng thành `VERIFIED_LIVE`.

## 3. Sources actually reviewed

### Repo / branch snapshots

- `AGENTS.md`
- `PROJECT.md`
- `rules/AGENT_WORKFLOW.md`
- `rules/REPOSITORY_SECURITY.md`
- `STATE.md`
- `CATALOG.yaml`
- `agents/hermes.md`
- `agents/hostinger.md`
- `tasks/2026-11-23-ttdnew-hermes-vps-migration.md` via `origin/main`
- `reports/2026-11-23-ttdnew-hermes-vps-migration-status.md` via `origin/main`
- `reports/2026-11-23-hostinger-sec02-s1-hardening-assessment.md` via `origin/hostinger/sec02-s1-design-2026-11-23`
- `reports/2026-11-22-hostinger-ws02-infrastructure-baseline.md` via `origin/hostinger/ws02-infrastructure-baseline-2026-11-22`
- `reports/2026-11-21-ttdnew-resource-identity-verification.md` via `origin/main`

### Official docs reviewed

- Hostinger AI Automation Applications overview
- Hostinger Managed Hermes overview and setup
- Hostinger Managed Hermes dashboard management
- Hostinger Managed Hermes backups
- How to switch Hostinger AI Automation applications
- How to get started with Hermes Agent on Hostinger VPS
- Hermes Agent docs: `Backup & Transfer`
- Hermes Agent docs: `Import from Other Agents`

## 4. Objective and current decision posture

Mục tiêu của MIG-HERMES/S1 là tạo **migration readiness & data-preservation decision package** cho:

- **SOURCE:** `ttdnew.tech` / Hostinger AI automation app / runtime `u4s-hermes-agent`
- **DEST:** Hermes đang chạy trên VPS KVM2 resource `1722328`

mà **không** thực hiện migration thật.

### High-level decision now

**Current migration-readiness verdict:** `BLOCKED_COMPATIBILITY`

Lý do chính:

1. Có bằng chứng chắc rằng **source và dest là hai runtime độc lập**.
2. Có metadata backup/report đủ để đánh giá rủi ro freshness.
3. Nhưng **không có đường import tương thích được tài liệu hóa chính thức** từ Managed Hermes backup sang self-hosted Hermes trên VPS hiện có.
4. Hostinger docs còn nêu rõ: **switch sang VPS không chuyển dữ liệu Managed Hermes**.
5. Hermes docs về `hermes import` áp dụng cho **Hermes-created backup zip** hoặc import từ các agent khác, không xác nhận dùng được cho Hostinger Managed Hermes backup download.

Vì vậy assessment package này có thể hoàn thành và sẵn sàng review, nhưng migration execution **không** được coi là ready.

## 5. SOURCE vs DEST identity & inventory

| Field | SOURCE | DEST |
|---|---|---|
| Runtime role | Managed Hermes / AI automation app | Self-hosted Hermes on VPS |
| Product class | Hostinger AI Automation application (U4S / dedicated Docker container) | Hostinger VPS KVM2 + Docker Manager catalog/project |
| Resource identifier | `SOURCE_APP_UUID_REDACTED`; domain `ttdnew.tech` | VPS resource `1722328`; Docker project `hermes-agent-l7fe` |
| Runtime label | `u4s-hermes-agent` | Hermes container image on VPS |
| Metadata plan label | `OpenClaw` label observed but **not** runtime truth | Hermes VPS deployment |
| Region / location | `UNKNOWN_IN_THIS_SESSION`; prior report confirms separate U4S resource | Kuala Lumpur per VPS inventory/reporting |
| Hermes version | `REPORTED`: `v0.22.5-2`, target upgrade `v0.23.2-1` in prior identity report | `REPORTED`: Hermes `0.22.5` on KVM2 from prior audit/state |
| Access plane | Hostinger dashboard Managed Hermes app | VPS/Docker Manager / SSH / Docker metadata on KVM2 |
| Storage / data boundary | isolated managed app container boundary | VPS-local Docker/project boundary |
| Backup authority | Managed Hermes Backups page in Hostinger dashboard | Hostinger VPS scheduled backups |
| Last verified UTC from available evidence | resource identity report dated 2026-11-21; migration status report dated 2026-11-23 | INF-01/SEC-02 evidence on 2026-11-23 UTC |
| Evidence path | `reports/2026-11-21-ttdnew-resource-identity-verification.md`, `reports/2026-11-23-ttdnew-hermes-vps-migration-status.md` | `reports/2026-11-22-hostinger-ws02-infrastructure-baseline.md`, `reports/2026-11-23-hostinger-sec02-s1-hardening-assessment.md` |

### Identity conclusion

`SOURCE != DEST` ở cả product class, lifecycle, backup authority và operational boundary. Không có bằng chứng chúng dùng chung container, volume, state store, credential set hoặc conversation history.

## 6. Archive validity and freshness

### Source backup, from existing repo evidence

- **Backup timestamp:** `2026-11-22 05:22:45 UTC`
- **Approx size:** `1233 MB`
- **Entries:** `12743`
- **Temporary link expiry:** `2026-11-30 02:07:28 UTC`

### Important limits on those numbers

Các số trên chỉ là:

- **reported metadata** từ report migration status hiện có,
- **không phải** bằng chứng rằng archive chứa đầy đủ mọi loại dữ liệu người dùng,
- **không phải** bằng chứng rằng archive tương thích với đích,
- **không phải** bằng chứng rằng source changes sau thời điểm backup đã được giữ lại.

### Destination backup freshness

- VPS backup schedule đã được report là **weekly**.
- Latest listed completed backup trong INF-01: `2026-11-16 09:23:43 UTC`.
- Điều này tạo gap rõ ràng: backup đích cũ hơn source migration-status snapshot và không được chứng minh đủ mới cho bất kỳ import thử nào.

### Freshness risk statement

Ngay cả khi import path tồn tại, source backup hiện hữu **có thể bỏ sót** các thay đổi sau `2026-11-22 05:22:45 UTC`, còn destination backup hiện tại **không đủ chứng minh** rollback safety cho một bài import thử vào runtime đang sống.

## 7. Compatibility & import path feasibility

## 7.1 What Hostinger docs explicitly document

### Managed Hermes backups

Hostinger docs cho Managed Hermes mô tả:

- backup tự động hàng ngày,
- có thể **restore**, **download**, xem restore history,
- restoring **replaces all current application files**,
- restore không undo được,
- delete/re-setup là cách khởi tạo app mới.

### Managed Hermes to VPS switch

Hostinger docs cũng nói rõ:

- switch sang VPS là **subscription change**, không phải data migration,
- current Managed Hermes setup and data **don’t move** to the VPS,
- có thể mất memory, agents, configs, conversation history,
- không có automatic way to return.

### AI Automation app switching

Hostinger docs cho switching giữa AI Automation apps nêu flow là:

1. delete current application,
2. setup new application.

Docs **không** mô tả một import bridge từ Managed Hermes backup sang một Hermes VPS có sẵn.

## 7.2 What Hermes docs explicitly document

### Hermes backup/import

Hermes docs `Backup & Transfer` nêu:

- `hermes backup` tạo zip toàn bộ Hermes home,
- zip đó có thể restore bằng `hermes import <zip>`,
- backup kiểu này bao gồm profiles, memory, conversations, scheduled jobs, settings, `.env`, `auth.json`.

### Hermes imports from other agents

Hermes docs `Import from Other Agents` mô tả import từ:

- OpenClaw
- Claude Code
- Codex CLI
- Cursor
- Grok Bot
- OpenBot

Managed Hermes backup download của Hostinger **không** được nêu là supported import source trong docs này.

## 7.3 Compatibility conclusion

Từ các docs đã kiểm:

- **DOCUMENTED:** Managed Hermes có backup download/restore **trong chính môi trường Managed Hermes**.
- **DOCUMENTED:** self-hosted Hermes có `hermes backup` / `hermes import` cho **Hermes backup zip**.
- **DOCUMENTED:** switch Managed Hermes → VPS **không chuyển dữ liệu**.
- **UNKNOWN / NOT DOCUMENTED:** backup download từ Managed Hermes có cùng format/semantic với zip do `hermes backup` tạo hay không.
- **UNKNOWN / NOT DOCUMENTED:** có import tool chính thức để inject Managed Hermes backup vào một Hermes đang chạy trên VPS hiện có hay không.

=> **Readiness decision for compatibility:** `BLOCKED_COMPATIBILITY`.

## 8. Collision & preservation options

## Option A — Preserve destination, then selectively import after isolated test

**Description:** giữ nguyên KVM2 runtime hiện tại; chỉ sau khi có isolated test target và verified import semantics mới cân nhắc selective import/reconcile.

- **Pros:** bảo toàn đích tốt nhất; ít rủi ro overwrite dữ liệu hiện có.
- **Cons:** hiện chưa có documented selective import path.
- **Data-loss boundary:** thấp trên dest, nhưng source-to-dest coverage chưa biết.
- **Identifier collision risk:** cao nếu archive/import tái tạo cùng profile names, auth files, conversations, schedule IDs.
- **Version compatibility:** unknown.
- **Secret handling:** high risk nếu archive chứa `.env`/auth state mà không có scoped import rules.
- **Permission need:** cần isolated test runtime, explicit owner approval, backup mới cho cả hai bên.
- **Rollback path:** restore isolated target; dest production untouched.
- **Downtime/cost:** thấp cho production nếu thật sự test cô lập; có thể cần extra infra.
- **Decision now:** **not executable yet** do compatibility blocker.

## Option B — Separate namespace / parallel instance, then reconcile

**Description:** dựng một Hermes đích riêng biệt/cô lập để test import/archive behavior, không đụng KVM2 Hermes hiện có; sau đó mới quyết định manual reconciliation hay cutover.

- **Pros:** an toàn nhất cho dữ liệu đích hiện tại.
- **Cons:** đòi isolated runtime, extra setup, và vẫn bị compatibility blocker nếu archive không có import path.
- **Data-loss boundary:** thấp nhất cho production dest.
- **Identifier collision risk:** trung bình, vì namespace có thể tách ở level instance; nhưng reconciliation logic vẫn unknown.
- **Version compatibility:** vẫn unknown.
- **Secret handling:** tốt hơn vì secrets có thể không nhập hoặc giữ tách biệt trong test lane.
- **Permission need:** separate runtime approval, fresh backup, cleanup plan, cost owner.
- **Rollback path:** destroy isolated test lane only.
- **Downtime/cost:** downtime production gần 0; cost/ops overhead cao hơn.
- **Decision now:** **recommended future test shape**, nhưng vẫn **not ready** vì compatibility unknown.

## Option C — Replacement of destination runtime

**Description:** dùng source backup/data để thay thế runtime Hermes trên KVM2.

- **Pros:** operationally simple only if import path were officially supported.
- **Cons:** rủi ro mất dữ liệu đích rất cao.
- **Data-loss boundary:** rất cao; có thể overwrite memory, conversations, settings, credentials, schedule state.
- **Identifier collision risk:** tối đa.
- **Version compatibility:** unknown.
- **Secret handling:** high-risk.
- **Permission need:** explicit owner decision + verified rollback + fresh dual backups + downtime approval.
- **Rollback path:** phụ thuộc hoàn toàn vào backup đích đủ mới và restore đã được chứng minh; hiện chưa có.
- **Downtime/cost:** cao nhất.
- **Decision now:** **NOT RECOMMENDED**.

## 9. Recovery / rollback acceptance design

### Minimum future prerequisites before any authorized execution stage

1. **Fresh source backup** with independently verified timestamp and ownership.
2. **Fresh destination backup** with independently verified timestamp and ability to restore into isolation.
3. **Manifest before import** describing what counts are expected to be preserved/reviewed:
   - profiles
   - memory stores
   - conversations/session DB
   - skills
   - scheduled jobs
   - settings/config
   - provider credentials / tokens / connector state
4. **Isolated target** that is not the current KVM2 production Hermes.
5. **Version comparison** between source and intended import target.
6. **Collision policy** explicitly chosen by owner: preserve / map / replace / skip.
7. **No-delete rule** for source until verification completes and owner approves disposal.
8. **Rollback evidence plan** proving restore can happen without touching wrong runtime.

### Recovery acceptance tests for a future authorized stage

- verify source identity before touching backup,
- verify dest identity before touching runtime,
- import only into isolated target,
- compare pre/post manifest counts and metadata,
- confirm no unintended overwrite of preexisting dest state,
- verify secrets are not exposed in logs/report,
- stop immediately on resource mismatch,
- keep source running and unchanged,
- only after owner review decide whether any data should move beyond test lane.

### RPO / RTO

- **RPO:** `UNKNOWN` until owner sets policy and fresh backups are verified.
- **RTO:** `UNKNOWN` until restore/import method is proven in isolation.

## 10. Tabletop-only scenarios

## Scenario 1 — Stale source backup after last meaningful updates

- **Expected safe decision:** STOP / no-change.
- **Observed decision from current evidence:** source backup is known to exclude changes after `2026-11-22 05:22:45 UTC`; therefore any execution using this archive without owner refresh decision must stop.
- **Result:** `PASS_STOP`

## Scenario 2 — Target identifier collision / overwrite risk

- **Expected safe decision:** choose preserve-first or separate-namespace path; do not import into live dest.
- **Observed decision from current evidence:** KVM2 Hermes already exists and has its own state boundary; collision policy is not approved; replacement path is not acceptable.
- **Result:** `PASS_STOP`

## Scenario 3 — Failed isolated import and rollback needed

- **Expected safe decision:** rollback only inside isolated target; no production dest mutation.
- **Observed decision from current evidence:** rollback design is possible only if isolated target and fresh dual backups are created in a future approved stage; absent that, no import should start.
- **Result:** `PASS_STOP`

## 11. Readiness decision table

| item | source UTC | observed | expected | class | risk | required approval | next owner |
|---|---|---|---|---|---|---|---|
| Source identity | 2026-11-21 / 2026-11-23 reports | `ttdnew.tech` is Managed Hermes `u4s-hermes-agent` on separate AI automation runtime | exact source identity must be explicit before migration | `VERIFIED/REPORTED` | wrong-target action | no write approval; identity preflight mandatory | chatgpt |
| Destination identity | 2026-11-23 INF-01/SEC-02 evidence | KVM2 `1722328` hosts separate Hermes Docker project | explicit dest identity before any test | `VERIFIED/REPORTED` | wrong-target action | no write approval; identity preflight mandatory | chatgpt |
| Source backup freshness | source status report 2026-11-23 | snapshot known, but may omit later changes | fresh-enough source backup for migration window | `REPORTED` | stale data | owner approval for backup refresh in separate task | chatgpt |
| Destination backup recency | INF-01 2026-11-23 | latest listed backup `2026-11-16 UTC` only | fresh restore point before any test | `REPORTED` | rollback failure | owner approval for fresh backup/restore design | chatgpt |
| Managed → VPS import path | docs checked 2026-11-23 | no official import path found; Hostinger says switch to VPS does not move data | documented compatible import path | `UNKNOWN / DOCUMENTED_BLOCKER` | data loss / false migration assumption | vendor-confirmed method or safe isolated test design | chatgpt |
| Archive content semantics | 2026-11-23 status report + docs | size/entry count known; content types not verified | known archive scope and mapping | `UNKNOWN` | hidden omissions / incompatible data | archive inspection only in future approved stage | chatgpt |
| Collision policy | current reports | not decided | explicit preserve/parallel/replace policy | `UNKNOWN` | overwrite of dest state | explicit owner decision | chatgpt |
| Isolated test feasibility | docs + prior reports | designable, but not verified live in this session | isolated target available before any import | `UNKNOWN` | accidental production touch | explicit infrastructure approval | chatgpt |
| Rollback readiness | docs + prior reports | concept only; no restore proof | tested restore into isolation | `UNKNOWN` | irreversible failure | restore-test approval in separate task | chatgpt |

## 12. Final assessment

### Delivery verdict

`MIG_HERMES_S1_ASSESSMENT_READY_FOR_REVIEW`

### Migration readiness verdict

`BLOCKED_COMPATIBILITY`

### Why both statements are true

- The **assessment package itself** is complete enough to review: identities, backup metadata, compatibility blockers, collision options, rollback gates and tabletop outcomes are all documented.
- The **migration itself** is not ready: the import path between Managed Hermes backup and the current Hermes on VPS remains undocumented/unverified.

## 13. Blockers

1. No official documented import path from Managed Hermes backup into existing self-hosted Hermes on VPS was found.
2. Hostinger docs explicitly say switching to VPS does **not** transfer Managed Hermes data.
3. Source archive contents/types remain unverified because archive inspection is out of scope.
4. Destination rollback point is not fresh enough to claim safe execution readiness.
5. Control-plane live revalidation of backup availability/timestamps was not available in this Hermes session.

## 14. Handoff line

`TASK=MIG-HERMES/S1 | AGENT=Hermes WebUI | BASE_SHA=e385c1bea2070973e3007e5717f7e980348d6ab3 | ACK_EXECUTE=EXECUTE MIG-HERMES/S1 | EXPECTED=source-target identity, backup/compatibility/collision and rollback readiness package without touching data | OBSERVED=source and destination are separate runtimes; source backup metadata exists; destination backup is older; official docs do not document a Managed-Hermes-backup to VPS-Hermes import path; Hostinger says VPS switch does not transfer data | SOURCES=repo snapshots + Hostinger Managed Hermes docs + Hermes docs | TABLETOP=3 safe-stop scenarios PASS | EVIDENCE=reports/evidence/2026-11-23-hostinger-mig-hermes-s1-readiness.json | VERDICT=BLOCKED_COMPATIBILITY with assessment package ready for review | BLOCKERS=compatibility path undocumented, archive contents unverified, dest backup recency insufficient, no live control-plane recheck in this session | NEXT_OWNER=chatgpt`
