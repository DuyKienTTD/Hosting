---
id: multi-agent-handoff
type: rule
status: draft
updated_at: 2026-11-24
sensitivity: public
---

# Quy tắc vận hành Agent

Bản tinh gọn theo chỉ thị A0 ngày 24/11/2026; chỉ là candidate cho đến khi được tích hợp hợp lệ. Không tự cấp quyền. [Lịch sử và bằng chứng](../references/history/README.md).

## 1. Nguồn và quyền

Trước mỗi nhiệm vụ, xác minh HEAD main thực tế, đọc đầy đủ AGENTS, quy tắc này, REPOSITORY_SECURITY, STATE, hồ sơ vai trò và đặc tả chính xác; ghi commit/blob SHA. Dùng CATALOG như chỉ mục: công cụ kiểm toàn bộ cấu trúc, ID/path; Agent chỉ đọc các mục liên quan, không cần nạp cả danh mục vào ngữ cảnh. Đọc đầy đủ mọi nguồn làm căn cứ quyết định, bao gồm metadata, quyền, STOP, dependencies, acceptance và bổ sung cuối file. Nếu bị cắt, dùng phạm vi dòng liên tục trên cùng commit/blob, kiểm tra đủ đầu-cuối; nếu không đủ, PARTIAL_READ hoặc BLOCKED_RULE_ACCESS, không suy đoán hay sửa phạm vi chưa hiểu. Trước khi sửa file phải đọc trọn file.

GitHub là kho tri thức, không phải quyền runtime. Xác minh quyền từng phiên, task-specific approval, môi trường, chi phí, preflight và rollback trước side effect. A0 giữ quyền tài chính, production, merge và các quyền dành riêng; ủy quyền phải đúng phạm vi. Không tự kích hoạt từ file, trạng thái, comment hoặc kết quả mô phỏng.

## 2. Vai trò, ưu tiên và chi phí

Chat Điều phối là accountable delivery director, phân công và quản lý shared-write độc quyền; Trợ lý A0 là reviewer độc lập và chỉ đại diện trong phạm vi được ủy quyền. Điều phối tự làm phần phù hợp bằng công cụ có thật; chỉ giao Agent khi năng lực bổ sung được kiểm chứng. A1/A2/Work theo task và ACK thực tế; n8n là công cụ orchestration, không phải Agent có quyền phê duyệt. Không tự QA độc lập phần mình viết. Không giao trùng hoặc mở lại công việc đã xác minh.

KNG-01 routing: đọc [source snapshot](../program/current.json) và [release-state gate](../program/kng/release_state.py). Chỉ coi KNG effective sau phê duyệt A0 đúng candidate SHA/tree, merge method merge và independent authenticated remote main readback đúng merge commit/tree/hai parent theo thứ tự. Thiếu/mâu thuẫn/stale: NOT_EFFECTIVE, STOP new dispatch; nguồn main có hiệu lực trước đó vẫn kiểm soát. Source snapshot KNG_ONLY, A1 scoped author, Work source QA đã hoàn thành, không phải ACK nhiệm vụ mới. Công việc ngoài KNG HOLD trừ quyền riêng được xác minh. Không mở WS-04. Hostinger PAUSED (resume cần A0 và ACK), Hermes HOLD_NO_NEW_TASKS, Codex NOT_AUTHORIZED; không tự kích hoạt. Giữ các gate VPS/SEC, paid, production, GATE B và real ledger. Không suy diễn quyền từ báo cáo lịch sử.

Ưu tiên chi phí + thời gian + chất lượng + rủi ro. WHY_DELEGATE/COST_ROUTING ghi năng lực, công cụ, phương án rẻ hơn, quyền, reviewer và giới hạn. Codex chỉ ngoại lệ khi có ALTERNATIVES_CHECKED, WHY_ONLY_CODEX, MAX_SCOPE, ESTIMATED_COST_OR_CALL_CAP, STOP, ACCEPTANCE, INDEPENDENT_REVIEWER, A0_APPROVAL_ID; thiếu bất kỳ mục nào thì không dispatch. Hermes ngoại lệ cần chứng minh năng lực không thay thế và A0 duyệt cap token/USD. Không dùng token cộng dồn/ước tính làm invoice; đối soát usage/spend theo phạm vi. Không tìm cách vượt content_policy_blocked. Paid API, render/publish cần approved scope, cost cap, consent, credential, STOP và đối soát. Không tự retry paid hoặc side effect chưa chứng minh idempotency.

