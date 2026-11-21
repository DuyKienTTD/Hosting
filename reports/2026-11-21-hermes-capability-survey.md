---
id: hermes-capability-survey-2026-11-21
type: report
status: current
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: TTD-AGENT-CAPABILITY-SURVEY-001
source: hermes-webui-session-tests,existing-hermes-self-assessment,live-n8n-hermes-audit,repository-agent-profile
---

# Khảo sát năng lực Hermes Agent — 2026-11-21

## Tóm tắt

Kết quả tổng thể: **PARTIAL**.

Hermes trong **phiên WebUI hiện tại** đã được xác minh có thể đọc/ghi GitHub cho repository này, thao tác file/terminal/web/browser trong sandbox phiên, dùng skills/memory/session recall, và có công cụ background/delegation ở mức tool surface. Tuy nhiên, **không được đồng nhất** năng lực của phiên WebUI với năng lực của **Hermes container trên VPS**.

Bằng chứng live hiện có cho thấy container Hostinger Hermes trên VPS là **dashboard/control plane `0.22.5`** và khỏe ở mức dịch vụ, nhưng **chưa expose live agent inference API**, **n8n MCP vẫn disabled**, và **chưa có luồng end-to-end n8n ↔ Hermes production-ready**. Vì vậy, Hermes phù hợp nhất hiện tại cho vai trò **reasoning / analysis / planning / draft generation / tool-assisted investigation**, chưa phù hợp để tuyên bố đã sẵn sàng làm backend AI 24/7 cho workflow production.

## Thời điểm và phương pháp

- Thời điểm kiểm tra bổ sung trong phiên này: **2026-11-21T05:26:21Z**.
- Phương pháp: đọc task và hồ sơ agent; tái sử dụng bằng chứng đáng tin cậy từ self-assessment và live audit; chỉ kiểm tra lại các điểm còn giá trị trong **phiên WebUI hiện tại** như GitHub push, skills, session recall, cron/background surface, connector readiness.
- Không sửa production, không bật API/MCP, không thay network/credential/workflow, không gọi model trả phí ngoài phạm vi phiên hiện tại.

## Nguồn bằng chứng chính

- Task: `tasks/2026-11-21-agent-capability-survey.md`
- Hồ sơ hiện tại: `agents/hermes.md`
- Self-assessment trước đó: `reports/2026-11-21-hermes-self-assessment.md`
- Live audit VPS: `reports/2026-11-21-n8n-hermes-integration-audit.md`
- Danh bạ agent: `agents/README.md`

## 1. Identity / runtime

### VERIFIED

- Tên tác nhân: **Hermes Agent**.
- Phiên đang khảo sát là **Hermes WebUI session** trên profile `default`.
- Model ở phiên WebUI đang dùng theo metadata phiên: **`gpt-5.4`** qua provider **OpenAI**.
- Shell gắn với phiên WebUI hiện tại có:
  - `whoami = u4s`
  - `Python 3.14.10`
  - `git version 2.47.3`
  - **`hermes` CLI không có trên PATH** trong shell này.

### VERIFIED từ live audit VPS, không phải từ shell WebUI

- Hermes chạy trên VPS qua image Hostinger: dashboard/control plane **`0.22.5`**, upstream commit `bf0203a7`.
- Container Hermes healthy, auth dashboard hoạt động, n8n reach được dashboard qua host-published path.

### Kết luận runtime

Có **hai môi trường phải tách biệt**:

1. **Hermes WebUI session / shell**
   - nơi mình đang thao tác GitHub, file, browser, memory, skills, session search.
   - không có `hermes` binary trên PATH trong shell này.

2. **Hermes container trên VPS**
   - theo live audit là service dashboard/control plane `0.22.5`.
   - là môi trường được n8n chạm tới trong audit kỹ thuật.

Không được suy luận rằng việc WebUI có một tool nào đó đồng nghĩa container VPS cũng expose đúng cùng capability qua HTTP/API.

## 2. Tools / permissions đã test

### VERIFIED trong phiên WebUI hiện tại

