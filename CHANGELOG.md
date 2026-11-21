# Lịch sử cập nhật

## 2026-11-21

- ChatGPT đã nghiệm thu kết quả H3 `MOCK_E2E_PASS` từ report/evidence trên GitHub và bổ sung mục nghiệm thu vào task mẹ mà không thay owner/status/approval. Paid GATE B vẫn `BLOCKED_PREFLIGHT`; credential guard và token count theo final digest chờ xác minh, không rerun bài test mock đã PASS khi không đổi điều kiện.


- Lưu điểm tiếp tục GATE B sau H3, liên kết bằng chứng đã có và ghi điều kiện gỡ chặn. [Checkpoint](reports/2026-11-21-gate-b-h3-checkpoint.md).

- Chủ dự án ban hành quy tắc tránh thao tác sai/lặp lại: đọc đủ toàn bộ tài liệu liên quan trước khi suy luận hoặc sửa; rà evidence đã PASS và chỉ rerun theo change trigger; tách dữ liệu/ownership và write-set, bảo vệ metadata task mẹ; review toàn diff, xác minh remote post-push, dừng khi output truncated hoặc quyền chưa rõ. Đã cập nhật AGENT_WORKFLOW mục 8, AGENTS, CONTRIBUTING, README, template báo cáo và CATALOG; GitHub branch protection/CI chưa được xác nhận là đã bật.


- H3 PASS combined mock E2E trên KVM2 với callback, một dispatch và one-shot accounting trong cùng lượt. Xác nhận rollback, topology cách ly và ledger thật không đổi. Paid readiness chờ credential guard và token count theo provider. [Báo cáo](reports/2026-11-21-hermes-gate-b-h3-preflight.md).

- Tổng hợp H1 Hostinger và H2 Hermes để chuẩn bị H3 trong task GATE B hiện có: chẩn đoán replay bridge task_id vs runtime mismatch, khóa forwarded Responses digest và token-count cùng digest, yêu cầu rerun combined mock callback+one-shot trên isolated topology, guard-only OpenAI credential, không nhầm với service auth keys. H3 chuẩn bị cho Codex ở PREPARED_FOR_OWNER_FORWARD; chưa gửi/ACK, chưa paid dispatch.


- Khôi phục nhiệm vụ GATE B bị H1 ghi đè nội dung/owner/status trong commit `5b8dd629`: giữ nguyên quyết định paid một attempt ở `owner: codex`, `status: blocked`, và ghi kết quả H1 read-only đã nhận từ Hostinger. Phân biệt provider OpenAI key (guard-only) với hai service-auth keys cần dùng theo vai trò. Bổ sung quy tắc tránh agent tham vấn ghi đè task mẹ. H2 Hermes chưa ACK, GATE B chưa dispatch.
- Hoàn tất handoff H2 cho `TTD-HERMES-GATE-B-001`: thêm `reports/2026-11-21-gate-b-hermes-consult.md` và `reports/evidence/2026-11-21-gate-b-hermes-consult.json`, cập nhật task/STATE/CATALOG tương ứng.
- Kết luận H2: `HERMES_RUNTIME_MISMATCH` chưa chứng minh mismatch live; bridge có thể replay lỗi cũ theo `task_id`. Canonical permit/hash phải bind vào forwarded `/v1/responses` body sau guard, và contract `POST /v1/responses/input_tokens` phải dùng cùng input surface của request inference.

- Điều phối GATE B theo rule mục 7 sau egress isolation: xác minh report/evidence `88268989`; cập nhật task hiện có để chuẩn bị hai handoff H1/H2 Hostinger Agent và Hermes Agent sau egress isolation, ghi owner, cách bắt đầu, nguồn vendor, nghiệm thu, trạng thái PREPARED_FOR_OWNER_FORWARD; chưa gửi/ACK, chưa giao Codex thực thi, 0 paid call. Giữ GATE B BLOCKED_PREFLIGHT.


