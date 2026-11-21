---
id: current-state
type: state
status: current
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
---

# Trạng thái hiện tại

Đây là điểm đọc nhanh. Chi tiết đầy đủ nằm trong `inventory/current-vps-state.md`.

## VPS

- Hostinger KVM 2, Ubuntu 24.04.4 LTS, 2 vCPU, 8 GB RAM, 100 GB đĩa.
- Đang chạy n8n và Hermes Agent bằng Docker Compose.
- PostgreSQL và Nginx đang chạy; Nginx hiện không phục vụ site hay chứng chỉ.
- `CHUNG_KHOAN_PRO` và Alibaba OneTalk đã bị xóa khỏi filesystem và dịch vụ đang chạy.
- Hai backup Hostinger cũ có thể vẫn chứa trạng thái trước khi xóa.

## Rủi ro ưu tiên

- SSH cho phép root và mật khẩu.
- XRDP và hai cổng Docker đang công khai.
- Hostinger firewall chưa có quy tắc.
- Có 90 gói cần nâng cấp và VPS cần khởi động lại.
- Hermes chạy bằng root trong container; image n8n/Hermes dùng tag `latest`.

## Nền tảng AI Automation TTD METAL

- Mục tiêu tổng thể: [PROJECT.md](PROJECT.md).
- Đã chuẩn hóa giao nhiệm vụ qua `tasks/`, kết quả qua `reports/`; [quy tắc](rules/AGENT_WORKFLOW.md).
- Đã hoàn tất [TTD-AI-PLATFORM-AUDIT-001](tasks/2026-11-21-n8n-hermes-integration-audit.md); xem [báo cáo live n8n ↔ Hermes](reports/2026-11-21-n8n-hermes-integration-audit.md).
- Đã xác minh n8n `2.45.7` và Hermes `0.22.5`; cả hai health/readiness PASS, 0 restart/OOM và có thể chạm nhau hai chiều qua host bridge.
- P0 Mức 1 đã triển khai hai runtime phụ cô lập trên `ttd-ai-p0-sandbox`: n8n sandbox có đúng một authenticated webhook và reasoner deterministic mock không provider/Internet egress.
- Structural E2E 9/9, negative auth, schema, callback, timeout/retry/idempotency và rollback/restore đều PASS. Production n8n/Hermes không restart, downtime 0, public port/firewall/DNS không đổi và paid inference call bằng 0.
- Mức 2 đã chạy: **Provider E2E PASS** qua GPT-6 Luna với đúng 1 paid attempt, 131 input + 73 output + 0 reasoning token và usage-based cost USD 0,0000496; authenticated callback, schema, replay và kill switch đều PASS. [Báo cáo Mức 2](reports/2026-11-21-n8n-hermes-p0-level2-results.md).
- **Hermes Agent E2E vẫn BLOCKED_COST_CONTROL**, nhưng khảo sát hard-cap đã complete: cấu hình/CLI upstream đơn thuần là NO-GO; phương án khả thi nhất là Hermes auxiliary nguyên bản sau private pre-dispatch guard dùng cùng ledger P0, cùng authenticated bridge/callback. Offline contract rehearsal đã PASS exact model, cap 600, no-tools, kill switch, idempotency và concurrency; chưa triển khai hoặc paid test. [Báo cáo feasibility](reports/2026-11-21-hermes-agent-e2e-hard-cap-feasibility.md).
- Kill switch persistent hiện bật, chặn task paid mới bằng HTTP 429; n8n production MCP vẫn tắt và production có 0 workflow.
- Kiến trúc được khuyến nghị: n8n làm control plane, Hermes reasoning qua API private, một internal Docker network, schema/policy/approval gate và media-worker FFmpeg riêng.

## Khảo sát năng lực và phối hợp các tác nhân

