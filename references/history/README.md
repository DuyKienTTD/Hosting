# Kho tham khảo lịch sử HOSTING

Không phải nguồn cấp quyền hay danh sách công việc đang chạy. Bảo toàn nguồn gốc trên Git; không xóa bằng chứng bắt buộc hay tái sử dụng ID. Báo cáo tạm hết vòng đời được loại khỏi cây hiện hành theo mục 8 của quy tắc vận hành. Các liên kết dưới đây cố định commit.

| Nội dung | Nguồn nguyên bản |
|---|---|
| Quy tắc trước tinh gọn (265 dòng), §7.7 GATE B, §11–12 phân công lịch sử, §13 KNG | [AGENT_WORKFLOW.md](https://github.com/DuyKienTTD/Hosting/blob/d549564de52429e777c68daf9df7a93df5f22f27/rules/AGENT_WORKFLOW.md) |
| Hướng dẫn Agent trước tinh gọn | [AGENTS.md](https://github.com/DuyKienTTD/Hosting/blob/d549564de52429e777c68daf9df7a93df5f22f27/AGENTS.md) |
| Trạng thái KNG tại thời điểm tích hợp | [STATE.md](https://github.com/DuyKienTTD/Hosting/blob/d549564de52429e777c68daf9df7a93df5f22f27/STATE.md) |
| Danh mục 130 mục tại baseline | [CATALOG.yaml](https://github.com/DuyKienTTD/Hosting/blob/d549564de52429e777c68daf9df7a93df5f22f27/CATALOG.yaml) |
| Quy tắc và phân công PR31 | [AGENT_WORKFLOW.md](https://github.com/DuyKienTTD/Hosting/blob/a770de80a2467ca1789c820b63416209cf53b7d1/rules/AGENT_WORKFLOW.md) |
| Bằng chứng tích hợp KNG | [migration.json](https://github.com/DuyKienTTD/Hosting/blob/d549564de52429e777c68daf9df7a93df5f22f27/program/kng/migration.json), [provenance-lock.json](https://github.com/DuyKienTTD/Hosting/blob/d549564de52429e777c68daf9df7a93df5f22f27/program/kng/provenance-lock.json) |

Báo cáo và bằng chứng gốc vẫn tra cứu bằng CATALOG. Trạng thái current trong báo cáo có ngày không phải quyền hiện hành hoặc live telemetry.

## Giới hạn candidate 24/11/2026

A0 yêu cầu tinh gọn trên nhánh riêng, giữ CATALOG nguyên bản. Chỉ sửa AGENTS và workflow (bao gồm chính sách vòng đời); thêm chỉ mục này và changelog. STATE, security, CATALOG, current.json, migration, provenance và code giữ nguyên. Workflow giữ các ranh giới của §7–13, tách ví dụ, diễn giải lịch sử và routing cũ vào nguồn Git cố định. Chưa merge; không cấp quyền mới.

KNG validator hiện kiểm result_blob lịch sử với working tree; thay đổi hai file sẽ gây INTEGRATED_BLOB_MISMATCH. Không sửa pin hoặc bỏ kiểm tra để báo PASS. Trước tích hợp cần coordinator/reviewer xác minh lịch sử tại commit gốc và thiết kế validator phiên bản hiện hành, đồng bộ must_read trong typed source và hồ sơ Agent liên quan. Không tự nghiệm thu. Runtime tests NOT_RUN.

A0 bổ sung yêu cầu chống phình tri thức: xem [vòng đời tài liệu và đóng thử nghiệm](../../rules/AGENT_WORKFLOW.md#8-vòng-đời-tri-thức--chống-phình-kho-chỉ-thị-a0-24112026). Đây là chính sách candidate; chưa dọn backlog hay xóa báo cáo trong PR này.

## Tách tài liệu vận hành khỏi CATALOG (candidate)

[A0 baseline đầy đủ 130 ID](https://github.com/DuyKienTTD/Hosting/blob/d549564de52429e777c68daf9df7a93df5f22f27/CATALOG.yaml) giữ nguyên 16 task, 65 report, 33 evidence cùng metadata. CATALOG hiện hành candidate chỉ giữ 16 mục durable; không xóa tệp nguồn, không tái sử dụng ID. Chỉ thị mới thay thế yêu cầu giữ nguyên CATALOG trong đoạn lịch sử trên, không thay quyền merge/production.
