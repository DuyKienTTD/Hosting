---
id: hermes-grow-01-s1-editorial-workflow-2026-11-23
type: task
status: complete
updated_at: 2026-11-23
sensitivity: public
owner: hermes
next_owner: chatgpt
related_prs:
  - https://github.com/DuyKienTTD/Hosting/pull/12
related_issue_comments:
  - https://github.com/DuyKienTTD/Hosting/pull/12#issuecomment-7090773585
---

# GROW-01/S1 — Hermes editorial workflow and sample content packages

## 1. Nguồn giao việc

- **TASK_ID:** `GROW-01/S1`
- **Assignment source:** PR #12 comment `7090773585`
- **Assignment URL:** <https://github.com/DuyKienTTD/Hosting/pull/12#issuecomment-7090773585>
- **BIZ-01 accepted source commit reused:** `8c821bbf1842eccb8519127f54ba7673965276d5`
- **Execution base:** `origin/main@e385c1bea2070973e3007e5717f7e980348d6ab3`

## 2. Phạm vi được phép

Thực hiện **draft/fake-only** cho workflow nội dung và media của TTD METAL:

1. SOP vòng đời editorial/asset.
2. Ba gói nội dung mẫu `P1`, `P2`, `P3`.
3. Approval matrix và asset governance.
4. Feasibility mapping tái sử dụng kết quả BIZ-01.
5. JSON schema/example và kiểm thử cổng phê duyệt bằng dữ liệu giả.

## 3. Giới hạn bắt buộc

- Không dùng API trả phí.
- Không publish.
- Không thay đổi account hoặc production.
- Không kết nối connector thật.
- Không làm lại khảo sát BIZ-01.
- Không sửa `CATALOG.yaml`, `STATE.md`, `CHANGELOG.md`, `rules/` hoặc nội dung PR #12.
- Không dùng dữ liệu khách hàng thật.
- Không bịa giá, tồn kho, chiết khấu, chứng nhận kỹ thuật hoặc claim an toàn.

## 4. WRITE_SET đã dùng

- `tasks/2026-11-23-hermes-grow-01-s1-editorial-workflow.md`
- `reports/2026-11-23-hermes-grow-01-s1-media-workflow.md`
- `reports/evidence/2026-11-23-hermes-grow-01-s1-content-packages.json`
- `runbooks/grow-01-content-review-and-publish-gates.md`

## 5. Đầu ra bàn giao

- Báo cáo chính: `reports/2026-11-23-hermes-grow-01-s1-media-workflow.md`
- Evidence JSON: `reports/evidence/2026-11-23-hermes-grow-01-s1-content-packages.json`
- Runbook review/publish gate: `runbooks/grow-01-content-review-and-publish-gates.md`

## 6. Kết quả trạng thái

`GROW01_S1_DRAFT_WORKFLOW_READY_FOR_REVIEW`

## 7. Ghi chú owner kế tiếp

ChatGPT Điều phối có thể dùng gói này để:

1. review business/claim boundaries,
2. chuyển cho Codex phần contract/schema offline nếu cần,
3. quyết định có mở PR từ branch Hermes hay chỉ cherry-pick/selective merge,
4. tách tiếp `BIZ-02` cho KPI/priority thật khi owner chốt mục tiêu tăng trưởng.