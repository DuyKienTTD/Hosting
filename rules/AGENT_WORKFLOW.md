---
id: multi-agent-handoff
type: rule
status: current
updated_at: 2026-11-21
sensitivity: public
---

# Quy ước chung: giao việc và bàn giao qua GitHub

Áp dụng cho Codex, ChatGPT Work và mọi tác nhân có quyền truy cập repository. Mục đích: **GitHub là nơi lưu tài liệu làm việc và kết quả có thể truy xuất**, còn tin nhắn giao việc chỉ cần ngắn gọn và dẫn link. Không áp đặt kỹ thuật triển khai, cấu trúc code hay checklist cứng khi không cần.

## 1. Nguồn chính, không dựa vào lịch sử chat

- Bắt đầu từ [README](../README.md) -> [PROJECT](../PROJECT.md) (mục tiêu) -> [STATE](../STATE.md) (tiến độ) -> [CATALOG](../CATALOG.yaml) (danh mục) -> [AGENTS](../AGENTS.md) (quy tắc).
- Chỉ đọc tài liệu chi tiết của công việc đang được giao. Nếu thiếu dữ liệu, tìm trong repository, rồi xác minh tại hệ thống live nếu có quyền.
- GitHub phản ánh lần kiểm tra/báo cáo cuối; trạng thái thực của VPS, WordPress, n8n, Hermes, Google Ads... phải kiểm tra lại khi có thay đổi theo thời gian.
- Không tự suy diễn rằng quyền truy cập GitHub cũng là quyền thay đổi các hệ thống production.

## 2. Giao nhiệm vụ: tài liệu đầy đủ trên Git

- Người tạo nhiệm vụ lưu **đặc tả đầy đủ** vào `tasks/` (ví dụ `tasks/2026-11-21-n8n-hermes-integration-audit.md`), commit/push rồi gửi **URL trực tiếp + hướng dẫn một đến hai câu** cho tác nhân nhận việc.
- Không cần gửi lại nguyên văn đặc tả trong chat nếu đường dẫn truy cập được.
- Tối thiểu trong task: mục tiêu/kết quả mong muốn, bối cảnh/link nguồn, phạm vi/giới hạn quyền, tiêu chí nghiệm thu có thể kiểm chứng, nơi nộp kết quả. Các bước kỹ thuật chỉ là gợi ý trừ khi là ràng buộc bắt buộc.
- Tác nhân có quyền tự chọn công cụ, phương pháp và thứ tự tối ưu; chủ động giải quyết vướng mắc không trọng yếu. Không xem danh sách phương pháp là khóa cứng.
- Nếu không thể đọc link, nói rõ bị chặn và yêu cầu quyền hoặc phương án truy xuất khác; không bịa nội dung.

## 3. Khi tác nhân làm việc

- Xác nhận branch/commit của tài liệu nhận việc và trạng thái hiện hành; tránh ghi đè kết quả tác nhân khác.
- Phân biệt **đã đo/đã làm**, **đề xuất**, **chưa kiểm chứng**, **bị chặn** và **không thực hiện**.
- Được thực hiện công việc trong phạm vi đã giao. Các thao tác có thể phá hủy dữ liệu, làm gián đoạn dịch vụ, thay đổi chi phí/ngân sách hoặc xuất bản phải có ủy quyền cụ thể.
- Nếu phát hiện thiếu quyền hoặc phụ thuộc bên ngoài, ghi BLOCKED rõ nguyên nhân, bằng chứng và hướng xử lý; vẫn hoàn thành phần độc lập có thể làm.
- Tránh thiết kế thêm quy trình hành chính, biểu mẫu và phê duyệt không đem lại lợi ích thực tế.

## 4. Bàn giao: báo cáo được push lại GitHub

