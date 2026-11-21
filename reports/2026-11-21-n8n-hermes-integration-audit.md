---
id: n8n-hermes-integration-audit-2026-11-21
type: report
status: current
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: TTD-AI-PLATFORM-AUDIT-001
source: live-hostinger-terminal-tests,repository-inventory,official-vendor-documentation
---

# Kiểm toán n8n ↔ Hermes và kiến trúc AI Automation — 2026-11-21

## Tóm tắt điều hành

**Kết quả tổng thể: PARTIAL.** Hai dịch vụ đang hoạt động độc lập, ổn định và có thể chạm nhau theo cả hai chiều qua các cổng đã publish trên host. Tuy nhiên, chưa có một đường tích hợp AI production-ready và chưa thể hoàn thành luồng end-to-end trong phạm vi audit an toàn.

Điểm đo live chính: **2026-11-21 11:53:25 ICT** (`04:53:25Z`), từ Hostinger Web Terminal trên chính VPS. Không ghi IP, hostname, thông tin xác thực hoặc log thô vào repository công khai.

| Hạng mục | Kết quả | Bằng chứng ngắn |
|---|---|---|
| n8n chạy độc lập | **PASS** | `2.45.7`; `/healthz` và `/healthz/readiness` trả 200; 0 restart/OOM |
| Hermes chạy độc lập | **PASS** | `0.22.5`, upstream `bf0203a7`; dashboard health trả 200; 0 restart/OOM |
| n8n → Hermes: mạng + auth | **PASS** | API bảo vệ trả 401 khi chưa auth, login 200, sau auth trả 200 trong 146 ms |
| n8n → Hermes: suy luận AI | **BLOCKED** | Image đang chạy dashboard quản trị; không expose API `/v1/*` của Hermes upstream |
| Hermes → n8n: mạng/readiness | **PASS** | Readiness trả 200 trong 21 ms |
| Hermes → n8n: MCP chính thức | **BLOCKED** | `/mcp-server/http` trả 404 JSON `MCP access is disabled` |
| Luồng fake ads end-to-end | **BLOCKED** | n8n có 0 workflow/0 execution; MCP tắt; không có Hermes inference endpoint |
| Service discovery nội bộ | **FAIL** | Hai container ở hai bridge network khác nhau, không resolve được tên nhau |
| Production bị thay đổi | **NO** | Chỉ probe đọc và process client tạm trong container; không restart/recreate/configure |

Kết luận kinh doanh: hạ tầng hiện tại **đủ làm nền cho pilot**, nhưng chưa phải hệ thống AI Automation 24/7. Phương án đơn giản nhất là giữ n8n làm control plane, bật một đường Hermes API riêng tư có token, nối hai dịch vụ bằng một internal Docker network và triển khai một workflow sandbox có schema + human approval trước khi nối tài khoản marketing thật.

Artifact máy đọc: [bằng chứng đã khử định danh](evidence/2026-11-21-ttd-ai-platform-audit-001.json).

## 1. Phạm vi và mức tin cậy nguồn

| Nhãn | Ý nghĩa trong báo cáo |
|---|---|
| **LIVE** | Đo trực tiếp trên VPS trong đợt này |
| **INVENTORY** | Kế thừa kiểm kê 2026-11-21, không lặp lại nếu đã đủ bằng chứng |
| **DOC** | Khả năng theo tài liệu chính thức; không được coi là đã bật trên instance |
| **INFERENCE** | Suy luận kiến trúc từ bằng chứng, ghi rõ giả định |

Audit chỉ dùng phép thử đọc, endpoint health/settings, truy vấn SQLite ở chế độ read-only và client tạm thời qua `docker exec`. Không restart/recreate container, đổi network/firewall/credentials, tạo workflow, bật MCP, gọi model, publish nội dung hoặc dùng tài khoản production.

## 2. Bản đồ runtime thực tế

### 2.1 Nền tảng VPS

Theo **INVENTORY**: Hostinger KVM 2 tại Kuala Lumpur, Ubuntu 24.04.4 LTS, 2 vCPU, 8 GB RAM, gói đĩa 100 GB; filesystem `/` có 96 GiB khả dụng, 12 GiB đã dùng và 85 GiB trống. Các rủi ro SSH/XRDP, firewall và cập nhật hệ điều hành nằm trong [báo cáo bảo mật riêng](2026-11-21-vps-security-review.md).