| Năng lực | Trạng thái | Bằng chứng ngắn |
|---|---|---|
| GitHub read/write repo `DuyKienTTD/Hosting` | **VERIFIED** | clone/pull/push dry-run OK; các commit trước đã push thành công; remote dùng SSH |
| File tools | **VERIFIED** | `read_file`, `write_file`, `search_files`, `patch` dùng trực tiếp trong task này |
| Terminal shell | **VERIFIED** | chạy lệnh đọc/ghi an toàn trong workspace thành công |
| Browser automation | **VERIFIED** | đã dùng `browser_exec` để đọc GitHub/login state ở phần khảo sát trước |
| Skills catalog | **VERIFIED** | `skills_list` trả **55 skills** |
| Memory/session recall | **VERIFIED** | block memory xuất hiện trong runtime; `session_search` trả session cũ |
| Cron/background tool surface | **VERIFIED** | `cronjob_manage` khả dụng; `list` trả **0 job** |
| Delegation/process control surface | **VERIFIED** | `delegate_task`, `process_manage` có mặt trong toolset/schemas |
| MCP / connector catalog surface | **VERIFIED** | `manage_connections status` liệt kê catalog connectors/MCP khả dụng |

### VERIFIED nhưng chỉ ở mức “có bề mặt”, chưa phải đã sẵn sàng vận hành business

| Năng lực | Trạng thái | Giải thích |
|---|---|---|
| Background scheduling | **AVAILABLE_UNTESTED** | có `cronjob_manage`, nhưng chưa chứng minh job dài hạn 24/7 cho dự án này |
| Delegation/subagents | **AVAILABLE_UNTESTED** | có `delegate_task`, nhưng chưa chứng minh governance/logging chuẩn cho production workflow |
| External connectors | **AVAILABLE_UNTESTED** | catalog có mặt, nhưng trong phiên này **không có account connected nào được xác minh** |
| Browser vault / credential fill | **AVAILABLE_UNTESTED** | tool có mặt; dùng được khi có login được lưu và phù hợp origin/page |

### VERIFIED từ live audit VPS

| Năng lực | Trạng thái | Bằng chứng ngắn |
|---|---|---|
| Hermes dashboard/control API on VPS | **VERIFIED** | health/auth dashboard PASS trong audit live |
| Hermes ↔ n8n network reachability qua host bridge | **VERIFIED** | n8n → Hermes dashboard auth PASS; Hermes → n8n readiness PASS |

### BLOCKED / UNKNOWN

| Năng lực | Trạng thái | Lý do |
|---|---|---|
| Hermes inference API live trên VPS | **BLOCKED** | audit xác nhận image đang chạy không expose `/v1/*` agent API upstream |
| n8n instance-level MCP | **BLOCKED** | audit trả `MCP access is disabled` |
| SSH/root/VPS shell trực tiếp từ phiên Hermes WebUI | **UNKNOWN** | không có bằng chứng phiên này có quyền shell vào VPS production ngoài sandbox đang dùng |
| Hostinger hPanel control từ chính Hermes session | **UNKNOWN** | chưa xác minh có quyền thao tác hPanel/Hostinger Agent từ phiên này |
| API ngoài cho Ads / GA4 / WP / social / media | **UNKNOWN** | chưa có connector/account/API key nào được xác minh connected trong phiên này |
| Approval mode chi tiết của Hermes production runtime | **UNKNOWN** | chỉ quan sát được rằng một số thao tác shell có approval mediation; chưa có ma trận policy đầy đủ |

## 3. Các nghiệp vụ có thể thực hiện cho TTD METAL

### VERIFIED

- **Báo cáo / phân tích / khảo sát kỹ thuật**: đọc tài liệu, tổng hợp bằng chứng, tạo report GitHub, cập nhật catalog/state/changelog khi cần.
- **SEO / content planning / QA text-first**: lập brief, phân loại backlog, rà task, viết draft có cấu trúc, kiểm tra logic trước khi publish.
- **Nghiên cứu tích hợp**: đọc docs MCP/API/tooling, so sánh phương án triển khai, đề xuất kiến trúc và acceptance criteria.
- **Git-backed task execution**: nhận task qua GitHub, sửa tài liệu trong repo, commit và push khi quyền SSH còn hoạt động.
- **Tool-assisted investigation**: dùng terminal/file/browser/web để xác minh claim trong phạm vi an toàn.

