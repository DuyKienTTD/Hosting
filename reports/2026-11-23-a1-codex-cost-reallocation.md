---
id: report-2026-11-23-a1-codex-cost-reallocation
type: report
status: proposed_for_review
updated_at: 2026-11-23
sensitivity: public
owner: chatgpt
---

# Báo cáo điều phối: A1 và cost-first routing

**Nguồn:** owner directive ngày 23/11/2026; main `e385c1bea2070973e3007e5717f7e980348d6ab3`; kế hoạch PR #6 `03fb56b6d3b4f42a1cb65c6e3c87a19099785044`; Work GOV-02 QA PR #28 [comment 7092060267](https://github.com/DuyKienTTD/Hosting/pull/28#issuecomment-7092060267); Codex GOV-02/S2 Phase A PR #30. Trước đó có [cost control override PR #28](https://github.com/DuyKienTTD/Hosting/pull/28#issuecomment-7092117583) và [Codex hold PR #30](https://github.com/DuyKienTTD/Hosting/pull/30#issuecomment-7092118230).

**Thay đổi:** A1 là ChatGPT thông thường phiên riêng, ưu tiên task thấp rủi ro; Codex exception-only. Hủy các gói Codex đơn giản chưa khởi chạy; giữ test/evidence commit lịch sử. Điều phối không thể tự chặn một phiên Codex đã chạy ngoài cuộc trò chuyện, nên chưa coi hold được nhận trừ khi ACK.

**Cụ thể:** GOV-02/S1 cross-package duplicate check chuyển đề nghị A1; GOV-02/S2 Phase B hủy giao Codex; 24 missing metadata entries/5 NO_TASK_YET/PR #10/#13 shared index chuyển governance+A1 review; không mở thêm Codex CI, dashboard, media, report/mock. Gate B vẫn BLOCKED, AI-03 NO_GO, S4 Linux NOT_RUN, real connectors UNTESTED.

**Năng lực A1:** profile là capability đề xuất, `GITHUB_WRITE` và `PYTHON_RUN` chưa được thử trong phiên A1; việc tạo profile không chứng minh Agent đã tạo hoặc đang thực hiện.

**Kiểm soát:** thay đổi trong Git là nguồn tài liệu đề xuất; chưa tác động VPS, Ads, billing, production hay PR implementation. Cần độc lập review trước khi merge. `NEXT_OWNER=ChatGPT Điều phối`.

## A1 capability follow-up — 2026-11-23

A1 đã ACK **vai trò** và báo cáo trực tiếp rằng GitHub, Drive, Gmail, Calendar, WordPress production/staging, Google Ads read, Canva, HeyGen, vidIQ/YouTube và QA/tooling đã kết nối. Những phép thử do A1 tự báo cáo được ghi `SELF_REPORTED_VERIFIED_BY_A1`, không phải điều phối đã lặp lại độc lập. Google Ads write, Google Cloud Shell, YouTube publish end-to-end, WordPress production write, video paid render, GitHub Python runner theo chính task chưa được chứng minh. A1-GOV02-QA01 chưa có ACK task ID hoặc commit/test mới. Không phát sinh external action hoặc billing.

## Delta điều phối và thực chứng sau QA (A0, 2026-11-23)

Phần trên là **checkpoint lịch sử tại thời điểm soạn**, không phải trạng thái hiện hành. A1 đã có role/task ACK, commit/PR #32 với Work độc lập [QA offline PASS_WITH_LIMITS](https://github.com/DuyKienTTD/Hosting/pull/32#issuecomment-7092722230), và proposal [PR #33](https://github.com/DuyKienTTD/Hosting/pull/33) được Hermes [QA nguồn PASS_WITH_LIMITS](https://github.com/DuyKienTTD/Hosting/pull/33#issuecomment-7093339962). Chưa có quyền Phase B, merge, live hoặc paid.

A0 đã tạm dừng Hostinger: [OPS](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7093337445), [SEC](https://github.com/DuyKienTTD/Hosting/pull/29#issuecomment-7093338761); thông báo chưa chứng minh Hostinger phiên riêng đã ACK. D2 OPS chuyển **A1 sole writer** qua nhánh mới stacked trên PR24 HEAD `e9c2d8f`; [lệnh A1](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7093346631). Work đã hoàn thành QA D1 18 nhóm synthetic, verdict NEEDS_HOSTINGER_DELTA; không thay lịch sử D1. Hermes nhận sửa F01–F03 PR34 theo A1 independent QA. Work vừa QA PR31, verdict `NEEDS_COORDINATOR_GOV_DELTA`, coordinator sửa delta G1–G3 trên cùng PR31 để QA targeted lại. Codex vẫn exception-only.
