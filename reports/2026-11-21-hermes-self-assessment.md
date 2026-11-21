---
id: hermes-self-assessment-2026-11-21
type: report
status: current
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
source: repository-entrypoints, official-hermes-docs, live-session-tests
---

# Tự đánh giá Hermes Agent — 2026-11-21

## Tóm tắt

Kết quả tổng thể: **PARTIAL**.

Đã xác minh an toàn được rằng tác nhân Hermes trong phiên này có thể sử dụng nhóm công cụ hệ thống/web/browser/file, có memory và session recall, có hệ kỹ năng (skills), có khả năng tự động hóa nền và có thể ghi/push lên GitHub repository `DuyKienTTD/Hosting`.

Tuy nhiên, **chưa xác minh được exact build/version của Hermes instance Hostinger**, **chưa xác minh được live API endpoint của Hermes từ shell hiện tại**, và **chưa xác minh được kết nối live n8n ↔ Hermes**. Các điểm này phải được giữ ở trạng thái chưa kiểm chứng, không được mô tả như đã hoàn tất.

## Phạm vi

- Chỉ dùng phép thử an toàn, chủ yếu là đọc tài liệu, kiểm tra shell chỉ-đọc, đọc repository, tra cứu docs chính thức và kiểm tra GitHub không phá hủy.
- Không thay đổi cấu hình production của VPS, n8n hay Hermes.
- Không tạo workflow, không publish nội dung, không phát sinh chi phí có chủ đích.

## Bằng chứng

### Entry points và quy tắc repository đã đọc

- `README.md`
- `PROJECT.md`
- `AGENTS.md`
- `STATE.md`
- `CATALOG.yaml`
- `rules/AGENT_WORKFLOW.md`
- `rules/REPOSITORY_SECURITY.md`
- `CONTRIBUTING.md`

### Tài liệu chính thức của Hermes đã đọc

- `https://hermes-agent.nousresearch.com/docs/llms.txt`
- `https://hermes-agent.nousresearch.com/docs/integrations/`
- `https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp`
- `https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server`
- `https://hermes-agent.nousresearch.com/docs/user-guide/features/memory`
- `https://hermes-agent.nousresearch.com/docs/user-guide/features/skills`
- `https://hermes-agent.nousresearch.com/docs/reference/tools-reference`

### Kiểm tra live trong phiên này

- Shell hiện tại trả về `Python 3.14.10`, `git version 2.47.3`, nhưng `hermes` CLI **không có trên PATH**.
- `skills_list` trả về **55 skills** thuộc nhiều nhóm.
- `session_search` trả về các phiên trước đây, xác minh có cơ chế lưu/tra cứu lịch sử hội thoại.
- `cronjob_manage list` trả về **0 job**, xác minh tool lập lịch có mặt nhưng chưa có job đang đăng ký.
- `manage_connections status` trả về danh mục connectors/MCP khả dụng; trong phiên này hầu hết đang ở trạng thái chưa kết nối.
- `git push --dry-run origin main` trên clone local của repo thành công (`Everything up-to-date`).
- `ssh -T git@github.com` xác minh SSH auth thành công với tài khoản GitHub `DuyKienTTD`.
- Thử gọi `http://127.0.0.1:32768`, `:4860`, `:32770`, `:5678` từ shell hiện tại đều thất bại; vì vậy không thể xem các endpoint này là đã được xác minh live từ runtime hiện tại.

## Phát hiện

### 1) Phiên làm việc hiện tại và định danh runtime

- Theo metadata của phiên Hermes hiện tại: model đang dùng là **`gpt-5.4`**, provider là **`openai`**, profile là **`default`**, nguồn truy cập là **WebUI**.
- Theo shell: có Python và git khả dụng, nhưng không có binary `hermes` trên PATH nên không thể lấy version bằng `hermes --version`.
- Theo kiểm kê trong repository, instance VPS được ghi nhận đang chạy image:
  - `ghcr.io/hostinger/hvps-hermes-agent:latest`

**Kết luận:** có bằng chứng rằng Hermes đang tồn tại như một runtime/instance hoạt động, nhưng **không có bằng chứng đủ mạnh để chốt số phiên bản/build chính xác** của instance Hostinger chỉ từ shell hiện tại.

