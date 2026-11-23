---
id: ws02-vps-monitoring-and-triage
type: runbook
status: proposed
updated_at: 2026-11-23
sensitivity: public-redacted
---

# WS-02 — Giám sát và xử lý sự cố ban đầu

Phạm vi: VPS KVM2, n8n và Hermes dashboard. Baseline lịch sử 21/11/2026: n8n 2.45.7 health/readiness 200, Hermes 0.22.5 dashboard 200, restart/OOM 0. Docker healthcheck chưa cấu hình ở thời điểm audit. Health hiện tại, baseline tải, lịch backup thực tế, endpoint TLS được duyệt và khả năng restore: **UNKNOWN** trong lượt INF-02. [Inventory](../inventory/current-vps-state.md) · [Audit](../reports/2026-11-21-n8n-hermes-integration-audit.md) · [Security review](../reports/2026-11-21-vps-security-review.md).

## Kiểm đầu tiên và chuyển xử lý

Các chu kỳ và ngưỡng dưới đây là đề xuất cho triển khai sau. Định danh đúng host, project, container, endpoint và phạm vi quyền trước khi lấy mẫu. Mỗi sự kiện ghi UTC, service alias, nguồn, giá trị/đơn vị, kỳ vọng, phạm vi, bước đọc tiếp và owner. Tín hiệu thiếu dữ liệu ghi UNKNOWN kèm lỗi thu thập. Gửi mẫu đã lược bỏ định danh nhạy cảm cho Điều phối; giữ log thô trong hệ thống nội bộ được phép.

| Tín hiệu | Nguồn và cách lấy mẫu đề xuất | Điều kiện mở triage và ý nghĩa | Người nhận và phép đọc đầu tiên |
| --- | --- | --- | --- |
| n8n liveness | HTTP GET nội bộ `/healthz`, mỗi phút, timeout 5 s | 3 mẫu liên tiếp khác 200 hoặc timeout: app không reachable từ vị trí probe | Codex vận hành. Kiểm DNS/port nội bộ và trạng thái container; ghi status/latency, tránh xuất response body |
| n8n readiness | HTTP GET nội bộ `/healthz/readiness`, mỗi phút, timeout 5 s | 3 mẫu lỗi: chưa sẵn sàng xử lý. Health 200 chỉ chứng minh HTTP reachable | Codex vận hành. So hai endpoint cùng thời điểm, kiểm state DB/migration từ nguồn đã duyệt |
| Hermes dashboard | Probe health dashboard đúng route đã xác minh, mỗi phút, timeout 5 s | 3 mẫu lỗi hoặc redirect/HTML ngoài contract: dashboard degrade hoặc probe sai. Inference health vẫn UNKNOWN | Codex, Hermes hỗ trợ. Kiểm route và HTTP status/content-type cùng trạng thái container |
| Container down/restart/OOM | `docker inspect --format '{{.State.Status}} {{.State.OOMKilled}} {{.RestartCount}} {{.State.StartedAt}}' <container>` mỗi phút | Down ngoài cửa sổ bảo trì hoặc OOM mới: báo ngay. Từ 2 restart/10 phút cùng ID: triage restart loop. ID đổi thì xác minh recreate để xây baseline mới | Codex vận hành. Đối chiếu ID, start time, exit/OOM và maintenance window |
| Disk/inode | `df -P` và `df -Pi` trên filesystem host/data đã xác minh, mỗi 5 phút | Cảnh báo ≥80% hoặc dự báo đầy ≤24 h, khẩn ≥90% hoặc ≤4 h. Chỉ ngoại suy khi ≥3 mẫu có xu hướng nhất quán; kiểm cả inode | Codex + Hostinger Agent. Đọc lại đúng mount, free bytes/inodes; khoanh vùng dung lượng bằng phép đọc có giới hạn |
| CPU/RAM | Host counters hoặc hPanel, cộng `docker stats --no-stream` cho container, mỗi phút | CPU host ≥85% công suất hoặc RAM available ≤15% trong 15 phút: triage, đối chiếu OOM/latency. Ngưỡng theo workload: UNKNOWN | Codex + Hostinger Agent. So host và container cùng cửa sổ; diễn giải CPU theo số core và RAM theo giới hạn thật |
| Backup | hPanel Backups & Monitoring mỗi ngày, đọc mốc backup hoàn tất và lịch được duyệt | Quá kỳ lịch +24 h hoặc không có bản thành công thì triage. Lịch chưa xác minh: UNKNOWN. Metadata chỉ chứng minh bản được liệt kê | Hostinger Agent + Điều phối. Đọc timestamp, trạng thái và kỳ backup; tra bằng chứng restore riêng |
| HTTPS | Sau khi xác nhận hostname/route được phép, probe TLS/SNI và HTTP từ nguồn đã duyệt mỗi 5 phút | 3 mẫu lỗi validate/route hoặc cert còn <14 ngày. Endpoint chưa xác nhận: UNKNOWN | Hostinger Agent + Codex. Xác minh hostname, SNI, status và hạn cert, không ghi hostname thật ra Git |

