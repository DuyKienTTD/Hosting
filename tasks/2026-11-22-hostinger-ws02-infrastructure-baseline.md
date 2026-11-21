---
id: ttd-hostinger-ws02-infrastructure-baseline-001
type: task
status: prepared
approved_at: 2026-11-22
updated_at: 2026-11-22
sensitivity: public-redacted
owner: hostinger-agent
reviewer: chatgpt
---

# WS-02 — Xác minh baseline hạ tầng qua hPanel

**Mục tiêu.** Hostinger Agent sở hữu bằng chứng hiện trạng hạ tầng WS-02. Chốt các tín hiệu hPanel có thể cung cấp và khoảng trống cần xử lý trước khi triển khai giám sát. Không có dependency vào B2-O hoặc runbook Work.

**FIRST_ACTION / READ_SET.** Fetch main và ACK SHA sau khi đọc AGENTS, Workflow §§7–10, Security, STATE/CATALOG, [hồ sơ Hostinger](../agents/hostinger.md), [WS-02](2026-11-21-repository-operating-plan.md#ws-02-infrastructure-reliability), [inventory VPS](../inventory/current-vps-state.md), [audit n8n/Hermes](../reports/2026-11-21-n8n-hermes-integration-audit.md) và [đánh giá bảo mật](../reports/2026-11-21-vps-security-review.md). Trong phiên hPanel có quyền, bắt đầu từ VPS KVM 2 của dự án và xác nhận đúng resource theo inventory; phân biệt VPS đó với Cloud Hosting và tài nguyên Docker Hosting khác.

| Đầu vào | Phạm vi |
| --- | --- |
| Inventory/audit 21/11 | `DONE_VERIFIED` cho snapshot lịch sử. Tái sử dụng để đối chiếu thay đổi. |
| Baseline hiện tại | `NOT_RUN` cho lượt này. Chỉ công bố `VERIFIED_LIVE` với từng mục có phép đọc trực tiếp. |
| Khôi phục backup và triển khai monitoring | `NOT_RUN`. Metadata backup và tùy chọn cảnh báo trong hPanel chỉ là đầu vào. |

**TEST_DELTA chỉ đọc và ACCEPTANCE.**

1. Trong hPanel, ghi trạng thái VPS, CPU/RAM/disk và cửa sổ quan sát nếu giao diện cung cấp. Trong Docker Manager, đối chiếu đúng project/service n8n và Hermes; ghi running/health/restart/OOM theo trường thực có. Phân biệt dashboard Hermes với inference và production với sandbox.
2. Đọc trạng thái firewall của VPS, mức công khai của cổng, và endpoint HTTPS/TLS nếu có bằng chứng trong control plane. Đọc lịch backup VPS, mốc backup gần nhất, trạng thái và tùy chọn khôi phục thấy trong hPanel. Ghi rõ khả năng restore chưa kiểm nếu chỉ thấy metadata. Không mở hoặc sao chép nội dung backup.
3. Lập ma trận tín hiệu và nguồn cho Work: trường nào được đọc, timestamp, giá trị đã khử định danh, delta so với 21/11, giới hạn quan sát, hành động tiếp theo và owner. Nêu mục nào hPanel hỗ trợ và mục nào phải được kiểm bằng phép đọc riêng sau này. Nếu bị thiếu quyền hoặc trường không tồn tại, ghi `BLOCKED_ACCESS` hoặc `UNKNOWN` theo từng mục và hoàn tất các mục độc lập. Chỉ đề xuất monitoring, restore test hoặc hardening như bước triển khai tách riêng.

**WRITE_SET.** Chỉ `reports/2026-11-22-hostinger-ws02-infrastructure-baseline.md` trên branch riêng `hostinger/ws02-infrastructure-baseline-2026-11-22` và PR riêng. ChatGPT nhận review và đối chiếu với runbook Work. Nếu phiên có quyền đọc hPanel nhưng không có quyền ghi GitHub, bàn giao nội dung đã khử nhạy cảm và ghi `NOT_PUSHED`.

**DO_NOT_TOUCH / STOP / INVARIANTS.** Chỉ dùng quyền đọc hPanel/Docker Manager hiện có. Dừng tại mục cần tăng quyền, chạy shell, đọc secret/log payload hoặc ghi hạ tầng. Không restart, restore, đổi firewall/SSH/DNS/HTTPS, tạo lịch/cảnh báo, truy cập provider hoặc tác động Gate B. Không công bố IP, hostname nội bộ, đường dẫn private, IDs tài khoản hoặc dữ liệu nhạy cảm.

**HANDOFF.** `from_agent: chatgpt`, `to_agent: hostinger-agent`, `next_owner: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`. Khi nhận, ACK SHA và cụ thể quyền phiên hPanel/GitHub. Bàn giao PR/SHA và remote readback nếu đã push. Work tiếp tục diễn tập và hoàn tất runbook độc lập. ChatGPT ghép baseline sau khi nhận cả hai đầu ra.
