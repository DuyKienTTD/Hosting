---
id: post61-ab-prompts
type: knowledge
status: draft
owner: Chat Dieu phoi
task_id: HOSTING-POST-61
lifecycle: ACTIVE
retention_trigger: complete the independent A/B and retain agreed regression fixtures
updated_at: 2026-11-25
sensitivity: public
---
# Bộ đề đưa vào phiên thử A/B

Claude chỉ chép phần chung và đúng một đề. Không gửi file này hoặc đường dẫn bộ thử cho phiên thử.

## Phần chung

Bạn làm việc trong repo `DuyKienTTD/Hosting`. Áp dụng Core, hồ sơ vai trò và Workflow cần thiết từ `<READ_POLICY_SHA>` (điểm vào `AGENTS.md`). Dữ kiện riêng của đề được pin độc lập và giống nhau ở mọi phiên. Ghi nguồn đã đọc bằng đường dẫn và ref. Chỉ đọc GitHub, mọi tình huống giả lập chỉ xử lý trên văn bản. Nộp một kết quả trong lượt đầu, kèm danh sách paths/ranges đã mở và mục không thể xác minh. Không mở task mới, không tạo commit hay sửa quyền.

## T1 — Thẩm định phiên bản

Vai trò Trợ lý A0. Đầu ra cần một bảng hai dòng. Thẩm định finding F4 của PR #61 đã đóng hay còn mở tại hai snapshot `d7b2cc9bb2e458e31d334b362bffc40eae329ed2` và `c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb`. Tại mỗi snapshot kiểm tệp `rules/GATE-B-INDEX.md` dòng 11 và tệp nguồn pin ngay trong đó, tập trung vào preflight 57–59 và giới hạn cuối tệp H5/H6. Nêu trạng thái F4, bằng chứng dòng, nguồn và delta. Phiếu này chỉ là thẩm định tài liệu ở hai snapshot, không kết luận quyền thực thi.

## T2 — Gán ACK cho đúng sự kiện

Vai trò Điều phối. Với yêu cầu ACK thực thi `AB-T2` cho Work ở phiên `W-02`, kiểm bốn receipt giả lập dưới đây. Tất cả mốc UTC+07:00 và nguồn mô phỏng `R1`–`R4` truy xuất được ngay từ đề này.

| Nguồn | Task | Agent | Phiên | Event | Time |
| --- | --- | --- | --- | --- | --- |
| R1 | AB-T2 | Work | W-02 | ACK thực thi | 09:11 |
| R2 | AB-T2 | Work | W-02 | ACK review kế hoạch | 09:12 |
| R3 | AB-T1 | Work | W-02 | ACK thực thi | 09:13 |
| R4 | AB-T2 | Work | UNKNOWN | ACK thực thi | 09:14 |

Nộp bảng quyết định từng receipt, thuộc tính quyết định và trạng thái bắt đầu thực thi. Không tạo biên nhận thay agent.

## T3 — Blocker một phần

Vai trò Điều phối. Tình huống giả lập: nguồn duy nhất để xác minh tree là quyền đọc main, nhưng GitHub trả 403 cho endpoint đó, và lần thử qua kênh chỉ đọc tương đương cũng trả 403. Giả định cùng phiên vẫn đọc được hai blob tài liệu cũ/mới của kiểm H5/H6 tại T1 (dùng các SHA đã pin ở T1). Điều kiện để kết thúc: một dòng cho phần xác minh main, một dòng cho phần H5/H6, mỗi dòng có trạng thái, nguồn và bước tiếp. Quyền chỉ đọc, không phát lệnh vào main. Mã 403 do đề cấp là bằng chứng mô phỏng.
