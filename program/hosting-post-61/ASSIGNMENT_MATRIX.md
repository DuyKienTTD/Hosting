---
id: post61-assignment
type: knowledge
status: draft
owner: Chat Dieu phoi
task_id: HOSTING-POST-61
lifecycle: ACTIVE
retention_trigger: A0 acceptance and closure
updated_at: 2026-11-25
sensitivity: public
---
# Ma trận phân công

[Chỉ mục](README.md) · [Trạng thái](WORK_ITEMS.md)

Chat Điều phối sở hữu cả outcome và có quyền ghi được kiểm tra trong phiên. Ứng viên khác cần cấp quyền theo phiên; trạng thái lấy từ WORK_ITEMS. A0 nghiệm thu toàn bộ. Claude phụ trách chạy/chấm thực nghiệm sau khi chủ dự án chuyển bộ thử, không nhận quyền ghi nhánh.

| ID | Năng lực cần | Phụ thuộc | Ứng viên 1 / owner | Ứng viên 2 theo năng lực |
| --- | --- | --- | --- | --- |
| ● [FIX-F4](tasks/FIX-F4.md) · DONE | GitHub, line anchors và đối chiếu blob | HEAD PR #61 | Chat Điều phối | A1 · Git/validator |
| ○ [POST-01](tasks/POST-01.md) · BLOCKED | Git ancestry, tree, CI GitHub | Chủ dự án merge #61 | Chat Điều phối | Work · QA GitHub độc lập |
| ● [POST-02](tasks/POST-02.md) · DONE | GitHub và đối chiếu capability/phiên | CV và nguồn gốc | Chat Điều phối | A1 · kiểm kê và metadata |
| ● [POST-03](tasks/POST-03.md) · DONE | Thiết kế thử nghiệm, đánh giá mù | Hai snapshot đã pin | Chat Điều phối | A2 · QA mù |
| ● [POST-04](tasks/POST-04.md) · DONE | Đọc Git, mã hóa UTF-8 và định tuyến module | Hai snapshot đã pin | Chat Điều phối | A1 · Git/Python đo blob |
| ● [POST-05](tasks/POST-05.md) · DONE | Phân tích sự kiện, bằng chứng và thống kê mô tả | Nguồn Claude và GitHub | Chat Điều phối | Trợ lý A0 · thẩm định bằng chứng |
