# TTD Zalo Assistant · M0

Ứng dụng desktop thử nghiệm ngoại tuyến cho một tài khoản giả lập. Khi mở lần đầu, STOP bật và quyền theo từng hội thoại đều chưa được cấp. Chỉ nhập dữ liệu giả lập. Gửi thử ghi một biên nhận SQLite cục bộ.

## Build và kiểm thử

Node 24, npm 11, Electron 40.0.0. Tải dependency đã khóa bằng `npm ci --ignore-scripts` trong giai đoạn chuẩn bị. Tải Electron cùng SHASUMS256.txt từ [release v40.0.0](https://github.com/electron/electron/releases/tag/v40.0.0) và kiểm tra checksum trước khi giải nén. Tắt egress trước khi thực thi package, build và chạy test.

```sh
npm run typecheck
npm run build
npm test
bash scripts/package-windows.sh /absolute/path/to/electron-v40.0.0-win32-x64.zip
```

Electron và công cụ build được khóa trong package-lock. Lifecycle scripts Electron/esbuild bị tắt khi cài. esbuild dùng package native theo OS đã khóa. Gói Windows giữ license và notices từ Electron distribution, kèm thông báo React/React DOM trong bundle. Application không cần `node_modules` tại runtime.

## Kiểm chứng Windows trên máy độc lập

Dùng Windows x64 với egress đã chặn theo cấu hình máy kiểm thử và trạng thái người dùng mới. Giải nén ZIP, xác minh SHA-256 từ báo cáo, mở `TTD-Zalo-Assistant.exe`. Xác nhận giao diện tiếng Việt và trạng thái đang dừng. Bỏ dừng, chọn một khách mẫu theo mã hội thoại, cấp quyền gửi giả lập, nhập nội dung mẫu, bấm duyệt rồi gửi. Kiểm tra bộ đếm tăng đúng một lần. Dùng khách cùng tên khác mã để xác nhận cách ly. Bấm dừng, đóng/mở lại và xác minh trạng thái dừng cùng biên nhận. Kiểm tra độc lập IPC và sandbox trên cây nguồn tương ứng. Ghi Windows version, SHA ZIP, log, ảnh và kết quả.

Trên Linux có môi trường GUI offline hỗ trợ Chromium sandbox, chạy Electron đã giải nén với `electron . --m0-smoke` từ thư mục app sau build, dùng HOME/XDG tạm. Smoke kiểm tra giao diện, renderer isolation và đối số IPC sai. `TTD_SMOKE_PNG` là đường dẫn ảnh tùy chọn. Giữ Chromium sandbox bật.

## Phạm vi Foundation

SQLite migration và reopen. Hai khách trùng tên được phân biệt bằng ID, cả hai thuộc cùng một tài khoản giả lập. Ba quyền retain/respond/send độc lập, hết hạn và tiếp quản. Duyệt gắn nội dung, đích và phiên bản policy. Reservation bền vững precedes preparation. Fake initiation đồng bộ bên trong transaction có khóa ghi, kiểm tra lại STOP và quyền. Không tự gửi lại sau lỗi hay restart. Việc thay transport thực tế cần kiểm chứng lại ranh giới initiation.

Giao diện M0 quản lý quyền và gửi thủ công giả lập. Inbound, tra cứu KB, AI draft, nhóm, replay và media thuộc các phạm vi khác. Nội dung gõ thử và approval nằm trong bộ nhớ. SQLite lưu quyền và metadata lần gửi, không lưu nội dung.
