# Quy trình cập nhật tri thức

## Chọn loại tài liệu

| Nội dung | Nơi lưu | Cách cập nhật |
|---|---|---|
| Trạng thái/cấu hình đang dùng | `inventory/` | Cập nhật tại chỗ và đổi `verified_at` |
| Audit, báo cáo, checkpoint, sự cố | `reports/` | Tạo file mới có ngày |
| Kiến thức bền vững | `knowledge/` | Cập nhật khi hiểu biết thay đổi |
| Quy trình thao tác | `runbooks/` | Viết từng bước, có điều kiện và cách xác minh |
| Quyết định kiến trúc | `decisions/` | Tạo ADR mới; không viết lại quyết định cũ |
| Nguồn bên ngoài | `references/` | Ghi URL, ngày truy cập và ý nghĩa |
| Chính sách bắt buộc | `rules/` | Cập nhật thận trọng, nêu tác động |

## Metadata tối thiểu

Mỗi tài liệu nghiệp vụ mới phải có metadata. Ngoại lệ: file chỉ mục `README.md`, các entrypoint ở gốc, hướng dẫn đóng góp và file mẫu trong `templates/`.

```yaml
---
id: ten-on-dinh
type: inventory|report|knowledge|runbook|decision|reference|rule
status: draft|current|superseded|archived
updated_at: YYYY-MM-DD
verified_at: YYYY-MM-DD
sensitivity: public|public-redacted
---
```

`verified_at` là ngày kiểm tra với nguồn thật; bỏ trường này nếu tài liệu chỉ là bản nháp hoặc ý tưởng.

## Checklist trước khi push

1. Nội dung đúng thư mục và tên file.
2. `STATE.md`, `CATALOG.yaml`, `CHANGELOG.md` đã cập nhật nếu cần.
3. Không có bí mật, IP/hostname thật, dữ liệu người dùng hoặc file lớn.
4. Liên kết nội bộ đúng.
5. Script đã kiểm tra cú pháp và chỉ làm đúng phạm vi mô tả.
6. Chạy `powershell -NoProfile -File scripts/validate-repository.ps1`.
7. `git diff --cached --check` không báo lỗi.
8. `git status` sạch sau khi push.

## Kiểm soát cập nhật an toàn và tránh trùng công việc

Tuân thủ [AGENT_WORKFLOW mục 8](rules/AGENT_WORKFLOW.md). Trước khi lập task/sửa tài liệu: đọc đủ các file có thẩm quyền và kết quả có liên quan, kể cả phần cuối file; kiểm tra output không bị truncate. Trước khi chạy test, xác định evidence PASS có thể dùng lại và `change_trigger` nếu buộc phải rerun. Trong task ghi rõ `READ_SET`, `WRITE_SET`, `DO_NOT_TOUCH`, `INVARIANTS`, `TEST_DELTA`, owner và handoff.

Trước khi ghi: lấy SHA hiện tại, đọc đủ file, tạo patch tối thiểu và so sánh toàn bộ diff với bản gốc; kiểm metadata/approval/section bị xóa ngoài write-set, secret và links. Nếu stale hoặc có concurrent edits, refresh và hòa giải; không ghi đè. Sau push: fetch remote, xác minh nội dung/trường bất biến; nêu `NOT_VERIFIED` nếu chưa xác minh. Agent tư vấn không đổi owner/status/approval của task mẹ.

Các kiểm soát tự động (GitHub rulesets, branch protection, CI validators) là **đề xuất cần xác minh/triển khai riêng**, không coi đã vận hành chỉ vì tài liệu yêu cầu.
