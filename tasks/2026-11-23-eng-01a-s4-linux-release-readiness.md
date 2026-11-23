---
id: eng-01a-s4-linux-release-readiness
type: task
status: ready_for_review
updated_at: 2026-11-23
sensitivity: public
owner: codex
reviewer: chatgpt
---

# ENG-01A-S4 — Manifest và merge readiness offline

**Handoff:** ChatGPT Điều phối → Codex → ChatGPT Điều phối. EXECUTE nhận ngày 23/11/2026 ICT. [Chỉ thị](https://github.com/DuyKienTTD/Hosting/pull/19#issuecomment-7091188510).

**FIRST_ACTION / READ_SET:** Fetch main, PR #6/#10/#13/#19, đọc quy tắc, PROJECT/roadmap, STATE/CATALOG, hồ sơ Codex và ba package đã ghim. Rà S4 trùng trước khi tạo branch. Kiểm Linux local hiện có, không mở runtime/CI thiếu căn cứ. Tái sử dụng kết quả Windows S1/S2/S3.

**ACCEPTANCE / TEST_DELTA:** Ghim HEAD, tree base, list path, blob và SHA-256. Kiểm assembly sandbox deterministic, reject drift/collision/override/extra files, transport bị khóa và unknown bất biến. Preview main + S1/S2/S3, phân loại conflict và điểm lệch metadata. Nếu có Linux local an toàn, chỉ chạy S3 delta với source ghim và fixture tạm. Nếu không, lưu runbook và `LINUX_NOT_RUN`.

**WRITE_SET:** Nhánh `codex/eng-01a-s4-linux-release-readiness-2026-11-23` từ main. Task này, `sandbox/connector-release/`, report/evidence S4. Đề xuất metadata trong report. PR mới vào main, không sửa PR gốc, không merge/rebase/push vào main.

**STOP / INVARIANTS:** `LIVE_ENABLED=False / MOCK_ONLY`. Không KVM2, production, connector/API account, credential, provider/paid hoặc Actions runner chưa xác minh. Không cài Linux hoặc bật Docker để vượt phạm vi. Gate B paid `BLOCKED_PREFLIGHT`.

**HANDOFF:** ChatGPT Điều phối nhận verdict scoped, PR/SHA, report/evidence và remote readback.

**RESULT:** `ENG01A_S4_MANIFEST_READY_LINUX_NOT_RUN`. [Báo cáo](../reports/2026-11-23-eng-01a-s4-release-readiness.md) và [evidence](../reports/evidence/2026-11-23-eng-01a-s4-release-readiness.json).
