---
id: report-2026-11-23-codex-gov02-s2-merge-readiness
type: report
status: ready_for_review
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
source: pinned-pr-trees-and-source-acceptance
---

# GOV-02/S2 Giai đoạn A — Kế hoạch reconciliation metadata

**Kết quả** `GOV02_S2_RECONCILIATION_PLAN_READY_FOR_REVIEW`. ACK EXECUTE GOV-02/S2 PHASE A. Main và rule commit `e385c1bea2070973e3007e5717f7e980348d6ab3`, workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. Nguồn S1 là PR #28 tại `6dafae50bd17bc1a18080b13b86c5b8c35573580`. [Chỉ thị Giai đoạn A](https://github.com/DuyKienTTD/Hosting/pull/28#issuecomment-7092005693)

## Phạm vi và kết quả đối chiếu

Đã đối chiếu HEAD, tree, base và file list GitHub với Git local cho 14 PR. Mọi HEAD trong ledger S1 còn khớp, nhưng phạm vi lịch sử mang nhãn `DELTA_REQUIRED` vì #27, #28 và #29 nằm ngoài snapshot S1. Phép đối chiếu chỉ bao phủ các nguồn đã liệt kê. Danh sách 40 mục chứa canonical path, proposed ID, source HEAD/blob, owner, executor, nhãn và hành động cho từng tệp. Tất cả path đều hiện diện tại HEAD nguồn, còn thiếu trên main và trong tập CATALOG đã đối chiếu. [Evidence và ledger nguồn](evidence/2026-11-23-codex-gov02-s2-merge-readiness.json)

| Nhóm | Mục | Hành động dự kiến |
| --- | --- | --- |
| Finding S1 | 24 đường dẫn từ #16/#19/#20/#21/#22/#23/#24/#25 | 23 mục có thể đề xuất lập chỉ mục khi đã có mặt trên base được duyệt. Giữ riêng report #24 chờ owner giải quyết ID. |
| Hồ sơ bổ sung | 16 đường dẫn | #6 có một plan; #19 và #21 có bốn report/evidence lịch sử; #27 có bốn hồ sơ A0; #28 có ba hồ sơ validator; #29 có bốn hồ sơ gồm runbook. |
| OPS-01A/S2 | Task và report có ID `ttd-hostinger-ops01a-s2-lifecycle-2026-11-23` | Giữ ID task. Đề xuất report ID `ttd-hostinger-ops01a-s2-lifecycle-2026-11-23-report` cho Hostinger xác nhận. Chỉ lập mục report sau khi có quyết định xử lý nhất quán giữa front matter và CATALOG trong lượt riêng. Work yêu cầu D1, nên giữ `INDEPENDENT_QA_PENDING` cho lần re-QA. |
| SEC-02/S2 | PR #29 `d3d6a2690cb3b08609d8708514c5594c0ebdd3e6` | Canonical report `reports/2026-11-23-hostinger-sec02-s2-tabletop.md`. Ghi Hermes WebUI là executor của tabletop, Hostinger Agent là owner được chỉ định và chưa ACK. Báo cáo và evidence chỉ dùng cho thiết kế, các work order vẫn `NOT_AUTHORIZED`. |
| GOV-01/S2 | PR #27 `b8c64655f4d6cd9c309fb2501ce58207c9b3c1db` | Đăng ký task, report, register và evidence riêng. Cả A0-1 đến A0-5 giữ `A0_PENDING`; khuyến nghị còn `PROPOSAL_NOT_APPROVED`. Quyền GA4 và consent cần quyết định riêng. |

