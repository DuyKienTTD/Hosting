---
id: z4-s4-ui-delivery
type: report
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# Z4-S4-UI

- Baseline `a56ec820148ab0bdc4a3577808f25a4a9d3077b6`, base PR `dev/z4-s1-data`.
- Phạm vi ghi gồm `apps/ttd-zalo-web/` và workflow riêng `.github/workflows/z4-web.yml`.
- Đã dựng tám màn hình từ brief, với tài khoản và dữ liệu giả lập MSW. Bản phác riêng chưa có trong nguồn truy cập được để đối chiếu từng chi tiết.
- Build TypeScript/Vite, kiểm tra OpenAPI và 8 test component/tính giá đạt tại máy. 22 kiểm thử Playwright đạt trên desktop và mobile với Chromium 148. Kết quả CI độc lập hiển thị trên PR.
- Quyền trong bản demo chỉ áp dụng cho màn hình vận hành. API server cần tích hợp xác thực và phiên, giới hạn dữ liệu theo quyền, dữ liệu nghiệp vụ Postgres, Guard sát lúc gửi, STOP bền, consent có chứng cứ và dịch vụ xử lý yêu cầu xóa. Đối chiếu qua [OpenAPI](docs/api-contract.yaml).
- Chưa có lần gửi Zalo thật, triển khai VPS hoặc thay đổi quyền agent. Bàn giao Điều phối và A0 để đối chiếu giao diện, nghiệm thu và nối API sau.

## Z4-S4-FIX1 · 2026-11-26

- Sửa hai điểm nghiệm thu tại `ddccb10`. Báo giá theo bảng giá đã duyệt có thể lưu hoặc duyệt và xếp hàng OA sau khi đủ dữ liệu và xác nhận. API giả lập kiểm tra lại vai trò, phiên bản giá và điều kiện gửi.
- Chặn truy cập trực tiếp Agent & AI Router và Cài đặt cho CSKH/Bán hàng. Tách API bảo vệ bằng 403 khỏi dữ liệu workspace và áp dụng quyền chỉ xem cho A0. Xem [ma trận quyền](docs/operator-permissions.md) và [OpenAPI](docs/api-contract.yaml).
- Thêm Playwright cho từng vai trò trên tất cả các màn hình, các điều kiện khóa của cả hai nút báo giá, 403 và xếp hàng OA giả lập. CI trên PR #79 là bằng chứng kiểm tra theo commit.

## Z4-S4-FIX2 · 2026-11-26

- Kiểm tra thời điểm tương tác OA bằng dữ liệu và đồng hồ của handler. Cửa sổ dưới 48 giờ miễn quota. Từ 48 giờ đến dưới 7 ngày tính vào quota tháng. Từ đúng 7 ngày bị chặn.
- UI đọc lý do từ workspace và cập nhật khi POST trả 409. MSW giữ chỗ quota lúc xếp hàng. Interface `OaQuoteGuard` là điểm nối với Guard của PR #78, nơi backend thực thi quota bền và kiểm tra lại sát lúc gửi.
- Hồi quy qua HTTP giả lập cho owner và sales, các mốc giờ/ngày, hết quota, opt-out và vai trò. Component test kiểm tra hai thông báo khóa và giữ quyền lưu báo giá.

## Z4-S4-REBASE · 2026-11-26

- Rebase lên `e56ebcc` sau #75, #77 và #78. Không có xung đột hoặc migration mới.
- Handler production `oaQuotes` gọi `SendGuard.dispatch` trên PostgreSQL. Workspace dùng projection `block(target)` từ adapter OA. Admission trong Guard ghi quota đúng một lần vào `send_log`. API production trả `delivery=sent` khi OA xác nhận tiếp nhận. MSW vẫn chạy demo độc lập.
- Host cần mount `handle`, cấp resolver phiên nhận diện owner/sales và nối lookup báo giá từ catalog đã duyệt, consent và OA identity. Route factory từ chối database ngoài PostgreSQL. Bộ test mount route HTTP trong fixture và dùng OA transport giả lập với Guard, quota và send_log thật.

## Z4-S4-FIX3 · 2026-11-26

- Mounted every operator API endpoint in the runtime entrypoint. Login uses revocable PostgreSQL sessions and server-assigned roles. Migration 009 adds operator authentication, approved catalogue prices, quote history and the supporting web records.
- OA quote submission resolves customer identity and price from PostgreSQL before dispatch. Guard remains the sole source of quota reservation. The production bundle was tested in Chromium through the actual runtime process and PostgreSQL, with a local OA transport fixture.