- Lưu **báo cáo có bằng chứng** trong `reports/` với ngày và mã task liên quan. Các tài sản kết quả (code, script, cấu hình mẫu, artifact phù hợp Git) lưu ở thư mục tương ứng và dẫn link từ báo cáo.
- Báo cáo tối thiểu: task/link; thời điểm; phạm vi thực tế; thay đổi đã thực hiện và nơi triển khai; kết quả kiểm thử (PASS/FAIL/BLOCKED); bằng chứng/log đã làm sạch; rủi ro còn lại; bước tiếp theo.
- Cập nhật `STATE.md` khi trạng thái dự án đổi, `CATALOG.yaml` khi thêm tài liệu có thẩm quyền, `CHANGELOG.md` khi có thay đổi đáng kể. Đừng viết lại báo cáo lịch sử để che dấu lỗi.
- Commit và push lên repository/nhánh được giao, xác minh đã xuất hiện trên remote. Nếu không được quyền push, cung cấp bản vá/tài liệu và ghi trạng thái `NOT_PUSHED`.
- Tin nhắn bàn giao chỉ cần: **kết quả ngắn + link báo cáo + link commit/PR + việc còn vướng**. Không cần dán lại toàn bộ báo cáo.

## 5. Cập nhật đồng thời và xung đột

- Mỗi tác vụ nên có file task và report riêng; ưu tiên branch/PR khi nhiều tác nhân cùng sửa hoặc thay đổi mã vận hành.
- Trước khi push, lấy trạng thái mới của nhánh, kiểm tra diff và hòa giải xung đột. Không force-push ghi đè công việc người khác.
- Khi xung đột thông tin, tài liệu có bằng chứng xác minh mới hơn và hệ thống live được ưu tiên, nhưng phải lưu vết thay đổi.

## 6. Bảo mật và tính linh hoạt

- Tuân thủ [quy tắc repository](REPOSITORY_SECURITY.md); thông tin nhạy cảm đã được chủ sở hữu quản lý, nhưng mọi dữ liệu **mới** trước khi commit phải được rà soát.
- Không tự ý đưa bí mật hoặc dữ liệu cá nhân chưa được xử lý lên repository public.
- Được đề xuất sửa quy ước nếu gây cản trở thực tế; giải thích lý do trong commit/report. Quy tắc này đặt **đích đến và tiêu chuẩn chứng cứ**, không áp đặt một lối làm việc duy nhất.

## Mẫu lời giao việc cực ngắn

> Đọc https://github.com/DuyKienTTD/Hosting/blob/main/README.md và tài liệu task tại [URL]. Thực hiện trong giới hạn nêu ở task; đẩy báo cáo, bằng chứng và cập nhật trạng thái lên GitHub. Trả lại các URL kết quả.

## Mẫu lời bàn giao cực ngắn

> Task: [mã]. Kết quả: [PASS/PARTIAL/BLOCKED]. Báo cáo: [URL]. Commit/PR: [URL]. Việc cần quyết định: [nếu có].


## 7. BẮT BUỘC: điều phối dựa trên tri thức và bằng chứng trước khi giao thực thi (bổ sung 2026-11-21)

**Quy tắc này áp dụng cho ChatGPT, Codex, Hermes, Hostinger Agent và mọi AI tham gia qua GitHub hoặc chuyển tiếp thủ công.** Mọi agent **phải đọc lại** `AGENTS.md`, quy tắc này, `STATE.md`, `CATALOG.yaml`, `rules/REPOSITORY_SECURITY.md`, hồ sơ năng lực của mình và task liên quan **khi bắt đầu nhiệm vụ mới**, không chỉ dựa vào chat hay trí nhớ phiên trước. Agent nhận việc phải nêu rõ commit/phiên bản quy tắc đã đọc; nếu không thể đọc, `BLOCKED_RULE_ACCESS` trước thao tác có tác động.

### 7.1. ChatGPT chịu trách nhiệm tổng hợp kiến thức và nghiên cứu

