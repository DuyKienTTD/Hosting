---
id: ttd-agent-capability-survey-codex-2026-11-21
type: report
status: complete
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: TTD-AGENT-CAPABILITY-SURVEY-001
agent: codex
source: live-local-session-tests,live-hpanel-read,prior-vps-audit,official-codex-documentation
---

# Báo cáo khảo sát năng lực Codex — 2026-11-21

## Kết luận điều hành

**Kết quả: VERIFIED_WITH_SESSION_LIMITS.** Codex trong phiên này là tác nhân kỹ thuật chạy cục bộ trong ChatGPT desktop app trên Windows, có quyền đọc/ghi filesystem và chạy command trong môi trường hiện tại, có mạng, Git, trình duyệt/Computer Use và quyền GitHub đủ để bàn giao bằng commit/push. Phiên đã chứng minh có thể đọc hPanel đang đăng nhập, dùng Hostinger Web Terminal để kiểm toán VPS, debug Docker/n8n/Hermes và lưu evidence đã khử định danh.

Đây không phải quyền vĩnh viễn. Quyền filesystem, mạng, trình duyệt, tài khoản đã đăng nhập, GitHub và approval mode phải kiểm tra lại ở mỗi chat/host. Codex không phải tiến trình 24/7, không có connector marketing hoặc credential production được expose trong phiên, và không được tự thay đổi production.

Thời điểm kiểm tra chính: **2026-11-21 12:27 ICT**. Không có thay đổi production, API/MCP/workflow, quảng cáo, website hay media trong khảo sát.

## 1. Identity và runtime

| Thuộc tính | Kết quả | Mức bằng chứng |
|---|---|---|
| Agent/surface | Codex trong ChatGPT desktop app, local project | **VERIFIED** |
| Hệ điều hành thực thi | Windows, PowerShell, `F:\7_QUANG_CAO\Hosting` | **VERIFIED** |
| App version/build | `26.1117.41037`, build `29803`, kênh `prod`, up-to-date | **VERIFIED** |
| Model | Không được expose qua tool/session metadata hiện tại | **UNKNOWN** |
| Filesystem profile | Phiên hiện tại cho phép đọc/ghi; test create/read/delete file tạm PASS | **VERIFIED_SESSION_ONLY** |
| Network | GitHub fetch/pull và tải Codex manual chính thức PASS | **VERIFIED_SESSION_ONLY** |
| Local/VPS boundary | Shell local là Windows; VPS chỉ được chạm qua kênh Hostinger đã đăng nhập, không phải cùng runtime | **VERIFIED** |

Codex app, model và policy là các lớp khác nhau. App build được đọc trực tiếp; model không được suy ra từ tên sản phẩm hay tài liệu. Quyền local hiện tại cũng không tự cấp quyền root/VPS hoặc quyền API ngoài.

## 2. Tools và permissions đã kiểm tra

### 2.1 Local terminal và files

| Công cụ | Trạng thái | Ghi chú |
|---|---|---|
| PowerShell / command execution | **VERIFIED** | Chạy command, script validation và Git trong workspace |
| File read/write/patch | **VERIFIED** | Đọc repo; tạo/đọc/xóa file probe; cập nhật report/profile bằng patch |
| Git | **VERIFIED** | `git 2.54.0`; fetch/pull/commit/push đã dùng thực tế |
| ripgrep | **VERIFIED** | `rg 15.2.0` |
| Node.js | **VERIFIED** | `v26.3.0` |
| Python | **VERIFIED** | `3.12.3` |
| OpenSSH client | **AVAILABLE_UNTESTED** | Binary có mặt; chưa xác minh direct SSH auth tới VPS trong khảo sát này |
| Docker CLI | **BLOCKED_LOCAL_DAEMON** | Client `29.4.3` có mặt; Docker Desktop daemon không chạy |
| GitHub CLI | **DEGRADED** | Binary có mặt; biến `GITHUB_TOKEN` hiện không hợp lệ và keyring account không active cho `gh` |

Không sửa hoặc xóa biến môi trường GitHub trong survey. Git qua HTTPS là kênh đã chứng minh; không phụ thuộc `gh` cho bàn giao này.

### 2.2 GitHub, PR và CI

