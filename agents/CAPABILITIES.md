---
id: hosting-agent-capabilities
type: knowledge
status: draft
owner: Chat Dieu phoi
parent: agents/README.md
updated_at: 2026-11-25
sensitivity: public
---
# Hồ sơ năng lực — tám Agent
[Danh bạ](README.md) · [MKOE](../rules/HOSTING-MKOE-01.md). Candidate, không cấp quyền. Mọi năng lực lịch sử cần xác minh freshness theo phiên. Plugin, skill đã cài/có thể cài và chi phí thực tế chưa có inventory riêng: UNKNOWN trừ nơi ghi rõ. Không cài mới. Capacity mặc định một outcome; khả dụng hiện tại UNKNOWN trừ phiên Điều phối đang làm MKOE. Chi phí phát sinh phải có A0 duyệt.

| Agent / môi trường | Điểm mạnh, công cụ có bằng chứng | Điểm yếu / không phù hợp | Outcome phù hợp | Nguồn |
|---|---|---|---|---|
| Điều phối / ChatGPT | GitHub connector VERIFIED hiện tại; lập kế hoạch, điều phối và đối chiếu | Không tự dispatch chat khác, không tự QA độc lập; runtime Windows chưa xác minh | Điều phối và tổng hợp | [PR61](https://github.com/DuyKienTTD/Hosting/pull/61) |
| Trợ lý A0 / ChatGPT | Thẩm định độc lập, phân tích quyền và rủi ro REPORTED | Không tự nghiệm thu phần mình viết, không thay quyền chủ dự án | Appraisal cấp outcome | [Hồ sơ](a0-assistant.md) |
| Work / Linux cloud lịch sử | Git, Python, Node, Electron/React/TS/SQLite, build/test offline REPORTED | Linux GUI EPERM, Windows runtime không có trong phiên Zalo | Developer single writer hoặc QA độc lập | [MVP report](https://github.com/DuyKienTTD/Hosting/blob/52b7c5ccac572b170925d28c44c5613c1e73a849/reports/ttd-zalo-mvp01-dev.md) |
| A1 / ChatGPT Standard | Python, Git, validator, repair/test offline REPORTED | Live/Windows/connector hiện tại UNKNOWN | Kỹ thuật offline, security review khi độc lập | [PR36](https://github.com/DuyKienTTD/Hosting/pull/36) |
| A2 / ChatGPT Standard | UX, tri thức, blind comprehension REPORTED | Blind isolation tự khai báo; production/Windows UNKNOWN | UX, dữ liệu mẫu, review nghiệp vụ | [Receipt](https://github.com/DuyKienTTD/Hosting/pull/41#issuecomment-7101453005) |
| Codex / Windows x64 lịch sử | Electron runtime, IPC, PowerShell, Git, hash, rollback REPORTED | Ngoại lệ chi phí, foreground sampling gap; không mặc định admin | Windows QA khi được cấp quyền | [QA](https://github.com/DuyKienTTD/Hosting/pull/51#issuecomment-7142182692) |
| Hermes / WebUI | Git, reasoning, design, Python; 55 skills REPORTED 23/11 | HOLD_NO_NEW_TASKS lịch sử; policy block, VPS runtime khác WebUI | Design/QA offline nếu có grant | [Survey](https://github.com/DuyKienTTD/Hosting/commit/45b4032bb2f57e779a22d62f505ebefb387f29c9) |
| Hostinger Agent / hPanel | Inventory, DNS, backup feasibility REPORTED | PAUSED lịch sử; 502; SSH/root/restore UNKNOWN | Read-only infrastructure khi resume | [Review](https://github.com/DuyKienTTD/Hosting/pull/6#issuecomment-7090335207) |

A0 là chủ dự án, n8n là workflow engine không phải Agent. Hồ sơ không thay quyền, STOP/HOLD hoặc ACK. Danh sách plugin/skill từng phiên phải lấy từ inventory thật, không suy ra từ quảng cáo.