- **Trước khi soạn task/ra phương án**, đọc trạng thái, chứng cứ mới nhất, phạm vi quyền; đặt các câu hỏi chuyên môn **có mục đích rõ** cho Hostinger Agent (hosting/VPS/hPanel/network), Hermes (runtime/inference/tool/serialization), Codex (mã/code/test) theo thế mạnh và bằng chứng năng lực ở `agents/README.md`.
- **Tự nghiên cứu thêm tài liệu công khai có thẩm quyền** của vendor/chủ dự án công nghệ (official docs, API reference, release notes, standards); ưu tiên phiên bản/endpoint thực tế đang dùng. Ghi URL, ngày kiểm tra, phiên bản áp dụng, điểm rút ra và khác biệt với runtime. Chỉ dùng nguồn cộng đồng như tín hiệu bổ sung; không dùng bài cũ làm bằng chứng trạng thái live.
- **Đối chiếu chéo** câu trả lời agent + tài liệu công khai + evidence runtime; phân tách `VERIFIED_LIVE`, `VERIFIED_MOCK`, `REPORTED`, `DOCUMENTED`, `UNKNOWN`, `BLOCKED`. Báo cáo agent không mặc nhiên là sự thật live; tài liệu hãng không chứng minh credential/permission đã bật.
- **Nếu có thể tự thu thập bằng công cụ hiện hữu thì làm trước;** nếu không có đường truy cập trực tiếp đến Hermes/Hostinger, tạo câu hỏi cụ thể và thông điệp chuyển tiếp qua kênh đã kiểm chứng. `TASK_COMMITTED` không phải `SENT`, `SENT` không phải `ACCEPTED`, `ACCEPTED` không phải `RUNNING` hay `DONE`. Không nói đã yêu cầu agent thực hiện nếu mới chỉ viết file GitHub.
- Không tạo nhiệm vụ Codex để Codex khảo sát lại những dữ kiện Hostinger/Hermes đã có thể báo cáo. Codex cần được giao việc triển khai/kiểm thử dựa trên thông tin đầu vào đã xác minh, đồng thời vẫn được dùng suy luận kỹ thuật ở điểm khó.

### 7.2. Đặc tả phải chỉ rõ cách bắt đầu, không chỉ nêu mục tiêu

Một task kỹ thuật/đa agent có tác động hoặc phụ thuộc phức tạp phải trả lời rõ:
1. **Vì sao và kết quả nào:** vấn đề, mục tiêu đo được và điều kiện DONE/PASS.
2. **Bối cảnh chính xác:** current task ID, branch/commit, môi trường/phiên bản, file/endpoint cần xem, evidence đã PASS để tránh làm lại.
3. **Điều kiện bắt đầu:** cần quyền gì, cần môi trường Linux/Windows nào, key/connector nào phải xác minh **không lộ giá trị**, backup/rollback, giới hạn chi phí và dữ liệu.
4. **Bắt đầu từ đâu và làm thế nào:** bước đầu tiên cụ thể (mở file nào, đối chiếu cấu hình nào, chạy kiểm tra chỉ đọc nào), thứ tự kiểm tra phụ thuộc, phương án test offline/mock trước khi ghi live; lệnh minh họa an toàn khi hữu ích. Không hướng dẫn giả định quyền chưa có; không áp đặt cứng giải pháp triển khai nếu agent phát hiện phương án tốt hơn trong giới hạn.
5. **Ai làm phần nào:** một owner cho từng đầu ra; Hostinger/Hermes báo cáo đầu vào trước khi Codex viết mã nếu việc đó giúp tránh mò mẫm; các agent khác làm reviewer/consultant theo khả năng thật.
6. **Kiểm thử và điểm dừng:** positive/negative/fault cases quan trọng, cách đo, evidence/link cần giao; trường hợp STOP và điều kiện phải xin duyệt.
7. **Bàn giao tiếp theo:** agent/người nhận, artifact URL, quyết định cần đưa ra, trạng thái đã gửi/đã nhận; không viết mơ hồ \"tiếp tục\" hoặc \"xử lý đi\".

Với công việc nhỏ đã rõ, có thể rút ngắn nhưng **không bỏ owner, bước bắt đầu, nghiệm thu, giới hạn quyền và nơi nhận kết quả**.

### 7.3. Chuyền bóng không được rơi: giao/nhận/hoàn thành có chứng cứ

