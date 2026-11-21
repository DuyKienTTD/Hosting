---
id: current-vps-inventory
type: inventory
status: current
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
source: live-hostinger-hpanel-and-root-terminal
---

# Kiểm kê VPS hiện tại

Ngày kiểm kê: **2026-11-21**

Nguồn: kiểm tra trực tiếp trong Hostinger hPanel và terminal root.

Phạm vi: hệ điều hành, tài nguyên, mạng, bảo mật, Docker, web, cơ sở dữ liệu và sao lưu.

> Repository là công khai nên IP, hostname và mọi bí mật xác thực đã được che. Không có giá trị `.env`, mật khẩu, token hoặc khóa riêng nào được đưa vào báo cáo.

## 1. Tổng quan máy chủ

| Hạng mục | Giá trị |
|---|---|
| Nhà cung cấp / gói | Hostinger KVM 2 |
| Vị trí | Kuala Lumpur, Malaysia |
| Trạng thái | Đang chạy |
| Hệ điều hành | Ubuntu 24.04.4 LTS |
| Kernel | Linux 6.8.0-147-generic |
| Kiến trúc / ảo hóa | x86_64 / KVM (QEMU) |
| CPU | 2 vCPU, AMD EPYC 9354P |
| RAM | 7.8 GiB khả dụng; khoảng 2.0 GiB đang dùng tại thời điểm kiểm tra |
| Swap | Không có |
| Đĩa gói | 100 GB |
| Phân vùng `/` | ext4, 96 GiB khả dụng, 12 GiB đã dùng, 85 GiB trống (13%) |
| Băng thông gói | 8 TB/tháng; hPanel ghi nhận 2.4 GB trong tháng |
| Uptime | Khoảng 34 ngày 16 giờ |
| Múi giờ hệ điều hành | UTC |
| IP / hostname | `[REDACTED_PUBLIC_IP]` / `[REDACTED_HOSTNAME]` |
| Trạng thái cập nhật | 90 gói có thể nâng cấp; hệ thống yêu cầu khởi động lại |

Phân vùng boot:

- `/boot`: 881 MiB, sử dụng 15%.
- `/boot/efi`: 105 MiB, sử dụng 6%.

## 2. Mạng và cổng dịch vụ

Các cổng TCP đang lắng nghe công khai:

| Cổng | Dịch vụ | Ghi chú |
|---:|---|---|
| 22 | OpenSSH | IPv4 và IPv6 |
| 3389 | XRDP | Remote Desktop |
| 32768 | Docker proxy | Hermes Agent, chuyển tiếp đến cổng container 4860 |
| 32770 | Docker proxy | n8n, chuyển tiếp đến cổng container 5678 |

Các dịch vụ chỉ lắng nghe cục bộ:

- PostgreSQL: `127.0.0.1:5432` và `[::1]:5432`.
- CUPS: loopback cổng 631.
- systemd-resolved: loopback cổng 53.
- XRDP session manager: loopback cổng 3350.

Mạng Docker:

- `docker0`: `172.17.0.0/16`, hiện không hoạt động.
- `hermes-agent-l7fe_default`: bridge `172.18.0.0/16`.
- `n8n-nbqy_default`: bridge `172.19.0.0/16`.
- `ttd-ai-p0-sandbox`: internal bridge cho P0; không publish port và không có Internet egress. Hai production container, n8n sandbox và GATE A bridge cùng attach để service discovery private; reasoner cũ đang stopped và production bridge cũ vẫn giữ nguyên.
- GATE A bổ sung ba network `internal=true` cho control, provider mock và upstream. Hermes auxiliary chỉ đi qua private guard; không có direct provider egress hoặc public port.

UFW đang bật với chính sách mặc định:

- Incoming: deny.
- Outgoing: allow.
- Routed: deny.
- Logging: low.
- Cho phép cả IPv4 và IPv6 trên: `22/tcp`, `80/tcp`, `443/tcp`, `3389/tcp`, `8501/tcp`.

Ghi chú:

