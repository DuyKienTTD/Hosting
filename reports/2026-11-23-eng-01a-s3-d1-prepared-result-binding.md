---
id: report-2026-11-23-eng-01a-s3-d1-prepared-result-binding
type: report
status: ready_for_review
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
source: offline-fixture-and-pinned-git-objects
---

# ENG-01A-S3-D1 — Liên kết kết quả đọc với native settlement

| Mục | Kết quả |
| --- | --- |
| TASK / AGENT / ACK_EXECUTE | `ENG-01A-S3-D1` / Codex / ACK thực thi theo comment `7091356418`. |
| BASE_SHA / SOURCE_SHAS | PR #19 `c343f7dded47a67e385ab05b8bb46aed88444f15`, S1 `79dfe8aae5c30d4e896c29333e0296ada1671b7e`, S2 `0235b5f9bb38d0d7e99a600188705d50977527f5`. Quy tắc tại `main@e385c1bea2070973e3007e5717f7e980348d6ab3`, workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. |
| FINDING_S3-QA-01 | Tái hiện trên mã gốc. Khi lỗi xảy ra sau commit prepared result 504 và trước native settle, recovery vẫn công bố orphan result vì hai outcome cùng `outcome_unknown`. |
| REPAIR_INVARIANT | Chỉ trả kết quả sau ACK khi liên kết theo job khớp cả digest native outbox và digest bytes của kết quả. Thiếu hoặc sai liên kết thì `result` và `result_sha256` đều null. |
| ACTUAL_TEST_DELTA | 11/11 trên Windows 11 AMD64, CPython 3.12.3, SQLite 3.45.1. Bốn ca mới, bảy ca S3 chịu tác động. `LINUX_NOT_RUN`. |
| EVIDENCE | [Kết quả chi tiết](evidence/2026-11-23-eng-01a-s3-d1-prepared-result-binding.json). |
| VERDICT | `ENG01A_S3_D1_PREPARED_RESULT_BINDING_PASS` trong fixture offline. |
| PR19_HEAD / S4_STALE_STATUS | [Commit D1 ở PR #19](https://github.com/DuyKienTTD/Hosting/pull/19/commits) là đối tượng cần QA lại. [PR #21](https://github.com/DuyKienTTD/Hosting/pull/21) giữ pin S3 cũ, trạng thái `STALE_AFTER_S3_D1`. |
| NEXT_OWNER | ChatGPT Điều phối chuyển Work kiểm tra độc lập trên HEAD D1. S3/S4 vẫn `BLOCKED_QA_DELTA` cho đến khi có nghiệm thu. |

[Chỉ thị D1](https://github.com/DuyKienTTD/Hosting/pull/19#issuecomment-7091356418) · [Finding độc lập của Work](https://github.com/DuyKienTTD/Hosting/pull/19#issuecomment-7091266578)

## Transaction và tương thích

S1 lấy lock tại `worker-lock.sqlite` trước khi chạy job. Trong khi giữ lock, S3 claim lượt đọc rồi commit `prepared_result` vào `state.sqlite`. Khi S1 settle lượt đọc đó qua `tx()`, S3 đối chiếu bytes đã prepare và dùng cùng transaction để ghi bảng `s3_settled_results`. Bảng chỉ có một liên kết theo job giữa SHA-256 của native outbox và SHA-256 của kết quả canonical. Đường ghi chỉ dùng INSERT. Recovery vào từ trạng thái `working` không có kết quả in-memory vừa đọc nên settle unknown mà không tạo liên kết. Nếu native settlement đổi outcome do deadline, bridge không gắn kết quả có outcome khác.

`worker-lock.sqlite` giữ lock và không tham gia commit dữ liệu. Không có cửa sổ commit riêng giữa outbox và liên kết. Exit khi cả hai đã được ghi nhưng trước commit rollback cả hai. Exit sau commit và trước receipt giữ nguyên outbox và liên kết để worker mới xử lý callback/receipt. Exit sau receipt và trước ACK giữ cả kết quả, outbox và receipt cho lần ACK kế tiếp.

Các field của contract v1 giữ nguyên. Fixture cũ được tạo thêm bảng khi mở; các kết quả thiếu liên kết đáng tin cậy không được backfill. Khi liên kết không hợp lệ, bridge trả native state và receipt đã xác minh, cùng `result=null` và `result_sha256=null`. Hash ở đây kiểm tính toàn vẹn trong fixture local. Fixture không chứng minh exactly-once ở hệ thống ngoài hoặc độ bền khi mất điện.

## Delta đã chạy

- Dùng SQLite tạm, GA4 synthetic `delayed`, deadline 20, process tick 1. Tiêm exception đúng seam Work trước S1 settle. Trước recovery, prepared trả 504, native vẫn `working`, chưa có callback hoặc receipt. Sau recovery tick 2 có một dispatch, một synthetic read, một receipt và hai trường kết quả đều null. Cùng request giữ job và replay ổn định. Settlement đến muộn bị từ chối.
- Exit 86 trong transaction settle rollback cả outbox và liên kết. Ca 504 thông thường trả kết quả đúng; exit 86 sau commit và trước receipt phục hồi cùng outbox, result digest và một receipt. Ca đọc thành công exit 86 sau receipt và trước ACK giữ nguyên callback, receipt và kết quả sau recovery.
- Liên kết sai digest event, bytes kết quả bị đổi, JSON lỗi và fixture cũ thiếu liên kết đều bị chặn công bố kết quả. GA4/WP/Woo, replay/409, callback mismatch, deadline, 403/429/404/422 và crash sau đọc trước khi prepare vẫn qua.

Không tìm thấy runner Linux local cô lập trong lượt kiểm tra WSL; distro Docker Desktop không được dùng. Suite lịch sử S1/S2/S4 và ca S3 chỉ kiểm endpoint/fixture pin không được chạy lại. Phạm vi ghi gồm bridge, test, README và hai hồ sơ mới trong PR #19. KVM2, production, connector thật và API trả phí nằm ngoài lần chạy; Gate B paid giữ `BLOCKED_PREFLIGHT`.
