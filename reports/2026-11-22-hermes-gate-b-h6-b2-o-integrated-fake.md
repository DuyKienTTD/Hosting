---
id: hermes-gate-b-h6-b2-o-integrated-fake-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# H6 B2-O — Deadline và callback tự động trên tuyến fake local

**ACKNOWLEDGED.** Đặc tả tại `40e672b14f310af76f39fa28afcf7eac1a76b146`. ACK AGENTS, Workflow §§7–10, Security, STATE/CATALOG, hồ sơ Codex, task và ADR-P0-003 tại `a343f184786dc6d71d9a3ad1a22a813243202f6e`. Tái sử dụng deadline và topology từ B2-H, hợp đồng async/receipt từ B2-I/K, cùng image pin và provenance từ B2-N. Đối chiếu Work PR #4 tại `00f5649`. [Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [B2-H](2026-11-22-hermes-gate-b-h6-b2-h-read-only.md) · [B2-N](2026-11-22-hermes-gate-b-h6-b2-n-offline-contract.md) · [Work PR #4](https://github.com/DuyKienTTD/Hosting/pull/4).

## Tuyến đã chạy

1. n8n nhận webhook local và chuyển job sang async adapter. HTTP node giữ timeout 30 s và trả lại HTTP 202 của adapter. Adapter lưu job trên SQLite trước khi ACK. Worker dùng HTTP client của `bridge.py` và Idempotency-Key theo task để gọi `/v1/runs` trên Hermes auxiliary đã ghim. Worker lưu run ID và binding job/task/correlation/run hash/request hash trên SQLite trước khi poll API Hermes. Evidence chỉ ghi hash của run ID.
2. Hermes gọi `guard.Handler` trên mạng riêng. Guard dùng `h6_provider.Lane` và `post_once` để đóng băng payload, đợi ACK reserve và gửi đúng một POST. Writer fixture lưu reserve và kết quả vào SQLite riêng, trả ACK qua HTTP nội bộ có bearer giả. Kết nối trực tiếp tới fake recorder qua mạng riêng, dùng budget connect 5 s và response 45 s của transport H6. `LIVE_ENABLED=False`.
3. Worker ghi outcome rồi gửi callback qua n8n candidate. Webhook kiểm bearer. Receiver kiểm HMAC trên event, độ mới và toàn bộ binding, commit một receipt vào SQLite, ký receipt bằng khóa riêng và trả ACK. Worker đối chiếu chữ ký và digest trước khi đánh dấu `delivered`. Driver chỉ submit và đọc trạng thái. [Hermes Runs API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server) · [n8n Respond to Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/).

Bridge được đo dưới dạng async adapter của B2-O. Cửa sổ poll đồng bộ 20 s của bridge gốc không chạy trên tuyến này. Giới hạn quan sát 60 s của worker kế thừa budget fixture B2-I. HTTP 30 s của n8n áp dụng cho admission. Nhánh callback của candidate chuyển sang receipt riêng và chấp nhận `outcome_unknown`. Với topology này, proxy CONNECT, TLS và idle 30 s của proxy đều `NOT_MEASURED`. Writer SQLite là fake, nên phép thử không xác minh IPC/P0 ledger thật. Các mốc Hermes là thời điểm adapter nhận HTTP 202 và quan sát trạng thái từ API build ghim, với độ phân giải poll khoảng 150 ms.

## Lệnh tái hiện

```powershell
python -X utf8 -B sandbox/p0-hermes-gate-a/h6_b2o_run.py --evidence "$env:TEMP/ttd-h6-b2o-evidence.json"
```

Project Docker Desktop local `ttd-b2o-local` dùng tám service, bảy mạng nội bộ và sáu volume riêng. Render all-profile và inspect lúc chạy xác minh mount, image pin, owner, rootfs RO, zero host port và không có default route ở các service. Hermes không resolve được provider hoặc writer, chỉ Guard có mạng nối tới cả recorder và writer. Mọi bind đều chỉ đọc và lấy từ thư mục fixture tạm. Evidence kèm projection Compose khử nhạy cảm, render lại từ cùng source sau lượt chạy. [Compose networking](https://docs.docker.com/compose/how-tos/networking/) · [Runner](../sandbox/p0-hermes-gate-a/h6_b2o_run.py) · [Fixture](../sandbox/p0-hermes-gate-a/h6_b2o_services.py).

## Kết quả `B2O_INTEGRATED_FAKE_PASS`

| Đo trên cùng tuyến local | Ca 31 s | Ca 46 s |
| --- | --- | --- |
| n8n trả HTTP 202, tính từ lúc gửi webhook | 0,143 s | 0,110 s |
| Adapter / Hermes admission | 202 / 202 | 202 / 202 |
| Tầng cắt trước, tính từ lúc Guard kết nối | Hoàn tất. First byte ở 31,011 s | Timer phản hồi H6 của Guard ở 45,001 s. Đọc socket kết thúc ngay sau timer, trước first byte |
| Guard HTTP / trạng thái Hermes qua API | 200 / `completed` | 503 / `failed` |
| Worker callback / receipt commit, tính từ webhook | 200 / 33,025 s | 200 / 45,424 s |
| Outcome đã lưu | `mock_succeeded` | `outcome_unknown` |
| Dispatch / receipt / settlement thành công | 1 / 1 / 1 | 1 / 1 / 0, reserve giả giữ `held` |

Mỗi trace khớp binding job/task/correlation/run hash/request hash giữa adapter và receipt. Digest của byte POST cuối khớp giữa reserve của writer, transport tại Guard và recorder. Hai ca đều ghi reserve commit và ACK trước connect/POST. Sau cutoff, fake provider thử trả ở mốc 46,000 s kể từ khi ghi dispatch. Kết nối đã đóng và receipt `outcome_unknown` đã commit trước lần trả đó. Không có callback do driver chèn. Đọc lại SQLite cho thấy một receipt mỗi job sau khi restart riêng receiver, cùng nội dung đã ký và cùng outcome. [Evidence JSON](evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-o-integrated-fake.json).

Cleanup xác minh owner label trước khi dọn. Không còn container, volume hoặc network của project. KVM2, production, ledger/permit/key thật, provider API và paid inference đều có số thao tác bằng 0. Chi phí 0 USD. `LIVE_INTEGRATION_NO_GO / BLOCKED_UID_OR_MOUNT / BLOCKED_PREFLIGHT`. Chuyển ChatGPT nghiệm thu trên [PR #5](https://github.com/DuyKienTTD/Hosting/pull/5), `PREPARED_FOR_OWNER_FORWARD`.