- Không có tiến trình lắng nghe trên 80, 443 hoặc 8501 tại thời điểm kiểm tra.
- Quy tắc 8501 là dấu vết cũ sau khi xóa `CHUNG_KHOAN_PRO`.
- Hostinger hPanel chưa cấu hình tường lửa cấp nhà cung cấp: **0 quy tắc**.
- Docker đang publish trực tiếp 32768 và 32770 trên mọi giao diện.

## 3. Docker

| Hạng mục | Giá trị |
|---|---|
| Docker Engine | 29.9.2 |
| Storage driver | overlayfs |
| Cgroup driver | systemd |
| Containers | 7 đang chạy tại điểm kiểm tra cuối: 2 production, n8n sandbox và 4 GATE A; reasoner mock cũ được giữ ở trạng thái stopped để rollback |
| Images | 2 |
| Dung lượng image | 6.9 GB |
| Dung lượng container writable layer | khoảng 50 MB |
| Build cache | 0 B |

### n8n

| Thuộc tính | Giá trị |
|---|---|
| Compose project | `n8n-nbqy` |
| Compose file | `/docker/n8n-nbqy/docker-compose.yml` |
| Container | `n8n-nbqy-n8n-1` |
| Image | `docker.n8n.io/n8nio/n8n:latest` |
| Version / image digest | `2.45.7` / `sha256:9a8d...7b5d` |
| Trạng thái | Up khoảng 3 tuần |
| Restart policy | `unless-stopped` |
| User trong container | `node` |
| Root filesystem | Có quyền ghi |
| Docker healthcheck / resource limits | Chưa cấu hình / chưa cấu hình |
| Public mapping | `32770 -> 5678/tcp` |
| Volume | `n8n-nbqy_n8n_data` -> `/home/node/.n8n` (read/write) |
| Dữ liệu volume | khoảng 6.6 MiB |
| Sử dụng lúc kiểm tra | khoảng 0.45% CPU, 374.7 MiB RAM, 21 PID |
| Restart/OOM | 0 / false |
| App state | health/readiness 200; 0 workflow; 1 credential; 0 execution; MCP disabled |

Ghi chú: các số liệu trên là **n8n production**. P0 Level 1 có thêm `ttd-p0-n8n-sandbox`, data directory và encryption key riêng, đúng một workflow `fake-ads-audit-v1`, không public port; limit 0.5 CPU, 768 MiB RAM và 128 PID. Health cuối `healthy`.

Tên biến môi trường được phát hiện, không lưu giá trị: `GENERIC_TIMEZONE`, `N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS`, `N8N_RELEASE_TYPE`, `N8N_RUNNERS_ENABLED`, `N8N_SECURE_COOKIE`, `NODE_ENV`, `TZ`, `WEBHOOK_URL` và các biến runtime chuẩn.

### Hermes Agent

| Thuộc tính | Giá trị |
|---|---|
| Compose project | `hermes-agent-l7fe` |
| Compose file | `/docker/hermes-agent-l7fe/docker-compose.yml` |
| Container | `hermes-agent-l7fe-hermes-agent-1` |
| Image | `ghcr.io/hostinger/hvps-hermes-agent:latest` |
| Version / image digest | `0.22.5`, upstream `bf0203a7` / `sha256:0ea6...344f` |
| Trạng thái | Up khoảng 3 tuần |
| Restart policy | `unless-stopped` |
| User trong container | `root` |
| Root filesystem | Có quyền ghi |
| Docker healthcheck / resource limits | Chưa cấu hình / chưa cấu hình |
| Public mapping | `32768 -> 4860/tcp` |
| Bind mount | `/docker/hermes-agent-l7fe/data` -> `/opt/data` (read/write) |
| Dữ liệu project | khoảng 14 MiB ngoài image |
| Sử dụng lúc kiểm tra | khoảng 0.57% CPU, 435.9 MiB RAM, 39 PID |
| Restart/OOM | 0 / false |
| App state | dashboard health 200; 0 cron job/session; webhook disabled; chưa expose agent `/v1/*` API |

P0 Level 1 không thay Hermes production. GATE A thay reasoner mock cũ trong sandbox bằng Hermes auxiliary thật, private inference guard, authenticated bridge và provider mock; bốn service đều healthy, restart count 0, không public port. Reasoner cũ vẫn tồn tại ở trạng thái stopped cho rollback. Hermes auxiliary không có provider credential hay direct egress; provider cuối vẫn là mock.

