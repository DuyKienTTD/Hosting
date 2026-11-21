---
id: ttdnew-resource-identity-verification-2026-11-21
type: report
status: complete
updated_at: 2026-11-21
sensitivity: public-redacted
owner: hostinger-agent
---

# TTD-RESOURCE-IDENTITY-001, báo cáo xác minh resource `ttdnew.tech`

## Kết luận

`ttdnew.tech` là một resource **Docker Hosting / AI automation apps của Hostinger**, không phải website WordPress, không phải AI Builder Manual mode và không phải project Docker Compose trực tiếp trên VPS KVM 2.

Metadata sản phẩm đang hiển thị nhãn **OpenClaw**, nhưng runtime trả về **`u4s-hermes-agent`** ở cả tra cứu theo domain và inventory ứng dụng. Vì vậy, identity vận hành chính xác của resource `ttdnew.tech` trong lần kiểm tra này là **Hermes Agent trên AI automation apps**, còn nhãn OpenClaw là metadata sản phẩm/label không khớp runtime.

## 1. Bằng chứng về `ttdnew.tech`

- Website/resource state: `active`.
- Platform: U4S, tức Docker Hosting / AI automation apps.
- Plan display name: `OpenClaw`.
- Runtime: `u4s-hermes-agent`.
- Application UUID được trả về giống nhau giữa domain lookup và U4S application inventory.
- Domain chính: `ttdnew.tech`.
- Có preview domain Hostinger.
- Application không có `horizonsUuid`, nên không phải Agentic mode của AI Builder.
- Resource order và application inventory chỉ có một application, loại runtime Hermes.

## 2. Đối chiếu OpenClaw và Hermes

### OpenClaw metadata

`OpenClaw` xuất hiện ở trường tên sản phẩm/plan của resource AI automation. Trường này không đủ để xác định app runtime, vì các app AI automation dùng chung loại plan và cần đọc trường runtime.

### Hermes runtime

`u4s-hermes-agent` xuất hiện trực tiếp trong:

- Website details của `ttdnew.tech`.
- U4S orders with applications.
- U4S application upgrade status.

Runtime hiện có version `v0.22.5-2`; Hostinger báo target upgrade `v0.23.2-1`, nhưng lần khảo sát này không upgrade và không restart.

### Kết luận identity

- Metadata label: OpenClaw.
- Runtime identity: Hermes Agent.
- Identity được dùng cho hướng dẫn vận hành: Hermes Agent.
- Không được áp dụng hướng dẫn channel hoặc CLI OpenClaw cho resource này khi chưa có bằng chứng runtime thay đổi.

## 3. Đối chiếu với Hermes trên VPS KVM 2

VPS `1722328` có một Docker Compose project tên `hermes-agent-l7fe` với các dấu hiệu độc lập sau:

- Project state: running.
- Container state: running, đã chạy khoảng 3 tuần tại thời điểm kiểm tra.
- Container image: `ghcr.io/hostinger/hvps-hermes-agent:latest`.
- Container service exposes the Hermes application port internally.
- VPS state: running, Ubuntu 24.04 LTS, KVM 2, Docker Manager installed.

Đây là một **Hermes Agent riêng, tự quản lý trên VPS**, khác với resource U4S `ttdnew.tech`.

Không có bằng chứng cho thấy:

- Hai resource dùng chung container.
- Hai resource dùng chung volume.
- U4S app được chạy bên trong VPS KVM 2.
- VPS project là backend của U4S `ttdnew.tech`.
- Có đồng bộ dữ liệu, credential, channel hoặc conversation history giữa hai bên.

## 4. Kiểm tra an toàn đã thực hiện

- Đọc task identity và tài liệu trạng thái dự án.
- Tra cứu website details theo `ttdnew.tech`.
- Tra cứu toàn bộ U4S orders/applications.
- Tra cứu mapping custom domain đến application UUID.
- Đọc disk usage U4S: persistent storage khoảng 1.23 GiB trên quota 25 GiB; chưa gần ngưỡng disk.
- Đọc runtime upgrade status.
- Liệt kê Docker Compose projects trên VPS.
- Đọc trạng thái container Hermes trên VPS.
- Không restart, upgrade, deploy, stop, migrate, đổi domain, đổi DNS, đọc secret hoặc thay đổi production.

Một lệnh process probe trong container không chạy vì image không cung cấp executable shell command đó. Kết quả này không làm thay đổi identity kết luận, vì image, project name, service và runtime metadata đã đủ để xác minh ở cấp resource.

## 5. Trạng thái các mục tiêu của task

- Xác định resource `ttdnew.tech`: **PASS**.
- Xác định runtime thực tế của U4S: **PASS**, `u4s-hermes-agent`.
- Đối chiếu metadata OpenClaw: **PASS**, label không khớp runtime.
- Xác định Hermes trên VPS KVM 2: **PASS**, project `hermes-agent-l7fe` và image Hermes.
- Chứng minh U4S và VPS dùng chung backend/dữ liệu: **UNKNOWN**, không có bằng chứng và không thực hiện truy cập sâu.
- Thay đổi production: **NOT PERFORMED**.

## 6. Khuyến nghị task tiếp theo

1. Tạo task riêng để xác minh app identity trong hPanel trước khi upgrade hoặc thay đổi cấu hình U4S.
2. Tạo task riêng để kiểm tra read-only logs của U4S Hermes và VPS Hermes, không ghi credential vào Git.
3. Lập topology redacted cho hai Hermes instance, bao gồm domain, entrypoint, volume, channel và backup boundary.
4. Chỉ kết nối hoặc di chuyển dữ liệu giữa hai instance khi có một task migration riêng với backup, rollback và approval.
