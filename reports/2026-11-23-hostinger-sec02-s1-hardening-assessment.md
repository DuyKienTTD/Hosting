---
id: ttd-hostinger-sec02-s1-hardening-assessment-2026-11-23
type: security-design-assessment
status: SEC02_S1_DESIGN_READY_FOR_REVIEW
updated_at: 2026-11-23
sensitivity: public-redacted
---
# SEC-02/S1 Security Exposure, Credential Handling and Recovery Design

`TASK=SEC-02/S1 | AGENT=hostinger-agent | BASE_SHA=e385c1bea2070973e3007e5717f7e980348d6ab3 | ACK_EXECUTE=ACKNOWLEDGED | NEXT_OWNER=chatgpt`

## Scope and source boundary

Đây là design/review read-only. Không restart, redeploy, restore, migration, sửa firewall/UFW/SSH/RDP/SSL, rotate/revoke/reset credential, đọc log/payload chứa secret, gọi paid API hoặc thay đổi production.

Nguồn chính:
- Comment thực thi SEC-02/S1 trên PR #9, comment ID `7090723789`, đọc ngày 2026-11-23.
- `main` tại BASE_SHA ở trên.
- INF-01 report trên branch riêng, commit `486afc2`, quan sát chính lúc `2026-11-23T03:17:49Z`.
- Read-only recheck trong phiên này lúc khoảng `2026-11-23T03:26Z`: Docker metadata P0, hai Docker project trước đó lỗi đọc, VPS inventory và resource identity.
- PR #8 INF-02 được đọc để tránh trùng runbook; trạng thái ghi nhận là runbook/tabletop synthetic, không phải runtime monitoring.

## Identity và boundary

- VPS KVM2 được xác minh là resource `1722328`, Ubuntu 24.04, đang chạy, Docker đã cài, không gắn Hostinger-managed firewall group.
- Docker projects trên VPS là phạm vi KVM2. `ttdnew.tech` được trả về từ resource AI automation riêng với runtime `u4s-hermes-agent`, không coi là container/project trên KVM2.
- Vì vậy, kết quả của KVM2 không được suy ra cho `ttdnew.tech`, và ngược lại. Hai runtime phải có inventory, backup, owner và approval riêng.
- INF-01 report/PR #9 vẫn chưa merge vào `main`; không coi evidence trên branch là trạng thái đã hoàn tất trên `main`.

## Finding matrix

