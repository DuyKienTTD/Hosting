---
id: ttd-work-ws02-monitoring-triage-001
type: task
status: prepared
approved_at: 2026-11-22
updated_at: 2026-11-22
sensitivity: public-redacted
owner: chatgpt-work
reviewer: chatgpt
---

# WS-02 — Runbook giám sát và xử lý sự cố ban đầu

**Mục tiêu.** Hoàn thành runbook sẵn để người vận hành review cho n8n/Hermes và VPS. Đây là đầu ra độc lập theo WS-02. Có thể hoàn thành ngay từ inventory, audit và tình huống giả. Dependency đối với B2-O, kết quả Gate B hoặc phiên Codex: không có.

**FIRST_ACTION / READ_SET.** Fetch `main`, ACK SHA và đọc AGENTS, Workflow §§7–10, Security, STATE/CATALOG, hồ sơ ChatGPT, [Roadmap](../GOALS_AND_ROADMAP.md), [WS-02](2026-11-21-repository-operating-plan.md#ws-02-infrastructure-reliability), [inventory](../inventory/current-vps-state.md), [audit n8n/Hermes](../reports/2026-11-21-n8n-hermes-integration-audit.md) và [VPS security review](../reports/2026-11-21-vps-security-review.md). Lấy audit làm mốc lịch sử, đối chiếu tài liệu chính thức của Docker/n8n/Hostinger khi xác định cách đọc tín hiệu. Ghi ngày và phạm vi xác minh.

| Đầu vào | Giá trị sử dụng |
| --- | --- |
| Audit/inventory 21/11 | `DONE_VERIFIED` cho kết quả health n8n/Hermes tại thời điểm đo. Dùng lại bằng chứng. |
| Monitoring định kỳ và cảnh báo | `NOT_RUN` trong phạm vi WS-02. Runbook đề xuất có thể soạn và diễn tập trên giấy. |
| Health hiện tại, ngưỡng vận hành, khả năng khôi phục backup | `UNKNOWN` khi nguồn hiện có chưa chứng minh. Ghi phép đo tối thiểu cho lượt triển khai sau. |

**Đầu ra và nghiệm thu.**

1. Runbook phân loại health/readiness n8n, health dashboard Hermes, container down/restart/OOM, disk, CPU/RAM, backup quá hạn và HTTPS khi có endpoint xác minh. Với mỗi tín hiệu ghi nguồn đọc, cách lấy mẫu, ngưỡng đề xuất hoặc `UNKNOWN` khi thiếu baseline, ý nghĩa, người nhận và bước kiểm chỉ đọc đầu tiên. Tách dashboard health khỏi suy luận inference health. Tách metadata backup khỏi khả năng restore.
2. Ghi trình tự triage cho ba tình huống giả: n8n không ready trong khi Hermes dashboard khỏe, disk tăng nhanh, backup quá hạn hoặc thiếu bằng chứng restore. Mỗi tình huống có input giả, verdict, hành động đầu tiên, tiêu chí escalations/khôi phục và evidence an toàn. Tách đề xuất xử lý có tác động sang change task sau khi được duyệt.
3. Kèm quy trình bàn giao triển khai tối thiểu, cấu hình dự kiến cần phê duyệt, kiểm thử trước/sau và rollback nếu triển khai sau này. Ngưỡng chưa có baseline là đề xuất. Đầu ra đạt `WS02_RUNBOOK_READY_FOR_REVIEW` khi đủ ma trận, ba ca giả đã đi qua runbook và nguồn. Trạng thái hạ tầng hiện tại không phải điều kiện hoàn tất runbook.

**WRITE_SET.** Branch riêng `work/ws02-monitoring-triage-2026-11-22` và PR riêng. Chỉ viết `runbooks/ws02-vps-monitoring-and-triage.md` và `reports/2026-11-22-work-ws02-monitoring-and-triage.md` ghi bằng chứng diễn tập/giới hạn. ChatGPT cập nhật chỉ mục sau review. PR #4 giữ tiêu chí QA B2-O đã nộp tại `26325b2`. Phần đối chiếu trace B2-O chỉ tiếp tục khi có evidence, độc lập với nghiệm thu WS-02.

**DO_NOT_TOUCH / STOP.** Chỉ đọc GitHub và tài liệu công khai, diễn tập với dữ liệu giả. Không cài monitor, tạo lịch, gửi cảnh báo thật, truy cập KVM2/hPanel, gọi endpoint production, restart, restore backup, thay firewall/DNS/HTTPS, provider, khóa hay ledger. Nếu dữ liệu thiếu, ghi `UNKNOWN` và tiếp tục các phần đọc được.

**HANDOFF.** `from_agent: chatgpt`, `to_agent: chatgpt-work`, `next_owner: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`. Work push, mở PR, xác minh remote diff đúng write-set và gửi SHA. Codex tiếp tục B2-O theo task Gate B và PR #5 riêng, không phải đồng tác giả hay reviewer bắt buộc của WS-02.

**Phối hợp WS-02.** [Hostinger Agent](2026-11-22-hostinger-ws02-infrastructure-baseline.md) sở hữu baseline hPanel/VPS/Docker/backup bằng PR riêng. Work sở hữu runbook và diễn tập giả. Work có thể nghiệm thu đầu ra theo audit lịch sử, ghi `UNKNOWN` cho dữ kiện live thiếu và hoàn tất trước khi có báo cáo Hostinger. ChatGPT đối chiếu hai đầu ra khi review. Codex tiếp tục B2-O.