- Mỗi lượt chuyển giao có tối thiểu: `task_id`; `from_agent`; `to_agent` **một người chịu trách nhiệm chính**; `why_this_agent`; `objective`; `first_action`; `inputs_and_urls`; `constraints_and_approval`; `acceptance`; `deliverable_path`; `next_owner_or_decision`; `handoff_state`.
- Trạng thái bàn giao: `PREPARED` (file đã tạo), `SENT` (gửi qua kênh thực có bằng chứng), `ACKNOWLEDGED` (agent nhận và xác nhận), `IN_PROGRESS`, `DONE`, `BLOCKED`, `NEEDS_OWNER_DECISION`. GitHub commit đơn thuần chỉ là `PREPARED`.
- Agent nhận việc đọc lại quy tắc và task, đối chiếu quyền/runtime, xác nhận đầu vào đã nhận, báo `ACKNOWLEDGED` khi có kênh phản hồi. Agent giao việc theo dõi đúng kênh, không giả định agent kia chạy nền. Nếu không có kênh gửi/nhận trực tiếp, chủ dự án chuyển link và ghi rõ `PREPARED_FOR_OWNER_FORWARD`.
- Khi `BLOCKED`, agent phải ghi **tác động, bằng chứng, owner giải quyết, first action an toàn, tiêu chí gỡ chặn**; phần độc lập đã PASS giữ nguyên. Không tạo liên tục nhiều task con cho cùng blocker nếu task hiện tại đủ phạm vi.
- Khi `DONE`, report/link/commit, phần chưa kiểm chứng, owner kế tiếp và việc cần duyệt được ghi rõ. Không chuyển bóng ngầm hoặc tự đổi owner.

### 7.4. Phân vai theo năng lực, không theo thói quen

- **ChatGPT:** research chính thức + đối chiếu nguồn, tổng hợp báo cáo chuyên gia, thiết kế kiến trúc/phương án, ra đề thực thi có điểm bắt đầu, nghiệm thu và điều phối/ghi quy tắc bền vững. Không tự nhận quyền VPS hoặc phê duyệt chi phí.
- **Hostinger Agent:** hPanel/hosting, VPS health, tài nguyên, Docker/network từ control plane, DNS/firewall/backup, khả năng và quy trình thao tác chính thức. Chỉ báo trạng thái live khi đã dùng công cụ live; đổi cấu hình theo quyền riêng.
- **Hermes Agent:** agent runtime, session/tools, request serialization, behavior, provider compatibility và reasoning/tool analysis; phân biệt Hermes WebUI với auxiliary KVM2 và production runtime.
- **Codex:** code review, viết mã, unit/integration/E2E, Docker Compose/config, triển khai sandbox/rollback, CI và chứng cứ kỹ thuật; không bị biến thành agent khảo sát mọi dịch vụ khi có chuyên gia phù hợp.
- **n8n:** orchestration/scheduling/runtime job-state khi workflow đã triển khai/được bật; không phải AI chuyên môn hoặc quyền cấp phép.
- Phân vai là **ưu tiên dựa trên khả năng đã kiểm chứng**, không độc quyền; đổi owner theo công cụ thực tế và giải thích trong handoff.

### 7.5. Quy tắc mới phải được ghi ngay vào kho tri thức

- Khi chủ dự án đưa ra **nguyên tắc chung, thay đổi cách phối hợp, điều kiện nghiệm thu hoặc bảo mật**, agent điều phối phải sửa `rules/AGENT_WORKFLOW.md` và/hoặc quy tắc chuyên đề tương ứng, đồng bộ `AGENTS.md`/agent profiles khi cần, `CATALOG.yaml`, `CHANGELOG.md`, entrypoint liên quan; commit/push rồi **đọc lại xác minh**. Tin nhắn chat chỉ giải thích, **không thay việc cập nhật tri thức**.
- Ghi rõ: quy tắc mới là `APPROVED_BY_OWNER` nếu chủ dự án chỉ thị; đề xuất chưa duyệt là `PROPOSED`. Không suy diễn quy tắc mới thành quyền thao tác production/paid API.
- Trong mọi thông điệp giao việc sau đó nhắc: \"Đọc `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml` và hồ sơ agent trước khi làm. Ghi commit rule đã đọc và tuân thủ quy tắc chung.\"
- Cập nhật quy tắc nên ngắn gọn đủ vận hành, không sản xuất thêm tài liệu hành chính dư thừa. Nếu thiếu quyền GitHub, cung cấp patch chính xác + trạng thái `NOT_PUSHED`, không nói đã cập nhật.

### 7.6. Không ghi đè task chính khi bàn giao tham vấn

