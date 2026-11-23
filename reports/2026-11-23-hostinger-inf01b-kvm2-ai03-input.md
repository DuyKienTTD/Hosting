---
id: ttd-hostinger-inf01b-kvm2-ai03-input-2026-11-23
type: read-only-preflight-input
status: INF01B_READONLY_PREFLIGHT_INPUT_READY_FOR_REVIEW
updated_at: 2026-11-23
sensitivity: public-redacted
---
# INF-01B — KVM2 / AI-03 preflight input delta

`TASK=INF-01B | AGENT=hostinger-agent | BASE_SHA=e385c1b | ACK_EXECUTE=ACKNOWLEDGED | UTC=2026-11-23T03:49:46Z | NEXT_OWNER=chatgpt`

## Scope

Đây là delta read-only, dùng INF-01/SEC-02 làm baseline và không lặp lại toàn bộ các kiểm tra đã PASS. Không chạy fixture KVM2, không tạo/xóa/chạy container, không pull/build image, không đọc secret/env/log payload, không thay đổi firewall/SSH/TLS/backup, không restore/migrate và không gọi paid API.

## Candidate B2-P reference

PR #7 mô tả candidate fake-only với `LIVE_ENABLED=False`, Linux amd64 dự kiến, zero host ports, internal networks, không Docker socket, 8 services, 7 networks và 6 volumes. Đây là cấu hình kế hoạch/evidence repository, không phải runtime đã tạo trên KVM2. Candidate cap được đối chiếu theo spec là 1.50 vCPU và 2304 MiB.

## Evidence matrix

| field | expected | observed/redacted | source | measured_at_utc | verifier | status | blocker | next_owner |
|---|---|---|---|---|---|---|---|---|
| KVM2 identity | đúng VPS được ủy quyền, tách khỏi managed Hermes | VPS resource duy nhất trong account khớp KVM2; managed Hermes là resource khác | Hostinger VPS inventory + U4S application inventory | 2026-11-23T03:49Z | hostinger-agent | PASS_INPUT | none | chatgpt |
| project collision | candidate name chưa có trong observed project list | không thấy `h6-b2-p-fake-candidate` trong 4 project hiện tại | Docker project inventory | 2026-11-23T03:49Z | hostinger-agent | PASS_INPUT | chỉ là observed scope, không phải global absence | chatgpt |
| network/volume collision | nonce names and bind root not in use | exact nonce names/bind root không có trong spec input được truy cập; không thể so sánh | allowed metadata + PR #7 plan | 2026-11-23T03:49Z | hostinger-agent | NOT_MEASURED | exact names/listing command bị giới hạn | chatgpt |
| image/platform/cache | candidate image resolved, platform and cache verified on KVM2 | current running projects expose image references; resolved candidate image/platform/cache chưa inspect được; không pull/build | Docker project/container metadata; PR #7 | 2026-11-23T03:49Z | hostinger-agent | BLOCKED_ACCESS | allow-list chặn inventory image/info sâu | chatgpt |
| host headroom | fresh total/available CPU, RAM, disk and inode | 2 vCPU plan; RAM 7940 MiB total, 5185 MiB available, 0 swap; root 14% used; root inode 4% used; disk 86.7 GB available | VPS command allow-list | 2026-11-23T03:49:46Z | hostinger-agent | PASS_INPUT | CPU total/host contention not independently measured | chatgpt |
| B2-P memory margin | candidate 2304 MiB must not overcommit | arithmetic headroom exists at snapshot, but candidate would consume about 2.3 GiB of 5.2 GiB available before overhead; no GO inference | fresh free + candidate spec | 2026-11-23T03:49:46Z | hostinger-agent | RISK_FOUND | no host CPU contention, cache growth or fixture overhead proof | chatgpt |
| Docker current usage | fresh per-container usage and limits | current stats: Gate-A aggregate about 316 MiB across limits; P0 n8n about 399 MiB/768 MiB; production Hermes about 483 MiB; production n8n about 380 MiB; CPU snapshots low but point-in-time | Docker stats and project container metadata | 2026-11-23T03:49Z | hostinger-agent | PASS_INPUT | no trend and no candidate overhead measurement | chatgpt |
| service/restart metadata | fresh Hermes/n8n health, IDs, OOM/start info | Hermes and n8n running about 3 weeks; health field empty; P0 reasoner still exited 137 about 43 hours, current state not recovered; no logs read | Docker project/container metadata | 2026-11-23T03:49Z | hostinger-agent | RISK_FOUND | P0 cause and recovery unknown; two project detail reads temporarily failed | chatgpt |
| rollback ledger | document-only schema before future fixture | schema included below; future real IDs do not exist yet and are not invented | INF-01B report design | 2026-11-23T03:49Z | hostinger-agent | PASS_INPUT | execution requires separate approval | chatgpt |
| security boundary | SEC-02 findings carried forward without re-querying secrets | public RDP/8501 and published service exposure remain prior risk; credential field exposure remains redacted; no re-query | SEC-02 report + INF-01 | 2026-11-23T03:49Z | hostinger-agent | RISK_FOUND | owner/need and consumer scope unresolved | chatgpt |