### 2.2 Container và phiên bản — LIVE

| Thuộc tính | n8n | Hermes |
|---|---|---|
| Version | `2.45.7` | `0.22.5` (`2026.9.24`), upstream `bf0203a7` |
| Image | `docker.n8n.io/n8nio/n8n:latest` | `ghcr.io/hostinger/hvps-hermes-agent:latest` |
| Digest quan sát | `sha256:9a8d...7b5d` | `sha256:0ea6...344f` |
| Image created | 2026-10-30 | 2026-10-23 |
| Uptime | khoảng 3 tuần | khoảng 3 tuần |
| Restart policy | `unless-stopped` | `unless-stopped` |
| Restart / OOM | 0 / false | 0 / false |
| User | `node` | `root` |
| Root filesystem | ghi được | ghi được |
| Healthcheck Docker | chưa cấu hình | chưa cấu hình |
| CPU/RAM/PID limit | chưa cấu hình | chưa cấu hình |
| Storage | volume RW tại `/home/node/.n8n` | bind RW tại `/opt/data` |
| Điểm đo tải | 0.45% CPU, 374.7 MiB, 21 PID | 0.57% CPU, 435.9 MiB, 39 PID |

Digest đầy đủ có trong artifact JSON để phục vụ đối chiếu; tên tag `latest` vẫn là rủi ro drift. Python mà shell hệ thống trong image trả về và runtime được Hermes CLI báo cáo không trùng nhau; số có thẩm quyền cho ứng dụng là version/runtime do chính Hermes CLI công bố, không suy ra từ binary `python` mặc định.

### 2.3 Tiến trình và bề mặt HTTP — LIVE

**n8n** chạy `tini`, tiến trình n8n và task runner. Các endpoint `/healthz` và `/healthz/readiness` trả `200 {"status":"ok"}`. Settings công khai báo `settingsMode=public`, auth `email`, setup đã hoàn tất và SMTP chưa cấu hình.

**Hermes** image Hostinger chạy dashboard/control API. Service s6 tên `main-hermes` hiện chỉ là `sleep infinity`; dashboard mới là tiến trình phục vụ thực tế. OpenAPI của dashboard có version `0.22.5`, nhưng không có operation `/v1/chat/completions`, `/v1/responses` hoặc `/v1/runs`. Các URL `/v1/*` và `/health` không phải agent API; khi chưa auth chúng redirect về login, sau auth chúng rơi về SPA HTML.

Điểm phân biệt quan trọng:

- **LIVE:** dashboard quản trị có health/config/session/cron/webhook APIs.
- **DOC:** Hermes upstream có API server tương thích OpenAI, nhưng mặc định tắt.
- **Kết luận:** không được dùng tài liệu upstream để tuyên bố image đang chạy đã expose inference API.

### 2.4 Mạng Docker — LIVE

- Hermes ở bridge riêng `172.18.0.0/16`; n8n ở bridge riêng `172.19.0.0/16`.
- n8n không resolve được tên container Hermes; Hermes không resolve được tên container n8n.
- Các bài test chéo đi qua gateway của bridge và cổng publish trên host.

Đường này chứng minh **network reachability**, nhưng không phải thiết kế service-to-service nên giữ cho production: nó đi vòng qua cổng công khai, không có DNS dịch vụ ổn định và làm tăng bề mặt tấn công.

### 2.5 Trạng thái ứng dụng — LIVE

| Hạng mục | Giá trị |
|---|---:|
| n8n workflows / active / inactive | 0 / 0 / 0 |
| n8n executions | 0 |
| n8n credentials | 1 (không đọc loại, tên hoặc giá trị) |
| n8n instance-level MCP | disabled |
| Hermes cron jobs | 0 |
| Hermes sessions/messages | 0 / 0 |
| Hermes webhooks | disabled |
| Hermes workspaces/repos | 0 / 0 |

