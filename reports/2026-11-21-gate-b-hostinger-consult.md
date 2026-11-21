---
id: hermes-gate-b-hostinger-consult-2026-11-21
type: report
status: complete
updated_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
handoff: H1
owner: hostinger-agent
next_owner: chatgpt
gate_status: NOT_READY
---

# H1, Hostinger Agent read-only handoff cho TTD-HERMES-GATE-B-001

## Phạm vi

Đã đọc bắt buộc `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/hostinger.md` và task H1 trước khi kiểm tra.

Chỉ thực hiện kiểm tra đọc trên VPS KVM 2. Không deploy, restart, stop, update, restore, migrate, đổi firewall, đổi network, gọi paid API hoặc thay đổi production.

## Kết luận điều hành

Topology hiện tại cho Gate A có dấu hiệu cô lập mạng rõ ràng và các container Gate A đang healthy. Tuy nhiên H1 **chưa đủ điều kiện PASS/READY** vì:

1. Strict guard-only credential mount không được xác nhận. Một số mount credential xuất hiện ở bridge, Hermes auxiliary và provider mock, không chỉ ở guard.
2. Persistence sau redeploy chưa được kiểm thử vì redeploy là thay đổi runtime.
3. Rollback thực tế chưa được kiểm thử; chỉ xác minh backup/schedule tồn tại.
4. Dynamic no-bypass test chưa được chạy trong H1; chỉ có topology live và evidence cũ trong repository.
5. Chi tiết container của hai project Gate A/P0 có lúc trả lỗi tạm thời từ Docker Manager, nên không đánh dấu các mục còn thiếu là PASS.

## Ma trận kết quả

| Hạng mục | Trạng thái | Bằng chứng đã khử bí mật |
|---|---|---|
| Rule/agent context đã đọc | VERIFIED_LIVE | Đã đọc sáu tài liệu bắt buộc trên `main` trước kiểm tra |
| Gate A container health | VERIFIED_LIVE | Bridge, guard, Hermes auxiliary và provider mock đều running/healthy tại thời điểm kiểm tra |
| Network separation topology | VERIFIED_LIVE | Bridge ở sandbox + control; Hermes ở control + provider; guard ở private + provider + upstream; provider mock chỉ ở upstream |
| Published port no-bypass | VERIFIED_LIVE | Các container Gate A không có published port; không có entrypoint công khai cho Gate A |
| Guard-only credential mount | NOT_VERIFIED | Mount credential tồn tại ở nhiều vai trò; chưa đạt strict guard-only |
| Guard code/test mount protection | VERIFIED_LIVE | Guard code và contract test được mount read-only; state/capture tách riêng |
| Hermes state persistence intent | VERIFIED_LIVE | Hermes có named volume cho data và bind mount home/state ở chế độ read-write |
| Persistence after redeploy | UNKNOWN | Không redeploy theo yêu cầu an toàn; chưa có bằng chứng sau recreate/redeploy |
| No-bypass dynamic test | UNKNOWN | Chưa chạy script/test từ file; topology chỉ chứng minh cấu hình hiện tại |
| Backup availability | VERIFIED_LIVE | VPS có hai backup finished và lịch backup 7 ngày đang enabled |
| Rollback execution | UNKNOWN | Chưa restore backup hoặc rollback Compose vì đó là thay đổi runtime |
| Paid API call | NOT_PERFORMED | Không gọi API trả phí |
| Production mutation | NOT_PERFORMED | Không thay đổi production |

## Bằng chứng live đã thu thập

### Docker projects

- `ttd-hermes-gate-a`: 4 container, running/healthy.
- `hermes-agent-l7fe`: running.
- `n8n-nbqy`: running.
- `ttd-p0-level1`: mixed, có một container exited; không dùng trạng thái này để kết luận H1 Gate B.

### Network topology

- `ttd-ai-p0-sandbox`: bridge/reasoner được nối vào sandbox và control.
- `ttd-hermes-gate-a-control`: bridge và Hermes auxiliary cùng control plane.
- `ttd-hermes-gate-a-provider`: guard và Hermes auxiliary cùng provider plane.
- `ttd-hermes-gate-a-upstream`: guard và provider mock cùng upstream plane.
- `ttd-gate-b-guard-private`: network riêng được hiện diện trên Docker host, nhưng chưa xác minh membership của container Gate B do Docker Manager/container lookup tạm thời không trả chi tiết.

Không đưa IP, hostnames, secret values, token values hoặc private endpoint vào evidence.

### Credential mounts

Đã đọc metadata mount nhưng không đọc hoặc ghi giá trị credential. Kết quả khử bí mật:

- Guard có guard-service credential ở chế độ read-only.
- Hermes auxiliary có API-server credential và guard-service credential ở chế độ read-only.
- Bridge có API-server credential và existing-P0 credential ở chế độ read-only.
- Provider mock có guard-service credential ở chế độ read-only.

Do đó, nếu acceptance yêu cầu credential provider/guard chỉ được mount vào guard, cấu hình hiện tại **không đạt strict guard-only**. Cần owner xác định chính xác credential nào là guard-only trước khi sửa; H1 không tự sửa.

### Persistence và rollback

- Hermes auxiliary có named data volume và bind mount state/home read-write.
- Bridge có named data volume và bind mount state read-write.
- Guard có named data volume, capture read-write, code/test read-only và budget ledger read-only.
- VPS có backup finished và schedule 7 ngày enabled.

Các mount trên chứng minh ý định lưu state ngoài container layer, không chứng minh persistence sau redeploy. Backup tồn tại không chứng minh restore/rollback đã thành công.

## Evidence sources

- Live VPS Docker project inventory.
- Live Docker network list.
- Live container status.
- Live container network membership đã khử IP.
- Live container mount metadata đã khử path/credential value.
- VPS backup inventory và schedule.
- Existing repository evidence về Gate B được giữ nguyên và không được nâng cấp trạng thái thành fresh live evidence.

## Handoff cho ChatGPT

`from_agent: hostinger-agent`

`to_agent: chatgpt`

`handoff_state: READY_FOR_OWNER_FORWARD`

`result: MIXED`

`gate_status: NOT_READY`

`verified_live`: rule context, Gate A health, network topology, no published Gate A ports, read-only code/secret mount modes, persistence intent, VPS backup inventory.

`unknown`: redeploy persistence, dynamic no-bypass, actual rollback, Gate B private network membership, exact owner of each credential mount.

`blocking_items`: strict guard-only mount not demonstrated; Docker Manager detail lookup temporarily failed for two projects; no destructive or paid test was allowed.

## Đề xuất bước tiếp theo, không thực hiện trong H1

1. Owner xác định credential nào phải guard-only và cập nhật Compose contract.
2. Codex kiểm tra static Compose diff/config mà không in secret value.
3. Chỉ sau approval mới chạy redeploy test trên sandbox copy, không dùng production runtime.
4. Chỉ sau khi sandbox PASS mới thiết kế rollback/restore test có backup và approval.
