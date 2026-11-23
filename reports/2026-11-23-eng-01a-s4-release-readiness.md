---
id: report-2026-11-23-eng-01a-s4-release-readiness
type: report
status: ready_for_review
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
source: local-sandbox-tests-and-git-merge-tree
---

# ENG-01A-S4 — Manifest và merge readiness offline

| Mục | Kết quả |
| --- | --- |
| TASK / AGENT | `ENG-01A-S4` / Codex |
| ACK / BASE_SHA | `EXECUTE ENG-01A-S4` theo comment `7091188510`. Quy tắc và baseline `e385c1bea2070973e3007e5717f7e980348d6ab3`, blob workflow `69ec0db902f457f06dd547dae171220331df0f5e`. |
| S1 / S2 / S3 | PR #10 `79dfe8aae5c30d4e896c29333e0296ada1671b7e`, PR #13 `0235b5f9bb38d0d7e99a600188705d50977527f5`, PR #19 `c343f7dded47a67e385ab05b8bb46aed88444f15`. |
| LINUX_EXECUTED_OR_NOT | `LINUX_NOT_RUN`. WSL chỉ có distro Docker Desktop đã dừng. Truy vấn inventory Hyper-V không thành công. Không tìm được runner Linux local độc lập trong các công cụ đã kiểm tra hoặc workflow sẵn có trên `main`. |
| TEST_DELTA | 7/7 S4 qua trên Windows 11 AMD64, CPython 3.12.3, SQLite 3.45.1. Hai assembly từ 12 Git blob có cùng SHA-256. |
| MERGE_PREVIEW | `CLEAN_TEXT_PREVIEW`, tree `d499e07ed390071156fe9cbb75b6770a5ef3fbe1`, đủ 12 blob chức năng. Có lệch giữa nội dung kế hoạch, catalog và nghiệm thu offline. |
| EVIDENCE | [JSON](evidence/2026-11-23-eng-01a-s4-release-readiness.json), [manifest](../sandbox/connector-release/manifest.json), [lệnh Linux](../sandbox/connector-release/README.md). |
| VERDICT | `ENG01A_S4_MANIFEST_READY_LINUX_NOT_RUN` / `S4_RELEASE_MANIFEST_READY_LINUX_UNTESTED`. |
| BLOCKERS | Thiếu runner Linux local cô lập đã xác minh. Chạy S3 delta theo runbook để đóng phần xác minh Linux. |
| PR_URL / NEXT_OWNER | [PR S4](https://github.com/DuyKienTTD/Hosting/pulls?q=is%3Apr+head%3Acodex%2Feng-01a-s4-linux-release-readiness-2026-11-23) → ChatGPT Điều phối, Work QA khi có slot. |

[Chỉ thị, nghiệm thu S3 và giới hạn](https://github.com/DuyKienTTD/Hosting/pull/19#issuecomment-7091188510)

## Evidence reuse và kiểm thử delta

Kết quả offline Windows S1 8/8, S2 7/7, S3 8/8 ở các SHA trên vẫn là bằng chứng cho hành vi đã nghiệm thu. Kiểm delta S4 vì có đường kiểm manifest và assembly mới. Các trường hợp từ chối sai baseline, HEAD, digest, path, policy và JSON trùng khóa đều đạt. Khi tracking ref thay đổi trong phép mô phỏng, checker từ chối capture. Assembly không chấp nhận tệp thừa, byte bị sửa hoặc ghi đè đích có sẵn. Hai lần trích xuất Git blob cho cùng digest `a2ea777f2ea051ff69d75415e36920757e891f772545cb3e98521b19d42701d7`.

S1 dùng `channel=fixture`. Bridge S3 chọn mock S2 theo operation, qua đó tuyến thử có đúng một fake dispatch ở S1 và một synthetic read ở S2. Với fixture GA4 `delayed`, kết quả là HTTP 504, không có rows và có receipt `outcome_unknown`. Gửi lại intent và xử lý lại sau khi mở Bridge trên cùng datastore trả về cùng job và receipt. Settlement đến muộn bị từ chối vì native job đã rời trạng thái `working`. Bridge chỉ đọc S2 tại checkpoint sau khi claim dispatch, còn S1 trả snapshot cho job đã kết thúc. Bằng chứng áp dụng cho fixture và không chứng minh exactly-once ở provider. Audit import, URL literal và socket audit hook chỉ áp dụng cho fixture đã kiểm.

## Rà tương thích Windows / Linux

| Bề mặt | Rủi ro và cách xác minh |
| --- | --- |
| Đường dẫn, chữ hoa/thường và byte | Manifest dùng path POSIX đã chuẩn hóa, từ chối path mơ hồ theo casefold. Trích xuất qua Git blob tránh chuyển LF/CRLF theo thiết lập checkout. Hai assembly có cùng digest trên Windows. |
| SQLite và file lock | Windows fixture quan sát `state.sqlite` và `worker-lock.sqlite` ở journal mode `delete`. S1 dùng `BEGIN IMMEDIATE` và `PRAGMA synchronous=FULL` trong transaction. Trên Linux cần kiểm lock/recovery trên filesystem local và ghi rõ phiên bản SQLite. Bằng chứng crash process không đánh giá mất điện hoặc độ bền storage backend. |
| Process và exit | S3 khởi chạy interpreter bằng `sys.executable` và cố ý `os._exit(86)` trong hai ca crash. Không phụ thuộc fork hay shell. Giữ nguyên exit code và xác minh recovery trên Linux để bao phủ khác biệt process/lock. |
| Deadline, locale, dữ liệu | Fixture dùng tick nguyên tính theo ms, UTF-8, output canonical và tiền tệ theo đơn vị nhỏ nhất dạng số nguyên. Chuỗi ngày và thứ tự mẫu do fixture kiểm soát. Runbook ép UTF-8 và kiểm lại digest từ blob. |
| Phân quyền và cleanup | Assembly chỉ ghi vào root riêng mới tạo. Fixture Linux dùng `umask 077` và thư mục tạm mode `0700`; kiểm fixture trống sau khi worker kết thúc. Phép kiểm này chưa chạy trên Linux. |

## Merge readiness

- Ba bước `main → #10 → #13 → #19` qua `git merge-tree` không có conflict chức năng, conflict ở `CATALOG.yaml` / `STATE.md` / `CHANGELOG.md`, hay conflict khác. Không phát hiện trùng ID catalog hoặc link tương đối mới bị thiếu trong các index được kiểm. Cả ba PR còn mở và chưa có review decision trên GitHub tại thời điểm đối chiếu.
- PR #6 tại `03fb56b6d3b4f42a1cb65c6e3c87a19099785044` còn ghi `NO_TASK_YET` cho ENG-01A và chưa nhắc S3. Sau preview, task S1 và S2 vẫn mang `ready_for_review`. Task, report và evidence S3 đã có trong tree nhưng chưa có mục tra cứu trong CATALOG.
- Đề xuất cho owner sau review là cập nhật dòng ENG-01A trong plan bằng các task và SHA đã review, bổ sung mục CATALOG cho S3/S4 và ghi riêng trạng thái nghiệm thu offline và sẵn sàng triển khai trong STATE/CHANGELOG. Thứ tự đề nghị là duyệt S1, refresh S2 theo `main` mới, rồi kiểm lại S3/S4 và ghim manifest theo HEAD đã duyệt. Nếu SHA hoặc tree thay đổi, kiểm lại pin, merge preview và chỉ chạy các test bị ảnh hưởng. Việc thử Linux là điều kiện của verdict Linux.

`LIVE_ENABLED=False`, `MOCK_ONLY`, `BACKEND_PRODUCTION_NOT_READY`, `REAL_CONNECTOR_UNTESTED`. Gate B paid giữ `BLOCKED_PREFLIGHT`. Phạm vi tác động của S4 là fixture tạm, Git local và PR riêng. `read_complete=true`, `handoff_state=PREPARED_FOR_OWNER_FORWARD`, `next_owner=ChatGPT Điều phối`.