Không được suy ra credential n8n duy nhất thuộc connector nào. Không có connector marketing nào được xác nhận production-ready trong audit này.

## 3. Matrix kiểm thử hai chiều

### 3.1 n8n → Hermes

| Test ID | Mục đích | Input | Kết quả đã khử bí mật | Latency | Trạng thái |
|---|---|---|---|---:|---|
| `AUDIT-N2H-001` | health dashboard | GET API health | 200; version `0.22.5`; auth-required flag true | 146 ms | **PASS** |
| `AUDIT-N2H-AUTH-002` | network + auth trên API bảo vệ | GET collection cron jobs | trước auth 401; login 200; sau auth 200; JSON array, 0 job | 146 ms | **PASS** |
| `AUDIT-N2H-AI-001` | planning/inference | fake ads payload | không có endpoint agent API live để gọi | — | **BLOCKED** |

Client Node.js chạy tạm trong container n8n. Thông tin dashboard auth được đọc ephemerally từ cấu hình container, không in ra và cookie jar tạm đã xóa. Kết quả PASS chỉ áp dụng cho **dashboard transport/auth**, không chứng minh n8n gọi được mô hình AI.

Phương án thay thế khả thi là bật API server Hermes upstream (`API_SERVER_ENABLED`, bind internal-only, bearer key, concurrency limit) hoặc dựng adapter tối thiểu trước Hermes CLI. Phương án API server upstream đơn giản hơn và đã có `/v1/responses`/`/v1/runs`, nhưng quyền của nó rất mạnh, nên phải cô lập mạng và giới hạn token. Đây là `APPROVAL_REQUIRED`.

### 3.2 Hermes → n8n

| Test ID | Mục đích | Input | Kết quả | Latency | Trạng thái |
|---|---|---|---|---:|---|
| `AUDIT-H2N-001` | readiness | GET `/healthz/readiness` | 200, `{"status":"ok"}` | 21 ms | **PASS** |
| `AUDIT-H2N-MCP-001` | official instance MCP | JSON-RPC `tools/list`, kèm context fake ads | 404 JSON `MCP access is disabled` | 3 ms | **BLOCKED** |

Client Python chạy tạm trong container Hermes. JSON-RPC chứa dữ liệu giả lập `{channel: ads, spend: 100, clicks: 10}` và không có dữ liệu khách hàng.

So sánh đường tích hợp:

| Đường | Ưu điểm | Hạn chế | Quyết định đề xuất |
|---|---|---|---|
| n8n instance-level MCP | Discovery/tool schema và quyền thực thi chuẩn; Hermes có MCP client | Phải bật instance + expose từng workflow; OAuth/token cần quản trị | **Ưu tiên cho Hermes gọi workflow n8n** |
| n8n webhook/REST | Đơn giản, dễ kiểm soát schema; phù hợp event trigger | Tự xây auth, idempotency, discovery | Dùng cho inbound event và callback |
| Adapter riêng | Có thể ép schema/quyền/budget rất chặt | Thêm code phải vận hành | Chỉ dùng nếu API/MCP không đáp ứng governance |

### 3.3 End-to-end tối thiểu

**`AUDIT-E2E-001`: BLOCKED, không đánh dấu FAIL.**

Luồng mong muốn là `fake ads input → Hermes phân tích → n8n thực hiện phép xử lý sandbox → validate schema/task ID/execution`. Audit không chạy tiếp vì cùng lúc có ba blocker:

1. n8n MCP đang tắt.
2. n8n không có workflow hoặc execution để gọi.
3. Hermes image chưa expose agent inference API.

Hoàn tất test sẽ cần đổi cấu hình production, tạo workflow/credential và có thể gọi model trả phí. Cả ba đều ngoài quyền audit. Việc dừng ở đây tuân thủ scope và tránh tạo một PASS giả từ health check.

## 4. Logs, độ bền và khả năng chạy 24/7

### 4.1 Những gì đã chứng minh — LIVE

- Hai container up khoảng ba tuần, restart count 0, không OOM.
- 24 giờ gần nhất: n8n 4 dòng log, không error/warning; Hermes 2 warning `Invalid HTTP request received` đã tóm tắt, phù hợp với traffic ngoài ý muốn tới cổng public.
- Docker log driver là `json-file`.
- Không có Docker healthcheck, resource limit hoặc PID limit.
- Không có workflow, queue, retry, error workflow, alert hoặc idempotency store đã chứng minh.

