---
id: ttd-hermes-gate-b-001
type: task
status: blocked
approved_at: 2026-11-21
updated_at: 2026-11-21
approval_scope: exactly_one_hermes_paid_attempt
paid_inference_approval: true
sensitivity: public
owner: codex
support: [hermes, hostinger-agent]
depends_on: [ttd-hermes-gate-a-001]
---

# TTD-HERMES-GATE-B-001 — Một lượt GPT-6 Luna qua Hermes Agent thật

## Phê duyệt chủ dự án — 2026-11-21

Chủ dự án đã **phê duyệt GATE B theo [ADR-P0-003](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md)**. Codex được phép thực hiện **tối đa đúng một physical paid inference attempt** qua Hermes Agent thật, trên sandbox KVM2 đã được kiểm thử GATE A, chỉ với dữ liệu giả. Đây là giới hạn tối đa, **không buộc phải thực hiện call nếu safety/cost gate không PASS**.

Route bắt buộc: `n8n sandbox → authenticated bridge → Hermes auxiliary đã xác minh → private pre-dispatch guard → OpenAI Responses API → authenticated n8n callback`.

## Giới hạn bắt buộc

- Provider/model **chỉ OpenAI `gpt-6-luna`**; xác minh exact model, giá, quyền API live trước dispatch.
- **≤4.000 input tokens**, `max_output_tokens=600` (bao gồm output/reasoning tokens do provider tính), không tools/web/search/media/MCP/subagent, một turn, không fallback.
- **Một task ID/idempotency key được phê duyệt; tối đa một physical paid attempt GATE B.** Không retry có tính phí, dù timeout/error/response lost. Cached replay cùng request chỉ đọc, không dispatch thêm. Không gọi lại provider adapter để test.
- Dùng **chung persistent atomic P0 ledger**: baseline 1 previous paid attempt, USD 0.0035 reserved, USD 0.0000496 usage-based actual (chưa đối soát hóa đơn). Không reset, nới, hoặc thay ledger. Ngưỡng tổng P0 **≤5 attempts, ≤USD 0.05/ngày, ≤USD 0.05 toàn P0**, ≤USD 0.01/job; upper-bound reservation bảo thủ trước request. Nếu bất kỳ ngưỡng, mức giá, hoặc phép hạch toán không chắc chắn, STOP.
- Kill switch **ON toàn cục**. Chỉ chấp nhận **atomic scoped one-shot permit** ở guard cho task/idempotency key được duyệt. Permit phải được validate và **consume/relock bền vững trước provider dispatch**, kể cả lỗi hoặc timeout; không được mở toàn cục, không mở cửa sổ cho request thứ hai. Nếu chỉ có cách tắt global kill switch, STOP để xin quyết định mới.
- **Không sửa production** n8n/Hermes, website, Ads, business services, firewall, DNS, public port, SSL hoặc U4S `ttdnew.tech`. Không restart/recreate các service chính hoặc tạo downtime. Không tạo account/service tính phí mới.
- Hermes auxiliary và bridge **không giữ provider key** và không có direct provider Internet egress; chỉ guard có kết nối outbound tối thiểu qua allowlist proxy. Secrets không xuất hiện trên GitHub public, chat, logs hoặc báo cáo.

## Preflight — bắt buộc trước paid attempt

1. Đọc [GATE A report](../reports/2026-11-21-hermes-gate-a-mock-results.md), [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-a-001.json) và [ADR-P0-003](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md); xác minh runtime image pin/version, private auth, full serialized input ≤4K và provider request cap 600/no-tools đã kiểm chứng.
2. Backup/config/rollback và production prehealth; CPU/RAM/network safety, no-bypass, callback reachability/authorization.
3. Chứng minh **atomic one-shot permit bằng test offline/mock**, cùng shared ledger, chống simultaneous requests, loss/restart và retries. Có chứng cứ permit consumed trước actual dispatch. Kiểm tra route không có cách gọi trực tiếp OpenAI từ Hermes.
4. Xác minh giá Standard chính thức đang áp dụng, model accessible, khả năng reserve upper bound và reconcile API usage. Nếu không có cách bảo đảm không vượt cap theo phép tính bảo thủ, STOP.
5. Chỉ khi tất cả gates PASS mới cho đúng một request fake-data đi qua guard; không test thêm paid dù cần debug.