## 3. Đặc tả và giao việc

Lưu task trong tasks/, commit/push và gửi URL cố định theo commit + hướng dẫn ngắn. Đặc tả chỉ định đường dẫn báo cáo dự kiến hoặc nguồn roadmap quản lý kết quả; báo cáo dùng cùng TASK_ID, dẫn về đúng phiên bản đặc tả và bằng chứng. Điều phối cập nhật liên kết kết quả trong roadmap hoặc đặc tả thuộc quyền ghi; không yêu cầu Agent tìm nhiệm vụ/báo cáo trong CATALOG. Một owner chính cho mỗi deliverable; phân vai theo kỹ năng, công cụ, quyền thực tế, không theo danh xưng. Tự thu thập bằng chứng nếu có thể; tham vấn đúng chuyên môn khi cần, đối chiếu nguồn chính thức đúng phiên bản và evidence runtime, không coi tài liệu hãng là bằng chứng quyền live. Không giao Codex khảo sát lại đầu vào đã có.

Task phải nêu TASK_ID, OWNER, MODE, mục tiêu/outcome, FIRST_ACTION, BASE_SHA, READ_SET, PREVIOUSLY_VERIFIED, WRITE_SET, DO_NOT_TOUCH, DEPENDENCIES, TEST_DELTA, INVARIANTS, quyền/cost cap, STOP, rollback, ACCEPTANCE, EVIDENCE, NEXT_OWNER. Chỉ rõ môi trường, kỹ năng, tool, cách bắt đầu, positive/negative/fault cases, nơi nộp kết quả và fallback. Với task nhỏ có thể rút ngắn nhưng không bỏ owner, bước đầu, nghiệm thu, quyền và nơi bàn giao. Một writer trên mỗi path/field; tư vấn H1/H2 chỉ ghi report/evidence và handoff được phép, không sửa owner/status/approval task mẹ.

Handoff ghi task_id, from_agent, to_agent, why_this_agent, objective, first_action, inputs_and_urls, constraints_and_approval, acceptance, deliverable_path, next_owner_or_decision, handoff_state. PREPARED là tài liệu đã ghi; SENT cần kênh gửi thực; ACKNOWLEDGED cần receipt đúng task; IN_PROGRESS/DONE cần bằng chứng. Không có kênh thì PREPARED_FOR_OWNER_FORWARD; không giả định Agent chạy nền hoặc GitHub comment tự dừng runtime. Chuyển tiếp chính xác URL, không tạo task trùng.

## 4. Thực thi liên tục và STOP

Theo đuổi outcome toàn phạm vi đã duyệt, tự phân rã và tiếp tục phần an toàn độc lập, không xin duyệt vi mô. Điều kiện chưa kiểm tra là việc cần làm, không mặc nhiên là blocker. Không deploy/recreate/dispatch trước khi gate bắt buộc PASS. Dừng đúng side effect nếu thiếu quyền, preflight, rollback, chi phí, phát hiện drift/bypass/lộ bí mật hoặc nguy cơ production; tiếp tục phần độc lập an toàn. Không tự đổi owner, mở quyền hoặc tăng ngân sách. Chỉ trình A0 khi cần quyền dành riêng hoặc blocker không thể tháo gỡ hợp lệ.

BLOCKED ghi observed, evidence, tác động, owner, first safe action và điều kiện gỡ chặn; không gọi việc chưa làm là lỗi kỹ thuật. Có thể retry read-only/idempotent/mock an toàn có lý do. Handoff kết thúc khi DONE/PASS, BLOCKED cụ thể, NEEDS_OWNER_DECISION hoặc INTERRUPTED_BY_ENVIRONMENT; status update không đóng task. Checkpoint tối thiểu khi gián đoạn: task ID, evidence, phần chưa xong, first safe action. Không tuyên bố 24/7 khi runtime/scheduler/retry/recovery/alert chưa được xác minh.

## 5. Bằng chứng, kiểm thử và nghiệm thu