### 4.2 Thiết kế vận hành tối thiểu đề xuất

- Mỗi workflow có `correlation_id` và `idempotency_key = source + object_id + time_window + action_version`.
- Validate mọi output Hermes bằng JSON Schema trước khi cho n8n chuyển bước.
- Retry exponential có jitter chỉ cho lỗi tạm thời; không retry lỗi validation/quyền.
- Error workflow chung ghi trạng thái, redacted payload hash và gửi cảnh báo; job quá hạn vào dead-letter/manual-review.
- Mọi action gây chi phí, publish, sửa website hoặc thay đổi ads phải có budget/policy gate và human approval ở giai đoạn đầu.
- Thêm Docker healthcheck, log rotation, uptime alert và watchdog kiểm tra backlog.
- Giữ SQLite cho pilot ít workflow. Chỉ chuyển n8n sang PostgreSQL + Redis queue mode khi workload đồng thời/latency/SLA thực tế chứng minh cần; queue mode với SQLite không được n8n khuyến nghị.

## 5. Media readiness VPS-first

| Hạng mục | LIVE | Đánh giá |
|---|---|---|
| Đĩa trống | 85 GiB | đủ pilot có quota, không đủ làm kho video dài hạn không giới hạn |
| FFmpeg host | không có | không dùng host làm media worker |
| FFmpeg trong n8n | không có | không encode trực tiếp trong container n8n |
| FFmpeg trong Hermes | có, `n9.0.1...` | không nên ghép render vào agent/control plane |
| `/srv` | tồn tại, rỗng, root-owned | chưa tạo `/srv/ttd-media` theo đúng scope |
| Backup ngoài VPS | chưa xác minh | Hostinger weekly backup không thay thế object/media backup có lifecycle |

Đề xuất P1 là container **media-worker** riêng, image FFmpeg được pin, mount `/srv/ttd-media` và chỉ nhận job schema rõ ràng từ n8n. Cấu trúc dự kiến: `incoming/`, `work/`, `output/`, `archive/`, `failed/`; mỗi job dùng thư mục theo `task_id`, checksum và TTL. Giữ tối thiểu khoảng 20 GiB headroom cho OS/Docker; áp quota làm việc khởi điểm khoảng 50 GiB, rồi hiệu chỉnh theo số liệu thực tế. File tạm tự dọn; sản phẩm đã duyệt được chuyển dần sang object storage có lifecycle/versioning. Đây là đề xuất, chưa tạo filesystem hay container.

## 6. Kiến trúc AI Automation đề xuất

```text
Nguồn/Schedule/Webhook
        |
        v
 n8n control plane -----> Connectors/API (read/draft first)
        |                           |
        | private HTTP/MCP          v
        v                    Website/Ads/Social
 Hermes reasoning
        |
        v
 JSON Schema + Policy/Budget Gate + Human Approval
        |
        +----> media-worker (FFmpeg) ----> /srv/ttd-media -> object storage
        |
        +----> executor workflows ------> status/callback
        |
        v
 Postgres/Data store + logs/metrics/alerts
```

### 6.1 Phân vai

| Thành phần | Vai trò | Không nên làm |
|---|---|---|
| n8n | lịch, webhook, connectors, state machine, retry, idempotency, approval, audit | suy luận tự do hoặc render nặng |
| Hermes | phân tích, lập kế hoạch, tạo nội dung có cấu trúc, chọn tool trong policy | giữ admin credentials hoặc publish không gate |
| PostgreSQL | job state, idempotency, KPI snapshots, approval/audit records | lưu raw secrets/media lớn |
| media-worker | FFmpeg, transcode, thumbnail, subtitle, package | orchestration hay reasoning |
| `/srv/ttd-media` | working set ngắn hạn có quota | archive duy nhất |
| object storage | artifact đã duyệt, lifecycle, chia sẻ/publish source | control state |
| monitoring | health, backlog, execution failures, budget, disk | chứa payload nhạy cảm chưa redaction |