## Acceptance

- **`HERMES_E2E_PAID_PASS`** chỉ khi evidence chỉ rõ chạy qua real Hermes auxiliary (không phải provider adapter), guard, GPT-6 Luna và authenticated n8n callback; JSON Schema PASS; model served/requested khớp.
- Ledger tăng **tối đa +1** paid attempt; số token/cost đúng giới hạn. Trường hợp attempt thất bại, ghi FAILED/BLOCKED, **không retry paid** và không ghi PASS giả.
- Global kill switch luôn ON; scoped permit consumed vĩnh viễn trước dispatch; verify post-state, no-bypass và production health PASS.
- Không suy luận một paid E2E thành production-ready/24x7. Báo cáo chi phí dựa trên usage riêng và invoice/billing verified riêng, không đồng nhất.
- Backup/rollback sau khi cần thiết nhưng **không khôi phục/xóa ledger để làm mất dấu paid attempt**.

## STOP conditions

Bất kỳ vấn đề về hard-cap, budget admission, one-shot permit, model, key, public exposure, provider routing, auth, bypass, production health, secret, uncertainty in upper bound hay tính toán chi phí → STOP. Nếu gọi đã dispatch thì không thực hiện paid attempt mới; lock/reconcile/report.

## Bàn giao

Codex lưu `reports/2026-11-21-hermes-gate-b-paid-results.md` và JSON evidence đã khử bí mật (hoặc ngày thực tế), nêu preflight, exactly one attempt or zero if blocked, model, input/output/reasoning token, reserved/actual cost, invoice status, task/run IDs dưới dạng hash, correlation and callback, one-shot state, ledger, health/rollback. Push vào repo, cập nhật task, ADR, STATE.md, CATALOG.yaml, CHANGELOG.md; không đưa API keys/secret/private endpoints vào repo.

## Kết quả preflight 2026-11-21

`BLOCKED_PREFLIGHT`: guard GATE A chưa có atomic scoped one-shot permit/consume/relock và worst-case reservation. Không thực hiện paid request; xem [báo cáo](../reports/2026-11-21-hermes-gate-b-paid-results.md). Approval vẫn giới hạn tối đa một attempt sau khi toàn bộ gate được chứng minh.

## Kiểm tra lại sau remediation

**BLOCKED_PREFLIGHT.** Fingerprint của toàn bộ byte gửi đi và hạch toán sau response, timeout hoặc stream bị cắt đã PASS với guard và provider mock trên Linux. Live bridge chạm được proxy Level 2 cũ, guard chưa có paid route riêng và chưa xác minh quyền Responses của credential dành cho guard hoặc số input tokens của request cuối theo provider. Ledger thật giữ 1 attempt, 0 permit và kill switch ON trước/sau. Paid dispatch mới 0. [Báo cáo tổng hợp](../reports/2026-11-21-hermes-gate-b-preflight-recheck.md) · [Evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-preflight-recheck.json).

## Kiểm tra sau cô lập proxy

Proxy trên KVM2 đã rời mạng dùng chung. Guard vào được proxy và sáu container còn lại bị chặn trong phép thử. Mock callback, hạch toán mock riêng và rollback egress đã kiểm chứng. Task vẫn **BLOCKED_PREFLIGHT** vì thiếu credential dành cho guard đã xác minh, số tokens theo provider và một lượt mock kết hợp callback với one-shot accounting. Có một lần lỗi metadata Hermes trước callback. Paid attempts mới 0. [Báo cáo hiện tại](../reports/2026-11-21-hermes-gate-b-egress-isolation.md).


