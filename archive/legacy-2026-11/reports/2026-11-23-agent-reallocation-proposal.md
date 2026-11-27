---
id: ttd-agent-reallocation-proposal-2026-11-23
type: report
status: proposed
updated_at: 2026-11-23
sensitivity: public-redacted
---
# Đề xuất phân bổ lại danh mục theo Agent

## Cơ sở và phạm vi
Đối chiếu danh mục trong PR #6 head 36745a2d3b308dbddc6faae6c67dab4c78943457, metadata main 116f25a887c0f1f08d144909cc05e30237d501fb lúc đọc, các hồ sơ trong agents/ và báo cáo khảo sát danh mục trong main. PR #6 là draft. Đây là phương án đề xuất, không thay đổi owner/status của task gốc, không phải bàn giao hoặc ACK thực thi cho bất kỳ Agent nào.

Phạm vi gồm 22 dòng portfolio của PR #6 và một task di trú Hermes hiện có trên main nhưng chưa có dòng riêng trong portfolio. Đếm số dòng chỉ là cách kiểm tra đủ phạm vi, không phải bằng chứng số giờ, mức sẵn sàng hoặc tải thực tế. Khả năng các Agent khác là hồ sơ và phản hồi được ghi nhận tại phiên trước, không được xác minh lại trực tiếp trong phiên Hostinger này. Quyền/capacity phải được xác nhận lại khi nhận việc. Hostinger trong phiên này đã đọc GitHub, hPanel/VPS, Docker, DNS và metadata WordPress; đã ghi và đọc lại một báo cáo trên main. Điều đó không chứng minh các thay đổi production hay di trú đã khả thi.

## Danh mục: một owner đề xuất cho từng dòng

| Dòng | Chủ trì đề xuất | Hỗ trợ/review | Pha và ranh giới |
|---|---|---|---|
| GOV-01 | ChatGPT điều phối | các Agent phản biện | Tổng hợp governance và phân bổ; không tự ký thay Agent khác |
| GOV-02 | ChatGPT điều phối | Codex làm validator khi có slot; Work review | Governance là đầu ra chính; kỹ thuật chia thành phần riêng, không kích hoạt đồng thời AI-02 |
| INF-01 | Hostinger Agent | Work review | Baseline hạ tầng chỉ đọc; không giả định monitoring liên tục |
| INF-02 | ChatGPT Work | Hostinger review thực tế hPanel | Runbook và tình huống giả; chỉ là gói phụ nhỏ sau AI-01 nếu Work còn sức |
| AI-01 | ChatGPT Work | ChatGPT nghiệm thu | QA độc lập theo head; tập trung phần chênh lệch, không lặp kiểm tra đã đạt nếu không có thay đổi |
| AI-02 | Codex | Hostinger cung cấp baseline khi cần; Work QA độc lập | Một gói kỹ thuật chủ động ưu tiên, preflight chỉ đọc và fake-only |
| AI-03 | ChatGPT điều phối | Work review; Hostinger dữ liệu hạ tầng | Tổng hợp bằng chứng và đề xuất quyết định; không tự phê duyệt thay chủ dự án |
| AI-03F | Codex | Work review, Hostinger tư vấn | Chờ AI-03 và phê duyệt riêng; không làm cùng AI-02 |
| AI-04 | Codex | ChatGPT gate, Hostinger/Hermes tư vấn | Chờ đủ điều kiện an toàn, quyền và phê duyệt riêng; không phát sinh paid trong đề xuất |
| SEC-01 | ChatGPT điều phối | Hostinger phần hạ tầng, Codex tư vấn ứng dụng, Work QA | Một owner cho chính sách/phân loại; Hostinger không đồng sở hữu toàn bộ deliverable |
| SEC-02 | Hostinger Agent | Codex review kỹ thuật, Work phản biện độc lập khi có slot | Thiết kế backup/restore và hardening; live phụ thuộc công cụ, quyền và phê duyệt |
| BIZ-01 | Hermes WebUI | Hostinger metadata WordPress; ChatGPT review | Discovery kênh và phạm vi; không giả định connector live |
| BIZ-02 | ChatGPT điều phối | Hermes hỗ trợ phân tích, Work review khi có slot | Ưu tiên use-case, KPI và giả định; đối chiếu BIZ-01 trước khi khóa feasibility |
| UX-01 | ChatGPT Work, đề xuất chuyển | ChatGPT cung cấp user stories và review; Codex feasibility | Work chỉ nhận sau AI-01; thiết kế/mock, không triển khai |
| ENG-01A | Codex | Hermes semantics; Work QA độc lập | Thiết kế offline và fake adapter sau khi trống slot AI-02; không bắt buộc đợi paid Gate B |
| ENG-01B | Codex | Chủ tài khoản về quyền; Work QA độc lập | Connector thật khi đủ scope/consent/approval; không đồng thời với gói Codex khác |
| GROW-01 | Hermes WebUI | ChatGPT review nghiệp vụ | Brief/draft sau BIZ-01 khi có slot, không publish |
| GROW-02A | ChatGPT Work, đề xuất chuyển | ChatGPT chốt mục tiêu dữ liệu, Hermes tư vấn | Bản kế hoạch event/đo lường offline, sau khi Work xong gói chính; không cần ENG-01B |
| GROW-02B | Codex | Work xác nhận chỉ số và QA độc lập | Pipeline dữ liệu thật phụ thuộc quyền dữ liệu, connector và phê duyệt; nằm trong hàng đợi |
| OPS-01A | Hostinger Agent | Work dùng INF-02; ChatGPT review | Đề xuất health/SLO/triage offline; không hứa chạy nền hay cảnh báo live |
| OPS-01B | Codex | Hostinger phần hPanel, Work QA | Scheduler/monitoring live cần quyền, preflight, rollback và phê duyệt riêng |
| QA-01 | ChatGPT Work | ChatGPT hoặc Hermes review khi độc lập | Dùng chung bằng chứng QA, theo slot; không QA chính sản phẩm do Work làm |
| MIG-HERMES | Hostinger Agent | Codex kiểm tra tương thích và rollback; Work review | Tham chiếu task di trú hiện có trên main; chỉ đánh giá nguồn/đích và quyền, không nhập hoặc ghi đè |

