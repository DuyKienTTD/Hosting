---
id: codex-gov02-s2-reconciliation-plan
type: task
status: ready_for_review
updated_at: 2026-11-23
sensitivity: public
owner: codex
reviewer: chatgpt
---

# GOV-02/S2 — Kế hoạch reconciliation trước merge

**ACK** EXECUTE GOV-02/S2 PHASE A theo [chỉ thị](https://github.com/DuyKienTTD/Hosting/pull/28#issuecomment-7092005693). Bộ quy tắc và baseline ở `e385c1bea2070973e3007e5717f7e980348d6ab3`.

**FIRST_ACTION / READ_SET** Xác minh main, PR #28 tại `6dafae50bd17bc1a18080b13b86c5b8c35573580`, các PR nguồn và index trên từng tree. Đối chiếu từng finding S1 với HEAD/blob hiện thời và bổ sung hồ sơ ngoài ledger S1.

**WRITE_SET** Task này, [báo cáo](../reports/2026-11-23-codex-gov02-s2-merge-readiness.md) và [evidence](../reports/evidence/2026-11-23-codex-gov02-s2-merge-readiness.json) trong draft PR riêng. Giai đoạn A không mở quyền sửa index, PR nguồn hoặc main.

**ACCEPTANCE / HANDOFF** Kế hoạch chỉ định canonical path, blob, hành động, writer, điều kiện áp dụng và test delta cho từng nhóm finding. ChatGPT Điều phối nhận draft để review. Giai đoạn B giữ `BLOCKED_PENDING_INDEPENDENT_QA_AND_COORDINATOR_APPROVAL`.
