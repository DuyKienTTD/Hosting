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
- P0 Mức 1 đã thiết lập n8n sandbox và reasoner deterministic mock cô lập trên `ttd-ai-p0-sandbox`; GATE A hiện giữ n8n sandbox, dừng reasoner cũ để dùng authenticated bridge tới Hermes auxiliary/guard/mock, vẫn không public port.
- Structural E2E 9/9, negative auth, schema, callback, timeout/retry/idempotency và rollback/restore đều PASS. Production n8n/Hermes không restart, downtime 0, public port/firewall/DNS không đổi và paid inference call bằng 0.
- Mức 2 đã chạy: **Provider E2E PASS** qua GPT-6 Luna với đúng 1 paid attempt, 131 input + 73 output + 0 reasoning token và usage-based cost USD 0,0000496; authenticated callback, schema, replay và kill switch đều PASS. [Báo cáo Mức 2](reports/2026-11-21-n8n-hermes-p0-level2-results.md).
- **Hermes Agent paid E2E vẫn chưa được thực hiện**, nhưng GATE A mock đã PASS: Hermes auxiliary nguyên bản, private pre-dispatch guard, authenticated bridge/callback và provider mock chạy trên sandbox private; exact model, cap 600, full request tối đa 3.315 ASCII bytes, no-tools, no-bypass, idempotency/concurrency và rollback đều PASS. Kill switch vẫn ON, paid calls mới 0. [Báo cáo GATE A](reports/2026-11-21-hermes-gate-a-mock-results.md).
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

- [ADR-P0-001](decisions/2026-11-21-p0-reasoning-integration-proposal.md) đã **APPROVED_WITH_RESTRICTIONS**: Mức 1 PASS; Mức 2 Provider PASS trong cap; Hermes hard guard đã PASS mock ở GATE A, còn paid Hermes E2E chờ phê duyệt GATE B riêng.

- [TTD-HERMES-E2E-HARD-CAP-001](tasks/2026-11-21-hermes-agent-e2e-hard-cap-feasibility.md) đã complete ở chế độ read-only/offline với kết luận `GO_FOR_SEPARATE_IMPLEMENTATION_APPROVAL`; phương án được kiểm chứng tiếp trong GATE A.

- [ADR-P0-002](decisions/2026-11-21-hermes-auxiliary-guard-bridge-approval-proposal.md) **GATE A APPROVED** đã được thực hiện: [TTD-HERMES-GATE-A-001](tasks/2026-11-21-hermes-auxiliary-guard-bridge-gate-a.md) hiện `complete / GATE_A_MOCK_PASS`. Bốn service sandbox private healthy, mock E2E và corrected rollback PASS; production health HTTP 200, restart/downtime 0. GATE B chưa được phê duyệt và không được thực hiện.

- Đã review GATE A mock **PASS** dựa trên báo cáo/evidence GitHub; đã tạo [ADR-P0-003](decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md) **APPROVED_WITH_RESTRICTIONS (2026-11-21)** cho Codex thực hiện tối đa một Hermes Agent paid call. [Task Codex GATE B](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) đã giao; chỉ one-shot permit khóa lại trước dispatch, global kill switch vẫn ON, không mở toàn cục và không paid retry. **Chưa có evidence thực thi GATE B.**

- GATE B guard remediation đã **MOCK_INTEGRATION_PASS** với one-shot permit và shared-ledger reservation trên ledger copy; sandbox đã rollback về cấu hình GATE A sau test. Ledger thật, kill switch và production health được xác minh live; paid attempts mới 0, chi phí mới 0. [Báo cáo tổng hợp](reports/2026-11-21-hermes-gate-b-guard-remediation-results.md). GATE B paid execution tiếp tục `BLOCKED_PREFLIGHT` đến khi preflight live riêng PASS.

