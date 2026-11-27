---
status: accepted
date: 2026-11-28
decision-makers: Chủ dự án (giao toàn quyền cho Claude-Điều phối ngày 28/11/2026)
---
# ADR-0002: Vai trò và quyền của agent

## Bối cảnh

Mô hình cũ có 8 hồ sơ agent (Điều phối, Trợ lý A0, Work, A1, A2, Codex, Hermes, Hostinger) và ACK qua chat. Codex mặc định bị cấm vì lo chi phí. Trên thực tế, Codex và Work dùng chung hạn mức gói ChatGPT, còn chat thường không bị trừ hạn mức. Mọi chuyển giao đi qua chủ dự án copy-paste.

## Quyết định

Gộp thành 4 vai trò người hoặc agent, cộng 2 lớp máy. Quyền thực thi bằng branch protection và CI, không bằng lời dặn.

| Vai trò | Ai | Quyền | Lý do |
|---|---|---|---|
| Chủ dự án | Chủ tài khoản | Mọi quyền. Merge `risk:prod`, `risk:cost`, `risk:secret`. | Quyết định không đảo ngược được phải là người. |
| Lập kế hoạch | Trợ lý A0 (ChatGPT chat) | Viết issue và tiêu chí, review bằng comment | Chat không trừ hạn mức; giỏi phân tích, không có hook để tự kiểm. |
| Điều phối | Claude | Giao việc, merge PR không có nhãn risk khi CI xanh và đã có review, giữ PROGRESS | Theo phân công của chủ dự án ngày 26/11/2026. |
| Thực thi | Codex (mặc định), Claude Code, ChatGPT Work (thao tác web) | Chỉ ghi lên nhánh `agent/*`, phải qua PR | Có hook SessionStart/Stop khi chạy local; Work dùng cho hPanel và WordPress. |
| Kiểm tự động | CI `check`, Codex review | Chặn merge | Người viết không tự nghiệm thu. |
| Runtime | n8n, Hermes | Chạy cấu hình đã merge | Không phải thành viên đội; không nhận lệnh từ chat. |

Các vai trò cũ: A1, A2, Work-QA gộp vào "Thực thi". Hostinger Agent giữ trạng thái PAUSED cho tới khi chủ dự án mở lại. "Codex NOT_AUTHORIZED" bị bãi bỏ, vì Codex dùng hạn mức có sẵn của gói ChatGPT.

## Cấu hình GitHub đi kèm

Nhánh `main`:
- bắt buộc qua PR;
- bắt buộc check `check` xanh;
- cấm force push và cấm xóa nhánh;
- không bắt buộc approval, vì repo chỉ có một tài khoản người và tác giả không tự duyệt được PR của mình. Review độc lập do Codex review và Điều phối đảm nhận.

## Hệ quả

- Hết bước "ACK trong chat". Issue được giao chính là lệnh, PR là bằng chứng.
- Chi phí nằm trong hạn mức gói ChatGPT. Credit chỉ bị dùng khi hết hạn mức và lượt đặt lại; chủ dự án có thể tắt "Tự động nạp lại" để giữ trần cứng.
