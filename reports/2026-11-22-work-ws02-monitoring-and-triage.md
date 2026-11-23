---
id: work-ws02-monitoring-and-triage-2026-11-22
type: report
status: current
updated_at: 2026-11-23
sensitivity: public-redacted
task_id: ttd-work-ws02-monitoring-triage-001
owner: chatgpt-work
---

# INF-02 — Diễn tập runbook WS-02

**TASK** `ttd-work-ws02-monitoring-triage-001` | **AGENT** `chatgpt-work` | **BASE_SHA** `e385c1bea2070973e3007e5717f7e980348d6ab3` | **NEXT_OWNER** ChatGPT Điều phối.

ACK phân công `cdf0aed51965465601320fd57623a84065ad9c5b`; task blob `eb170fa`; AGENTS `cb6a8af`, Workflow `69ec0db`, Security `c24d608`, STATE `c8e8941`, CATALOG `719c9c5`, hồ sơ ChatGPT `97071fc`. Phương pháp: áp ba bộ số liệu giả vào ma trận và trình tự của [runbook](../runbooks/ws02-vps-monitoring-and-triage.md). Baseline lịch sử dùng [inventory](../inventory/current-vps-state.md), [audit](2026-11-21-n8n-hermes-integration-audit.md) và [security review](2026-11-21-vps-security-review.md).

| Test | Input giả và observed | Expected, chuyển xử lý và đóng ca | Result / evidence |
| --- | --- | --- | --- |
| T1 readiness | Phút 0/1/2: n8n health 200/200/200, readiness 503/503/503, Hermes dashboard 200/200/200 | Phút 2 chuyển Codex vận hành. Trước tiên đối chiếu hai probe cùng nguồn và đọc container state, rồi kiểm DB/migration. Không kết luận inference. Mẫu giả phút 3/4/5 readiness 200 và không restart/OOM mới → đóng | PASS trên giấy; lưu status/latency, timestamp, role alias và owner |
| T2 disk | Ba mẫu 5 phút cùng mount: 82/86/90 GiB trên 100 GiB, inode 41/41/42%. Tại mẫu cuối còn 10 GiB, mức tăng 8 GiB/10 phút, dự báo 12,5 phút nếu tiếp diễn | Mức khẩn, báo Codex + Hostinger Agent. Kiểm mount và bytes/inode trước khi khoanh vùng. Không cleanup thực. Chỉ đóng khi dưới ngưỡng và ổn định 3 mẫu; ca giả giữ mở | PASS trên giấy; lưu series cùng đơn vị và phép tính, không ghi tên volume nhạy cảm |
| T3 backup | Lịch giả mỗi 7 ngày và grace 24 h. Bản hoàn tất cuối cách 9 ngày; không có báo cáo restore. Tuổi 216 h vượt ngưỡng 192 h | Báo Hostinger Agent + Điều phối. Đọc lịch và bản thành công. Bản backup giả mới được xác nhận → đóng cảnh báo tuổi; khả năng restore vẫn UNKNOWN đến khi có diễn tập cô lập được duyệt | PASS trên giấy; lưu timestamp/trạng thái và trạng thái bằng chứng restore |

**VERDICT:** `WS02_RUNBOOK_READY_FOR_REVIEW`. **TEST_RESULTS:** 3/3 tình huống giả đạt quy trình phân loại, chuyển owner và điều kiện đóng ca. **BLOCKERS:** Không có đối với review tài liệu. Triển khai thật còn cần baseline, probe origin/endpoint đã duyệt, lịch backup và quyết định change task. Không lấy mẫu KVM2/hPanel, gọi endpoint production, tạo lịch hoặc gửi cảnh báo thật. Bàn giao ChatGPT Điều phối qua PR riêng.