- **Không ghi đè task chính khi bàn giao tham vấn (H1/H2).** Agent tư vấn chỉ tạo report/evidence riêng và bổ sung link/status handoff vào mục phù hợp, không tự đổi owner, status, approval scope hoặc thay toàn bộ nội dung task mẹ. Chỉ chủ dự án hoặc owner được ủy quyền mới thay đổi các trường quyền hoặc đóng task mẹ; các nhiệm vụ paid vẫn BLOCKED cho tới nghiệm thu theo gate.
- Trước khi `update_file`, phải fetch phiên bản mới và review diff để không xóa mục tiêu, điều kiện an toàn hay kết quả agent khác. Nếu xảy ra overwrite, phục hồi nội dung task mẹ từ commit xác minh được, giữ report lịch sử và ghi rõ sửa đổi trong changelog.

### 7.7. Ví dụ áp dụng cho GATE B (không cấp quyền mới)

- **Hostinger Agent (consult, read-only):** bắt đầu từ inventory và live hPanel/VPS network; báo bridge có thể truy cập proxy Level 2 qua interface/network nào, topology cô lập đề xuất, thao tác nào đòi approval và test no-bypass. **Không sửa network/firewall/DNS**.
- **Hermes Agent (consult, read-only):** đối chiếu chính xác runtime auxiliary và serialized Responses request/cap/token/credential requirements; mô tả cách khóa fingerprint trên bytes cuối, cái gì đã mock PASS vs còn UNKNOWN. **Không dispatch paid**.
- **ChatGPT:** nghiên cứu Docker networking/Compose chính thức và OpenAI Responses/token-counting; đối chiếu hai report, xác định phương án và kiểm tra quyền, sau đó mới giao Codex cách bắt đầu, tests và rollback.
- **Codex:** sau khi nhận input, sửa sandbox network/guard theo task đã có và approval hiện hành, chạy negative network tests, mock E2E và bằng chứng. Paid GATE B vẫn `BLOCKED_PREFLIGHT` cho tới khi các điều kiện ADR-P0-003 được chứng minh; không mở thêm quyền nhờ quy tắc này.

## Tham khảo công khai được dùng khi cập nhật quy tắc

- OpenAI Agents SDK: https://developers.openai.com/api/docs/guides/agents/sdk (agent ownership, orchestration/handoffs, guardrails).
- OpenAI Handoffs: https://openai.github.io/openai-agents-python/handoffs/ (truyền ngữ cảnh, quyền phải kiểm tra trước side effects).
- OpenAI Guardrails: https://openai.github.io/openai-agents-python/guardrails/ (giới hạn kiểm tra ở ranh giới agent/tool).
- OpenAI Tracing: https://developers.openai.com/api/docs/guides/agents/integrations-observability (theo dõi tool calls, handoffs, kiểm tra).
- Google SRE incident response: https://sre.google/workbook/incident-response/ (rõ vai trò và kênh liên lạc).
- Google SRE managing incidents: https://sre.google/sre-book/managing-incidents/ (handoff phải rõ người nhận và xác nhận).

Đây là **nguyên tắc quản trị dự án**, tham khảo từ tài liệu công khai; không có nghĩa dự án đã cài OpenAI Agents SDK hoặc Google SRE tooling.

## 8. BẮT BUỘC: chống thao tác sai, tránh làm lại và kiểm tra toàn vẹn tri thức (chỉ thị chủ dự án 2026-11-21)

Áp dụng **ngay cho mọi agent**. Đây là kiểm soát **trước, trong và sau** thực thi, không chỉ là checklist khi viết báo cáo. Đơn giản hóa quy trình nếu tác vụ nhỏ, nhưng không miễn các ranh giới bảo toàn dữ liệu/quyền hoặc độ trung thực của bằng chứng.

### 8.1. Đọc ĐỦ tài liệu trước khi kết luận — không dự đoán nội dung bị cắt

