---
id: n8n-hermes-p0-sandbox-integration-2026-11-21
type: report
status: current
result: partial
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
source: live-hostinger-terminal-tests,repository-identity-report,agent-capability-reports
task: ttd-ai-p0-integration-001
---

# P0 sandbox n8n ↔ Hermes — kết quả triển khai 2026-11-21

## Tóm tắt

Kết quả tổng thể: **PARTIAL / BLOCKED_BY_BUDGET_AND_RUNTIME**.

Đã triển khai một Docker bridge riêng `ttd-ai-p0-sandbox` với `internal=true`, gắn live đúng hai container n8n và Hermes trên KVM 2. Hai dịch vụ phân giải nhau bằng DNS service alias và trao đổi trực tiếp trên mạng private, không đi qua host-published port. Không restart/recreate container, không đổi firewall, public port, DNS, credential hay resource U4S `ttdnew.tech`; downtime bằng 0 và số lần restart vẫn bằng 0.

Luồng AI E2E thật **chưa chạy**. Image Hermes hiện tại vẫn chỉ expose dashboard/control API; đường `/v1/models` private redirect về dashboard thay vì trả API inference. n8n MCP vẫn disabled và không có workflow sandbox đang hoạt động. Mặt khác, provider/model và trần chi phí chưa được phê duyệt. Theo GATE-COST, không gọi model và không tạo PASS giả.

Bằng chứng máy đọc đã khử định danh: [TTD-AI-P0-INTEGRATION-001 evidence](evidence/2026-11-21-ttd-ai-p0-integration-001.json).

## Gate trước thay đổi

| Gate | Kết quả | Bằng chứng |
|---|---|---|
| `GATE-ID` | **PASS** | Báo cáo định danh mới nhất xác nhận `ttdnew.tech` là U4S Hermes riêng; KVM 2 là target P0 độc lập, không có bằng chứng dùng chung container/volume/backend |
| `GATE-CHANGE` | **PASS cho thay đổi network-only** | Hai container running, restart 0, health nội bộ 200; network P0 chưa tồn tại; còn khoảng 85 GB đĩa; rollback không cần restart |
| `GATE-COST` | **BLOCKED cho inference** | Runtime có dấu hiệu provider credential được cấu hình nhưng không có model, đơn giá hoặc hạn mức đã duyệt; số API call tính phí thực tế bằng 0 |

Compose/config Hermes được sao lưu trong thư mục chỉ root trên VPS; checksum backup PASS. Docker label của n8n trỏ tới một compose path hiện không còn trên filesystem, nên không sửa/recreate compose n8n. Dữ liệu n8n không bị thay đổi, vì vậy không tạo bản sao dữ liệu không cần thiết. Rollback script đã được tạo, đặt quyền root-only và kiểm tra cú pháp PASS.

Một helper container Alpine read-only, `--rm`, được dùng để xác nhận volume n8n có SQLite và dung lượng khoảng 6.5 MB; không có container/service helper tồn tại sau phép thử. Image cache không được coi là thành phần P0.

## Thay đổi đã thực hiện

1. Tạo network `ttd-ai-p0-sandbox`:
   - driver `bridge`
   - `internal=true`
   - scope local
   - label task/sandbox để nhận dạng
2. Gắn n8n với alias `n8n-p0`.
3. Gắn Hermes với alias `hermes-p0`.
4. Giữ nguyên hai bridge Compose cũ để không cắt admin access hoặc gây downtime.

Không có public port mới. Các host-published port cũ chưa được thay đổi vì việc thu hẹp bề mặt public là change batch khác cần đường truy cập thay thế và phê duyệt riêng.

## Topology sau thay đổi

```text
n8n container -------- ttd-ai-p0-sandbox (internal bridge) -------- Hermes container
   |                                                                  |
bridge Compose cũ                                             bridge Compose cũ
   |                                                                  |
admin access hiện hữu                                         admin access hiện hữu
```

Service-to-service P0 dùng alias private. Public/host port chỉ được probe để xác nhận admin access sau thay đổi, không được dùng cho bài test private hai chiều.

## Ma trận kiểm thử live