- **GitHub read/write: VERIFIED.** Repo fetch/pull thành công; audit trước và survey này được commit/push bằng Git HTTPS.
- **Branch/commit/diff/review: VERIFIED.** Codex có thể tạo patch, stage, chạy checks, đọc diff và commit.
- **PR creation: AVAILABLE_UNTESTED.** Codex app hỗ trợ branch/worktree/PR theo tài liệu; repo này chưa thử flow PR trong survey.
- **CI execution: BLOCKED_NOT_CONFIGURED.** Không có file `.github/workflows` ở thời điểm kiểm tra, nên chưa có pipeline repo để trigger hoặc quan sát.
- `gh` CLI không được coi là kênh sẵn sàng cho đến khi dọn xung đột token bằng một task riêng; Git HTTPS vẫn hoạt động.

### 2.3 Browser, hPanel và VPS

- **Browser/Computer Use: VERIFIED.** Phiên có thể đọc và điều khiển Chrome qua Computer Use, với confirmation gate cho hành động nhạy cảm.
- **Hostinger hPanel read: VERIFIED_CURRENT_SESSION.** Đọc trực tiếp trang chủ hPanel đã đăng nhập và thấy VPS đang chạy; không click/thay đổi cấu hình.
- **Hostinger Web Terminal/VPS read: VERIFIED_SAME_DAY.** Audit trước trong cùng chat đã dùng Web Terminal để chạy probe read-only trên VPS.
- **VPS Docker/n8n/Hermes diagnostics: VERIFIED_SAME_DAY.** Có report/evidence cho image, version, network, health, resource, auth và blocker.
- **Direct SSH from local shell: AVAILABLE_UNTESTED.** Có client SSH nhưng không dùng endpoint/credential VPS trong survey.
- **Production mutation: APPROVAL_REQUIRED / NOT_TESTED.** Khả năng nhìn thấy hPanel hoặc root Web Terminal không phải ủy quyền restart, deploy, firewall, DNS, SSH hay credential change.

### 2.4 n8n và Hermes

Kế thừa bằng chứng mới cùng ngày, không lặp probe:

| Năng lực | Trạng thái |
|---|---|
| Đọc health/readiness n8n | **VERIFIED** |
| Đọc Hermes dashboard health/OpenAPI | **VERIFIED** |
| Test network/auth n8n → Hermes dashboard | **VERIFIED** |
| Test Hermes → n8n readiness | **VERIFIED** |
| n8n instance-level MCP | **BLOCKED — disabled** |
| Hermes inference API `/v1/*` | **BLOCKED — not exposed** |
| Fake ads end-to-end workflow | **BLOCKED — 0 workflow, MCP disabled, no inference endpoint** |
| Bật API/MCP/network/workflow | **APPROVAL_REQUIRED** |

Nguồn: [live audit](2026-11-21-n8n-hermes-integration-audit.md) và [evidence JSON](evidence/2026-11-21-ttd-ai-platform-audit-001.json).

### 2.5 Skills, MCP, web và memory

- **Skills: VERIFIED.** Phiên expose các skill cho OpenAI/Codex docs, Computer Use, documents, PDF, presentations, spreadsheets, image generation và skill management. Survey đã dùng trực tiếp `openai-docs` và `computer-use`.
- **Web research/network: VERIFIED.** Có thể tải official Codex manual và dùng web search; nguồn Internet không thay thế private connector evidence.
- **MCP resources/templates: NONE_EXPOSED.** Lệnh liệt kê trả về 0 resource và 0 template. Codex app tools/Computer Use là tool bề mặt phiên, không phải connector marketing đã cấu hình.
- **Persistent memory: UNKNOWN/NOT_EXPOSED.** Phiên có chat context và Git repository; không có memory store tool riêng được expose để chứng minh durable user memory.
- **External APIs:** GitHub qua Git và hPanel qua browser đã xác minh. Google Ads, GA4, WordPress/WooCommerce, YouTube, TikTok, Meta, Kling, HeyGen và ElevenLabs không có API credential/scope được kiểm thử.

### 2.6 Background, scheduling và continuity

- Command dài có thể trả session ID và Codex có thể poll trong **turn đang chạy**.
- Codex app có goal, automation, worktree và remote-control surfaces theo tài liệu; không có automation nào được tạo/test trong survey.
- Chat local không được coi là tiến trình 24/7. Nếu app/host ngủ, mất mạng hoặc chat dừng, không có đảm bảo tiếp tục tự động.
- Scheduled task có thể chạy trên worktree riêng khi được cấu hình, nhưng vẫn phụ thuộc host/policy và không tự tạo callback/job database cho TTD METAL.
- State vận hành dài hạn nên đặt tại n8n/PostgreSQL; Git dùng cho task/report/code/evidence.

## 3. Ma trận nghiệp vụ

