---
id: eng-01a-s1-offline-connector-contract
type: task
status: ready_for_review
updated_at: 2026-11-23
sensitivity: public
owner: codex
reviewer: chatgpt
---

# ENG-01A-S1 — Hợp đồng connector và fake adapter offline

**Handoff:** ChatGPT Điều phối → Codex → ChatGPT Điều phối. Lệnh thực thi nhận ngày 23/11/2026 ICT. Một gói kỹ thuật offline. [Chỉ thị thực thi](https://github.com/DuyKienTTD/Hosting/pull/7#issuecomment-7090656024) · [Master Plan](https://github.com/DuyKienTTD/Hosting/blob/cdf0aed51965465601320fd57623a84065ad9c5b/tasks/2026-11-23-multi-agent-master-allocation-review.md).

**FIRST_ACTION / READ_SET:** Fetch latest main và PR #6/#7, xác nhận rule SHA, kiểm trùng đường dẫn và nhánh. Đọc AGENTS, Workflow §§7–10, Security, STATE/CATALOG, PROJECT, hồ sơ Codex và contract/callback code B2-N/O liên quan. Đối chiếu Work O1–O4 tại `5a036fa` và B2-P tại `54b4e18`. Dùng Python/SQLite cục bộ.

**PREVIOUSLY_VERIFIED:** B2-N đo restart Hermes. B2-O đo tuyến fake local và restart receiver. Dùng lại semantics binding, idempotency và receipt commit trước ACK. Worker restart tại `working/sending` là test delta S1. [Work QA](https://github.com/DuyKienTTD/Hosting/commit/5a036fa8952b0dede7470579011a053bcdce51b1).

**WRITE_SET:** Nhánh `codex/eng-01a-s1-offline-contract-2026-11-23` từ main. Tệp task này, `sandbox/connector-contracts/`, report và JSON evidence ENG-01A-S1 ngày 23/11. Metadata repository chỉ thay đổi theo policy trong commit đề xuất riêng. Giữ PR #5/#7 và bằng chứng lịch sử.

**ACCEPTANCE / TEST_DELTA:** Admission kiểm schema, approval, deadline, budget và digest. Cùng key và payload replay cùng job, khác payload trả 409. Kiểm success/failure, timeout/late result, callback identity, receipt đọc lại và crash thật ở `working/sending`. Mỗi job có tối đa một fake dispatch và một receipt, worker giữ unknown và không tự redispatch. Nêu rõ cửa sổ không chứng minh được, source/environment SHA và kết quả từng ca. Chỉ nghiệm thu `ENG01A_S1_OFFLINE_CONTRACT_PASS` trong fixture, `REAL_CONNECTOR_UNTESTED`.

**STOP / INVARIANTS:** Fake dữ liệu tổng hợp, SQLite tạm riêng, `LIVE_ENABLED=False`. Thiếu bằng chứng cách ly, bind callback hoặc phát hiện công việc trùng thì dừng phần liên quan. Zero network/provider calls và paid cost trong fixture. Không truy cập KVM2, production, account connector, credential, ledger/permit/kill switch thật. Paid Gate B giữ `BLOCKED_PREFLIGHT`.

**ARTIFACT / NEXT_OWNER:** PR riêng vào main, [báo cáo](../reports/2026-11-23-eng-01a-s1-offline-connector-contract.md) và [evidence](../reports/evidence/2026-11-23-eng-01a-s1-offline-connector-contract.json) đã khử nhạy cảm, test delta và remote readback. ChatGPT Điều phối nghiệm thu offline.