### AVAILABLE_UNTESTED

- **Media pre-production**: viết prompt, shot list, cấu trúc pipeline, QA checklist cho render/video/audio, nhưng chưa xác minh connector thực tế của Kling/HeyGen/ElevenLabs trong instance này.
- **Scheduled reporting**: về mặt nền tảng có cron/background tool surface, nhưng chưa chứng minh lịch 24/7 và delivery chain phù hợp dự án.
- **MCP-based workflow calls**: về lý thuyết Hermes hỗ trợ MCP client/server, nhưng đường cụ thể tới n8n ở instance này còn blocked.
- **Multi-agent collaboration**: có delegate/subagent capabilities, nhưng chưa chứng minh policy/logging tiêu chuẩn cho vận hành liên tục của TTD METAL.

### BLOCKED

- **Hermes làm backend inference cho n8n trên VPS**: blocked vì chưa expose live inference API.
- **Hermes gọi workflow n8n qua MCP hiện tại**: blocked vì n8n MCP đang disabled.
- **Publish social / Ads write / website write production qua connector thật**: blocked ở mức quyền/cấu hình/chưa xác minh account.

### UNKNOWN

- Google Ads / GA4 operational write/read qua account thật
- WordPress / WooCommerce account access trong phiên Hermes này
- YouTube / TikTok / Meta publishing qua account thật
- VPS administration trực tiếp từ phiên Hermes WebUI hiện tại
- Hostinger Agent orchestration capabilities nếu không đi qua hPanel agent channel riêng

### PLANNED

- Hermes reasoning qua private API internal-only sau khi được phê duyệt
- Hermes gọi n8n workflow sandbox qua `n8n-official` MCP sau khi enable
- Media/content factory có approval + budget gates

## 4. Phối hợp

### Nhận task / đầu vào

Hermes hiện có thể nhận việc tốt nhất qua:

- **GitHub task URL / repo file** — đã được xác minh là workflow phù hợp nhất hiện tại.
- **WebUI chat** — để khởi động tác vụ, đọc file, kiểm tra bằng chứng và đẩy report.
- **Tương lai:** n8n callback / MCP / API chỉ nên xem là **PLANNED**, chưa phải đường đang hoạt động ổn định.

### Giao cho tác nhân khác / tách việc

- Có thể **delegate subtasks** trong phiên bằng `delegate_task` khi cần reasoning song song.
- Với công việc cần thay đổi hạ tầng/VPS/code sâu, **Codex** vẫn là owner phù hợp hơn theo agent directory.
- Với workflow scheduling, retry, state machine, callback routing — **n8n** nên là control plane khi đã được bật cấu hình cần thiết.

### Commit / push / delivery

- **VERIFIED:** Hermes trong phiên này có thể tự commit/push report lên GitHub repo này khi SSH auth còn hợp lệ.
- **VERIFIED:** có `session_search` để tham chiếu lịch sử phiên, và có artifact/report workflow qua Git.
- **AVAILABLE_UNTESTED:** cron/background delivery có tool surface nhưng chưa chứng minh 24/7 khi UI đóng trong bối cảnh TTD METAL.
- **UNKNOWN:** callback/log/task-id chuẩn hoá cho production workflow liên agent; hiện mới có pattern trong Git/report, chưa có runtime state bus chung ngoài n8n kế hoạch.

## 5. Giới hạn thực tế

1. **WebUI runtime khác VPS runtime**: đây là giới hạn quan trọng nhất; không được gộp bằng chứng chéo mà không ghi rõ môi trường.
2. **Không có `hermes` CLI trên PATH trong shell phiên này**: nên không thể dùng trực tiếp `hermes --version`, `hermes doctor`, `hermes model` trong shell hiện tại.
3. **Inference/API trên VPS chưa sẵn sàng**: container Hostinger Hermes hiện là dashboard/control plane, không phải inference endpoint production-ready.
4. **Connector/catalog ≠ credential thực**: thấy tool/connectors trong catalog không có nghĩa là đã có account usable.
5. **Chi phí / approval / quyền ghi production**: mọi action có thể phát sinh phí hoặc thay đổi business system cần human approval riêng; khảo sát này không tự nâng quyền.
6. **Background claims còn thiếu bằng chứng vận hành**: có tool surface nhưng chưa chứng minh SLA/retry/rollback/observability cho 24/7 workloads.
7. **Rollback và failure isolation**: trong repo/docs đã có quy tắc báo cáo và Git history, nhưng rollback cho business actions phụ thuộc vào hệ thống đích, chưa được chứng minh ở Hermes runtime.

