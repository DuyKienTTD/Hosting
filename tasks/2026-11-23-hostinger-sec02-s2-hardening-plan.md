---
id: sec02-s2-hardening-gates-2026-11-23
type: task
status: draft-for-review
updated_at: 2026-11-23
sensitivity: public-redacted
owner: hostinger-agent
executed_by: hermes-webui
next_owner: chatgpt
---
# SEC-02/S2 — ACK và phạm vi thực hiện

- **ACK:** `EXECUTE SEC-02/S2` theo [PR #11 comment 7091865470](https://github.com/DuyKienTTD/Hosting/pull/11#issuecomment-7091865470). Owner được chỉ định trong chỉ thị là Hostinger Agent; **tác giả thực tế của branch này là Hermes WebUI** theo lời chuyển tiếp của người dùng. Không tự nhận Hostinger Agent đã ACK, không có phép đo hPanel/VPS mới.
- **FIRST_ACTION:** fetch `origin/main`, PR #11 HEAD `142f6dc5dbc033554bd0b43e3444ea0d59f60d96`, PR #9/#17/#8/#22/#24/#6, đọc rules và findings F01–F07; kiểm tra không có branch/path SEC-02/S2 trùng.
- **BASE_SHA:** `e385c1bea2070973e3007e5717f7e980348d6ab3`; rules blobs `AGENTS=cb6a8af9`, `AGENT_WORKFLOW=69ec0db9`, `REPOSITORY_SECURITY=c24d6080`, `STATE=c8e8941a`, `CATALOG=719c9c5d`, Hostinger profile `15cade1f` (đầy đủ qua `git rev-parse`). `main` có AGENT_WORKFLOW §§1–7, không suy diễn §§8–10 ở main.
- **READ_SET:** task comment, SEC-02/S1, INF-01 PR #9, INF-01B PR #17, Work WS-02 PR #8, OPS S1/S2 PR #22/#24, PR #6, rules/profile/current state. **Historical evidence:** SEC S1 finding matrix design-only; INF-01B snapshot read-only; OPS S1/S2 synthetic only. Chỉ test policy S2 delta, không chạy lại suite khác.
- **WRITE_SET:** task này, `runbooks/sec02-s2-controlled-hardening-gates.md`, `reports/2026-11-23-hostinger-sec02-s2-tabletop.md`, `reports/evidence/2026-11-23-hostinger-sec02-s2-tabletop.json`, optional `sandbox/sec02-hardening-fixtures/**` trên `hostinger/sec-02-s2-hardening-gates-2026-11-23`. Không sửa main, S1, OPS, B2-P, STATE/CATALOG/CHANGELOG.
- **INVARIANTS:** F01–F07 ID/severity/provenance giữ từ S1; mọi work order `NOT_AUTHORIZED`. `PASS_TABLETOP` không phải thực thi kiểm soát production hay restore. Một phê duyệt không hợp lệ cho work order khác.
- **STOP:** mọi lệnh live VPS/hPanel/production, Docker/Compose, firewall/UFW/SSH/TLS/port, secret/credential, backup/restore, paid provider, merge. Không có chi phí. Mọi thao tác thật cần owner và A0 phê duyệt riêng qua change ID, reviewer độc lập, đường khôi phục đã xác minh.
- **PASS:** 7 finding, ít nhất 4 work order tách biệt, DAG và fail-stop, ít nhất 6 ca tabletop/test offline, SHA/blob remote xác minh. **NEXT_OWNER:** ChatGPT Điều phối và Hostinger Agent thực thụ rà soát độc lập trước A0.