| finding_id | observed/source/time | severity/impact | status | recommended change | risk of change | prerequisites | rollback / prevent-lockout | owner / reviewer | approval gate | post-change checks | dependency |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SEC02-F01 | UFW read-only snapshot from INF-01 at 2026-11-23T03:17:49Z: inbound default deny, but 3389 and 8501 allowed; RDP 3389 listening. No Hostinger firewall group attached. | HIGH if public RDP is not required; possible management exposure. No evidence of compromise. | VERIFIED exposure; `REACHABLE_EXTERNALLY` UNKNOWN | Confirm business need; prefer IP/VPN allowlist; if required, stage Hostinger firewall/UFW rule narrowing with SSH fallback. Do not remove access blindly. | Lockout or service outage if rule order/source is wrong. | Approved source IP/VPN, current admin SSH key, console fallback, service owner and maintenance window. | Export current rules; keep one verified SSH path and console fallback; apply one rule group at a time; test admin access before closing the old path; revert only with approved rollback. | Hostinger/platform owner; reviewer ChatGPT + independent security reviewer | Separate approval for firewall/UFW change. | Verify SSH/admin access, intended service reachability, denied source behavior, and rule persistence after reload. | Resource identity, admin fallback, service purpose, current threat model. |
| SEC02-F02 | UFW allows 8501 and the VPS socket snapshot did not show a 8501 listener. INF-01 also recorded published Docker ports 32768 Hermes and 32770 n8n. Internet reachability was not scanned. | MEDIUM/HIGH depending on intended exposure; unnecessary allow rules increase attack surface. | `UFW_ALLOWED` verified; `LISTENING` varies by port; `REACHABLE_EXTERNALLY` UNKNOWN | Map each published port to an owner and purpose; remove or narrow unused exposure only after approval; prefer reverse proxy/TLS or private access where applicable. | Breaking n8n/Hermes access or health checks. | Port-to-service inventory, consumers, DNS/reverse-proxy design, fallback path. | Snapshot rules and compose intent; preserve an approved management path; staged test and revert if health/owner checks fail. | Service owner; reviewer Hostinger Agent + ChatGPT | Separate exposure-change approval. | Check intended endpoint, denied unapproved source, container health and reverse-proxy path without port scans or login attempts. | SEC02-F01, TLS endpoint ownership, service inventory. |
| SEC02-F03 | Docker metadata recheck around 2026-11-23T03:26Z: `ttd-p0-reasoner` exited code 137, `OOMKilled=false`, unhealthy, started 2026-11-21T08:47:37Z, finished 08:49:38Z, restart policy `unless-stopped`; no logs read. | HIGH availability risk for P0 workflow; not proof of OOM or compromise. | VERIFIED exit state; cause `UNKNOWN` | Hand to runtime engineering for non-secret metadata diagnosis; compare resource limits, healthcheck and host pressure using approved read-only evidence only. | Restart/recreate/pull could alter evidence or create production impact. | Runtime owner, approved diagnostic scope, non-secret metadata source. | Do not restart in SEC-02. Preserve current state and container metadata; if a later change is approved, define pre-change snapshot and stop condition first. | Codex/runtime owner; reviewer ChatGPT | Separate runtime-engineering approval; no action from design PASS. | Read only exit/OOM/restart metadata, then validate health after any separately approved change. | INF-01, Docker project ownership, host capacity. |
| SEC02-F04 | INF-01 observed no local TCP 443 listener at 2026-11-23T03:17:49Z; allow-listed TLS probe was rejected. | MEDIUM/HIGH if this VPS owns an HTTPS endpoint; service impact or false alarm possible. | Local listener `VERIFIED_ABSENT` at snapshot; TLS ownership and external reachability `UNKNOWN`. | Identify actual TLS terminator/SNI owner before any change. If KVM2 owns it, design reverse-proxy/certificate validation with an explicit maintenance and rollback plan. | Misrouting, certificate outage or lockout if TLS is changed on the wrong runtime. | Endpoint ownership, DNS/SNI inventory, certificate metadata access, fallback path. | Preserve current endpoint until ownership is proven; stage config separately; validate certificate chain, SNI and health before cutover; retain prior config for rollback. | Owner of endpoint; reviewer independent security reviewer | Separate TLS/reverse-proxy approval. | Validate intended hostname, certificate chain, expiry, SNI, HTTP status and backend health through an approved non-invasive check. | Resource identity, published ports, DNS/reverse proxy. |
| SEC02-F05 | Backup schedule and completed weekly backups were verified in INF-01; latest listed completed backup was 2026-11-16. Restore, RPO/RTO and isolation were not tested. | HIGH data-recovery uncertainty, but backup existence is not evidence of recoverability. | Backup metadata `VERIFIED`; restore capability `UNKNOWN`. | Define manifest, retention, RPO/RTO and a future isolated restore test for each runtime; do not download/inspect/restore in S1. | Restore test can overwrite data, leak data or restart a runtime if isolation is wrong. | Approved isolated target, backup owner, data classification, downtime/cost approval, rollback and cleanup plan. | Never test against production; snapshot/manifest target; abort on wrong identity; destroy isolated test artifacts only through a separately approved procedure. | Platform owner; reviewer ChatGPT + recovery reviewer | Separate restore-test approval. | Validate file/database/service checks, timestamps, RPO/RTO measurement, isolation and cleanup evidence. | Runtime identity, backup inventory, data owner, retention policy. |
| SEC02-F06 | Docker metadata included a plaintext credential field in a response; value was redacted. No evidence in the checked data proves third-party access or compromise. | HIGH confidentiality risk; possible credential exposure. Do not label P0 without compromise evidence. | `VERIFIED_FIELD_EXPOSURE`; compromise `UNKNOWN`. | Credential owner should determine scope and rotate through an approved process: backup configuration safely, atomic consumer cutover, negative access test, revoke old credential, then verify consumers. | Service outage, lockout or accidental re-exposure if consumers are missed. | Credential owner, consumer inventory, non-secret config backup, replacement credential, maintenance window and rollback decision. | Do not re-enable the old credential after rotation; retain only approved non-secret rollback material; if cutover fails, use a separately approved emergency path rather than copying the old secret into logs/chat. | Credential owner; reviewer independent security reviewer | Separate credential-rotation approval; not performed by S1. | Confirm new consumer authentication, old credential rejection, no secret in Git/logs/reports, and service health. | Docker project inventory, consumer inventory, secret store/rotation path. |
| SEC02-F07 | Resource identity read-only checks around 2026-11-23: KVM2 `1722328` is separate from the AI automation resource running `u4s-hermes-agent` on `ttdnew.tech`. | MEDIUM operational risk if actions or backups are applied to the wrong runtime. | VERIFIED separation. | Make runtime ID, owner, endpoint and backup scope mandatory fields in future change requests. | Wrong-target change or restore. | Authoritative resource lookup before every action. | Abort on ID/domain mismatch; no inferred cross-resource access. | ChatGPT coordinator; reviewer Hostinger Agent | Mandatory preflight, no extra approval for read-only identity check. | Compare resource ID, hostname/domain, runtime, region and backup ID before change. | All subsequent INF/SEC/MIG tasks. |