## Điều phối theo quy tắc chung — checkpoint sau egress isolation (2026-11-21)

**Nguồn đã đọc:** [báo cáo egress](../reports/2026-11-21-hermes-gate-b-egress-isolation.md), [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-egress-isolation.json), commit `88268989af28243fd4bf490db199e55fda28dcfb`; [AGENTS](../AGENTS.md), [AGENT_WORKFLOW](../rules/AGENT_WORKFLOW.md), [REPOSITORY_SECURITY](../rules/REPOSITORY_SECURITY.md), [STATE](../STATE.md), [CATALOG](../CATALOG.yaml).

**Current evidence:** proxy isolation PASS trên 6 negative containers, guard-to-proxy PASS, disconnect/reconnect PASS; production HTTP 200. Fresh-task mock webhook+callback PASS nhưng một lỗi `HERMES_RUNTIME_MISMATCH` vẫn chưa giải thích; one-shot settlement mới PASS riêng chứ chưa cùng n8n callback trong một run. Guard chưa có OpenAI credential; 3.308 bytes không phải provider token count; live ledger 1 attempt, 0 permits, kill switch ON. **GATE B BLOCKED_PREFLIGHT; delta paid 0; không deploy paid upstream.** Network topology mới nằm ở Compose KVM2, cần đồng bộ cấu hình vận hành/backup để không tái tạo đường cũ khi redeploy.

### Handoff H1 — Hostinger Agent: xác minh hạ tầng và credential path (read-only)

- `from_agent: chatgpt`; `to_agent: hostinger-agent`; `owner: hostinger-agent`; `handoff_state: PREPARED_FOR_OWNER_FORWARD` (chưa chứng minh đã gửi hoặc ACK); `why_this_agent: hPanel/VPS/backup/network/credential-mount capabilities`.
- **BẮT BUỘC đọc quy tắc:** `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/hostinger.md` và báo cáo egress; ghi commit quy tắc đã đọc.
- **Bắt đầu:** đọc `reports/2026-11-21-hermes-gate-b-egress-isolation.md` và `reports/evidence/2026-11-21-ttd-hermes-gate-b-egress-isolation.json`. Nếu có quyền read-only hPanel/VPS thì đối chiếu các Docker networks hiện đang gắn, route guard→proxy, 6 negative paths, publish ports, proxy outbound ACL, rollback/backup của Compose runtime. Không tiết lộ IP thật, DNS private hoặc secret lên GitHub public.
- **Trả lời cụ thể:** (a) Docker topology cô lập hiện có survive `docker compose up/recreate` không, và cần persist/sync file nào; (b) cách mount secret least-privilege cho guard-only đúng project mà không để bridge/Hermes/n8n thấy key; (c) có thể đọc xác nhận key presence và quyền project/quota qua hPanel/API account không, nếu không đánh UNKNOWN và chuyển owner cấp key; (d) negative route test cần lặp sau redeploy là gì; (e) rollback không mất dữ liệu ledger. Không tạo key/đọc secret value/đổi network trong task khảo sát.
- **Nghiệm thu:** report `reports/2026-11-21-gate-b-hostinger-consult.md` redacted gồm VERIFIED_LIVE/UNKNOWN, evidence, đề xuất hành động cụ thể và approval needed; commit link. `next_owner: chatgpt` tổng hợp.

### Handoff H2 — Hermes Agent: runtime mismatch và exact request (read-only/mock)

