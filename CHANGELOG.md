# Lịch sử cập nhật

## 2026-11-21

- Chủ dự án phê duyệt **Mức 1** của ADR-P0-001: Codex được tiếp tục kỹ thuật sandbox n8n ↔ Hermes với inference runtime cô lập và một authenticated webhook, có preflight/backup/rollback. Mức 2 (provider/model, cost cap, paid inference) và thay đổi gây downtime/public production vẫn chưa được phê duyệt. Chưa có thay đổi VPS do ChatGPT thực hiện tại bước ghi nhận này.

- Lập ADR-P0-001 ở trạng thái PROPOSED sau P0 network PASS/E2E BLOCKED: Hermes inference cô lập, n8n authenticated webhook, nghiên cứu provider/model và cost cap; chưa phê duyệt hay thay production.

- Triển khai network-only P0 `ttd-ai-p0-sandbox` ở chế độ internal, gắn live n8n/Hermes bằng private DNS; health, negative auth và rollback preparation PASS, không restart/downtime/public port/firewall change và không gọi paid API.
- Ghi `PARTIAL / BLOCKED_BY_BUDGET_AND_RUNTIME`: Hermes chưa expose inference API, n8n MCP còn disabled và chưa có workflow/callback; thêm report/evidence, cập nhật task/state/catalog.
- Đồng bộ catalog/state với kết quả định danh đã complete: `ttdnew.tech` U4S Hermes tách biệt KVM 2; thêm catalog entry cho báo cáo identity.

- Tạo nhiệm vụ định danh resource `ttdnew.tech` (Hostinger Agent owner) và P0 sandbox n8n ↔ Hermes (Codex owner), có identity gate, backup/rollback, không phát sinh phí chưa duyệt.
- P0 chưa được thực thi; ghi rõ trạng thái BLOCKED cho tới khi resource được xác minh và các điều kiện an toàn đạt.

- Mở rộng hồ sơ Hostinger Agent theo account inventory 2026-11-21; ghi nhận Cloud Startup/WordPress, VPS, Docker/AI, domains, email, Reach và giới hạn quyền filesystem.
- Liên kết báo cáo `reports/2026-11-21-hostinger-account-capability-inventory.md` vào catalog, danh bạ và trạng thái chung; giữ mâu thuẫn OpenClaw vs `u4s-hermes-agent` ở trạng thái chưa xác minh.

- Thêm `reports/2026-11-21-hermes-capability-survey.md`, cập nhật `agents/hermes.md`, `CATALOG.yaml` và `STATE.md` cho khảo sát bổ sung theo task `TTD-AGENT-CAPABILITY-SURVEY-001`.
- Ghi nhận rõ khác biệt giữa Hermes WebUI session và Hermes VPS container `0.22.5`; xác minh lại GitHub write, skills/memory/session recall và giữ trạng thái BLOCKED/UNKNOWN cho inference API, n8n MCP và connector business.
- Hoàn tất khảo sát Codex theo `TTD-AGENT-CAPABILITY-SURVEY-001`; ghi rõ runtime, local/Git/browser/hPanel/VPS permissions, n8n/Hermes evidence, background limits và approval boundaries.
- Cập nhật `agents/codex.md`, danh bạ agent, state và catalog; thêm catalog entry cho báo cáo Hostinger Agent đã có trên remote.
- Xác nhận Codex app build hiện tại, Git HTTPS read/write và Computer Use; ghi `BLOCKED/UNKNOWN` cho local Docker daemon, exact model, persistent execution và các connector marketing chưa test.
- Không thay đổi production hoặc tạo connector/automation/paid API call.

- Thêm danh bạ vai trò `agents/` cho ChatGPT, Codex, Hermes, Hostinger/Hostinger Agent và n8n, phân biệt capability verified/reported/unknown.
- Đưa lên GitHub task `TTD-AGENT-CAPABILITY-SURVEY-001` để chủ dự án chuyển câu hỏi đến từng tác nhân và nhận báo cáo tự đánh giá.
- Liên kết các hồ sơ vào README, PROJECT, AGENTS, STATE và CATALOG.

- Hoàn tất `TTD-AI-PLATFORM-AUDIT-001` và thêm báo cáo/evidence đã khử định danh cho kiểm toán live n8n ↔ Hermes.
- Xác minh n8n `2.45.7`, Hermes `0.22.5`, network/auth hai chiều và trạng thái runtime; ghi rõ MCP, inference API và end-to-end còn `BLOCKED`.
- Đề xuất kiến trúc n8n control plane + Hermes reasoning + internal network + policy/approval gate + media-worker; cập nhật `PROJECT.md`, `STATE.md`, inventory và catalog.
- Không thay đổi production, không gọi model/media trả phí và không kết nối tài khoản marketing.

- Tạo task `TTD-AI-PLATFORM-AUDIT-001` kiểm toán live n8n ↔ Hermes và thiết kế hệ thống AI Automation dựa trên báo cáo tự đánh giá Hermes.

- Thêm `reports/2026-11-21-hermes-self-assessment.md`, catalog tương ứng và cập nhật `STATE.md` cho đợt tự đánh giá năng lực Hermes Agent hiện tại.
- Ghi nhận đã xác minh được skills, session recall và GitHub push của agent; đồng thời giữ trạng thái chưa kiểm chứng cho exact Hermes build/version, live API endpoint và live n8n integration.

- Thêm `PROJECT.md` xác định mục tiêu nền tảng AI TTD METAL và tiến độ thực tế.
- Thêm `rules/AGENT_WORKFLOW.md` thống nhất giao task qua GitHub, báo cáo trở lại GitHub, quy định tối thiểu không khóa phương pháp.
- Liên kết entrypoint và danh mục cho mọi tác nhân; chuẩn bị `tasks/` cho các đặc tả tiếp theo.

- Tổ chức repository thành nguồn tri thức cho nhiều tác nhân với `AGENTS.md`, `STATE.md` và `CATALOG.yaml`.
- Thêm quy trình đóng góp, cấu trúc inventory/report/knowledge/runbook/decision/reference/archive và các mẫu tài liệu.
- Thêm trình kiểm tra repository để phát hiện metadata, liên kết, catalog hoặc dấu hiệu bí mật không hợp lệ.
- Chuẩn hóa tên file và chuyển báo cáo bảo mật có ngày từ `inventory/` sang `reports/`.
- Khởi tạo cấu trúc tài liệu vận hành cho repository.
- Ghi nhận kiểm kê trực tiếp VPS Hostinger sau khi xóa `CHUNG_KHOAN_PRO` và Alibaba OneTalk.
- Ghi nhận cấu hình n8n, Hermes Agent, Docker, PostgreSQL, Nginx, UFW, Fail2ban, SSH và sao lưu.
- Thêm đánh giá bảo mật và lộ trình cải thiện.
- Thêm quy tắc chống commit bí mật và script kiểm kê chỉ đọc.
