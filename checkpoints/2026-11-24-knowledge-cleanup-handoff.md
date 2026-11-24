---
id: hosting-knowledge-cleanup-handoff-2026-11-24
type: report
status: current
updated_at: 2026-11-24
sensitivity: public-redacted
---

# Checkpoint — hoàn tất tối ưu tri thức, tiếp tục TTD Zalo Assistant

**Mục tiêu A0:** hoàn tất tối ưu kho tri thức trước khi tiếp tục sản phẩm TTD Zalo Assistant; giảm gánh nặng quản lý cho A0. Không lập kế hoạch lại, không báo cáo từng bước nhỏ, không yêu cầu A0 nhắc lại nhiệm vụ. Đây là checkpoint tạm thời, loại khỏi cây hiện hành khi bàn giao hoàn tất và kiểm tra tham chiếu.

## Trạng thái đã xác minh

- [Draft PR #59](https://github.com/DuyKienTTD/Hosting/pull/59), branch `a0-assistant/knowledge-streamline-2026-11-24`, HEAD trước checkpoint `ae9dd2937b555cbdf8d6adc24d642d4f38db7908`, main `d549564de52429e777c68daf9df7a93df5f22f27`. Chưa merge.
- Commit `b842f547e1b6b00adf12ddbfbbda9e96a5b7ea3a`: AGENTS và workflow tinh gọn, chỉ mục lịch sử, changelog.
- Commit `d2c61a38fe89b8225b6bf2eb1f7a71b6286391ee`: workflow §8 DURABLE/ACTIVE/TEMPORARY; một báo cáo kết thúc ngắn cho POC thất bại, dọn báo cáo trung gian khi đóng, bảo toàn bằng chứng thiết yếu và provenance.
- Commit `ae9dd2937b555cbdf8d6adc24d642d4f38db7908`: xóa 3 báo cáo cũ: agent-reallocation-proposal, parallelism-dependencies-bottlenecks, hostinger-portfolio-assessment (đều ngày 2026-11-23). Remote xác minh absent 3/3; CATALOG blob `26e125296fd0c39d0e82d6c5438dcc1ca2d8947f` không đổi, main không đổi.
- Phiên trước báo cáo quét ZIP main 275 file, không thấy tham chiếu trực tiếp đến 3 file trên; chưa có artifact quét độc lập được lưu. Không coi các nhánh khác đã quét. ZIP A0 đã cung cấp `Hosting-d549564de52429e777c68daf9df7a93df5f22f27.zip`; kiểm tra file thực tế khi bắt đầu phiên mới.
- Không có commit thực thi mới sau ae9dd293 trước checkpoint này; validator, runtime QA, merge và quyết định cấp quyền Zalo MVP chưa hoàn tất.

## FIRST_ACTION — thực thi, không nghiên cứu lại

1. Xác minh remote main/PR59 HEAD, quyền và lease shared-write. Đọc đầy đủ quy tắc hiện hành, security, state, role và phần task liên quan bằng range nếu cần. Quy tắc candidate chưa hiệu lực.
2. Dùng ZIP/bản clone cục bộ làm base; áp delta PR59 bằng các file remote đã pin, quét toàn cây bằng script một lần, kiểm tra tên/path/ID/blob và link tương đối; không gọi API cho từng file. Nếu môi trường thiếu công cụ hoặc ZIP, dùng fallback hợp lệ; nêu chính xác trở ngại, không tuyên bố PASS giả.
3. Đồng bộ luồng đọc CATALOG theo chỉ mục tại AGENTS/workflow/README/STATE/role/typed source và test liên quan. CATALOG hiện tại phải giữ nguyên theo chỉ thị A0; không tự loại ID/path hoặc sửa schema. Các generated marker phải giữ đúng derive contract.
4. Sửa validator theo hướng phân biệt kiểm chứng snapshot lịch sử bằng commit-tree-path-blob và kiểm tra tài liệu hiện hành; không ghi đè pin cũ, không tắt validation, không miễn fail-closed. Thêm ca âm tính sai pin, sai quyền, stale rule, drift, duplicate, broken link. Chạy baseline và candidate tests với môi trường thực có thể kiểm chứng; ghi chính xác lệnh/exit. Nếu ZIP không có Git object history, provenance verification phải BLOCKED chứ không PASS; tests fixture không phải xác minh live.
5. Rà soát 5 ứng viên còn tham chiếu dưới đây. Vì CATALOG phải nguyên byte và các entry trỏ đến path thực, không xóa physical file nếu làm mất path; dùng rút gọn có provenance nếu hợp lệ hoặc đề xuất delta riêng cần quyền cập nhật registry, không tự sửa CATALOG. Giữ ADR, receipt, security, rollback, tài chính và independent QA. Không làm lại POC.
6. Commit scoped thay đổi trên PR59, remote readback, kiểm thử diff; yêu cầu independent QA qua đúng Điều phối khi cần, không tự nhận independent PASS. A0 giữ quyền merge; chỉ merge theo quyền cụ thể và sau nghiệm thu. Hoàn tất cleanup trước khi tiếp tục Zalo.

## 5 ứng viên còn lại

| File (trong reports/ trừ dòng cuối) | Tham chiếu đã báo cáo | Xử lý |
|---|---|---|
| 2026-11-21-gate-b-h3-checkpoint.md | CATALOG 562–563; CHANGELOG 190 | superseded; giữ nguồn H3 |
| 2026-11-21-hermes-gate-b-guard-mount-paused-checkpoint.md | CATALOG 606–607; CHANGELOG 163 | superseded; giữ nghiệm thu mount |
| 2026-11-22-hermes-gate-b-guard-mount-access-result.md | CATALOG 615–616; CHANGELOG 149; task Gate B line 291 | giữ provenance/giới hạn, relink nếu được phép |
| 2026-11-23-a1-codex-cost-reallocation.md | CATALOG 63–64; CHANGELOG 28; KNG reconciliation JSON | giữ chỉ thị A0/ACK |
| tasks/2026-11-23-a1-cost-first-master-allocation.md | CATALOG 53–54; CHANGELOG 25,28; agents/codex.md 14; reconciliation JSON; workflow cũ 240 | archived non-dispatch, giữ authority/evidence |

Line numbers là kết quả phiên trước, cần xác minh tại SHA thực. Không xóa hàng loạt Gate B đang HOLD. Không nhập các báo cáo trung gian POC từ nhánh khác vào main. POC ZALO-01, ZALO-02, OPENCLAW-01 đã đóng NO-GO; chỉ giữ báo cáo kết thúc ngắn + nguồn evidence cần thiết khi tích hợp, không thử lại.

## Handoff sau cleanup

[Checkpoint Trợ lý A0 Zalo MVP](https://github.com/DuyKienTTD/Hosting/blob/7b5b16fb9d27eab945994f5d3c060b08347c2ecc/checkpoints/2026-11-24-a0-assistant-zalo-mvp01.md) — tiếp tục mục 9. [Checkpoint Điều phối](https://github.com/DuyKienTTD/Hosting/blob/f812ba4ada6a17f51e3c0d7c9879ed8917f552b9/reports/2026-11-24-ttd-zalo-mvp01-checkpoint.md). Quyền A0 Assistant thẩm định và phê duyệt Zalo trong phạm vi offline được ủy nhiệm; coordinator sole allocator. Đọc nguồn bắt buộc, ghi quyết định chính thức trên GitHub và chuyển Điều phối; chưa có quyền thực thi MVP chính thức ở checkpoint này. Không paid API, tài khoản Zalo thật, production, VPS, Codex hoặc main merge ngoài phê duyệt riêng.

**NEXT_OWNER:** phiên Trợ lý A0 mới. **HANDOFF_STATE:** PREPARED_FOR_OWNER_FORWARD. **Không tạo thêm báo cáo trung gian; cập nhật checkpoint/task hiện có nếu cần.**

## Tiếp nhận phiên A0 Assistant — 2026-11-24 (kiểm tra thực tế, chưa nghiệm thu)

- Đã đọc checkpoint HEAD `5dd2f7c5272b526dda6d7244e8427e076cd8d2db`, xác minh PR59 Draft/Open tại đúng HEAD, base main `d549564de52429e777c68daf9df7a93df5f22f27`; GitHub connected identity `DuyKienTTD`, repository push/admin có sẵn nhưng **không suy ra quyền merge**.
- Đã đọc quy tắc main (AGENTS, workflow, security, STATE), hồ sơ ChatGPT, typed current và candidate workflow; CATALOG blob giữ `26e125296fd0c39d0e82d6c5438dcc1ca2d8947f`. Candidate tree API trả `truncated=false` với 298 entries / 274 blobs. Phân biệt candidate với quy tắc main hiện hành.
- **ĐÍNH CHÍNH:** ZIP do A0 gửi trước đó đã được mount tại `/mnt/data/Hosting-d549564de52429e777c68daf9df7a93df5f22f27.zip` và giải nén thành công (275 files trong archive). Thông báo không thấy ZIP lúc đầu là sai. Baseline Python suite `python3 -m unittest discover -s program/kng -p 'test_*.py'` exit 0: 131/131 PASS; sau sửa validator và thêm 1 negative test, exit 0: 132/132 PASS trên baseline+delta. `python3 program/kng/validate.py --json` exit 1, 18 `PROVENANCE_UNVERIFIED` do archive thiếu `.git`/object history. Không xem fixture PASS là live provenance hay QA độc lập.
- Đã chạy script audit trên baseline ZIP: 130 CATALOG IDs không trùng, 130 indexed paths tồn tại; 1 chuỗi link `missing-source.md` chỉ nằm trong source test negative fixture, không phải broken Markdown link thực. 5 hồ sơ còn references từ CATALOG/CHANGELOG/task/evidence; candidate remote tree giữ nguyên. Ba file báo cáo đã xóa trên PR59 vẫn hiện hữu trong ZIP baseline đúng kỳ vọng. Full candidate content-scan và historical git-object verification vẫn NOT_RUN vì shell không truy cập GitHub và candidate không có local object graph.
- Code delta PR59: `e509931c9f585d4db2014845b6c39e05ecf62e77` sửa `program/kng/validate.py` tách pin lịch sử D2 khỏi phép kiểm candidate; `3a6cac58bb5fd8e8acc23c5c6efe4d62d15e286b` thêm test âm tính `UNSAFE_CURRENT_RULE`. `CATALOG.yaml`, lock, migration, current.json không đổi.

- Cả 5 ứng viên còn tham chiếu đều tồn tại trong candidate tree, CATALOG chưa được phép đổi; không xóa. Ba báo cáo đã xóa trong commit `ae9dd293` được checkpoint trước xác nhận absent, chưa có tái kiểm full-tree một lượt độc lập.
- Validator đã được sửa theo phạm vi hẹp, nhưng historical commit/tree/blob verification và candidate full test cần kiểm chứng thêm; không thay đổi pin hoặc vô hiệu kiểm tra.
- **Status:** `PARTIAL · CLEANUP_NOT_ACCEPTED · PR59_DRAFT_UNMERGED`. **Next owner:** A0 Assistant tiếp tục scoped QA/code khi có khả năng thực thi kiểm chứng; Điều phối điều phối independent QA sau candidate. Quyền merge vẫn thuộc A0. Chưa chuyển sang TTD Zalo MVP khi cleanup chưa đạt gate.
