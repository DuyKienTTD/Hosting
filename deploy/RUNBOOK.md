---
id: z4-production-deploy-runbook
type: runbook
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# Chuẩn bị triển khai CSKH

Gói này dùng runtime đã merge tại `c4ee17c` và bổ sung tiến trình nhận callback OA riêng. OA ingress lưu sự kiện đã xác thực vào Postgres. Runtime trong gói này chạy kênh mock. Image runtime chứa giao diện production của #79 và phục vụ giao diện cùng API trên HTTPS. Runtime mặc định mock. Nghiệm thu OAuth callback, luồng OA qua Runtime và gửi OA thật trước khi mở phục vụ khách. Giữ STOP toàn hệ thống và `ADS_ENABLED=false` trong smoke test.

## 1. Chuẩn bị sau khi có phê duyệt triển khai

- Từ checkout đúng commit đã nghiệm thu, dùng một thư mục riêng. Kiểm tra `ss -ltn`, cấu hình Nginx đang sử dụng, DNS và dung lượng trước khi thay đổi. Chỉ dùng project `ttd-cskh`. Kiểm tra 80/443 và 18080/18081 trước khi dùng. Nếu có xung đột, dừng để đối soát. Giữ các listener 32768/32770 cùng Hermes, n8n, ttd-hermes-gate-a và ttd-p0-level1 ngoài phạm vi thao tác.
- Tạo image runtime từ `apps/ttd-zalo-agent-server/Dockerfile.data` với context là gốc repo. Tạo image Postgres từ `apps/ttd-zalo-agent-server/postgres/Dockerfile` với context là thư mục `postgres` đó. Đưa image đã nghiệm thu vào registry và ghi cả hai digest `image@sha256:…` vào hồ sơ release.
- Từ gốc repo, chạy `(umask 077 && cp deploy/.env.example deploy/.env)`. Điền digest, bốn mật khẩu DB riêng, `IDENTITY_KEY` ổn định tối thiểu 32 byte, và `DATA_TOMBSTONE_KEY` dạng 64 ký tự hex. Giữ các khóa cố định và sao lưu qua kho bí mật. Không in kết quả Compose đã nội suy ra log.
- Điền `AI_ROUTER_BASE_URL` (HTTPS), `AI_ROUTER_API_KEY`, `AI_ROUTER_DAILY_USD` và `AI_ROUTER_RATE_MULTIPLIER` đã xác minh. Runtime khóa model bằng bảng giá trong [config.ts](../apps/ttd-zalo-agent-server/src/config.ts), cho phép `claude-sonnet-5-5` và `claude-haiku-5-5`. Chọn model cho từng agent bằng `MODEL_*`. Giữ cả ba cờ bật và xác nhận credit ở 0 trong smoke. Chỉ bật AI sau khi đối chiếu trần chi và nguồn credit.
- Điền `ZALO_APP_ID`, `ZALO_APP_SECRET`, `ZALO_OA_ID`, `ZALO_WEBHOOK_SECRET` và `ZALO_OA_ENCRYPTION_KEY` (64 ký tự hex). Từ phiên cấp quyền quản trị OA, lưu cặp access/refresh token vào tệp JSON 0600 gồm `access`, `refresh`, `seconds` (tuổi token), `issued` (epoch ms). `ZALO_OA_TOKEN_FILE` và `SMOKE_TEST_PHONE` dùng riêng cho người vận hành. Số test phải là tài khoản đã đồng ý tham gia smoke. Không gắn tệp token hay số test vào container.
- `OA_WEBHOOK_MAX_SKEW_SECONDS` mặc định 300. Webhook kiểm timestamp đã ký trước khi truy cập Postgres. Event còn trong cửa sổ và đã nhận sẽ trả 200 một cách idempotent. Event thiếu chữ ký, chữ ký sai hoặc nằm ngoài cửa sổ nhận 200 và bị bỏ trước Postgres. Sau 30 lượt bị bỏ mỗi IP/phút, ingress trả 429. Cấu hình `TRUSTED_PROXY` chỉ với địa chỉ peer thực của Nginx để ingress dùng IP client do Nginx ghi đè.
- Điền `AGE_RECIPIENT`, `BACKUP_REMOTE`, `PURGE_RECEIPT_REMOTE`, `PURGE_RECEIPT_BACKUP_REMOTE`, `WORKER_RCLONE_FILE` và `BACKUP_RCLONE_FILE`. Sổ chính và bản sao dùng đích offsite độc lập với dump. Cấp worker quyền xóa chỉ trong pending, đọc và thêm immutable đối với confirmed và sổ biên nhận. Cấp backup quyền ghi dump và đọc sổ chính, chỉ thêm vào đích sao lưu sổ. Tạo object `tombstones/_format` chứa `z4-tombstones-v1` tại prefix dump trước khi bật worker.