- `from_agent: chatgpt`; `to_agent: hermes-agent`; `owner: hermes-agent`; `handoff_state: DONE`; `why_this_agent: inference runtime, response serialization, model/tool/metadata semantics`.
- **BẮT BUỘC đọc:** `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/hermes.md` và hai báo cáo GATE B mới nhất; ghi commit quy tắc.
- **Bắt đầu:** đối chiếu `sandbox/p0-hermes-gate-a/bridge.py`, `guard.py`, test harness và evidence fresh-task (chỉ nếu công cụ có quyền truy cập); định vị check phát `HERMES_RUNTIME_MISMATCH`, so expected metadata trên task đầu và task mới, idempotency/task/session, model exact `gpt-6-luna` và `max_output_tokens=600`.
- **Trả lời cụ thể:** nguyên nhân mismatch với log đã khử nhạy cảm; cách làm request deterministic từ Hermes auxiliary không đổi semantic trên retry; vị trí canonical-serialization và SHA256 của **full provider-bound request**; test nào xác nhận first task, new task, replay/callback cùng one-shot accounting; thông số request gửi `/v1/responses/input_tokens` sao cho cùng `model/instructions/input/tools` với request inference. Nếu không thấy live runtime, chỉ đánh DOCUMENTED/UNKNOWN, không báo VERIFIED_LIVE.
- **Nghiệm thu:** report `reports/2026-11-21-gate-b-hermes-consult.md` và evidence `reports/evidence/2026-11-21-gate-b-hermes-consult.json` đã được tạo bằng read-only/mock analysis. `next_owner: chatgpt`. Không gọi paid inference, không mở tool/fallback.

### Handoff H3 — ChatGPT phân tích và Codex thực thi (sau H1/H2)

- `from_agent: hostinger-agent + hermes-agent`; `to_agent: chatgpt`; `handoff_state: WAITING_FOR_REPORTS`. ChatGPT đối chiếu hai reports, nguồn vendor bên dưới, evidence mới và phạm vi ADR-P0-003. Khi đủ dữ kiện, cập nhật **task này**, không tạo nhiệm vụ con không cần thiết.
- `from_agent: chatgpt`; `to_agent: codex`; `handoff_state: NOT_SENT` tại checkpoint này. Codex là **owner phần code/test** sau khi được chuyển một đặc tả có cách bắt đầu cụ thể và môi trường/approval rõ. Chỉ sửa sandbox: fix metadata mismatch, persist isolated proxy topology, guard-only secret mount khi owner cho phép, chạy token count với đúng credential theo phạm vi đã duyệt, khóa count với digest request (lưu ý count endpoint và create có thể khác request shape; canonical bytes phải được kiểm chứng), chạy **một** mock E2E kết hợp callback+one-shot accounting. Không paid inference nếu chưa preflight PASS.
- Khi preflight PASS, giữ nguyên nguyên tắc đã duyệt trong ADR-P0-003: model `gpt-6-luna`, input ≤4K billable tokens, max output 600, global kill switch ON, one-shot consumed before dispatch, ≤1 paid attempt toàn GATE B, cap P0 ≤USD 0.05, no retry/production change. **Không suy diễn việc tạo tài liệu là đã gửi lệnh tới Codex/Hermes/Hostinger.**

### Tài liệu vendor tham khảo (kiểm tra 2026-11-21)

- Docker bridge networking: https://docs.docker.com/engine/network/drivers/bridge/ — container cùng user-defined network có thể liên lạc, cô lập theo network membership; cần kiểm tra đường gateway/host/published ports thực tế.
- Docker Compose networking: https://docs.docker.com/compose/how-tos/networking — thay đổi topology cần lưu cấu hình Compose của môi trường thực, kiểm tra membership sau recreate.
- OpenAI input-token counting: https://developers.openai.com/api/docs/guides/token-counting và https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count — endpoint `POST /v1/responses/input_tokens`, không thay paid inference, đếm cả định dạng message, tools nếu có.
- OpenAI API project/key management: https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform và https://developers.openai.com/api/docs/guides/api-keys — service account thuộc project cụ thể; model access/role và key permissions cần xác minh, không suy ra từ dashboard model list.