- Chủ dự án phê duyệt quy tắc điều phối mới: ChatGPT tự nghiên cứu tài liệu vendor chính thức, hỏi Hostinger/Hermes trước khi giao Codex theo đúng sở trường, đặc tả có bước bắt đầu cụ thể, nhận/giao bóng ghi owner và trạng thái ACK, mọi agent đọc lại AGENTS/workflow/security/STATE/CATALOG trước task. Đã cập nhật trực tiếp `rules/AGENT_WORKFLOW.md`, `AGENTS.md`, agent directory/profile, README, catalog; quy tắc không tự cấp thêm quyền paid/production. Nguồn tham khảo chính thức ghi trong rule.


- Cô lập proxy Level 2 trên mạng riêng với guard. Kiểm tra quyền truy cập từ sáu container, mock callback, hạch toán mock và rollback egress. Paid GATE B vẫn chờ credential và token count theo provider. [Báo cáo](reports/2026-11-21-hermes-gate-b-egress-isolation.md).

- Kiểm tra lại paid GATE B. Guard mock khớp fingerprint toàn body và lưu usage hoặc trạng thái không rõ sau timeout. Dừng trước paid dispatch vì bridge chạm được proxy Level 2 và còn thiếu bằng chứng credential/cap theo provider. Ledger thật giữ nguyên và kill switch ON. [Báo cáo](reports/2026-11-21-hermes-gate-b-preflight-recheck.md).

- Hoàn tất GATE B guard remediation mock trên KVM2: shared-lock interop và 14 fault cases PASS, full n8n→Hermes→guard→provider mock→callback PASS, replay không cấp thêm admission. Sandbox rollback; production health 200/restart 0; ledger thật không đổi, kill switch ON, paid calls và chi phí mới 0. Paid GATE B vẫn chờ preflight riêng.

- Chạy one-shot Linux unit trên KVM2 với ledger copy: 20 tiến trình, đúng 1 admitted, 19 rejected, fault/replay và hai crash boundary PASS; đối chiếu live ledger 1 attempt/kill switch ON, production health 200/restart 0. Guard mock E2E và full crash matrix còn pending, 0 paid calls.

- Thêm bản nháp one-shot transaction trên ledger copy cho GATE B. Local Windows thiếu `fcntl` và Docker daemon không chạy, nên mock/live chưa xác minh; dừng ở `BLOCKED_PREFLIGHT`, 0 paid calls và không đổi runtime.

- Đối chiếu GATE B `BLOCKED_PREFLIGHT` (0 Hermes paid attempts mới, 0 USD phát sinh). Guard hiện thiếu one-shot permit và reserve ngân sách trên shared ledger; ledger/kill switch/production chưa xác minh live. Giao Codex task `TTD-HERMES-GATE-B-GUARD-REMEDIATION-001` để sửa và kiểm thử mock-only, không mở paid dispatch hoặc nới phạm vi.

- GATE B preflight `BLOCKED_PREFLIGHT`: guard GATE A chưa triển khai atomic one-shot permit và reservation trên shared ledger; dừng trước dispatch, 0 paid Hermes attempt, 0 chi phí API mới. Thêm báo cáo/evidence và cập nhật task/ADR/state.

- Chủ dự án phê duyệt GATE B theo ADR-P0-003: Codex được thực hiện tối đa một paid Hermes Agent call qua `gpt-6-luna`, ≤4K input và max_output_tokens=600, fake data, shared P0 USD 0.05 cap, không tools/retry/production change; one-shot permit phải tự tiêu thụ và khóa lại trước dispatch, global kill switch luôn ON. Tạo task `TTD-HERMES-GATE-B-001`; chưa có evidence paid Hermes E2E mới.

- Đối chiếu GATE A Hermes auxiliary+guard+bridge mock PASS với evidence và commit `ab319ee`; cập nhật đề xuất ADR-P0-003 (PROPOSED), chỉ cho một Hermes Agent paid call nếu chủ dự án phê duyệt riêng, có one-shot permit/atomic ledger/kill-switch, không đổi production. Chưa thực hiện GATE B.

