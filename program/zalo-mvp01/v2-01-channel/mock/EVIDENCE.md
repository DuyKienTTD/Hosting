---
id: v2-01-evidence
type: report
status: draft
updated_at: 2026-11-26
sensitivity: public
---

# Bằng chứng thực thi

26/11/2026 ICT, Node 24.22.3, Python jsonschema 4.26.0. Chỉ dùng ID tổng hợp. Kết quả HTTP dưới đây đã bỏ ID trace và thuộc tính không cần thiết.

| Lệnh | Quan sát | Exit |
|---|---|---|
| `curl -sS --max-time 12 -X GET -w '\nHTTP %{http_code}\n' https://api.subiz.com.vn/4.1/me` | HTTP 400, `{"code":"access_deny,internal","class":500,"error":{"code":"access_deny,internal"}}` | 0 |
| `curl -sS --max-time 12 -X GET -w '\nHTTP %{http_code}\n' https://api.subiz.com.vn/4.0/conversations/synthetic/messages` | HTTP 400, `code=missing_id,invalid_input,internal`, `class=500`, `error.code` cùng giá trị. Request bị chặn ở định danh, chưa chứng minh quyền đọc. | 0 |
| `curl -sS --max-time 12 -X POST -w '\nHTTP %{http_code}\n' https://bot-api.zaloplatforms.com/botINVALID/getMe` | HTTP 200, `{"ok":false,"description":"Not Found","error_code":404}`. Đọc cả envelope. Docs nêu 401 cho token không hợp lệ/hết hạn, còn chuỗi giả thử ở đây nhận 404 trong body. | 0 |
| `curl -sS --max-time 4 -w '\nHTTP %{http_code}\n' https://api.subiz.com.vn/4.1/conversations/synthetic/history` | Negative control ngoài danh mục, HTTP 404 `not_found,invalid_input`; route đúng nằm ở phiên bản 4.0 như hàng trên. | 0 |
| `npm --fetch-retries=0 --fetch-timeout=4000 install --prefix /tmp/v201-sdk --ignore-scripts --no-audit --no-fund node-zalo-bot` | Cài 0.1.6, 189 package; có cảnh báo dependency deprecated. Cài ở thư mục tạm. Để tái lập cố định `node-zalo-bot@0.1.6`. | 0 |
| `V201_SDK_MODULE=/tmp/v201-sdk/node_modules/node-zalo-bot node --test mock/check.mjs` | Loopback PASS 5, 0 skipped, gồm SDK `getMe/getUpdates/processUpdate/sendMessage`. Thử webhook HMAC, body đã sửa, hai digest, replay, echo/nội bộ, 429, mất phản hồi, Bot header. | 0 |
| `python mock/check-schemas.py` | PASS 10 lệnh, key bắt buộc, tách group/direct, event và lỗi. | 0 |
| `npx --yes --fetch-retries=0 --fetch-timeout=10000 --package typescript@5.9.3 tsc --noEmit --strict --target es2022 ADAPTER_CONTRACT.ts` | TypeScript PASS. | 0 |

INCIDENT: Probe ban đầu 4–8 giây có HTTP 000 và curl exit 28 trên endpoint Subiz/Bot, probe registry trực tiếp cũng timeout. Các probe đúng route sau đó nhận phản hồi, npm cài thành công. Schema test lần đầu exit 1 vì clock format checker của môi trường không xác minh date-time, đã thêm ràng buộc cấu trúc trong schema và chạy lại. Git CLI mirror thiếu xác thực, dùng đường GitHub connector. Local không có PowerShell. GitHub Actions chạy validator của repo theo workflow.

Nguồn schema: [Subiz sign](https://subiz.com.vn/developers/webhooks/receiving), [Subiz send](https://subiz.com.vn/developers/api-reference/messages/send), [Subiz errors](https://subiz.com.vn/developers/get-started/errors), [Bot polling](https://bot.zaloplatforms.com/docs/apis/getUpdates/), [Bot webhook](https://bot.zaloplatforms.com/docs/webhook/), [Bot send](https://bot.zaloplatforms.com/docs/apis/sendMessage/) · 26/11/2026. [Payload](payloads.json) là tổng hợp. Server chỉ bind loopback. Dedup mock dùng bộ nhớ và script chỉ gây mất kết nối cục bộ, không xác nhận idempotency sau restart, gửi thật hay delivery. Mô phỏng tĩnh cho Subiz history, không kiểm paging live. Các quyền nhóm, bạn bè và route Personal cần smoke đã xác thực.
