---
status: accepted
date: 2026-11-28
decision-makers: Chủ dự án (giao toàn quyền cho Claude-Điều phối ngày 28/11/2026)
---
# ADR-0001: Chuyển repo Hosting sang mô hình agent-native tối giản

## Bối cảnh

Đến ngày 28/11/2026 repo có 25 file quy tắc, cùng lúc README/PROJECT ghi "KNG-01 ONLY" còn STATE ghi đã chuyển hướng sang Zalo. Trạng thái nằm rải ở STATE.md, program/current.json, CATALOG.yaml và các cửa sổ chat. Ba lỗi lặp lại:

- agent quên việc giữa các phiên;
- agent biết việc nhưng dừng trước khi xong (Điều phối kết thúc lượt sớm);
- việc rơi khi chuyền tay qua chat.

Các lỗi này khớp với nhóm lỗi đặc tả và kiểm chứng trong nghiên cứu MAST (Cemri và cộng sự, NeurIPS 2025). Tài liệu dài hơn không sửa được, vì agent có thể không đọc hoặc không tuân theo.

## Phương án đã xét

1. Giữ cấu trúc, rút gọn tài liệu. Rẻ, nhưng vẫn dựa vào việc agent tự giác.
2. Spec Kit cho toàn repo. Hợp với phát triển sản phẩm, quá nặng cho vận hành hạ tầng.
3. **Agent-native tối giản và cổng bằng máy (chọn).**

## Quyết định

- **Một AGENTS.md ngắn** (chuẩn mở của Agentic AI Foundation), chỉ chứa điều agent không tự suy ra được: vai trò, quyền, luật cứng. CLAUDE.md import lại file này.
- **Nguồn trạng thái:** GitHub Issues cho việc, `work/<issue>.json` cho tiêu chí xong (mẫu feature list `passes: false` của Anthropic), `PROGRESS.md` cùng lịch sử git cho nhật ký. Bỏ STATE.md, current.json, CATALOG.yaml.
- **Cổng bằng máy:**
  - hook SessionStart nạp ngữ cảnh;
  - hook Stop chặn kết thúc khi tiêu chí chưa đạt (chạy trên Codex local và Claude Code; Codex cloud không chạy hook);
  - CI `check` bắt buộc trước merge;
  - cron gắn nhãn `treo` cho việc đứng yên 3 ngày.
- **Thư mục:** `docs/adr`, `docs/runbooks`, `docs/reference` (chia theo Diátaxis), `infra/`, `work/`, `scripts/`.
- Toàn bộ hồ sơ cũ chuyển nguyên vẹn bằng `git mv` vào `archive/legacy-2026-11/`. Lịch sử git còn đủ.

## Hệ quả

- Tốt: một nguồn trạng thái, máy chặn thay cho lời dặn, agent mới chỉ cần đọc khoảng 60 dòng.
- Đánh đổi: các validator KNG cũ (program/kng, scripts/validate-*) không còn chạy trong CI. Nếu cần dùng lại, mở issue để đưa từ archive ra.
- Hook Codex cần chủ dự án tin cậy một lần bằng lệnh `/hooks`, và phải tin cậy lại mỗi khi file hook thay đổi.
