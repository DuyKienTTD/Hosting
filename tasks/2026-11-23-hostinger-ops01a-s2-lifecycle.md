---
id: ttd-hostinger-ops01a-s2-lifecycle-2026-11-23
type: offline-lifecycle-delta
status: completed-synthetic-pass
owner: hostinger-agent
next_owner: chatgpt
---
# OPS-01A/S2 Offline Lifecycle Delta

Phạm vi: state machine synthetic-only cho một resource+rule: `NORMAL -> OPEN -> RECOVERED/CLOSED -> OPEN`, time-aware dedupe theo UTC, rule version, resource và cooldown 900 giây. Không có notification thật, live monitoring, VPS, Docker, scheduler, credential, network hoặc paid API.

Nguồn pin: OPS-01A/S1 policy/evidence đã được chấp nhận; đặc tả S2 tại comment điều phối PR #22.

Acceptance: actual offline tests cho bad×3 → OPEN → good×3 → RECOVERED → bad×3 → OPEN lần hai; duplicate trong 899 giây bị suppress; đúng 900 giây được phép REOPEN; UNKNOWN/stale/blocked reset streak; duplicate/out-of-order/resource/source fail closed; source đổi không giả mạo resource; S1 timeline giữ nguyên; UTC clock reversal; snapshot/replay deterministic.

QA result: `OPS01A_S2_OFFLINE_LIFECYCLE_PASS`. PASS chỉ cho offline lifecycle contract, không phải `MONITORING_LIVE` hay production approval.
