---
id: current-state
type: state
status: current
updated_at: 2026-11-22
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

- **Codex đã kiểm tra live metadata sau owner input:** `PRESENT`, mode `0600`, `mounted=false`; không đọc/băm/đo kích thước key và không chạy Compose. H4 owner entry ở `VERIFIED_LIVE_STORED_NOT_MOUNTED`; project/Responses/billing/token count vẫn chưa xác minh. Guard-only sandbox recreate/mount cần phê duyệt riêng; GATE B giữ `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-21-hermes-gate-b-h4-owner-key-live-check.md).

- **Chủ dự án đã phê duyệt riêng guard-only mount (2026-11-21):** cho phép Codex recreate **chỉ sandbox `guard`** với H4 overlay để mount OpenAI secret read-only, có backup/rollback, kiểm targeted six-container no-bypass, health, ports và ledger; **không** gọi provider, không mount sang service khác, không đổi production/kill switch/paid permit. [Task GATE B, mục phê duyệt guard mount](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md). `handoff_state: PREPARED_FOR_OWNER_FORWARD`, chưa Codex ACK; GATE B vẫn `BLOCKED_PREFLIGHT`.

- **Checkpoint GATE B — mount Guard vẫn chưa thực hiện:** Codex báo đã đọc approval ở `0e564e0` và đối chiếu overlay H4 từ repo, nhưng dừng trước recreate do chưa đọc xong rules mới và chưa kiểm tra live Compose/backup/rollback. Không có runtime change hay provider call; không có nghiệm thu mount. Chủ dự án đã phê duyệt guard-only mount, approval vẫn có hiệu lực trong phạm vi cũ; Codex phải hoàn tất preflight chỉ đọc trước khi thao tác. GATE B `BLOCKED_PREFLIGHT`. [Checkpoint](reports/2026-11-21-hermes-gate-b-guard-mount-paused-checkpoint.md).

- **2026-11-22 — Guard-only mount `GUARD_MOUNT_PASS`:** Kết nối lại KVM2 qua Chrome và recreate đúng sandbox Guard với mount chỉ đọc. Guard/proxy healthy, 18/18 phép thử cách ly sau recreate đạt, production HTTP 200/restart 0 và ledger khớp từng byte. Paid GATE B vẫn `BLOCKED_PREFLIGHT` cho đến bước provider preflight riêng. [Báo cáo](reports/2026-11-22-hermes-gate-b-guard-mount-results.md).

## Việc đang chờ

- **H6 B2-F source/mock PASS (2026-11-22)** — Guard transport hard-disabled, writer P0 v1 ký ACK sau reserve, exact bytes, JSON/SSE, unknown outcome, crash và callback giả đạt offline. ChatGPT nghiệm thu. Live apply giữ `BLOCKED_UID_OR_MOUNT`, paid giữ `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-f-source-mock.md).

- **ChatGPT H6 B2-E accepted / B2-F opened (2026-11-22):** `H6_B2_E_ACCEPTED / VERIFIED_KVM2_MOCK / ROLLBACK_PASS` theo Codex `e4269f0` (4 service, 4 private volumes, UID 0 caps 0, ext4 mock/HMAC, 1/4 ACK, crash fail-closed, callback fake, production và metadata ledger thật không đổi). Mở `H6_B2_F_REAL_PATH_SOURCE_MOCK_AUTHORIZED` cho Codex lập trình tuyến provider/ledger thực **chỉ trong source và mock dữ liệu giả**, hard-disabled, không dùng secret/real ledger, không provider request hoặc paid. Live apply `BLOCKED_UID_OR_MOUNT`, paid `BLOCKED_PREFLIGHT`. [Reviewer](reports/2026-11-22-hermes-gate-b-h6-b2-e-chatgpt-review.md).

- **H6 B2-E KVM2 mock PASS (2026-11-22)** — HMAC v2, no-bypass, Level 2/ext4, 1/4 signed ACK, hai ca crash mất ACK, callback mô phỏng và rollback PASS. Inventory GATE A/production và metadata ledger thật khớp pre/post. ChatGPT nghiệm thu. Live apply giữ `BLOCKED_UID_OR_MOUNT`, paid GATE B giữ `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-e-kvm2-mock.md).

- **ChatGPT B2-D nghiệm thu / mở B2-E (2026-11-22):** `H6_B2_D_CODE_MOCK_ACCEPTED` theo source Guard/writer HMAC v2, Docker local evidence tại `cf36e59`. `H6_B2_E_KVM2_ISOLATED_AUTH_MOCK_AUTHORIZED` cho Codex dựng project mock KVM2 riêng sau full rendered Compose collision gate, chỉ ledger/khóa giả và rollback; không chạm GATE A/production/ledger/permit thật hoặc provider/paid. Handoff PREPARED, chờ Codex ACK. Live apply `BLOCKED_UID_OR_MOUNT`, paid `BLOCKED_PREFLIGHT`. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-d-chatgpt-review.md).

- **H6 B2-D code/mock PASS (2026-11-22)** — Guard/writer dùng IPC HMAC hai chiều ở UID 0, socket B2-D riêng và khóa giả RO. Mock đã kiểm tamper, replay, Level 2, crash và rollback. ChatGPT nghiệm thu. Live apply giữ `BLOCKED_UID_OR_MOUNT`, paid giữ `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-d-ipc-integration.md).

