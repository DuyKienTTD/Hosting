---
id: mkoe-cv-coordinator
type: knowledge
status: draft
owner: Chat Dieu phoi
parent: agents/CAPABILITIES.md
updated_at: 2026-11-25
sensitivity: public
---
# Điều phối / ChatGPT
[Capability index](../CAPABILITIES.md)

- Strengths/tools: GitHub connector VERIFIED hiện tại; lập kế hoạch, điều phối và đối chiếu.
- Limitations/nonfit: Không tự dispatch chat khác, không tự QA độc lập; runtime Windows chưa xác minh.
- Suitable outcomes: Điều phối và tổng hợp.
- Evidence: [PR61](https://github.com/DuyKienTTD/Hosting/pull/61). Historical unless explicitly current; verify session freshness.
- Inventory plugin/skills: VERIFIED ngày 25/11, phiên HOSTING-POST-61: GitHub plugin đọc ref/blob, tạo commit và cập nhật nhánh có readback. [Commit FIX-F4](https://github.com/DuyKienTTD/Hosting/commit/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb). AVAILABLE_UNTESTED trong phiên: môi trường liệt kê imagegen, openai-docs, documents, pdf, Presentations, Spreadsheets. Đây là danh sách kỹ năng executor có sẵn theo cấu hình, chưa kiểm thực thi. Tình trạng kết nối của các plugin khác và danh sách kỹ năng chưa cài nhưng có thể cài theo phiên UNKNOWN.
- Capacity: current availability UNKNOWN (Coordinator active in MKOE); one outcome by default, verify actual capacity.
- Cost: actual usage UNKNOWN; no incremental paid authority inferred. A0 approval and cap required.
- Authority: profile is not permission; read [Core](../../AGENTS.md), actual role, task and mandatory safety sources.
