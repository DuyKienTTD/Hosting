---
id: component-hostinger
type: knowledge
status: current
updated_at: 2026-11-21
sensitivity: public-redacted
---

# Hostinger — nhà cung cấp hạ tầng; Hostinger Agent là AI hỗ trợ riêng

**Phân loại:** Hostinger **không phải** một AI Agent duy nhất. HPanel/VPS/Docker Manager/backup là các dịch vụ quản trị. Hostinger Agent là trợ lý AI hiện diện trong UI, năng lực thực tế và quyền thao tác cần khảo sát độc lập.

## VERIFIED / OBSERVED

- [Kiểm kê VPS](../inventory/current-vps-state.md) và [audit](../reports/2026-11-21-n8n-hermes-integration-audit.md): KVM 2 Kuala Lumpur, Ubuntu 24.04 LTS, 2 vCPU, 8 GB RAM, 100 GB, 8 TB/tháng; Docker n8n/Hermes chạy.
- Nội dung hPanel đã đọc trong phiên ChatGPT 2026-11-21: VPS đang chạy; có mục Docker Manager (dự án/credentials/catalog), terminal web, backups/snapshot, resource usage, firewall, SSH keys, DNS và Hostinger API.
- UI có **Hostinger Agent**, công cụ hỏi/đáp và chế độ phê duyệt manual; đó chỉ là bằng chứng về **sự hiện diện của giao diện**, không xác minh tác nhân có thể thay đổi cấu hình/API hay tự chạy nhiệm vụ.
- HPanel hiện ghi 0 provider firewall rules và backup hàng tuần tại thời điểm xem. Không công bố IP/hostname thật vào repo.

## Vai trò kỳ vọng, chưa trao quyền

- Cung cấp thông tin tài nguyên/hạ tầng, backups, trạng thái Docker và công cụ quản trị khi có quyền.
- Là nền tảng chạy n8n, Hermes, media storage/worker và công cụ giám sát.
- Hostinger Agent có thể hỗ trợ kiểm tra và đề xuất sửa lỗi **nếu tự khảo sát chứng minh khả năng**.

## UNKNOWN / giới hạn cần kiểm thử

- Hostinger Agent có thể đọc Docker compose/logs, gọi Hostinger API, SSH, quản trị firewall, sao lưu/restore hay không?
- Có hỗ trợ tự động hóa không cần UI không? Có API/service identity nào được cấp và có thể giới hạn quyền không?
- Năng lực rollback, multi-step execution, báo cáo và push GitHub trực tiếp của Hostinger Agent: **UNKNOWN**.
- Không coi quyền của chủ tài khoản hPanel là quyền được ủy quyền cho AI Agent.

## Bàn giao

- Việc thay đổi VPS production ưu tiên giao Codex theo đặc tả và approval; Hostinger là công cụ/nền tảng hỗ trợ.
- Nếu Hostinger Agent làm được GitHub write, tuân thủ [AGENT_WORKFLOW](../rules/AGENT_WORKFLOW.md); nếu không, xuất kết quả đã redacted và giao Codex/ChatGPT đẩy lên.
- Khảo sát tự đánh giá: [Agent capability survey](../tasks/2026-11-21-agent-capability-survey.md), mục Hostinger.

**Evidence:** live audit, inventory, hPanel overview quan sát 2026-11-21. Không có bài test thực thi độc lập của Hostinger Agent.
