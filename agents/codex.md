---
id: agent-codex
type: knowledge
status: current
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
---

# Codex — kỹ thuật, kiểm toán, xây dựng và triển khai

**Role ưu tiên:** software/infrastructure engineer; thiết kế, code, test và vận hành API, Docker, network, workflow, media-worker và CI khi task cấp đúng quyền. Hồ sơ là bằng chứng năng lực, không phải quyền production.

## Identity và môi trường đã xác minh

- Codex chạy trong ChatGPT desktop app trên Windows; app `26.1117.41037`, build `29803`, kênh production tại lần kiểm tra 2026-11-21.
- Exact model/reasoning effort không được tool/session metadata expose: `UNKNOWN`.
- Phiên khảo sát có local PowerShell, filesystem read/write, network và Git trong checkout `Hosting`.
- Local shell và VPS là hai runtime khác nhau. VPS được truy cập qua hPanel/Web Terminal đã đăng nhập; direct SSH local chưa test.
- Permission/network/browser/account state là **session-scoped** và phải kiểm tra lại ở task tương lai.

## VERIFIED

- Đọc/sửa file, chạy command/test, review diff, commit/push GitHub bằng Git HTTPS.
- Toolchain local có Git, ripgrep, Node.js, Python, OpenSSH và PowerShell.
- Browser/Computer Use trên Windows; đọc hPanel đang đăng nhập trong current session, có confirmation gate cho action nhạy cảm.
- Audit VPS read-only qua Hostinger Web Terminal; kiểm kê Docker/image/network/storage/resource.
- Debug live n8n `2.45.7` và Hermes dashboard `0.22.5`; xác định health, auth, network và blocker MCP/inference/E2E.
- Triển khai P0 Level 1 cô lập: n8n sandbox, authenticated webhook, mock adapter, schema/callback/retry/idempotency, resource limits và rollback/restore; structural E2E 9/9 PASS mà không tác động production.
- Tải/đối chiếu official docs, dùng skills, tạo report/evidence đã redaction và cập nhật state/catalog/changelog.

Nguồn: [Codex capability survey](../reports/2026-11-21-codex-capability-survey.md), [live audit](../reports/2026-11-21-n8n-hermes-integration-audit.md) và [evidence](../reports/evidence/2026-11-21-ttd-ai-platform-audit-001.json).

## AVAILABLE_UNTESTED

- Tạo branch/worktree/PR và cấu hình CI; repo hiện chưa có GitHub Actions workflow.
- Direct SSH read-only bằng account least-privilege; SSH client có mặt nhưng auth chưa test.
- Triển khai Docker/Compose, internal network, reverse proxy/TLS, monitoring và hardening sau approval riêng.
- Xây n8n workflow, Hermes API adapter, schema/idempotency/retry/error workflow và media-worker FFmpeg.
- Dùng document/PDF/spreadsheet/presentation/image skills khi task cần.
- Dùng Codex goal/automation/worktree/remote-control surfaces; chưa xác minh chạy bền khi UI/host đóng.

## BLOCKED / DEGRADED / UNKNOWN

- Local Docker CLI có nhưng Docker Desktop daemon không chạy: `BLOCKED_LOCAL_DAEMON`.
- GitHub CLI bị precedence bởi `GITHUB_TOKEN` không hợp lệ; Git HTTPS vẫn VERIFIED. Không dựa vào `gh` cho đến khi có task dọn cấu hình.
- 0 MCP resources/templates được expose; không có marketing/website/media connector trong phiên.
- n8n production MCP disabled, Hermes chính chưa expose inference API và production có 0 workflow; real-model E2E vẫn chờ Mức 2 dù structural sandbox E2E đã PASS.
- Google Ads/GA4, WordPress/WooCommerce, YouTube/TikTok/Meta, Kling/HeyGen/ElevenLabs API scopes và credentials: `BLOCKED/UNKNOWN`.
- Durable memory ngoài chat/Git, model/cost/quota và execution 24/7 khi app đóng: `UNKNOWN`.
- Không có quyền tự sửa production chỉ vì từng đọc root Web Terminal.

## Nhiệm vụ nên giao Codex

1. Code/API adapters/test harness/schema/migration có rollback.
2. Docker, network, TLS, observability, security hardening theo task đã duyệt.
3. n8n↔Hermes sandbox/E2E, queue/retry/idempotency/callback và monitoring.
4. Media-worker/FFmpeg, storage lifecycle và CI/release engineering.
5. Technical audit, incident diagnosis, evidence/report và Git handoff.

## Việc nên phối hợp hoặc giao bên khác

- Hermes cho reasoning/content/tool execution sau khi API/MCP an toàn.
- n8n cho schedule, connector, execution state và retry.
- Hostinger/hPanel cho provider control plane theo approval.
- ChatGPT/business owner cho yêu cầu, priority và review nghiệp vụ.
- Con người cho credentials, ngân sách, Ads write, publish và thay đổi DNS/SSH/firewall.

## Thực thi liền mạch trong quyền hiện hành

- Áp dụng [AGENT_WORKFLOW mục 9](../rules/AGENT_WORKFLOW.md): tự hoàn thành các phép kiểm tra còn thiếu và những bước hợp lệ trong scope đã duyệt; không kết thúc nhiệm vụ chỉ vì preflight chưa đo.
- STOP thao tác ghi/recreate/paid khi thiếu điều kiện an toàn, nhưng tiếp tục các bước read-only hoặc độc lập an toàn. Nếu không thể tiếp tục vì phiên/công cụ, ghi blocker hoặc INTERRUPTED_BY_ENVIRONMENT có bằng chứng.
- Không tự retry paid inference, không vượt approval, không coi báo cáo tiến độ là nghiệm thu cuối.

## Cách nhận và bàn giao

- Nhận task từ URL/file Git hoặc prompt chat; n8n/API chưa nối trực tiếp vào Codex session.
- Có thể dùng Codex threads/subagents khi người dùng yêu cầu; không tự spawn trong survey này.
- Bàn giao bằng report có ngày, code/config, evidence đã làm sạch, commit/PR và trạng thái PASS/FAIL/BLOCKED.
- Không đảm bảo tiếp tục khi app/host dừng. Automation/worktree cần cấu hình và vẫn không thay n8n/DB làm job-state store.

## Approval và an toàn

- Production mutation, restart/recreate, firewall/SSH/DNS/SSL, credentials, paid API, Ads write và publish cần task + approval riêng.
- Browser access tới account đã đăng nhập không phải API scope hoặc quyền đại diện.
- Mọi diff public phải scan secret/IP/hostname/cookie/raw log trước push.
- Quyền và tools phải xác minh lại theo từng chat/host; không lấy hồ sơ này làm ủy quyền.

## Ba phép thử tiếp theo đề xuất

1. Real-model fake-data E2E trong sandbox sau approval provider/model và cost cap Mức 2.
2. Branch/PR + repository validator/secret-scan CI smoke test.
3. Direct SSH read-only bằng user least-privilege, đối chiếu inventory với hPanel.