MIG-HERMES là nhãn đề xuất trong báo cáo để dễ đọc, không tạo ID task chính thức. Task gốc về di trú cần tiếp tục giữ trạng thái đang bị chặn cho tới khi được đối chiếu và cập nhật riêng.

## Thay đổi trọng tâm so với PR #6
- UX-01: từ ChatGPT chủ trì nội dung người dùng và Work hỗ trợ thiết kế sang Work chủ trì một deliverable thiết kế/mock; ChatGPT vẫn cung cấp yêu cầu và review. Chỉ chuyển khi Work xác nhận có slot và phù hợp năng lực; đây là phương án, không tự sửa task.
- GROW-02A: từ ChatGPT chủ trì sang Work chủ trì bản kế hoạch đo lường offline, ChatGPT chịu trách nhiệm yêu cầu/KPI; nhường slot cho sau AI-01.
- SEC-01: quy một owner cho deliverable tổng là ChatGPT; Hostinger chỉ chịu trách nhiệm nội dung hạ tầng được yêu cầu, tránh giao hai owner mơ hồ.
- Di trú Hermes: bổ sung vào đánh giá portfolio qua task gốc thay vì tạo bản sao. Hostinger đánh giá hạ tầng/quyền; Codex hỗ trợ kiểm tra kỹ thuật; chưa hứa thực hiện di trú.
- Các nhiệm vụ code/live vẫn tạm xếp Codex theo thế mạnh được tài liệu mô tả, nhưng không kích hoạt cùng lúc hoặc chuyển sang Agent chưa xác minh năng lực chỉ để làm đều số lượng.

## Tải theo đợt đề xuất
- Lượt đầu: ChatGPT GOV-01; Codex AI-02; Work AI-01 và nếu còn năng lực thì INF-02 hẹp; Hermes BIZ-01; Hostinger INF-01. Đây là thứ tự đề xuất, không khẳng định các Agent đang online hoặc đã nhận việc.
- Sau lượt đầu: Work chọn UX-01 hoặc GROW-02A, không mở cả hai cùng lúc; Hermes chọn GROW-01 hoặc tư vấn nhỏ; Hostinger chọn SEC-02 thiết kế hoặc đánh giá MIG-HERMES. Codex chọn ENG-01A hoặc gói validator GOV-02 theo mức ưu tiên thực tế.
- Các mục AI-03F, AI-04, ENG-01B, GROW-02B, OPS-01B là tương lai/có điều kiện, không cộng vào tải đang chạy. Một gói kỹ thuật Codex tại một thời điểm là giả định giới hạn kế hoạch phù hợp phản hồi trước, không phải SLA hay capacity đã xác minh của phiên mới.
- Số dòng dự kiến: ChatGPT 5, Codex 7, Work 5, Hermes 2, Hostinger 4. Danh mục không cân bằng về số vì công việc kỹ thuật chuyên sâu chưa có owner thay thế được xác minh; tránh dồn tải bằng xếp hàng, tách thiết kế/QA và chỉ giao sau xác nhận năng lực. Số dòng không tương đương giờ công.

## Phụ thuộc và an toàn
AI-01 + AI-02 và dữ liệu hạ tầng liên quan cung cấp đầu vào cho AI-03; AI-03F và AI-04 cần điều kiện cùng phê duyệt riêng. GROW-02A, UX draft và thiết kế ENG-01A có thể chuẩn bị độc lập với paid inference khi đầu vào cần thiết đã có. Các thay đổi production, khôi phục, ghi đè dữ liệu, dịch vụ, connector thật và API trả phí không nằm trong phạm vi đề xuất này. Bằng chứng giả lập không xác nhận an toàn production.

## Giới hạn
Chưa đọc mọi evidence và cập nhật lịch sử của mọi task; phân bổ dựa trên danh mục và hồ sơ, không khẳng định đầy đủ năng lực thực tế hay các Agent đã nhận nhiệm vụ. Chưa thực hiện di trú, chạy workflow, sửa website hoặc giao việc trực tiếp; chỉ tạo báo cáo đề xuất này.
