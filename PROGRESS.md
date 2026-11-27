# PROGRESS

Nhật ký phiên, mục mới nhất ở trên. Mỗi mục tối đa 5 dòng: ngày, ai, issue, đã làm, việc tiếp theo hoặc blocker. Khi file quá 40 mục, gộp các mục cũ thành một dòng tóm tắt theo tháng.

## 2026-11-28 — Claude (Điều phối) — Work mặc định, dọn nhánh
- ChatGPT Work thành người thực thi mặc định (ADR-0004); CI thêm cổng "xong" theo `Closes #N`.
- Xóa 24 nhánh Zalo khỏi repo public; bản sao ở `archive/*` của repo private TTD-Zalo-Assistant.

## 2026-11-28 — Claude (Điều phối) — tái cấu trúc
- Chuyển sang mô hình agent-native: AGENTS.md gọn, Issue + `work/*.json` làm nguồn trạng thái, hook SessionStart/Stop cho Codex và Claude Code, CI `check`, cron nhắc việc treo.
- Tách Zalo Assistant sang repo private `TTD-Zalo-Assistant`; hồ sơ cũ chuyển vào `archive/legacy-2026-11/`.
- Tiếp theo: chủ dự án tin cậy hook Codex (`/hooks` trong Codex CLI), bật Codex review cho repo; Trợ lý A0 viết issue đầu tiên theo mẫu mới.