- **H6 B2-C ChatGPT review / B2-D open (2026-11-22):** Chấp nhận `H6_B2_C_UID_MODEL_OFFLINE_PASS` trên Docker Desktop, chọn writer UID 0 bỏ caps, HMAC hai chiều, không ACL-only. **HMAC hiện chỉ nằm trong fixture**, chưa ở Guard/writer deployable. Mở `H6_B2_D_IPC_INTEGRATION_OFFLINE_AUTHORIZED` cho Codex tích hợp mã và thử mock, tuyệt đối chưa apply KVM2/ledger thật/provider/paid. Live apply `BLOCKED_UID_OR_MOUNT`; paid `BLOCKED_PREFLIGHT`. [Reviewer](reports/2026-11-22-hermes-gate-b-h6-b2-c-chatgpt-review.md).

- **H6 B2-C offline PASS (2026-11-22)** — writer UID 0 bỏ toàn bộ caps và xác thực HMAC hai chiều qua Unix socket đạt trên ledger giả. UID 23062 với ACL lỗi ở lock `fchmod` và mất quyền sau Level 2 ghi. ChatGPT nghiệm thu trước mọi quyết định apply. Live apply giữ `BLOCKED_UID_OR_MOUNT`, paid GATE B giữ `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-c-uid-model.md).

- **H6 B2-B reviewed (2026-11-22):** `READ_ONLY_PREFLIGHT_ACCEPTED`, live apply `BLOCKED_UID_OR_MOUNT`: ledger/lock root:root 0600, directory 0700; writer UID 23062 cannot access. ChatGPT opens `H6_B2_C_UID_MODEL_OFFLINE_AUTHORIZED` for Codex: compare root-owned no-capabilities writer and nonroot ACL on fake root-owned ledger, test IPC peer auth and Level 2 concurrency, offline-only, no KVM2 apply, no real-ledger/permit/provider/paid/production. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-b-chatgpt-review.md).

- **H6 B2-B đã kiểm chỉ đọc (2026-11-22):** `H6_B2_B_READ_ONLY_PREFLIGHT_COMPLETE`, apply `BLOCKED_UID_OR_MOUNT`. Ledger/lock `0:0` mode `0600` và parent `0700` không ACL, writer UID 23062 không có quyền. Preview Compose và rollback render đã đối chiếu. ChatGPT nghiệm thu theo §10. GATE B paid `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-b-preflight.md).

- **B2-A nghiệm thu & B2-B read-only mở (2026-11-22):** ChatGPT `H6_B2_A_ACCEPTED` trên bằng chứng offline Codex và mã Level 2; 1/4 admission ACK, hai crash không ACK, 14 từ chối. Phát hiện Level 2 `atomic_write` chưa fsync directory. Cho phép Codex `H6_B2_B_READ_ONLY_PREFLIGHT`: kiểm KVM2 UID/mount/lock bằng stat/inspect và render overlay đề xuất offline; **không đổi quyền/ghi ledger thật, không recreate, không provider/paid**. GATE B `BLOCKED_PREFLIGHT`. [Reviewer](reports/2026-11-22-hermes-gate-b-h6-b2-a-chatgpt-review.md).

