---
id: hermes-gate-b-h6-b2-g-kvm2-fake-tls-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-G — CONNECT/TLS giả trên KVM2

**ACKNOWLEDGED / H6_B2_G_KVM2_FAKE_TLS_PASS / VERIFIED_KVM2_MOCK / ROLLBACK_PASS.** Phê duyệt `76276c282ad33ef824393ba5428ed4eee8dd9698`. ACK AGENTS, Workflow §§7–10, Repository Security, STATE, CATALOG, hồ sơ Codex, toàn bộ task và ADR-P0-003 tại `c401f35dbf8da5ca6176cd7da54bec482381661f`. Workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. Task blob của base trùng bản phê duyệt. [Review B2-F](2026-11-22-hermes-gate-b-h6-b2-f-chatgpt-review.md).

## Cổng pre-up

- KVM2 dùng Docker Engine 29.9.2, Compose 5.6.1 và ext4. Kiểm rollback B2-E sạch. Hai file backup H4 khớp byte và render, hash Guard đang chạy khớp. Baseline GATE A/production, mount, ledger và lock chỉ được kiểm qua Docker inspect và metadata. Production n8n/Hermes HTTP 200/200.
- Dùng image cache đã ghim từ B2-E với `pull_policy: never`, bảy blob runtime B2-F từ `b670a65`, helper baseline B2-E ghim từ `d32aff1`, cùng [runner](../sandbox/p0-hermes-gate-a/h6_b2g_rehearsal.py) và [fixture](../sandbox/p0-hermes-gate-a/h6_b2g_fixture.py) tại `fbe3fa6`. Bản build B2-F vẫn khóa tuyến live; Guard test chỉ được cấp factory HTTPS tới proxy giả. Mã nguồn runtime B2-F giữ nguyên.
- Standalone Compose kiểm đủ profile và render lần hai ngay trước up. Kết quả có 4 service, 2 bridge mới `internal` ở gateway mode `isolated`, 0 network ngoài, 0 port publish, 0 Docker volume mới và 0 xung đột với container/network/mount hiện hữu. Render SHA-256 `e8fec81c08f310986976dcb40dc565c03079b2f5ae5e0e43c90c8685bb0e41a9`. Front chỉ Guard và proxy, back chỉ proxy và provider giả. Writer dùng `network_mode: none`. Inspect và phép kiểm trong namespace xác nhận layout đúng render, UID/GID `0:0`, các cap set bằng 0, no-new-privileges, rootfs RO, không default route, không Docker socket/mount ledger/provider-key thật. Khóa IPC giả RO chỉ ở Guard/writer. CA ngắn hạn sinh trong thư mục riêng, CA private key chỉ ở staging, leaf key chỉ ở provider giả, Guard chỉ đọc CA cert. [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-g-kvm2-fake-tls.json).

## Kết quả ma trận

| Phép thử | KVM2 quan sát được |
| --- | --- |
| TLS hostname và chain | Hostname khớp SAN và synthetic CA hợp lệ, thực tế negotiated TLSv1.3. Wrong CA, hostname không khớp và leaf hết hạn đều bị `SSLCertVerificationError` trước POST. Client luôn bật hostname check và `CERT_REQUIRED`. |
| CONNECT và exact bytes | Bốn admission song song ở ca thành công cho một ACK hợp lệ, **một CONNECT và một POST**. Guard đọc signed snapshot xác nhận reserve 0,0035 đã có trước khi tạo kết nối. Audit độc lập của proxy/provider ghi 13 CONNECT cho 13 ca, cộng một CONNECT unapproved bị chặn. Bảy ca tới POST, mỗi ca đúng một lần và cùng SHA-256 `b2101473dd51b957f3896619ca5be6134c8ddb5e512179f8798bf417a0a4d578`, 239 byte. Sáu ca lỗi TLS/proxy không có POST. |
| Proxy reject, drop và TLS timeout | CONNECT 403, proxy ngắt trước khi trả status và TLS handshake timeout đều fail closed. Ca timeout đo 0,667 giây. Không thử lại CONNECT hoặc POST. |
| HTTP/SSE và slow-drip | SSE Content-Length và chunked hợp lệ được settle. 302, body ngắn hơn khai báo, SSE thiếu terminal và chunk lỗi đều trả lỗi. 302 không theo `Location`. Slow-drip nhận dữ liệu liên tiếp, timer ngắt TLS, Guard trả 503 sau 0,816 giây với deadline fixture 0,8 giây. Stub ghi 9 byte gửi rời trước khi kết nối đóng. |
| Unknown/replay | Hai ca hợp lệ `usage_recorded`. 11 ca lỗi `outcome_unknown`, giữ nguyên reserve và permit đã consume, 0 usage estimate ghi thêm. Lock fixture giữ nguyên device/inode. Replay tất cả ca bị chặn trước transport. Không fallback sang mock route cũ. |
| No-bypass | Guard không thể TCP trực tiếp tới IP của fake TLS provider phía back, địa chỉ documentation ngoài project hoặc hai địa chỉ của proxy hiện hữu. Fake CONNECT proxy từ chối hostname ngoài allowlist mà không forward. Writer chỉ loopback. |
| Rollback | Gỡ đúng bốn container và hai bridge thuộc project, xóa fixture, ledger giả và khóa/chứng thư tổng hợp. Inventory hiện hữu khớp pre/post, production HTTP vẫn 200/200. Parent, ledger và lock thật khớp metadata đã đo, bao gồm device/inode, owner/mode, ACL, kích thước, mtime và ctime. Không mở nội dung thật. |

Lần chạy đầu đã tự dọn sau khi phép thử slow-drip kỳ vọng kiểu lỗi TCP quá hẹp. Lần cuối quan sát trực tiếp timer shutdown, thời gian và nhật ký stub để phân biệt deadline thực với lỗi mạng sớm. TLS trả `BrokenPipeError` sau timer shutdown trong lần PASS. Runtime B2-F không cần sửa để đạt phép đo này.

## Bàn giao ChatGPT

`from_agent: codex` · `next_owner: chatgpt` · `handoff_state: PREPARED_FOR_OWNER_FORWARD`. Đề nghị đối chiếu code fixture, audit counts và snapshot rollback trong evidence. B2-G kiểm chứng tunnel với trust store và hai bridge giả trên KVM2. Tuyến proxy live, OpenAI, key thật, cấp permit thật, count của body live, tương thích deadline Hermes/n8n và mất điện vẫn ngoài bằng chứng này.

Live shared-ledger apply giữ `BLOCKED_UID_OR_MOUNT`, paid GATE B giữ `BLOCKED_PREFLIGHT`. Có 0 lần đọc nội dung hoặc sửa ledger/lock/key/permit thật, 0 OpenAI API, 0 paid, 0 production mutation.