## Resource and collision conclusion

`COLLISION_NOT_FOUND_IN_OBSERVED_SCOPE` for the planned project name only. `NOT_MEASURED` for exact nonce network names, volume names and bind root because the exact values were not available and deeper listing commands were blocked. No cleanup or deletion was attempted. Existing Hermes environments remain distinct: KVM2 Docker versus the separate managed application.

## Image/platform conclusion

`IMAGE_PLATFORM_UNVERIFIED` for the B2-P candidate. PR #7 records Linux amd64 as planned/source evidence, but no KVM2 resolved candidate image manifest/digest/platform/cache was inspected in this delta, and no image was pulled or built.

## Headroom and overcommit

Fresh RAM and disk are not exhausted, but the candidate cap of 1.50 vCPU on a 2 vCPU VPS leaves limited CPU allocation for active workloads. Candidate memory of 2304 MiB is arithmetically within current available RAM, but the calculation excludes image/page cache, Docker overhead, filesystem cache, restart bursts and the P0 failure state. Therefore this is `RISK_FOUND`, not a fixture GO.

## Document-only rollback ledger

Before any future approved fixture, record:
- `resource_id`: KVM2 resource ID, exact target confirmed preflight.
- `project_name` and `project_label`: candidate project plus unique nonce.
- `container_ids`, `network_ids`, `volume_ids`: populated only after approved creation; never invented in a preflight report.
- `created_at_utc`, `owner`, `task_id`, `branch_sha`: immutable audit fields.
- `preexisting_excluded`: existing production and Gate-A/P0 resources explicitly excluded from cleanup.
- `bind_root`: approved isolated path only; stop if it overlaps an existing path.
- `ports`: expected zero published host ports for candidate; stop on any non-zero publication.
- `rollback_path`: remove only resources whose IDs and nonce match the ledger, after owner approval; never broad-delete by prefix.
- `loss_of_access_stop`: stop before any firewall/SSH/TLS operation or if target identity differs.

Hard STOP conditions: identity mismatch, exact collision, unexpected host port, Docker socket mount, non-internal network, missing owner label/nonce, candidate `LIVE_ENABLED` not false, resource headroom below approved margin, P0/production health deterioration, or any tool request for secret/write/paid access.

## Five-category preflight status

- **PASS_INPUT:** identity/resource boundary; observed project-name collision check; fresh RAM/disk/inode and current Docker stats; document-only rollback schema.
- **RISK_FOUND:** memory/CPU overcommit margin; P0 reasoner failure; SEC-02 exposure risks.
- **BLOCKED_ACCESS:** resolved candidate image/platform/cache; exact Docker network/volume/bind-root comparison; complete detail for two project reads.
- **NOT_MEASURED:** exact nonce collision and external reachability; no fixture run, no trend measurement.
- **VERDICT:** `INF01B_READONLY_PREFLIGHT_INPUT_READY_FOR_REVIEW`. This does not validate a candidate runtime, does not approve AI-03, and does not open paid Gate B.

## Handoff

`TASK | AGENT | BASE_SHA | ACK_EXECUTE | UTC | SOURCE | OBSERVED/EXPECTED | EVIDENCE | VERDICT | BLOCKERS | NEXT_OWNER=chatgpt`

Hostinger Agent → ChatGPT điều phối. ChatGPT phải reconcile với Codex B2-P và Work findings trước bất kỳ GO/NO_GO nào.
