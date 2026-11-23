# TTD METAL — Danh bạ tác nhân và thành phần

**Nguồn duy nhất về phân vai và năng lực**; đọc sau [AGENTS](../AGENTS.md), [PROJECT](../PROJECT.md) và [STATE](../STATE.md). Hồ sơ không thay thế việc kiểm tra quyền truy cập thật trong phiên đang chạy.

## Phân loại

| Thành phần | Loại | Vai trò ưu tiên | Hồ sơ | Mức xác minh |
|---|---|---|---|---|
| ChatGPT Điều phối | AI trợ lý tương tác | tư vấn, đặc tả, phân tích, điều phối bằng GitHub | [chatgpt](chatgpt.md) | GitHub write/read đã thử trong phiên; thực thi nền chưa có |
| **A1 — ChatGPT Thông thường** | AI trợ lý phiên riêng | GitHub/metadata, validator, code offline, QA độc lập theo task | [a1](a1.md) | Role ACK; PR #32 author delta, Work QA offline PASS_WITH_LIMITS; PR #33 proposal review PASS_WITH_LIMITS | 
| ChatGPT Work | Agent thực hiện đa bước | source QA độc lập, browser/UX, offline integration | [chatgpt](chatgpt.md) (profile Work riêng pending) | QA PR #32 và PR #24 đã có evidence; quyền theo phiên |
| Codex | Tác nhân kỹ thuật **ngoại lệ chi phí** | chỉ case đặc thù đã chứng minh các Agent khác không làm được | [codex](codex.md) | CODEX_NOT_AUTHORIZED cho lệnh mới nếu chưa được A0 duyệt chi phí |
| Hermes | AI agent trên VPS/WebUI | suy luận, tools, memory, thực thi tác vụ | [hermes](hermes.md) | capability survey hoàn tất; E2E với n8n chưa chạy |
| Hostinger | Nhà cung cấp / control plane + Hostinger Agent | hPanel/VPS/DNS, capability lịch sử (không giao mới) | [hostinger](hostinger.md) | **PAUSED theo A0**, chưa ACK thông báo; mọi thay đổi tiếp tục bị chặn |
| n8n | Workflow engine, **không phải AI agent** | trigger, connectors, schedule, job state | [n8n](n8n.md) | service healthy, 0 workflow, MCP tắt |

**Hostinger Agent** là trợ lý AI có giao diện trong hPanel, phải khảo sát riêng; không đồng nhất với Hostinger là nhà cung cấp hoặc với quyền root/VPS. Các hồ sơ là **bản ghi năng lực** không phải lệnh cấp quyền.

## Quy ước về mức bằng chứng

- `VERIFIED`: có phép thử trực tiếp và liên kết kết quả; ghi môi trường và thời gian.
- `REPORTED`: báo cáo của tác nhân/kiểm kê, chưa kiểm lại độc lập khi cần.
- `AVAILABLE_UNTESTED`: giao diện/docs có chức năng nhưng chưa thử end-to-end.
- `BLOCKED`: chưa thể thử do thiếu quyền/cấu hình/đầu vào.
- `UNKNOWN`: chưa biết; không được suy diễn.
- `PLANNED`: mục tiêu tương lai, không phải năng lực hiện tại.

## Lệnh tạm dừng Hostinger và phân công mới (A0, 2026-11-23)