- **H1/H2 chuyên trách sau egress isolation (2026-11-21):** Báo cáo [GATE B egress isolation](reports/2026-11-21-hermes-gate-b-egress-isolation.md) xác nhận dedicated proxy network và 6 negative routes PASS; task mới mock callback PASS nhưng lỗi `HERMES_RUNTIME_MISMATCH` ban đầu chưa giải thích; accounting one-shot chưa PASS cùng callback trong một lượt. Guard chưa có provider credential, 3.308 bytes chưa có count provider, paid attempts mới 0, ledger thật 1 attempt, kill switch ON. Đã cập nhật [GATE B task](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) với hai handoff tham vấn Hostinger Agent (network, secret mount) và Hermes Agent (runtime, exact request).
- **Hermes H2 đã hoàn tất** tại [reports/2026-11-21-gate-b-hermes-consult.md](reports/2026-11-21-gate-b-hermes-consult.md) + [evidence](reports/evidence/2026-11-21-gate-b-hermes-consult.json): `HERMES_RUNTIME_MISMATCH` chưa chứng minh được mismatch live; cùng triệu chứng có thể xuất hiện do replay failed state theo `task_id` ở bridge. H2 cũng chốt canonical permit/hash nằm ở forwarded `/v1/responses` bytes sau guard, không phải body `/v1/runs`, và định nghĩa contract cho `/v1/responses/input_tokens`. One-shot accounting mock PASS; callback+one-shot combined đã có historical PASS nhưng chưa rerun ở checkpoint egress-isolation mới.
- **Hostinger H1 vẫn chờ** báo cáo chuyên trách; H3 `WAITING_FOR_REPORTS/OWNER_SYNTHESIS`, paid GATE B tiếp tục `BLOCKED_PREFLIGHT` và chưa có paid dispatch mới.

- H1 Hostinger đã DONE_RECEIVED_AND_REVIEWED: [báo cáo](reports/2026-11-21-gate-b-hostinger-consult.md), commit `5b8dd629`. Chỉ read-only, Gate A health/topology/mount metadata/backup verified, redeploy persistence và rollback chưa test. Phân biệt **OpenAI provider key guard-only** với `API_SERVER_KEY`/`guard-service token` nội bộ vốn có thể được chia cho các service cần auth; provider credential guard vẫn chưa được thiết lập/verified. Đã **khôi phục nhiệm vụ GATE B** sau khi H1 vô tình overwrite nội dung và đổi owner/status: task chính trở lại `owner: codex, status: blocked, paid_inference_approval: true`, H1 report vẫn giữ; H2 Hermes chờ bàn giao, H3 chưa giao Codex. Paid attempt mới 0, GATE B BLOCKED_PREFLIGHT.

- H2 Hermes đã DONE_RECEIVED_AND_REVIEWED: [báo cáo](reports/2026-11-21-gate-b-hermes-consult.md), commit `e0297d2`. HERMES_RUNTIME_MISMATCH có thể do bridge replay failed task_id; không có chứng cứ metadata lỗi live. Fingerprint phải khóa guard-forwarded /v1/responses body; provider token count phải bind cùng digest. Kết hợp callback + one-shot trên topology cô lập mới chưa rerun. H1 Hostinger cũng đã nhận và tổng hợp; cập nhật [GATE B task](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) với H3 cụ thể cho Codex, **PREPARED_FOR_OWNER_FORWARD**, chưa Codex ACK. Paid GATE B vẫn BLOCKED_PREFLIGHT; không có paid inference mới.

- **ChatGPT đã nghiệm thu H3 từ evidence (2026-11-21):** H3 `DONE_RECEIVED_AND_REVIEWED / MOCK_E2E_PASS`, không khẳng định đo lại trực tiếp VPS; GATE B vẫn `BLOCKED_PREFLIGHT` do guard chưa có OpenAI provider credential và chưa có provider token count theo final forwarded digest. H3 mock overlay đã rollback; không dùng SHA/3.345 bytes của mock làm paid permit. Chủ dự án là owner cấp credential qua secret mount kín; Codex chỉ thực hiện preflight targeted sau đó. [Task GATE B](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md), [H3](reports/2026-11-21-hermes-gate-b-h3-preflight.md).

- **H4 nhập OpenAI API Key an toàn đã `READY_FOR_OWNER_KEY_INPUT`:** Codex đã review/sửa interface terminal no-echo, Linux fake-key test 11/11 và Compose read-only PASS. Giao diện chỉ lưu file `0600` root-only, không tự mount/recreate container; fake key đã revoke và secret cuối absent. Production restart 0, ledger 1 attempt/0 permit, kill switch ON, paid delta 0. [Báo cáo H4](reports/2026-11-21-hermes-gate-b-h4-key-input-preparation.md). Handoff `PREPARED_FOR_OWNER_FORWARD` cho ChatGPT nghiệm thu; GATE B vẫn `BLOCKED_PREFLIGHT`.