## Proposed remediation sequence, not execution

### S0: preserve access and evidence
1. Keep current runtime unchanged.
2. Record current resource identity, branch SHA, evidence timestamp and redacted findings.
3. Confirm an approved SSH key/admin path and console fallback before any firewall, SSH, RDP or TLS change.
4. Do not rotate or revoke the exposed credential until consumer inventory and replacement path are approved.

### S1: close identity and exposure gaps
1. Owner identifies whether 3389 and 8501 are required and maps 32768/32770 to consumers.
2. Security reviewer approves a least-exposure design with source restrictions and a rollback sequence.
3. Endpoint owner identifies TLS terminator and SNI, if any, before touching certificate or reverse-proxy configuration.

### S2: recovery and runtime follow-up
1. Runtime owner investigates exit 137 using non-secret metadata and resource evidence, not logs in this task.
2. Recovery owner defines isolated restore manifest, RPO/RTO and post-restore checks.
3. Only after separate approval may a controlled rotation, firewall hardening, TLS change, or isolated restore be scheduled.

## Acceptance and safety gates

`SEC02_S1_DESIGN_READY_FOR_REVIEW` is satisfied for the design artifact: each finding has source/time, impact, VERIFIED/UNKNOWN state, owner/reviewer, prerequisites, rollback/prevent-lockout, approval gate, post-change checks and dependencies; evidence is redacted; no runtime change was made.

This does **not** mean `SECURITY_HARDENED`, `TLS_VERIFIED`, `RESTORE_PASS` or `P0_RECOVERED`. Those remain blocked or unknown until their separate evidence and approvals exist.

## Blockers
- No approved owner/source inventory for public 3389, 8501 or published service ports.
- TLS endpoint ownership and external reachability are not verified.
- Credential consumer scope and compromise status are unknown; no rotation performed.
- P0 exit-137 cause is unknown; no restart or logs read.
- Restore isolation and RPO/RTO are untested.
- PR #9 evidence remains on a draft branch and is not merged to `main`.

## Handoff
`HANDOFF/REPORT FORMAT: TASK=SEC-02/S1 | AGENT=hostinger-agent | BASE_SHA=e385c1b | ACK_EXECUTE=ACKNOWLEDGED | OBSERVED=INF-01 plus permitted delta checks | EXPECTED=redacted risk/remediation matrix with rollback and approvals | TESTS/READ_SOURCE=PR #9 comment, main rules/state/catalog/agent profile, INF-01 report, PR #8 INF-02 metadata, VPS/Docker read-only tools | EVIDENCE=SEC-02 report and optional redacted JSON on branch | VERDICT=SEC02_S1_DESIGN_READY_FOR_REVIEW | BLOCKERS=see above | NEXT_OWNER=chatgpt`

No production hardening was started from this design result.