| Nghiệp vụ | Trạng thái | Codex có thể làm hiện tại |
|---|---|---|
| Phát triển code/API/test | **VERIFIED** | đọc/sửa repo, test, review, commit/push; xây adapter và harness khi được giao |
| VPS/Docker/network audit | **VERIFIED_READ_ONLY** | hPanel/Web Terminal, inventory, health/log redaction, topology |
| VPS deployment/hardening | **AVAILABLE_UNTESTED + APPROVAL_REQUIRED** | chuẩn bị diff/rollback/check; chỉ apply trong task production riêng |
| n8n/Hermes debug | **VERIFIED_READ_ONLY** | health, auth, OpenAPI, Docker/network, blocker analysis |
| n8n/Hermes implementation | **PLANNED + APPROVAL_REQUIRED** | API private, MCP, workflow sandbox, idempotency/observability |
| Media pipeline engineering | **AVAILABLE_UNTESTED** | code worker, FFmpeg container, storage/lifecycle; render API chưa nối |
| Document/PDF/sheet/presentation | **AVAILABLE_UNTESTED** | skills có mặt; chưa cần test trong survey |
| Google Ads/GA4 analysis | **BLOCKED_CONNECTOR** | có thể thiết kế/query code; chưa có API scopes/credential/test account |
| Ads write/budget changes | **BLOCKED + APPROVAL_REQUIRED** | không thực hiện trong survey |
| WordPress/WooCommerce/SEO | **AVAILABLE_UNTESTED_BROWSER; BLOCKED_API** | có thể audit/code/draft; chưa test API service identity hoặc publish |
| YouTube/TikTok/Meta | **BLOCKED_CONNECTOR** | thiết kế/upload draft flow; chưa có app scopes/credential |
| Public publishing/email | **APPROVAL_REQUIRED** | có thể chuẩn bị draft, không đại diện gửi/publish khi chưa duyệt |
| Báo cáo/tri thức Git | **VERIFIED** | report, evidence, state, catalog, changelog và commit/push |

## 4. Nhận task và phối hợp

### Nhận việc

- **VERIFIED:** task URL/file trong Git và prompt trực tiếp trong chat.
- **AVAILABLE_UNTESTED:** Codex thread riêng, worktree, automation hoặc remote control khi người dùng chủ động cấu hình.
- **BLOCKED_CURRENTLY:** n8n webhook/MCP/API không được nối trực tiếp vào Codex chat này.

### Giao việc và song song hóa

- Có tool điều phối Codex threads/subagents, nhưng policy phiên hiện tại chỉ cho spawn khi người dùng yêu cầu rõ. Survey không spawn agent.
- Có thể tạo/fork/send message tới Codex thread khi có ủy quyền; không đồng nghĩa có thể nhắn Hermes/Hostinger Agent trực tiếp.
- Với Hermes, Hostinger Agent hoặc tác nhân khác, Git task/report vẫn là cơ chế bàn giao bền vững; chủ dự án có thể chuyển tiếp.
- Worktree/branch nên dùng khi hai task có thể sửa cùng repository; không để nhiều agent cùng ghi một checkout.

### Callback, logs và task ID

- Git commit, report ID và command session ID cung cấp trace cho công việc kỹ thuật.
- Codex thread có trạng thái/wait tools, nhưng không phải queue nghiệp vụ hay SLA monitor.
- Không có callback URL/job store chung với n8n/Hermes trong phiên.
- Workflow production cần `task_id`, correlation ID, execution log và final status trong n8n/DB.

## 5. Approval mode và giới hạn thực tế

### Session boundary

- Phiên hiện tại cho command/filesystem/network rộng và không yêu cầu prompt cho các thao tác local đã chạy. Đây là cấu hình phiên, không phải quyền lâu dài.
- Computer Use có gate riêng cho login, upload, truyền dữ liệu nhạy cảm, publish, permission, delete và các hành động tác động ngoài.
- Repository rule vẫn yêu cầu approval riêng cho production, chi phí, credentials, restart/recreate, firewall/SSH/DNS/SSL và publish.

### Chi phí và quota

- Model name, token budget, billing unit và quota account không được expose: **UNKNOWN**.
- Không gọi LLM/media paid API trong survey.
- Mọi connector trả phí phải có budget cap, estimated cost, idempotency và approval gate.

### Security

- Repo công khai: không commit IP/hostname thật, token, cookie, `.env`, raw logs hoặc customer payload.
- Browser session có thể nhìn thấy tài khoản đã đăng nhập; read access không cấp quyền API và không tự cấp quyền gửi/publish.
- `GITHUB_TOKEN` local hiện không hợp lệ; không ghi giá trị và không sửa trong survey.
- Docker daemon local không chạy; không suy ra local Docker từ CLI presence.

