---
id: eng-01a-s3-integration-and-merge-preview-report
type: report
status: current
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
task_id: eng-01a-s3-offline-integration
owner: codex
---

# ENG-01A-S3 — Tích hợp offline S1/S2

| TASK | AGENT | BASE_SHA | SOURCE_SHAS | ACK_EXECUTE | ACTUAL_TEST_DELTA | MERGE_PREVIEW | EVIDENCE | VERDICT | BLOCKERS | NEXT_OWNER |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENG-01A-S3 | Codex | `e385c1b` | S1 `79dfe8a`, S2 `0235b5f` | 23/11/2026 ICT, chỉ thị `7091064405` | 8/8 phương thức S3 trên Windows | `CLEAN_PREVIEW`, không xung đột | [JSON](evidence/2026-11-23-eng-01a-s3-integration.json) | `ENG01A_S3_OFFLINE_INTEGRATION_PASS` | Không có trong scope offline. `LINUX_NOT_RUN / REAL_CONNECTOR_UNTESTED`. | ChatGPT Điều phối |

ACK quy tắc ở main `e385c1bea2070973e3007e5717f7e980348d6ab3`, Workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. Đã đối chiếu PR #6 `03fb56b`, D1 PR #7 `d4962a4`, BIZ-01 `8c821bb` và source/evidence của hai PR gốc. Không thấy S3 trùng trước khi bắt đầu. PR riêng vào main chỉ chứa package thí nghiệm, task, report và evidence. [Chỉ thị](https://github.com/DuyKienTTD/Hosting/pull/13#issuecomment-7091064405) · [Task](../tasks/2026-11-23-eng-01a-s3-offline-integration.md).

## Tích hợp và kết quả

Harness xuất hai module và fixture JSON vào thư mục tạm từ object Git ghim. Xác minh blob khi copy và trước mỗi lần import. S3 intent v1 ánh xạ ba operation allowlist vào S2, giữ engine S1 cho admission, worker lock, fake dispatch, settlement, outbox và receipt. Native S1 vẫn `channel=fixture` và payload mode cố định. SQLite fixture thêm một bảng mapping để giữ key public và digest đủ của intent, claim đọc và kết quả chuẩn bị. Callback/receipt dùng identity native. S3 kèm digest binding intent/result riêng trong local view sau ACK. [Contract và bảng tương thích](../sandbox/connector-integration/README.md).

| Ca S3 | Kỳ vọng và quan sát |
| --- | --- |
| GA4 và idempotency | Đọc thật bằng code S2 ghim, đạt 3 dòng aggregate. Canonical digest không đổi khi đảo thứ tự key. Replay 200 giữ cùng job/receipt, payload khác cùng key trả 409. |
| WP/Woo | Đọc danh sách product hai trang ở EN/VI và chi tiết page VI. Cùng snapshot đọc lại cho cùng dữ liệu. USD/VND và minor units được giữ nguyên. |
| Lỗi S2 | 403/429/404/422 ghi failed receipt. 504 logic ghi unknown receipt. Không có cursor/watermark mới hoặc retry sau lỗi. Cursor ban đầu vẫn đọc đúng trên snapshot cũ. |
| Deadline S1 | Job chưa chạy đến hạn ghi unknown, 0 fake dispatch, 0 S2 read, đúng một receipt. |
| Callback/receipt | Callback gắn digest sai bị từ chối dù tính lại callback ID. Replay callback gốc trả receipt đã commit. Binding S3 khớp digest request và result. |
| Crash sau S2 read | Child thoát mã 86 ở `working`, trước khi commit receipt. Worker mới trên cùng SQLite chốt `outcome_unknown`, không trả output vừa đọc, giữ một fake dispatch/một S2 read/một receipt. Late settlement bị từ chối. |
| Crash sau receipt trước ACK | Child thoát ở `sending` khi receipt đã commit. Worker mới giữ đúng callback và receipt, thêm ACK, không đọc lại S2. |
| Offline/provenance | Từ chối request không được duyệt, route ghi, budget ngoài cap, endpoint và credential. Blob fixture đổi bị từ chối. Test socket audit không mở kết nối. Output giữ `MOCK/SYNTHETIC` và không thêm dữ liệu cá nhân. |

Môi trường CPython 3.12.3, SQLite 3.45.1, Windows 11 AMD64. Evidence kèm observed/expected, PID/exit code, trace audit và SHA nguồn/môi trường. Không chạy lại suite lịch sử. `LINUX_NOT_RUN` vì WSL chỉ liệt kê distro Docker Desktop. Kết quả chỉ chứng minh crash tiến trình với fixture SQLite. Không chứng minh power loss, external delivery hoặc exactly-once trên provider network.

## Merge preview

| Thành phần | Quan sát tại base `e385c1b` |
| --- | --- |
| `CATALOG.yaml` | Không conflict. Tree dự kiến giữ entry task, report và evidence của cả hai gói. |
| `STATE.md` | Không conflict. Hai dòng kết quả offline ở vị trí riêng; merge preview giữ cả hai. |
| `CHANGELOG.md` | Không conflict. Giữ cả hai entry ngày 23/11. |
| Mã chức năng | Không conflict. Cả hai package trong tree dự kiến khớp byte với heads tương ứng. |

`git merge-tree --write-tree` trong detached worktree tạm trả tree `d2e23b3d0c9eaf41a9b3384823cab6da60424b98`. Worktree đã dọn, refs không đổi. JSON có diff metadata đề xuất chính xác ở trường `merge_preview.proposed_metadata_diff`. Đề xuất review S1 trước, refresh main rồi đối chiếu lại merge preview của S2, giữ cả hai bộ entry, sau đó review S3. Không commit merge hoặc sửa PR #10/#13.

**Handoff:** ChatGPT Điều phối nghiệm thu phạm vi offline. 0 runtime network requests, KVM2/production operations, provider calls và USD. Paid Gate B giữ `BLOCKED_PREFLIGHT`.
