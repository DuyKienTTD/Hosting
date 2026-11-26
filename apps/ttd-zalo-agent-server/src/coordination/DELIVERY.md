# Z4-S5-ROOM · Delivery log

Base PR #75, commit `a56ec820148ab0bdc4a3577808f25a4a9d3077b6`. [DIRECTION-04](https://github.com/DuyKienTTD/Hosting/blob/main/decisions/ZALO-PRODUCT-DIRECTION-04.md).

Chức năng phòng điều phối nằm trong thư mục này. Test tương ứng ở [coordination.test.mjs](../../test/coordination.test.mjs). CI Postgres sẵn có chọn test này qua lệnh `npm test`.

| API | Hành vi |
|---|---|
| `GET /coordination` | Snapshot tin và phiếu |
| `GET /coordination/events` | SSE gửi snapshot khi kết nối và khi revision thay đổi |
| `POST /coordination/messages` | `{text, dueAt?, links?}`. Tạo phiếu cho tối đa 3 agent có tên hợp lệ. |
| `POST /coordination/tickets/:id/run` | `{}`. Phiên có quyền chạy nhận phiếu mới và thực hiện pipeline. |
| `PATCH /coordination/tickets/:id` | `{version}`. Duyệt phiếu đang chờ với phiên bản đang thấy. |
| `POST /coordination/tickets/:id/recover` | `{version}`. Chuyển phiếu quá hạn hoặc mất worker sang chờ duyệt với trạng thái lỗi. |
| `POST /coordination/tickets/:id/rename` | `{index, expectedName}`. Duyệt riêng đề xuất đổi tên sau khi phiếu đã xong. |

Phiếu chuyển `new → working → review → done`. Một lượt Claude có tối đa 3 phiếu con, 5 lệnh gọi và một thời hạn chung. Mỗi lượt chỉ nhận một lần. Đầu ra tool kiểm tra JSON Schema và tập liên kết đã cấp. SQL đổi tên có đối chiếu giá trị đang thấy, ghi audit và giữ biên nhận chống lặp cùng transaction. Hai principal được kiểm tra quyền tại tầng dịch vụ. Đề xuất từ agent không gọi SQL hoặc transport.

Trước mỗi lần gọi, Postgres giữ toàn bộ ước tính chi phí trên sổ phòng dùng chung giữa các replica. Sổ áp cả trần ngày UTC+7 và tổng trần của key chuyên dùng, giữ nguyên phần đã tính khi kết quả chưa rõ hoặc lỗi. Khi model/usage vượt giới hạn, sổ khóa. Cấu hình giá và hạn mức của nhà cung cấp cần được xác nhận trước khi nối key thật.

## Kiểm thử

Node 24.22.3 chạy typecheck và build thành công. Suite runtime cục bộ dùng Chromium fixture có 65 đạt và 3 mục Postgres bỏ qua trong lượt đó. Chạy riêng suite phòng với PostgreSQL 17.12 và role `data_app` có 8/8 đạt, gồm cạnh tranh ghi và kiểm tra quyền. Bộ kiểm tra tính toàn vẹn repo đạt.

## Tích hợp ngoài phạm vi

- Host cần mount `coordinationHttp` vào router nội bộ và nối bộ xác thực phiên thu hồi được. `session(handle)` trả về principal do máy chủ xác minh. `allowed` đọc ACL và STOP hiện hành cho người gọi, hành động và agent đích. A0 dùng vai trò phòng do host xác thực, cùng principal dữ liệu vai trò `operator` đã có. Client gửi nội dung, liên kết và phiên bản, còn vai trò lấy từ phiên. Tin inbound không đi qua handler này.
- Áp dụng `install.sql` sau khi có schema nền và `data_app`. Tạo `PostgresRoomStore` và truyền `checkedRename(pool)`. Nối Router HTTPS với key dành riêng và các trần đã được duyệt. Không đưa dữ liệu khách vào prompt. Triển khai bảo trì/archive khi chạm trần 2.000 phiếu. Snapshot giữ 200 tin gần nhất.
- Kiểm thử bằng FakeProvider và HTTP mock, với Postgres fixture khi bật `RUN_POSTGRES_TESTS=1`. Kết quả thực tế của CI xem tại PR. Bản này chỉ bàn giao mô-đun và contract tích hợp; thay đổi entrypoint, schema bootstrap và cấu hình triển khai thuộc phạm vi tích hợp sau.
