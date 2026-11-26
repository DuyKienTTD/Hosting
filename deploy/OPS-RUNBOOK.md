# Backup and monitoring jobs

Copy `ops.env.example` into a private configuration file and substitute the placeholders. Set file access to owner only. Store key material separately.

1. Load the private setup configuration and run `setup-rclone-gdrive.sh` locally on the deployment host. On the browser machine, follow the headless authorization command emitted by rclone. Use the approved Drive account and paste the resulting authorization response into the private prompt. [Rclone headless authorization](https://rclone.org/remote_setup/)
2. Set `BACKUP_REMOTE=<BACKUP_REMOTE>`, `PURGE_RECEIPT_REMOTE=<RECEIPT_REMOTE>`, `PURGE_RECEIPT_BACKUP_REMOTE=<RECEIPT_BACKUP_REMOTE>`, rclone mount paths, and `BACKUP_RETENTION_COUNT=<DUMP_COUNT>` in the external Compose environment. Choose separate destinations for receipt storage and its recovery copy according to the operator policy.
3. Install the checked-in units. In private service drop-ins, set `EnvironmentFile=<OPS_ENV_FILE>` under `[Service]`. In private timer drop-ins, set `OnCalendar=<BACKUP_SCHEDULE>` and `OnCalendar=<MONITOR_SCHEDULE>` under `[Timer]`, respectively. Validate each calendar expression before enabling the timers.
4. Run `host-job.sh backup` once with the private environment and verify the success marker. Run `host-job.sh drill <DUMP_NAME>` with the age identity and tombstone key provided through the private environment. The drill never promotes staging. It refuses to reuse an existing staging database.
5. Check the logs under `<STATE_DIR>` and review owner notices after running `host-job.sh monitor`. Monitor reads service health, certificate expiry, disk use, backup freshness, budget consumption, and OA token expiry. Alerts are recorded locally and in owner notices when the database is reachable.

## OAuth và quyền đọc cấu hình

Tạo OAuth client loại **Desktop** trong Google Cloud. Chọn **Internal** khi tổ chức dùng Workspace và ứng dụng phục vụ nội bộ. Chạy script setup trong terminal riêng. Client ID, client secret và kết quả token đều nhập ẩn. Script lưu blob URL-safe không padding vào tệp tạm riêng. Chuyển tệp này qua kênh riêng, dùng lệnh authorize được in ra, rồi xóa bản sao trên máy trình duyệt. Blob có thể giải mã thành thông tin client.

Scope `drive.file` không tự cấp cho client mới quyền đọc các tệp do client cũ tạo. Khi đổi client, tạo lại thư mục và `_format` bằng client mới, giữ bản backup cũ cùng đường truy cập đã xác minh. Sau đó thử backup và restore với đích mới.

`BACKUP_REMOTE=<REMOTE>:<PREFIX>` là prefix gốc. Script tự nối `/dumps` và `/tombstones`. Dùng `<REMOTE>:<PREFIX>/dumps` làm giá trị sẽ tạo `dumps/dumps` và worker không đọc được marker. Kiểm tra bằng `rclone --config "$BACKUP_RCLONE_FILE" cat "$BACKUP_REMOTE/tombstones/_format"`. Kỳ vọng `z4-tombstones-v1`.

Giữ bản cấu hình quản trị root 0600 riêng. Worker chạy dưới user node của image, mặc định UID/GID 1000. Tạo bản worker riêng bằng `install -o <CONTAINER_UID> -g <CONTAINER_GID> -m 0400 <ADMIN_RCLONE_CONFIG_FILE> <WORKER_RCLONE_CONFIG_FILE>` và trỏ `WORKER_RCLONE_FILE` vào bản đó. Khi đổi hoặc cấp lại token, cập nhật lại bản worker và tạo lại container worker để bind mount đọc tệp mới.

## Môi trường riêng cho restore drill

Đặt `DATA_TOMBSTONE_KEY` và `AGE_IDENTITY_HOST_FILE` trong tệp môi trường riêng quyền 0600. Giữ key ngoài `ops.env`. Chạy drill trong subshell với biến được export:

```sh
(
  set -a
  . "<PRIVATE_OPS_ENV_FILE>"
  . "<PRIVATE_DRILL_ENV_FILE>"
  set +a
  bash deploy/host-job.sh drill "<DUMP_NAME>"
)
```

Giữ tệp Compose `.env` để Compose đọc qua `--env-file`. Tránh source tệp này vào shell tương tác vì biến shell đã export được ưu tiên hơn giá trị trong `--env-file`.

## Làm mới token trong container

Worker và các job backup sao chép cấu hình nguồn chỉ đọc vào tmpfs riêng, quyền 0600 và thuộc UID của tiến trình. rclone lưu token vừa làm mới trong vòng đời container. Cấu hình trên host giữ nguyên. Khi đổi token trên host, cập nhật bản worker rồi recreate worker bằng `compose up -d --force-recreate worker` theo lệnh Compose của dự án. Job backup mới đọc bản cấu hình admin hiện tại mỗi lần chạy. Bind mount một tệp có thể giữ inode cũ sau khi host thay tệp.

`RCLONE_MARKER_TIMEOUT_SECONDS` mặc định 30 giây và nhận số nguyên từ 1 đến 120. Lệnh đọc marker thử ở cấp lệnh một lần và giới hạn thử cấp kết nối ở hai lần. Khi chạy restore thủ công và ghi đè entrypoint backup, gọi `sh /deploy/with-rclone-config.sh sh /ops/restore.sh <DUMP_NAME> <STAGING_DATABASE>` để chuẩn bị bản ghi được trước khi dùng rclone.
