---
id: eng-01a-s2-fake-channel-adapters
type: task
status: ready
updated_at: 2026-11-23
sensitivity: public
owner: codex
reviewer: chatgpt
---

# ENG-01A-S2 — GA4 và WordPress/WooCommerce synthetic read

**Handoff:** ChatGPT Điều phối → Codex → ChatGPT Điều phối. Đã nhận EXECUTE offline ngày 23/11/2026 ICT. [Chỉ thị](https://github.com/DuyKienTTD/Hosting/pull/10#issuecomment-7090796992).

**FIRST_ACTION / READ_SET:** Fetch main và PR #6/#10/#12, kiểm rule SHA, task và write-set không trùng. Đọc AGENTS, PROJECT, roadmap, Workflow §§7–10, Security, STATE/CATALOG, hồ sơ Codex, hợp đồng/evidence S1 và BIZ-01. S1 tại `79dfe8a` còn trên PR #10; chỉ dùng semantics theo SHA ghim, giữ package S2 tự chạy trên main. [BIZ-01](https://github.com/DuyKienTTD/Hosting/commit/8c821bbf1842eccb8519127f54ba7673965276d5).

**ACCEPTANCE / TEST_DELTA:** GA4 fake report kiểm attribution, ngày, allowlist và budget. WP/Woo fake reads kiểm site/posts/pages/products, EN/VI, cursor và watermark, 403/429/404. Chuẩn hóa source ID, timestamp, provenance, classification và đơn vị tiền/KPI. Kiểm mapping bất nhất, unknown, isolation sau lỗi và từ chối remote/config thật. Chạy chỉ suite S2. Linux/WSL chỉ dùng nếu có runtime local độc lập đã xác minh. Ghi `INTEGRATION_PENDING_PR10` nếu S1 chưa nhập vào main.

**WRITE_SET:** Nhánh `codex/eng-01a-s2-fake-channel-adapters-2026-11-23` từ main, task này, `sandbox/connector-channel-mocks/`, report và evidence S2 ngày 23/11. Đề xuất metadata repo bằng commit riêng. PR về main và remote readback.

**STOP / INVARIANTS:** `LIVE_ENABLED=False`. Fixture tổng hợp, read-only, zero requests, zero provider calls và zero USD. Dừng khi cần credentials/account, network, runtime hoặc dependency ngoài stdlib. Không chạy lại S1, không sửa PR #5/#7/#10, không KVM2/Docker/production. Paid Gate B giữ `BLOCKED_PREFLIGHT`.

**HANDOFF:** `ENG01A_S2_CHANNEL_MOCK_PASS` hoặc blocker có evidence. `REAL_GA4_UNTESTED / REAL_WP_WOO_UNTESTED`. ChatGPT Điều phối nghiệm thu bản ghi theo SHA.