- Với từng tài liệu làm căn cứ ra quyết định/đặc tả/sửa đổi: kiểm tra **đúng đường dẫn, branch, commit/SHA, kích thước hoặc giới hạn kết quả**, đọc **đủ toàn bộ phần liên quan** (đặc biệt metadata, quyền/approval, STOP, dependencies, acceptance, handoff và các phần bổ sung cuối file). **Không dựa vào đoạn preview, nội dung bị truncation, 4.000 ký tự đầu hoặc tìm kiếm snippet để suy đoán phần còn lại.**
- Nếu công cụ trả thiếu/truncated, tiếp tục lấy các đoạn chưa đọc bằng phân trang/range/đọc tệp nguyên bản rồi đối chiếu đầu–cuối và section; nếu bất khả thi, ghi `PARTIAL_READ` cùng phần chưa đọc, **không xác nhận tài liệu đã đọc đủ**, không thực hiện thay đổi tác động vào tài liệu/phạm vi chưa hiểu.
- Trước khi kết luận, đọc tài liệu **hiện hành và liên kết bằng chứng quyết định**; kiểm tra cả bổ sung gần nhất ở cuối task/report. Không dùng kết luận một bản cũ nếu bản mới đã supersede hoặc đã thay đổi điều kiện.
- Trước khi cập nhật một file tồn tại: phải **đọc trọn file hiện tại**, không lấy nội dung cũ từ trí nhớ/session, không thay nội dung bằng bản tóm tắt; khi file rất lớn, đọc từng đoạn đủ bao phủ file hoặc dùng công cụ lấy toàn bộ. Không thể đọc trọn thì **không được overwrite**. Sau khi push: **đọc lại file đầy đủ hoặc xác minh nội dung bất biến bằng diff/hash/section checks**, không chỉ xem HTTP success.

### 8.2. Trước mỗi task: đối chiếu công việc đã làm để không tiêu hao lại

- Phải tạo **bảng trạng thái ngắn** ngay trong đặc tả (không tạo tài liệu riêng nếu không cần) phân loại: `DONE_VERIFIED`, `DONE_REPORTED`, `PARTIAL`, `FAILED`, `BLOCKED`, `NOT_RUN`, kèm **report/evidence URL, commit, môi trường, thời gian, phạm vi test**.
- **Không yêu cầu chạy lại** phần `DONE_VERIFIED` khi cùng phiên bản mã, cấu hình, topology, dữ liệu và tiêu chí nghiệm thu. Nếu trạng thái có thể đổi theo thời gian, dùng kiểm tra **nhẹ nhất cần thiết** (health/diff/read-only) thay vì chạy lại toàn bộ suite.
- Chỉ rerun khi **có điều kiện thay đổi có thể ảnh hưởng kết quả**, bằng chứng thiếu/không đúng phạm vi, lỗi mới, test không tái lập hoặc yêu cầu xác minh độ tươi trước thao tác rủi ro. Nêu rõ `change_trigger`, test bị ảnh hưởng, lý do, chi phí/tác động dự kiến; ưu tiên targeted tests trước full suite. Không viện dẫn \"chắc ăn\" hoặc \"kiểm tra lại tất cả\" nếu không có cơ sở.
- Không phủ định historical PASS chỉ vì agent mới không tự chạy lại; không nâng historical PASS thành live PASS cho topology khác. Reuse evidence có **điều kiện tương đương rõ ràng**.
- Khi xử lý BLOCKED: chỉ làm phần thiếu và phần bị ảnh hưởng theo dependency graph; tránh tạo task con/checkpoint trùng lặp nếu task mẹ vẫn đủ phạm vi.

### 8.3. Thiết kế dữ liệu để khoanh vùng lỗi và giảm blast radius

- Tách dữ liệu theo **trách nhiệm và vòng đời**: `tasks/` chứa đặc tả/owner/approval; `reports/` và `reports/evidence/` chứa kết quả bất biến, có nguồn/thời điểm; `STATE.md` tóm tắt hiện tại; `CATALOG.yaml` lập chỉ mục duy nhất; `rules/` là chính sách; `inventory/` là snapshot cấu hình; `runbooks/` là hướng dẫn thao tác. Không thay task mẹ bằng báo cáo agent tư vấn.
- Mỗi artifact quan trọng có **stable ID**, owner, trạng thái, môi trường/commit/source, liên kết đến task và evidence, ranh giới `verified_at`/runtime version; dùng một **nguồn có thẩm quyền** cho mỗi sự kiện/trường, hạn chế sao chép trạng thái nhiều nơi. Bản tóm tắt phải trỏ nguồn và không tự biến thành bằng chứng.
- Dùng **write-set/ownership contract** trong task: agent được quyền sửa chính xác những path/section/field nào; mục nào chỉ đọc; owner nào phải phê duyệt. Với H1/H2 tư vấn: chỉ tạo report/evidence và thêm mục handoff khi được phép; **không sửa metadata** `owner/status/approval_scope/paid_inference_approval` của task mẹ. Không sửa file ngoài write-set dù có quyền Git chung.
- Chia module/test/ledger/state/secret theo boundary; thay đổi nhỏ, rollback được, có diff. Không trộn dữ liệu thử nghiệm vào ledger live; không dùng một file làm nơi vừa lưu cấu hình, vừa ghi kết quả thử nghiệm, vừa cấp quyền chi phí.
- Mỗi lỗi cần có `component`, `environment`, `task_id/run_id` hoặc hash an toàn, `code_config_version`, `observed`, `expected`, `evidence`, `next_owner`; đủ khoanh vùng mà không công khai IP/secret/payload. Chỉ tạo mã máy-readable mới khi thực sự giúp chẩn đoán, không gia tăng hành chính.

