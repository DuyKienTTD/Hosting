# AGENTS.md — Hosting (TTD METAL)

Repo **public** cho hạ tầng và tự động hóa marketing của TTD METAL: VPS Hostinger, n8n, Hermes, website wroughtiron.shop, quảng cáo, media, báo cáo. Sản phẩm Zalo Assistant nằm ở repo **private** `DuyKienTTD/TTD-Zalo-Assistant`. Không đưa mã, tài liệu hay dữ liệu Zalo vào repo này.

## Mỗi phiên làm việc

1. Đầu phiên: hook tự chạy `python3 scripts/session_start.py`. Nếu công cụ của bạn không có hook thì tự chạy lệnh đó. Lệnh in PROGRESS và các việc đang mở.
2. Làm **đúng một issue**. Không có issue thì không sửa repo; hãy đề xuất issue cho Lập kế hoạch.
3. Làm trên nhánh `agent/<số-issue>-<mô-tả-ngắn>`. Mở PR có dòng `Closes #<số-issue>`.
4. Cuối phiên: cập nhật `work/<số-issue>.json`, thêm một mục vào đầu `PROGRESS.md` (tối đa 5 dòng), commit và push. Hook Stop sẽ chặn kết thúc nếu tiêu chí chưa đạt mà không ghi lý do bị chặn.

## Định nghĩa "xong"

- Mỗi issue có `work/<số-issue>.json`, tạo từ [work/TEMPLATE.json](work/TEMPLATE.json).
- Mỗi tiêu chí bắt đầu với `passes: false` và có `verify`, là lệnh hoặc bằng chứng mà người khác kiểm lại được.
- Chỉ đổi `passes` thành `true` sau khi đã chạy `verify` thành công, và ghi vào `evidence`. Không xóa tiêu chí, không sửa `description`.
- Bị chặn thì đặt `status: "blocked"` và ghi rõ `blocker`: thiếu gì, cần ai. Không dừng im lặng.
- PR chỉ được merge khi CI `check` xanh.

## Vai trò và quyền

| Vai trò | Ai | Được làm | Không được làm |
|---|---|---|---|
| Chủ dự án | Chủ sở hữu tài khoản (A0) | Mọi quyền. Merge PR có nhãn `risk:*`. Quyết định tài khoản, chi phí, production. | — |
| Lập kế hoạch | Trợ lý A0 (ChatGPT, chat) | Viết issue và tiêu chí. Review PR bằng comment. | Push, merge, sửa tiêu chí sau khi đã có người nhận |
| Điều phối | Claude | Phân loại issue, chọn người thực thi. Merge PR **không** có nhãn `risk:*` khi CI xanh và đã có review. Giữ PROGRESS gọn. | Merge `risk:*`, đổi quyền, đổi thanh toán |
| Thực thi | Codex (mặc định, dùng hạn mức gói ChatGPT), Claude Code; ChatGPT Work cho việc thao tác web (hPanel, WordPress) | Sửa trong phạm vi issue, trên nhánh `agent/*`, rồi mở PR | Push lên `main`, tự merge, tự review PR của mình, làm việc ngoài issue |
| Kiểm tự động | CI `check`, Codex review | Chặn merge | — |
| Runtime | n8n, Hermes trên VPS | Chạy cấu hình đã merge | Nhận việc trực tiếp từ chat |

Việc cần chủ dự án duyệt phải gắn nhãn tương ứng: `risk:prod` (thay đổi live), `risk:cost` (phát sinh chi phí), `risk:secret` (credential, quyền truy cập).

## Luật cứng (CI kiểm)

- Không đưa vào Git: bí mật, token, `.env`, PII, IP hoặc hostname thật, dump, log thô. Nếu lỡ lộ: dừng, báo chủ dự án, rotate credential. Không tự rewrite lịch sử.
- Không push thẳng lên `main`, không force push.
- Không có đường dẫn nào chứa `zalo`.
- File `work/*.json` phải đúng mẫu.
- Link nội bộ trong Markdown phải trỏ tới file có thật (trừ `archive/`).

Chạy kiểm tra tại máy: `python3 scripts/check.py`.

## Bản đồ

| Thư mục | Dùng cho |
|---|---|
| `docs/adr/` | Quyết định, định dạng MADR. Không sửa quyết định cũ; tạo ADR mới để thay thế. |
| `docs/runbooks/` | Cách làm từng bước, có cách xác minh và rollback |
| `docs/reference/` | Tra cứu: VPS, dịch vụ, cổng. Đã che giá trị nhạy cảm. |
| `infra/` | Script và cấu hình triển khai |
| `work/` | Tiêu chí "xong" theo issue |
| `archive/legacy-2026-11/` | Hồ sơ của mô hình cũ. Chỉ đọc khi issue yêu cầu. **Không** phải nguồn quyền hay trạng thái. |
