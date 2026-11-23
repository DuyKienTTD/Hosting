# ChatGPT Work — Roadmap UI, Integration & Independent Assurance

**Owner:** ChatGPT Work | **ROADMAP_STATUS:** `ROADMAP_PARTIAL_BLOCKED` | **READ_SET:** existing PR31 Work QA assignment, program docs, offline connector release evidence, current UI PR16 and relevant policy; **WRITE_SET:** own roadmap + independent UI/integration branch after task assignment; Work QA verdicts as PR comments. **STOP:** cannot control sessions, tool not present, source drift, bad provenance, unapproved live/paid/publish.

| ID | Required skills | Task / measurable deliverable | Depends | Status | Evidence / UTC |
|---|---|---|---|---|---|
| EXIST-QA31 | K-QA,K-GIT,K-SEC | Complete already-assigned seven-file PR31 independent governance QA; do not rerun D7 unrelated suites | PR31 existing task | PLANNED | — |
| G1-04 | K-QA,K-DATA,K-TEST | Compare context pack vs original on content, Git-change and sensitive tasks; measure errors and token proxy | G1-02,G1-03 | PLANNED | — |
| UI-01 | K-UX,K-BROW,K-PY | Build/test interactive operator UI prototype from A2 spec, including empty/loading/UNKNOWN/error states | G0-02,G2-02 | PLANNED | — |
| UI-02 | K-UX,K-API,K-TEST,K-SEC | Connect UI to durable task/evidence state and approval indicators; demonstrate sandbox E2E | UI-01,INF-03 | PLANNED | — |
| CTRL-01 | K-BROW,K-AUTO,K-TEST | Test 2 original chat sessions with synthetic task dispatch, actual ACK, receipts and uncertainty dedupe | G2-01 | PLANNED | — |
| UC01-02 | K-WP,K-API,K-TEST,K-UX | Turn A2 real read-only gap audit into repeatable UI/worker flow, show bounded failures | UC01-01,UI-01 | PLANNED | — |
| GROW-03 | K-DATA,K-ADS,K-API,K-UX | Prove cross-channel reporting integration with sourced quality/freshness, distinguish mock vs live | GROW-01,UI-02 | PLANNED | — |

**KNG-01 priority override (2026-11-23):** All unrelated roadmap feature items are ON_HOLD_DEPENDENCY_KNG01 until Work independent QA, coordinator integration, A0-authorized merge and a new dispatch/actual ACK. Historical PLANNED items remain proposals, not current task orders.

**Completion:** a running prototype/workflow with clear environment, checks, actual receipts and independent QA for any Work-authored material code by another qualified agent. **A GitHub notification is not session ACK.** Complete existing PR31 QA before conflicting governance review, and independent UI development is now ON_HOLD_DEPENDENCY_KNG01; only scoped KNG QA may proceed after real session ACK.
## Cách tự cập nhật

Chủ roadmap cập nhật **chính file này** sau khi hoàn thành một đầu việc: chuyển `PLANNED → IN_PROGRESS → DONE_WITH_EVIDENCE`, ghi `EVIDENCE` (commit/PR/log/source link), `UTC`, kết quả PASS/FAIL và lỗi thực tế. Không yêu cầu A0/Điều phối nghiệm thu từng dòng. Chỉ thông báo một lần khi roadmap đạt `READY_FOR_ROADMAP_ACCEPTANCE` hoặc `ROADMAP_PARTIAL_BLOCKED`. Nếu còn công việc an toàn độc lập, phải làm tiếp. Không đẩy secret hoặc PII lên Git.

Nếu cuối roadmap có hạng mục thực sự không thể thực hiện sau các nỗ lực hợp lệ, phải sử dụng nguyên văn: **Đã làm hết công việc có thể làm, một số công việc chưa thể làm do "Bảo mật"/ "Giới hạn kỹ thuật".** Kèm từng lỗi, bước đã thử, bằng chứng và hướng khắc phục. Không suy diễn môi trường hay quyền chỉ từ tên tài khoản.

Quy trình và các giới hạn: [Operating Protocol](../OPERATING_PROTOCOL.md). Quy tắc hiện hành trên main luôn có hiệu lực cho tới khi candidate được tích hợp hợp lệ.

## DGN-FEASIBILITY — bàn giao thiết kế

**Session ACK:** `TASK_ACKNOWLEDGED — DGN-FEASIBILITY`. **Source main:** `d549564de52429e777c68daf9df7a93df5f22f27`. Các mục PLANNED/HOLD phía trên là lịch sử thiết kế và không được kích hoạt bởi nghiên cứu này.

| Phạm vi | Trạng thái | Kết quả / bước tiếp theo |
|---|---|---|
| DGN-1 · UI feasibility | DONE_WITH_EVIDENCE | Work Linux kiểm lại PR16 DOM contract 10/10 PASS, 7 kiểm tra bổ sung. A2 dùng ma trận màn hình, nguồn và acceptance để chốt đặc tả. Browser accessibility, RBAC và live data UNKNOWN. |
| DGN-2 · Giao việc và trạng thái | DONE_WITH_EVIDENCE cho phương án thủ công | Git/derive PASS, SQLite fixture PASS. Điều phối dùng owner-forward, ACK thật, receipt theo attempt, append-only evidence và STOP/rollback có đối soát. |
| Kết nối/dispatch/receipt tự động trên phiên hiện hữu | UNKNOWN · BLOCKED | Không có đích/kênh cross-session đã xác minh, STOP cấm điều khiển Agent khác. Giữ owner-forward cho đến khi có kênh hợp lệ và phép thử được giao riêng. |

**Bằng chứng và giới hạn:** [Báo cáo DGN-FEASIBILITY](../../reports/2026-11-24-dgn-feasibility-work.md), quan sát 23/11/2026 18:07 UTC. **NEXT_OWNER:** A2 tiếp nhận UI feasibility, Chat Điều phối tiếp nhận operating model. Giữ nguyên quyền tác giả của A2, A1 và Điều phối. Không kích hoạt UI/CTRL/M1 hoặc cấp quyền live.

**Đã làm hết công việc có thể làm, một số công việc chưa thể làm do "Bảo mật"/ "Giới hạn kỹ thuật".**