## 2. Khởi động và TLS

Từ gốc repo, dùng hàm sau cho mọi lệnh Compose của release.

```sh
cskh() { docker compose --env-file deploy/.env -f deploy/compose.prod.yml "$@"; }
cskh --profile maintenance config --quiet
cskh pull
cskh up -d --wait
cskh ps
curl -fsS http://127.0.0.1:18080/health
curl -fsS http://127.0.0.1:18081/health
```

Postgres dùng volume `ttd-cskh_postgres`. Init chạy migration 001–010 cho volume mới. Với volume đã có dữ liệu, đối chiếu migration đã áp và sao lưu trước khi chạy migration còn thiếu theo thứ tự. Giới hạn tổng gồm service bảo trì là **1,45 vCPU và 2.944 MiB**. Chỉ runtime và OA ingress publish cổng loopback.

Khi health đạt và host chưa có site trùng tên, cài riêng server block.

```sh
sudo install -d /var/www/cskh-acme/.well-known/acme-challenge
sudo install -m 0644 deploy/nginx/cskh.conf /etc/nginx/sites-available/ttd-cskh
sudo ln -s /etc/nginx/sites-available/ttd-cskh /etc/nginx/sites-enabled/ttd-cskh
sudo nginx -t && sudo systemctl reload nginx
sudo certbot certonly --nginx -d cskh.thuanthanhdat.com.vn
# Xác minh Certbot tạo đúng đường dẫn fullchain.pem và privkey.pem trong template.
sudo cp /etc/nginx/sites-available/ttd-cskh /etc/nginx/sites-available/ttd-cskh.bootstrap
sudo install -m 0644 deploy/nginx/cskh-https.conf /etc/nginx/sites-available/ttd-cskh
sudo nginx -t && sudo systemctl reload nginx
curl -sI http://cskh.thuanthanhdat.com.vn/health
curl -sI https://cskh.thuanthanhdat.com.vn/health
```

