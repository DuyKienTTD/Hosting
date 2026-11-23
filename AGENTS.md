# Hướng dẫn cho tác nhân

Các hướng dẫn này áp dụng cho toàn bộ repository.

## Ưu tiên phân công hiện hành — A1 và Codex ngoại lệ (A0, 2026-11-23)

**Mục 11 [AGENT_WORKFLOW](rules/AGENT_WORKFLOW.md) có hiệu lực ưu tiên** khi tài liệu cũ gợi ý giao Codex theo thói quen. **A1 là ChatGPT Thông thường ở phiên riêng**, khác ChatGPT Điều phối và ChatGPT Work; xem [hồ sơ A1](agents/a1.md) và [master allocation v2](tasks/2026-11-23-a1-cost-first-master-allocation.md). Điều phối phải tự thực hiện hoặc giao A1/Work/Hermes/Hostinger nếu đủ năng lực/công cụ, Codex chỉ còn ngoại lệ theo gate chi phí có A0 duyệt. **Thu hồi phần giao Codex đơn giản chưa làm**, không xóa kết quả lịch sử. Mọi lệnh GitHub vẫn `PREPARED_FOR_OWNER_FORWARD` cho tới khi Agent ACK; không tự tạo phiên A1. Không có quyền mới cho paid, live, production, merge.

## A0 override — Hostinger PAUSED / A1 OPS D2 (2026-11-23)

