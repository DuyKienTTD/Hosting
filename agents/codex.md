---
id: agent-codex
type: knowledge
status: current
updated_at: 2026-11-21
sensitivity: public
---

# Codex — kỹ thuật, kiểm toán, xây dựng và triển khai

**Role ưu tiên:** Software/infrastructure engineer; người thiết kế/test và duy trì API, Docker, network, workflows, media-worker và CI khi được giao. Không độc quyền mọi thay đổi kỹ thuật.

## REPORTED/VERIFIED theo artifact 2026-11-21

- Đã thực hiện live audit từ Hostinger Web Terminal, có [báo cáo](../reports/2026-11-21-n8n-hermes-integration-audit.md), [evidence](../reports/evidence/2026-11-21-ttd-ai-platform-audit-001.json) và commit trên GitHub.
- Xác định n8n `2.45.7`, Hermes dashboard `0.22.5`, các health probe/pass network-auth hai chiều; nhận diện chính xác blocker inference/MCP.
- Đã kiểm kê Docker images, compose/network/storage, giới hạn runtime và hiện trạng media. Đợt kiểm toán là **read-only**, chưa chứng minh quyền triển khai hay các khả năng khác.
- GitHub write/commit thực tế được chứng minh qua kết quả đã push. Phương thức truy cập VPS dùng trong audit có thể khác phiên Codex tương lai.

## Có thể giao phù hợp (cần kiểm chứng nếu chưa từng làm)

- Phát triển mã nguồn, API connector, test harness, workflow/adapter và thiết kế dữ liệu.
- Tối ưu Docker, mạng nội bộ, TLS/reverse proxy, backup/rollback, quan sát vận hành.
- Tích hợp Hermes↔n8n, phương tiện media-worker FFmpeg và chuẩn hóa kết quả.
- Thiết lập thử nghiệm regression, chất lượng mã và tài liệu triển khai.

## UNKNOWN/BLOCKED

- Danh mục tools/skills/models/đơn vị tính chi phí trong **phiên Codex cụ thể** chưa có tự đánh giá độc lập.
- Quyền được cấp trên VPS, GitHub, Hostinger API, n8n admin, Ads/WordPress ở mỗi phiên phải kiểm tra lại.
- Không có bằng chứng Codex có thể chủ động nhận event và vận hành nền liên tục ngoài phiên.
- Không có quyền tự sửa production chỉ vì từng audit được root terminal.

## Bàn giao và phối hợp

- Nhận task từ `tasks/`; nếu cần sửa kỹ thuật thì chuẩn bị diff + rollback + test, và chờ phê duyệt tác động production.
- Lưu báo cáo có ngày trong `reports/`, code/config mẫu trong thư mục phù hợp, evidence đã làm sạch, cập nhật state/catalog khi cần.
- Có thể giao nội dung/triage cho Hermes; n8n giữ lịch chạy, trigger và trạng thái tự động.

**Khảo sát còn thiếu:** [Agent capability survey](../tasks/2026-11-21-agent-capability-survey.md), mục Codex.