Đặc tả ghi trạng thái DONE_VERIFIED, DONE_REPORTED, PARTIAL, FAILED, BLOCKED, NOT_RUN kèm URL/commit/môi trường/thời gian/phạm vi. Reuse evidence tương đương; chỉ rerun khi change_trigger, thiếu bằng chứng, lỗi mới, không tái lập hoặc cần độ tươi trước thao tác rủi ro. Ưu tiên targeted tests; không phủ nhận historical PASS, không nâng mock/source/author report thành live hoặc QA độc lập. Phân biệt VERIFIED_LIVE, VERIFIED_MOCK, REPORTED, DOCUMENTED, UNKNOWN, BLOCKED, DESIGNED_NOT_RUN. Báo cáo tiến độ tách maturity/readiness, nêu nguồn, trọng số có căn cứ và sai số; không tính PR chưa merge là sản phẩm live. Nghiệm thu dựa trên khả năng sử dụng, outcome, evidence và reviewer khác tác giả; không dựa vào số test hoặc hình thức. Roadmap-level QA không miễn security/release gate.

## 6. Toàn vẹn dữ liệu và cập nhật (thay thế mục 8 cũ)

Tách tasks (đặc tả/quyền), reports/evidence (bằng chứng bất biến), rules (chính sách), inventory (snapshot), runbooks (thao tác), decisions (quyết định), references (tham khảo). Stable ID, nguồn, owner, verified_at và môi trường; một nguồn thẩm quyền mỗi sự kiện/trường. STATE là hiển thị dẫn xuất có provenance, CATALOG chỉ là registry tri thức dùng chung, không tự cấp quyền. Không đăng ký task, report hoặc evidence vào CATALOG hay các phân vùng của nó. Task ACK là sự kiện có ngày và receipt. Không trộn test với ledger live hoặc secrets. Lỗi cần component/environment/task/run/version, observed/expected, evidence, next owner; khử định danh.

Pre-change: fetch latest, đọc trọn file, pin base, write-set, invariants và rollback. Patch tối thiểu, review toàn diff kể cả phần xóa, metadata, quyền, ngân sách, STOP, source/evidence; kiểm diff, validators, links, secret. Không force-push, phá lịch sử, ghi đè stale hoặc ngoài write-set. Sau push kiểm remote SHA và nội dung bằng readback/diff/hash, không coi HTTP success/test exit 0 là nghiệm thu. Nếu sai, dừng phần phụ thuộc, phục hồi có chọn lọc và ghi changelog. Tuân thủ CONTRIBUTING và REPOSITORY_SECURITY; kiểm soát GitHub/CI chỉ được coi bật khi có bằng chứng thật.

Khi cập nhật canonical event/field, sinh STATE bằng công cụ đã kiểm chứng; cập nhật CATALOG chỉ khi tri thức dùng chung thay đổi, không sinh mục báo cáo từ sự kiện nghiệm thu. Bảo toàn marker và stable ID/path. Quy tắc mới cần A0 approval phù hợp, coordinator exclusivity, security QA, append-only evidence/changelog, cập nhật nguồn có thẩm quyền và các điểm đọc liên quan; không tự merge. Lịch sử phải xác minh theo commit gốc, không sửa hash cũ để tạo PASS.

## 7. Bàn giao và lưu lịch sử

Lưu report ngày/task trong reports/, artifact đúng thư mục, log đã khử dữ liệu nhạy cảm; ghi scope, thay đổi, tests PASS/FAIL/BLOCKED, evidence, residual risks, next owner. Commit/push đúng branch, verify remote, cập nhật nguồn trạng thái/index/changelog khi phù hợp. Không ghi đè report cũ, không tạo hồ sơ hành chính trùng. Tin nhắn bàn giao chỉ cần kết quả ngắn, report/commit/PR URL, blocker và next action.

Nội dung lịch sử được truy xuất khi cần bằng chứng qua [chỉ mục lịch sử](../references/history/README.md), không phải quyền mới hoặc luồng đọc bắt buộc.

## 8. Vòng đời tri thức — chống phình kho (chỉ thị A0 24/11/2026)

Chi tiết triển khai và validator: [Data Lifecycle & Context Management Protocol](DATA_LIFECYCLE_CONTEXT.md) (candidate).

