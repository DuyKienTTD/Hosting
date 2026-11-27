---
id: ttd-p0-reasoning-integration-proposal-2026-11-21
type: decision
status: approved_with_restrictions
approval_level: 2
approved_at: 2026-11-21
updated_at: 2026-11-21
sensitivity: public
decision_owner: business-owner
related_task: ttd-ai-p0-integration-001
---

# ADR-P0-001 — Đề xuất hoàn tất n8n ↔ Hermes E2E

**ĐÃ PHÊ DUYỆT MỨC 1 VÀ MỨC 2 (2026-11-21), CÓ GIỚI HẠN.** Chủ dự án cho phép Codex tiếp tục sandbox cô lập, với **GPT-6 Luna** (`gpt-6-luna`) tối đa **5 lượt**, mỗi lượt **≤ 4.000 input tokens** và **≤ 2.000 output tokens**, trần **0,05 USD/ngày** và **0,05 USD tổng toàn P0**, dùng **dữ liệu giả**. Phải DỪNG nếu không chứng minh được kiểm soát chi phí, model ID, credential hay quyền truy cập. Không được thay Hermes image/container chính, thay public port/firewall/DNS, tác động U4S `ttdnew.tech`, tự tạo downtime hay thay business accounts. Nếu cần restart/recreate production, thay credential hiện có hoặc mở quyền mạng ngoài sandbox, dừng xin phê duyệt riêng.

## Bằng chứng

- [P0 integration report](../reports/2026-11-21-n8n-hermes-p0-sandbox-integration.md) và [JSON evidence](../reports/evidence/2026-11-21-ttd-ai-p0-integration-001.json): private Docker bridge `ttd-ai-p0-sandbox`, service DNS hai chiều, health/auth PASS, không restart/downtime.
- Hermes container Hostinger `0.22.5` chỉ phục vụ dashboard/control plane; `/v1/models` rơi về login/dashboard. Không có inference API đã kiểm chứng.
- n8n production vẫn giữ MCP disabled và 0 workflow. Mức 1 đã bổ sung một instance n8n sandbox độc lập với đúng một webhook workflow; đây không phải thay đổi production.
- [Identity report](../reports/2026-11-21-ttdnew-resource-identity-verification.md): `ttdnew.tech` U4S Hermes độc lập với KVM 2; không đụng vào U4S trong P0.

## Phương án được khuyến nghị

1. **Không thay image Hermes dashboard đang chạy.** Codex kiểm tra read-only liệu image/entrypoint hiện có hỗ trợ API inference thật; nếu không, ưu tiên chuẩn bị **Hermes API runtime phụ / adapter cô lập** kết nối private network. Chỉ triển khai khi rõ cơ chế auth, dữ liệu, isolation, rollback, resource limit và approval; không suy diễn upstream API mặc nhiên có sẵn trên Hostinger wrapper.
2. **Thử nghiệm n8n webhook/HTTP có xác thực trước MCP** cho một workflow `fake-ads-audit-v1`, vì phạm vi nhỏ, dễ kiểm tra schema, token, timeout và rollback. Nếu n8n webhook endpoint cần mạng phục vụ, bind private và không public. Giữ MCP như phương án mở rộng khi có nhiều tools/workflows và governance rõ. Không đánh đồng webhook với MCP.
3. **Provider/model và ngân sách:** Codex lập bảng lựa chọn từ quyền/account hiện có (model, provider, billing, price per input/output token, mức tiền tối đa ước lượng, số call), so sánh độ tin cậy và hỗ trợ tool use. **Không đọc/commit API key, không gọi model tính phí cho đến khi chủ dự án duyệt model, tổng cost cap và giới hạn mỗi job/ngày.** Đề xuất thử quy mô nhỏ nhất: một đến vài fake-data calls, cap riêng rõ bằng tiền; số cụ thể chờ xác minh pricing và phê duyệt.
4. **Tính bền vững:** bridge attach hiện tại có thể mất khi container recreate. Lập phương án cập nhật Compose/config sao cho private DNS tồn tại sau recreate, nhưng không thay compose thất lạc/bị drift, không recreate container khi chưa có backup, phiên bảo trì và rollback. Giữ public port/firewall hiện hữu không đổi ở thử nghiệm này; hardening là change batch riêng.
5. **Acceptance:** n8n trigger → Hermes **real inference** → authenticated callback/workflow n8n → JSON Schema, `task_id`, correlation ID, execution log, error/timeout/retry/idempotency tests; xác minh health, không phát sinh phí vượt cap, không chạm business account. Khả năng inference phải được chứng minh bằng output của model, không phải HTTP 200 của dashboard.
6. **Resource envelope:** KVM 2 chỉ 2 vCPU/8 GB; đánh giá CPU/RAM của service phụ. Tránh chạy model nặng cục bộ hay thêm database/queue layer chưa cần.

