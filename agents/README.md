# TTD METAL — Danh bạ tác nhân và thành phần

**Nguồn duy nhất về phân vai và năng lực**; đọc sau [AGENTS](../AGENTS.md), [PROJECT](../PROJECT.md) và [STATE](../STATE.md). Hồ sơ không thay thế việc kiểm tra quyền truy cập thật trong phiên đang chạy.

## Phân loại

| Thành phần | Loại | Vai trò ưu tiên | Hồ sơ | Mức xác minh |
|---|---|---|---|---|
| ChatGPT Điều phối | AI trợ lý tương tác | tư vấn, đặc tả, phân tích, điều phối bằng GitHub | [chatgpt](chatgpt.md) | GitHub write/read đã thử trong phiên; thực thi nền chưa có |
| **A1 — ChatGPT Thông thường** | AI trợ lý phiên riêng | tài liệu, Git metadata, validator/fixtures/code nhỏ nếu tool verified | [a1](a1.md) | phiên A1 chưa ACK; công cụ GitHub/shell UNKNOWN |\n| ChatGPT Work | Agent thực hiện đa bước | source QA độc lập, browser/UX, offline integration | [chatgpt](chatgpt.md) (profile Work riêng pending) | bằng chứng qua PR review; quyền từng phiên |\n| Codex | Tác nhân kỹ thuật **ngoại lệ chi phí** | chỉ case đặc thù đã chứng minh các Agent khác không làm được | [codex](codex.md) | CODEX_NOT_AUTHORIZED cho lệnh mới nếu chưa được A0 duyệt chi phí |
| Hermes | AI agent trên VPS/WebUI | suy luận, tools, memory, thực thi tác vụ | [hermes](hermes.md) | capability survey hoàn tất; E2E với n8n chưa chạy |
| Hostinger | Nhà cung cấp / control plane + Hostinger Agent | Cloud Hosting, WordPress, domain/DNS/email, VPS/Docker/backup | [hostinger](hostinger.md) | khảo sát account inventory + GitHub PASS; thao tác theo quyền/approval |
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
- **ChatGPT** có thể tạo task/đánh giá bằng chứng; **A1/Work/Hermes/Hostinger** ưu tiên xử lý kỹ thuật theo khả năng; **Codex chỉ ngoại lệ theo chi phí**; **Hermes** ưu tiên reasoning và tác vụ dùng tools; **n8n** ưu tiên trigger/execution; **Hostinger** cung cấp platform và các thao tác trong hPanel được phê duyệt.
- Chuyển nhiệm vụ bằng URL task + trạng thái/đầu vào/tiêu chí nghiệm thu; nhận kết quả bằng URL report và commit. Không lấy lịch sử chat làm nguồn sự thật.
- Dữ liệu sống (job state, retry, queue) đặt tại n8n/DB; GitHub lưu đặc tả, quyết định, mã nguồn, evidence đã khử nhạy cảm và báo cáo.
- Nếu hai tác nhân cùng sửa, dùng file task riêng, branch/PR hoặc phối hợp trước commit. Không force-push, không tự viết đè báo cáo có ngày.
- Thiếu năng lực hoặc công cụ: chuyển cho tác nhân phù hợp hoặc ghi BLOCKED. Không giả định mọi nền tảng có quyền sửa production.
- Để biết ai có năng lực mới nhất, xem hồ sơ và các evidence liên kết; nếu cần xác minh lại, giao [khảo sát bổ sung](../tasks/2026-11-21-agent-capability-survey.md).

## Điều phối nghiên cứu trước thực thi

**Bắt buộc đọc** [AGENTS](../AGENTS.md), [AGENT_WORKFLOW mục 7](../rules/AGENT_WORKFLOW.md), [quy tắc bảo mật](../rules/REPOSITORY_SECURITY.md), [STATE](../STATE.md), [CATALOG](../CATALOG.yaml), hồ sơ của mình và task trước khi nhận việc. Thứ tự ưu tiên: ChatGPT tổng hợp nguồn chính thức + evidence; Hostinger Agent khảo sát VPS/hPanel/network/hosting; Hermes khảo sát agent/inference/tools/serialized request; Codex viết code, chạy test, deploy sandbox/rollback; n8n thực thi workflow khi đã bật. **Phân vai dựa trên năng lực và quyền được chứng minh trong phiên, không độc quyền.**

Mọi handoff phải có **một owner**, nguồn đầu vào, **bước bắt đầu cụ thể**, bằng chứng nghiệm thu, giới hạn quyền, next owner và trạng thái `PREPARED/SENT/ACKNOWLEDGED/IN_PROGRESS/DONE/BLOCKED`. GitHub task đã commit chỉ là `PREPARED`, chưa phải đã gửi/nhận. Nếu phải chuyển tiếp thủ công, báo `PREPARED_FOR_OWNER_FORWARD` và cung cấp thông điệp rõ người nhận. Người nhận đọc lại quy tắc và ghi rule commit đã dùng trong ACK/report.

## Phân công theo nghiệp vụ — định hướng, chưa có nghĩa đã sẵn sàng

| Nghiệp vụ | Owner ưu tiên | Thành phần hỗ trợ | Giới hạn |
|---|---|---|---|
| Nền tảng/API/triển khai VPS | Work/Hermes/Hostinger theo quyền và scope; Codex chỉ ngoại lệ | A1/ChatGPT | production changes cần quyền riêng và Codex cần A0 cost gate |
| Chiến lược, backlog, nghiệm thu | ChatGPT hoặc owner task được chỉ định | Codex, Hermes | không thành single point of failure 24/7 |
| Video/content pipeline | Hermes | n8n, Codex, công cụ media | chi phí render và publish cần gate |
| Ads/SEO analysis | Hermes hoặc ChatGPT | n8n, Codex, connectors | read-first, chỉ ghi khi có quyền |
| Scheduled reporting | n8n workflow + owner nghiệp vụ | Hermes, DB | n8n điều phối, không tự suy luận |
| Backup, network, VPS ops | Hostinger Agent; Work/Hermes nếu offline phù hợp | A1/ChatGPT; Codex ngoại lệ | tránh mất kết nối/downtime |
| Cloud Hosting, domain, DNS, email, backup inventory | Hostinger Agent | Codex, ChatGPT | chỉ thao tác khi tool/quyền đã kiểm chứng |

## Nguồn xác minh

- [Hermes tự đánh giá](../reports/2026-11-21-hermes-self-assessment.md)
- [n8n/Hermes live audit](../reports/2026-11-21-n8n-hermes-integration-audit.md)
- [Evidence live](../reports/evidence/2026-11-21-ttd-ai-platform-audit-001.json)
- [VPS inventory](../inventory/current-vps-state.md)
- [Hostinger account/capability inventory](../reports/2026-11-21-hostinger-account-capability-inventory.md)

**Ghi chú áp dụng:** phân vai legacy trong các dòng cũ chỉ là lịch sử; [workflow mục 11](../rules/AGENT_WORKFLOW.md) và [allocation v2](../tasks/2026-11-23-a1-cost-first-master-allocation.md) kiểm soát lệnh mới. A1 chưa có năng lực GitHub/shell được xác minh trong phiên A1; không gán nhiệm vụ đã nhận khi chưa ACK.
