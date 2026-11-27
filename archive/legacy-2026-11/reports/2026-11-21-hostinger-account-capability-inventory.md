---
id: hostinger-account-capability-inventory-2026-11-21
type: report
status: current
updated_at: 2026-11-21
sensitivity: public-redacted
---

# Inventory chức năng Hostinger của tài khoản

## Phạm vi và cách đọc

Báo cáo này được đối chiếu từ trạng thái tài khoản, VPS, website, email, AI Builder, Docker/AI automation và tài liệu vận hành Hostinger tại ngày 2026-11-21. Không có thay đổi nào được thực hiện trên production.

Các nhãn:

- `VERIFIED`: công cụ tài khoản trả về trực tiếp.
- `DOCUMENTED`: có trong tài liệu Hostinger hiện hành.
- `APPROVAL_REQUIRED`: có khả năng nhưng cần xác nhận trước khi thay đổi.
- `BLOCKED_OR_UNKNOWN`: chưa có kênh hoặc bằng chứng đủ để kết luận.

## 1. Các dịch vụ đang có

### Cloud Startup Hosting

`VERIFIED`: có 1 plan Cloud Startup Hosting, đang hoạt động, gắn với `giadongthau.com`, có addon Daily Backup.

Các website/resource trên plan này:

- `wroughtiron.shop`: WordPress, CDN đang bật.
- `qtcty.com`: WordPress, CDN đang bật.
- `thuanthanhdat.com`: WordPress.
- `nepdong.com`: WordPress.
- `thuanthanhdat.com.vn`: website loại khác, chưa xác định là WordPress qua inventory website.
- `nepdong.top`: Hostinger AI Builder Manual mode, đã publish và có online store.

Ngoài 4 website WordPress chính còn có staging WordPress `staging.wroughtiron.shop` trong danh sách cài đặt WordPress của tài khoản.

### KVM VPS

`VERIFIED`:

- VPS ID: `1722328`.
- Plan: KVM 2.
- Trạng thái: đang chạy.
- Hệ điều hành: Ubuntu 24.04 LTS.
- Tài nguyên: 2 vCPU, 8 GB RAM, 100 GB disk; mức sử dụng disk lúc kiểm tra khoảng 12 GB.
- Khu vực máy chủ: Kuala Lumpur.
- Docker Manager đã cài đặt.
- Kết nối SSH cổng 22 đã được kiểm tra thành công.
- Có 2 bản backup đã hoàn tất, bản gần nhất ngày 2026-11-16.
- Lịch backup đang bật theo chu kỳ 7 ngày.
- Chưa có firewall group được gắn vào VPS trong lần kiểm tra này.
- Daily Backup của VPS không được bật theo trạng thái VPS hiện tại.

### Docker Hosting / AI automation app

`VERIFIED`:

- Có 1 resource Docker Hosting / AI automation apps đang hoạt động.
- Resource website/app gắn với `ttdnew.tech`.
- Có preview domain Hostinger.
- Trường sản phẩm hiển thị OpenClaw, nhưng runtime hiện báo `u4s-hermes-agent`. Đây là điểm cần xác minh riêng trước khi khẳng định app đang chạy thực tế là OpenClaw hay Hermes Agent.

### Hostinger AI Builder Manual mode

`VERIFIED`:

- Có 1 website: `nepdong.top`.
- Tên site: Mina.
- Đã publish.
- Không bị suspended.
- Có online store.

### Hostinger Email

`VERIFIED`: có 4 dịch vụ email đang hoạt động, mỗi dịch vụ hiện báo 100 seats:

- `nepdong.com`
- `nepdong.top`
- `qtcty.com`
- `thuanthanhdat.com`

Có thể quản lý mailbox, password, alias, forwarder, automatic reply, catch-all, storage, Webmail, IMAP/SMTP, DNS email, app/device connection và deliverability theo giới hạn gói thực tế.

### Hostinger Reach

`VERIFIED`: có 1 plan Reach 1000 gắn với `wroughtiron.shop`.

Có thể quản lý campaign, contact, sending domain, deliverability và tích hợp với store khi loại store và profile đáp ứng điều kiện.

### Hostinger Agent

`VERIFIED`: có 1 resource Hagents đang hoạt động; GitHub đã được kết nối và quyền ghi repository đã được kiểm chứng bằng commit trước đó.

### Domains

`VERIFIED`: tài khoản có các domain đang hoạt động:

- `nepdong.com`
- `nepdong.top`
- `qtcty.com`
- `giadongthau.com`
- `wroughtiron.shop`
- `ttdnew.tech`

Ngoài ra có một free domain đang ở trạng thái pending setup. Trạng thái này không được coi là domain đang hoạt động.

## 2. Chức năng tôi có thể đọc và cung cấp tài liệu vận hành

### Tài liệu Git và dự án

`VERIFIED`:

- Đọc README, PROJECT, STATE, CATALOG, rules, agents, tasks và reports trong repository.
- Đọc diff, tổng hợp hiện trạng, viết runbook, decision record, task, report và checklist.
- Tạo/cập nhật file Markdown/YAML/JSON/code theo yêu cầu.
- Commit và kiểm tra lại thay đổi trên GitHub.

### Cloud Startup Hosting và website

`DOCUMENTED` và có công cụ hỗ trợ theo từng website:

