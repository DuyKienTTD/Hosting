---
id: z4-production-deploy-runbook
type: runbook
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# Chuẩn bị triển khai CSKH

Gói này dùng runtime đã merge tại `c4ee17c` và bổ sung tiến trình nhận callback OA riêng. OA ingress lưu sự kiện đã xác thực vào Postgres. Runtime trong gói này chạy kênh mock. Giao diện #79 đã merge. Đóng gói giao diện, OAuth callback đổi authorization code, xử lý hàng đợi OA qua Runtime và gửi OA thật cần được nối và nghiệm thu trước khi mở phục vụ khách. Giữ STOP toàn hệ thống và `ADS_ENABLED=false` trong smoke test.

## 1. Chuẩn bị sau khi có phê duyệt triển khai

- Từ checkout đúng commit đã nghiệm thu, dùng một thư mục riêng. Kiểm tra `ss -ltn`, cấu hình Nginx đang sử dụng, DNS và dung lượng trước khi thay đổi. Chỉ dùng project `ttd-cskh`. Kiểm tra 80/443 và 18080/18081 trước khi dùng. Nếu có xung đột, dừng để đối soát. Giữ các listener 32768/32770 cùng Hermes, n8n, ttd-hermes-gate-a và ttd-p0-level1 ngoài phạm vi thao tác.
- Tạo image runtime từ `apps/ttd-zalo-agent-server/Dockerfile.data` với context là gốc repo. Tạo image Postgres từ `apps/ttd-zalo-agent-server/postgres/Dockerfile` với context là thư mục `postgres` đó. Đưa image đã nghiệm thu vào registry và ghi cả hai digest `image@sha256:…` vào hồ sơ release.
- Từ gốc repo, chạy `(umask 077 && cp deploy/.env.example deploy/.env)`. Điền digest, bốn mật khẩu DB riêng, `IDENTITY_KEY` ổn định tối thiểu 32 byte, và `DATA_TOMBSTONE_KEY` dạng 64 ký tự hex. Giữ các khóa cố định và sao lưu qua kho bí mật. Không in kết quả Compose đã nội suy ra log.
- Điền `AI_ROUTER_BASE_URL` (HTTPS), `AI_ROUTER_API_KEY`, `AI_ROUTER_DAILY_USD` và `AI_ROUTER_RATE_MULTIPLIER` đã xác minh. Runtime khóa model bằng bảng giá trong [config.ts](../apps/ttd-zalo-agent-server/src/config.ts), cho phép `claude-sonnet-5-5` và `claude-haiku-5-5`. Chọn model cho từng agent bằng `MODEL_*`. Giữ cả ba cờ bật và xác nhận credit ở 0 trong smoke. Chỉ bật AI sau khi đối chiếu trần chi và nguồn credit.
- Điền `ZALO_APP_ID`, `ZALO_APP_SECRET`, `ZALO_OA_ID`, `ZALO_WEBHOOK_SECRET` và `ZALO_OA_ENCRYPTION_KEY` (64 ký tự hex). Từ phiên cấp quyền quản trị OA, lưu cặp access/refresh token vào tệp JSON 0600 gồm `access`, `refresh`, `seconds` (tuổi token), `issued` (epoch ms). `ZALO_OA_TOKEN_FILE` và `SMOKE_TEST_PHONE` dùng riêng cho người vận hành. Số test phải là tài khoản đã đồng ý tham gia smoke. Không gắn tệp token hay số test vào container.
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

Postgres dùng volume `ttd-cskh_postgres`. Init chạy migration 001–009 cho volume mới. Với volume đã có dữ liệu, đối chiếu migration đã áp và sao lưu trước khi chạy migration còn thiếu theo thứ tự. Giới hạn tổng gồm service bảo trì là **1,45 vCPU và 2.944 MiB**. Chỉ runtime và OA ingress publish cổng loopback.

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

Kỳ vọng HTTP trả 308 với Location HTTPS, còn đường ACME vẫn phục vụ HTTP-01. HTTPS phải có `Strict-Transport-Security: max-age=31536000`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin` và `Content-Security-Policy: frame-ancestors 'none'`. HSTS chỉ áp cho hostname CSKH. Nếu kiểm tra cấu hình thất bại, khôi phục bản bootstrap rồi kiểm tra lại. Sau khi đã phát HSTS, duy trì TLS trong các lần rollback vì trình duyệt có thể đã lưu chính sách. Cấu hình Certbot reload Nginx sau khi gia hạn thành công. Timeout đọc proxy là 2 giây cho callback và handler OA trả tối đa sau 1.750 ms khi quá hạn. Kiểm tra từ bên ngoài qua TLS thay vì suy ra thời gian từ timeout cấu hình.

## 3. Smoke có kiểm soát

1. Kiểm tra `https://cskh.thuanthanhdat.com.vn/health` trả 200, `stopped=true` và `channel=mock`. `/internal`, `/internal/nick-worker` và `/operator` phải trả 404 qua Nginx. Kiểm tra không có cổng DB hoặc cổng ứng dụng bind ra ngoài loopback.
2. Gửi chữ ký giả kèm timestamp hiện tại. Kỳ vọng **401** và không tạo receipt. Kiểm tra thời gian thực tế bằng `time_total`.

   ```sh
   curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' \
     -H 'Content-Type: application/json' \
     -H "X-ZEvent-Signature: mac=$(printf '%064d' 0)" \
     -d "{\"timestamp\":\"$(date +%s%3N)\"}" \
     https://cskh.thuanthanhdat.com.vn/webhooks/zalo-oa
   ```

3. Đọc đường dẫn tệp token từ cấu hình riêng, rồi nhập bằng stdin sau khi kiểm tra đúng OA.

   ```sh
   cskh exec -T oa-ingress node /app/oa-ingress.mjs install-tokens < "$ZALO_OA_TOKEN_FILE"
   ```

4. Đăng ký webhook HTTPS `/webhooks/zalo-oa` trong Zalo và dùng tài khoản test để gửi một sự kiện test đã đồng ý. Kỳ vọng callback **200** trong dưới 2 giây. Đối soát timestamp và số receipt tại Postgres, không in ciphertext hay token. Gửi lại cùng sự kiện phải giữ một receipt. Dừng smoke nếu nhận 404, 5xx hoặc trễ. Mục này đo callback sự kiện OA. OAuth token pair được nhập ở bước 3.
5. Rà tình trạng UI và wiring OA đã nghiệm thu trước khi cho phép gửi. Chỉ dùng số test được chỉ định cho lần nghiệm thu gửi thực tế.

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
