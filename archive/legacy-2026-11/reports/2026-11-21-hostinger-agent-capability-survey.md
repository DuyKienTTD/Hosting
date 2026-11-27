---
id: ttd-agent-capability-survey-hostinger-2026-11-21
type: report
status: complete
updated_at: 2026-11-21
sensitivity: public-redacted
agent: hostinger
---

# Báo cáo khảo sát năng lực Hostinger Agent

## Phạm vi

Khảo sát theo task `tasks/2026-11-21-agent-capability-survey.md`, hồ sơ `agents/hostinger.md`, cấu trúc dự án và quyền được cấp trong phiên hiện tại. Không có thay đổi nào được thực hiện trên production.

## Kết luận điều hành

**Có thể đảm nhận:** điều phối task, quản trị tài liệu Git, kiểm tra hạ tầng Hostinger/VPS, chẩn đoán an toàn, thiết kế workflow, viết runbook, lập kế hoạch rollback và báo cáo có bằng chứng.

**Chưa thể xác nhận:** điều khiển trực tiếp Hermes WebUI/private API, chạy workflow n8n/Hermes end-to-end, đọc filesystem VPS ngoài các kênh được cấp, hoặc thực hiện thay đổi production không có approval.

## Ma trận năng lực

| Nhóm | Kết quả | Bằng chứng hoặc giới hạn |
|---|---|---|
| Nhận diện phiên | VERIFIED | Đang hoạt động trong hPanel với vai trò Hostinger Agent |
| GitHub read | VERIFIED | Đọc được task khảo sát, hồ sơ agent và tài liệu dự án |
| GitHub write | VERIFIED | Đã có quyền tạo commit tài liệu trong repository đã kết nối |
| VPS inventory | VERIFIED | Đọc được VPS đang chạy, Ubuntu 24.04 LTS, 2 vCPU, 8 GB RAM, 100 GB disk |
| SSH reachability | VERIFIED | Kết nối SSH cổng 22 được kiểm tra thành công |
| SSH key inventory | VERIFIED | Không có SSH public key nào được trả về ở cấp tài khoản trong lần kiểm tra này |
| Allowlisted VPS diagnostics | AVAILABLE_UNTESTED | Công cụ có hỗ trợ, nhưng không chạy lệnh trong khảo sát để tránh tác động production |
| Docker/VPS changes | APPROVAL_REQUIRED | Có khả năng qua công cụ Hostinger, nhưng cần approval và task có rollback |
| Browser/public research | AVAILABLE | Có khả năng đọc nguồn công khai khi được yêu cầu; không dùng làm bằng chứng cho trạng thái private |
| Sandbox code | AVAILABLE | Chạy trong máy tạm riêng, không có credential hoặc mạng riêng của VPS |
| Hermes private API | BLOCKED | Chưa có kênh/API trực tiếp được expose trong phiên |
| n8n workflow execution | BLOCKED_OR_UNKNOWN | Chưa có evidence về quyền chạy end-to-end trong runtime |
| Production mutation | NOT_USED | Bị loại khỏi phạm vi khảo sát theo yêu cầu |

## Nhiệm vụ đề xuất cho TTD METAL

### Ưu tiên P0

- Duy trì `STATE.md`, `CATALOG.yaml`, task, report và rule.
- Xây dựng ma trận health check cho VPS, Docker, reverse proxy, HTTPS, backup và disk.
- Chuẩn hóa Definition of Ready/Done và approval gate cho production.
- Rà soát diff để tránh secret, IP riêng, token, private URL và dữ liệu cá nhân.

### Ưu tiên P1

- Lập topology đã redacted của Hermes, n8n, PostgreSQL, Nginx và media worker.
- Viết runbook rollback và incident response.
- Thiết kế test cases auth, timeout, retry, idempotency, callback và failure recovery.
- Phân loại workflow nào có thể chạy sandbox, workflow nào cần approval production.

### Ưu tiên P2

- Xây backlog SEO/content/media/website dựa trên baseline thực tế.
- Thiết kế dashboard chỉ số reliability, automation, security và growth.
- Đánh giá readiness trước khi publish hoặc mở rộng production.

## Rủi ro và blocker

1. Tên dịch vụ trong tài liệu không thay thế cho bằng chứng runtime.
2. Không nên ghi credential hoặc endpoint private vào Git.
3. Chưa có test end-to-end cho Hermes/n8n trong khảo sát này.
4. Không có daily backup được xác nhận từ bằng chứng VPS hiện tại, vì vậy backup readiness cần một task riêng.
5. Không chạy command, restart, deploy, upgrade, firewall change, DNS/SSL change hoặc publish trong khảo sát.

## Khuyến nghị task tiếp theo

Tạo task riêng để kiểm tra read-only runtime của Docker Compose và các health endpoint, sau đó tạo task riêng cho từng thay đổi production. Mỗi task phải có approval, rollback, evidence và kết quả PASS/FAIL/BLOCKED.

## Bằng chứng nội bộ

- Hồ sơ agent: `agents/hostinger.md`
- Task khảo sát: `tasks/2026-11-21-agent-capability-survey.md`
- Trạng thái dự án: `STATE.md`
- Quy tắc phối hợp: `rules/MULTI_AGENT_COLLABORATION.md`
- Commit của báo cáo và hồ sơ: commit message `docs: complete Hostinger Agent capability survey`