**Trạng thái tại thời điểm ban hành H1/H2:** H1/H2 `PREPARED_FOR_OWNER_FORWARD`; H3 `WAITING_FOR_REPORTS`; paid GATE B `BLOCKED_PREFLIGHT`. Cập nhật mới nhất xem cuối tài liệu. Không ai được hiểu đây là quyền bổ sung hoặc một lệnh đã gửi tự động.

## Kiểm tra sau cô lập proxy

Proxy trên KVM2 đã rời mạng dùng chung. Guard vào được proxy và sáu container còn lại bị chặn trong phép thử. Mock callback, hạch toán mock riêng và rollback egress đã kiểm chứng. Task vẫn **BLOCKED_PREFLIGHT** vì thiếu credential dành cho guard đã xác minh, số tokens theo provider và một lượt mock kết hợp callback với one-shot accounting. Có một lần lỗi metadata Hermes trước callback. Paid attempts mới 0. [Báo cáo hiện tại](../reports/2026-11-21-hermes-gate-b-egress-isolation.md).


## H1 Hostinger Agent đã báo cáo và ChatGPT đã nhận — 2026-11-21

- `handoff_id: H1`; `from_agent: hostinger-agent`; `to_agent: chatgpt`; `handoff_state: DONE_RECEIVED_AND_REVIEWED`. Hostinger Agent đã push [báo cáo H1](../reports/2026-11-21-gate-b-hostinger-consult.md), [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-h1-hostinger-readonly.json), commit `5b8dd629e4acfd21bc4db1aa3634a131bb97f0cc`.
- **H1 hoàn thành nhiệm vụ khảo sát read-only; GATE B chính vẫn `BLOCKED_PREFLIGHT` và `owner: codex`.** Không đánh đồng trạng thái H1 complete với paid Gate B complete.
- VERIFIED_LIVE: Gate A 4 containers healthy; network/control/provider/upstream topology và không public port; các volume/state hiện có; backup VPS sẵn có. UNKNOWN: persistence sau redeploy, rollback thật, kiểm tra no-bypass động *trong phiên H1* và membership đầy đủ của mạng riêng Gate B. Evidence no-bypass động trong [báo cáo egress](../reports/2026-11-21-hermes-gate-b-egress-isolation.md) là test Codex từ **phiên khác**, không mất hiệu lực chỉ vì H1 không tự chạy lại.
- **Phân biệt loại credentials:** `API_SERVER_KEY` của Hermes và `guard-service token` là service-to-service credentials dành cho các vai trò giao tiếp nội bộ, đã tồn tại ở Hermes/bridge/mock phù hợp mô hình auth. **Không được kết luận chúng phải guard-only.** Yêu cầu strict guard-only của ADR-P0-003 áp dụng riêng cho **OpenAI provider API key** (hoặc credential có quyền gọi OpenAI), phải không tồn tại trong Hermes auxiliary/bridge/n8n/mock. Báo cáo H1 **chưa phát hiện provider credential mount** và chưa chứng minh key guard đã được cấp. Phải kiểm tra mount metadata theo **loại credential** và quyền tối thiểu, không dùng chung nhãn `credential` để kết luận FAIL.
- `next_owner: chatgpt` tổng hợp H1 với H2; `H2: PREPARED_FOR_OWNER_FORWARD` đến khi Hermes xác nhận nhận báo cáo; `H3: NOT_SENT`, Codex chưa được giao lại. Không tạo paid permit, không gọi API, kill switch ON.
- **Nguyên tắc bảo tồn task:** các agent tham vấn H1/H2 chỉ thêm section kết quả/link vào task chính hoặc update report riêng; không ghi đè toàn bộ file, đổi `owner/status/paid_inference_approval` của GATE B. Task chính chỉ được complete khi `HERMES_E2E_PAID_PASS` có evidence nghiệm thu (hoặc quyết định đóng dự án riêng).

## H1 + H2 tổng hợp bởi ChatGPT — H3 đặc tả cho Codex (2026-11-21)