## 6. Đề xuất phân vai cho Hermes

### Việc Hermes làm tốt nhất ngay bây giờ

1. **AI analyst/operator cho task dạng Git + tools**: đọc task, điều tra, tổng hợp bằng chứng, viết report và cập nhật knowledge base.
2. **Planning / reasoning / draft generation**: nội dung, SEO, media plan, schema đầu vào/đầu ra, QA checklist, audit kết nối.
3. **Preflight research trước khi thay đổi production**: đọc docs, đối chiếu capability, xác định blocker/risk/acceptance criteria trước khi giao Codex hoặc n8n thực thi.

### Việc nên giao đối tác

- **Codex**: thay đổi VPS/Docker/network/API, debug sâu môi trường chạy, triển khai code, workflow sandbox, healthcheck/resource limits.
- **n8n**: scheduling, retries, state machine, callback routing, execution logs, cross-system job state.
- **ChatGPT / owner task**: chiến lược, ưu tiên backlog, nghiệm thu business, soát output trước publish khi cần.
- **Hostinger / Hostinger Agent**: những gì gắn với hPanel/control plane nếu cần quyền mà Hermes phiên này không có.

### 3 thử nghiệm an toàn có giá trị cao nhất

1. **P0-A: xác minh private Hermes inference path**
   - Mục tiêu: chứng minh một endpoint inference private, không public, trả lời được request schema nhỏ.
   - Điều kiện: change window + token riêng + không dùng connector business.

2. **P0-B: bật n8n instance-level MCP cho đúng 1 workflow sandbox**
   - Mục tiêu: chứng minh Hermes có thể `tools/list` và gọi 1 workflow giả lập có `task_id`, validation, no side effects.
   - Điều kiện: enable MCP có kiểm soát, workflow fake-data only.

3. **P0-C: pilot scheduled reporting read-only**
   - Mục tiêu: dùng n8n làm scheduler, Hermes làm reasoning, Git/report làm output; không có write vào Ads/social/site.
   - Điều kiện: dữ liệu nguồn chỉ-read, budget/logging rõ ràng, approval cho delivery nếu gửi ra ngoài.

## 7. Cập nhật hồ sơ Hermes cần phản ánh

Bằng chứng mới từ khảo sát này cho phép nâng độ rõ ràng của hồ sơ `agents/hermes.md` ở các điểm sau:

- GitHub write trong phiên WebUI hiện tại là **VERIFIED**, không chỉ reported.
- Cần ghi rõ phân biệt **Hermes WebUI session** với **Hermes VPS container `0.22.5`**.
- Nên tách các nhóm năng lực thành VERIFIED / AVAILABLE_UNTESTED / BLOCKED / UNKNOWN thay vì mô tả gộp.
- Cần ghi rõ catalog connectors có mặt nhưng **không có account production-ready nào được xác minh trong phiên này**.

## 8. Kết luận

Hermes hiện **hữu ích ngay** cho các việc reasoning, audit, planning, Git-based reporting, SEO/content analysis và điều tra dùng tools. Hermes **chưa nên được xem là production AI backend 24/7** cho TTD METAL cho tới khi có ít nhất một đường inference/API private đã PASS và một workflow sandbox n8n ↔ Hermes đã chạy end-to-end thành công.

Các quyền/khả năng vẫn chưa rõ sau khảo sát này:

- live Hermes inference API trên VPS sau dashboard image
- n8n official MCP sau khi enable
- connector/account thực cho Google Ads, GA4, WordPress/WooCommerce, YouTube, TikTok, Meta, Kling, HeyGen, ElevenLabs
- quyền hPanel/Hostinger Agent trực tiếp từ Hermes session
- khả năng background 24/7 có SLA/rollback/logging phù hợp production