### Failure và rollback

- Thay đổi repo có thể kiểm tra bằng diff/test và rollback bằng commit correction; không force-push.
- Production change phải có backup/snapshot khi phù hợp, rollback command, health check và maintenance/approval riêng.
- Không dùng audit read-only trước đây làm bằng chứng Codex luôn có root hoặc được phép deploy.

## 6. Phân vai đề xuất cho TTD METAL

### Codex nên làm owner

1. Code, API adapters, test harness, schema, data migrations có rollback.
2. Docker/Compose, private networking, reverse proxy/TLS, observability và security hardening theo task được duyệt.
3. n8n↔Hermes integration, workflow sandbox, idempotency/retry/error handling.
4. Media-worker/FFmpeg, storage lifecycle, CI/test/release engineering.
5. Audit kỹ thuật, incident diagnosis, report/evidence và Git handoff.

### Nên giao hoặc phối hợp

- **Hermes:** reasoning/content planning/tool execution sau khi API/MCP được bật an toàn.
- **n8n:** schedule, connectors, retry, execution state, callback và job observability.
- **ChatGPT/business owner:** yêu cầu nghiệp vụ, priority, copy/creative review và acceptance.
- **Hostinger/hPanel:** provider-level backup/firewall/VPS controls theo approval.
- **Con người:** credentials, ngân sách, quảng cáo write, publish, DNS/SSH/firewall và quyết định có rủi ro.

## 7. Ba thử nghiệm an toàn có giá trị cao nhất

1. **Sandbox n8n↔Hermes E2E bằng fake data** — sau approval riêng, expose Hermes API internal-only và đúng một n8n workflow sandbox; không dùng account marketing hoặc model trả phí ngoài budget cap. PASS khi có task ID, schema, execution log và final state hai đầu.
2. **Git branch/PR/CI smoke test** — thêm một workflow CI chỉ chạy repository validator/secret scan trên branch thử nghiệm, mở PR và kiểm tra review/rollback; không đụng production VPS.
3. **Direct SSH read-only với account least-privilege** — tạo task riêng để kiểm tra kênh SSH không-root, run allowlisted inventory script và đối chiếu với hPanel; không restart/chỉnh config. Mục tiêu là giảm phụ thuộc Web Terminal/root.

## 8. Việc đã thực hiện trong survey

- Đọc task, entrypoints, hồ sơ Codex và quy tắc repository.
- Cập nhật repo từ remote mà không ghi đè thay đổi khác.
- Tải Codex manual chính thức hiện hành bằng helper của skill `openai-docs`.
- Đo app build/update, toolchain local, workspace write, Git/network, Docker daemon, `gh` auth state và MCP inventory.
- Dùng Computer Use chỉ-đọc để xác nhận hPanel hiện đang đăng nhập; không thao tác thay đổi.
- Kế thừa live audit n8n/Hermes thay vì chạy lại probe VPS.
- Cập nhật hồ sơ, report, catalog/state/changelog; chạy validator/secret scan trước push.

## 9. Không thực hiện

- Không mở Web Terminal mới hoặc chạy thêm command VPS.
- Không dùng direct SSH, Docker mutation, restart, deploy, firewall/DNS/SSL/credential change.
- Không bật Hermes API, n8n MCP hoặc tạo workflow.
- Không đọc/ghi Ads, WordPress, social, email hay media API.
- Không tạo automation, subagent, account, key hoặc chi phí mới.

## 10. Nguồn

- [Task khảo sát](../tasks/2026-11-21-agent-capability-survey.md)
- [Hồ sơ Codex](../agents/codex.md)
- [n8n/Hermes live audit](2026-11-21-n8n-hermes-integration-audit.md)
- [Codex best practices](https://learn.chatgpt.com/guides/best-practices.md)
- [Codex local environments và Git controls](https://learn.chatgpt.com/docs/environments/local-environment.md)
- [Codex Computer Use](https://learn.chatgpt.com/docs/computer-use.md)
- [Codex long-running work](https://learn.chatgpt.com/docs/long-running-work.md)
- [Codex sandboxing](https://learn.chatgpt.com/docs/sandboxing.md)

## 11. Khả năng vẫn chưa rõ

- Exact model/reasoning effort và account-level cost/quota của chat này.
- Direct SSH authentication/authorization từ local shell tới VPS.
- PR/CI end-to-end và Codex scheduled task khi app/host không tương tác.
- Durable memory ngoài chat/Git.
- API scopes/credentials cho toàn bộ hệ thống marketing, website, media và social.
- Quyền production trong một task tương lai; phải được cấp lại rõ ràng.