**Bằng chứng đã nhận:** H1 [Hostinger consult](../reports/2026-11-21-gate-b-hostinger-consult.md) / [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-h1-hostinger-readonly.json), commit `5b8dd629e4acfd21bc4db1aa3634a131bb97f0cc`; H2 [Hermes consult](../reports/2026-11-21-gate-b-hermes-consult.md) / [evidence](../reports/evidence/2026-11-21-gate-b-hermes-consult.json), commit `e0297d2c1fffe2808702601de9db8e996cd67517`; egress topology report commit `88268989af28243fd4bf490db199e55fda28dcfb`.

**Task gốc không đổi:** `owner: codex`, `status: blocked`, `paid_inference_approval: true` (chỉ tối đa một call nếu toàn preflight PASS). Consult H1/H2 `DONE_RECEIVED_AND_REVIEWED`; H3 `PREPARED_FOR_OWNER_FORWARD` (**chưa gửi trực tiếp hoặc được Codex ACK**). GATE B `BLOCKED_PREFLIGHT`, không paid call mới.

### Kết luận điều phối theo chứng cứ

- Network isolation: Codex đã thực nghiệm 6 negative containers trên topology egress mới; H1 chỉ kiểm tra live topology và backup, **không làm test dynamic trong phiên H1**, không phủ định evidence trước. Persistence sau redeploy và rollback Compose toàn diện vẫn UNKNOWN.
- Secrets: H1 thấy service-auth keys ở bridge/Hermes/mock. **Chúng không phải OpenAI provider key.** Strict guard-only chỉ áp dụng cho **credential có quyền gọi provider**. Guard chưa có provider credential, nên kiểm chứng key identity/Responses/billing chưa đạt. Không đưa secret value vào Git hoặc chat.
- `HERMES_RUNTIME_MISMATCH`: H2 mock reproducer chứng minh same `task_id` replay failed state mà không gọi lại runtime; exact metadata live ban đầu UNKNOWN. Chỉ chẩn đoán mismatch live nếu `fresh task_id` còn lỗi và có redacted runtime payload.
- Authoritative fingerprint/cap: final **guard-forwarded** `/v1/responses` body **sau enforce** mới là request được duyệt. H2 xác minh mock fixture 253 bytes/hash; candidate 3308 bytes/hash từ egress evidence chưa được tự tính lại từ fixture private. Không thay thế token count bằng byte length.
- Mock callback + one-shot đã từng PASS ở checkpoint cũ, nhưng **chưa chạy một combined E2E trên topology cô lập mới**. Mock unit accounting/timeout PASS không đủ kết luận full E2E.
- Đối chiếu nguồn chính thức: Docker Compose service-level secrets https://docs.docker.com/compose/how-tos/use-secrets và https://docs.docker.com/reference/compose-file/services/; Docker network https://docs.docker.com/compose/how-tos/networking; OpenAI token counting API https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count và project keys https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform. Nguồn docs cung cấp contract/thiết kế, **không chứng minh live key scope**.

### H3 → Codex: các bước cụ thể, theo thứ tự (không làm lại test đã PASS nếu không đổi mã/topology)