Tên biến môi trường nhạy cảm tồn tại nhưng giá trị không được ghi lại: `ADMIN_PASSWORD`, `ADMIN_USERNAME`, `DASHBOARD_AUTH_SECRET`, `OXYLABS_AI_STUDIO_API_KEY`; ngoài ra có các biến runtime và cấu hình Hermes.

Các file cấu hình ứng dụng tồn tại trên VPS:

```text
/docker/hermes-agent-l7fe/.env
/docker/hermes-agent-l7fe/docker-compose.yml
/docker/n8n-nbqy/.env
/docker/n8n-nbqy/docker-compose.yml
```

Các file `.env` không được sao chép vào repository.

### Trạng thái tích hợp n8n ↔ Hermes

Kiểm thử live ngày 2026-11-21 xác nhận:

- Hai container ở hai Docker bridge riêng và không resolve được tên nhau.
- Network transport hai chiều hoạt động qua các cổng publish trên host.
- n8n → API bảo vệ của Hermes dashboard: 401 trước auth, 200 sau auth.
- Hermes → n8n readiness: 200.
- n8n instance-level MCP: tắt, endpoint trả `MCP access is disabled`.
- Hermes image hiện chạy dashboard quản trị; agent inference API `/v1/*` của upstream chưa expose.
- Vì n8n không có workflow/execution và hai tính năng trên chưa bật, luồng AI end-to-end vẫn `BLOCKED`.

Chi tiết và latency nằm trong [báo cáo kiểm toán tích hợp](../reports/2026-11-21-n8n-hermes-integration-audit.md).

### P0 Level 1 sandbox — cập nhật 2026-11-21

- Đã triển khai `ttd-p0-n8n-sandbox` và `ttd-p0-reasoner` trên internal bridge; không public port, firewall hoặc DNS change.
- Hai secret persistent riêng của sandbox được sinh bằng CSPRNG và lưu root-only; không thay encryption key/credential/volume production.
- Đúng một authenticated webhook workflow; structural E2E 9/9 và rollback/restore PASS.
- Production n8n/Hermes health PASS, restart count 0, downtime 0 trong toàn bộ change/rehearsal.
- Mốc Level 1 kết thúc với paid call 0. Sau đó Provider E2E Mức 2 chạy đúng 1 paid call trong cap; GATE A mock không tạo thêm paid call và kill switch vẫn ON.

Chi tiết hiện hành và bằng chứng đã khử bí mật: [P0 Level 1 report](../reports/2026-11-21-n8n-hermes-p0-sandbox-integration.md).

### Hermes GATE A mock sandbox — cập nhật 2026-11-21

- Đã triển khai Hermes auxiliary, private guard, authenticated bridge và provider mock trên các network nội bộ; không đổi production, DNS, firewall hoặc public port.
- Exact `gpt-6-luna`, hard cap 600, full serialized request lớn nhất 3.315 ASCII bytes, tools disabled, one-turn và direct/provider-egress bypass đều được kiểm chứng.
- Mock E2E n8n → Hermes → guard → mock → authenticated callback, negative/fault/idempotency/concurrency và corrected rollback/restore đều PASS.
- Production health HTTP 200 trước/sau, restart count 0, downtime 0. Kill switch vẫn ON, ledger thật không đổi, paid calls mới 0 và chi phí API mới USD 0.
- GATE B chưa được phê duyệt hoặc thực hiện. Chi tiết: [GATE A report](../reports/2026-11-21-hermes-gate-a-mock-results.md).

## 4. Web, TLS và cơ sở dữ liệu

### Nginx / TLS

- Nginx 1.24.0 đang chạy; kiểm tra cú pháp thành công.
- Không có site trong `/etc/nginx/sites-enabled`.
- Không có reverse proxy, `server_name` hoặc listener 80/443 được nạp.
- Certbot hiện không quản lý chứng chỉ nào.
- Nginx đang chạy nhưng chưa phục vụ website.

### PostgreSQL

- PostgreSQL 16.15 đang chạy.
- Chỉ lắng nghe trên loopback.
- Database người dùng còn lại: `postgres`, khoảng 7.5 MiB.
- Không còn database `stock_ai`.
- MySQL, MariaDB và Redis không hoạt động.

