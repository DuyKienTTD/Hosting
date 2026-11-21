---
id: hermes-gate-b-egress-isolation-2026-11-21
type: report
status: blocked
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
---

# GATE B — Cô lập proxy và preflight trên KVM2

**BLOCKED_PREFLIGHT.** Đã khắc phục đường từ bridge tới proxy Level 2. Guard vẫn chạy upstream mock và chưa được gắn credential OpenAI. Không tạo permit thật, không gọi inference và không phát sinh phí. [Nhiệm vụ](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [Evidence](evidence/2026-11-21-ttd-hermes-gate-b-egress-isolation.json).

## Điều đã kiểm chứng

| Hạng mục | Kết quả |
| --- | --- |
| Topology live | Gỡ proxy khỏi mạng P0 dùng chung. Mạng nội bộ mới chỉ có guard và proxy, còn mạng outbound chỉ có proxy. Đã backup hai file Compose và chạy `docker compose config -q` trước khi áp dụng. Cấu hình hiện nằm trong Compose trên VPS. Adapter Level 2 đang dừng. |
| Negative network tests | Bridge, Hermes auxiliary, provider mock, n8n sandbox và hai container production đều bị chặn khi thử DNS alias và cả hai IPv4 của proxy. Guard truy cập health của proxy HTTP 200. Guard, bridge, auxiliary, provider mock và n8n sandbox đều bị chặn khi mở TCP trực tiếp tới IPv4 OpenAI dùng trong phép thử. Hai network của proxy không bật IPv6. |
| Provider | Guard đi qua proxy, xác minh TLS và nhận HTTP 401 từ GET metadata OpenAI không gửi credential. Không có credential provider trong mount dự kiến hoặc biến môi trường của guard. Vì vậy chưa xác minh được danh tính key thực tế, project, quyền ghi Responses, quota hoặc billing của key đó. |
| Request | Đóng băng 3.308 byte canonical từ lượt Hermes mock thành công. SHA-256 có trong evidence. Đây là fixture bên trong VPS, chưa có kết quả đếm token chính xác từ provider và chưa khóa vào permit paid. Có thể dùng endpoint đếm token miễn phí sau khi xác minh credential và ràng buộc kết quả với digest cuối. [OpenAI về đếm input](https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens). |
| Mock E2E và callback | Lượt đầu webhook trả 500 với `HERMES_RUNTIME_MISMATCH` trong bridge. Lượt mock với task mới PASS trên topology đã sửa. Webhook 200, callback 200, một lượt đến mock và replay không tăng lượt. Ma trận cũng PASS cho xác thực, schema, timeout phía client, concurrency và lỗi provider mock. Sai khác metadata Hermes chưa được chẩn đoán dứt điểm. |
| Hạch toán mock | Chạy riêng test one-shot trong namespace guard, với loopback và ledger tạm. Ba ca hoàn chỉnh, timeout và stream bị cắt đều PASS. Mock quan sát permit consumed và reservation trước mỗi lần nhận, đúng fingerprint, tamper và replay đều không gửi thêm. Chưa chạy một lượt xuyên n8n và Hermes đồng thời dùng cơ chế hạch toán one-shot mới. |
| Rollback và production | Ngắt guard khỏi mạng proxy làm mất quyền tới proxy trong khi health mock guard vẫn 200. Nối lại phục hồi health proxy 200 và không nối proxy về mạng chung. Production n8n/Hermes HTTP 200 trước/sau với restart count cuối 0. Ledger thật giữ 1 attempt, 0,0035 USD reserved, 0,0000496 USD ước tính usage lịch sử, kill switch ON và 0 permit. Tiền tố SHA-256 khớp baseline. |

## Điều kiện còn thiếu

Chỉ định credential dành cho guard bằng secret mount trong VPS và xác minh đúng project, quyền Responses hữu hiệu và billing. Cần chốt request do Hermes thực sự gửi, đếm token theo provider với cùng đầu vào và gắn số đếm với hash của byte cuối. Cần giải quyết lỗi metadata không ổn định và chứng minh callback cùng hạch toán one-shot trong một lượt mock trước khi cấp permit thật. Reservation 0,0035 USD chỉ là khoản giữ chỗ. Phải đối chiếu endpoint, tier phục vụ, số tokens và mọi thành phần tính phí trước khi xem khoản này là đủ.

Khi cần ngắt egress sandbox, tách guard khỏi network chuyên dụng và giữ proxy ngoài mạng dùng chung. Nếu tái tạo container từ cấu hình mẫu trong Git, áp dụng lại thay đổi topology hiện có trên VPS trước khi start proxy. Hai file Compose mẫu GATE A và Level 2 thể hiện cấu hình ở mốc tương ứng.