- **ChatGPT nghiệm thu H4 (2026-11-21):** theo [báo cáo](reports/2026-11-21-hermes-gate-b-h4-key-input-preparation.md), [evidence](reports/evidence/2026-11-21-ttd-hermes-gate-b-h4.json) và code reviewed `f335752`: H4 `READY_FOR_OWNER_KEY_INPUT`, 11/11 Linux fake-key tests PASS, giao diện no-echo chỉ lưu staging secret chưa mount. Chủ dự án nhập riêng trong Hostinger Web Terminal và dừng ở `STORED_NOT_MOUNTED`; guard recreate/mount cần duyệt riêng. GATE B `BLOCKED_PREFLIGHT`; 0 paid attempts mới, kill switch ON. [Task](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md).

- **Chủ dự án đã tự nhập API Key trong Hostinger Web Terminal:** terminal trả `STORED_NOT_MOUNTED` sau nhập hai lần qua no-echo (bằng chứng do chủ dự án cung cấp, chưa được ChatGPT kiểm chứng độc lập trên VPS). Secret chỉ ở staging, chưa mount guard; không tự restart/recreate, chưa provider token-count, GATE B vẫn `BLOCKED_PREFLIGHT`. Codex tiếp theo chỉ chuẩn bị kiểm tra read-only + kế hoạch mount và xin quyền riêng trước recreate; không làm lại H3/H4 PASS. [Task](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md).

## Việc đang chờ

- [TTD-HERMES-GATE-B-GUARD-REMEDIATION-001](tasks/2026-11-21-hermes-gate-b-permit-ledger-remediation.md) đã **MOCK_INTEGRATION_PASS**: shared-lock interop, 20-process race, 14 fault cases và full mock E2E qua n8n→Hermes→guard→callback PASS. Sandbox đã rollback, production health 200/restart 0, ledger thật 1 attempt/kill switch ON và không đổi, paid calls mới 0. [Báo cáo nghiệm thu](reports/2026-11-21-hermes-gate-b-guard-remediation-results.md). Paid GATE B vẫn BLOCKED_PREFLIGHT, cần preflight live riêng.

- H3 Codex đã ACK và kiểm chứng combined mock E2E trên topology cô lập, gồm callback 200, duy nhất 1 dispatch mock và hạch toán one-shot. Rollback giữ nguyên Compose và sáu negative proxy tests PASS. GATE B paid vẫn `BLOCKED_PREFLIGHT` do thiếu credential riêng cho guard và số token provider cho digest cuối. Ledger thật giữ 1 attempt, 0 permit, kill switch ON. Paid attempt và chi phí mới đều 0. ChatGPT là người nhận nghiệm thu. [Báo cáo H3](reports/2026-11-21-hermes-gate-b-h3-preflight.md).

- Chưa thực hiện hardening SSH/XRDP hoặc firewall.
- Chưa đặt n8n/Hermes sau reverse proxy HTTPS.
- Chưa xử lý các backup Hostinger có thể chứa ứng dụng đã xóa.
- Chưa cập nhật hệ điều hành hoặc reboot.
- Provider E2E và GATE A mock đã có evidence. **GATE B đã được phê duyệt có điều kiện** cho tối đa đúng một Hermes Agent paid call; vẫn chờ Codex chạy/ghi evidence, không được tự đổi guard hay dùng adapter OpenAI trực tiếp để thay bằng chứng Hermes.
- Chưa kết nối/xác minh Google Ads, GA4, WordPress/WooCommerce, YouTube, TikTok, Meta, Kling, HeyGen hoặc ElevenLabs.

## Tài liệu tiếp theo

- Kiểm kê: `inventory/current-vps-state.md`
- Kiểm toán n8n ↔ Hermes: `reports/2026-11-21-n8n-hermes-integration-audit.md`
- Báo cáo bảo mật: `reports/2026-11-21-vps-security-review.md`
- Quy tắc an toàn: `rules/REPOSITORY_SECURITY.md`
