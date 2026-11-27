---
id: hosting-post-61
type: task
status: draft
owner: Chat Dieu phoi
task_id: HOSTING-POST-61
lifecycle: ACTIVE
retention_trigger: A0 acceptance and closure
updated_at: 2026-11-25
sensitivity: public
---
# HOSTING-POST-61 — Đặc tả theo giao việc của chủ dự án

SPEC_ID `HOSTING-POST-61-v1` · OWNER Chat Điều phối · NEXT_OWNER A0 nghiệm thu · MODE kiểm chứng và Git write tài liệu, một PR nháp.

OUTCOME và ACCEPTANCE — Sáu mục có DONE hoặc BLOCKED kèm nguồn đọc lại từ GitHub. Sửa chỉ mục Gate B, kiểm điều kiện tích hợp main, kiểm kê năng lực theo bằng chứng, chuẩn bị A/B, đo READ_SET và đánh giá dừng sớm. Claude chạy A/B độc lập. Báo cáo duy nhất ở [reports/2026-11-25-hosting-post-61.md](https://github.com/DuyKienTTD/Hosting/tree/coordinator/hosting-post-61/reports).

FIRST_ACTION — Đọc trạng thái, HEAD và nhánh PR #61. BASE_REF là PR #61, BASE_SHA ban đầu `d7b2cc9bb2e458e31d334b362bffc40eae329ed2`. Baseline trước MKOE `097c080cc6d7fb3ca36b1849d9c10375d5cbd67f`. Cha của nhánh POST-61 là HEAD sau FIX-F4 `c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb`.

AUTHORITY — Giao trực tiếp của chủ dự án ngày 25/11/2026 ở phiên HOSTING-POST-61. Cho phép FIX-F4 trên nhánh PR #61 khi mở và tạo nhánh/PR nháp cho POST-61. Cost cap phát sinh bằng 0. Báo cáo một lần, ACK ở đầu báo cáo chat. Bản này ghi phạm vi công việc và không thay biên nhận hội thoại.

READ_SET — [Core](https://github.com/DuyKienTTD/Hosting/blob/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb/AGENTS.md), hồ sơ Điều phối, [MKOE-01](https://github.com/DuyKienTTD/Hosting/blob/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb/rules/HOSTING-MKOE-01.md), Workflow và module phát sinh, Security, CONTRIBUTING, Lifecycle, bằng chứng theo task. PREVIOUSLY_VERIFIED — CI tại HEAD cũ chỉ áp dụng cho SHA cũ. Đọc ref mới trước khi ghi và sau lỗi ghi.

WRITE_SET — Chỉ mục Gate B trên nhánh PR #61. Nhánh POST-61 chỉ gồm đặc tả này, `program/hosting-post-61/`, inventory trong tám CV và một báo cáo trên. DO_NOT_TOUCH — main, mã, runtime, nguồn Gate B, catalog, release gate, quyền Agent và dữ liệu thật.

DEPENDENCIES — POST-01 chờ PR #61 merge. POST-02 dựa trên bằng chứng theo vai trò. POST-03 chuẩn bị cho Claude, không tự chạy. POST-05 số đo của phiên này do Claude cung cấp sau.

TEST_DELTA/INVARIANTS — Soát anchor, link, tài liệu nguồn, diff, validator và đọc lại SHA/tệp trên GitHub. Trạng thái BLOCKED không dừng mục độc lập. STOP thao tác ghi nếu ref trôi hoặc quyền thiếu. Khi công cụ lỗi, đọc lại HEAD/tệp trước retry, tra hàm tương đương và lưu lỗi chưa gỡ. Rollback bằng revert commit đúng phạm vi sau quyết định của A0.

STATUS và EVIDENCE — Trạng thái tổng hợp ở `program/hosting-post-61/WORK_ITEMS.md`, dẫn tới bộ hồ sơ và báo cáo.
