---
id: multi-agent-handoff
type: rule
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# Quy tắc vận hành Agent

Candidate theo A0 24/11/2026. Không cấp quyền. Hiệu lực sau QA độc lập, A0 duyệt merge, xác minh main/CI. [MKOE](HOSTING-MKOE-01.md) · [Lịch sử](../references/history/README.md) · [Gate B](GATE-B-INDEX.md).

Khi Core kích hoạt Workflow, đọc Core, vai trò, task và [chung](workflow-common.md). Đọc đủ **mọi** dòng khớp. Review Git + ACK cộng review, Git và biên nhận. Review cả nội dung đặc tả thì cộng dispatch.

| Thao tác hoặc đối tượng review | Nguồn thêm bắt buộc |
|---|---|
| Review, nghiệm thu, xác minh bằng chứng | [review](workflow-review.md) |
| Đặc tả, ownership, phân/giao việc | [dispatch](workflow-dispatch.md) |
| Chuẩn bị/gửi/nhận handoff hoặc kiểm ACK | [biên nhận](workflow-receipts.md) |
| Chuẩn bị/gửi/nhận/kiểm bàn giao, báo cáo, B6 | [handoff](workflow-handoff.md) |
| Git, diff hoặc review tính toàn vẹn | [Git review](workflow-git-review.md); Git thêm [Security](REPOSITORY_SECURITY.md), [CONTRIBUTING](../CONTRIBUTING.md) |
| Ghi Git/ghi dùng chung | Hàng Git, [review](workflow-review.md), [Git write](workflow-git-write.md) |
| Định tuyến/quyền ngoài KNG, ghi trạng thái tổng hợp | [routing](workflow-routing.md), [STATE](../STATE.md) |
| Định tuyến/release KNG | [KNG](workflow-kng.md), [STATE](../STATE.md), snapshot và release gate |
| Lưu/chuyển/tái sử dụng/dọn dữ liệu quản trị | [lifecycle](workflow-lifecycle.md), [protocol](DATA_LIFECYCLE_CONTEXT.md), [Git review](workflow-git-review.md) |
| Đổi quyền/duyệt chi phí, ngoại lệ Codex/Hermes, paid/render/publish, production/VPS, destructive/release/merge | [hạn chế](workflow-restricted-operations.md), [review](workflow-review.md), exact authority, preflight và rollback |

Routing/STOP/release cần STATE và nguồn live theo Core. Khi chưa rõ, đọc mọi module và nguồn an toàn có thể áp dụng. STOP phần phụ thuộc nếu nguồn thiếu hoặc mâu thuẫn.
