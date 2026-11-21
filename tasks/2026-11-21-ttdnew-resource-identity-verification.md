---
id: ttd-resource-identity-001
type: task
status: current
updated_at: 2026-11-21
sensitivity: public
owner: hostinger-agent
support: [codex]
depends_on: []
---

# TTD-RESOURCE-IDENTITY-001 — Xác minh resource `ttdnew.tech`

## Mục tiêu

Xác định chính xác resource Docker Hosting / AI automation đang gắn `ttdnew.tech`: loại resource/product trong Hostinger, runtime thực chạy là gì, có phải OpenClaw hay Hermes (hay metadata/template đã đổi), nằm ở môi trường nào, có quan hệ hoặc trùng với Hermes Docker container trên KVM 2 không. **Không đưa ra kết luận khi chưa có bằng chứng**.

## Đọc trước

- [Quy tắc](../AGENTS.md), [agent directory](../agents/README.md) và [hồ sơ Hostinger](../agents/hostinger.md).
- [Hostinger account inventory](../reports/2026-11-21-hostinger-account-capability-inventory.md).
- [Kiểm toán n8n ↔ Hermes trên VPS](../reports/2026-11-21-n8n-hermes-integration-audit.md).
- [P0 integration task — chỉ bắt đầu sau gate của task này](2026-11-21-n8n-hermes-p0-sandbox-integration.md).

## Phương pháp mở: kiểm chứng danh tính, không đổi trạng thái

Hostinger Agent là owner khảo sát account/control plane; Codex giúp kiểm tra bản đồ runtime/VPS khi cần. Tùy công cụ có quyền, đối chiếu:

1. **Resource Hostinger**: product/resource ID loại đã che, vùng chạy, loại hosting, preview domain, custom domain `ttdnew.tech`, app/template/metadata label, lifecycle và cấp quản trị.
2. **Runtime thực tế**: tên instance/process/container được công cụ trả về; image/tag/digest/app version/entrypoint/health/logs đã lọc bí mật. Đánh giá OpenClaw, Hermes, app wrapper hay alias; không định danh chỉ từ `u4s-hermes-agent`.
3. **Ranh giới**: đối chiếu resource Docker Hosting với VPS KVM 2 (compose/container ID/image/volume/network/domain binding) mà không nhầm phần mềm, shell, tài khoản, filesystem và network. Có thể là resource tách biệt; đánh dấu VERIFIED hoặc UNKNOWN.
4. **Mục đích và rủi ro**: resource có đang phục vụ khách hàng/channel/data không; tác động nếu tắt/chuyển; có backup và quyền xuất/đọc cấu hình không.
5. **DNS/HTTP**: chỉ kiểm tra chỉ-đọc, không đưa IP, hostname, cookie, key, private route, token vào Git public; HTTPS/response bên ngoài chỉ là tín hiệu phụ, không đủ để chứng minh runtime identity.

## Điều kiện chốt GATE-ID

Báo cáo phải trả lời được:
- `ttdnew.tech` đang gắn resource nào, nền tảng/provider nào, runtime nào, có bằng chứng trực tiếp và mức tin cậy nào?
- Resource này **trùng với**, **độc lập với**, hay **chưa phân biệt được** so với container Hermes của VPS KVM 2?
- Chọn rõ **target integration** cho P0: ưu tiên KVM 2 nơi n8n `2.45.7` và Hermes dashboard `0.22.5` đã kiểm toán; nếu resource khác cần dùng, trình bày lý do + approval trước.
- Những thành phần nào tuyệt đối không được đụng trong P0?
- Nếu UNKNOWN/BLOCKED, **P0 chưa được phép sửa runtime**, chỉ được chuẩn bị patch / preflight.

## Phạm vi

Được phép kiểm tra metadata, trạng thái app, dashboard/runtime logs đã làm sạch và lệnh chẩn đoán chỉ-đọc theo quyền có sẵn. Không đổi DNS/domain binding, xóa/restart/migrate OpenClaw/Hermes, không cài/đổi dịch vụ, không tiết lộ credentials, không dùng API trả phí.

## Bàn giao

Tạo `reports/2026-11-21-ttdnew-resource-identity.md` (hoặc ngày thực tế) và cập nhật catalog/state, profile Hostinger nếu phát hiện mới. Báo cáo gồm ma trận nguồn bằng chứng, kết luận identity, so sánh Docker Hosting resource vs VPS container, target quyết định và gate PASS/BLOCKED. Push GitHub và trả link báo cáo/commit. Chủ dự án chuyển tiếp kết quả cho Codex và ChatGPT theo [quy tắc](../rules/AGENT_WORKFLOW.md).
