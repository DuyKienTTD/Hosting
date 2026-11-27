---
id: report-2026-11-23-codex-gov02-s1-readiness
type: report
status: ready_for_review
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
source: pinned-git-objects-and-local-synthetic-tests
---

# GOV-02/S1 — Validator metadata và thứ tự review

| Mục | Kết quả |
| --- | --- |
| TASK / OWNER / ACK | GOV-02/S1 / Codex / EXECUTE theo [chỉ thị Điều phối](https://github.com/DuyKienTTD/Hosting/pull/21#issuecomment-7091856757). |
| BASE_SHA | Main và rule commit `e385c1bea2070973e3007e5717f7e980348d6ab3`, tree `991af4f21ca12f3db98c7a1bd89c297f18e446d7`, workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. |
| SOURCE_SHAS | 12 snapshot gồm main, PR #6 và 10 PR gói offline/design. HEAD/tree/file list trong [evidence](evidence/2026-11-23-codex-gov02-s1-validator.json). |
| TESTS | 7/7 fixture, gồm một ca hợp lệ và sáu nhóm lỗi. Nguồn thật có 30 artifact path/blob, 0 lỗi pin hoặc source unavailable. Windows 11 AMD64, CPython 3.12.3. |
| INDEX_GAPS | 24 artifact chưa được lập mục, 5 dòng kế hoạch cũ, 3 file metadata có hai writer và 1 cặp tài liệu dùng chung ID. |
| VERDICT | `GOV02_S1_OFFLINE_METADATA_VALIDATOR_PASS`. Lượt audit nguồn thật trả exit 1 vì còn findings governance. Đây là đầu vào review, chưa phải nghiệm thu merge. |
| PR_URL / NEXT_OWNER | [Draft PR GOV-02/S1](https://github.com/DuyKienTTD/Hosting/pulls?q=is%3Apr+head%3Acodex%2Fgov-02-s1-offline-repo-validator-2026-11-23) → ChatGPT Điều phối. |

## Kết quả đối chiếu

- CATALOG của các tree đã kiểm thiếu 24 trong 30 task/report/evidence path, gồm task và bộ báo cáo D1 của ENG-01A S3/S4. Không phát hiện ID CATALOG trùng hoặc link tương đối ở các index đã kiểm bị hỏng. Task và report OPS-01A/S2 trên PR #24 dùng cùng front matter ID `ttd-hostinger-ops01a-s2-lifecycle-2026-11-23`. Đề nghị Hostinger Agent xác nhận ID của report trước khi lập mục.
- PR #6 tại `03fb56b6d3b4f42a1cb65c6e3c87a19099785044` còn `NO_TASK_YET` cho BIZ-02, UX-01, ENG-01A, GROW-02A và OPS-01A, trong khi các task đã tồn tại ở HEAD PR tương ứng. CATALOG, STATE và CHANGELOG đều xuất hiện trong diff của PR #10 và #13, dù preview S4-D1 trước đó sạch về văn bản. Validator lấy file list thật từ GitHub, đối chiếu với local Git, kiểm SHA và ghi findings độc lập với merge preview. [Preview S4-D1 tại các HEAD này](https://github.com/DuyKienTTD/Hosting/pull/21#issuecomment-7091721615)
- Quyết định A0-1 đến A0-5 vẫn chờ chủ dự án. Consent GA4 và quyền truy cập property cần quyết định riêng. UX browser vẫn unverified, OPS mới có synthetic evaluator/lifecycle và live monitoring vẫn unverified. ENG-01A S4 còn `LINUX_NOT_RUN`, connector thật vẫn `REAL_UNTESTED`. Metadata không cấp quyền triển khai.

## Thứ tự review và điều kiện refresh pin

Các HEAD sau đều có base `e385c1bea2070973e3007e5717f7e980348d6ab3`. Preview đã giao ở S4-D1 ghi tree `e96250487222ccc9277c7e3b1c544a622fa7125e` cho chuỗi này. GOV-02/S1 dùng lại bằng chứng vì các HEAD khớp.

| Bước dự kiến | HEAD đã đọc | Kiểm sau khi merge được phê duyệt |
| --- | --- | --- |
| #10 · S1 | `79dfe8aae5c30d4e896c29333e0296ada1671b7e` | Đối chiếu S1 source blob trên main. Refresh review base #13 và trạng thái `INTEGRATION_PENDING_PR10`; S2 dùng fixture riêng. Rà pin S1 của #19 nếu source blob hoặc nguồn chuẩn thay đổi. Main di chuyển làm manifest S4 và snapshot GOV-02 cần kiểm lại baseline. |
| #13 · S2 | `0235b5f9bb38d0d7e99a600188705d50977527f5` | Kiểm hai blob S2 và fixture được S3 ghim, ghi lại HEAD/tree của nguồn đã duyệt và chạy focused S3 nếu pin thay đổi. Rà lại #21 theo base mới và pin S2. |
| #19 · S3-D1 | `17ac45c1350776614e00ef0e14bdaf52b382b6ba` | Đối chiếu source D1 với HEAD Work đã kiểm và ba blob S3-D1. #21 phải refresh baseline và nguồn chuẩn trước khi xét tiếp. Nếu pin HEAD đổi, duyệt lại provenance và chạy assembly delta. |
| #21 · S4-D1 | `272855817cffe5334757fcf3a64cfae750b3b119` | Kiểm lại 12 pin sau các bước trước. Nếu ref PR bị xóa hoặc main tiếp tục dịch chuyển, lưu commit/tree nguồn bất biến và tạo snapshot được review riêng. Giữ gate Linux và connector thật độc lập. |

Đề xuất Codex là writer duy nhất cho `CATALOG.yaml` và `CHANGELOG.md` trong PR metadata riêng sau khi Điều phối duyệt. CATALOG thêm đúng ID/path đã có mặt trên base, CHANGELOG ghi verdict theo SHA. ChatGPT Điều phối sở hữu `STATE.md` và PR #6. Đề xuất thay `NO_TASK_YET` của ENG-01A bằng các đường dẫn S1–S4 đã xác minh, kèm trạng thái offline/Linux/real tách riêng. Chỉ điều chỉnh các dòng tương tự khi owner tương ứng xác nhận.

Rollback đề xuất tại mỗi bước là dừng chuỗi nếu base/pin/link đổi ngoài dự kiến, giữ SHA nguồn và evidence cũ, rồi làm lại preview và delta liên quan. Nếu metadata đã được merge mà có sai sót, owner chuẩn bị PR revert metadata, xác minh lại link và pin trước khi tiếp tục. Hoàn nguyên code chỉ bằng PR revert đã được duyệt khi cần. Không sửa lịch sử Git.

## Khoanh vùng xác minh

Fixture dùng repo Git tạm. Sáu nhóm lỗi gồm thiếu report/evidence/source, trùng ID, SHA drift hoặc object thiếu, kế hoạch cũ, production claim trái phạm vi và đánh dấu draft đã duyệt. Không chạy lại test lịch sử của các package, không dùng Actions, KVM2, scheduler, connector thật, production hoặc paid API. Chỉ draft PR GOV-02/S1 được cập nhật.