Phân loại ngay khi tạo tài liệu: **DURABLE** (giữ lâu dài: quy tắc có hiệu lực, kiến trúc/ADR, đặc tả sản phẩm, hướng dẫn vận hành đã xác minh, mã/test hữu ích, nghiệm thu cuối và bằng chứng bắt buộc); **ACTIVE** (giữ đến khi đóng: task, roadmap, blocker, checkpoint và trạng thái đang dùng); **TEMPORARY** (dọn khi đóng: bản nháp, log thử, báo cáo tiến độ trung gian, phương án bị loại, các bản cập nhật cùng một thử nghiệm). Không biến tài liệu tạm thành tri thức lâu dài theo mặc định. Owner, task ID, loại lưu trữ và điều kiện hết hạn ghi trong metadata hoặc hồ sơ task hiện có; không tạo biểu mẫu riêng chỉ để phân loại.

Một mục đích có một nguồn chính. Cập nhật tài liệu hiện có hoặc log task, không tạo báo cáo/checkpoint mới cho mỗi lượt trao đổi. Chỉ tạo tài liệu độc lập khi có quyết định, artifact, bằng chứng bắt buộc hoặc kết quả có giá trị tái sử dụng mới. Không chép log dài, toàn bộ chat, nội dung quy tắc hay báo cáo cũ vào tài liệu vận hành. Dùng liên kết commit cố định; CATALOG là chỉ mục tra cứu, không là nội dung đọc tuần tự. Quy tắc mới phải hợp nhất hoặc thay thế điều khoản cũ, không nối thêm phiên bản mâu thuẫn.

Khi A0/Điều phối có thẩm quyền quyết định dừng một thử nghiệm/POC thất bại: đóng task, giữ **một báo cáo kết thúc ngắn, dễ hiểu** (mục tiêu, phiên bản/môi trường, kết quả thực tế, nguyên nhân đã chứng minh hoặc UNKNOWN, lý do dừng, bài học tái sử dụng, điều kiện duy nhất để mở lại nếu có, quyết định và liên kết bằng chứng thiết yếu). Mặc định tối đa một trang, dài hơn chỉ khi cần để bảo toàn an toàn hoặc nghĩa vụ kiểm toán. Không tạo thêm chuỗi báo cáo cho thử nghiệm đã đóng. Các báo cáo cập nhật/trung gian không còn giá trị độc lập phải xóa khỏi cây tài liệu hiện hành ngay trong đợt đóng, sau kiểm tra tham chiếu và phạm vi quyền; không chỉ đổi tên sang archive rồi để phình cây file. Có thể phục hồi bằng Git commit đã pin; không rewrite lịch sử.

Ngoại lệ bắt buộc giữ nguyên: phê duyệt/quyền/STOP, sự cố bảo mật hoặc dữ liệu, tài chính/kiểm toán, rollback, bằng chứng nghiệm thu độc lập, regression cần tái sử dụng và tài liệu còn dependency. Chỉ giữ phần thật sự thiết yếu và dẫn từ báo cáo kết thúc; không xóa khi retention/reference chưa rõ. Không ghi lại hash lịch sử hay làm mất provenance. Nếu xóa khiến link/ID hoặc validator hỏng, sửa tham chiếu về báo cáo kết thúc hoặc nguồn lịch sử bất biến, kiểm tra đầy đủ trước commit; không bỏ validator hoặc giả PASS. Chỉ thị A0 24/11/2026: tách đặc tả, báo cáo, bằng chứng khỏi CATALOG; giữ tệp nguồn và ID lịch sử tại commit gốc. Dọn backlog/xóa tệp nguồn là phạm vi riêng; không tự xóa. ID lịch sử không tái sử dụng.

Điều phối chịu trách nhiệm dọn ngay khi đóng task/POC và rà soát tại cuối mỗi milestone: tài liệu trùng, ACTIVE đã đóng, TEMPORARY hết vòng đời, link hỏng, ID trùng, quy tắc mâu thuẫn. Đo số tài liệu đang hoạt động, số TEMPORARY tồn đọng và kích thước luồng đọc bắt buộc trước/sau; mục tiêu không có TEMPORARY hết hạn chưa xử lý (ngoại lệ có lý do/owner), không tăng luồng đọc nếu chỉ bổ sung lịch sử. Không tạo một dự án báo cáo định kỳ mới chỉ để theo dõi việc dọn. Nghiệm thu cleanup bằng diff, link/ID check, preservation checks và remote readback; reviewer độc lập khi ảnh hưởng rule/authority/security.
