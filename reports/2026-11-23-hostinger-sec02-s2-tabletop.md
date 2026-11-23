---
id: sec02-s2-tabletop-2026-11-23
type: report
status: draft-ready-for-owner-review
updated_at: 2026-11-23
sensitivity: public-redacted
task_id: SEC-02/S2
owner: hostinger-agent
executed_by: hermes-webui
next_owner: chatgpt
---

# SEC-02/S2 — kế hoạch hardening có gate và diễn tập quyết định giả

## ACK và nguồn
- [Lệnh PR #11 comment 7091865470](https://github.com/DuyKienTTD/Hosting/pull/11#issuecomment-7091865470). **Executor thực tế:** Hermes WebUI soạn tài liệu/test offline; Hostinger Agent là owner nêu trong chỉ thị nhưng chưa ACK trong phiên này. Không có bằng chứng Hostinger live mới; không mạo nhận Hostinger execution. `origin/main=e385c1bea2070973e3007e5717f7e980348d6ab3`.
- Rule blobs: AGENTS `cb6a8af9`, WORKFLOW `69ec0db9`, SECURITY `c24d6080`, STATE `c8e8941a`, CATALOG `719c9c5d`, Hostinger profile `15cade1f`. Main workflow hiện chỉ §§1–7; đây là rule hiện hành của base.
- Nguồn ghim SHA: SEC S1 PR #11 `142f6dc5`, INF-01 PR #9 `486afc2`, INF-01B PR #17 `5c9d183`, Work WS-02 PR #8 `18e41d1`, OPS S1 PR #22 `7f18955`, OPS S2 PR #24 `d981c81`, roadmap PR #6 `03fb56b` (full SHA trong JSON). Đây là snapshot historical trên branch/PR, không phải kiểm tra live mới.
- **Write-set:** task, runbook, report, JSON evidence, validator offline. **Not touched:** main, SEC S1, INF, OPS, STATE/CATALOG/CHANGELOG, VPS, hPanel, Docker, firewall, SSH/TLS/port, secret/credential, backup/restore và provider. Không có production change, PR merge hay chi phí.

## F01–F07 — truy vết nguyên trạng mức độ và nguồn S1
Severity/status/provenance được giữ **nguyên văn** từ bảng SEC-02/S1; không chứng nhận rằng snapshot vẫn đúng hôm nay. Mỗi dòng JSON còn có risk-of-change, prerequisite S1, authorized read-only verification proposed, change window, backup/rollback, lockout hazard, hard STOP, owner/reviewer, A0 gate và postflight.
| Finding | Severity S1 | Status S1 | Asset và đích đề xuất | Owner/reviewer S1; approval |
|---|---|---|---|---|
| `SEC02-F01` | HIGH if public RDP is not required; possible management exposure. No evidence of compromise. | VERIFIED exposure; `REACHABLE_EXTERNALLY` UNKNOWN | KVM2 management/RDP; Only approved management sources can reach management plane | Hostinger/platform owner; reviewer ChatGPT + independent security reviewer; Separate approval for firewall/UFW change.; A0 required |
| `SEC02-F02` | MEDIUM/HIGH depending on intended exposure; unnecessary allow rules increase attack surface. | `UFW_ALLOWED` verified; `LISTENING` varies by port; `REACHABLE_EXTERNALLY` UNKNOWN | KVM2 8501 and Docker published service ports; Unused port exposure narrowed only after consumer validation | Service owner; reviewer Hostinger Agent + ChatGPT; Separate exposure-change approval.; A0 required |
| `SEC02-F03` | HIGH availability risk for P0 workflow; not proof of OOM or compromise. | VERIFIED exit state; cause `UNKNOWN` | KVM2 P0 reasoner; Cause of exit 137 established by authorized limited metadata; no speculative restart | Codex/runtime owner; reviewer ChatGPT; Separate runtime-engineering approval; no action from design PASS.; A0 required |
| `SEC02-F04` | MEDIUM/HIGH if this VPS owns an HTTPS endpoint; service impact or false alarm possible. | Local listener `VERIFIED_ABSENT` at snapshot; TLS ownership and external reachability `UNKNOWN`. | TLS endpoint owner (not verified); TLS terminator and SNI ownership verified before any change | Owner of endpoint; reviewer independent security reviewer; Separate TLS/reverse-proxy approval.; A0 required |
| `SEC02-F05` | HIGH data-recovery uncertainty, but backup existence is not evidence of recoverability. | Backup metadata `VERIFIED`; restore capability `UNKNOWN`. | KVM2 backups and isolated restore target; Independent isolated restore proof within A0 RPO/RTO | Platform owner; reviewer ChatGPT + recovery reviewer; Separate restore-test approval.; A0 required |
| `SEC02-F06` | HIGH confidentiality risk; possible credential exposure. Do not label P0 without compromise evidence. | `VERIFIED_FIELD_EXPOSURE`; compromise `UNKNOWN`. | credential consumer scope (value never handled); Consumers mapped and rotation/cutover scoped without raw secret in Git | Credential owner; reviewer independent security reviewer; Separate credential-rotation approval; not performed by S1.; A0 required |
| `SEC02-F07` | MEDIUM operational risk if actions or backups are applied to the wrong runtime. | VERIFIED separation. | KVM2 versus separate managed app identity; Exact runtime/resource/backup identity checked per change | ChatGPT coordinator; reviewer Hostinger Agent; Mandatory preflight, no extra approval for read-only identity check.; A0 required |

### Ranh giới theo finding
- F01/F02: snapshot UFW cho phép RDP 3389/8501; Docker publish 32768/32770. **Internet reachability chưa được đo**, 8501 listener chưa thấy trong snapshot. Trước khi thu hẹp: kiểm mục đích dịch vụ và nguồn quản trị được duyệt, alternate access + console độc lập, rollback rule và health; không đóng đường hiện tại theo suy đoán.
- F03: reasoner exit 137, `OOMKilled=false` và unhealthy theo S1; không chứng minh OOM, nguyên nhân khác hoặc trạng thái hiện tại. Chỉ metadata non-secret theo allow-list khi một owner thực thụ thực hiện sau.
- F04: snapshot thiếu local listener 443 không chứng minh VPS sở hữu TLS; DNS/SNI/terminator và reachability là `UNKNOWN`. Không tự đổi cert/reverse proxy.
- F05: thấy lịch và bản backup hoàn tất cũ, **restore chưa thử**; RPO/RTO, isolation và khả năng khôi phục vẫn UNKNOWN. Không đưa backup vào fixture S2.
- F06: S1 báo Docker metadata có credential field dạng plaintext đã redacted; compromise/consumer scope UNKNOWN; không truy vấn lại giá trị, không để lộ trong evidence.
- F07: KVM2 khác managed Hermes resource; mọi work order bắt buộc xác minh alias/owner/backup scope trước khi cân nhắc thay đổi.

## Đề xuất thứ tự và phân quyền
- Năm work order tách biệt trong [runbook](../runbooks/sec02-s2-controlled-hardening-gates.md): WO-ACCESS, WO-CREDENTIAL, WO-RESTORE, WO-P0, WO-TLS. **Tất cả `NOT_AUTHORIZED`**, rollback `PROPOSED_NOT_TESTED`, restore proof `UNKNOWN`. Một approval không cấp quyền cho các control khác.
- DAG bất biến: `IDENTITY_VERIFIED -> BACKUP_RECOVERY_PLAN -> ALTERNATE_ADMIN_ACCESS_CONFIRMED -> CHANGE_APPROVAL -> SINGLE_CONTROL_CHANGE -> HEALTH_CHECK -> ROLLBACK_DECISION`. Đây là gate cho giai đoạn tương lai; không chạy `SINGLE_CONTROL_CHANGE` trong S2.
- Threat/fail-stop: loss SSH/RDP hoặc console, n8n outage, TLS break, leaked credential value, resource/rollback owner ambiguity đều dừng và escalates tới owner; không self-heal/retry/destruct. Dashboard HTTP 200 không chứng minh inference health.

## 10 tình huống quyết định synthetic đã chạy
- Runner: `python3 -B sandbox/sec02-hardening-fixtures/validate.py` (Python stdlib, local worktree). Dữ liệu flags trong JSON hoàn toàn giả. `PASS_OFFLINE_ONLY` là kết quả hàm quyết định thuần; **không phải** diễn tập firewall/SSH/TLS/restore thật, không có lệnh privileged. `T10` với toàn bộ giả định đều đủ vẫn chỉ `HOLD_FOR_SEPARATE_CHANGE_WINDOW`, không sinh approval.
| Case | Input giả | Expected | Observed |
|---|---|---|---|
| `T01` | no backup restore proof; signal: restore_proof_required_and_missing, two_person_review | `STOP_RECOVERY_UNPROVEN` | `STOP_RECOVERY_UNPROVEN` |
| `T02` | privileged command blocked by allow-list; signal: privileged_command_blocked, two_person_review | `STOP_NO_BYPASS` | `STOP_NO_BYPASS` |
| `T03` | credential value unexpectedly visible; signal: secret_value_seen, two_person_review | `STOP_REDACT_ESCALATE` | `STOP_REDACT_ESCALATE` |
| `T04` | dashboard 200 but inference fails; signal: two_person_review, inference_failed_despite_dashboard_200 | `STOP_HEALTH_ROLLBACK_DECISION` | `STOP_HEALTH_ROLLBACK_DECISION` |
| `T05` | firewall change risks admin lockout; signal: lockout_risk, two_person_review | `STOP_ACCESS_RISK` | `STOP_ACCESS_RISK` |
| `T06` | rollback target owner ambiguous; signal: resource_owner_ambiguous, two_person_review | `STOP_WRONG_OR_UNKNOWN_TARGET` | `STOP_WRONG_OR_UNKNOWN_TARGET` |
| `T07` | n8n outage after hypothetical single change; signal: two_person_review, n8n_outage | `STOP_HEALTH_ROLLBACK_DECISION` | `STOP_HEALTH_ROLLBACK_DECISION` |
| `T08` | TLS break after hypothetical single change; signal: two_person_review, tls_break | `STOP_HEALTH_ROLLBACK_DECISION` | `STOP_HEALTH_ROLLBACK_DECISION` |
| `T09` | change requested without independent approval; signal: all hypothetical gates | `STOP_NOT_AUTHORIZED` | `STOP_NOT_AUTHORIZED` |
| `T10` | all hypothetical preconditions but S2 cannot authorize execution; signal: two_person_review | `HOLD_FOR_SEPARATE_CHANGE_WINDOW` | `HOLD_FOR_SEPARATE_CHANGE_WINDOW` |

## Approval checklist và blockers cho owner
- Mẫu đầy đủ trong runbook và JSON: `change_id=UNASSIGNED`, exact owner/resource/action/inverse/window cần điền bởi bên có quyền; current backup/restore evidence và rollback test `UNKNOWN`, independent two-person review bắt buộc, A0 approval cho từng control, redacted evidence path. Nếu thiếu một điều kiện, không triển khai.
- **Blockers:** quyền làm việc Hostinger Agent chưa ACK trong phiên Hermes; public port owner/need và alternate access chưa chứng minh; TLS owner unknown; credential consumer scope/compromise unknown; P0 cause unknown; isolated restore/RPO/RTO chưa xác minh; all approvals absent. Hostinger thực thụ và ChatGPT Điều phối review độc lập rồi A0 quyết định scope từng future change.
- **Verdict:** `SEC02_S2_HARDENING_PLAN_READY_FOR_A0_REVIEW` nghĩa là kế hoạch và policy fixture offline có thể review; không phải `SECURITY_HARDENED`, `RESTORE_PASS`, `P0_RECOVERED`, `TLS_VERIFIED` hay ủy quyền production.
- **Handoff:** `TASK=SEC-02/S2 | AGENT=Hermes WebUI (executor; Hostinger Agent nominated owner) | EXECUTE_ACK=ACKNOWLEDGED in this session only | SOURCE_SHAS=see JSON | F01-F07=7 traced | CONTROL_GATES=5 distinct NOT_AUTHORIZED orders | TABLETOP=10/10 offline policy decisions | EVIDENCE=reports/evidence/2026-11-23-hostinger-sec02-s2-tabletop.json | VERDICT=SEC02_S2_HARDENING_PLAN_READY_FOR_A0_REVIEW (author draft) | PR_URL=unavailable until GitHub auth | NEXT_OWNER=ChatGPT Điều phối`.
