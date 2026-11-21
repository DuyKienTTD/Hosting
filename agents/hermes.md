---
id: agent-hermes
type: knowledge
status: current
updated_at: 2026-11-21
sensitivity: public-redacted
---

# Hermes Agent — AI reasoning và tool execution

**Role ưu tiên:** AI operator / analyst; lập kế hoạch, phân tích, tạo nội dung có cấu trúc, điều tra bằng tools và bàn giao qua GitHub. Trong kiến trúc TTD METAL dài hạn, Hermes được định hướng làm reasoning layer phối hợp với n8n, nhưng **định hướng không đồng nghĩa runtime production đã sẵn sàng**.

## VERIFIED

- **Hermes WebUI session** đã được xác minh có thể dùng file/terminal/web/browser tools, `skills_list`, `skill_view`, `memory`, `session_search`, `cronjob_manage`, `delegate_task` và các tool MCP/connector discovery trong phiên khảo sát 2026-11-21.
- GitHub read/write cho repo `DuyKienTTD/Hosting` đã được xác minh trong phiên WebUI: clone/pull/commit/push qua SSH thành công; có thể tạo report và cập nhật tri thức trong repo khi auth còn hiệu lực.
- `skills_list` trả **55 skills** trong profile hiện tại.
- `session_search` hoạt động; `cronjob_manage list` trả **0 job** tại thời điểm khảo sát.
- [Audit VPS](../reports/2026-11-21-n8n-hermes-integration-audit.md) xác minh **Hermes container trên VPS** là dashboard/control plane `0.22.5`, healthy; n8n reach được dashboard auth path; Hermes reach được n8n readiness qua host bridge.

## AVAILABLE_UNTESTED

- Background scheduling/cron có tool surface trong phiên WebUI, nhưng chưa chứng minh workload 24/7 có SLA/retry/observability cho dự án này.
- Delegation/subagents có sẵn, nhưng chưa được kiểm chứng như cơ chế production orchestration của TTD METAL.
- Catalog connectors/MCP rất rộng, nhưng sự hiện diện của catalog **không phải** bằng chứng đã có credential hay account usable.
- Hermes phù hợp để khảo sát media/Ads/SEO và tạo draft/plan trước khi gọi API thật hoặc thay đổi production.

## BLOCKED / NOT YET PROVEN

- Hermes **chưa expose live agent inference API** từ Hostinger dashboard image trong audit; API upstream theo docs ≠ API của instance hiện hữu.
- n8n instance-level MCP đang disabled; chưa có workflow, chưa có execution và chưa có luồng Hermes ↔ n8n E2E thành công.
- Không có connector/account production-ready nào cho Google Ads, GA4, WordPress/WooCommerce, YouTube, TikTok, Meta, Kling, HeyGen hoặc ElevenLabs được xác minh trong phiên khảo sát Hermes.
- Chưa chứng minh background execution 24/7, self-healing, budget controls và rollback cho business actions.

## UNKNOWN

- Quyền VPS/SSH trực tiếp từ **phiên Hermes WebUI shell** vào production runtime ngoài sandbox hiện tại.
- Quyền thao tác hPanel/Hostinger Agent trực tiếp từ phiên Hermes này.
- Approval matrix chi tiết của Hermes production runtime ngoài việc quan sát thấy có approval mediation với một số thao tác shell.
- Vị trí/lifecycle memory vật lý trên VPS container Hostinger trong triển khai hiện tại.

## Có thể giao phù hợp ngay bây giờ

- Phân tích yêu cầu/dữ liệu, audit tài liệu và kết nối, viết brief/script/checklist/report.
- Dùng tools để kiểm tra claim, đọc task qua GitHub, cập nhật report và push khi GitHub auth hoạt động.
- Chuẩn bị schema, acceptance criteria, runbook và đề xuất kiến trúc trước khi giao Codex hoặc n8n thực thi.
- SEO/content planning, media pre-production planning, reporting/read-only analysis và QA sơ bộ.

## Không nên tự giao nếu chưa có phê duyệt/hạ tầng bổ sung

- Vai trò backend inference production 24/7 cho n8n.
- Publish social/site/Ads write hoặc bất kỳ action phát sinh chi phí ngoài quyền được cấp.
- Thay đổi VPS/network/firewall/MCP/API enablement mà chưa có change window.

## Phối hợp / bàn giao

- Nhận task tốt nhất qua URL GitHub + tiêu chí nghiệm thu; nhận kết quả qua report + commit URL.
- Với thay đổi VPS/Docker/API sâu: chuyển cho **Codex** làm owner ưu tiên.
- Với scheduling/retry/state machine/callback routing: giao **n8n** khi workflow đã được bật và kiểm thử.
- Với publish/chi phí/Ads write: yêu cầu human approval và policy gate.
- Không coi việc có tool trong catalog hoặc docs là bằng chứng runtime hiện tại đã có quyền tương ứng.

## Hồ sơ khảo sát liên quan

- [Hermes self-assessment](../reports/2026-11-21-hermes-self-assessment.md)
- [Hermes capability survey](../reports/2026-11-21-hermes-capability-survey.md)
- [n8n ↔ Hermes live audit](../reports/2026-11-21-n8n-hermes-integration-audit.md)
- Task khảo sát: [TTD-AGENT-CAPABILITY-SURVEY-001](../tasks/2026-11-21-agent-capability-survey.md)