### 6.2 Mạng và auth

- Thêm một external Docker bridge `ttd-ai-internal` và gắn n8n, Hermes API và media-worker; gọi bằng service DNS.
- Không publish agent API/media-worker ra Internet. UI/webhook cần công khai đi qua Nginx TLS, IP/rate limit và route allowlist.
- n8n → Hermes dùng service token riêng, không dùng admin dashboard credential.
- Hermes → n8n MCP dùng OAuth/token riêng, chỉ expose workflow được phê duyệt; workflow write/publish ở trust tier thấp và phải approval.
- Pin image bằng version/digest, chuyển Hermes khỏi root nếu image hỗ trợ, read-only root filesystem khi khả thi.

## 7. Pipeline theo nghiệp vụ

### 7.1 Video/content factory

`brief → Hermes plan/script/shot list → approval → Kling/HeyGen render → ElevenLabs voice → media-worker QA/compose → approval → n8n upload draft → publish approval → KPI feedback`

- Kling: text/image-to-video qua API; cần API package/key, kiểm soát concurrency và cost.
- HeyGen: avatar/prompt/video APIs, batch/webhook/MCP; cần API plan/key.
- ElevenLabs: TTS async/sync; metered theo usage; cần voice/IP consent và commercial-use review.
- Không connector nào trong ba dịch vụ được cấu hình hoặc test trong đợt này.

### 7.2 Quảng cáo và analytics

`Google Ads + GA4 read → normalize → Hermes diagnosis/creative hypotheses → approval → draft change set → bounded executor → post-change monitor`

Giai đoạn đầu chỉ đọc/report và tạo đề xuất. Bất kỳ thay đổi budget, bid, campaign status hoặc creative production nào cũng cần human approval, giới hạn ngân sách/ngày và rollback plan. Google Ads/GA4 chưa được nối/test.

### 7.3 Website, SEO và WooCommerce

`crawl/Search Console/GA4/WooCommerce read → issue backlog → Hermes brief/draft EN-VI → validation → WordPress draft → editorial approval → publish → regression/KPI`

Ưu tiên tạo draft, không publish thẳng. WooCommerce order/customer data phải giảm thiểu trường dữ liệu và không gửi vào model nếu không cần. WordPress/WooCommerce chưa được nối/test.

### 7.4 YouTube, TikTok, Meta

`approved master asset → platform transform → metadata/UTM → upload private/draft → human preview → schedule/publish → collect metrics`

YouTube có API upload; TikTok Content Posting cần app/scope/audit và client chưa audit bị giới hạn; Facebook Page publishing cần Page token và quyền phù hợp. Không platform account nào được nối/test. Phát hành luôn là action có phê duyệt trong P1.

### 7.5 Báo cáo

`scheduled reads → immutable daily snapshot → KPI transform → anomaly rules → Hermes narrative → schema validation → dashboard/email draft → approval/send`

Đây nên là pilot đầu tiên vì read-only, ít rủi ro và tạo dữ liệu đo giá trị trước khi cho phép write automation.

## 8. Ma trận connector và mức sẵn sàng

| Connector | Hỗ trợ kỹ thuật | Instance hiện tại | Cần làm | Chi phí/ràng buộc |
|---|---|---|---|---|
| Google Ads | API chính thức; n8n có node/HTTP | **NOT_CONNECTED / NOT_TESTED** | OAuth, developer access, test account/read scope | quota/API governance; write cần approval |
| GA4 | Data API; n8n Google Analytics | **NOT_CONNECTED / NOT_TESTED** | property + OAuth/service identity | chủ yếu quota; dữ liệu analytics |
| WordPress | REST API; n8n node | **NOT_CONNECTED / NOT_TESTED** | app password/service user, draft-only | hardening và least privilege |
| WooCommerce | REST API v3; n8n node | **NOT_CONNECTED / NOT_TESTED** | read key trước, tách order PII | bảo vệ dữ liệu đơn hàng |
| YouTube | Data API upload/metrics; n8n node | **NOT_CONNECTED / NOT_TESTED** | OAuth channel, private upload pilot | quota + review trước publish |
| TikTok | Content Posting API qua HTTP | **NOT_CONNECTED / NOT_TESTED** | registered app, approved scope, audit | unaudited client bị giới hạn visibility |
| Meta/Facebook | Graph API Page publishing qua HTTP/node phù hợp | **NOT_CONNECTED / NOT_TESTED** | app review, Page token/scopes | versioning, permission review |
| Kling | REST API | **NOT_CONNECTED / NOT_TESTED** | access/secret, async polling/webhook | paid generation/concurrency |
| HeyGen | REST/MCP, batch + webhook | **NOT_CONNECTED / NOT_TESTED** | API key/plan, consent, callback | paid video rendering |
| ElevenLabs | REST/MCP | **NOT_CONNECTED / NOT_TESTED** | scoped key, voice/IP consent | usage-based audio generation |

