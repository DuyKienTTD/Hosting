# TTD Zalo nick worker

## Windows fixture test

Install Node.js 22 or newer and use PowerShell from this directory.

```powershell
npm ci
npx playwright install chromium
npm test
```

The test starts an HTTP server bound to loopback, opens the synthetic fixture in Chromium and exercises the worker with an in-process server endpoint. No account is needed.

## Windows runtime configuration

Install Google Chrome Stable. Start the process under the Windows user that owns its dedicated profile directory. Playwright starts Chrome over a local CDP pipe without an open debugging port. Run one worker per profile and keep its runtime directory outside the Git checkout.

| Environment variable | Value |
|---|---|
| `NICK_PROFILE_ROOT` | Absolute, access-controlled local directory for this worker |
| `NICK_WEB_URL` | Local synthetic fixture URL with the fixture selectors |
| `NICK_SELECTOR_FILE` | Absolute path to a reviewed, versioned selector JSON. The included `selectors/fixture-v2.json` targets the fixture |
| `NICK_SERVER_URL` | WSS endpoint implementing the [protocol](../../docs/nick-worker-protocol.md) |
| `NICK_WORKER_AUTH` | Runtime credential supplied by the approved local secret mechanism |

Start the configured process with `npm start`; stop it with Ctrl+C. The server STOP and UI safety markers latch a durable stop. Preserve `delivery.jsonl` and the profile on restart. Any reactivation requires operator review of the cause and controlled restoration that preserves the delivery journal's idempotency records. A blocked attempt can leave a draft in the composer. The worker requires an empty composer before starting the next job.

The supplied selectors only cover synthetic HTML. A separately reviewed selector configuration and server integration are prerequisites for live use. The worker rotates through visible existing 1-1 inbox rows and checks the active recipient before sending. Off-screen inbox rows and unrendered history are outside the scanner.

## Cài trên máy Windows của chủ dự án

1. Sau khi quản trị viên triển khai migration `014-nick-enrollment.sql`, runtime và cấu hình Nginx của PR này, đăng nhập bằng chính tài khoản Windows sẽ chạy worker.
2. Chuẩn bị bản checkout của PR đã duyệt và tệp selector Zalo Web đã được kiểm chứng. Repo hiện chỉ kèm selector fixture. PowerShell dùng winget nếu thiếu Chrome hoặc Node.js LTS.
3. Đăng nhập ứng dụng CSKH với quyền chủ dự án. Vào **Kênh Zalo → Nick Zalo phụ → Tạo mã ghép cặp nick phụ**. Mã dùng một lần, hết hạn trong 10 phút.
4. Trong PowerShell, tại thư mục worker, chạy:

   ```powershell
   .\install-nick-worker.ps1 -SelectorFile 'C:\DuongDan\selectors-da-duyet.json'
   ```

   Để ghi danh sách thử, thêm `-SmokePeer 'id-test-1','id-test-2'` với ID hội thoại đã xác minh. Danh sách trống chặn mọi gửi ở worker. Nhập mã khi được hỏi. Credential được lưu bằng DPAPI theo user Windows. Không đưa mã hay credential vào dòng lệnh.
5. Kiểm tra tác vụ **TTD-Zalo-Nick-…** trong Task Scheduler. Worker chạy khi user đăng nhập, dùng profile riêng và CDP qua pipe cục bộ không mở cổng TCP. Đăng nhập Zalo trong cửa sổ Chrome riêng. Worker kết nối WSS ra ngoài. Ghép cặp mới đặt STOP và chỉ thiết lập kết nối điều khiển/audit. Runtime hiện chưa cấp job hoặc permit gửi nick.
6. Bản cài chạy smoke-only. Worker giới hạn tối đa 2 lượt/giờ và 5 lượt/ngày, kiểm tra bạn bè trước khi soạn và bấm, và chỉ chấp nhận permit Guard xác nhận quyền chăm sóc khách và opt-out. Không dùng tài khoản khách thật để thử.

**Gỡ cài đặt:** Trong UI, chọn **Thu hồi kết nối** trước. Sau đó chạy `.\install-nick-worker.ps1 -Uninstall` bằng cùng user Windows. Lệnh xóa lịch chạy và credential cục bộ, giữ profile cùng nhật ký để đối soát. Xóa các tệp còn lại thủ công sau khi đã lưu bằng chứng cần giữ.