Nguồn phân định trách nhiệm và trạng thái gồm [OPS D1](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7091997554), [SEC owner gate](https://github.com/DuyKienTTD/Hosting/pull/29#issuecomment-7092009189) và [hồ sơ A0](https://github.com/DuyKienTTD/Hosting/pull/27#issuecomment-7091925689).

## Kế hoạch index và một writer cho mỗi file

| Đích | Writer duy nhất | Thay đổi dự kiến sau gate |
| --- | --- | --- |
| `CATALOG.yaml` | Codex theo write set được duyệt riêng | Lập mục theo ID/path và loại task, report, evidence hoặc runbook trong ledger. Trong số 40 mục, 39 có thể xét khi có mặt trên base, còn report #24 giữ chờ owner. Giữ sáu mục S1/S2 đã có trong source diff #10/#13. |
| `CHANGELOG.md` | Codex theo write set được duyệt riêng | Ghi một mục cho lần reconciliation, liên kết report và SHA, bảo toàn các mốc lịch sử. |
| `STATE.md` | ChatGPT Điều phối | Ghi quyết định hiện thời và gate còn mở. Giữ UX browser, OPS live và connector thật ở mức chưa xác minh. |
| PR #6 | ChatGPT Điều phối | Sửa 5 dòng `NO_TASK_YET` đã phát hiện ở HEAD `03fb56b6d3b4f42a1cb65c6e3c87a19099785044`: BIZ-02 dòng 66 → #20/#25, UX-01 dòng 67 → #16, ENG-01A dòng 68 → #10/#13/#19/#21, GROW-02A dòng 71 → #23, OPS-01A dòng 73 → #22/#24. Dòng GOV-02 số 54 là phát hiện bổ sung, trỏ tới task #28 khi được duyệt. Dùng link PR hoặc commit đã ghim trong thời gian task chưa vào main. |

`DRAFT` ghi mức bản nháp. `SOURCE_ACCEPTED` ghi mức đã nhận hoặc nghiệm thu nguồn trong phạm vi đã công bố và có thể cùng tồn tại với `DRAFT`. `INDEPENDENT_QA_PENDING` ghi còn chờ QA hoặc re-QA của đúng HEAD. `LINUX_NOT_RUN` áp dụng cho tuyến release S4. `A0_PENDING` và `REAL_UNTESTED` giữ riêng quyết định kinh doanh và bằng chứng vận hành thực tế. Các nhãn này không cấp quyền triển khai.

Giữ folder và canonical path của PR nguồn. Thứ tự đề xuất sau phê duyệt là review #10 → cập nhật preview #13 trên main mới → #19 → #21 với pin được kiểm lại. PR #10 và #13 đều sửa CATALOG, STATE và CHANGELOG. Thu nhận hai diff theo thứ tự và đối chiếu nội dung của cả hai sau từng bước. Chỉ mở PR metadata riêng trên base có các path cần thêm. Điều phối cập nhật STATE và PR #6 theo cùng snapshot, tránh hai writer đụng cùng file trong thời gian source PR đang được review. #24 D1, #27 A0 và #29 owner review có gate riêng. Kế hoạch không yêu cầu viết lại code các PR gốc.

Nếu HEAD, blob, owner hoặc mục đích thay đổi, khoanh scope bị lệch và refresh evidence trước khi đề xuất patch. Nếu patch metadata sau này gây sai link hay sai trạng thái, đề xuất revert đúng commit metadata qua PR đã phê duyệt, giữ nguyên nguồn và bằng chứng lịch sử.

## Test delta đề xuất cho Giai đoạn B

| Ca âm | Kết quả phải thấy |
| --- | --- |
| Đổi HEAD hoặc một blob nguồn, kể cả nguồn bị mất | Báo drift hoặc source unavailable và dừng áp dụng mục tương ứng. |
| Thêm link cho path mới chỉ có ở source PR, thiếu trên base đích | Từ chối lập mục hoặc giữ chờ. |
| Dùng lại ID report #24 hoặc gỡ hold khi owner chưa xác nhận | Từ chối duplicate hoặc premature publish. |
| Hai package có task ID khác nhau nhưng dùng chung report/front matter ID trên hai canonical path | Phát hiện va chạm xuyên package. Cùng path xuất hiện ở nhiều snapshot chỉ được tính một lần. Đây là regression bắt buộc của `GOV02-QA-01`. |
| Giữ `NO_TASK_YET` khi đã có task, hoặc để hai lượt cùng ghi shared file | Báo stale/double writer dù diff văn bản có thể sạch. |
| Đổi `DRAFT`, `INDEPENDENT_QA_PENDING`, `LINUX_NOT_RUN`, `A0_PENDING` hoặc `REAL_UNTESTED` thành approval/production-ready | Từ chối trạng thái nâng vượt bằng chứng; `SOURCE_ACCEPTED` không đóng các gate. |
| Gán executor #29 cho Hostinger hoặc ghi một work order đã được cấp quyền | Từ chối provenance và approval sai; giữ Hermes tabletop và Hostinger owner gate. |

Ca dương kiểm mỗi ID duy nhất, tất cả path đã có trên đúng base, đúng SHA và một writer mỗi file. Giai đoạn A chỉ chạy đối chiếu nguồn và các bất biến của kế hoạch. Các ca âm/dương trên patch còn chờ Giai đoạn B. Không chạy lại bộ test S1.

**Bàn giao** ChatGPT Điều phối nhận kế hoạch trên draft PR. Work trả `NEEDS_CODEX_DELTA` tại PR #28 HEAD `6dafae50bd17bc1a18080b13b86c5b8c35573580` vì validator bỏ sót ID front matter trùng giữa hai package. Đối chiếu bổ sung trên tập tài liệu đã ghim của kế hoạch chỉ thấy cặp OPS-01A/S2 đã được giữ chờ. Giai đoạn B vẫn `BLOCKED_PENDING_INDEPENDENT_QA_AND_COORDINATOR_APPROVAL`. Điều phối cần giao riêng việc sửa `GOV02-QA-01`, nhận Work PASS trên HEAD đã sửa được duyệt, rồi phê duyệt write set của Giai đoạn B. [Verdict QA độc lập](https://github.com/DuyKienTTD/Hosting/pull/28#issuecomment-7092060267)