| Test ID | Phép thử | Kết quả | Trạng thái |
|---|---|---:|---|
| `P0-ID-001` | U4S `ttdnew.tech` tách biệt KVM 2 | xác nhận theo báo cáo identity mới nhất | **PASS** |
| `P0-NET-001` | Network private tồn tại và có đúng hai container | `internal=true`, 2 attachment | **PASS** |
| `P0-N2H-DNS-001` | n8n gọi Hermes bằng alias private | HTTP 302 về login, chứng minh DNS/transport hoạt động | **PASS** |
| `P0-N2H-AUTH-NEG-001` | n8n gọi API Hermes bảo vệ khi thiếu auth | HTTP 401 | **PASS** |
| `P0-N2H-INFERENCE-001` | n8n gọi candidate `/v1/models` private | HTTP 302 về dashboard, không phải inference API | **BLOCKED** |
| `P0-H2N-HEALTH-001` | Hermes gọi n8n health bằng alias private | HTTP 200 | **PASS** |
| `P0-H2N-MCP-001` | Hermes gọi n8n MCP bằng alias private | HTTP 404, MCP disabled | **BLOCKED** |
| `P0-POST-HEALTH-001` | n8n readiness sau thay đổi | HTTP 200 | **PASS** |
| `P0-POST-HEALTH-002` | Hermes dashboard sau thay đổi, follow redirect | HTTP 200 | **PASS** |
| `P0-POST-RUNTIME-001` | restart/critical log sau thay đổi | restart 0; không có match fatal/panic/OOM trong cửa sổ kiểm tra | **PASS** |

HTTP 302 ở root Hermes là hành vi dashboard yêu cầu login, không phải lỗi transport. HTTP 401 xác nhận lớp auth chặn request thiếu credential. Không truyền admin credential Hermes sang n8n vì credential đó không được dùng làm inference service token.

## E2E và schema dự kiến

Không có execution `n8n → Hermes reasoning thật → n8n callback` trong lần này. Hai blocker độc lập:

1. Hermes Hostinger image không expose private agent inference API; `/v1/*` rơi về dashboard.
2. n8n instance-level MCP vẫn disabled và chưa có đúng một workflow sandbox có auth.

Schema đề xuất cho lần test sau:

```json
{
  "task_id": "p0-fake-ads-001",
  "correlation_id": "generated-per-run",
  "input": {"channel": "ads", "spend": 100, "clicks": 10},
  "status": "succeeded|failed|blocked",
  "timings_ms": {"total": 0, "reasoning": 0, "callback": 0},
  "result": {
    "summary": "string",
    "signals": ["string"],
    "recommendations": ["string"]
  },
  "result_hash": "sha256",
  "error": null
}
```

Test kế tiếp phải có token service riêng, validation input/output, timeout, invalid JSON, retry hữu hạn và idempotency theo `task_id`; không dùng admin dashboard cookie cho inference.

## Rollback

Rollback đã chuẩn bị trên VPS và không phụ thuộc compose:

1. Disconnect n8n khỏi đúng network `ttd-ai-p0-sandbox`.
2. Disconnect Hermes khỏi đúng network đó.
3. Xóa network khi không còn attachment.
4. Kiểm tra lại readiness/dashboard và restart count.

Script đã qua `sh -n`; backup config Hermes đã qua checksum. Chưa thực thi rollback vì thay đổi đang healthy và là nền cần thiết cho lần P0 tiếp theo.

## Phối hợp tác nhân

- **Hostinger Agent:** dùng báo cáo identity và account inventory đã push làm bằng chứng có thẩm quyền cho resource boundary, backup/firewall và phạm vi hPanel; không lặp lại các probe identity đã đủ bằng chứng.
- **Hermes:** dùng capability profile/report mới nhất để chốt rằng WebUI reasoning khác với VPS dashboard runtime, inference API và n8n MCP chưa được chứng minh. Không gọi Hermes/LLM để tránh phí chưa duyệt.
- **Codex:** thực hiện live preflight, network change, negative auth, private DNS hai chiều, post-health, rollback preparation và tài liệu hóa.

Không gửi tin nhắn đại diện, không tạo account/key, không thay quyền và không dùng connector business.

## Đối chiếu acceptance

| Tiêu chí | Kết quả |
|---|---|
| Identity đúng target | **PASS** |
| n8n/Hermes healthy, admin access duy trì | **PASS** |
| Private DNS và auth enforcement | **PASS** |
| n8n gọi agent reasoning thật private | **BLOCKED_BY_RUNTIME_AND_BUDGET** |
| Hermes gọi đúng một workflow n8n | **BLOCKED_BY_MCP/WORKFLOW** |
| Error/rollback/post-health | **PARTIAL PASS**: negative auth/MCP, rollback chuẩn bị, health PASS; chưa test timeout/invalid JSON/retry của E2E |
| Không thay business account/publish/phí | **PASS** |

## Quyết định cần phê duyệt

1. Chọn cách cung cấp Hermes inference private: bật upstream API server trên runtime phụ/adapter cô lập, hay dùng image khác đã pin digest; không thay image chính trong P0 hiện tại.
2. Chọn provider/model và trần chi phí theo job/ngày; cho phép đúng một fake-data inference call sau khi biết giá.
3. Cho phép bật n8n MCP và expose đúng một workflow `fake-ads-audit-v1`, hoặc chọn authenticated webhook/REST; cần maintenance plan nếu thay đổi yêu cầu restart.
4. Sau E2E PASS, quyết định có chuyển cấu hình network vào Compose để tồn tại qua recreate. Hiện network attachment live sẽ mất nếu container bị recreate.
