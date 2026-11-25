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

## Inventory công cụ theo phiên HOSTING-POST-61b

Nguồn: tự liệt kê trong phiên Điều phối POST-61b, 25/11/2026. Môi trường: ChatGPT Work, executor Linux.

| Nhóm | Công cụ quan sát được trong phiên | Mức xác minh |
| --- | --- | --- |
| Code Mode và GitHub | `functions.exec` và `ALL_TOOLS`. Connector GitHub dùng tiền tố `mcp__codex_apps__github_`. Nhóm đọc PR, commit, ref, cây Git và tệp gồm `get_pr_info`, `list_pr_changed_filenames`, `fetch_commit`, `fetch` và `fetch_file`. Nhóm ghi Git gồm `create_tree`, `create_commit`, `update_ref`, `create_blob`, `create_file`, `update_file` và `create_branch`. Connector cũng liệt kê nhóm tìm kiếm, issue, review PR và GitHub Actions. | `VERIFIED` cho việc tự liệt kê và đọc GitHub. Thao tác ghi được đối chiếu bằng commit và HEAD của PR #62. Các hàm khác ở mức `AVAILABLE_UNTESTED`. |
| Tìm kiếm web | `mcp__codex_apps__search_service_web_run` có tìm web, tài liệu nghiên cứu, ảnh và mở nguồn. | `AVAILABLE_UNTESTED`. |
| Workspace và kỹ năng | Shell `exec_command` trên Linux và Git CLI. Có thêm `write_stdin`, `apply_patch`, `view_image`, `image_gen__imagegen` và nhóm `skills__list`, `skills__read`, `skills__installations`. Executor liệt kê imagegen, openai-docs, documents, pdf, Presentations và Spreadsheets. | `VERIFIED` cho shell/Git CLI. Các công cụ và kỹ năng còn lại ở mức `AVAILABLE_UNTESTED`. |
| Connector và ứng dụng khác | Automations, Browser, Canva, ElevenLabs, Gmail, Google Calendar, Google Contacts, Google Drive (Docs/Sheets/Slides), HeyGen, Hotline, Kling AI, OpenAI Library, Pages (ChatGPT Space), Personal Context, Pets, Plugin Creator, Plugin Management, Sites, Supermetrics Marketing Agent, vidIQ và WordPress. Có thêm bề mặt điều khiển máy tính hợp nhất `cua_repl`. | `AVAILABLE_UNTESTED` theo danh sách công cụ. Trạng thái kết nối tài khoản, dữ liệu truy cập được và quyền thao tác của từng ứng dụng là `UNKNOWN`. |

Phiên này chưa xác minh danh sách kỹ năng có thể cài thêm, chi phí thực tế hoặc khả năng sử dụng các công cụ trên ở phiên khác.
