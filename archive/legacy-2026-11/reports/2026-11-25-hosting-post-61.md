---
id: hosting-post-61-report-2026-11-25
type: report
status: draft
owner: Chat Dieu phoi
task_id: HOSTING-POST-61
lifecycle: DURABLE
updated_at: 2026-11-26
verified_at: 2026-11-26
sensitivity: public-redacted
---
# HOSTING-POST-61 — Báo cáo kết quả

[Đặc tả pin](https://github.com/DuyKienTTD/Hosting/blob/cbb60147caed49467d76c71b84139e00b4fd3e61/tasks/hosting-post-61.md) · [Kế hoạch](../program/hosting-post-61/README.md) · [Trạng thái chuẩn](../program/hosting-post-61/WORK_ITEMS.md)

PR #61 mở dạng nháp tại lần đọc đầu, nhánh `coordinator/hosting-mkoe-01` → `main`, HEAD `d7b2cc9bb2e458e31d334b362bffc40eae329ed2`. FIX-F4 đưa HEAD lên `c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb`. GitHub Actions **Data integrity** tại HEAD sau sửa báo success. PR #61 đã merge vào `main`. Xem bằng chứng POST-01 bên dưới. [PR #61](https://github.com/DuyKienTTD/Hosting/pull/61) · [CI của HEAD sau sửa](https://github.com/DuyKienTTD/Hosting/actions/runs/45590897631).

| Mục | Trạng thái | Kết quả và nguồn |
| --- | --- | --- |
| FIX-F4 | DONE | Dòng 11 thêm preflight L57–L59 và sửa endpoint H5/H6 từ 719 thành 718. Nguồn pin vẫn có 718 dòng và giữ cùng blob. [Chỉ mục](https://github.com/DuyKienTTD/Hosting/blob/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb/rules/GATE-B-INDEX.md#L11) · [Nguồn L57–L59](https://github.com/DuyKienTTD/Hosting/blob/097c080cc6d7fb3ca36b1849d9c10375d5cbd67f/tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md#L57-L59) |
| POST-01 | DONE | PR #61 đã tích hợp vào `main`. [Merge commit](https://github.com/DuyKienTTD/Hosting/commit/f9dcdb5299489099add2d7d5e0263e0b81f4d12c) · [CI main](https://github.com/DuyKienTTD/Hosting/actions/runs/45677702167) · [Bằng chứng POST-01](#post-01--tích-hợp-main-và-ci) |
| POST-02 | DONE | Kiểm tám CV theo nguồn có tên vai trò và mức xác minh. Khoảng trống giữ UNKNOWN. [Danh bạ tám CV](../agents/CAPABILITIES.md) |
| POST-03 | DONE (đã chạy) | Hoàn thành 12 phiên A/B T1–T3. [Bảng chấm](../program/hosting-post-61/ab/SCORECARD.md) · [Tổng hợp A/B](#post-03--tổng-hợp-ab-read_set) |
| POST-04 | DONE | 0/56 ô đạt giảm 30% về ký tự Unicode trong phép đo định mức. [Số đo và phương pháp](#post-04--đo-read_set) |
| POST-05 | DONE | Đã đánh giá S1–S3 và vòng 1, đồng thời ghi số đo phiên POST-61 do Claude giám sát. [Đánh giá](#post-05--đánh-giá-dừng-sớm) · [Số đo phiên](#số-đo-phiên-post-61) |

## POST-01 — Tích hợp main và CI

- Merge commit của [PR #61](https://github.com/DuyKienTTD/Hosting/pull/61) và HEAD `main` tại lần đọc lại GitHub là [`f9dcdb5299489099add2d7d5e0263e0b81f4d12c`](https://github.com/DuyKienTTD/Hosting/commit/f9dcdb5299489099add2d7d5e0263e0b81f4d12c).
- Hai parent theo thứ tự là [`097c080cc6d7fb3ca36b1849d9c10375d5cbd67f`](https://github.com/DuyKienTTD/Hosting/commit/097c080cc6d7fb3ca36b1849d9c10375d5cbd67f) (main cũ) và [`c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb`](https://github.com/DuyKienTTD/Hosting/commit/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb) (candidate). Tree sau merge `2e604002dd1f5bc7c4e0ac51eb54306821a677f2` khớp candidate đã nghiệm thu. [Biên nhận nghiệm thu độc lập](https://github.com/DuyKienTTD/Hosting/pull/61#issuecomment-7171088669).
- GitHub Actions **Data integrity** trên `main`, event `push`, run [`45677702167`](https://github.com/DuyKienTTD/Hosting/actions/runs/45677702167) thành công. Claude đọc trực tiếp trên GitHub lúc 01:43 ICT ngày 26/11/2026. Phiên Điều phối POST-01 đọc lại job `integrity` và xác nhận kết quả `success`.

## POST-03 — Tổng hợp A/B READ_SET

Claude chạy và chấm 12 phiên ngày 25/11/2026, A0 hiệu chỉnh điểm. Mỗi điều kiện có sáu phiên trên ba đề T1–T3. [Cấu hình, refs và số liệu từng phiên](../program/hosting-post-61/ab/SCORECARD.md).

| Chỉ số | A | B | Kết quả đối chiếu |
| --- | --- | --- | --- |
| Hoàn thành lượt đầu | 6/6 | 6/6 | 12/12 |
| Dừng sớm | 0/6 | 0/6 | 0/12 |
| Số lần nhắc | 0 | 0 | 0 |
| Lỗi bắt buộc | 0/6 | 0/6 | 0/12 |
| Tổng thời gian đến final đầu tiên | 199 giây | 242 giây | B lâu hơn 21,6% |
| Tổng số tệp các phiên nêu đã mở | 33 | 80 | B cao hơn 142,4% |
| Tổng điểm | 21/24 | 24/24 | B cao hơn 3 điểm |

Trong mẫu này, chưa thấy chất lượng giảm ở B. Ở cả hai cặp T2, B đạt 4/4 theo quy tắc B2 về kiểm ACK, còn A đạt 3/4 do thiếu thời điểm và nguồn của R1. Kết quả T2 cho thấy B2 giúp kiểm ACK đầy đủ hơn trong các phiên thử. Với MKOE hiện tại, các phiên B nêu đã mở nhiều tệp hơn và mất nhiều thời gian hơn. Đề xuất READSET-OPT-01 nhắm vào phần tài liệu phải đọc. [PR #63](https://github.com/DuyKienTTD/Hosting/pull/63).

Số tệp do phiên tự báo. Bản tổng hợp A0 chuyển giao ghi A 31, B 80 (+158%), trong khi cộng sáu dòng A trong SCORECARD ra 33 (6 + 4 + 7 + 6 + 4 + 6). Bảng trên dùng tổng từ các dòng phiên. Chưa đo ký tự hoặc byte thực tế, nên mức giảm 30% về lượng đọc duy nhất chưa xác minh được. Mẫu nhỏ và chưa tách riêng tác động của B4.

## POST-04 — Đo READ_SET

Baseline trước MKOE là [main tại `097c080`](https://github.com/DuyKienTTD/Hosting/commit/097c080cc6d7fb3ca36b1849d9c10375d5cbd67f); candidate là [PR #61 tại `c0720d7`](https://github.com/DuyKienTTD/Hosting/commit/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb). Phép đo lấy nội dung UTF-8 thô từ hai snapshot, gồm front matter, Markdown, dòng trống và newline cuối khi có. Đếm code point Unicode và byte UTF-8 riêng. Mỗi path/range chỉ tính một lần trong mỗi ô. Một ô dùng một vai trò và một thao tác giả định; bảng định mức không cấp quyền cho tất cả vai trò. Kết quả phản ánh lượng tài liệu bắt buộc trong thiết kế, chưa có số liệu thực tế agent đã nạp/chất lượng đọc.

Mọi ô đọc `AGENTS.md`, startup của vai trò, và cùng đặc tả kiểm soát [HOSTING-POST-61](https://github.com/DuyKienTTD/Hosting/blob/cbb60147caed49467d76c71b84139e00b4fd3e61/tasks/hosting-post-61.md) (2.692 ký tự / 3.094 byte). Before dùng `agents/chatgpt.md` cho Điều phối, Work, A2; năm vai trò còn lại dùng file riêng. Candidate dùng mọi entrypoint riêng. Các khóa file lần lượt là `a0-assistant.md`, `a1.md`, `a2.md`, `codex.md`, `coordinator.md`, `hermes.md`, `hostinger.md`, `work.md` trong `agents/`. A0 là chủ dự án và nằm ngoài tám CV tác nhân. Directory/CATALOG và CV đầy đủ chỉ tra khi cần. Giả định biết đường dẫn startup từ đầu và dùng phiên đọc mới; không trừ cache.

Với C1–C6, before luôn đọc hết [Workflow nguyên khối](https://github.com/DuyKienTTD/Hosting/blob/097c080cc6d7fb3ca36b1849d9c10375d5cbd67f/rules/AGENT_WORKFLOW.md); candidate đọc [Workflow index](https://github.com/DuyKienTTD/Hosting/blob/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb/rules/AGENT_WORKFLOW.md) và các module tích lũy bên dưới. Số module 1–8 lần lượt là `authority.md`, `coordination.md`, `dispatch.md`, `execution.md`, `evidence.md`, `integrity.md`, `handoff.md`, `lifecycle.md` trong `rules/`. Các tài liệu bổ sung trong cột cuối áp dụng cả hai snapshot theo cùng phạm vi công việc. Với Trợ lý A0 ở C1, C2, C6, cộng [tiêu chuẩn thẩm định pin L35 đến hết](https://github.com/DuyKienTTD/Hosting/blob/819249e1c08875f23041502c604c47928bf1bbdc/agents/a0-assistant.md#L35) ở cả hai snapshot. C5 dùng chung chuẩn MKOE vì đề việc POST-61 chỉ định nguồn này. C6 giả định đã có quyết định cùng nội dung ở cả hai ref và chỉ đo các tệp repo được liệt kê. Các quyết định A0, telemetry phiên, runbook live, nguồn thật ngoài task kiểm soát và bằng chứng từng ca cần cộng thêm khi task thực tế yêu cầu.

| Loại việc | Module candidate | Nguồn thêm ngoài Core, role, task và Workflow |
| --- | --- | --- |
| C0 · Khởi đầu | — | — |
| C1 · Review phi Git, không ACK | 1, 2, 4, 5, 7 | — |
| C2 · Review Git + ACK | 1–7 | `rules/REPOSITORY_SECURITY.md`, `CONTRIBUTING.md` |
| C3 · Điều phối chuẩn bị dispatch ngoài KNG | 1–5, 7 | `STATE.md` |
| C4 · Ghi Git tài liệu và bàn giao | 1–7 | `rules/REPOSITORY_SECURITY.md`, `CONTRIBUTING.md` |
| C5 · Điều phối + Git + lifecycle + trạng thái | 1–8 | `rules/REPOSITORY_SECURITY.md`, `CONTRIBUTING.md`, `rules/DATA_LIFECYCLE_CONTEXT.md`, `STATE.md`, [MKOE](https://github.com/DuyKienTTD/Hosting/blob/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb/rules/HOSTING-MKOE-01.md) cùng blob cả hai |
| C6 · Review định tuyến KNG | 1–5, 7 | `STATE.md`, `program/current.json`, `program/kng/release_state.py` |

### Ký tự Unicode trước → sau (tỷ lệ giảm)

| Vai trò | C0 | C1 | C2 | C3 | C4 | C5 | C6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Trợ lý A0 | 7.787 → 8.103 (-4,1%) | 30.025 → 26.778 (10,8%) | 33.810 → 35.553 (-5,2%) | 24.513 → 22.161 (9,6%) | 23.949 → 25.692 (-7,3%) | 39.646 → 43.005 (-8,5%) | 43.550 → 41.198 (5,4%) |
| A1 | 6.832 → 7.138 (-4,5%) | 19.209 → 15.952 (17,0%) | 22.994 → 24.727 (-7,5%) | 23.558 → 21.196 (10,0%) | 22.994 → 24.727 (-7,5%) | 38.691 → 42.040 (-8,7%) | 32.734 → 30.372 (7,2%) |
| A2 | 7.050 → 6.738 (4,4%) | 19.427 → 15.552 (19,9%) | 23.212 → 24.327 (-4,8%) | 23.776 → 20.796 (12,5%) | 23.212 → 24.327 (-4,8%) | 38.909 → 41.640 (-7,0%) | 32.952 → 29.972 (9,0%) |
| Codex | 6.847 → 7.156 (-4,5%) | 19.224 → 15.970 (16,9%) | 23.009 → 24.745 (-7,5%) | 23.573 → 21.214 (10,0%) | 23.009 → 24.745 (-7,5%) | 38.706 → 42.058 (-8,7%) | 32.749 → 30.390 (7,2%) |
| Điều phối | 7.050 → 6.825 (3,2%) | 19.427 → 15.639 (19,5%) | 23.212 → 24.414 (-5,2%) | 23.776 → 20.883 (12,2%) | 23.212 → 24.414 (-5,2%) | 38.909 → 41.727 (-7,2%) | 32.952 → 30.059 (8,8%) |
| Hermes | 6.813 → 7.123 (-4,6%) | 19.190 → 15.937 (17,0%) | 22.975 → 24.712 (-7,6%) | 23.539 → 21.181 (10,0%) | 22.975 → 24.712 (-7,6%) | 38.672 → 42.025 (-8,7%) | 32.715 → 30.357 (7,2%) |
| Hostinger Agent | 6.823 → 7.136 (-4,6%) | 19.200 → 15.950 (16,9%) | 22.985 → 24.725 (-7,6%) | 23.549 → 21.194 (10,0%) | 22.985 → 24.725 (-7,6%) | 38.682 → 42.038 (-8,7%) | 32.725 → 30.370 (7,2%) |
| Work | 7.050 → 6.774 (3,9%) | 19.427 → 15.588 (19,8%) | 23.212 → 24.363 (-5,0%) | 23.776 → 20.832 (12,4%) | 23.212 → 24.363 (-5,0%) | 38.909 → 41.676 (-7,1%) | 32.952 → 30.008 (8,9%) |

### Byte UTF-8 trước → sau

| Vai trò | C0 | C1 | C2 | C3 | C4 | C5 | C6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Trợ lý A0 | 9.315 → 9.689 | 36.622 → 32.084 | 41.069 → 42.388 | 28.639 → 25.530 | 28.708 → 30.027 | 45.488 → 49.363 | 50.181 → 47.072 |
| A1 | 8.074 → 8.438 | 23.020 → 18.472 | 27.467 → 28.776 | 27.398 → 24.279 | 27.467 → 28.776 | 44.247 → 48.112 | 36.579 → 33.460 |
| A2 | 8.334 → 7.951 | 23.280 → 17.985 | 27.727 → 28.289 | 27.658 → 23.792 | 27.727 → 28.289 | 44.507 → 47.625 | 36.839 → 32.973 |
| Codex | 8.103 → 8.470 | 23.049 → 18.504 | 27.496 → 28.808 | 27.427 → 24.311 | 27.496 → 28.808 | 44.276 → 48.144 | 36.608 → 33.492 |
| Điều phối | 8.334 → 8.048 | 23.280 → 18.082 | 27.727 → 28.386 | 27.658 → 23.889 | 27.727 → 28.386 | 44.507 → 47.722 | 36.839 → 33.070 |
| Hermes | 8.044 → 8.412 | 22.990 → 18.446 | 27.437 → 28.750 | 27.368 → 24.253 | 27.437 → 28.750 | 44.217 → 48.086 | 36.549 → 33.434 |
| Hostinger Agent | 8.073 → 8.444 | 23.019 → 18.478 | 27.466 → 28.782 | 27.397 → 24.285 | 27.466 → 28.782 | 44.246 → 48.118 | 36.578 → 33.466 |
| Work | 8.334 → 7.988 | 23.280 → 18.022 | 27.727 → 28.326 | 27.658 → 23.829 | 27.727 → 28.326 | 44.507 → 47.662 | 36.839 → 33.010 |

Tỷ lệ = (trước − sau) / trước. Giảm nhiều nhất 19,9% (A2, C1). C2 và C4 tăng cho cả tám vai trò; C5 tăng đến 8,7%. Mốc 30% chưa đạt trong điều kiện đo. Khả năng đọc theo module giúp giảm ở ca review hẹp; các ca đòi gần trọn Workflow tăng độ dài do index/module và metadata. Chất lượng đầu ra được đánh giá riêng trong [kết quả A/B](#post-03--tổng-hợp-ab-read_set).

## POST-05 — Đánh giá dừng sớm

Nguồn S1–S3 là trao đổi điều tra do Claude/chủ dự án cung cấp và phần tự thuật của phiên Điều phối cũ. Nhãn `REPORTED` ghi nhận bằng chứng qua trao đổi. PR #61 và báo cáo đã lưu chỉ xác nhận diễn tiến tài liệu/GitHub, không thay log lượt chat đầy đủ. Mốc sự kiện theo ICT, 25/11/2026.

| Ca | Quan sát đã báo cáo | Đánh giá và giới hạn |
| --- | --- | --- |
| S1 · khoảng 15:20 | ACK, tra công cụ rồi trả final trước khi tạo nhánh hoặc commit. Phiên tự ghi chưa đáp ứng B1. | REPORTED premature. Bước ghi phù hợp còn khả thi theo các lượt sau. Nguyên nhân hệ thống UNKNOWN. |
| S2 · khoảng 15:24 | M1 đã có hai commit. M2 dừng sau lỗi được báo nguyên văn `TypeError: tools.mcp__GitHub__create_file is not a function`. Chưa thử truy tên hàm hay phương án tree/commit/ref. | REPORTED premature ở bước xử lý lỗi. Lỗi gọi hàm được báo, nguyên nhân binding lỗi UNKNOWN. [M1 đầu](https://github.com/DuyKienTTD/Hosting/commit/1139975) · [M1 tiếp](https://github.com/DuyKienTTD/Hosting/commit/8313317) |
| S3 · khoảng 15:30 | Sau khi nhận phản hồi thẩm định M1, final báo chưa ghi GitHub và không nêu trở ngại. Điều tra ghi không có thao tác tool ở lượt đó. | REPORTED premature. Chưa có log hệ thống để xác định nguyên nhân. |

Vòng 1 do Claude báo cáo gồm **10/10 phiên mới hoàn tất lượt đầu**, **0/10 dừng sớm**, cùng GPT-6.2 Sol mức Vừa, Code Mode + GitHub, trong khoảng 16:28–16:36 ICT. Nhiệm vụ chung VERIFY-61 chỉ đọc một SHA. Tóm tắt kết quả ghi thời lượng 44–129 giây, trung vị 66 giây, và 4/10 phiên gắn F4 CLOSED. Chấm độ đúng tách khỏi completion: một số phiên nêu F4 vẫn còn lỗi. Việc đọc lại trong POST-61 xác nhận off-by-one và preflight thiếu tại [index trước sửa](https://github.com/DuyKienTTD/Hosting/blob/d7b2cc9bb2e458e31d334b362bffc40eae329ed2/rules/GATE-B-INDEX.md#L11). Dữ liệu chi tiết phiên vẫn là số do Claude báo cáo, không có transcript/telemetry công khai trong Git.

Hai nhóm khác loại việc, quyền ghi, cấu trúc yêu cầu, nguồn pin và điều kiện phiên. S1–S3 là ca được chọn để điều tra; vòng 1 dùng một tác vụ đọc lặp lại. Mẫu hiện tại chưa tách hiệu ứng phiên mới khỏi điều kiện công việc hay chứng minh nguyên nhân context/tool. Số nhắc, độ dài context và compaction chưa đủ dữ liệu để đối chiếu giữa các nhóm. [Đánh giá vận hành trước đây](https://github.com/DuyKienTTD/Hosting/blob/d7b2cc9bb2e458e31d334b362bffc40eae329ed2/reports/hosting-operational-reliability-validation-01.md) · [Đặc tả A/B](../program/hosting-post-61/ab/PROTOCOL.md).

### Số đo phiên POST-61

Nguồn: Claude giám sát phiên HOSTING-POST-61 và cung cấp số đo cho Điều phối trong HOSTING-POST-61b ngày 25/11/2026. Các số liệu dưới đây là `REPORTED`.

| Chỉ số | Quan sát của Claude |
| --- | --- |
| Work order | 2.238 ký tự. Hành động đầu tiên và tiêu chí hoàn thành nằm ở hai dòng đầu. |
| Cách báo cáo | Không gửi ACK riêng. Báo cáo một lần ở cuối lượt. |
| Thời điểm gửi | 16:59 ICT, 25/11/2026. |
| Thực thi | Một lượt, 11 phút 45 giây. |
| Dừng sớm và số lần nhắc | 0 lần dừng sớm, 0 lần nhắc. |
| Lỗi công cụ | Không thấy lỗi công cụ. |

So sánh số lượt dừng sớm do Claude báo cáo: POST-61 **0/1**, Điều phối cũ MKOE **3/6**, vòng thử 1 **0/10**. POST-61 mới có một lần chạy và các nhóm khác nhau về điều kiện, nên chưa đủ dữ liệu để kết luận nhân quả.

**Nghiệm thu:** A0 đọc báo cáo và delta nhánh POST-61. Điều phối đã xác minh tích hợp main và CI ở POST-01. Claude đã chạy và chấm A/B ở các phiên riêng, A0 đã hiệu chỉnh điểm. [Bảng chấm](../program/hosting-post-61/ab/SCORECARD.md).