**Hostinger Agent đang PAUSED:** không gửi thêm việc hoặc cho phép nối lại các work order SEC/OPS; [OPS pause](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7093337445), [SEC pause](https://github.com/DuyKienTTD/Hosting/pull/29#issuecomment-7093338761). Chỉ thị tạm dừng đã đăng trên GitHub, **chưa phải ACK của phiên Hostinger**; lịch sử và bằng chứng đã bàn giao được giữ nguyên. Chỉ A0 mới cho phép tiếp tục và cần Agent ACK mới.

**A1 là sole writer của OPS-01A/S2-D2**, qua [đặc tả A1](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7093346631): branch riêng stacked trên PR #24 tại `e9c2d8f759850ea9c654de7e103549e041f66679`, **không ghi vào branch Hostinger**; chờ A1 ACK và sau đó Work QA độc lập. A1 đã có role ACK và source/task evidence PR #32/#33; PR #32 Work QA offline PASS_WITH_LIMITS, PR #33 Hermes QA proposal PASS_WITH_LIMITS (không đồng nghĩa Phase B/merge). Codex vẫn exception-only.

## Mục tiêu

Trước khi nhận việc mới, nắm mục tiêu doanh nghiệp tại [PROJECT.md](PROJECT.md). Đặc tả và kết quả trao đổi qua GitHub theo [rules/AGENT_WORKFLOW.md](rules/AGENT_WORKFLOW.md): task được commit trước khi giao; báo cáo, bằng chứng được commit/push sau khi thực hiện; tin nhắn chỉ dẫn URL và kết quả ngắn. Dùng `tasks/` cho đặc tả và `reports/` cho kết quả. Các giới hạn nhiệm vụ là ràng buộc, còn cách triển khai là linh hoạt.

Giữ repository thành nguồn thông tin chung, ngắn gọn và đáng tin cậy để tác nhân mới có thể bắt đầu làm việc mà không phải đọc toàn bộ lịch sử chat.

Mỗi tác nhân phải tham khảo [agents/README.md](agents/README.md) và hồ sơ chính mình trước khi nhận việc. Không coi **Hostinger** (nền tảng) là một AI Agent; khả năng của **Hostinger Agent** cần khảo sát riêng. Hồ sơ chỉ ghi năng lực và bằng chứng, không tự tạo quyền truy cập. Khi giao việc cho tác nhân khác, xem hồ sơ của họ và kiểm tra quyền phiên hiện tại. Nhiệm vụ khảo sát: [TTD-AGENT-CAPABILITY-SURVEY-001](tasks/2026-11-21-agent-capability-survey.md). Chủ dự án có thể chuyển tiếp câu hỏi và báo cáo giữa các tác nhân; không đòi kết nối trực tiếp giữa các agent.

## Bắt buộc trước khi giao việc hoặc nhận việc

**Quy tắc điều phối do chủ dự án phê duyệt ngày 2026-11-21:** [AGENT_WORKFLOW mục 7](rules/AGENT_WORKFLOW.md) có hiệu lực cho ChatGPT, Codex, Hermes, Hostinger Agent và mọi agent tham gia. **Mỗi task mới phải đọc lại** `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, hồ sơ agent và task. Ghi commit quy tắc đã đọc trong ACK/report.

**Trước giao thực thi:** ChatGPT nghiên cứu nguồn công khai chính thức, đối chiếu trạng thái/bằng chứng; chủ động xin báo cáo Hostinger Agent về VPS/network/hPanel và Hermes về runtime/inference khi phù hợp, trước khi đề xuất giao **bất kỳ Agent** code/test/deploy; Codex chỉ exception-only theo A0 cost gate. Đặc tả phải có **bước đầu tiên cụ thể, file/endpoint/môi trường, dependency, owner duy nhất, quyền, kiểm thử/STOP, đường dẫn đầu ra và next owner**; không chỉ nói “làm đi”. Không giả định đã giao việc qua GitHub nếu agent chưa thật sự nhận.

**Chuyền bóng rõ ràng:** `PREPARED → SENT → ACKNOWLEDGED → IN_PROGRESS → DONE/BLOCKED/NEEDS_OWNER_DECISION`; mỗi lượt giao nêu `from_agent, to_agent, why, first_action, inputs, limits, acceptance, artifact, next_owner`. Nếu thiếu kênh giao trực tiếp, ghi `PREPARED_FOR_OWNER_FORWARD` để chủ dự án chuyển.

**Mọi quy tắc mới của chủ dự án phải được cập nhật ngay vào `rules/`, đồng bộ entrypoint, `CATALOG.yaml`, `CHANGELOG.md`, commit/push/read-back.** Lời nói trong chat không phải kho tri thức bền vững. Quy tắc mới không tự cấp thêm quyền production/paid API.

## Thực thi liền mạch trong phạm vi đã phê duyệt

**BẮT BUỘC áp dụng [AGENT_WORKFLOW mục 9](rules/AGENT_WORKFLOW.md):** chủ động hoàn thành toàn bộ phần hợp lệ có thể tiếp tục; điều kiện chưa kiểm tra là việc cần làm, không mặc nhiên là blocker. Chỉ dừng side effect khi safety/approval gate chưa PASS; handoff BLOCKED phải có blocker cụ thể. Không mở rộng quyền, không tự retry paid API và không giả định phiên chạy 24/7.

## Ủy quyền điều phối liên tục (chủ dự án 2026-11-22)

Theo [AGENT_WORKFLOW mục 10](rules/AGENT_WORKFLOW.md), ChatGPT tự quyết định và điều phối bước kế tiếp trong ranh giới task/ADR/an toàn đã có, không hỏi lại phê duyệt hình thức. Chỉ chuyển tới chủ dự án khi phát sinh vấn đề bảo mật/credential/quyền truy cập mà không tác nhân nào có hoặc nghĩa vụ chỉ chủ tài khoản thực hiện được. Không suy diễn quyền VPS/provider/production từ việc điều phối; mọi thay đổi phải có preflight, rollback, bằng chứng và STOP. Git commit `PREPARED` không phải Codex ACK.

## Bảo toàn tài liệu và chống làm lại

**BẮT BUỘC đọc và áp dụng [AGENT_WORKFLOW mục 8](rules/AGENT_WORKFLOW.md)** cho mọi nhiệm vụ: đọc **đủ** tài liệu liên quan (không dự đoán từ preview/truncated result), đối chiếu evidence công việc đã PASS, chỉ chạy lại khi có `change_trigger`/thiếu bằng chứng, và giới hạn file/section được sửa bằng `READ_SET`, `WRITE_SET`, `DO_NOT_TOUCH` cùng `INVARIANTS`.

Trước update: fetch phiên bản remote mới nhất, đọc toàn bộ tài liệu sắp sửa, xác minh owner/status/approval và base SHA, tạo patch tối thiểu, review **toàn bộ diff/deletions**. Sau commit/push: đọc lại từ remote và xác minh trường bất biến cùng nội dung liên quan. Không đổi metadata task mẹ khi chỉ được giao nhiệm vụ tư vấn. Khi bị truncation/không đọc được toàn bộ: đánh `PARTIAL_READ`, không tự kết luận hoặc ghi đè.

Mỗi đặc tả phải nêu đã làm gì, evidence nào còn áp dụng, test delta nào thật sự cần và phạm vi thao tác của agent. Ưu tiên định danh ổn định, dữ liệu tách theo trách nhiệm để khoanh vùng lỗi; không ghi secret trên Git public. Quy tắc này không chứng minh branch protection/CI đã bật và không tự cấp quyền chi phí/production.

## Thứ tự đọc bắt buộc

1. `README.md` — phạm vi và bản đồ repository.
2. `STATE.md` — trạng thái hiện tại, rủi ro và việc đang chờ.
3. `CATALOG.yaml` — tài liệu có thẩm quyền và vị trí cần đọc.
4. Tài liệu liên quan trực tiếp đến nhiệm vụ.
5. `rules/REPOSITORY_SECURITY.md` trước mọi commit hoặc push.

Không đọc toàn bộ `reports/` hoặc `archive/` nếu `CATALOG.yaml` không chỉ tới đó.

## Quy tắc nguồn sự thật

- Hệ thống trực tiếp là nguồn sự thật cho trạng thái thay đổi theo thời gian.
- `inventory/` là bản ghi hiện tại gần nhất, không thay thế việc xác minh live trước thao tác rủi ro.
- `STATE.md` là bản tóm tắt nhanh, không chứa toàn bộ chi tiết.
- Báo cáo có ngày trong `reports/` là bằng chứng lịch sử; tạo báo cáo mới thay vì sửa lại quá khứ, trừ khi sửa lỗi thực tế.
- `knowledge/` chứa kiến thức bền vững; không đặt số liệu vận hành dễ lỗi thời ở đây.
- Nếu hai tài liệu mâu thuẫn, ưu tiên tài liệu có `status: current` và `verified_at` mới hơn, sau đó xác minh live.

## Tìm thông tin nhanh

- Dùng `rg` hoặc `rg --files` trước khi duyệt thủ công.
- Tìm ID tài liệu trong `CATALOG.yaml`.
- Tìm trạng thái hiện tại trong `STATE.md` và `inventory/`.
- Tìm lịch sử thay đổi trong `CHANGELOG.md` và `reports/`.
- Tìm quy trình thao tác trong `runbooks/`.

## Khi thêm hoặc thay đổi thông tin

1. Phân loại tài liệu đúng thư mục.
2. Dùng tên file chữ thường, dấu gạch ngang; báo cáo có ngày theo `YYYY-MM-DD-chu-de.md`.
3. Thêm metadata theo mẫu tương ứng trong `templates/`; file chỉ mục và entrypoint được miễn metadata.
4. Cập nhật `CATALOG.yaml` nếu tài liệu là mới, đổi trạng thái hoặc thay thế tài liệu khác.
5. Cập nhật `STATE.md` nếu trạng thái vận hành, rủi ro hoặc việc đang chờ thay đổi.
6. Cập nhật `CHANGELOG.md` cho mọi thay đổi có ý nghĩa.
7. Kiểm tra bí mật, liên kết và `git diff --cached` trước khi push.

## An toàn

- Repository là công khai. Không commit bí mật hoặc định danh máy chủ thật.
- Không sao chép `.env`, log thô, database dump, backup hoặc output chứa token.
- Chỉ ghi tên biến môi trường; không ghi giá trị.
- Không mô tả một thay đổi là đã hoàn tất nếu chưa có bằng chứng xác minh.
- Không dùng tài liệu cũ làm quyền cho một hành động phá hủy; quyền phải đến từ yêu cầu hiện tại của người dùng.

## Tiêu chuẩn hoàn thành

Một nhiệm vụ cập nhật tri thức chỉ hoàn tất khi tài liệu đúng thư mục, metadata và catalog nhất quán, không có bí mật, changelog đã cập nhật, working tree sạch và commit đã có trên remote được yêu cầu.
