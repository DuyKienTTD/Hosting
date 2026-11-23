---
id: eng-01a-s2-fake-channel-adapters-report
type: report
status: current
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
task_id: eng-01a-s2-fake-channel-adapters
owner: codex
---

# ENG-01A-S2 — GA4 và WordPress/WooCommerce synthetic reads

| TASK | OWNER | BASE_SHA | ASSIGNMENT_ACK | OBSERVED/EXPECTED | TEST_DELTA | EVIDENCE | VERDICT | LIMITATIONS | NEXT_OWNER |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENG-01A-S2 | Codex | `e385c1b` | EXECUTE, 23/11/2026 ICT | Hai adapter chỉ đọc fixture, dữ liệu chuẩn hóa có attribution/provenance, lỗi không đổi kết quả đọc sau đó | 7/7 phương thức test S2 | [JSON](evidence/2026-11-23-eng-01a-s2-fake-channel-adapters.json) | `ENG01A_S2_CHANNEL_MOCK_PASS` | `REAL_GA4_UNTESTED / REAL_WP_WOO_UNTESTED / LINUX_NOT_RUN / INTEGRATION_PENDING_PR10` | ChatGPT Điều phối |

Đã ACK chỉ thị `7090796992`, quy tắc tại `e385c1bea2070973e3007e5717f7e980348d6ab3`, Workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. Fetch PR #6 `cdf0aed`, S1 PR #10 `79dfe8a`, BIZ-01 PR #12 `8c821bb`. Không thấy task/branch trùng khi nhận việc. S1 đã có acceptance offline có giới hạn, PR #10 vẫn mở; không sửa nhánh hoặc chạy lại suite S1. [Lệnh thực thi](https://github.com/DuyKienTTD/Hosting/pull/10#issuecomment-7090796992) · [Task](../tasks/2026-11-23-eng-01a-s2-fake-channel-adapters.md) · [BIZ-01](https://github.com/DuyKienTTD/Hosting/commit/8c821bbf1842eccb8519127f54ba7673965276d5).

## Test delta

| Ca | Kỳ vọng và quan sát |
| --- | --- |
| GA4 report hợp lệ | Trả đúng 3 dòng tổng hợp có nguồn/kênh và đơn vị đếm cho khoảng ngày 20–21/11. Hai bản ghi nguồn được tham chiếu từ aggregate. Report lặp khớp digest. Observation timestamp đến từ fixture. |
| GA4 validation | 10 biến thể sai dimension/metric/ngày/budget bị 422. Kỳ hợp lệ không có dữ liệu trả 200 với 0 dòng. Budget thiếu không cắt im lặng. |
| WP/Woo scope và locale | Hai locale EN/VI có site, posts, pages và products riêng. Get khớp list. Phân trang posts/pages/products đã đo ở cả hai locale. Giá product giữ nguyên số nguyên ở đơn vị tiền nhỏ và USD/VND. |
| Cursor và watermark | Ba trang posts EN cho 3 ID khác nhau. Cursor lặp trả cùng trang. Đổi locale, limit hoặc watermark từ chối cursor cũ 409; cursor malformed/out-of-range bị 422. Incremental giữ bản ghi có timestamp trùng nhưng ID sau watermark. Chỉ trang cuối trả watermark để commit. |
| Lỗi và isolation | Cả hai adapter cho lỗi giả 403, 429, hoặc deadline logic 504/`outcome_unknown` với 0 record. Missing WP trả 404. Không phát cursor/watermark ở các lỗi. Sau lỗi, lần đọc hợp lệ vẫn bằng baseline, thay đổi response từ phía caller không ảnh hưởng fixture. |
| Mapping | Bốn loại record có version, ID, nguồn, observation UTC, classification/source status `SYNTHETIC`, provenance `MOCK`. Bảy bản ghi bị sửa sai nguồn, KPI, locale, tiền, timestamp hoặc thêm định danh cá nhân đều bị từ chối. Không tạo lead/customer/order record hoặc join người từ aggregate. |
| Offline boundary | `LIVE_ENABLED=False`, kiểm import qua AST, không có write method. Cả hai adapter từ chối endpoint/credential. Test tự kiểm socket audit hook từ chối, không mở kết nối. |

```powershell
python -X utf8 -B sandbox/connector-channel-mocks/test_channel_mocks.py
```

Đã chạy trên CPython 3.12.3 Windows 11 AMD64, standard library và JSON fixture UTF-8. Hai lần chạy từ working directory khác nhau cho cùng case evidence. Source, fixture, test và môi trường có SHA-256 trong JSON. `LINUX_NOT_RUN` vì WSL hiện chỉ có distro `docker-desktop`, Docker ngoài quyền S2. Case-sensitive path, UTF-8 locale và digest equality liên nền tảng cần xác minh ở lần Linux riêng; không tuyên bố đã chạy Linux.

## Ranh giới ENG-01B

S2 không tạo job, dispatcher hoặc receipt. Đọc lại fixture là phép đọc xác định. S1 job/idempotency và outbox/receipt là điểm nối ghim tại `79dfe8a`; PR #10 cần vào main trước delta tích hợp. Logic deadline 504 hiện là mô phỏng có chủ đích, với 0 dispatch và 0 retry. [Contract và đường dẫn tích hợp](../sandbox/connector-channel-mocks/README.md).

ENG-01B cần chốt auth/OAuth scope GA4, compatibility dimension/metric, quyền read-only Woo, API version/locale WordPress, quota/rate limit, consent/retention, pricing và quyền owner. `REAL_GA4_UNTESTED / REAL_WP_WOO_UNTESTED`. Không đánh giá plugin /vi/ live, không đọc tài khoản hoặc dữ liệu khách hàng.

**Handoff:** PR riêng nhánh `codex/eng-01a-s2-fake-channel-adapters-2026-11-23` vào main. ChatGPT Điều phối nghiệm thu source/evidence. Runtime dùng 0 network requests, 0 provider calls, 0 USD, 0 KVM2/production operations. Paid Gate B giữ `BLOCKED_PREFLIGHT`.
