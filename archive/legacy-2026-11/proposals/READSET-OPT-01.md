---
id: hosting-readset-opt-01
type: knowledge
status: draft
owner: Chat Dieu phoi
task_id: HOSTING-READSET-OPT-01
lifecycle: ACTIVE
retention_trigger: A0 decision and proposal closure
updated_at: 2026-11-25
sensitivity: public
---

# READSET-OPT-01 — Đề xuất tối ưu READ_SET

**Đề xuất cho chủ dự án và A0.** Dự tính **30/56** ô đạt giảm ≥30% ký tự Unicode so với baseline trước MKOE (POST-04 hiện tại **0/56**). 30/56 cũng đạt ngưỡng theo byte UTF-8, và trùng tập ô đạt trong dự tính này. Các con số là dự tính theo ngân sách, cần xác nhận lại bằng blob triển khai và thử nghiệm độc lập. Quyền thực thi và hiệu lực MKOE tiếp tục theo quyết định A0 và các gate hiện hành. PR này chỉ chứa tài liệu đề xuất.

Nguồn đo: [POST-04 trên HEAD PR #62](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/reports/2026-11-25-hosting-post-61.md#post-04--đo-read_set) · [Baseline trước MKOE](https://github.com/DuyKienTTD/Hosting/commit/097c080cc6d7fb3ca36b1849d9c10375d5cbd67f) · [Candidate đã đo trong POST-04](https://github.com/DuyKienTTD/Hosting/commit/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb). Đọc lại HEAD `4198797bd6c889b915cf8f48be319f730db9f442`; mục POST-04 và các blob rules dùng để đo giữ nguyên khi PR #62 cập nhật POST-05 và CV chi tiết của Điều phối.

## 1. Vì sao READ_SET giảm ít

- **C1–C6 luôn mở cùng nhau** Workflow index, `authority`, `coordination`, `execution`, `evidence`, `handoff` (48/56 ô). Chùm này dài **8.814 ký tự / 10.034 byte**; baseline nguyên khối dài **12.377 / 14.946**. Review phi Git vẫn nạp routing KNG, chi phí, chuẩn bị hồ sơ bàn giao và quy trình thực thi đầy đủ. Mỗi module lặp front matter và banner trạng thái khoảng 275 ký tự.
- **C2–C6 luôn mở `dispatch`** (40/56 ô), gồm mẫu đặc tả B3 và biên nhận B2 trong cùng file. Review Git + ACK cần B2 và traceability, nhưng thường không cần chạy quy trình tạo/đổi owner hoặc soạn work order mới. `integrity` cũng được mở nguyên khối cho C2/C4/C5 (24/56), kéo cả quy tắc sửa trạng thái, CATALOG và quản trị cùng thao tác review diff.
- **C2/C4 mở cùng bộ bảy module** cộng index (**13.804 / 15.891**). **C5 mở cả tám** cộng index (**17.511 / 20.560**), rồi đọc cả `DATA_LIFECYCLE_CONTEXT.md`. Khai báo vòng đời, bảo toàn lịch sử và kiểm tra trước xóa xuất hiện ở nhiều nơi; hướng dẫn đóng POC và cam kết giữ bằng chứng là phần riêng phải bảo toàn. `STATE`, Security, CONTRIBUTING, MKOE, task và hồ sơ tạo chi phí cố định khi phạm vi yêu cầu chúng.
- **C0 không tải Workflow.** Nguồn bắt buộc là Core, đúng startup riêng và task. Giữ hồ sơ riêng, đặc tả và điều khoản Core; chỉnh nhóm Workflow sẽ không làm C0 giảm. Riêng review của Trợ lý A0 ở C1/C2/C6 còn có tiêu chuẩn thẩm định pin, không tính phần đó là khoản tiết kiệm.

Nguồn: [rules/AGENT_WORKFLOW.md L23-L35](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/AGENT_WORKFLOW.md#L23-L35) · [rules/coordination.md L14-L18](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/coordination.md#L14-L18) · [rules/dispatch.md L14-L18](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/dispatch.md#L14-L18) · [rules/integrity.md L14-L18](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/integrity.md#L14-L18) · [rules/lifecycle.md L14-L24](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/lifecycle.md#L14-L24).

## 2. Phương án gộp và tách

Giữ `AGENT_WORKFLOW.md` làm một index định tuyến theo **thao tác thực tế** và các điều kiện bắt buộc. Các ký hiệu dưới đây chỉ dùng trong phép tính. Mỗi tệp được kích hoạt phải đọc đầy đủ. Ở bước triển khai, các tệp có thể chọn riêng vì điều kiện khác nhau. Nhóm có cùng điều kiện thì gộp để tránh đọc hai file và lặp metadata. Mỗi điều khoản có một nguồn chuẩn. Khi Core hoặc protocol đã chứa cùng điều khoản, trỏ về nguồn đó và giữ mọi chi tiết bổ sung chưa có ở nguồn chuẩn. Ánh xạ lại consumer và liên kết cũ trong cùng delta được phê duyệt, giữ nguyên commit pin lịch sử.

| Ký hiệu | Tệp đề xuất và phạm vi | Ngân sách ký tự / byte |
| --- | --- | ---: |
| X | `AGENT_WORKFLOW.md`: điều kiện định tuyến, liên kết, trạng thái hiệu lực và đọc mở rộng khi chưa rõ. | 700 / 900 |
| G | `workflow-common.md`: gộp phần dùng chung của authority, vai trò chung ở coordination và execution. Core vẫn chứa nguyên văn các gate dùng chung. Giữ B1/B4, checkpoint, STOP từng thao tác, tiếp tục phần an toàn, phân biệt blocker với việc chưa kiểm tra và điều kiện tuyên bố vận hành liên tục. | 1.150 / 1.500 |
| R | `workflow-review.md`: evidence, QA độc lập, phân loại và độ tươi kết quả, điều kiện reuse/rerun, verdict theo phạm vi, nội dung kết luận review. | 800 / 1.100 |
| D | `workflow-dispatch.md`: B3, chọn owner theo năng lực, WHY_DELEGATE/COST_ROUTING thông thường, đặc tả đủ trường, một writer trên path/field, pin spec, attribution báo cáo, không giao trùng. Giữ danh mục trường bắt buộc kể cả khi chuyển vào mẫu canonical bắt buộc đọc. | 1.600 / 2.200 |
| A | `workflow-receipts.md`: tách B2 khỏi đặc tả, dùng cho chuẩn bị/kiểm tra/gửi/nhận handoff và mọi ACK. Giữ PREPARED/SENT/ACK, phân biệt review/thực thi, nguồn và đủ thuộc tính receipt. | 650 / 900 |
| I | `workflow-git-review.md`: phần integrity dùng cho review diff, provenance, xóa/đổi quyền và kiểm đồng thời; giữ cả Security + CONTRIBUTING trong các ca đã tính. | 650 / 900 |
| J | `workflow-git-write.md`: phần integrity riêng khi ghi, pin/freshness trước ghi, kiểm delta, rules change approval, rollback và remote readback. Kích hoạt kèm I. | 1.000 / 1.400 |
| H | `workflow-handoff.md`: trường bàn giao và báo cáo, B6, trạng thái hiển thị dẫn xuất, nơi lưu, link, next owner. Trỏ B2 tới A. | 800 / 1.100 |
| N | `workflow-routing.md`: trạng thái tác nhân, quyền ngoại lệ và HOLD ngoài KNG, không mở WS-04, provenance của trạng thái. Kích hoạt với STATE khi định tuyến hoặc cập nhật tổng hợp. | 500 / 700 |
| K | `workflow-kng.md`: tách phần KNG khỏi coordination, giữ điều kiện exact SHA/tree, merge method và readback có xác thực, quyền hạn trong snapshot và STOP dispatch. Kích hoạt kèm STATE, snapshot và release gate; đọc N nếu thực sự định tuyến/giao việc ngoài KNG. | 1.150 / 1.600 |
| L | `workflow-lifecycle.md`: đóng/dọn POC có thẩm quyền, checklist milestone, giữ stable ID/provenance, STATE và CATALOG khi đổi nguồn chuẩn. Trỏ phân loại, retention, validator và kiểm phụ thuộc về nguyên protocol. | 1.900 / 2.550 |

Phần ngoại lệ Codex/Hermes, nội dung bị policy chặn, paid/render/publish, production/VPS, destructive, merge và Gate B giữ nguyên trong một nguồn bắt buộc theo rủi ro (`workflow-restricted-operations.md`) hoặc nguồn canonical hiện có, kèm quyết định A0, preflight, runbook/rollback, Security và gate liên quan. Các tác vụ kiểm soát C0–C6 không giả định thực hiện các thao tác đó. Nếu thêm thao tác, hợp các tập nguồn bắt buộc và đọc đủ trước phần phụ thuộc. Khi quyền/điều kiện đọc chưa rõ, đọc toàn bộ module và nguồn an toàn có thể áp dụng, giữ STOP khi nguồn thiếu, stale, truncate, mâu thuẫn hoặc chưa có quyền. Chỉ mục Gate B tiếp tục dẫn đến phạm vi pin gồm preflight L57–L59 và H5/H6 kết thúc L718; nguồn lịch sử phải được đọc theo điều khoản an toàn liên quan, kèm xác minh authority live, ledger và kill switch.

### Định tuyến cho đúng bảy ca đo

| Ca | Loại việc | Bộ Workflow đề xuất | Workflow hiện tại → dự tính (ký tự / byte) |
| --- | --- | --- | ---: |
| C0 | Khởi đầu | Không tải Workflow | 0 / 0 → 0 / 0 |
| C1 | Review phi Git, không ACK | X G R | 8.814 / 10.034 → 2.650 / 3.500 |
| C2 | Review Git + ACK | X G R A I | 13.804 / 15.891 → 3.950 / 5.300 |
| C3 | Điều phối chuẩn bị dispatch ngoài KNG | X G D A H N | 11.800 / 13.576 → 5.400 / 7.300 |
| C4 | Ghi Git tài liệu và bàn giao | X G R A I J H | 13.804 / 15.891 → 5.750 / 7.800 |
| C5 | Điều phối + Git + lifecycle + trạng thái | X G R D A I J H N L | 17.511 / 20.560 → 9.750 / 13.250 |
| C6 | Review định tuyến KNG | X G R K | 11.800 / 13.576 → 3.800 / 5.100 |

C3 có N vì cần đọc STATE để chuẩn bị dispatch ngoài KNG. READ_SET C3 gồm A/H để kiểm trường và trạng thái của handoff ngay lúc chuẩn bị. C4 giữ A/R/I/J/H vì có handoff, bằng chứng và Git write. C5 giả định thao tác trạng thái quản trị có quyền riêng trong phạm vi POST-04. Khi ghi trạng thái phát sinh quyết định KNG, C5 phải cộng K cùng nguồn KNG. C6 chỉ review định tuyến KNG, giữ R/K và các nguồn KNG đầy đủ; dispatch hoặc ACK thực tế mở thêm các module tương ứng.

## 3. Dự tính 56 trường hợp

Lấy nguyên cột baseline và candidate của POST-04. Với từng ô, lấy **phần cố định = candidate POST-04 − Workflow hiện tại** (index và các module tương ứng). Kiểm chéo bằng cách cộng lại kích thước blob Core + startup riêng + đặc tả kiểm soát 2.692 ký tự/3.094 byte + nguồn thêm theo hàng C0–C6 của POST-04. Giữ đầy đủ Security, CONTRIBUTING, Lifecycle Protocol, STATE, MKOE, KNG snapshot/release gate và phần tiêu chuẩn pin của Trợ lý A0 ở các ô tương ứng. Cộng ngân sách Workflow đề xuất vào phần cố định. Dùng UTF-8 thô, tính cả front matter, link, khoảng trắng và newline cuối, đếm mỗi path/range một lần. So với baseline **trước MKOE**, phép kiểm đạt là `10 × dự tính ≤ 7 × baseline` trên số nguyên. Bảng làm tròn phần trăm đến một chữ số.

### Unicode · baseline → dự tính (% giảm)

Dấu ✓ là đạt ngưỡng. Mỗi ô là một ca định mức.

| Vai trò | C0 | C1 | C2 | C3 | C4 | C5 | C6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Trợ lý A0 | 7.787 → 8.103 (-4,1%) | 30.025 → 20.614 (31,3%) ✓ | 33.810 → 25.699 (24,0%) | 24.513 → 15.761 (35,7%) ✓ | 23.949 → 17.638 (26,4%) | 39.646 → 35.244 (11,1%) | 43.550 → 33.198 (23,8%) |
| A1 | 6.832 → 7.138 (-4,5%) | 19.209 → 9.788 (49,0%) ✓ | 22.994 → 14.873 (35,3%) ✓ | 23.558 → 14.796 (37,2%) ✓ | 22.994 → 16.673 (27,5%) | 38.691 → 34.279 (11,4%) | 32.734 → 22.372 (31,7%) ✓ |
| A2 | 7.050 → 6.738 (4,4%) | 19.427 → 9.388 (51,7%) ✓ | 23.212 → 14.473 (37,6%) ✓ | 23.776 → 14.396 (39,5%) ✓ | 23.212 → 16.273 (29,9%) | 38.909 → 33.879 (12,9%) | 32.952 → 21.972 (33,3%) ✓ |
| Codex | 6.847 → 7.156 (-4,5%) | 19.224 → 9.806 (49,0%) ✓ | 23.009 → 14.891 (35,3%) ✓ | 23.573 → 14.814 (37,2%) ✓ | 23.009 → 16.691 (27,5%) | 38.706 → 34.297 (11,4%) | 32.749 → 22.390 (31,6%) ✓ |
| Điều phối | 7.050 → 6.825 (3,2%) | 19.427 → 9.475 (51,2%) ✓ | 23.212 → 14.560 (37,3%) ✓ | 23.776 → 14.483 (39,1%) ✓ | 23.212 → 16.360 (29,5%) | 38.909 → 33.966 (12,7%) | 32.952 → 22.059 (33,1%) ✓ |
| Hermes | 6.813 → 7.123 (-4,6%) | 19.190 → 9.773 (49,1%) ✓ | 22.975 → 14.858 (35,3%) ✓ | 23.539 → 14.781 (37,2%) ✓ | 22.975 → 16.658 (27,5%) | 38.672 → 34.264 (11,4%) | 32.715 → 22.357 (31,7%) ✓ |
| Hostinger Agent | 6.823 → 7.136 (-4,6%) | 19.200 → 9.786 (49,0%) ✓ | 22.985 → 14.871 (35,3%) ✓ | 23.549 → 14.794 (37,2%) ✓ | 22.985 → 16.671 (27,5%) | 38.682 → 34.277 (11,4%) | 32.725 → 22.370 (31,6%) ✓ |
| Work | 7.050 → 6.774 (3,9%) | 19.427 → 9.424 (51,5%) ✓ | 23.212 → 14.509 (37,5%) ✓ | 23.776 → 14.432 (39,3%) ✓ | 23.212 → 16.309 (29,7%) | 38.909 → 33.915 (12,8%) | 32.952 → 22.008 (33,2%) ✓ |

### UTF-8 · byte dự tính

Đối chiếu baseline byte trong bảng POST-04 đã dẫn ở đầu tài liệu.

| Vai trò | C0 | C1 | C2 | C3 | C4 | C5 | C6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Trợ lý A0 | 9.689 | 25.550 | 31.797 | 19.254 | 21.936 | 42.053 | 38.596 |
| A1 | 8.438 | 11.938 | 18.185 | 18.003 | 20.685 | 40.802 | 24.984 |
| A2 | 7.951 | 11.451 | 17.698 | 17.516 | 20.198 | 40.315 | 24.497 |
| Codex | 8.470 | 11.970 | 18.217 | 18.035 | 20.717 | 40.834 | 25.016 |
| Điều phối | 8.048 | 11.548 | 17.795 | 17.613 | 20.295 | 40.412 | 24.594 |
| Hermes | 8.412 | 11.912 | 18.159 | 17.977 | 20.659 | 40.776 | 24.958 |
| Hostinger Agent | 8.444 | 11.944 | 18.191 | 18.009 | 20.691 | 40.808 | 24.990 |
| Work | 7.988 | 11.488 | 17.735 | 17.553 | 20.235 | 40.352 | 24.534 |

| Chỉ tiêu | C0 | C1 | C2 | C3 | C4 | C5 | C6 | Tổng |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ≥30% Unicode | 0 | 8 | 7 | 8 | 0 | 0 | 7 | **30/56** |
| ≥30% UTF-8 | 0 | 8 | 7 | 8 | 0 | 0 | 7 | **30/56** |
| Unicode khi ngân sách Workflow vượt 20% | 0 | 7 | 7 | 8 | 0 | 0 | 3 | **25/56** |

C4 gần ngưỡng nhất ở A2, còn thiếu 25 ký tự. C5, sau khi giữ phần cố định, chỉ còn **2.258–3.107** ký tự cho Workflow để chạm 30%, trong khi các module cần khoảng **9.750**. Giữ nguồn an toàn bắt buộc, chấp nhận C0/C4/C5 chưa đạt trong phương án này. Tiêu chuẩn A0 pin khiến C2 và C6 của Trợ lý A0 khó đạt. Ngân sách là giả định thiết kế, chưa có nội dung triển khai để đo. Quyết định A0, runbook live, Gate B, dữ kiện task thật và bằng chứng từng ca cộng theo scope thực tế. Chữ và byte không đại diện token, chi phí hoặc chất lượng đọc.

## 4. Điều khoản phải giữ và cách kiểm

| Nhóm | Điều khoản phải giữ nguyên về hiệu lực | Bằng chứng và ca kiểm tối thiểu |
| --- | --- | --- |
| Quyền, STOP và tính hiệu lực | Core/role/task pin; deny mặc định; quyền riêng theo phiên/task; A0 giữ production, chi phí, merge; preflight, đúng môi trường/phạm vi, rollback; một writer; freshness, partial read, STOP/HOLD và tiếp tục phần độc lập an toàn. MKOE candidate chỉ có hiệu lực sau nghiệm thu độc lập, hợp nhất được duyệt và readback/CI. | Thiếu approval mới, receipt sai phạm vi, stale source, output truncate hoặc STOP bắt buộc dừng phần phụ thuộc. So nguyên blob Core. [AGENTS.md L3-L28](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/AGENTS.md#L3-L28) · [rules/authority.md L12-L16](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/authority.md#L12-L16) · [rules/execution.md L14-L16](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/execution.md#L14-L16) |
| Dispatch, định danh và hai tầng QA | B3 một owner/outcome, spec ghi đủ phạm vi/quyền/test/rollback và pin; Điều phối giữ shared-write, trạng thái tổng hợp; Trợ lý A0 có giới hạn ủy quyền; reviewer khác tác giả; QA roadmap không thay gate bảo mật/release. B1 tiếp tục đến đầu ra, B4 phiên mới bắt buộc cho outcome lớn độc lập; giữ checkpoint tối thiểu. | Ca sửa lỗi nội bộ tiếp tục phiên cũ. Ca outcome lớn mở phiên mới. Tác giả tự QA hoặc ghi ngoài write-set không qua gate. [rules/dispatch.md L14-L16](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/dispatch.md#L14-L16) · [rules/execution.md L14-L16](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/execution.md#L14-L16) · [rules/coordination.md L14](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/coordination.md#L14) · [rules/evidence.md L14](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/evidence.md#L14) |
| Handoff và bằng chứng | B2 đủ task, recipient, session, event/scope, time, nguồn cùng receipt; giữ phân biệt ACK review/thực thi, PREPARED/SENT/ACK, trạng thái chưa biết. B6 một comment trạng thái dẫn xuất. Phân loại nguồn live/mock/historical/author, chỉ reuse khi tương đương, đúng phiên bản và còn tươi. | ACK sai task/phiên không được tính; một commit hoặc comment chuẩn bị không thành SENT/ACK; mock hoặc author report không nâng thành live/QA độc lập. [rules/dispatch.md L18](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/dispatch.md#L18) · [rules/handoff.md L14-L16](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/handoff.md#L14-L16) · [rules/evidence.md L14](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/evidence.md#L14) |
| Routing KNG và ngoại lệ | A0 duyệt exact candidate SHA/tree; merge method merge; independent authenticated remote main readback đúng merge/tree và hai cha có thứ tự. KNG_ONLY và vai A1/Work giữ nguyên theo snapshot. Ngoài KNG HOLD nếu thiếu quyền riêng; cấm mở WS-04; Hostinger PAUSED, Hermes HOLD_NO_NEW_TASKS, Codex NOT_AUTHORIZED. Giữ đủ điều kiện ngoại lệ Codex/Hermes, cost cap, consent, đối soát, STOP, không retry paid/side effect thiếu idempotency và tuân thủ policy. | Thử stale snapshot, thiếu auth, SHA/tree sai, cha đảo, squash, Hostinger chưa được resume/ACK, Codex/Hermes thiếu điều kiện ngoại lệ, paid timeout chưa chứng minh idempotency. Chạy KNG regressions ở delta triển khai. [rules/coordination.md L16-L18](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/coordination.md#L16-L18) · [program/kng/release_state.py](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/program/kng/release_state.py) · [rules/GATE-B-INDEX.md L11](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/GATE-B-INDEX.md#L11) |
| An toàn kho và Git | Cấm credential/PII/raw logs/dump/IP thật chưa được duyệt; rotate nếu lộ. Pin base, đọc đủ, kiểm diff gồm phần xóa, invariant/validator/link/secret, chống stale/force-push/rewrite/bypass; rollback đúng phạm vi và đọc lại remote SHA/nội dung. | Negative fixtures cho credential giả, ghi stale, mất provenance và thiếu readback. So nguyên blob Security và CONTRIBUTING. [rules/REPOSITORY_SECURITY.md](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/REPOSITORY_SECURITY.md) · [CONTRIBUTING.md](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/CONTRIBUTING.md) · [rules/integrity.md L14-L18](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/integrity.md#L14-L18) |
| Lifecycle và lịch sử | DURABLE/ACTIVE/TEMPORARY có owner/trigger; một nguồn chuẩn, task/report/evidence ngoài CATALOG; giữ quyền/STOP, bảo mật/dữ liệu, tài chính/kiểm toán, rollback, QA độc lập, regression, dependency. Đóng POC bằng một báo cáo ngắn; dọn khi có quyền, xác định retention/tham chiếu và pin đường phục hồi. Giữ stable ID/path, marker, hash lịch sử; không tự xóa hoặc sửa lịch sử. | Xóa file còn dependency, retention chưa rõ hoặc quyền thiếu phải chặn; mẫu POC đã đóng giữ báo cáo và bằng chứng cần thiết. So nguyên blob Protocol, provenance và Gate B source/anchors. [rules/lifecycle.md L14-L24](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/lifecycle.md#L14-L24) · [rules/DATA_LIFECYCLE_CONTEXT.md](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/DATA_LIFECYCLE_CONTEXT.md) · [rules/GATE-B-INDEX.md L11](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/rules/GATE-B-INDEX.md#L11) |

### Nghiệm thu nếu A0 duyệt triển khai

1. Lập bảng đối chiếu từng đoạn quy phạm ở baseline và candidate pin → tệp/anchor mới, trigger đọc và ca kiểm; đánh dấu giữ nguyên, chuyển nguyên văn hoặc hợp nhất trùng. Giữ nguyên văn các câu điều kiện an toàn duy nhất, gồm ngoại lệ và STOP. Reviewer độc lập đọc toàn diff, xác nhận mọi điều khoản nguồn còn hiệu lực và mọi trigger bảo toàn coverage; kiểm consumer khi đổi đường dẫn, ID cũ và fallback đọc đầy đủ. Điều khoản chưa ánh xạ hoặc bị hẹp điều kiện kích hoạt thì chặn nghiệm thu, kể cả khi hụt ngân sách.
2. Đối chiếu nguyên blob các nguồn được giữ, chạy kiểm link/anchor, dữ liệu/secret, Data Integrity validator/tests, KNG provenance/QA, regression của release gate và kiểm policy trước Git write. Chạy tình huống dương/âm/lỗi trong bảng trên bằng fixture offline, đặc biệt là case ghép nhiều thao tác. Giữ bằng chứng pin đến exact candidate SHA. Đo lại cùng 56 ô từ blob thật và ghi danh sách từng nguồn trong từng ô.
3. Trợ lý A0 hoặc reviewer khác tác giả chấm mù theo [quy trình POST-61](https://github.com/DuyKienTTD/Hosting/blob/4198797bd6c889b915cf8f48be319f730db9f442/program/hosting-post-61/ab/PROTOCOL.md). Thêm cặp ca C2/C4 (phân biệt ACK với quyền ghi), C5 (retention/quyền xóa) và C6 (STOP khi sai release gate). Cùng đề, model, môi trường, quyền và bằng chứng pin; log nguồn đã đọc, số ký tự/byte, lỗi bắt buộc, kết quả tác vụ, nhắc và thời gian. Chấp nhận khi đo lại báo đúng số đạt, không mất điều khoản, không giảm độ đúng và không bỏ gate. Telemetry hoặc thử nghiệm độc lập thiếu thì ghi PARTIAL/NOT_RUN. Chỉ đổi chính sách sau quyết định A0 đúng SHA, CI và remote readback theo gate.