- Hoàn tất `TTD-HERMES-GATE-A-001`: triển khai Hermes auxiliary, private guard, authenticated bridge và provider mock trên internal sandbox; exact model, cap 600, full request ≤4K, no-tools/no-bypass, auth, fault/idempotency/concurrency và mock E2E đều PASS.
- Phát hiện ownership workflow trong rollback rehearsal đầu, sửa script và chạy lại corrected rollback/restore PASS; redeploy smoke PASS. Production n8n/Hermes HTTP 200, restart/downtime 0; kill switch/ledger không đổi, paid calls và chi phí mới bằng 0.
- Ghi trạng thái `GATE_A_MOCK_PASS / GO_FOR_GATE_B_APPROVAL`; GATE B không được thực hiện và vẫn cần phê duyệt riêng cho đúng một paid Hermes call.

- Chủ dự án phê duyệt GATE A theo ADR-P0-002: Codex triển khai Hermes auxiliary, private guard, authenticated bridge và hai service secrets chỉ trên KVM2 sandbox; mock capture, kill switch ON, paid calls 0, không đổi production. Tạo task `TTD-HERMES-GATE-A-001`; GATE B chưa được phê duyệt. Việc ghi nhận GitHub không có nghĩa VPS đã được thay đổi.

- Review feasibility Hermes hard cap và lập ADR-P0-002 ở trạng thái PROPOSED: đề xuất GATE A cho Hermes auxiliary, guard, bridge và provider mock capture (kill switch bật, 0 paid call); paid Hermes call GATE B yêu cầu phê duyệt riêng. Không thực hiện thay đổi VPS.

- Hoàn tất `TTD-HERMES-E2E-HARD-CAP-001` ở chế độ read-only/offline: xác minh Hermes `0.22.5`, exact-model/no-tools serialization và kết luận CLI/config upstream không đủ hard output cap.
- Thêm offline guard contract rehearsal PASS cho kill switch, validation-before-reservation, idempotency và 10-way concurrency dùng bản sao shared ledger; paid call mới 0, production change 0.
- Đề xuất Hermes auxiliary nguyên bản + private pre-dispatch guard + authenticated bridge/callback ở trạng thái `GO_FOR_SEPARATE_IMPLEMENTATION_APPROVAL`; Hermes E2E vẫn `BLOCKED_COST_CONTROL` cho tới khi mock/full-input/no-bypass và paid-test riêng được duyệt.

- Đối chiếu Provider E2E PASS (1 call, USD 0.0000496 theo usage, chưa đối soát hóa đơn) và Hermes Agent E2E `BLOCKED_COST_CONTROL`. Tạo `TTD-HERMES-E2E-HARD-CAP-001` để Codex khảo sát read-only cơ chế hard output cap trước request và shared budget gate; chưa cấp quyền triển khai thêm hoặc paid inference.

- Hoàn tất Mức 2 Provider E2E trên sandbox: đúng 1 GPT-6 Luna call, authenticated n8n callback/schema PASS, 131 input + 73 output + 0 reasoning token, usage-based cost USD 0,0000496; replay/conflict không phát sinh call mới.
- Thêm persistent atomic ledger, allowlist CONNECT proxy và kill switch đã bật; task mới bị chặn trước provider, không public port/firewall/DNS/production change, n8n/Hermes production restart 0.
- Ghi `HERMES_E2E_BLOCKED_COST_CONTROL`: Hermes CLI thật chưa chứng minh hard output cap trước request và chưa có private inference callback route; không dùng Provider PASS làm bằng chứng Hermes.

- Chủ dự án phê duyệt Mức 2 GPT-6 Luna: ≤5 paid calls, ≤4K input + 2K output tokens/call, hard target USD 0.05/ngày và USD 0.05 tổng P0, fake data; dừng nếu không kiểm soát được chi phí/quyền. Tạo task Codex `TTD-AI-P0-LEVEL2-001`, nghiệm thu provider E2E và Hermes Agent E2E độc lập; chưa có bằng chứng live paid inference.

