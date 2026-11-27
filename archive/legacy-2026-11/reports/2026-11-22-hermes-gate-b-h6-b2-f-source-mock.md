---
id: hermes-gate-b-h6-b2-f-source-mock-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-F — provider lane source và P0 v1 writer

**ACKNOWLEDGED / B2_F_SOURCE_MOCK_PASS / VERIFIED_OFFLINE_MOCK.** Phê duyệt `2056d6236507a31753099c2a4354de7bbcfc99ca`. ACK AGENTS, Workflow §§7–10, Repository Security, STATE, CATALOG, hồ sơ Codex, toàn bộ task và ADR-P0-003 tại `e2bc9740e51370b761d73a5fa9198e4aefea1a22`. Workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. Task blob của base khớp phê duyệt. B2-B và B2-E được giữ làm baseline lịch sử cho layout, cách ly và KVM2 mock. [Review B2-E](2026-11-22-hermes-gate-b-h6-b2-e-chatgpt-review.md).

## Mã đã tích hợp

- [Guard](../sandbox/p0-hermes-gate-a/guard.py) và [provider lane](../sandbox/p0-hermes-gate-a/h6_provider.py) dùng chốt `LIVE_ENABLED = False`; biến môi trường không thể mở chốt. Yêu cầu mode real với bản build hiện tại bị chặn trước khi đọc khóa, ledger hoặc tạo kết nối. Mode sai hoặc trộn mock cấu hình bị chặn. Nhánh provider tách khỏi `MOCK_URL`.
- [Writer P0 v1](../sandbox/p0-hermes-gate-a/h6_p0.py) chỉ nhận `snapshot`, `admit` và `settle` qua socket/domain HMAC riêng, với `SO_PEERCRED` UID/GID `0:0`, nonce hai bên và chữ ký gắn request/ACK. Writer kiểm rootfs RO, cap sets bằng 0, no-new-privileges, chỉ loopback và không có Docker socket/provider credential trước startup. Writer yêu cầu mount RW private tại đúng thư mục, ledger/lock root-only có sẵn và fixture marker vắng. Guard từ chối mount ledger trực tiếp.
- [Ledger transaction](../sandbox/p0-hermes-gate-a/one_shot.py) giữ lock inode của P0/Level 2, consume permit và reserve 0,0035 USD trong một commit trước ACK. Scope ràng buộc task, SHA key theo quy ước hiện có của bridge, model, digest byte cuối, count đã duyệt, Standard, tối đa 600 output và quote còn hiệu lực. `approval_sha256` là tham chiếu hồ sơ đã duyệt do quy trình bên ngoài cung cấp. Writer kiểm trường scope, thời hạn và caps, còn việc xác minh hồ sơ count/pricing phải hoàn thành trước khi cấp permit thật ở gate riêng. H6 fsync file và thư mục. Kill switch giữ ON.
- Guard khóa canonical bytes sau policy enforcement, bỏ cache key động, ép Standard, `store=false`, một user turn dạng text, không tools. Sau ACK đúng digest, transport có một CONNECT tunnel tới đích cố định, TLS xác minh hostname/certificate và đúng một `POST /v1/responses`, với timeout và response-size bound. Kết nối proxy/TLS được kiểm tại ranh giới cấu hình bằng recorder. HTTP loopback thực kiểm byte, framing JSON/SSE và đường request/response. [Python CONNECT](https://docs.python.org/3/library/http.client.html#http.client.HTTPConnection.set_tunnel) · [Responses contract](https://developers.openai.com/api/reference/resources/responses/methods/create).
- Usage hợp lệ được hạch toán theo giá dự kiến bên trong reserve và lưu response-ID hash, served model, counts, trạng thái và `invoice_status=unreconciled`. HTTP response thành công chỉ trả sau ACK settlement. Redirect, HTTP lỗi, timeout, payload không hoàn chỉnh hoặc usage vượt approved count giữ reserve và ghi `outcome_unknown` khi writer còn phản hồi. Writer chết để lại `inflight` đã consume; mất ACK settlement khiến Guard từ chối trả thành công. Không retry, fallback hoặc refund. Response terminal `incomplete` có usage hợp lệ vẫn được hạch toán nhưng Guard không trả thành công.

## Offline evidence

Docker Desktop Linux Engine 29.4.3, Compose 5.1.4. [Compose](../sandbox/p0-hermes-gate-a/compose.h6-b2-f-offline.yaml) render đúng một service, 13 bind chỉ đọc cho mã Python, tmpfs, UID 0, cap_drop ALL, rootfs RO, network none, và không gắn credential/provider/ledger thật. Có thể tái lập bằng `docker --context desktop-linux compose -f sandbox/p0-hermes-gate-a/compose.h6-b2-f-offline.yaml run --rm --no-deps -T tests`. [Test source](../sandbox/p0-hermes-gate-a/h6_b2f_test.py) · [Evidence JSON](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-f-source-mock.json).

| Kiểm tra | Kết quả |
| --- | --- |
| Startup và scope | Real CLI/Guard bị hard lock. Fixture giả kiểm key, ledger, permit vắng, lock vắng/sai mode, marker mock, quote/digest/count/caps sai, generic op, sai HMAC domain/key, nonce replay và ACK ký cho request khác. Ca bị chặn không mở transport. |
| Reserve và concurrency | 4 request qua Guard, 1 signed admission được dùng và đúng 1 POST tới stub. Stub so từng byte với wire đã freeze và kiểm ledger đã commit trước khi trả. Adapter Level 2 nguyên bản tranh chấp đúng device/inode lock trên P0 v1 giả. Cập nhật đồng thời và trường lạ được giữ; lock giữ inode qua replace. Replay sau restart bị chặn. |
| HTTP và settlement | JSON Content-Length, SSE Content-Length và SSE chunked đạt. 302, 429, timeout, truncation, thiếu terminal SSE và count vượt quote mỗi ca chỉ thấy một POST, 0 redirect hit/fallback. Settlement lặp y hệt giữ nguyên bytes, sai digest/usage bị chặn. Response không hoàn tất với usage hợp lệ được ghi, Guard trả 503. |
| Crash và rollback | Crash trước rename và sau file+directory fsync đều mất ACK, 0 POST. Crash trước rename giữ bytes cũ. Crash sau fsync giữ reserve và `inflight`. Writer chết sau POST cũng giữ `inflight` với đúng 1 POST. Dừng/restart writer rồi kiểm bytes và inode trên fixture, không khôi phục snapshot cũ. |
| Callback và hồi quy | Handler bridge hiện hữu với Hermes/n8n giả trả 200, đúng một callback xác thực, 0 callback thêm khi replay. Hồi quy phần mã dùng chung B2-D, Stage A và B2-A chạy offline. B1 và B2-E không chạy lại trên KVM2. |

## Delta đề xuất cho một gate KVM2 riêng

| Thành phần | Delta cần trình duyệt |
| --- | --- |
| `guard` hiện hữu | Gỡ ledger bind chỉ đọc cũ. Bind private IPC vào `/opt/ttd/h6-b2f-live-ipc` RO và key riêng vào `/run/h6-b2f-live-auth` RO. Credential provider RO ở Guard duy nhất qua mount H4 đã phê duyệt. Giữ đường nội bộ từ Hermes và đường outbound duy nhất tới allowlist CONNECT proxy. Mode và runtime build chỉ bật ở gate được phê duyệt. |
| `h6-writer` mới | UID/GID `0:0`, cap_drop ALL, no-new-privileges, rootfs RO, network none. Một bind RW `rprivate` của đúng thư mục P0 đã duyệt tại `/opt/ttd/p0-ledger`; private IPC RW, key IPC RO, code RO. Giữ lock inode và root:root 0700/0600. Writer chỉ chạy entrypoint `--b2-f-real` sau gate. |
| Level 2, Hermes, bridge, production | Giữ topology và scope hiện hữu. Xác minh restart policy và live inode/mount read-only trước mọi quyết định. Kiểm lại deny-bypass và runtime callback nếu code/topology thay đổi. |

Render đầy đủ overlay tương lai với source/mount đã duyệt, đối chiếu lại H4 backup, health/restarts, userns, mode/ACL, inode/mount propagation và nguồn credential. Cấp key IPC khác fixture qua kênh bảo mật. Đối chiếu model/quota/tier/pricing và provider count cho SHA byte cuối. Count 723 ở đây chỉ là input fixture. TLS tunnel live, deadline của Hermes khi Guard buffer SSE đến settlement, đường Hermes/n8n thật và mất điện chưa được đo. Không áp dụng file Compose live trong giai đoạn này. Khi rollback, cô lập writer, phục hồi cấu hình đã kiểm, giữ ledger và lock cùng phần ghi đã commit. Outcome chưa rõ phải được đối soát trước mọi bước tiếp theo.

`from_agent: codex` · `next_owner: chatgpt` · `handoff_state: PREPARED_FOR_OWNER_FORWARD`. Live shared ledger giữ `BLOCKED_UID_OR_MOUNT`, paid GATE B giữ `BLOCKED_PREFLIGHT`. 0 KVM2 apply, real ledger/lock/permit/key operations, OpenAI API, production hoặc paid.