### 8.4. Trước khi sửa/push: kiểm tra thay đổi so với bản gốc

- **Pre-change:** ghi base SHA/commit, danh sách path được phép sửa (`write_set`), trường/section bất biến (`invariants`), backup/rollback nếu cần. `fetch latest -> read whole -> patch minimal -> compare diff -> validate -> push -> re-fetch`; nếu base SHA stale phải refresh, merge có ý thức, **không force overwrite**.
- **Review diff toàn bộ**, bao gồm deleted sections/metadata thay đổi, `git diff --check`, validators liên quan. Từ chối patch nếu xóa/đổi mục tiêu, owner, quyền, ngân sách, STOP, source hoặc evidence ngoài phạm vi. Với file quan trọng và diff lớn/đổi metadata: ưu tiên PR có review/CI; không khẳng định branch protection đang bật khi chưa kiểm chứng.
- **Post-change:** đối chiếu đầy đủ file/sections trước–sau, xác minh link, metadata, references, trạng thái báo cáo, Git remote SHA, an toàn thông tin. Nếu phát hiện sai: dừng tác vụ kế tiếp, khôi phục nội dung có chọn lọc từ commit chuẩn, **không xóa lịch sử và không che lỗi**; cập nhật changelog và owner liên quan.
- Mọi thao tác cập nhật tài liệu phải tuân thủ đồng thời `CONTRIBUTING.md`, `rules/REPOSITORY_SECURITY.md` và quy tắc này. Không coi `update_file` success hoặc test exit 0 là đã nghiệm thu đầy đủ khi chưa review invariants.

### 8.5. Mẫu ranh giới bắt buộc trong đặc tả (nằm trong task, không tạo nhiều biểu mẫu)

`READ_SET`: tài liệu/mã/evidence cần đọc đủ, ref/commit cụ thể. `PREVIOUSLY_VERIFIED`: các hạng mục và evidence có thể tái sử dụng. `WRITE_SET`: path, section/field được sửa. `DO_NOT_TOUCH`: production/approval/ledger/metadata hoặc dữ liệu khác. `FIRST_ACTION`: bước an toàn bắt đầu. `DEPENDENCIES`: điều kiện/công việc chuyên gia phải có trước. `TEST_DELTA`: chỉ test thay đổi và điều kiện bắt buộc, cùng lý do rerun. `INVARIANTS`: giá trị/trường phải giữ nguyên. `PASS`: phép đo/evidence. `STOP`: điểm dừng và owner xử lý. `HANDOFF`: ai nhận, kênh, trạng thái, link artifact.

### 8.6. Kiểm soát bằng công cụ — phân biệt đã áp dụng và cần triển khai

- **Hiệu lực ngay:** tất cả agent đọc đủ, lập phạm vi đọc/ghi, kiểm diff và xác minh sau push theo quy tắc này.
- **Có thể tự động hóa tiếp:** quy tắc GitHub ruleset/branch protection, yêu cầu PR review, status checks, CI validator kiểm metadata bất biến, uniqueness ID, links, diff xóa section, secrets, và phân quyền write-path. **Chưa coi các kiểm soát này là đã bật** nếu chưa có bằng chứng cấu hình GitHub thật; đề xuất triển khai riêng khi đủ quyền và có sự đồng ý của chủ dự án.
- Tài liệu tham khảo: Git diff https://git-scm.com/docs/git-diff ; GitHub rulesets https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets ; GitHub PR review https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-proposed-changes-in-a-pull-request .