Kỳ vọng HTTP trả 308 với Location HTTPS, còn đường ACME vẫn phục vụ HTTP-01. HTTPS phải có `Strict-Transport-Security: max-age=31536000`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin` và CSP giới hạn script, CSS, font và kết nối trong cùng origin, cùng `frame-ancestors 'none'`. HSTS chỉ áp cho hostname CSKH. Nếu kiểm tra cấu hình thất bại, khôi phục bản bootstrap rồi kiểm tra lại. Sau khi đã phát HSTS, duy trì TLS trong các lần rollback vì trình duyệt có thể đã lưu chính sách. Cấu hình Certbot reload Nginx sau khi gia hạn thành công. Timeout đọc proxy là 2 giây cho callback và handler OA trả tối đa sau 1.750 ms khi quá hạn. Kiểm tra từ bên ngoài qua TLS thay vì suy ra thời gian từ timeout cấu hình.

### Cập nhật máy chủ đang chạy và tạo Chủ dự án

Sau khi đối chiếu và sao lưu DB, với volume đã có migration 009 nhưng chưa có 010, áp migration 010 một lần qua kết nối quản trị trong container. Xác minh migration đã áp bằng `SELECT to_regprocedure('public.web_create_operator(uuid,text,text,text,text)');`. Kết quả rỗng nghĩa là còn thiếu.

```sh
cskh exec -T postgres psql -v ON_ERROR_STOP=1 -U zalo_admin -d zalo < apps/ttd-zalo-agent-server/postgres/010-web-accounts.sql
cskh up -d --wait
sudo install -m 0644 deploy/nginx/cskh-https.conf /etc/nginx/sites-available/ttd-cskh
sudo nginx -t && sudo systemctl reload nginx
curl -fsSI https://cskh.thuanthanhdat.com.vn/health
curl -fsS https://cskh.thuanthanhdat.com.vn/ >/dev/null
```

Các lệnh trên giả định digest đã được cập nhật trong cấu hình và image đã được pull. UI dùng cùng runtime và cổng loopback 18080, vì vậy ngân sách Compose không tăng. Template bootstrap HTTP chưa phục vụ UI hoặc API đăng nhập.

Tạo tài khoản đầu tiên bằng Bash trên VPS. Dùng tên đăng nhập do Chủ dự án chọn và nhập mật khẩu qua stdin dạng ẩn. Giữ mật khẩu ít nhất 16 ký tự.

```bash
(
  set +x
  IFS= read -r -s -p 'Mật khẩu tài khoản Chủ dự án: ' owner_pass
  printf '\n' >&2
  printf '%s' "$owner_pass" | cskh exec -T runtime node dist/ttd-zalo-agent-server/src/main.js \
    web-bootstrap-owner ten-chu-du-an 'Chủ dự án'
)
```

Bootstrap chỉ chạy khi bảng tài khoản trống. Đăng nhập tại HTTPS, vào **Cài đặt → Tạo tài khoản vận hành** để cấp tài khoản riêng cho Bán hàng và CSKH. Truyền mật khẩu ban đầu qua kênh riêng đã được phê duyệt. Phiên HTTPS dùng cookie Secure, HttpOnly, SameSite=Strict. Phiên bản này giới hạn 10 lần đăng nhập sai cho mỗi IP và 5 lần cho mỗi tên tài khoản (bỏ khoảng trắng đầu/cuối và không phân biệt hoa thường khi tính giới hạn) trong 15 phút. Khi chạm ngưỡng, lần thử tiếp theo phải chờ 30 giây. Mỗi lần sai tiếp theo kéo dài thời gian chờ đến tối đa 5 phút và hết hạn theo cửa sổ 15 phút. Bộ nhớ tạm có giới hạn 10.000 khóa mỗi loại, tổng tối đa 600 lượt xác minh/phút và 16 lượt đồng thời. Bộ đếm bắt đầu lại khi runtime khởi động lại.

Nginx ghi đè `X-Forwarded-For` bằng địa chỉ client. Runtime chỉ dùng header khi peer socket là loopback hoặc IP khai báo chính xác trong `TRUSTED_PROXY`. Nếu Docker chuyển kết nối từ Nginx qua địa chỉ gateway thay vì loopback, chạy lệnh sau sau khi runtime đã lên, đối chiếu với các bridge của riêng project CSKH, rồi điền IP gateway thực tế vào `deploy/.env` và tạo lại runtime. Chỉ liệt kê IP proxy cần thiết, phân cách bằng dấu phẩy. Khi peer chưa được tin cậy, bộ đếm dùng IP socket.

```sh
docker inspect --format '{{range .NetworkSettings.Networks}}{{println .Gateway}}{{end}}' "$(cskh ps -q runtime)"
cskh up -d --wait runtime
```

## 3. Smoke có kiểm soát

1. Kiểm tra `https://cskh.thuanthanhdat.com.vn/health` trả 200, `stopped=true` và `channel=mock`. `/internal`, `/internal/nick-worker` và `/operator` phải trả 404 qua Nginx. Kiểm tra không có cổng DB hoặc cổng ứng dụng bind ra ngoài loopback.
2. Gửi chữ ký giả kèm timestamp hiện tại. Kỳ vọng **200** với `{"error":0}` và thay đổi **0 receipt**. Đếm bằng `SELECT count(*) FROM oa_inbox` trước và sau trong phiên smoke cô lập. Kiểm tra thời gian thực tế bằng `time_total`.

   ```sh
   curl -sS -w '%{http_code} %{time_total}\n' \
     -H 'Content-Type: application/json' \
     -H "X-ZEvent-Signature: mac=$(printf '%064d' 0)" \
     -d "{\"timestamp\":\"$(date +%s%3N)\"}" \
     https://cskh.thuanthanhdat.com.vn/webhooks/zalo-oa
   ```