1. **Rule ACK + baseline**: đọc `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/codex.md`, task này và 2 report H1/H2; xác nhận commit rule đã đọc. Đầu tiên dùng checkout `main` mới nhất, review `sandbox/p0-hermes-gate-a/bridge.py`, `guard.py`, `mock_contract.py`, `one_shot.py`, `compose.yaml` và Compose topology hiện chạy trên KVM2 (đọc/backup; **không chép đè bằng compose GATE A cũ**). Phân biệt secrets `API_SERVER_KEY`/guard-service token với OpenAI provider credential.
2. **Reproduce bridge state với mock**: xem điều kiện `run_hermes()` và persisted `bridge-tasks.json` chỉ theo metadata redacted; dùng **fresh task_id** không đụng persisted failed state. Bổ sung `route_source=live_run|persisted_replay` vào telemetry an toàn nếu cần; chỉ sửa runtime mismatch khi fresh request tái hiện mismatch với evidence. Không xóa/reset bridge ledger để che lỗi.
3. **Test combined trên topology isolated hiện tại**: backup sandbox configs/state, dựng fixture và **disposable ledger copy**, mock one-shot permit đã scope theo final forwarded body digest, chạy `n8n sandbox → authenticated bridge → Hermes auxiliary → guard enforcing one-shot → provider mock → callback`. Acceptance trong **cùng run**: first webhook/callback HTTP 200; exactly 1 mock dispatch; permit consumed + reserve durable **trước dispatch**; usage recorded hoặc `outcome_unknown` (nếu fault injection); replay cùng task không dispatch lần hai; negative bad task/key/model/body; zero real-ledger mutation. Sau đó verify six-container proxy no-bypass/DNS+IPv4, no public port, backup/rollback and production health.
4. **Credential/provider preflight (không paid inference)**: giữ provider key **chỉ cho guard**, dùng per-service Docker Compose secrets/bind mount tối thiểu và secret permissions (không chia cho bridge/Hermes/n8n/mock); owner cấp key đúng project qua kênh an toàn nếu có authorization riêng. Có thể xác minh key identity/quyền/quota qua account/provider metadata nếu khả thi và không thực hiện paid inference. Nếu thiếu credential hoặc quyền, ghi `BLOCKED_CREDENTIAL`; **không yêu cầu dán API key vào chat/GitHub**.
5. **Count token trên exact forwarded bytes**: chốt canonical `/v1/responses` request **sau guard enforcement**, băm SHA-256, derive `POST /v1/responses/input_tokens` từ **chính bản đó**, map đúng model/instructions/input/tools và các trường ảnh hưởng input; giữ bản mapping/digest bảo đảm không drift. Verify `input_tokens <=4000` từ provider endpoint khi credential có quyền, không dùng 3308 bytes làm tokens. Kiểm chứng actual project pricing/service tier/output cap 600 (reasoning included) và tính conservative reservation ≤USD 0.01/job, P0 ≤USD 0.05 total; nếu thiếu dữ liệu, STOP.
6. **Paid preflight-only checkpoint**: khi mọi mock/live checks PASS, báo trạng thái, ledger actual (baseline 1 attempt/0 permits), kill switch ON, code/compose diff, guard-only provider credential presence (không key value), provider token count bound digest, rollback và callback readiness. Không được tạo paid permit hoặc dispatch trước khi có toàn bộ evidence. Quyền ADR-P0-003 cho tối đa một physical paid attempt vẫn có điều kiện; ở nhiệm vụ H3 này **chỉ chuẩn bị & xác minh**, chưa coi các report H1/H2 là pass cho paid E2E.
7. **Bàn giao**: bổ sung section kết quả vào task gốc **không ghi đè owner/status/approval**, tạo report/evidence đã redacted (tên ngày thực tế), commit/push, read-back. Ghi mỗi item `VERIFIED_LIVE / VERIFIED_MOCK / UNKNOWN / BLOCKED`, ghi lại 0 paid calls hoặc số physical calls thực tế; next owner `chatgpt` review. Nếu thiếu quyền thao tác sandbox/secret, nêu blocker + hành động cụ thể dành cho owner.

**Stop:** no direct bypass; không sửa production/U4S, không restart production, không reset paid ledger, không đổi global kill switch, không paid retry, không phát sinh phí không phê duyệt, không tạo permit trả phí trong giai đoạn H3 chuẩn bị. H3 là **PREPARED_FOR_OWNER_FORWARD**; Codex phải ACK theo quy tắc mới trước khi triển khai.

## Kết quả H3 của Codex — 2026-11-21