## Phê duyệt đã nhận và giới hạn hiệu lực

- **D1 APPROVED — Level 1:** nghiên cứu rồi có thể triển khai runtime inference phụ/adapter **cô lập** nếu preflight compatibility, giới hạn tài nguyên, service authentication, backup/rollback và khả năng không gián đoạn được chứng minh; không thay container Hermes chính.
- **D2 APPROVED — Level 1:** triển khai đúng **một authenticated webhook sandbox** với dữ liệu giả, không public mới và không bật instance-wide MCP; thực hiện schema/negative auth/dry-run tests khi có thể.
- **D3 APPROVED — Level 2 (2026-11-21):** chỉ `gpt-6-luna`, ≤5 calls tính cả retry, ≤4K input và ≤2K output tokens/call, trần ≤USD 0.05/ngày và ≤USD 0.05 toàn P0, fake data; paid calls chỉ sau khi kiểm chứng preflight model/price/cost control, key/egress bảo mật. Không tự chuyển model, nâng cap hoặc gọi công cụ tính phí.
- **D4 PENDING:** mọi thao tác có khả năng gây restart/downtime, thay public exposure hay đụng production business services cần phê duyệt riêng.
- Mọi bước cần điều kiện kỹ thuật chưa đáp ứng được ghi BLOCKED; không diễn giải phê duyệt Mức 1 là quyền vượt qua security gate.

## Quyết định đang chờ

- **D1:** Đồng ý định hướng inference private **cô lập** (không thay Hermes chính), nhưng chỉ sau Codex chứng minh compatibility, backup và rollback.
- **D2:** Đồng ý **authenticated webhook** cho một workflow sandbox trước; MCP để giai đoạn tiếp theo nếu cần.
- **D3:** Đã duyệt `gpt-6-luna` và giới hạn Mức 2 nêu trên. Nếu model ID, giá, quyền truy cập hoặc bộ kiểm soát chi phí không xác minh được, không được gọi API.
- **D4:** Mọi thay đổi cần restart/downtime/đụng public network đòi approval maintenance riêng.

## Kết quả thực thi Mức 1

- **D1 EXECUTED:** runtime phụ cô lập chạy deterministic mock, không provider và không Internet egress; có resource limits, healthcheck, root filesystem read-only và rollback riêng. Hermes chính không thay đổi.
- **D2 EXECUTED:** đúng một authenticated webhook `fake-ads-audit-v1` chạy trên n8n sandbox có data directory và khóa mã hóa độc lập; structural E2E 9/9 PASS.
- Backup/rollback/restore rehearsal PASS; n8n và Hermes production vẫn healthy, restart count 0, downtime 0.
- **D3 APPROVED sau khi Mức 1 hoàn tất:** chủ dự án đã cấp giới hạn paid pilot Mức 2; chưa có bằng chứng đã chạy real inference sau phê duyệt. Bảng provider/model và giá tham chiếu nằm trong báo cáo P0.

## Phân vai

- Codex: owner kỹ thuật, nghiên cứu feasibility, bản vá và kế hoạch triển khai.
- Hermes: đề xuất schema reasoning và xác minh API runtime với đúng phiên đang chạy.
- Hostinger Agent: xác minh VPS/U4S boundaries, backup và change impact.
- Chủ dự án: quyết định các gate D1-D4.

**Trạng thái:** APPROVED_WITH_RESTRICTIONS — Mức 1 đã PASS; Mức 2 được phê duyệt **để Codex thực hiện** theo [task riêng](../tasks/2026-11-21-n8n-hermes-p0-level2-real-inference.md), chưa có bằng chứng real inference đã chạy. Các thay đổi production/maintenance vẫn cần phê duyệt riêng.