Nguồn đọc ngày 23/11/2026: [n8n monitoring](https://docs.n8n.io/hosting/logging-monitoring/monitoring/) · [Docker inspect](https://docs.docker.com/reference/cli/docker/inspect/) · [Docker stats](https://docs.docker.com/reference/cli/docker/container/stats/) · [Hostinger backups](https://www.hostinger.com/support/1583232-how-to-back-up-or-restore-a-vps-at-hostinger/).

## Trình tự xử lý

1. Xác thực probe và mốc thời gian. Gắn incident theo service/tín hiệu; gộp mẫu lặp trong cùng sự kiện.
2. Thu phép đọc đầu tiên theo bảng. So trạng thái độc lập trước khi suy nguyên nhân. Ghi điều kiện chuyển owner, người đang xử lý và lần đọc kế tiếp.
3. Dùng tiêu chí ca tương ứng để đóng sự kiện. Mọi sửa cấu hình, cleanup, khởi động lại hoặc restore chuyển sang change task riêng có phê duyệt.

| Ca | Trình tự đọc và chuyển owner | Điều kiện phục hồi |
| --- | --- | --- |
| Readiness n8n lỗi, Hermes dashboard khỏe | Kiểm liveness và readiness từ cùng nguồn → state n8n/OOM → trạng thái DB/migration bằng phép đọc được duyệt → Codex vận hành khi đủ 3 mẫu hoặc thấy container down/OOM | 3 mẫu readiness 200 liên tiếp, liveness ổn định, không có restart/OOM mới; ghi thời điểm và latency |
| Disk tăng nhanh | Kiểm mount, free bytes và inode → đối chiếu 3 mẫu cùng filesystem → khoanh vùng log/volume bằng metadata → chuyển Codex và Hostinger Agent theo ngưỡng; không xóa | Dung lượng dưới ngưỡng, tốc độ tăng đã ổn định và 3 mẫu 5 phút đạt; ghi nguyên nhân hoặc UNKNOWN |
| Backup quá hạn hoặc thiếu restore evidence | Đọc lịch/kỳ, backup thành công gần nhất → tính trễ → tra report diễn tập restore riêng → chuyển Hostinger Agent và Điều phối | Đóng cảnh báo tuổi khi backup mới đúng lịch được xác nhận. Chỉ xác nhận restore khi có diễn tập cô lập được duyệt và kiểm dữ liệu/app sau restore |

## Bàn giao triển khai sau review

Change task riêng xác định owner, quyền chỉ đọc, probe origin/allowlist, endpoint chính xác, lịch/ngưỡng và lịch bảo trì, nơi lưu mẫu đã lược bỏ dữ liệu, retention và kênh nhận cảnh báo thử. Kiểm preflight identity, headroom và rollback, sau đó kiểm trên mock với mẫu good/bad/missing, dedupe, recovery và một đích cảnh báo thử được duyệt. Kiểm chênh lệch CPU/RAM, health trước/sau và xác nhận không mở thêm cổng. Nếu bắt đầu ảnh hưởng dịch vụ, sai đích, lộ dữ liệu hoặc spam cảnh báo, dừng probe/schedule mới, khôi phục cấu hình collector trước thay đổi và kiểm lại health. Đầu ra lượt này chỉ là runbook và [diễn tập giả](../reports/2026-11-22-work-ws02-monitoring-and-triage.md).
