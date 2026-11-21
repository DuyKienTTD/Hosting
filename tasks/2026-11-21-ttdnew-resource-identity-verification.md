---
id: ttd-resource-identity-001
type: task
status: complete
updated_at: 2026-11-21
sensitivity: public
owner: hostinger-agent
support: [codex]
depends_on: []
---

# TTD-RESOURCE-IDENTITY-001, Xác minh resource `ttdnew.tech`

## Mục tiêu

Xác minh resource Docker Hosting / AI automation đang gắn với `ttdnew.tech`; đối chiếu metadata OpenClaw, runtime U4S và Hermes chạy trong VPS KVM 2.

## Kết quả

- `ttdnew.tech` là U4S Docker Hosting / AI automation resource, state active.
- Metadata plan hiển thị `OpenClaw`.
- Runtime thực tế trả về `u4s-hermes-agent`.
- U4S application UUID nhất quán giữa domain lookup, application inventory và upgrade status.
- VPS KVM 2 có Docker Compose project `hermes-agent-l7fe`, container image Hermes và trạng thái running.
- U4S Hermes và VPS Hermes là hai resource riêng; chưa có bằng chứng chúng chia sẻ backend, volume, credential hoặc dữ liệu.
- Không thay đổi production.

## Acceptance

- [x] Resource/domain identity được xác minh.
- [x] Runtime U4S được xác minh là Hermes.
- [x] Metadata OpenClaw được đối chiếu và đánh dấu không khớp runtime.
- [x] Hermes trên VPS KVM 2 được xác minh độc lập.
- [x] Không restart, upgrade, deploy, migrate hoặc thay đổi production.
- [x] Báo cáo được tạo trong `reports/`.
- [x] Commit được tạo và kiểm tra lại trên nhánh `main`.

## Evidence

- `reports/2026-11-21-ttdnew-resource-identity-verification.md`
- `STATE.md`
- `agents/hostinger.md`

## Ghi chú giới hạn

Không truy cập secret, `.env`, private API, volume data hoặc conversation history. Không kết luận về liên kết dữ liệu giữa hai Hermes instance khi chưa có bằng chứng trực tiếp.
