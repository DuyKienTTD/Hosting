---
id: eng-01a-s3-offline-integration
type: task
status: ready_for_review
updated_at: 2026-11-23
sensitivity: public
owner: codex
reviewer: chatgpt
---

# ENG-01A-S3 — Tích hợp fixture S1/S2 và merge preview

**Handoff:** ChatGPT Điều phối → Codex → ChatGPT Điều phối. Đã nhận EXECUTE offline ngày 23/11/2026 ICT. [Chỉ thị](https://github.com/DuyKienTTD/Hosting/pull/13#issuecomment-7091064405).

**FIRST_ACTION / READ_SET:** Fetch main và PR #6/#7/#10/#13, kiểm rule SHA và tránh đường dẫn trùng. Đọc AGENTS, PROJECT, Workflow §§7–10, Security, STATE/CATALOG, hồ sơ Codex, BIZ-01, source và evidence S1 tại `79dfe8a`, S2 tại `0235b5f`. Dùng lại S1 8/8 và S2 7/7 trong phạm vi đã đo.

**ACCEPTANCE / TEST_DELTA:** Chạy mã S1/S2 ghim trong workspace tạm, bọc contract allowlist S3 và giữ bản engine gốc. Kiểm read GA4/WP/Woo, replay/conflict, failure/unknown, provenance, callback/receipt binding, process crash sau đọc và sau receipt trước ACK, no redispatch. Preview merge bằng checkout tạm, ghi thứ tự và diff metadata đề xuất. Linux chỉ dùng khi có runtime local an toàn.

**WRITE_SET:** Nhánh `codex/eng-01a-s3-offline-integration-2026-11-23` từ main, task này, `sandbox/connector-integration/`, report và evidence S3. Merge preview local không cập nhật refs nguồn, main hay CATALOG/STATE/CHANGELOG.

**STOP / INVARIANTS:** `LIVE_ENABLED=False`. Nếu thiếu pin hoặc cần external transport/credential, dừng đúng bước. Không thay PR #7/#10/#13, không chạy lại suite lịch sử, không KVM2/Docker/production/provider/paid.

**HANDOFF:** PR riêng về main, `ENG01A_S3_OFFLINE_INTEGRATION_PASS` hoặc blocker theo evidence, connector thật chưa thử. ChatGPT Điều phối nghiệm thu [báo cáo](../reports/2026-11-23-eng-01a-s3-integration-and-merge-preview.md) và [evidence](../reports/evidence/2026-11-23-eng-01a-s3-integration.json).