- Đã thiết lập [agents/README.md](agents/README.md) và hồ sơ ChatGPT, Codex, Hermes, Hostinger, n8n dựa trên báo cáo, GitHub connector và quan sát hPanel.
- ChatGPT đã xác minh GitHub read/write và có thể đọc tab Hostinger.
- Codex đã hoàn tất [capability survey](reports/2026-11-21-codex-capability-survey.md): local code/Git/browser/hPanel/VPS audit VERIFIED; local Docker daemon, marketing connectors, persistent execution và exact model còn BLOCKED/UNKNOWN theo session.
- Hermes đã hoàn tất [capability survey](reports/2026-11-21-hermes-capability-survey.md): GitHub write, skills/memory/session recall và WebUI tool surface VERIFIED; inference API, n8n MCP và connector business còn BLOCKED/UNKNOWN.
- Hostinger Agent đã hoàn tất [capability survey](reports/2026-11-21-hostinger-agent-capability-survey.md) với phạm vi hPanel/provider tools và các approval boundary.
- **Hostinger Account Inventory** đã được bổ sung tại [reports/2026-11-21-hostinger-account-capability-inventory.md](reports/2026-11-21-hostinger-account-capability-inventory.md): Cloud Startup (4 WordPress chính + staging, Builder/other site), VPS KVM 2, email, domain, Reach và resource Docker/AI. Báo cáo identity mới nhất xác nhận `ttdnew.tech` là U4S Hermes runtime tách biệt với Hermes trên KVM 2; OpenClaw chỉ là metadata plan không khớp runtime.
- Ba phần bổ sung của [TTD-AGENT-CAPABILITY-SURVEY-001](tasks/2026-11-21-agent-capability-survey.md) đã có báo cáo; quyền vẫn phải xác minh lại theo từng phiên/task.

## Định danh resource và tích hợp P0

- [TTD-RESOURCE-IDENTITY-001](tasks/2026-11-21-ttdnew-resource-identity-verification.md) đã complete: U4S `ttdnew.tech` và KVM 2 là hai runtime độc lập.
- [TTD-AI-P0-INTEGRATION-001](tasks/2026-11-21-n8n-hermes-p0-sandbox-integration.md) có kết quả `LEVEL1_PASS / PROVIDER_E2E_PASS / HERMES_E2E_BLOCKED`: sandbox workflow/callback và real GPT-6 Luna inference đã PASS; Hermes Agent route chưa đạt. Xem [báo cáo P0 Mức 1](reports/2026-11-21-n8n-hermes-p0-sandbox-integration.md) và [Mức 2](reports/2026-11-21-n8n-hermes-p0-level2-results.md).
- Không thay U4S, account business, public port/firewall hoặc production credential; downtime production 0. Paid usage Mức 2 là USD 0,0000496 theo response usage, chưa đối soát invoice.

- [ADR-P0-001](decisions/2026-11-21-p0-reasoning-integration-proposal.md) đã **APPROVED_WITH_RESTRICTIONS**: Mức 1 PASS; Mức 2 Provider PASS trong cap; [task Mức 2](tasks/2026-11-21-n8n-hermes-p0-level2-real-inference.md) hiện `blocked` riêng ở Hermes hard cost control.

- [TTD-HERMES-E2E-HARD-CAP-001](tasks/2026-11-21-hermes-agent-e2e-hard-cap-feasibility.md) đã complete ở chế độ read-only/offline với kết luận `GO_FOR_SEPARATE_IMPLEMENTATION_APPROVAL`. Đề nghị Hermes auxiliary + private inference guard + authenticated bridge; **chưa phê duyệt triển khai runtime phụ, thay egress, tạo secret mới, mở kill switch hoặc gọi AI thêm**. Kill switch vẫn bật.

- Đã tạo [ADR-P0-002](decisions/2026-11-21-hermes-auxiliary-guard-bridge-approval-proposal.md) **PROPOSED**, đề xuất GATE A chỉ triển khai Hermes auxiliary + guard + bridge, tạo 2 service secrets, mock full request capture và rollback; giữ kill switch ON, **0 paid Hermes call**. GATE B (một paid Hermes call) cần phê duyệt riêng sau khi mock PASS. Việc tạo tài liệu không cấp quyền thao tác VPS.

## Việc đang chờ

- Chưa thực hiện hardening SSH/XRDP hoặc firewall.
- Chưa đặt n8n/Hermes sau reverse proxy HTTPS.
- Chưa xử lý các backup Hostinger có thể chứa ứng dụng đã xóa.
- Chưa cập nhật hệ điều hành hoặc reboot.
- Provider E2E đã có evidence. Muốn tiếp tục Hermes Agent E2E cần phê duyệt triển khai guard/bridge/runtime phụ, mock capture full serialized Hermes request ≤4K, chứng minh không có direct egress/bypass và chỉ sau đó phê duyệt riêng một paid call; không được dùng adapter OpenAI trực tiếp để thay bằng chứng Hermes.
- Chưa kết nối/xác minh Google Ads, GA4, WordPress/WooCommerce, YouTube, TikTok, Meta, Kling, HeyGen hoặc ElevenLabs.

## Tài liệu tiếp theo

- Kiểm kê: `inventory/current-vps-state.md`
- Kiểm toán n8n ↔ Hermes: `reports/2026-11-21-n8n-hermes-integration-audit.md`
- Báo cáo bảo mật: `reports/2026-11-21-vps-security-review.md`
- Quy tắc an toàn: `rules/REPOSITORY_SECURITY.md`