## 5. Dịch vụ hệ thống và người dùng

Dịch vụ quan trọng đang chạy:

- `docker`, `containerd`.
- `nginx`.
- `postgresql@16-main`.
- `ssh`, `fail2ban`, `ufw`.
- `cron`, `rsyslog`, `unattended-upgrades`.
- `xrdp`, `xrdp-sesman`.
- Các dịch vụ desktop/phụ trợ: CUPS, Avahi, NetworkManager, ModemManager, colord, fwupd, udisks2, upower và wpa_supplicant.

Không có systemd service bị lỗi tại thời điểm kiểm tra.

Tài khoản tương tác:

- `root`.
- `desktopuser`, thành viên nhóm `sudo`.

## 6. Bảo mật hiện tại

- UFW: bật.
- Fail2ban: bật, có jail `sshd`.
- AppArmor: đã nạp 121 profile, 28 profile ở chế độ enforce.
- Trình quét mã độc Monarx của Hostinger: **chưa cài đặt**.
- Hostinger firewall: **chưa cấu hình**.

Cấu hình SSH hiệu lực:

```text
port 22
permitrootlogin yes
passwordauthentication yes
pubkeyauthentication yes
maxauthtries 6
x11forwarding yes
clientaliveinterval 0
clientalivecountmax 3
```

## 7. Cập nhật và lịch chạy tự động

- 1.522 gói Debian/Ubuntu đã cài.
- 90 gói có thể nâng cấp.
- `unattended-upgrades` được bật.
- VPS đang yêu cầu khởi động lại để hoàn tất cập nhật.
- Root crontab không có job tùy chỉnh.
- `/etc/cron.d` có Certbot, dọn Docker builder/image, e2scrub và sysstat.
- Cron hằng ngày có apt/dpkg, logrotate, man-db, apport và sysstat.

## 8. Sao lưu

Hostinger đang cung cấp sao lưu tự động **hàng tuần** và lưu tách khỏi máy chủ chính.

| Thời điểm tạo | Vị trí lưu | Kích thước | Ước tính khôi phục |
|---|---|---:|---:|
| 2026-11-16 16:21 | Ấn Độ | 12.37 GB | 30 phút |
| 2026-11-09 20:13 | Ấn Độ | 12.34 GB | 30 phút |

Lưu ý quan trọng: hai bản sao lưu này được tạo trước ngày xóa `CHUNG_KHOAN_PRO` và Alibaba OneTalk, nên có thể vẫn chứa trạng thái cũ của hai ứng dụng. Đây là bản sao lưu do Hostinger quản lý, không nằm trong filesystem đang chạy.

Dung lượng dữ liệu hệ thống khác:

- `/var/backups`: khoảng 3.8 MiB.
- `/var/log`: khoảng 177 MiB.
- `/var/lib/postgresql`: khoảng 55 MiB.

## 9. Xác nhận trạng thái sau dọn dẹp

Đã kiểm tra và xác nhận trên VPS đang chạy:

- Không còn `/opt/CHUNG_KHOAN_PRO`.
- Không còn `/opt/alibaba-onetalk-callback`.
- Không còn systemd service hoặc user `alibaba-callback`.
- Không còn database `stock_ai`.
- Không còn cron backup `stock_ai`.
- Không còn Nginx site hoặc Certbot certificate của `ttdnew.tech`, `admin.ttdnew.tech`, `oauth.ttdnew.tech`.
- Không còn listener trên 8501, 8502 hoặc 8510.
- n8n và Hermes Agent vẫn hoạt động.

## 10. Kết luận

VPS hiện có hai workload production n8n/Hermes, n8n sandbox và bốn service GATE A mock được giới hạn tài nguyên; reasoner mock cũ dừng để làm đường rollback. Máy còn dung lượng đĩa và RAM, nhưng cần ưu tiên siết SSH/XRDP, giới hạn cổng Docker, bổ sung firewall cấp Hostinger, cập nhật 90 gói và khởi động lại có kế hoạch. Chi tiết ưu tiên nằm trong báo cáo bảo mật đi kèm.
