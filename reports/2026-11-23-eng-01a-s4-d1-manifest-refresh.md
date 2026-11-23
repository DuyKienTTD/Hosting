---
id: report-2026-11-23-eng-01a-s4-d1-manifest-refresh
type: report
status: ready_for_review
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
source: exact-head-work-qa-and-local-offline-delta
---

# ENG-01A-S4-D1 — Refresh manifest theo S3-D1

| Mục | Kết quả |
| --- | --- |
| TASK / AGENT / ACK_PHASE_B | `ENG-01A-S4-D1` / Codex / EXECUTE theo comment `7091621291`. |
| BASE_SHA / PR21_BASE | Main và rule commit `e385c1bea2070973e3007e5717f7e980348d6ab3`, workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. PR #21 trước delta `761e9545d2fcca8f359513b9918d0a6bb4aef776`. |
| PR19_APPROVED_SHA | `17ac45c1350776614e00ef0e14bdaf52b382b6ba`, đúng HEAD Work xác nhận `S3_D1_INDEPENDENT_QA_PASS_WITH_LIMITS`. |
| MANIFEST_DIFF | Cập nhật HEAD S3 và ba blob của README, bridge và runner. Giữ 12 đường dẫn, base tree, policy và pin S1/S2. Runbook Linux đọc pin S3 từ manifest. |
| ACTUAL_TEST_DELTA | Windows 11 AMD64, CPython 3.12.3, SQLite 3.45.1. 3/3 test S4, 4/4 test recovery S3-D1 tại đúng HEAD. Checker xác minh 12 blob, hai lần assembly khớp digest và từ chối manifest cũ trước khi tạo thư mục đích. |
| ASSEMBLY_DIGEST | SHA-256 quan sát từ hai assembly độc lập `57d930a7d45cf695cd25bd372a9057a64bf7786d62b83134548dc7d9c0528119`. Digest manifest canonical `fa224e4608339b4944190c17d5d3c600b29c58d655551173a11cb06143df2887`. |
| MERGE_PREVIEW | `main → #10 → #13 → #19` cho tree `00e7c4de7d97f1e171606dfcf9775b69fe84a3b8`, không conflict và 12 blob chức năng khớp. CATALOG và PR #6 còn lệch về nội dung. |
| EVIDENCE | [Kết quả chi tiết](evidence/2026-11-23-eng-01a-s4-d1-manifest-refresh.json) · [Manifest](../sandbox/connector-release/manifest.json). |
| VERDICT | `ENG01A_S4_D1_MANIFEST_REFRESH_PASS_OFFLINE_LINUX_NOT_RUN`. `REAL_CONNECTOR_UNTESTED`. |
| NEXT_OWNER | ChatGPT Điều phối nhận [PR #21](https://github.com/DuyKienTTD/Hosting/pull/21) và kiểm HEAD/diff D1. |

[Chỉ thị Giai đoạn B](https://github.com/DuyKienTTD/Hosting/pull/21#issuecomment-7091621291) · [Giai đoạn A](https://github.com/DuyKienTTD/Hosting/pull/21#issuecomment-7091484845) · [QA độc lập của Work](https://github.com/DuyKienTTD/Hosting/pull/19#issuecomment-7091488222)

## Evidence reuse và delta

Báo cáo S4 gốc và kết quả 7/7 ở `761e954` được giữ nguyên làm lịch sử. Test S4 lần này bao phủ drift, kiểm runtime fixture không dùng live transport và receipt 504 giữ nguyên sau khi mở lại datastore từ assembly mới. Kiểm thêm đúng manifest S4 cũ bị từ chối. Bốn ca S3-D1 chạy từ worktree tạm ở commit đã được Work duyệt, với S1 `79dfe8a` và S2 `0235b5f` trích từ local Git objects. Exception trước settle và process exit 86 trong transaction đều phục hồi unknown với result digest null. Exit sau commit outbox giữ kết quả 504 hợp lệ. Exit sau receipt và trước ACK giữ receipt và callback để replay. Không chạy lại suite lịch sử.

## Đề xuất đối chiếu metadata

- `CATALOG.yaml` thiếu task/report/evidence S3/S4 và các báo cáo D1. Sau khi file xuất hiện trên base mục tiêu, đề xuất Codex là writer duy nhất cho CATALOG và `CHANGELOG.md` theo một lượt giao riêng. CATALOG thêm các đường dẫn đã có, CHANGELOG ghi verdict và đúng SHA theo từng mốc.
- Đề xuất ChatGPT Điều phối sở hữu verdict trong `STATE.md` và dòng ENG-01A trong PR #6. STATE phân biệt nghiệm thu offline, `LINUX_NOT_RUN` và `REAL_CONNECTOR_UNTESTED`. Dòng `NO_TASK_YET` cần trỏ tới task đã có. Preview không phát hiện ID trùng hay link index tương đối bị thiếu.
- Thứ tự đề nghị là duyệt S1, refresh S2 trên main sau khi được phép, rồi xác minh lại S3/S4 theo các HEAD đã duyệt. Mọi thay đổi pin hoặc base đều phải kiểm lại manifest và preview. Phạm vi lượt này chỉ có PR #21, không có thay đổi shared metadata.

Kết quả giới hạn ở local fixture Windows. WSL chỉ có Docker Desktop đã dừng. Không dùng runner đó hoặc GitHub Actions. Paid Gate B vẫn `BLOCKED_PREFLIGHT`, AI-03 vẫn `NO_GO_CURRENT_PREFLIGHT`.
