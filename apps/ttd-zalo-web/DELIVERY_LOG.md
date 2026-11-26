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