- **H6 B2-A hoàn tất offline (2026-11-22):** Codex ACK `8d705b0`, bàn giao `H6_B2_A_COMPLETE` với schema P0 v1, lock Level 2, atomic admission và settlement trên fixture giả. ChatGPT nghiệm thu và quyết định bước an toàn kế tiếp theo §10. Quyền UID/lock trên KVM2 và rollback là gate của B2-B. GATE B paid giữ `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-a.md).

- **H6 Stage B1 ChatGPT nghiệm thu (2026-11-22):** `H6_STAGE_B1_ACCEPTED / VERIFIED_KVM2_MOCK / ROLLBACK_PASS` từ code/review và evidence Codex: 8/8 mock, 6/6 proxy no-bypass, project thử riêng đã dọn, GATE A/production/ledger thật không đổi theo postflight. Chưa xác minh Hermes/provider/ledger thật trong B2; Stage B2/C chưa được phép. GATE B paid `BLOCKED_PREFLIGHT`. [Reviewer](reports/2026-11-22-hermes-gate-b-h6-stage-b1-chatgpt-review.md).

- **H6 Stage B1 đạt trên KVM2 (2026-11-22):** Codex ACK approval `6e5ee58`. Project mock riêng đạt cổng render, 8/8 ca mock, 6/6 no-bypass và rollback. GATE A, production và ledger thật khớp baseline. ChatGPT là next owner review. Stage B2/C chờ phê duyệt riêng và Paid GATE B giữ `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-stage-b1.md).

- **H6 Stage A nghiệm thu (2026-11-22):** ChatGPT `H6_STAGE_A_ACCEPTED / VERIFIED_OFFLINE_MOCK` theo source `a411114` và Codex evidence `5a70e3b`. 8/8 mock PASS; chưa chạy Hermes đích hoặc KVM2 runtime, chưa ghi ledger thật/gọi provider. Stage B chỉ được xem xét sau quyết định chủ dự án, ưu tiên Stage B1 sandbox mock riêng, không gộp quyền writer ledger thật/provider. GATE B `BLOCKED_PREFLIGHT`. [Reviewer](reports/2026-11-22-hermes-gate-b-h6-stage-a-chatgpt-review.md).

- **H6 Stage A hoàn tất (2026-11-22):** Codex ACK approval `c1fe91c` và bàn giao `H6_STAGE_A_COMPLETE / VERIFIED_OFFLINE_MOCK`. Guard/writer, IPC, admission durable và overlay đã kiểm trên fixture Linux cục bộ. ChatGPT review trước khi chủ dự án quyết định Stage B. Stage B/C chưa duyệt và Gate B paid `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-stage-a.md).

- **ChatGPT review thiết kế H6 (2026-11-22):** `H6_PREPARATION_ACCEPTED / ARCHITECTURE_CONDITIONALLY_ACCEPTED`. Tách ledger writer với Unix socket phù hợp về hướng, nhưng cần ràng buộc peer auth, lock/inode, crash, thử mock và rollback. **Chưa duyệt apply/recreate Guard hoặc writer**, chưa được chạm ledger thật/permit/paid. Owner quyết định scope sandbox sau khi có patch và bằng chứng test. GATE B `BLOCKED_PREFLIGHT`. [Review](reports/2026-11-22-hermes-gate-b-h6-chatgpt-design-review.md).

- **H6 chuẩn bị xong (2026-11-22):** Codex đã ACK và nộp `H6_PREPARATION_COMPLETE / NEEDS_OWNER_DECISION`. Guard live mock-only, ledger bind theo file chỉ đọc, proposal writer giới hạn chờ ChatGPT nghiệm thu và chủ dự án duyệt phạm vi triển khai sandbox. H5 đã được nghiệm thu và Gate B paid tiếp tục `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-preparation.md).

- **ChatGPT nghiệm thu H5 (2026-11-22):** `H5_ACCEPTED / PROVIDER_PREFLIGHT_PASS` trong phạm vi dashboard/project, token count 723 và one-shot mock. Không nghiệm thu H6/paid route; Guard live mock-only, ledger mount RO; paid GATE B `BLOCKED_PREFLIGHT`. [Reviewer](reports/2026-11-22-gate-b-chatgpt-provider-and-scope-review.md).

- **ChatGPT review H5 follow-up (2026-11-22):** bằng chứng mới xác minh project/key qua dashboard và metadata an toàn, Standard/pay-as-you-go, 723 input tokens cho digest ứng viên, mock exact-byte one-shot PASS. Tuyến Guard live vẫn mock-only và ledger thật mount RO; paid GATE B `BLOCKED_PREFLIGHT`, không paid dispatch. [Review](reports/2026-11-22-gate-b-chatgpt-provider-and-scope-review.md).

- **H5 Provider preflight:** Codex báo `PROVIDER_PREFLIGHT_PASS` với bằng chứng quản trị project, 723 input tokens cho digest ứng viên và exact-byte one-shot trên ledger mock. ChatGPT là next owner nghiệm thu. Guard live vẫn ở chế độ mock và paid GATE B tiếp tục `BLOCKED_PREFLIGHT` chờ duyệt và xác minh tuyến H6. [Báo cáo](reports/2026-11-22-hermes-gate-b-h5-preflight-followup.md).

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
