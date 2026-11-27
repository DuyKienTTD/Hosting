---
status: accepted
date: 2026-11-28
decision-makers: Chủ dự án
supersedes: phần "Thực thi" của ADR-0002
---
# ADR-0004: ChatGPT Work là người thực thi mặc định

## Bối cảnh

Chủ dự án muốn dùng ChatGPT Work thay Codex làm người thực thi mặc định. Work dùng chung hạn mức gói ChatGPT với Codex. Work không chạy hook `.codex/hooks.json`, vì hook Codex chỉ chạy khi Codex cài trên máy. Do đó hook Stop không chặn được Work kết thúc sớm.

## Quyết định

- Người thực thi mặc định là ChatGPT Work. Codex hoặc Claude Code chỉ dùng khi việc cần chạy lệnh trên máy có hook.
- Thêm cổng "xong" vào CI, áp cho mọi người thực thi. PR có `Closes #N` thì `work/N.json` phải ở một trong hai trạng thái:
  - `done`, với mọi tiêu chí `passes: true` kèm `evidence`;
  - `blocked`, kèm `blocker`.
- Cùng với bảo vệ nhánh `main` (bắt buộc PR, check `check` xanh, áp cho cả admin), Work không merge được việc chưa xong.

## Hệ quả

- Work dừng giữa chừng thì không bị chặn trong phiên, nhưng PR không merge được. Cron `nhac-viec-treo` sẽ gắn nhãn `treo` sau 3 ngày.
- Đầu phiên, Work phải tự đọc `PROGRESS.md` và `work/`, vì không có hook nạp sẵn.