- Phân biệt provider E2E và Hermes Agent E2E trong [review P0 Mức 1](reports/2026-11-21-p0-level1-review-and-level2-criteria.md); GPT-6 Luna model/pricing đã đối chiếu tài liệu OpenAI, Mức 2 vẫn chưa được duyệt.

- Hoàn tất P0 Mức 1 trên KVM 2: triển khai n8n sandbox độc lập và reasoner mock cô lập trên internal network, đúng một authenticated webhook, structural E2E 9/9 và rollback/restore PASS.
- Xác minh không restart/downtime production, không public port/firewall/DNS/business change và không paid inference; cập nhật task thành `blocked` chỉ vì real reasoning còn chờ phê duyệt Mức 2.
- Thêm mã triển khai secret-free trong `sandbox/p0-level1`, cập nhật report/evidence/inventory/state/catalog và bảng provider/model cùng đề xuất cap USD 0.05 cho P0 Mức 2.

- Chủ dự án phê duyệt **Mức 1** của ADR-P0-001: Codex được tiếp tục kỹ thuật sandbox n8n ↔ Hermes với inference runtime cô lập và một authenticated webhook, có preflight/backup/rollback. Mức 2 (provider/model, cost cap, paid inference) và thay đổi gây downtime/public production vẫn chưa được phê duyệt. Chưa có thay đổi VPS do ChatGPT thực hiện tại bước ghi nhận này.

- Lập ADR-P0-001 ở trạng thái PROPOSED sau P0 network PASS/E2E BLOCKED: Hermes inference cô lập, n8n authenticated webhook, nghiên cứu provider/model và cost cap; chưa phê duyệt hay thay production.

- Triển khai network-only P0 `ttd-ai-p0-sandbox` ở chế độ internal, gắn live n8n/Hermes bằng private DNS; health, negative auth và rollback preparation PASS, không restart/downtime/public port/firewall change và không gọi paid API.
- Ghi `PARTIAL / BLOCKED_BY_BUDGET_AND_RUNTIME`: Hermes chưa expose inference API, n8n MCP còn disabled và chưa có workflow/callback; thêm report/evidence, cập nhật task/state/catalog.
- Đồng bộ catalog/state với kết quả định danh đã complete: `ttdnew.tech` U4S Hermes tách biệt KVM 2; thêm catalog entry cho báo cáo identity.

- Tạo nhiệm vụ định danh resource `ttdnew.tech` (Hostinger Agent owner) và P0 sandbox n8n ↔ Hermes (Codex owner), có identity gate, backup/rollback, không phát sinh phí chưa duyệt.
- P0 chưa được thực thi; ghi rõ trạng thái BLOCKED cho tới khi resource được xác minh và các điều kiện an toàn đạt.

- Mở rộng hồ sơ Hostinger Agent theo account inventory 2026-11-21; ghi nhận Cloud Startup/WordPress, VPS, Docker/AI, domains, email, Reach và giới hạn quyền filesystem.
- Liên kết báo cáo `reports/2026-11-21-hostinger-account-capability-inventory.md` vào catalog, danh bạ và trạng thái chung; giữ mâu thuẫn OpenClaw vs `u4s-hermes-agent` ở trạng thái chưa xác minh.

- Thêm `reports/2026-11-21-hermes-capability-survey.md`, cập nhật `agents/hermes.md`, `CATALOG.yaml` và `STATE.md` cho khảo sát bổ sung theo task `TTD-AGENT-CAPABILITY-SURVEY-001`.
- Ghi nhận rõ khác biệt giữa Hermes WebUI session và Hermes VPS container `0.22.5`; xác minh lại GitHub write, skills/memory/session recall và giữ trạng thái BLOCKED/UNKNOWN cho inference API, n8n MCP và connector business.
- Hoàn tất khảo sát Codex theo `TTD-AGENT-CAPABILITY-SURVEY-001`; ghi rõ runtime, local/Git/browser/hPanel/VPS permissions, n8n/Hermes evidence, background limits và approval boundaries.
- Cập nhật `agents/codex.md`, danh bạ agent, state và catalog; thêm catalog entry cho báo cáo Hostinger Agent đã có trên remote.
- Xác nhận Codex app build hiện tại, Git HTTPS read/write và Computer Use; ghi `BLOCKED/UNKNOWN` cho local Docker daemon, exact model, persistent execution và các connector marketing chưa test.
- Không thay đổi production hoặc tạo connector/automation/paid API call.