### 2) Công cụ (tools)

Theo tài liệu `Built-in Tools Reference`, Hermes hiện có khoảng **~85 built-in tools**, chưa tính các tool nạp động từ MCP.

Trong phiên hiện tại đã xác minh thực tế việc dùng được các nhóm năng lực sau:

- file tools: `read_file`, `write_file`, `search_files`, `patch`
- terminal tools: `terminal`, `process_manage` (đã mô tả schema)
- web tools: `web_search`, `web_extract`
- browser tools: `browser_exec`, `browser_vault`
- skills tools: `skills_list`, `skill_view`, `skill_manage`
- memory/session tools: `memory`, `session_search`
- automation/orchestration tools: `delegate_task`, `cronjob_manage`, `todo_list`
- multimodal/output tools: `vision_analyze`, `text_to_speech`
- connection/MCP discovery: `manage_connections`, `tool_search`, `tool_describe`, `tool_call`

Ngoài ra, tool discovery hiện cho thấy có các nguồn nạp động đang khả dụng như `browser`, `cronjob`, `session_search`, `terminal`, `todo`, `hostinger-api`.

**Kết luận:** Hermes trong phiên này có bề mặt công cụ đủ rộng cho nghiên cứu, thao tác file, terminal, browser, nhớ ngữ cảnh, automation, và tích hợp ngoài qua MCP/connectors.

### 3) Memory và session recall

Tài liệu chính thức mô tả memory bền vững gồm hai store có giới hạn:

- `MEMORY.md`: 2,200 ký tự
- `USER.md`: 1,375 ký tự

Các store này được quản lý bởi tool `memory` và nạp vào system prompt ở đầu phiên. Trong phiên hiện tại cũng xuất hiện block memory/profile ở phần ngữ cảnh tác nhân, và `session_search` đã trả về các session trước đây của profile `default`.

**Kết luận:** khả năng nhớ dài hạn và truy hồi lịch sử **được xác minh ở mức chức năng phiên làm việc**, dù không kiểm tra trực tiếp file vật lý của memory từ shell hiện tại.

### 4) Skills

`skills_list` trả về **55 skills** thuộc các nhóm lớn như:

- autonomous-ai-agents
- creative
- email
- media
- note-taking
- productivity
- research
- social-media
- software-development
- web

`skill_view('hermes-agent')` hoạt động bình thường và cho thấy skill này được dùng làm hub điều hướng tới tài liệu/chủ đề Hermes chi tiết.

**Kết luận:** hệ skills đang hoạt động và có catalog đáng kể trong profile hiện tại.

### 5) API và truy cập chương trình

Tài liệu `API Server` cho biết Hermes có thể expose OpenAI-compatible HTTP API, gồm các nhóm endpoint như:

- `/v1/chat/completions`
- `/v1/responses`
- `/v1/runs`
- `/v1/models`
- `/v1/capabilities`
- `/api/jobs`
- `/health`
- `/health/detailed`

Tuy nhiên, các thử nghiệm `curl` tới `127.0.0.1:32768`, `127.0.0.1:4860`, `127.0.0.1:32770`, `127.0.0.1:5678` từ shell hiện tại đều không kết nối được.

**Kết luận:** **khả năng API là có theo tài liệu**, nhưng **instance API cụ thể của Hostinger chưa được xác minh live từ shell hiện tại**.

### 6) Tự động hóa nền và vận hành tự chủ

Các nguồn bằng chứng:

- `cronjob_manage` có mô tả đầy đủ cho create/list/update/pause/resume/remove/run.
- `process_manage` hỗ trợ điều khiển background process.
- `delegate_task` hỗ trợ tách việc cho subagents độc lập.
- Docs chính thức mô tả recurring loops, jobs API, runs API, webhooks, bot mode và multi-platform gateway.

Phiên hiện tại không có cron job nào đã đăng ký (`jobs = 0`).

**Kết luận:** Hermes có năng lực automation/autonomy đáng kể ở mức nền tảng và toolset; trên instance hiện tại, khả năng này **có mặt nhưng chưa có job nền nào được xác minh đang hoạt động**.

### 7) n8n và khả năng tích hợp

Repository nội bộ hiện ghi rõ:

