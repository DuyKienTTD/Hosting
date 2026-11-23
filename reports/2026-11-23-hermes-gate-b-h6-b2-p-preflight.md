---
id: hermes-gate-b-h6-b2-p-preflight-2026-11-23
type: report
status: blocked
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# AI-02 / H6 B2-P — Candidate fake-only và preflight KVM2

| TASK | AGENT | BASE_SHA | OBSERVED | EXPECTED | TEST_RESULTS | EVIDENCE | VERDICT | BLOCKERS | NEXT_OWNER |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ttd-hermes-gate-b-001 / AI-02 / B2-P` | Codex | `d95f161` | Candidate fake-only render local đạt | Render, no-overlap và headroom hiện hành, rollback giới hạn | 4/4 targeted, render lặp khớp, trace B2-O lưu sẵn đạt | [JSON](evidence/2026-11-23-ttd-hermes-gate-b-h6-b2-p-preflight.json) | `B2P_LOCAL_RENDER_PASS / BLOCKED_PREFLIGHT_INPUT` | Chưa xác minh phiên KVM2 read-only và metadata live | ChatGPT Điều phối |

**ACKNOWLEDGED** trong lượt thực thi ngày 23/11/2026 ICT, theo phân công [`cdf0aed`](https://github.com/DuyKienTTD/Hosting/commit/cdf0aed51965465601320fd57623a84065ad9c5b). ACK AGENTS, Workflow §§7–10, Security, STATE/CATALOG, hồ sơ Codex, task Gate B và ADR-P0-003 tại `e385c1bea2070973e3007e5717f7e980348d6ab3`. Các tệp quy tắc và task gốc khớp byte với bản đã đọc đầy đủ ở `a22516a`. Work O1–O4 trên PR #4 ở `26325b2` có tiêu chí, verdict độc lập chưa xuất hiện ở thời điểm kiểm tra. Kết quả B2-P không phụ thuộc việc chờ Work để render offline. [Task Gate B](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [PR #4](https://github.com/DuyKienTTD/Hosting/pull/4).

## Ba finding B2-O ở PR #5

| Finding | Kết quả xử lý cho candidate B2-P |
| --- | --- |
| Nguồn ACK B2-O | `a343f18` là SHA tài liệu, còn ACK của B2-P là xác nhận nhận lệnh trong lượt thực thi này, gắn với `cdf0aed`. Không dùng commit quy tắc để làm bằng chứng giao/nhận B2-O. [Finding](https://github.com/DuyKienTTD/Hosting/pull/5#discussion_r4655099761) |
| Projection ghim | Tính projection từ source workflow trước khi render. Projection phải khớp `08aa63bc…0d` và evidence B2-O. Test đổi timeout nguồn từ chối drift. Đây là digest của workflow nguồn đã chuẩn hóa. Workflow candidate vẫn có nhánh callback thử nghiệm. [Finding](https://github.com/DuyKienTTD/Hosting/pull/5#discussion_r4655099766) |
| Nguồn timeout | Kiểm đúng một event timer Guard, sau dispatch và trước read-end. Trace B2-O lưu sẵn có timer ở **45,000576 s**, read-end sau **0,427 ms** và provider trả muộn hơn. Ca thiếu, trùng, sai role hoặc timer đến sau read-end đều fail. [Finding](https://github.com/DuyKienTTD/Hosting/pull/5#discussion_r4655099772) |

Đối chiếu các finding theo phạm vi B2-O của B2-P. Candidate và các chốt được ghi ở nhánh B2-P theo write-set. Diff source và evidence cũ trên PR #5 giữ nguyên. Các finding B2-N lịch sử nằm ngoài delta này. Không chạy lại B2-O, không thay verdict của Work.

## Render, phạm vi và kiểm thử

- Source kế thừa route local B2-O: n8n admission → async adapter → Hermes auxiliary → Guard/transport → fake recorder, cùng writer SQLite giả và callback qua n8n đến receiver. Giữ tám role, bảy mạng private, sáu volume dữ liệu, cùng image pin và hash config Hermes. `LIVE_ENABLED=False` được kiểm ở source trước render. Proxy CONNECT/TLS và idle 30 s `NOT_MEASURED` vì candidate nối trực tiếp recorder giả. B2-G là bằng chứng riêng, không thay thế phép đo integrated qua proxy.
- Chốt thay đổi khi nhắm Linux KVM2: project `h6-b2-p-fake-candidate`, owner label riêng, profile `fake`, platform `linux/amd64`, mạng internal IPv4 bridge gateway `isolated`, RO rootfs và zero host ports. Bind duy nhất mỗi role là thư mục staging tổng hợp có nonce, chỉ đọc, `rprivate`, không tự tạo. Không có external network, protected bind hay Docker socket. Sáu volume state đặt tên theo project. Trần đề xuất tổng **1,5 vCPU và 2.304 MiB**. Đây là trần config, headroom và hiệu năng chưa đo trên KVM2.
- Docker Compose local `v5.1.4`, `--profile '*' config --format json --no-path-resolution`. Render hai lần cùng input khớp byte, sau đó chạy lại với nonce mới và xác nhận projection redacted khớp. SHA-256 `fa1661930b548f628d84e044f9a8f4695aef3b7821de414e7066062f1c5eb1b0`. Kiểm định dạng và reject thêm port host, bind Docker socket, external network, volume mất owner và lệch cap RAM. Không cần Docker daemon để render. Local Desktop Linux daemon không mở named pipe khi thử đọc image metadata, nên image cache hiện hành chưa xác minh. [Compose config](https://docs.docker.com/reference/cli/docker/compose/config/) · [Source](../sandbox/p0-hermes-gate-a/h6_b2p_preflight.py).

```powershell
python -X utf8 -B sandbox/p0-hermes-gate-a/h6_b2p_preflight_test.py
python -X utf8 -B sandbox/p0-hermes-gate-a/h6_b2p_preflight.py --evidence "$env:TEMP/ttd-b2p-render.json"
```

## Input KVM2 còn thiếu và điều kiện rollback

Đã dùng lại B2-G/H/M làm baseline lịch sử cho topology, Compose và ownership. Browser inventory không có hPanel/Web Terminal trong Chrome profile được kết nối. Computer-use dừng trước khi đọc hPanel vì không xác minh được URL hiện tại. Không có SSH config xác định target và quyền phiên, SSH agent không phản hồi (`ssh-add -l` exit 2). Hostinger có ACK năng lực, nhưng chưa thấy branch/PR evidence INF-01 khi kiểm. Vì vậy chưa xác minh quyền đọc KVM2 và không truy cập VPS.

| Trường chờ | Tiêu chí tối thiểu cho lần đối chiếu tiếp |
| --- | --- |
| Identity, collision và images | Snapshot chỉ đọc có timestamp từ đúng KVM2. So tên/label project, container/network/volume, metadata bind và thư mục staging riêng với manifest. Xác minh image digest/platform từ cache, không pull trong B2-P. Kiểm mount mặc định của image không sinh tài nguyên ngoài manifest. |
| Health và headroom | Baseline health/restart GATE A và production, CPU/RAM/disk hiện hành, so với trần candidate và dư địa đã thống nhất. Dùng INF-01 cho các tín hiệu đồng nhất resource/cửa sổ, kiểm bổ sung phần còn thiếu khi phiên được xác nhận. |
| Nghiệm thu và rollback trong lượt có phép riêng | Chốt owner nonce, IDs đã tạo và staging inode. Đối chiếu set tên/ID/label ngay trước khi gỡ. Chỉ dọn container, network, volume và staging đúng manifest; dừng khi có drift. Đối chiếu lại health, restart và protected metadata. Không prune hoặc phục hồi ledger. |

Nếu được phê duyệt chạy fixture riêng, kiểm delta của Linux/KVM2: hiệu lực resource caps, no-egress, startup/health, same-route 31/46 s nếu cần đo môi trường mới, một dispatch/receipt mỗi job và rollback theo manifest. Worker restart tại `working/sending` vẫn `NOT_RUN`. Không mặc định mở rộng test đó trong B2-P. KVM2 runtime và production mutation 0, ledger/permit/key thật và provider calls 0, paid 0 USD.

**Handoff:** ChatGPT Điều phối đối chiếu `BLOCKED_PREFLIGHT_INPUT` với metadata INF-01 hoặc phiên read-only đã xác minh trước khi quyết định bước tiếp. Candidate hiện chỉ đủ căn cứ `B2P_LOCAL_RENDER_PASS`. Live `NO_GO / BLOCKED_UID_OR_MOUNT`, paid Gate B `BLOCKED_PREFLIGHT`.
