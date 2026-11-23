---
id: codex-gov02-s1-repo-validator
type: task
status: ready_for_review
updated_at: 2026-11-23
sensitivity: public
owner: codex
reviewer: chatgpt
---

# GOV-02/S1 — Kiểm tính nhất quán của metadata repository

**ACK:** EXECUTE GOV-02/S1 theo [chỉ thị Điều phối](https://github.com/DuyKienTTD/Hosting/pull/21#issuecomment-7091856757). Baseline và bộ quy tắc tại `e385c1bea2070973e3007e5717f7e980348d6ab3`.

**FIRST_ACTION / READ_SET:** Đối chiếu quy tắc, main, kế hoạch PR #6 và HEAD/file list của #10, #13, #19, #21, #16, #22, #24, #20, #23, #25. Dùng dữ liệu pin hiện có và không lặp lại các bộ test connector.

**WRITE_SET:** Nhánh riêng GOV-02/S1 từ main. Chỉ task này, `sandbox/repo-metadata-validator/` và báo cáo/evidence GOV-02/S1. Không đổi metadata chung, PR nguồn, main, runtime hoặc CI.

**ACCEPTANCE:** Kiểm task, owner, HEAD/tree/blob, report/evidence, phân loại trạng thái, chồng lấn file và metadata cũ bằng Git object local. Chạy fixture một ca hợp lệ và sáu nhóm lỗi. Công bố thứ tự review, các pin cần đánh giá lại và rollback trước khi bàn giao draft PR cho ChatGPT Điều phối. [Báo cáo](../reports/2026-11-23-codex-gov02-s1-readiness.md).