**ACKNOWLEDGED** từ chủ dự án. Commit quy tắc `9f497608c65273f4ccf2dd9776042c8a3aa2ecf5`. **VERIFIED_MOCK** cho combined E2E với task mới, callback 200, đúng một lượt provider mock, permit/reserve bền vững trước khi mock nhận, usage recorded và replay không dispatch. **VERIFIED_LIVE** cho rollback egress, sáu negative proxy tests, production health và ledger thật giữ nguyên. **BLOCKED_CREDENTIAL / BLOCKED_PREFLIGHT** cho provider key riêng, project/billing, số token provider gắn với digest request cuối. Paid calls và phí đều 0. `next_owner: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`. [Báo cáo H3](../reports/2026-11-21-hermes-gate-b-h3-preflight.md) · [Evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-h3.json).

## ChatGPT nghiệm thu H3 và khoanh vùng điều kiện còn thiếu — 2026-11-21

- `handoff: H3`; `from_agent: codex`; `to_agent: chatgpt`; `handoff_state: DONE_RECEIVED_AND_REVIEWED`; **H3 = MOCK_E2E_PASS; GATE B = BLOCKED_PREFLIGHT**. Căn cứ: [báo cáo H3](../reports/2026-11-21-hermes-gate-b-h3-preflight.md), [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-h3.json), commit `2e7fa11a96d0bfbf60bc90d545bcdff3833add66`. Nghiệm thu chỉ dựa trên bằng chứng report/evidence, không nhận là ChatGPT trực tiếp đo lại VPS.
- **Dữ liệu đã PASS được giữ nguyên:** mock combined n8n→Hermes→guard→provider mock→callback, 1 physical mock request; permit+reserve trước dispatch; ledger mock `usage_recorded`; replay và 4 negative cases không dispatch; rollback giữ Compose bytes, 6 container negative network tests, production health, real ledger unchanged và kill switch ON. Mọi mock cost/token fixture không phải provider billing/token count. **Không rerun** khi không có code/config/topology/fixture change ảnh hưởng test.
- **BLOCKED_CREDENTIAL và BLOCKED_TOKEN_COUNT:** OpenAI provider key chưa tồn tại trong vị trí cấu hình guard được kiểm tra; cần chủ dự án chỉ định/cấp đúng project **qua kênh secret kín**, không đưa credential vào chat/GitHub. Xác minh guard-only mounting/permissions, project access, Responses permissions, billing/quota rồi dùng `POST /v1/responses/input_tokens` cho **chính final guard-forwarded request**; lưu returned count cùng digest, model/tier và mọi input-semantic fields. Mock H3 3.345 bytes có overlay ổn định `prompt_cache_key` tạm, đã rollback, **không được dùng làm paid-permit fingerprint**.
- **BUDGET STOP:** xác minh pricing Standard đúng model/tier, maximum output 600 bao gồm reasoning, tính upper-bound reservation bằng số đếm token provider và giới hạn P0; USD 0.0035 chỉ là reservation cũ, không được tự kết luận đủ. Real ledger vẫn 1 historical attempt, 0 real permits, kill switch ON, 0 paid Hermes attempts mới.
- **Next ownership:** `business-owner` giải quyết việc cấp credential/ủy quyền đúng phạm vi; sau đó `codex` chỉ thực hiện provider preflight và targeted checks bị ảnh hưởng, không mở paid dispatch trước khi toàn bộ gate PASS. Task mẹ **owner=codex, status=blocked, approval restriction nguyên vẹn**. Handoff tiếp theo chưa gửi/ACK.
- **READ_SET:** task này, ADR-P0-003, H1/H2/H3 reports/evidence, rules latest + Compose/guard hiện tại; **WRITE_SET:** bổ sung mục kết quả và report preflight mới, cập nhật STATE/CHANGELOG nếu trạng thái đổi; **DO_NOT_TOUCH:** owner/status/approval mẹ, production, live paid ledger, global kill switch, API key values; **TEST_DELTA:** credential presence + permission + free token count + final exact-digest/budget/no-bypass health; chỉ lặp combined mock nếu thật sự thay logic/route ảnh hưởng.
