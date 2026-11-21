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
- P0 đã tạo internal bridge `ttd-ai-p0-sandbox` và gắn live n8n/Hermes bằng service DNS private; negative auth, n8n readiness, post-health và rollback preparation PASS, không restart/downtime/public port/firewall change.
- E2E reasoning vẫn `BLOCKED_BY_BUDGET_AND_RUNTIME`: n8n MCP đang tắt, chưa có workflow/callback và Hermes chưa expose agent inference API; không có paid inference call.
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
- [TTD-AI-P0-INTEGRATION-001](tasks/2026-11-21-n8n-hermes-p0-sandbox-integration.md) có kết quả `PARTIAL`: private network/DNS/health PASS; inference/workflow/callback còn blocked. Xem [báo cáo P0](reports/2026-11-21-n8n-hermes-p0-sandbox-integration.md).
- Không thay U4S, account business, public port/firewall hoặc credential; downtime 0 và chi phí API 0.

- Đã lập [ADR-P0-001](decisions/2026-11-21-p0-reasoning-integration-proposal.md) trạng thái **PROPOSED**: ưu tiên inference cô lập, webhook có xác thực cho 1 sandbox workflow, model/cost cap cần định giá rồi duyệt; chưa cấp quyền triển khai hay chi phí.

## Việc đang chờ

- Chưa thực hiện hardening SSH/XRDP hoặc firewall.
- Chưa đặt n8n/Hermes sau reverse proxy HTTPS.
- Chưa xử lý các backup Hostinger có thể chứa ứng dụng đã xóa.
- Chưa cập nhật hệ điều hành hoặc reboot.
- Chưa phê duyệt mode Hermes inference private, provider/model + cost cap, n8n instance-level MCP hoặc authenticated webhook/workflow để chạy lại test end-to-end.
- Chưa kết nối/xác minh Google Ads, GA4, WordPress/WooCommerce, YouTube, TikTok, Meta, Kling, HeyGen hoặc ElevenLabs.

## Tài liệu tiếp theo

- Kiểm kê: `inventory/current-vps-state.md`
- Kiểm toán n8n ↔ Hermes: `reports/2026-11-21-n8n-hermes-integration-audit.md`
- Báo cáo bảo mật: `reports/2026-11-21-vps-security-review.md`
- Quy tắc an toàn: `rules/REPOSITORY_SECURITY.md`
