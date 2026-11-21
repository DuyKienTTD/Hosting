---
id: ttd-agent-capability-survey-001
type: task
status: current
updated_at: 2026-11-21
sensitivity: public
---

# TTD-AGENT-CAPABILITY-SURVEY-001 — Tự kiểm tra năng lực và cách phối hợp

**Phạm vi:** khảo sát bổ sung Codex, Hermes và Hostinger Agent. Mục tiêu làm rõ năng lực **thực sự có trong instance/session và quyền được cấp**, không tạo thêm thủ tục hành chính. Đây là yêu cầu *assessment-only*, không sửa production.

## Điểm bắt đầu

Đọc [AGENTS](../AGENTS.md), [PROJECT](../PROJECT.md), [STATE](../STATE.md), [Agent Directory](../agents/README.md) và hồ sơ riêng tại `agents/<tên>.md`. Xem [self-assessment Hermes](../reports/2026-11-21-hermes-self-assessment.md) và [live audit](../reports/2026-11-21-n8n-hermes-integration-audit.md) nếu liên quan. **Không lặp phép kiểm tra đã có bằng chứng đủ tin cậy**, trừ khi trạng thái đổi.

## Mỗi bên hãy trả lời

1. **Identity/runtime:** tên agent, phiên bản/build/model nếu có thể xem, môi trường thực thi, sự khác nhau giữa local/session và VPS.
2. **Tools/permissions đã test:** GitHub read/write, terminal/file, browser, SSH/Hostinger hPanel, Docker/VPS, n8n/Hermes API, lịch chạy/background, skills/memory, có quyền tới API ngoài nào, có approval mode không.
3. **Các nghiệp vụ có thể thực hiện:** code/VPS, media, Google Ads/GA4, WordPress/SEO, social publishing, báo cáo; phân nhóm VERIFIED / AVAILABLE_UNTESTED / BLOCKED / UNKNOWN / PLANNED.
4. **Phối hợp:** nhận task từ Git/n8n/API/UI; có thể giao cho tác nhân khác như thế nào; có thể tự commit/push report không; có chạy khi UI đóng không; có callbacks/logs/task-id không?
5. **Giới hạn thực tế:** chi phí, scopes, quota, security, sandbox, failure/rollback, tính cần thiết của human approval. Không tự nâng quyền.
6. **Đề xuất phân vai:** việc mình làm tốt nhất, việc nên giao đối tác, và 3 thử nghiệm an toàn có giá trị cao nhất.

## Yêu cầu riêng

### Codex
Khảo sát session Codex đang được dùng: tools và quyền VPS/Hostinger/GitHub, khả năng tự triển khai code và dùng PR/CI, debug n8n/Hermes, khả năng quan sát/tiếp tục ngoài phiên. Đối chiếu với audit đã thực hiện, không đồng nhất audit một lần với quyền vĩnh viễn.

### Hermes
Kiểm tra sự khác nhau giữa Hermes WebUI shell và VPS container image; phạm vi tools/memory/background đã xác nhận; GitHub push; API inference/MCP/n8n còn BLOCKED. Không thử model trả phí hoặc bật API khi chưa duyệt.

### Hostinger Agent
Dùng giao diện Hostinger Agent hiện diện trong hPanel hoặc tài liệu/API chính thức; hỏi chính xác trợ lý **có thể đọc gì, thao tác gì, cần phê duyệt gì, có thể chạy nền và ghi Git không**. Không đồng nhất hPanel provider capabilities với quyền của Hostinger Agent. Nếu không có kênh để gửi câu hỏi, báo `BLOCKED — no interactive agent channel`. Cần thực hiện kiểm tra chỉ-đọc nếu được phép.

## Tiêu chuẩn báo cáo

- Tạo một báo cáo riêng `reports/YYYY-MM-DD-<agent>-capability-survey.md`, ghi nhận phương pháp, time, tested tools/scopes, evidence links, trạng thái từng năng lực, giới hạn; không chứa secret/IP.
- Cập nhật hồ sơ tại `agents/<agent>.md` **chỉ khi có bằng chứng mới**, giữ các kết luận chưa chứng minh là UNKNOWN/BLOCKED.
- Cập nhật `CATALOG.yaml`, `STATE.md`, `CHANGELOG.md` nếu thông tin dự án thay đổi; commit/push theo [quy tắc](../rules/AGENT_WORKFLOW.md).
- Nếu Hostinger Agent không hỗ trợ GitHub, bàn giao tài liệu trong chat/hPanel cho Codex/ChatGPT đẩy lên.
- Cuối cùng gửi **URL báo cáo + URL commit + những quyền/khả năng vẫn chưa rõ**.

Không chỉnh production, không bật API/MCP, không thay mạng/credentials/workflow, không phát sinh phí inference/media, không publish/Ads write.