- n8n đang chạy qua Docker Compose ở lần kiểm kê gần nhất.
- Tích hợp hai chiều n8n ↔ Hermes **chưa được xác minh**.
- Kiểm kê VPS ghi public mapping `32770 -> 5678/tcp` cho n8n và `32768 -> 4860/tcp` cho Hermes.

Tài liệu MCP mới của Hermes cho biết:

- Bridge n8n bên thứ ba cũ **đã retired** khỏi catalog.
- Đường tích hợp hiện tại là **`n8n-official` MCP** dùng URL `/mcp-server/http` và browser OAuth.
- Cần n8n bật `Settings > Instance-level MCP` và Hermes backend phải reach được URL đó.

Trong phiên đánh giá này:

- Không có n8n connector/MCP nào được xác minh là đã cấu hình.
- Không có URL MCP hoặc OAuth flow nào được cung cấp để kiểm tra.
- Các curl localhost liên quan đều không truy cập được.

**Kết luận:** Hermes **có đường tích hợp n8n rõ ràng theo docs**, nhưng **instance TTD METAL hiện chưa được kiểm chứng kết nối n8n ↔ Hermes**.

### 8) GitHub integration

Đã xác minh trực tiếp:

- Repo `DuyKienTTD/Hosting` clone được về `/data/workspace/Hosting`.
- SSH auth tới GitHub thành công với `DuyKienTTD`.
- Remote repo local đã dùng SSH.
- `git push --dry-run origin main` thành công.

**Kết luận:** tại thời điểm đánh giá, Hermes **có khả năng làm việc với GitHub repo này theo hướng đọc/sửa/commit/push**.

## Rủi ro

1. Dùng image `latest` cho Hermes làm cho exact build/version khó truy xuất và khó kiểm soát thay đổi.
2. Shell hiện tại không có `hermes` CLI trên PATH nên một số phép xác minh chuẩn (`hermes --version`, `hermes doctor`, `hermes model`) không thực hiện được trực tiếp.
3. Không truy cập được các cổng localhost dự kiến của Hermes/n8n từ runtime shell hiện tại, nên không được suy diễn rằng API live đã ổn.
4. Danh mục connector rất rộng nhưng trong phiên này hầu hết ở trạng thái chưa kết nối; năng lực lý thuyết cao hơn năng lực đã sẵn sàng vận hành thực tế.

## Khuyến nghị

1. Ghim image Hermes theo version/digest thay vì `latest`.
2. Bổ sung cách kiểm tra version/build rõ ràng cho instance Hostinger (ví dụ expose version trong inventory hoặc qua health endpoint).
3. Tạo task riêng để kiểm thử end-to-end **Hermes API** bằng endpoint live an toàn (ví dụ `/health`, `/v1/models`) từ vị trí mạng thực sự truy cập được service.
4. Tạo task riêng để bật và kiểm thử **`n8n-official` MCP** với dữ liệu giả lập, xác minh cả chiều Hermes -> n8n và quyền chạy workflow.
5. Ghi nhận rõ connector/account nào là production-ready thay vì chỉ dựa vào catalog khả dụng.

## Việc đã thực hiện

- Đọc entrypoint và quy tắc của repository.
- Đọc skill `hermes-agent` và tài liệu chính thức liên quan đến integrations, API, memory, skills, tools, MCP.
- Kiểm tra shell runtime hiện tại.
- Liệt kê skills hiện có.
- Kiểm tra session recall và cron jobs.
- Kiểm tra danh mục connectors.
- Đối chiếu inventory/report hiện có của VPS trong repository.
- Xác minh GitHub SSH auth và push dry-run.
- Thử gọi localhost endpoints của Hermes và n8n bằng `curl` theo cách chỉ-đọc.

## Việc còn lại

- Xác minh exact version/build của Hermes Hostinger instance.
- Xác minh live API/health endpoint của Hermes từ vị trí mạng có thể chạm service thật.
- Xác minh live n8n ↔ Hermes qua `n8n-official` MCP hoặc một đường tích hợp đã được phê duyệt.
- Ghi nhận chính thức connector/account production-ready cho các dịch vụ ngoài nếu muốn agent tự động hóa end-to-end.
