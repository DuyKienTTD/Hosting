---
id: ttd-ai-p0-integration-001
type: task
status: in_progress
approval_level: 1
updated_at: 2026-11-21
sensitivity: public
owner: codex
support: [hostinger-agent, hermes]
depends_on: [ttd-resource-identity-001]
execution_result: partial
---

# TTD-AI-P0-INTEGRATION-001 — Tích hợp sandbox n8n ↔ Hermes (sau xác minh resource)

## Mục tiêu

Tạo bằng chứng **n8n → Hermes AI reasoning → n8n callback/workflow → kết quả JSON có schema**, với dữ liệu quảng cáo giả lập, task ID, log đã khử nhạy cảm, kiểm soát lỗi và rollback. Triển khai P0 **trên đúng runtime đã xác nhận**; không gây gián đoạn WordPress/Ads/media và không tạo dịch vụ/public API ngoài phạm vi.

## Gate bắt buộc

**GATE-ID (hard stop):** đọc kết quả [TTD-RESOURCE-IDENTITY-001](2026-11-21-ttdnew-resource-identity-verification.md). Chỉ triển khai trên môi trường KVM 2 đã đo live nếu xác minh nó là target đúng và không xung đột resource `ttdnew.tech`. Nếu identity chưa rõ, **không đổi network, API, MCP, Docker**; chỉ chuẩn bị proposal và báo BLOCKED.

**GATE-CHANGE:** xác nhận live versions/config hiện tại; sao lưu config/compose và dữ liệu cần thiết, kiểm tra khôi phục/rollback khả thi, capture pre-change health, xác nhận đường truy cập admin không bị cắt, xác định cửa sổ thao tác và phương án khôi phục khi lỗi. Một bản backup cũ có mặt không phải bằng chứng restore đã kiểm thử. Tránh động chạm resource khác.

**GATE-COST:** Không sử dụng LLM/media API phát sinh chi phí ngoài hạn mức đã được chủ dự án duyệt. Nếu test inference không thể chạy với quyền/model đã được phép và không có mức chi phí xác định, dừng ở `AWAITING_BUDGET_APPROVAL`. Có thể hoàn tất network/auth/schema dry-run trước.

## Quyền được hiểu từ yêu cầu hiện tại

Chủ dự án đã yêu cầu xác minh resource rồi triển khai P0. Cho phép Codex chuẩn bị và thực hiện **thay đổi sandbox tối thiểu, có thể rollback** sau khi thỏa các gate và không cần cài thêm hạ tầng trả phí. Quyền này **không bao gồm** sửa Google Ads, WordPress, DNS, production firewall/SSH/public port đang phục vụ người dùng, thay credential hiện hữu, publish hoặc tạo/gọi paid API chưa có hạn mức. Các thay đổi gây downtime/cắt kết nối, chuyển resource hoặc làm tăng chi phí phải lập phương án và xin duyệt riêng.

## Phân vai

- **Codex (owner):** xác minh target, xây phương án và triển khai kỹ thuật sandbox có rollback, kiểm thử n8n/Hermes auth/network/API/MCP, lưu evidence.
- **Hostinger Agent:** phân loại resource Hostinger, hỗ trợ backup/firewall/Docker/hPanel và kiểm tra rủi ro; chỉ thực thi phần được phê duyệt.
- **Hermes:** cung cấp schema reasoning, kiểm tra khả năng agent inference/MCP có trong runtime, QA logic và báo cáo; không tự thay đổi hạ tầng.
- **ChatGPT:** review evidence, yêu cầu, quyết định business khi người dùng gọi; không làm dependency 24/7.
- **n8n:** runtime điều phối, callback/execution logs sau khi workflow được tạo.

## Các bước kỹ thuật linh hoạt

1. Xác minh network segregation: n8n và Hermes đang chạy bridge riêng theo [audit](../reports/2026-11-21-n8n-hermes-integration-audit.md); thiết kế private Docker network, DNS service và credentials riêng tối thiểu; không dùng admin dashboard cookie cho inference service.
2. Đánh giá có thể kích hoạt **Hermes inference API internal-only** trên Hostinger-specific image không. Kiểm tra compatibility với upstream `API_SERVER_ENABLED`; đừng mặc định dashboard `0.22.5` hỗ trợ endpoint `/v1/*`. Nếu không, đánh giá adapter cô lập hoặc Hermes runtime phụ an toàn; không thay image chính khi chưa duyệt.
3. Bật n8n instance-level MCP hoặc thay bằng webhook/REST có xác thực **chỉ cho một workflow sandbox**. Chọn đường thực tế ít rủi ro hơn; không bật mọi workflow.
4. Tạo workflow `fake-ads-audit-v1`: input ví dụ `{channel:"ads",spend:100,clicks:10}`; Hermes trả nhận xét cấu trúc, n8n validate JSON Schema; callback gồm `task_id`, `correlation_id`, status, timings, result hash, lỗi có thể hiểu. Không kết nối tài khoản thật.
5. Kiểm tra token sai/thiếu, request hợp lệ, timeout, invalid JSON, retry có giới hạn, idempotency chạy lại, app health sau đổi. Không load/stress-test hoặc gây chi phí bất ngờ.
6. Đảm bảo không expose inference API, media worker hay raw logs ra Internet. Reverse proxy TLS/đóng các cổng public là một **change batch riêng** sau khi đã có đường thay thế, kiểm tra login/rollback và được duyệt; không tự cắt đường truy cập hiện tại.
7. Cập nhật bản đồ service topology, runbook rollback, trạng thái/vấn đề phát hiện. Đánh giá giới hạn 2 vCPU/8GB, chi phí model và khả năng vận hành nền; tránh quảng cáo 24/7 production-ready khi chưa có evidence.

