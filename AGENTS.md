# Hướng dẫn cho tác nhân

Các hướng dẫn này áp dụng cho toàn bộ repository.

## Mục tiêu

Giữ repository thành nguồn thông tin chung, ngắn gọn và đáng tin cậy để tác nhân mới có thể bắt đầu làm việc mà không phải đọc toàn bộ lịch sử chat.

## Thứ tự đọc bắt buộc

1. `README.md` — phạm vi và bản đồ repository.
2. `STATE.md` — trạng thái hiện tại, rủi ro và việc đang chờ.
3. `CATALOG.yaml` — tài liệu có thẩm quyền và vị trí cần đọc.
4. Tài liệu liên quan trực tiếp đến nhiệm vụ.
5. `rules/REPOSITORY_SECURITY.md` trước mọi commit hoặc push.

Không đọc toàn bộ `reports/` hoặc `archive/` nếu `CATALOG.yaml` không chỉ tới đó.

## Quy tắc nguồn sự thật

- Hệ thống trực tiếp là nguồn sự thật cho trạng thái thay đổi theo thời gian.
- `inventory/` là bản ghi hiện tại gần nhất, không thay thế việc xác minh live trước thao tác rủi ro.
- `STATE.md` là bản tóm tắt nhanh, không chứa toàn bộ chi tiết.
- Báo cáo có ngày trong `reports/` là bằng chứng lịch sử; tạo báo cáo mới thay vì sửa lại quá khứ, trừ khi sửa lỗi thực tế.
- `knowledge/` chứa kiến thức bền vững; không đặt số liệu vận hành dễ lỗi thời ở đây.
- Nếu hai tài liệu mâu thuẫn, ưu tiên tài liệu có `status: current` và `verified_at` mới hơn, sau đó xác minh live.

## Tìm thông tin nhanh

- Dùng `rg` hoặc `rg --files` trước khi duyệt thủ công.
- Tìm ID tài liệu trong `CATALOG.yaml`.
- Tìm trạng thái hiện tại trong `STATE.md` và `inventory/`.
- Tìm lịch sử thay đổi trong `CHANGELOG.md` và `reports/`.
- Tìm quy trình thao tác trong `runbooks/`.

## Khi thêm hoặc thay đổi thông tin

1. Phân loại tài liệu đúng thư mục.
2. Dùng tên file chữ thường, dấu gạch ngang; báo cáo có ngày theo `YYYY-MM-DD-chu-de.md`.
3. Thêm metadata theo mẫu tương ứng trong `templates/`; file chỉ mục và entrypoint được miễn metadata.
4. Cập nhật `CATALOG.yaml` nếu tài liệu là mới, đổi trạng thái hoặc thay thế tài liệu khác.
5. Cập nhật `STATE.md` nếu trạng thái vận hành, rủi ro hoặc việc đang chờ thay đổi.
6. Cập nhật `CHANGELOG.md` cho mọi thay đổi có ý nghĩa.
7. Kiểm tra bí mật, liên kết và `git diff --cached` trước khi push.

## An toàn

- Repository là công khai. Không commit bí mật hoặc định danh máy chủ thật.
- Không sao chép `.env`, log thô, database dump, backup hoặc output chứa token.
- Chỉ ghi tên biến môi trường; không ghi giá trị.
- Không mô tả một thay đổi là đã hoàn tất nếu chưa có bằng chứng xác minh.
- Không dùng tài liệu cũ làm quyền cho một hành động phá hủy; quyền phải đến từ yêu cầu hiện tại của người dùng.

## Tiêu chuẩn hoàn thành

Một nhiệm vụ cập nhật tri thức chỉ hoàn tất khi tài liệu đúng thư mục, metadata và catalog nhất quán, không có bí mật, changelog đã cập nhật, working tree sạch và commit đã có trên remote được yêu cầu.
