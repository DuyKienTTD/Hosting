# TTD Zalo Assistant · MVP-01 ngoại tuyến

Ứng dụng Windows x64 cho một tài khoản giả lập. Chỉ nhập tài liệu và tin nhắn mẫu. Khi mở lần đầu, STOP bật và chưa có quyền xử lý hội thoại. Gửi giả lập chỉ ghi biên nhận SQLite cục bộ.

## Thử luồng hội thoại mẫu

1. Mở **Tri thức** và nhập ba dòng dưới đây, hoặc chọn tệp TXT chứa ba dòng đó.
2. Mở **Hội thoại**, chọn khách theo mã hội thoại. Hai khách mẫu dùng cùng tên.
3. Trong **Quyền và hoạt động**, cấp riêng quyền lưu, soạn phản hồi và gửi giả lập. Bỏ dừng thử nghiệm.
4. Mở **Tin nhắn**, nhập `Cho tôi hỏi SKU MAU-01`, nhận tin giả rồi bấm **Soạn nháp từ tri thức**.
5. Kiểm tra nguồn, sửa nội dung nếu cần và bấm **Duyệt nội dung**, sau đó **Gửi giả lập**. Số biên nhận tăng một lần.
6. Quay lại **Tin nhắn**, chọn **Tạo ghi nhớ** trên tin đã lưu. **Hồ sơ khách** hiển thị ghi nhớ và ID nguồn của đúng khách.
7. Bấm **Dừng gửi**, đóng/mở ứng dụng. Xác nhận trạng thái dừng và biên nhận còn nguyên. Lượt chưa rõ kết quả được giữ ở **Quyền và hoạt động** để đối soát.

```text
SKU: MAU-01
Tên: Mẫu lan can A
Thông tin: Thép mạ kẽm, số liệu minh họa.
```

Câu hỏi về giá thiếu dữ liệu sẽ yêu cầu làm rõ. Soạn nháp dùng bộ sinh phản hồi tất định cục bộ. Tri thức nhập vào chỉ được đọc như dữ liệu văn bản. Ứng dụng tắt nhóm, phát lại tự động và gửi tệp.

## Build và đóng gói

Node 24, npm 11, Electron 40.0.0. Trong giai đoạn chuẩn bị, dùng `npm ci --ignore-scripts`, tải Electron và SHASUMS256.txt từ [release v40.0.0](https://github.com/electron/electron/releases/tag/v40.0.0), xác minh checksum. Chặn egress trước khi chạy mã phụ thuộc, build, test và ứng dụng. Gói giữ các license/notices Electron và thông báo React trong bundle.

```sh
npm run typecheck
npm run build
npm test
bash scripts/package-windows.sh /absolute/path/to/electron-v40.0.0-win32-x64.zip
```

## Nghiệm thu runtime độc lập

Dùng Windows x64 với egress chặn, trạng thái người dùng mới và Chromium sandbox bật. So khớp SHA-256 ZIP theo báo cáo, giải nén rồi mở `TTD-Zalo-Assistant.exe`. Thực hiện luồng trên, thử khách cùng tên khác mã, từ chối khi chưa cấp quyền, thu hồi quyền và thử dừng trước lượt gửi. Đối chiếu SQLite và ảnh giao diện sau restart. Trên runner có Electron đã giải nén, chạy `electron . --m0-smoke` từ thư mục app đã build để kiểm tra sáu màn hình, từ chối IPC sai, STOP và luồng IPC giả. Tùy chọn `TTD_SMOKE_PNG` lưu ảnh. Smoke chỉ có trong bản source chạy thử.

SQLite nâng schema M0 tại chỗ. Dữ liệu inbound chỉ lưu khi có quyền retain. Tin chỉ được phép respond có dấu dedup nhưng nội dung chỉ ở RAM. Thu hồi quyền ẩn dữ liệu đã lưu khỏi giao diện và vô hiệu phiên soạn tương ứng. Dữ liệu được phép lưu trước đó vẫn còn trong DB. Approval gắn nội dung/đích/policy và chỉ dùng một lần. Reservation duy nhất theo ID hội thoại + sự kiện được commit trước khi cho phép ghi biên nhận giả lập. Các trạng thái reserve/close có thể đối soát nhưng không gửi lại.

## Bản mở rộng sản phẩm ngoại tuyến

- **Tri thức:** trên màn hình Tri thức, nhập tệp TXT/MD mẫu để tra cứu nội dung bằng FTS5. Tài liệu nhập theo tệp chỉ là văn bản tham khảo. Công cụ soạn nháp dùng bản ghi catalogue có thẩm quyền và tách riêng sản phẩm, giá, chính sách. Nhập một bản ghi mỗi lần, với ID nguồn duy nhất cho mỗi phiên bản. `effective` là ngày bắt đầu, `until` là ngày kết thúc không bao gồm. Khi hai giá cùng hiệu lực khác nhau, nháp hỏi lại và liệt kê các nguồn xung đột.
- **Hồ sơ khách:** chọn hội thoại rồi mở Hồ sơ khách. Mỗi thẻ, giai đoạn, nhu cầu và việc theo dõi phải gắn với một tin nhắn đã lưu của chính khách đang chọn. Xuất JSON qua hộp thoại lưu. Xóa hồ sơ thu hồi quyền và xóa nội dung đã lưu. SQLite giữ định danh tối thiểu để chặn phát lại và giữ lịch sử lượt gửi giả lập đã kiểm toán.
- **Nháp:** FakeProvider chạy cục bộ trong main process. Giao diện hiển thị ID nguồn và trạng thái căn cứ. Người vận hành lưu đề xuất theo dõi theo từng khách. Chỉnh câu nháp hủy lượt duyệt đã cấp. Ứng dụng chỉ dùng kênh giả lập.

Ví dụ bản ghi giá mẫu nhập ở mục catalogue:

```json
{"id":"price-mau-01-v1","sku":"MAU-01","kind":"price","title":"Bảng giá mẫu","summary":"Bản giá thử nghiệm","version":"1.0","effective":"2026-11-26","until":null,"origin":"Bảng thử nghiệm nội bộ","amount":123456,"unit":"chiếc"}
```

Chạy `npm run build && npm test` cho regression suite. Chạy `node scripts/evaluate-corpus.mjs` sau khi build để đối chiếu hành vi, nguồn, hiệu ứng và các dữ kiện chính với corpus tổng hợp đã pin. Lệnh đánh giá cần Git object của commit `3dfc6fa1a0140267ac8d5604a5169299bd62b68d` trong checkout.
