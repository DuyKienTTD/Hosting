---
id: post61-ab-protocol
type: knowledge
status: draft
owner: Chat Dieu phoi
task_id: HOSTING-POST-61
lifecycle: ACTIVE
retention_trigger: complete the independent A/B and retain agreed regression fixtures
updated_at: 2026-11-25
sensitivity: public
---
# A/B READ_SET · hướng dẫn riêng cho Claude

[POST-03](../tasks/POST-03.md) · [Đề](PROMPTS.md) · [Đáp án dành cho người chấm](ANSWER_KEY.md) · [Bảng chấm](SCORECARD.md)

1. Giữ cùng mô hình, mức suy luận, project, Code Mode, quyền GitHub đọc, và bản đề trong từng cặp. Biến duy nhất là chính sách đọc ở ref được cấp. A dùng `097c080cc6d7fb3ca36b1849d9c10375d5cbd67f`, B dùng `c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb`. Mỗi phiên nhận một đề và một ref. Hai ref chỉ áp dụng cho Core/hồ sơ/Workflow, dữ kiện T1 pin riêng và giống nhau ở cả hai nhánh thử.
2. Mở tối thiểu 6 chat mới, mỗi ô T1–T3 × A/B một phiên, cùng cài đặt dự án. Ưu tiên 12 chat (hai cặp cho mỗi đề, đổi A→B/B→A). Tạo trước thứ tự từ phép hoán vị có seed, lưu seed và lịch thực tế, không tái dùng chat hoặc đáp án các lượt trước. Chỉ gửi nguyên văn phần chung đã thay placeholder ref và một đề tương ứng. Giữ nguyên quyền và đầu vào. Không cấp đường dẫn đáp án/bảng chấm cho phiên thử. Claude giữ đáp án riêng khi chạy; nếu phiên tìm được đáp án thì đánh dấu nhiễm và chạy cặp thay thế. Các tệp là công khai trong Git.
3. Mốc bắt đầu là gửi prompt, mốc cuối là final đầu tiên. Không nhắc ở lượt đầu. Lượt dừng sớm là final thiếu đầu ra bắt buộc trong khi phần thiếu còn khả thi và được phép; lỗi môi trường có bằng chứng ghi riêng. Nếu cần chạy lượt sau để chẩn đoán, lưu tách và ghi số nhắc.
4. Thu ref, role, phiên nhãn ẩn danh, timestamp, trạng thái final, điểm, sai lệch scope, số lần gọi và retry, các path/range đã mở, ký tự Unicode/UTF-8 của payload nguồn theo từng lần đọc và bộ tập hợp source duy nhất theo blob+ranges. Không suy ra telemetry thiếu từ thời lượng hay token ước tính. Tách độ dài bắt buộc theo định mức POST-04 và lượng đọc quan sát được.
5. Chấm đầu ra đã ẩn ref test nếu có thể, khóa điểm trước khi lộ cặp; giữ trích ngắn và liên kết nguồn. Báo từng cặp, mẫu số, mức giảm = (A−B)/A, completion và điểm theo cặp. Mốc nhận định ≥30% ở lượng đọc độc nhất, không giảm chất lượng hoặc tăng lỗi bắt buộc trong mẫu; mẫu nhỏ không chứng minh tác động toàn dự án. Session hỏng hoặc telemetry thiếu ghi PARTIAL/NOT_RUN, không loại im lặng.