Credential count `1` trong n8n không thay đổi trạng thái trên vì loại/tên không được đọc và không có execution chứng minh.

## 9. Chi phí và kiểm soát ngân sách

Không khóa số tiền cụ thể vì giá/model/package thay đổi và chưa có volume business được duyệt. Dùng cost envelope:

| Nhóm | Mức tương đối | Cách kiểm soát |
|---|---|---|
| VPS hiện hữu + pilot SQLite | đã có / thấp | giữ 20 GiB headroom, resource limits |
| LLM Hermes | biến thiên theo token/tool rounds | max tokens, max concurrent runs, per-job cap |
| Kling/HeyGen | cao nhất theo video/render | approval trước call, daily cap, preview thấp trước |
| ElevenLabs | biến thiên theo text/audio | character/minute cap, cache approved voiceover |
| Object storage/egress | thấp lúc đầu, tăng theo media | lifecycle, checksum dedupe, retention classes |
| Postgres/Redis queue | hạ tầng bổ sung | chỉ thêm khi SLA/concurrency chứng minh cần |

Mỗi workflow cần khai báo `cost_class`, giới hạn request/job/ngày, estimated cost trước action và hard stop khi vượt budget. Không cho Hermes tự nâng giới hạn.

## 10. Backlog P0/P1/P2

### P0 — tạo một đường tích hợp an toàn

| Việc | Độ khó | Phụ thuộc | Tiêu chí nghiệm thu |
|---|---|---|---|
| Pin image/version và backup config | thấp | maintenance window | digest cố định, rollback được |
| Internal Docker network + bỏ đường vòng public cho S2S | vừa | network change approval | DNS service hai chiều; cổng agent không public |
| Bật Hermes API server internal-only với bearer key | vừa | chọn model/budget | `/v1/models` + fake schema request PASS, token scoped |
| Bật n8n MCP + expose 1 workflow sandbox | vừa | admin approval/token | Hermes `tools/list` và execute workflow manual PASS |
| Workflow `fake-ads-audit-v1` | vừa | hai mục trên | task ID, JSON Schema, idempotency, execution log, final state |
| Healthcheck/log rotation/error alert | vừa | alert destination | lỗi có cảnh báo và runbook, không chứa secret |
| Reverse proxy TLS và thu hẹp cổng public | vừa | domain/firewall plan | chỉ route được duyệt public |

### P1 — tạo giá trị read/draft-first

| Việc | Độ khó | Tiêu chí nghiệm thu |
|---|---|---|
| GA4 + Google Ads daily read-only report | vừa | số liệu đối chiếu UI, không mutate ads |
| WordPress SEO draft EN/VI | vừa | draft + diff + editor approval |
| Video pilot 1 asset với budget cap | cao | artifact, QA, cost và approval trace đầy đủ |
| media-worker + `/srv/ttd-media` quota | vừa | FFmpeg reproducible, cleanup/failed queue |
| YouTube private/draft upload | vừa | private asset, checksum, manual publish gate |

### P2 — mở rộng khi P1 có số liệu

- Ads bounded write automation và social scheduling theo policy.
- TikTok/Meta publishing sau app review và approval flow.
- Chuyển n8n sang PostgreSQL + Redis queue mode khi tải/SLA yêu cầu.
- Object storage, lifecycle, advanced observability và cost attribution theo chiến dịch.