**HOSTINGER_AGENT_PAUSED:** đình chỉ giao mới và thu hồi lệnh chưa thực thi; [OPS pause PR #24](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7093337445), [SEC pause PR #29](https://github.com/DuyKienTTD/Hosting/pull/29#issuecomment-7093338761). Hostinger chưa ACK việc tạm dừng qua phiên riêng; không khẳng định runtime đã dừng. Năng lực Hostinger vẫn là hồ sơ lịch sử, **không phải owner đang sẵn sàng**. Tiếp tục chỉ khi A0 tái cấp quyền và phiên Agent ACK.

**OPS-01A/S2-D2:** [A1 là writer duy nhất](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7093346631), branch A1 riêng **stacked trên PR #24 tại HEAD `e9c2d8f759850ea9c654de7e103549e041f66679`**, không sửa branch Hostinger. A1 đã ACK và bàn giao [PR36](https://github.com/DuyKienTTD/Hosting/pull/36) `6838ca7d5e69b43f5272e5fe7f03ba5fff1d7222`, 31/31 author tests offline; Hermes được giao [QA D2 độc lập](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7093565021), Hermes đã ACK và trả `NEEDS_A1_DELTA` (19 PASS / 2 FAIL) [#7093801751](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7093801751); A1 đã ACK và bàn giao [OPS D3 PR36 HEAD `5626bb55072cdcca0d39f3ba57180d3c57af05ad`](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7093985995) (44/44 **author** tests offline); [Hermes QA D3 độc lập](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7094119127) đã được giao, chờ Hermes ACK và verdict trên HEAD mới, **chưa phải PASS độc lập**. Work 18 nhóm QA D1 là lịch sử, không phải reviewer D2. Lịch sử Hostinger D1 và Work QA 18 nhóm vẫn giữ nguyên.

## Cách phối hợp

- **Chủ dự án** quyết định mục tiêu, quyền, ngân sách và publish; tác nhân không tự cấp quyền.
- **Mỗi task có 1 owner** chịu trách nhiệm kết quả, có thể có collaborators. Vai trò ưu tiên là gợi ý điều phối, không độc quyền một loại việc.
- **ChatGPT** có thể tạo task/đánh giá bằng chứng; **A1/Work/Hermes** ưu tiên xử lý kỹ thuật theo khả năng; **Hostinger PAUSED**, chỉ xét lại nếu A0 resume và phiên Hostinger ACK; **Codex chỉ ngoại lệ theo chi phí**; **Hermes** ưu tiên reasoning và tác vụ dùng tools; **n8n** ưu tiên trigger/execution; **Hostinger là nhà cung cấp platform**, còn Hostinger Agent đang **PAUSED**, không được nhận lệnh thao tác hPanel.
- Chuyển nhiệm vụ bằng URL task + trạng thái/đầu vào/tiêu chí nghiệm thu; nhận kết quả bằng URL report và commit. Không lấy lịch sử chat làm nguồn sự thật.
- Dữ liệu sống (job state, retry, queue) đặt tại n8n/DB; GitHub lưu đặc tả, quyết định, mã nguồn, evidence đã khử nhạy cảm và báo cáo.
- Nếu hai tác nhân cùng sửa, dùng file task riêng, branch/PR hoặc phối hợp trước commit. Không force-push, không tự viết đè báo cáo có ngày.
- Thiếu năng lực hoặc công cụ: chuyển cho tác nhân phù hợp hoặc ghi BLOCKED. Không giả định mọi nền tảng có quyền sửa production.
- Để biết ai có năng lực mới nhất, xem hồ sơ và các evidence liên kết; nếu cần xác minh lại, giao [khảo sát bổ sung](../tasks/2026-11-21-agent-capability-survey.md).

## Điều phối nghiên cứu trước thực thi

**Bắt buộc đọc** [AGENTS](../AGENTS.md), [AGENT_WORKFLOW mục 7 và 11](../rules/AGENT_WORKFLOW.md), [quy tắc bảo mật](../rules/REPOSITORY_SECURITY.md), [STATE](../STATE.md), [CATALOG](../CATALOG.yaml), hồ sơ của mình và task trước khi nhận việc. **Lưu ý lịch sử:** hướng dẫn trước 23/11 từng mặc định giao Codex việc code/test/deploy và Hostinger khảo sát VPS. **Không áp dụng cho lệnh mới.** Hiện tại Điều phối đối chiếu nguồn/evidence, A1/Work/Hermes đảm nhiệm phần việc phù hợp, Hostinger Agent **PAUSED** theo chỉ thị A0 và Codex **exception-only** có phê duyệt chi phí; n8n chỉ thực thi workflow đã bật. **Phân vai dựa trên năng lực, quyền và trạng thái phiên được chứng minh.**

Mọi handoff phải có **một owner**, nguồn đầu vào, **bước bắt đầu cụ thể**, bằng chứng nghiệm thu, giới hạn quyền, next owner và trạng thái `PREPARED/SENT/ACKNOWLEDGED/IN_PROGRESS/DONE/BLOCKED`. GitHub task đã commit chỉ là `PREPARED`, chưa phải đã gửi/nhận. Nếu phải chuyển tiếp thủ công, báo `PREPARED_FOR_OWNER_FORWARD` và cung cấp thông điệp rõ người nhận. Người nhận đọc lại quy tắc và ghi rule commit đã dùng trong ACK/report.

## Phân công theo nghiệp vụ — định hướng, chưa có nghĩa đã sẵn sàng

| Nghiệp vụ | Owner ưu tiên | Thành phần hỗ trợ | Giới hạn |
|---|---|---|---|
| Nền tảng/API/triển khai VPS | Work/A1/Hermes chỉ được làm offline/source theo scope; **Hostinger PAUSED** | ChatGPT; Codex chỉ ngoại lệ có A0 duyệt | **Không triển khai VPS/live**; Hostinger cần A0 resume + ACK trước khi nhận việc |
| Chiến lược, backlog, nghiệm thu | ChatGPT hoặc owner task được chỉ định | Codex, Hermes | không thành single point of failure 24/7 |
| Video/content pipeline | Hermes | n8n, Codex, công cụ media | chi phí render và publish cần gate |
| Ads/SEO analysis | Hermes hoặc ChatGPT | n8n, Codex, connectors | read-first, chỉ ghi khi có quyền |
| Scheduled reporting | n8n workflow + owner nghiệp vụ | Hermes, DB | n8n điều phối, không tự suy luận |
| Backup, network, VPS ops | **PAUSED** đối với Hostinger; Work/A1/Hermes chỉ được làm offline/source trong scope hiện có | ChatGPT; Codex exception-only | không có lệnh live VPS/backup, tránh downtime |
| Cloud Hosting, domain, DNS, email, backup inventory | **Hostinger PAUSED** (owner tương lai sau A0 resume) | ChatGPT/A1 read-only nếu có quyền riêng | không triển khai live hoặc tiếp nhận work Hostinger đang bị thu hồi |

## Nguồn xác minh

- [Hermes tự đánh giá](../reports/2026-11-21-hermes-self-assessment.md)
- [n8n/Hermes live audit](../reports/2026-11-21-n8n-hermes-integration-audit.md)
- [Evidence live](../reports/evidence/2026-11-21-ttd-ai-platform-audit-001.json)
- [VPS inventory](../inventory/current-vps-state.md)
- [Hostinger account/capability inventory](../reports/2026-11-21-hostinger-account-capability-inventory.md)

**Ghi chú áp dụng:** phân vai legacy trong các dòng cũ chỉ là lịch sử; [workflow mục 11](../rules/AGENT_WORKFLOW.md) và [allocation v2](../tasks/2026-11-23-a1-cost-first-master-allocation.md) kiểm soát lệnh mới. A1 đã ROLE_ACK và TASK_ACK cho PR #32/#33, có commit/QA evidence; ACK nhiệm vụ mới vẫn bắt buộc. Hostinger PAUSED: không nhận nhiệm vụ mới hoặc tiếp tục work cũ khi chưa có chỉ thị A0 và ACK.