3. Trên Zalo Developers, đặt **Callback URL** của app là `https://cskh.thuanthanhdat.com.vn/api/v1/oa/oauth/callback` và lưu quyền OA dùng cho nhắn tin. Giữ STOP, OA mock và AI mock. Đăng nhập giao diện bằng tài khoản owner, mở **Kênh Zalo → Kết nối OA**, rồi chọn đúng OA và bấm cho phép bằng tài khoản quản trị OA. Nút tạo link cấp quyền mới tại `https://oauth.zaloapp.com/v4/oa/permission` với PKCE và state hết hạn sau 10 phút. Sau callback thành công, hệ thống lưu cặp token mã hóa trong Postgres và trở lại Kênh Zalo. [OAuth v4 của Zalo](https://docs.zaloplatforms.com/docs/OA/bat-dau/xac-thuc-va-uy-quyen-cho-ung-dung-new)
4. Gửi một tin từ tài khoản test đã đồng ý để tạo tương tác. Webhook có chữ ký hợp lệ phải trả 200 dưới 2 giây. Phát lại trong cửa sổ giữ đúng một receipt. Chỉ kiểm thời gian và số receipt.
5. Trong `.env`, đặt `OA_MODE=live`, `CHANNEL_MODE=mock`, `CHANNEL_SMOKE_ONLY=1`, `SMOKE_ALLOWLIST=<UID OA của tài khoản test>` và `AI_MODE=mock`. Allowlist chứa UID mà OA nhận trong webhook, ví dụ trường `sender.id`. Chạy `cskh up -d --wait runtime`, kiểm health và STOP, rồi chạy `cskh exec -T runtime node dist/ttd-zalo-agent-server/src/main.js resume global` ngay trước lượt gửi đã duyệt. Giữ quảng cáo tắt. Chỉ dùng hội thoại test có consent và đã tương tác hợp lệ.
6. Kết thúc smoke hoặc gặp lỗi, chạy `cskh exec -T runtime node dist/ttd-zalo-agent-server/src/main.js stop global`. Đặt lại `OA_MODE=mock`, `CHANNEL_SMOKE_ONLY=0`, xóa giá trị `SMOKE_ALLOWLIST` và giữ `AI_MODE=mock`. Tạo lại runtime, kiểm `channel=mock` và `stopped=true`. Chỉ xem xét bật AI sau khi owner xác nhận credit, allowlist model và các trần ngân sách.

## 4. Backup và thử restore

Lập lịch hằng ngày, chạy tuần tự để không vượt ngân sách tài nguyên.

```sh
# BACKUP_LOG là đường dẫn log riêng tồn tại ngoài container, quyền 0600.
(umask 077
 cskh --profile maintenance run -T --rm backup postgres >> "$BACKUP_LOG" 2>&1 &&
 cskh --profile maintenance run -T --rm backup receipts >> "$BACKUP_LOG" 2>&1)
```

Hai job dùng `restart: "no"`, truyền mã lỗi khác 0 lên scheduler và chỉ ghi `backup_success job=… at=…` sau khi job tương ứng hoàn tất. Giám sát dòng thành công mới nhất riêng cho `postgres` và `receipts` trong log bền, đồng thời cảnh báo khi lệnh lập lịch trả lỗi. Mọi service chạy lâu có healthcheck.

Dump Postgres được mã hóa bằng age. Sổ biên nhận có đích ghi chính và bản sao riêng ngoài VPS. Xác minh quyền đọc và checksum của bản sao, cùng thời hạn giữ không ngắn hơn dump lâu nhất. Nạp `DATA_TOMBSTONE_KEY` vào môi trường shell từ kho bí mật. Mount tệp khóa age riêng chỉ đọc rồi thử restore vào tên DB staging duy nhất bắt đầu bằng `restore_`:

```sh
cskh --profile maintenance run --rm \
  -e DATA_TOMBSTONE_KEY -e AGE_IDENTITY_FILE=/run/age-identity \
  -e RESTORE_SOURCE_DATABASE=zalo -v "$AGE_IDENTITY_HOST_FILE:/run/age-identity:ro" \
  --entrypoint sh backup /ops/restore.sh "$DUMP_NAME" restore_cskh_drill
cskh --profile maintenance run --rm --entrypoint sh backup \
  /ops/restore-control.sh restore_cskh_drill list
```

Kiểm tra bản ghi và audit trong staging. Đối soát mọi purge chưa rõ trước khi promote. Drill để staging cô lập. Với khôi phục thật, freeze writer, worker và cập nhật legal hold ở nguồn trong suốt cutover. Tham chiếu [quy trình dữ liệu](../apps/ttd-zalo-agent-server/DEPLOY.md) để đổi đích kết nối sau khi owner duyệt.

## 5. Rollback

- Dừng nhận callback bằng cách gỡ symlink site riêng của CSKH, kiểm tra `nginx -t` rồi reload. Giữ bản cấu hình site và TLS để phục hồi. Dùng `cskh stop` khi cần dừng project.
- Khôi phục hai digest và checkout của release trước. Nếu schema còn tương thích, chạy `cskh up -d --wait`, kiểm tra health rồi mới mở lại site. Giữ volume. Khi migration không tương thích, khôi phục vào staging và đối soát purge trước khi đổi đích kết nối. Giữ STOP khi xác minh.