## 11. Quyết định còn cần phê duyệt

1. **Hermes integration mode:** bật API server upstream internal-only (khuyến nghị) hay xây adapter riêng.
2. **n8n MCP:** cho phép bật instance-level MCP và expose đúng một workflow sandbox hay tiếp tục chỉ dùng webhook.
3. **Network/security change:** tạo `ttd-ai-internal`, đặt UI/webhook sau Nginx TLS và đóng cổng Docker public sau kiểm thử.
4. **Model + budget:** provider/model nào cho Hermes, trần chi phí theo job/ngày và ai được nâng trần.
5. **Pilot business đầu tiên:** khuyến nghị báo cáo GA4/Google Ads read-only; lựa chọn thứ hai là WordPress SEO draft.
6. **Media policy:** quota làm việc khoảng 50 GiB, giữ tối thiểu 20 GiB trống, retention và object-storage provider.
7. **Approval owners:** ai duyệt thay đổi Ads, publish website/social và chi phí video/audio.

## 12. Đã thay đổi, chỉ đề xuất và chưa kiểm chứng

### Đã thay đổi

- Không thay đổi production.
- Chỉ cập nhật repository bằng báo cáo, evidence đã redaction và trạng thái dự án.

### Chỉ đề xuất — `APPROVAL_REQUIRED`

- Bật Hermes API server, n8n MCP, tạo workflow/credentials.
- Thay Docker network, reverse proxy/firewall, healthcheck/resource limits.
- Tạo `/srv/ttd-media`, media-worker, PostgreSQL/Redis hoặc object storage.
- Kết nối/publish/mutate trên Google Ads, GA4, WordPress/WooCommerce, YouTube, TikTok, Meta, Kling, HeyGen, ElevenLabs.

### Chưa kiểm chứng

- Model/provider thực tế sẽ dùng cho Hermes API và chi phí inference.
- Khả năng OAuth/API của mọi tài khoản marketing TTD METAL.
- Backup/restore media ngoài VPS và SLA thực tế.
- Load/concurrency cần queue mode; audit không stress-test.

## 13. Nguồn chính thức dùng cho kiến trúc

- [n8n instance-level MCP](https://docs.n8n.io/connect/connect-to-n8n-mcp-server/)
- [n8n queue mode](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode.md)
- [Hermes API server](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/api-server.md)
- [Hermes programmatic integration](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/programmatic-integration.md)
- [Hermes MCP client](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/mcp.md)
- [Google Ads API](https://developers.google.com/google-ads/api)
- [GA4 Data API](https://developers.google.com/analytics/devguides/reporting/data/v1/basics)
- [WordPress REST API](https://developer.wordpress.org/rest-api/using-the-rest-api/)
- [WooCommerce REST API v3](https://developer.woocommerce.com/docs/apis/rest-api/v3/)
- [YouTube video upload](https://developers.google.com/youtube/data/reference/rest/v3/videos/insert)
- [TikTok Content Posting API](https://developers.tiktok.com/docs/en/content-posting-api-get-started)
- [Facebook Page publishing](https://developers.facebook.com/docs/graph-api/reference/page/feed/)
- [Kling AI API specification](https://docs.qingque.cn/d/home/eZQDkhg4h2Qg8SEVSUTBdzYeY)
- [HeyGen developer platform](https://developers.heygen.com/)
- [ElevenLabs Text to Speech](https://elevenlabs.io/docs/overview/capabilities/text-to-speech)

## 14. Kết luận nghiệm thu

Tiêu chí audit đã đạt ở mức an toàn: có bản đồ runtime chính xác, test hai chiều có auth/latency/error, phân biệt rõ transport với AI integration, xác định blocker end-to-end, đánh giá độ bền/media và đưa ra kiến trúc/lộ trình có tiêu chí nghiệm thu. Không có thay đổi production và không phát sinh chi phí model/media.

Việc tiếp theo hợp lý là phê duyệt một **P0 sandbox change window** để bật Hermes API internal-only, n8n MCP cho một workflow giả lập và chạy lại `AUDIT-E2E-001`. Chỉ sau khi test đó PASS mới nối connector business read-only.
