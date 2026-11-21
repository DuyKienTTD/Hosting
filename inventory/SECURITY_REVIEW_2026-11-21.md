# Đánh giá bảo mật VPS — 2026-11-21

Đây là báo cáo quan sát, chưa tự động thay đổi cấu hình máy chủ.

## Ưu tiên cao

1. **SSH cho phép root và mật khẩu**

   Hiện tại `permitrootlogin yes` và `passwordauthentication yes`. Nên tạo tài khoản quản trị riêng, xác nhận đăng nhập bằng SSH key hoạt động, sau đó tắt đăng nhập root và mật khẩu.

2. **XRDP công khai trên cổng 3389**

   Chỉ nên mở qua VPN hoặc allowlist IP quản trị. Nếu không dùng giao diện desktop, nên tắt XRDP và các dịch vụ desktop phụ trợ.

3. **Docker publish trực tiếp ra Internet**

   Cổng 32768 (Hermes) và 32770 (n8n) đang bind `0.0.0.0` và IPv6. Nên đặt sau reverse proxy HTTPS, xác thực, rate limit và firewall; không nên để truy cập trực tiếp.

4. **Không có Hostinger firewall**

   hPanel báo 0 quy tắc. UFW trong VPS đang bật nhưng nên bổ sung lớp lọc ở nhà cung cấp.

5. **90 gói cần nâng cấp và máy cần reboot**

   Lập lịch bảo trì, kiểm tra snapshot mới, cập nhật, khởi động lại, rồi xác nhận Docker/PostgreSQL/Nginx.

## Ưu tiên trung bình

- Xóa quy tắc UFW cũ cho cổng 8501 sau khi xác nhận không còn dùng.
- Xem xét đóng 80/443 nếu Nginx tiếp tục không phục vụ site, hoặc triển khai reverse proxy/TLS đúng mục đích.
- Hermes chạy trong container bằng `root` với root filesystem và bind mount có quyền ghi; nên giảm quyền nếu image hỗ trợ.
- n8n và Hermes dùng tag `latest`; nên ghim version/digest để kiểm soát nâng cấp.
- Không có swap; cân nhắc swapfile nhỏ hoặc cơ chế giới hạn RAM/OOM cho workload.
- Monarx chưa cài. Có thể dùng nếu phù hợp chi phí, nhưng không thay thế cập nhật, phân quyền và giám sát.
- Rà soát Avahi, CUPS, ModemManager và các dịch vụ desktop không cần thiết trên máy chủ Internet.
- Thiết lập giám sát dung lượng, CPU/RAM, trạng thái container, hạn chứng chỉ và đăng nhập bất thường.

## Sao lưu và dữ liệu đã xóa

Hai bản sao lưu Hostinger ngày 2026-11-09 và 2026-11-16 có thể chứa `CHUNG_KHOAN_PRO` và Alibaba OneTalk. Nếu yêu cầu “không thể phục hồi” áp dụng cả bản sao lưu do nhà cung cấp quản lý, cần xử lý riêng trong Hostinger sau khi cân nhắc mất khả năng phục hồi toàn bộ VPS.

## Trình tự cải thiện đề xuất

1. Tạo/kiểm tra SSH key cho tài khoản quản trị không phải root.
2. Siết SSH và giới hạn XRDP theo IP/VPN.
3. Tạo Hostinger firewall với allowlist tối thiểu.
4. Đặt n8n/Hermes sau HTTPS reverse proxy; đóng cổng publish trực tiếp.
5. Tạo backup/snapshot mới, cập nhật gói và reboot có kế hoạch.
6. Ghim phiên bản image, đặt giới hạn CPU/RAM và healthcheck cho container.
7. Dọn rule/dịch vụ dư thừa và thiết lập giám sát định kỳ.
