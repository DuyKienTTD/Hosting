# TTD METAL — Danh bạ tác nhân và thành phần

**Nguồn duy nhất về phân vai và năng lực**; đọc sau [AGENTS](../AGENTS.md), [PROJECT](../PROJECT.md) và [STATE](../STATE.md). Hồ sơ không thay thế việc kiểm tra quyền truy cập thật trong phiên đang chạy.

## Phân loại

| Thành phần | Loại | Vai trò ưu tiên | Hồ sơ | Mức xác minh |
|---|---|---|---|---|
| ChatGPT | AI trợ lý tương tác | tư vấn, đặc tả, phân tích, điều phối bằng GitHub | [chatgpt](chatgpt.md) | GitHub write/read đã thử trong phiên; thực thi nền chưa có |
| Codex | Tác nhân kỹ thuật | code, VPS, Docker, API, kiểm thử, vận hành | [codex](codex.md) | có audit/evidence đã push; tự đánh giá rộng hơn còn thiếu |
| Hermes | AI agent trên VPS/WebUI | suy luận, tools, memory, thực thi tác vụ | [hermes](hermes.md) | self-assessment và VPS audit; E2E với n8n chưa chạy |
| Hostinger | Nhà cung cấp / control plane | VPS, Docker Manager, backup, firewall, hỗ trợ | [hostinger](hostinger.md) | hPanel và kiểm kê VPS; quyền của Hostinger Agent chưa đo |
| n8n | Workflow engine, **không phải AI agent** | trigger, connectors, schedule, job state | [n8n](n8n.md) | service healthy, 0 workflow, MCP tắt |

**Hostinger Agent** là trợ lý AI có giao diện trong hPanel, phải khảo sát riêng; không đồng nhất với Hostinger là nhà cung cấp hoặc với quyền root/VPS. Các hồ sơ là **bản ghi năng lực** không phải lệnh cấp quyền.

## Quy ước về mức bằng chứng

- `VERIFIED`: có phép thử trực tiếp và liên kết kết quả; ghi môi trường và thời gian.
- `REPORTED`: báo cáo của tác nhân/kiểm kê, chưa kiểm lại độc lập khi cần.
- `AVAILABLE_UNTESTED`: giao diện/docs có chức năng nhưng chưa thử end-to-end.
- `BLOCKED`: chưa thể thử do thiếu quyền/cấu hình/đầu vào.
- `UNKNOWN`: chưa biết; không được suy diễn.
- `PLANNED`: mục tiêu tương lai, không phải năng lực hiện tại.

## Cách phối hợp

- **Chủ dự án** quyết định mục tiêu, quyền, ngân sách và publish; tác nhân không tự cấp quyền.
- **Mỗi task có 1 owner** chịu trách nhiệm kết quả, có thể có collaborators. Vai trò ưu tiên là gợi ý điều phối, không độc quyền một loại việc.
- **ChatGPT** có thể tạo task/đánh giá bằng chứng; **Codex** ưu tiên phát triển/kiểm toán kỹ thuật; **Hermes** ưu tiên reasoning và tác vụ dùng tools; **n8n** ưu tiên trigger/execution; **Hostinger** cung cấp platform và các thao tác trong hPanel được phê duyệt.
- Chuyển nhiệm vụ bằng URL task + trạng thái/đầu vào/tiêu chí nghiệm thu; nhận kết quả bằng URL report và commit. Không lấy lịch sử chat làm nguồn sự thật.
- Dữ liệu sống (job state, retry, queue) đặt tại n8n/DB; GitHub lưu đặc tả, quyết định, mã nguồn, evidence đã khử nhạy cảm và báo cáo.
- Nếu hai tác nhân cùng sửa, dùng file task riêng, branch/PR hoặc phối hợp trước commit. Không force-push, không tự viết đè báo cáo có ngày.
- Thiếu năng lực hoặc công cụ: chuyển cho tác nhân phù hợp hoặc ghi BLOCKED. Không giả định mọi nền tảng có quyền sửa production.
- Để biết ai có năng lực mới nhất, xem hồ sơ và các evidence liên kết; nếu cần xác minh lại, giao [khảo sát bổ sung](../tasks/2026-11-21-agent-capability-survey.md).

## Phân công theo nghiệp vụ — định hướng, chưa có nghĩa đã sẵn sàng

| Nghiệp vụ | Owner ưu tiên | Thành phần hỗ trợ | Giới hạn |
|---|---|---|---|
| Nền tảng/API/triển khai VPS | Codex | Hostinger/VPS, Hermes | production changes cần quyền riêng |
| Chiến lược, backlog, nghiệm thu | ChatGPT hoặc owner task được chỉ định | Codex, Hermes | không thành single point of failure 24/7 |
| Video/content pipeline | Hermes | n8n, Codex, công cụ media | chi phí render và publish cần gate |
| Ads/SEO analysis | Hermes hoặc ChatGPT | n8n, Codex, connectors | read-first, chỉ ghi khi có quyền |
| Scheduled reporting | n8n workflow + owner nghiệp vụ | Hermes, DB | n8n điều phối, không tự suy luận |
| Backup, network, VPS ops | Codex với chủ dự án phê duyệt | Hostinger | tránh mất kết nối / downtime |

## Nguồn xác minh

- [Hermes tự đánh giá](../reports/2026-11-21-hermes-self-assessment.md)
- [n8n/Hermes live audit](../reports/2026-11-21-n8n-hermes-integration-audit.md)
- [Evidence live](../reports/evidence/2026-11-21-ttd-ai-platform-audit-001.json)
- [VPS inventory](../inventory/current-vps-state.md)