- Thêm danh bạ vai trò `agents/` cho ChatGPT, Codex, Hermes, Hostinger/Hostinger Agent và n8n, phân biệt capability verified/reported/unknown.
- Đưa lên GitHub task `TTD-AGENT-CAPABILITY-SURVEY-001` để chủ dự án chuyển câu hỏi đến từng tác nhân và nhận báo cáo tự đánh giá.
- Liên kết các hồ sơ vào README, PROJECT, AGENTS, STATE và CATALOG.

- Hoàn tất `TTD-AI-PLATFORM-AUDIT-001` và thêm báo cáo/evidence đã khử định danh cho kiểm toán live n8n ↔ Hermes.
- Xác minh n8n `2.45.7`, Hermes `0.22.5`, network/auth hai chiều và trạng thái runtime; ghi rõ MCP, inference API và end-to-end còn `BLOCKED`.
- Đề xuất kiến trúc n8n control plane + Hermes reasoning + internal network + policy/approval gate + media-worker; cập nhật `PROJECT.md`, `STATE.md`, inventory và catalog.
- Không thay đổi production, không gọi model/media trả phí và không kết nối tài khoản marketing.

- Tạo task `TTD-AI-PLATFORM-AUDIT-001` kiểm toán live n8n ↔ Hermes và thiết kế hệ thống AI Automation dựa trên báo cáo tự đánh giá Hermes.

- Thêm `reports/2026-11-21-hermes-self-assessment.md`, catalog tương ứng và cập nhật `STATE.md` cho đợt tự đánh giá năng lực Hermes Agent hiện tại.
- Ghi nhận đã xác minh được skills, session recall và GitHub push của agent; đồng thời giữ trạng thái chưa kiểm chứng cho exact Hermes build/version, live API endpoint và live n8n integration.

- Thêm `PROJECT.md` xác định mục tiêu nền tảng AI TTD METAL và tiến độ thực tế.
- Thêm `rules/AGENT_WORKFLOW.md` thống nhất giao task qua GitHub, báo cáo trở lại GitHub, quy định tối thiểu không khóa phương pháp.
- Liên kết entrypoint và danh mục cho mọi tác nhân; chuẩn bị `tasks/` cho các đặc tả tiếp theo.

- Tổ chức repository thành nguồn tri thức cho nhiều tác nhân với `AGENTS.md`, `STATE.md` và `CATALOG.yaml`.
- Thêm quy trình đóng góp, cấu trúc inventory/report/knowledge/runbook/decision/reference/archive và các mẫu tài liệu.
- Thêm trình kiểm tra repository để phát hiện metadata, liên kết, catalog hoặc dấu hiệu bí mật không hợp lệ.
- Chuẩn hóa tên file và chuyển báo cáo bảo mật có ngày từ `inventory/` sang `reports/`.
- Khởi tạo cấu trúc tài liệu vận hành cho repository.
- Ghi nhận kiểm kê trực tiếp VPS Hostinger sau khi xóa `CHUNG_KHOAN_PRO` và Alibaba OneTalk.
- Ghi nhận cấu hình n8n, Hermes Agent, Docker, PostgreSQL, Nginx, UFW, Fail2ban, SSH và sao lưu.
- Thêm đánh giá bảo mật và lộ trình cải thiện.
- Thêm quy tắc chống commit bí mật và script kiểm kê chỉ đọc.
