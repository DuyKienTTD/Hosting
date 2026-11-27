---
id: ttd-hostinger-ws02-infrastructure-baseline-001
type: evidence-report
status: completed-with-blockers
observed_at: 2026-11-23T03:17:49Z
owner: hostinger-agent
reviewer: chatgpt
sensitivity: public-redacted
---
# WS-02 Infrastructure Baseline

## Scope and safety
Read-only inspection of VPS KVM2 `1722328` through Hostinger VPS tools and allow-listed diagnostics. No restart, redeploy, restore, migration, firewall/service change, secret read, production write, or paid API call was performed.

## Sources and observation time
- Hostinger VPS inventory and Docker project listing: observed during this run on 2026-11-23 UTC.
- VPS allow-listed commands: observed at `2026-11-23T03:17:49Z` for uptime and immediately following checks for memory, disk, sockets, firewall service, SSH, Docker, and network reachability.
- Backup schedule, backup inventory and VPS action log: observed during this run on 2026-11-23 UTC.
- GitHub task and repository rules: read from `main` before inspection.
- Values below are point-in-time observations, not a continuous monitor.

## Baseline results

### VPS inventory and capacity
- VPS: KVM2, Ubuntu 24.04 LTS, running, 2 vCPU, 8 GiB RAM, 100 GB plan disk.
- Hostinger-reported snapshot: CPU 10.83%, disk usage approximately 13.5 GB, bandwidth usage 0.03%.
- In-guest uptime: 36 days 16 hours 36 minutes; load average 0.87 / 0.48 / 0.39.
- In-guest memory: 2.7 GiB used, 5.1 GiB available, 346 MiB free, no swap configured.
- Filesystem: root volume 96 GB, 14 GB used, 83 GB available, 14% used; `/boot` 15% used.
- Baseline verdict: `PASS_WITH_NOTES`. Capacity is not currently near disk or memory exhaustion, but no swap and the exited workload below require monitoring.

### Docker state
Projects listed as running:
- `hermes-agent-l7fe`: one container running; published host port 32768 to container port 4860.
- `n8n-nbqy`: one container running; published host port 32770 to container port 5678.
- `ttd-hermes-gate-a`: four containers running and healthy; no published host ports in the returned container details.
- `ttd-p0-level1`: two containers running and healthy; `ttd-p0-reasoner` exited with code 137 about 42 hours before observation.

Detailed container stats were returned for `ttd-hermes-gate-a` and `ttd-p0-level1`. The Docker Manager detail calls for two other projects returned a temporary read failure, so their detailed health/stats are not treated as verified beyond the project listing.

The Docker metadata response included a plaintext admin credential field for one project. The value is intentionally redacted and not copied into this report. This is a security finding requiring credential rotation through an approved change task; no rotation was performed in INF-01.

Baseline verdict: `BLOCKED_ACCEPTANCE` for full application health because one P0 reasoner is exited and two project detail reads were unavailable.

### Network and services
- Connectivity: three ICMP probes to a public resolver succeeded with 0% loss; average round trip was approximately 7.94 ms.
- Listening sockets observed: SSH on 22; Docker-published services on 32768 and 32770; PostgreSQL bound to loopback on 5432; local printing and resolver sockets; RDP on 3389.
- Docker service: active.
- SSH service: active.
- Host firewall service: active.
- Baseline verdict: `PASS_WITH_SECURITY_FINDINGS`.

### Firewall
- Hostinger-managed firewall group: none attached to this VPS at observation time.
- UFW: active, incoming default deny, outgoing allow, routed default deny.
- UFW allowed inbound ports: 22, 80, 443, 8501 and 3389, for IPv4 and IPv6.
- The socket check did not show listeners on 80, 443 or 8501, but 3389 was listening and globally allowed. Exposing RDP on all addresses is a security finding and is not changed by this read-only task.
- Baseline verdict: `BLOCKED_SECURITY_REVIEW` until the owner confirms whether public RDP and port 8501 are required and narrows access where appropriate.

### HTTPS/TLS
- No listener on TCP 443 appeared in the in-guest socket snapshot.
- The allow-listed command runner rejected the attempted HTTPS/TLS probe, so certificate chain, protocol version and endpoint response were not independently verified.
- Baseline verdict: `BLOCKED_VERIFICATION`. This report does not claim HTTPS/TLS is healthy or unhealthy; the evidence is insufficient and the local 443 listener was absent at observation time.

### Backups and actions
- Backup schedule: enabled, weekly frequency, daily backup not enabled.
- Latest listed completed backup: 2026-11-16 09:23:43 UTC. Another completed backup was listed for 2026-11-09.
- Both listed backups were finished successfully. The action log also showed recurring successful weekly backup creation events.
- No restore test was performed. Backup existence is not evidence that restore isolation or recovery objectives have been tested.
- Baseline verdict: `PASS_WITH_LIMITS` for backup metadata; restore acceptance remains unverified.

## Acceptance matrix

| Area | Verdict | Evidence gap / follow-up |
|---|---|---|
| VPS identity and capacity | PASS_WITH_NOTES | Point-in-time only; no swap and exited P0 workload need monitoring |
| Docker project inventory | PASS_WITH_BLOCKERS | P0 reasoner exited 137; two detailed project reads temporarily unavailable |
| Network reachability | PASS | ICMP succeeded, Docker and SSH state observed |
| Firewall | BLOCKED_SECURITY_REVIEW | Public RDP and 8501 rules require owner review; no Hostinger firewall group attached |
| HTTPS/TLS | BLOCKED_VERIFICATION | No 443 listener observed; TLS probe rejected by command whitelist |
| Backup metadata | PASS_WITH_LIMITS | Weekly backups present; restore test and RPO/RTO not verified |
| Secrets exposure | BLOCKED_REMEDIATION | Docker listing exposed a plaintext credential field; value redacted, no rotation performed |

## Acceptance criteria status
`NOT_READY_FOR_FULL_ACCEPTANCE`.

The read-only baseline is complete enough to hand off, but full acceptance is blocked by: exited P0 reasoner, incomplete Docker detail reads, public RDP exposure, unverified HTTPS/TLS with no 443 listener, and a plaintext credential field returned by Docker metadata. These findings are recorded without changing the system.

## Handoff
- From agent: `hostinger-agent`
- To agent: `chatgpt`
- Next owner: `chatgpt`
- Handoff state: `COMPLETED_WITH_BLOCKERS`
- Recommended next task IDs: security review for public RDP/8501 and credential rotation; separate P0 reasoner diagnosis; HTTPS/TLS endpoint verification; restore/RPO-RTO validation.

## Evidence boundary
This is a redacted point-in-time read-only report. It does not authorize or perform firewall edits, credential rotation, restart, redeploy, restore, migration, production changes or paid API calls.