- Website inventory, nền tảng, trạng thái, domain, subdomain, parked domain và CDN.
- WordPress core context, plugin/theme, admin access, posts, pages, media, comments, users, categories, tags, products và settings khi site expose công cụ tương ứng.
- PHP, database, SSL, DNS, backup/restore, malware status, resource usage, FTP account và website availability.
- Tạo, di chuyển, đổi domain, khôi phục hoặc xử lý website theo đúng skill và approval.
- Hostinger AI Builder Manual mode: đọc site, chẩn đoán domain/publish, quản lý nội dung theo công cụ của Builder và không nhầm với WordPress hoặc Agentic mode.

### VPS KVM 2

`DOCUMENTED` và có công cụ hỗ trợ:

- Đọc trạng thái, OS, CPU/RAM/disk/bandwidth, SSH connectivity, action log, backup, snapshot, lịch backup và firewall group.
- Web Console/SSH, reset cấu hình SSH hoặc firewall, hostname, DNS resolver, PTR IPv4/IPv6 và SSH keys theo điều kiện công cụ.
- Docker Manager, Docker Compose project, container status/logs và lệnh allowlisted.
- Snapshot/backup restore, malware scanning nếu dịch vụ đã có, monitoring và resource diagnosis.
- DNS Manager, API, OS/panel và các template ứng dụng theo quyền thực tế.

Mọi lệnh hoặc thay đổi có rủi ro đều cần phạm vi rõ, rollback và approval. Reinstall OS, xóa dữ liệu, restart dịch vụ, firewall change, SSH reset, DNS change, Docker deploy/upgrade và restore không được tự động suy đoán.

### Docker Hosting / AI automation

`DOCUMENTED`:

- Theo dõi trạng thái app, restart, logs, AI log analysis, environment variables, backup và disk usage.
- OpenClaw hỗ trợ channel như WhatsApp/Telegram/Hostinger Email theo app và version.
- Hermes hỗ trợ channel và AI provider settings theo app/version.
- n8n có dashboard, environment, backups và logs theo tài liệu hiện hành.
- Hostinger Connector có thể giúp app quản lý Hostinger resources khi app, version và connector đã được xác minh.

`BLOCKED_OR_UNKNOWN` trong phiên này:

- Chưa có bằng chứng đủ về app thực tế đang chạy trên `ttdnew.tech` do metadata sản phẩm và runtime không khớp.
- Chưa có quyền truy cập trực tiếp để khẳng định trạng thái workflow n8n/Hermes/OpenClaw end-to-end.
- Không đọc secret, API key hoặc `.env` để đưa vào báo cáo.

### Email

`DOCUMENTED` và có công cụ hỗ trợ:

- Liệt kê email domain và dịch vụ.
- Mailbox, password, app password, alias, forwarder, auto-reply, catch-all, 2FA và storage.
- Webmail, IMAP/SMTP, Gmail/Outlook/Apple Mail setup.
- DNS email, MX/SPF/DKIM/DMARC và sending/receiving diagnostics.
- Deliverability, bounce, blocklist/allowlist và giới hạn plan.

## 3. Tài liệu vận hành có thể đọc trong tài khoản

Hiện tôi đọc được chắc chắn:

1. Tài liệu trong GitHub repository `DuyKienTTD/Hosting`.
2. Metadata và cấu hình trạng thái mà các công cụ Hostinger trả về.
3. Tài liệu Hostinger hiện hành về VPS, Cloud Hosting, Email, AI Builder và AI automation.
4. Nội dung WordPress/website khi site và công cụ nội dung tương ứng được xác định.

Trong lần tra cứu này, catalog không expose công cụ đọc trực tiếp filesystem của các hosting account. Vì vậy tôi **chưa thể xác nhận** rằng tôi đã đọc được các file vận hành riêng nằm trong `/home/...`, File Manager hoặc private server filesystem. Nếu tài liệu được đặt trong GitHub, WordPress, Customer Files hoặc một kênh được expose, tôi có thể đọc, phân tích và chuyển thành runbook.

## 4. Quyền hành động và giới hạn

### Có thể thực hiện sau khi có đủ input

- Đọc và chẩn đoán tài khoản, website, VPS, email, domain, DNS, backup và resource state.
- Tạo/cập nhật tài liệu và commit GitHub.
- Thực hiện thay đổi Hostinger có tool phù hợp và approval đúng yêu cầu.
- Chạy lệnh VPS nằm trong allowlist, với phạm vi rõ và không vượt qua safety gate.

### Không tự ý thực hiện

- Không thay đổi production trong khảo sát hoặc khi chưa có approval.
- Không đưa secret, token, private key, cookie, database dump hoặc dữ liệu cá nhân vào Git.
- Không kết luận app/workflow/API hoạt động chỉ từ tên resource.
- Không coi backup list là bằng chứng rằng restore đã thành công.
- Không coi một website resource là bằng chứng rằng tất cả subdomain/staging đã được kiểm tra.

## 5. Việc nên làm tiếp theo cho TTD METAL

1. Xác minh app thật đang chạy trên `ttdnew.tech`, gồm app identity, version, logs, channel và domain.
2. Tạo topology redacted của Cloud Startup, VPS, Docker/AI app, DNS, email và Reach.
3. Tạo ma trận health check cho VPS/Docker/WordPress/Builder/Email.
4. Kiểm tra backup bằng quy trình không phá hủy và ghi evidence riêng.
5. Tạo runbook rollback cho Docker, WordPress, DNS/SSL và email.
6. Đặt baseline cho reliability, automation, security, content và growth.