## Nghiệm thu P0

- Identity gate PASS, đúng target không nhầm `ttdnew.tech` với VPS.
- Live service n8n & Hermes giữ healthy và admin access duy trì.
- Test private service DNS/auth PASS, không dùng cổng public để hai container gọi nhau.
- n8n gọi được **agent reasoning** thật qua endpoint private (không chỉ dashboard health).
- Hermes gọi đúng một workflow n8n có schema, auth và log; luồng end-to-end có task ID, final state và evidence.
- Test lỗi có kết quả rõ, rollback đã chuẩn bị và health sau thay đổi PASS.
- Không động chạm accounts business, không publish, không phát sinh API phí ngoài mức cho phép.

Nếu chưa được phép call inference, báo **PARTIAL** và tách riêng phần `BLOCKED_BY_BUDGET`, tuyệt đối không tạo PASS giả.

## Bàn giao

Tạo `reports/2026-11-21-n8n-hermes-p0-sandbox-integration.md` hoặc file ngày thực tế; ghi lại thao tác thực hiện vs đề xuất, schema, evidence kết nối, test matrix, downtime (nếu có), chi phí thực tế, thay đổi cấu hình đã redacted và rollback. Cập nhật `STATE.md`, `CATALOG.yaml`, `CHANGELOG.md`; push GitHub, trả URL report và commit. Không đưa secret, private endpoint, IP, tài khoản đăng nhập vào repo public.

## Phê duyệt Mức 1 — 2026-11-21

Chủ dự án phê duyệt tiếp tục P0 theo [ADR-P0-001](../decisions/2026-11-21-p0-reasoning-integration-proposal.md), **chỉ trong sandbox cô lập**. Codex được khảo sát kỹ thuật, chuẩn bị và triển khai runtime phụ/adapter private (nếu compatibility, backup, resource/cost isolation và rollback đều đạt) và **một authenticated webhook workflow giả lập**. Không thay image/container Hermes chính, không bật MCP instance-wide, không mở public endpoint/đổi firewall/DNS, không chạm U4S `ttdnew.tech` và không sửa business account. Nếu thay đổi ảnh hưởng production, restart/recreate hoặc downtime, **dừng xin approval riêng**. Việc chọn provider/model, trần chi phí và mọi paid inference call thuộc Mức 2 **chưa được phê duyệt**. Có thể kiểm thử HTTP/auth/schema và mock reasoning miễn phí; tuyệt đối không đánh dấu E2E real reasoning PASS bằng mock.

### Bàn giao tiếp theo của Codex

- Feasibility runtime inference cô lập, service auth, backup/rollback và giới hạn tài nguyên.
- Một webhook sandbox với dữ liệu giả, token riêng, schema validation, timeout/negative auth và execution evidence nếu có thể làm không gián đoạn.
- Bảng các provider/model có thể dùng, đơn giá đã xác minh và đề xuất cost cap cho chủ dự án chọn.
- Báo cáo live các bước đã triển khai, blocker Mức 2; commit/push report + evidence đã khử nhạy cảm.

## Tiến độ thực thi 2026-11-21

- [x] `GATE-ID` PASS; target là KVM 2, không phải U4S `ttdnew.tech`.
- [x] Pre-change health, restart count, disk, network conflict và admin access được kiểm tra live.
- [x] Tạo `ttd-ai-p0-sandbox` với `internal=true`; gắn n8n/Hermes bằng service alias, không restart hoặc đổi public port/firewall.
- [x] Private DNS hai chiều, negative auth, n8n health, n8n MCP state và post-change health được test.
- [x] Backup config cần thiết, checksum và rollback script đã chuẩn bị.
- [ ] Hermes private inference: **BLOCKED_BY_RUNTIME_AND_BUDGET**.
- [ ] Một n8n workflow có auth/schema/callback: **BLOCKED_BY_MCP/WORKFLOW**.
- [ ] E2E reasoning thật: chưa chạy; không tạo PASS giả, không phát sinh API fee.

Kết quả chi tiết: [báo cáo P0](../reports/2026-11-21-n8n-hermes-p0-sandbox-integration.md) và [evidence JSON](../reports/evidence/2026-11-21-ttd-ai-p0-integration-001.json).
