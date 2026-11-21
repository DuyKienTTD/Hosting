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

## H4 — Codex chuẩn bị giao diện nhập API Key an toàn (chỉ thị chủ dự án 2026-11-21)

**Phạm vi ủy quyền mới, tách khỏi paid inference:** Chủ dự án cho phép **Codex chuẩn bị cấu hình và cơ chế nhập OpenAI API Key để chính chủ dự án tự nhập vào giao diện bảo mật**. Đây là approval cho **thiết kế/triển khai trong sandbox và hướng dẫn thao tác nhập**, **không phải** lệnh công khai form trên Internet, không cấp quyền xem key, tạo project/key hộ chủ dự án, sửa production, gọi paid inference, đổi global kill switch hoặc tạo permit thật. GATE B giữ `BLOCKED_PREFLIGHT`.

**Owner:** `codex`. **Handoff:** `chatgpt -> codex; PREPARED_FOR_OWNER_FORWARD` (file đã push, chưa xác nhận giao trực tiếp/ACK). **READ_SET:** đọc đủ quy tắc mới nhất, task/ADR-P0-003, báo cáo H1/H2/H3 và evidence, hiện trạng Compose guard-only, network/secret mount và báo cáo cấu hình VPS. **PREVIOUSLY_VERIFIED:** H3 combined mock E2E, no-bypass, rollback, ledger integrity đã PASS; không chạy lại full suite nếu không có thay đổi ảnh hưởng. **WRITE_SET:** chỉ script/giao diện thiết lập mới trong `sandbox/` hoặc `scripts/`, Compose **sandbox guard-only** khi được phép, bổ sung duy nhất section H4 kết quả vào task mẹ, report/evidence, STATE/CHANGELOG khi cần. **DO_NOT_TOUCH:** metadata owner/status/approval task mẹ, production n8n/Hermes, U4S, firewall/DNS/public port, business account, real ledger, global kill switch, API key value.

### Yêu cầu thiết kế và thao tác

1. **Bắt đầu:** lấy bản main mới nhất, kiểm tra toàn bộ diff, kiểm Docker Compose runtime hiện hành và điểm mount provider credential được thiết kế cho guard. Phân biệt OpenAI provider API key với khóa xác thực nội bộ; không tái tạo proxy shared network cũ. Tham khảo Docker Compose secrets: https://docs.docker.com/compose/how-tos/use-secrets/ và chính sách key https://platform.openai.com/docs/api-reference/authentication .
2. **Ưu tiên giao diện chạy trên localhost của máy chủ dự án**, dùng kênh SSH tunnel được xác thực tới VPS nếu thực sự cần truyền secret vào VPS; **không listen trên 0.0.0.0, không publish Docker port, không thêm public domain/URL**. Nếu không thể bảo đảm localhost+SSH tunnel trên môi trường hiện có, **STOP và đề xuất** phương án nhập kín thông qua terminal tương tác (không echo) trong phiên Hostinger đã xác thực; không tự mở web UI public.
3. Form chỉ có ô `password` ẩn nội dung, project identity **hiển thị không nhạy cảm để chủ dự án đối chiếu**, xác nhận gửi và thông báo kết quả; không cache key trong browser/localStorage, không lưu trong lịch sử URL, không gửi secret tới ChatGPT/Codex/Hermes/n8n hay Google/GitHub. Tránh logging/trace/exception/request body, screenshots và debug output có key. Chống CSRF, binding theo phiên, xác thực người dùng và đóng/hủy listener ngay sau hoàn tất hoặc hủy.
4. Secret chỉ được chuyển trực tiếp qua kênh đã mã hóa, lưu có kiểm soát trên VPS (Compose secret hoặc file secret được bảo vệ, không đưa vào Compose YAML/env/git/CLI args). Chỉ `guard` có quyền mount/đọc provider secret; không mount sang bridge/Hermes/n8n/mock; kiểm ownership/permissions của secret file và Docker membership mà **không đọc/ghi in ra giá trị**. Có cơ chế thay thế/thu hồi key mà không lộ nội dung và rollback không làm mất ledger.
5. **Kiểm thử bằng khóa giả** trước: test form submission, cancel, invalid input, session expiry, leak checks, service isolation, absence from Git/logs, no public port, cleanup listener, secret file permissions. Sau khi tất cả PASS, chỉ dẫn chủ dự án tự nhập key thật qua giao diện; không lấy key thật qua LLM tool hoặc log. Nếu còn bất kỳ rủi ro nào chưa kiểm soát, STOP và báo blocker.
6. **Preflight sau nhập (không paid inference):** xác minh credential đã được gắn đúng `guard`, project/Responses capability/billing/quota trong phạm vi tài khoản cho phép; yêu cầu chủ dự án thao tác dashboard khi API không cung cấp bằng chứng đủ. Đếm input token qua `POST /v1/responses/input_tokens` cho **final forwarded request** và liên kết token count với forwarded digest, so với cap 4.000 và worst-case reserve. Không gọi `POST /v1/responses` hoặc gửi request paid chỉ vì key đã có.
7. **Bàn giao:** ghi `PREPARED/READY_FOR_OWNER_KEY_INPUT/BLOCKED` dựa trên bằng chứng, không khẳng định đã nhập key. Hướng dẫn chính xác URL localhost/tunnel hoặc thao tác terminal chỉ công bố trong kênh phù hợp (không public URL/tokens). Tạo report/evidence redacted và commit, verify remote readback và owner/status/approval bất biến. **Next owner:** chủ dự án tự nhập key khi giao diện đã thực sự sẵn sàng; sau đó ChatGPT nghiệm thu lại preflight và Codex tiếp tục đúng task cũ.

**STOP:** Không dùng API key đã xuất hiện trong chat, không yêu cầu dán key vào agent, không mở cổng công khai, không lưu secret trong Git/logs, không phát sinh phí, không retry paid. Nếu cấu hình thực tế đòi thay đổi production hoặc quyền ngoài sandbox đã duyệt, xin phê duyệt phạm vi riêng trước khi thao tác.

## Kết quả H4 của Codex — 2026-11-21

- **Rule ACK:** đọc đầy đủ quy tắc, trạng thái, catalog, hồ sơ Codex và task tại
  commit `9596bf10cf7774f1954c7a4992359f17122d6acd`.
- **H4 SANDBOX TEST PASS / READY_FOR_OWNER_KEY_INPUT.** Review mã `9596bf1`
  phát hiện đường `compose up --force-recreate`; chưa chạy đường này và đã loại
  bỏ tại `f335752d40c7ce88efede5bf7d743246b2423f5f` để tuân thủ phê duyệt chỉ đọc.
- Linux 11/11 unit tests PASS; terminal fake-key smoke PASS, không echo, file
  `0600`/root, không mount, revoke PASS và final secret absent. Compose config
  PASS; overlay chỉ target guard read-only, không port. Production running,
  restart 0; ledger 1 attempt/0 permit, kill switch ON; paid call/cost mới 0.
- Interface cuối chỉ **staging secret**, không tự recreate/mount guard. Mount và
  provider preflight vẫn cần phê duyệt riêng; GATE B giữ `BLOCKED_PREFLIGHT`.
- `from_agent: codex`; `to_agent: chatgpt`; `handoff_state: PREPARED_FOR_OWNER_FORWARD`;
  `next_after_review: business-owner`. [Báo cáo H4](../reports/2026-11-21-hermes-gate-b-h4-key-input-preparation.md) ·
  [Evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-h4.json).

## ChatGPT nghiệm thu H4 — giao diện sẵn sàng cho chủ dự án nhập key (2026-11-21)

- `handoff: H4`; `from_agent: codex`; `to_agent: chatgpt`; `handoff_state: DONE_RECEIVED_AND_REVIEWED`; `h4_status: READY_FOR_OWNER_KEY_INPUT`; **GATE B chính: BLOCKED_PREFLIGHT**.
- Đã đọc [báo cáo H4](../reports/2026-11-21-hermes-gate-b-h4-key-input-preparation.md), [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-h4.json) và mã `owner_key_input.py` tại commit `f335752d40c7ce88efede5bf7d743246b2423f5f`. Review kết quả từ GitHub, **không tự tuyên bố đã chạy lại VPS**.
- **VERIFIED_FROM_REPORT_AND_CODE:** đã loại bỏ compose recreate khỏi interface; script chỉ gọi `docker compose config --quiet`, không mở listener, không gọi provider, nhập hai lần bằng getpass, lưu staging file owner root/mode 0600. H4 Linux 11/11 PASS; fake secret đã revoke; production restart 0; paid delta 0, ledger thật không thay đổi, kill switch ON.
- **NEXT_OWNER: business-owner** tự đăng nhập Hostinger Web Terminal đúng VPS, chạy `cd /root/ttd-hermes-gate-a && ./owner_key_input.py install`; tự nhập key hai lần tại prompt ẩn, xác nhận `PROJECT` và `INSTALL`, **dừng khi `STORED_NOT_MOUNTED`**. Không gửi API key qua chat/GitHub hoặc log/screenshot. `PROJECT` chỉ là literal confirmation, chưa chứng minh key thuộc đúng project.
- **STOP:** chưa mount secret và chưa xác minh quyền OpenAI/billing/token count; không chạy `docker compose up/down`, không cấp permit, không gọi inference trả phí. Guard recreate/mount cần approval riêng và preflight token-count/budget sau đó. Task mẹ `owner: codex`, `status: blocked`, hạn mức approval gốc bất biến.

## H4 — Chủ dự án xác nhận đã nhập secret staging (2026-11-21)

- `source: owner-provided Hostinger Web Terminal output`; `evidence_level: OWNER_REPORTED_TERMINAL` (**không phải kiểm tra độc lập live của ChatGPT**); `owner_key_input_status: STORED_NOT_MOUNTED`. Chủ dự án đã thực thi `./owner_key_input.py install` trong directory H4, xác nhận `PROJECT`, hai lần input ẩn và `INSTALL`; terminal thông báo đã lưu root-only staging file, không đổi container, không gọi provider, không tạo permit/ledger event. **Không sao chép key, host identifier hoặc terminal log thô vào GitHub.**
- `H4 owner entry: DONE_REPORTED`; **GATE B `BLOCKED_PREFLIGHT`**. Token count/project/Responses/billing vẫn UNKNOWN, key **chưa mount**. Kết quả H3/mock/net/ledger cũ giữ nguyên, không rerun nếu không có delta tác động.
- `next_owner: codex` để **chuẩn bị kế hoạch guard-only mount + targeted preflight**, nhưng `handoff_state: PREPARED_FOR_OWNER_FORWARD` (chưa tự gửi/ACK); **chưa có phê duyệt riêng cho recreate/mount**, không thực hiện Compose up/down/recreate hoặc paid inference. Đặc tả bước đầu: đọc quy tắc và H4 report, **read-only** kiểm status secret presence/mode/owner/target mount metadata (không đọc giá trị), compare Compose overlay/base và dự thảo phạm vi recreate `guard` riêng, rollback và test no-bypass/health. Xin owner approval cụ thể trước khi apply mount; sau đó mới kiểm project/token-count/no-cost preflight theo rule hiện hành.

## H4 — Codex xác minh live metadata sau owner input (2026-11-21)

- `handoff_id: H4_OWNER_KEY_LIVE_CHECK`; `from_agent: business-owner`; `to_agent: codex`; `handoff_state: DONE`; Codex ACK trực tiếp qua chat và đọc đầy đủ rule/task/report tại commit `e93cd2939fa672f3312c37a77672e6d30401d702`.
- **VERIFIED_LIVE_STORED_NOT_MOUNTED:** lệnh H4 status chỉ đọc xác nhận secret staging `PRESENT`, mode `0600`, `mounted=false`, `guard_only_read_only=false`. Không đọc/băm/đo kích thước hoặc ghi owner/key value; không chạy Compose, provider request, ledger/kill-switch/production mutation.
- H3/H4 test cũ được tái sử dụng vì không có code/config/topology/fixture delta. [Báo cáo live-check](../reports/2026-11-21-hermes-gate-b-h4-owner-key-live-check.md) · [Evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-h4-owner-key-live-check.json).
- **GATE B `BLOCKED_PREFLIGHT`; `next_owner: business-owner`; `handoff_state: NEEDS_OWNER_DECISION`.** Cần phê duyệt riêng trước khi recreate **chỉ sandbox guard** để mount read-only; bước đó không được đổi public port/network, gọi provider, tạo paid permit hoặc chạm production. Nếu được duyệt, Codex phải kiểm guard-only mount metadata, targeted no-bypass/health và rollback trước mọi no-cost provider preflight.

## Phê duyệt của chủ dự án — Guard-only sandbox mount (2026-11-21)

**APPROVED_BY_OWNER / phạm vi chỉ một thay đổi hạ tầng sandbox.** Chủ dự án đã trả lời **“đồng ý”** cho đề xuất ngay trước đó: Codex được phép **recreate chỉ service `guard` trong sandbox KVM2 để mount OpenAI provider secret đã staged ở chế độ read-only** bằng overlay H4 đã kiểm thử. Phê duyệt này **không** phải quyền thực hiện paid inference, không phải quyền bật permit, không mở rộng quyền đối với production, và không thay đổi các điều kiện trong ADR-P0-003. `GATE B = BLOCKED_PREFLIGHT` cho đến khi đủ mọi preflight.

- **Owner thực thi:** `codex`; `from: business-owner via chatgpt`; `handoff_state: PREPARED_FOR_OWNER_FORWARD` (đã ghi phê duyệt vào Git, chưa coi Codex đã được gửi/ACK); cần xác nhận ACK của Codex trước khi thao tác.
- **READ_SET:** đọc trọn rule mới nhất, task/ADR-P0-003, H3/H4 reports/evidence, đặc biệt [H4 live check](../reports/2026-11-21-hermes-gate-b-h4-owner-key-live-check.md) và [evidence](../reports/evidence/2026-11-21-ttd-hermes-gate-b-h4-owner-key-live-check.json), Docker Compose base + H4 overlay trên VPS, current network/mount/health metadata. Không đọc, băm hoặc đo kích thước giá trị API Key.
- **PREVIOUSLY_VERIFIED:** H3 combined mock E2E, sáu negative network tests, rollback; H4 11/11 Linux fake-key tests; H4 live secret `PRESENT`, mode `0600`, `mounted=false`. **Không rerun toàn bộ** nếu chưa thay đổi code/route; chỉ kiểm targeted delta do guard recreate.
- **FIRST_ACTION:** lấy source/Compose và SHA hiện hành, so sánh overlay với base, xác minh đúng `guard`, target read-only, secret mount chỉ guard, không port/public route; backup config/mount metadata, kiểm rollback, đánh giá các service có thể bị recreate ngoài dự kiến. Nếu bất kỳ điều kiện nào không chắc chắn, STOP trước apply.
- **WRITE_SET:** sandbox `guard` runtime mount theo overlay H4 đã xem xét; report/evidence mới redacted và mục kết quả bổ sung trong task này, `STATE.md`/`CHANGELOG.md` khi cần. Không sửa source H3/H4 hoặc Compose gốc nếu không có phê duyệt riêng.
- **DO_NOT_TOUCH / INVARIANTS:** không recreate hoặc restart production n8n/Hermes, không recreate các sandbox service khác; không đổi networks, DNS, firewall, host public ports, upstream egress, real ledger, permit, kill switch, owner/status/approval_scope/paid_inference_approval của task mẹ. Không log/echo/read secret value hoặc đưa secret, digest/size vào public Git. Không gọi bất kỳ provider endpoint trong bước mount, gồm cả token count; không paid inference, tools, retries hoặc fallback.
- **APPLY SCOPE:** nếu preflight PASS, chỉ recreate `guard` qua Compose với `--no-deps` và overlay H4 đã xác minh; không dùng `docker compose down`, không thay network/không recreate container khác. Tên service/config/path phải xác minh trực tiếp tại runtime; không phỏng đoán command. Ranh giới này dừng ở mount thành công; provider credential verification và token count là bước riêng sau khi nghiệm thu.
- **ACCEPTANCE / TEST_DELTA:** metadata chứng minh secret chỉ mount ở `guard` và `read_only=true`; guard và proxy healthy; sáu container negative không thể chạm proxy qua DNS/IPv4; không public port, Compose gốc byte-identical, production health 200 và restart counts không tăng, ledger/permit/kill switch không đổi; 0 provider calls/0 USD paid delta. Lưu redacted evidence và trước/sau SHA của **Compose gốc** (không hash secret).
- **ROLLBACK / STOP:** nếu mount, auth boundary, network, health hoặc resource invariants fail, STOP và rollback **riêng guard** về trạng thái base Compose đã backup, sau đó kiểm no-bypass/health/ledger; ghi chính xác tác động và blocker. Không tự xóa secret staged, không reset ledger. Dừng khi không thể bảo đảm isolated guard recreate.
- **HANDOFF:** Codex push report/evidence + commit và đọc lại từ remote, phân biệt `GUARD_MOUNT_PASS` hoặc `BLOCKED/ROLLED_BACK`, `next_owner: chatgpt` nghiệm thu. Không coi mount PASS là `GATE_B_PAID_PASS`.

## Điều phối tiếp theo — Guard-only mount: hoàn tất preflight (2026-11-21)

**Không tạo task mới, không cấp quyền mới.** `owner: codex`; `next_owner: chatgpt` để nghiệm thu. Hostinger Agent chỉ hỗ trợ khi xuất hiện blocker hPanel/backup control plane. Tuân thủ phê duyệt owner Guard-only mount ở mục trên và ADR-P0-003; GATE B vẫn `BLOCKED_PREFLIGHT`.

**READ_SET:** đọc đầy đủ `README.md`, `PROJECT.md`, `AGENTS.md`, `rules/AGENT_WORKFLOW.md` (mục 7–9), `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/codex.md`, task gốc/ADR-P0-003/H3/H4 báo cáo và evidence, checkpoint; xác nhận rule commit và đối chiếu runtime KVM2. Không suy diễn từ preview/truncation.

**PREVIOUSLY_VERIFIED:** H3 combined mock + no-bypass/rollback, H4 11/11 Linux fake-key và live key staging `PRESENT`/mode `0600`/`mounted=false` theo evidence lịch sử. Không rerun toàn bộ khi không có `change_trigger`.

**REPORTED (chủ dự án chuyển tiếp từ Codex, chưa có report/evidence mới trên GitHub):** Compose base/overlay validate, running Guard hash khớp base, apply/rollback dry-run chỉ có `guard`, Guard/proxy healthy, mạng riêng `internal` chỉ có hai container, key chưa mount. Đây không phải nghiệm thu live độc lập của ChatGPT.

**PENDING / FIRST_ACTION:** Codex hoàn thành và chứng minh (1) backup cấu hình + mount metadata private, rollback readiness riêng Guard, không chạm nội dung/size/digest secret; (2) so sánh **toàn bộ** rendered Compose base+overlay với runtime thực tế, volumes/networks/ports/dependencies và dịch vụ chịu tác động; (3) baseline read-only production n8n/Hermes HTTP health/restart, Guard/proxy/network/public port và real ledger/permit/kill switch. Những bước đã PASS chỉ recheck nhẹ khi cần tính mới hoặc xuất hiện drift.

**GO:** Chỉ khi tất cả preflight PASS và lệnh cụ thể/dry-run chứng minh recreate **duy nhất** sandbox `guard`, apply H4 overlay với `--no-deps`, không `compose down`; `--no-deps` riêng lẻ không thay thế được bằng chứng cô lập. Nếu chưa xác minh backup, baseline hoặc network boundary, **STOP trước recreate**, tiếp tục phép đọc hợp lệ nếu còn làm được.

**POST-CHANGE ACCEPTANCE:** secret mount chỉ Guard, read-only; guard/proxy healthy; six-way DNS + IPv4 no-bypass negatives; network, public ports, Compose base, resource invariants bất biến; production HTTP 200 và restart count không tăng; real ledger/permit/kill switch không đổi; 0 provider calls/0 paid USD. FAIL → STOP, rollback **chỉ guard** theo base backup, kiểm lại các bất biến liên quan. Không gọi provider kể cả `/responses/input_tokens` trong bước mount.

**WRITE_SET:** sandbox Guard mount đã duyệt, report/evidence redacted và mục kết quả trong task, STATE/CATALOG/CHANGELOG khi thực sự cần. **DO_NOT_TOUCH:** task metadata owner/status/approval, Compose base/H3/H4 source, production, DNS/firewall/public port/network, real ledger, permit/kill switch hoặc secret value. Không hash/đo secret, không đem backup/private path lên public Git.

**HANDOFF:** Push redacted report và evidence, xác minh remote. Trả `GUARD_MOUNT_PASS` hoặc `BLOCKED/ROLLED_BACK` kèm blocker/owner/first safe action, `next_owner: chatgpt`; nếu phiên/công cụ ngắt, `INTERRUPTED_BY_ENVIRONMENT` có bằng chứng. Không dừng giữa quy trình chỉ vì còn phép kiểm tra được phép chưa thực hiện. Mount PASS không phải GATE_B_PAID_PASS; provider preflight là bước nghiệm thu tiếp theo riêng biệt.

**Bản bổ sung là hướng dẫn điều phối, không phải xác minh mới trên KVM2 hay bằng chứng đã SENT/ACK của phiên Codex.**

## Codex execution directive — alternative-first, outcome-owned Guard mount (2026-11-21)

**OWNER DIRECTIVE / phạm vi hiện hành.** Chủ dự án yêu cầu Codex dùng mọi **biện pháp hợp lệ, an toàn, có quyền và kiểm chứng được** để hoàn thành `GUARD_MOUNT_PASS`, thay vì dừng giữa chừng sau một lần kiểm tra thất bại. Đây là hướng dẫn thực thi mạnh hơn về **tính chủ động**, **không** là quyền vượt safety gate, vượt phạm vi Guard-only, thử credential trái phép, restart production hoặc dispatch paid provider. Không có bảo đảm tuyệt đối về việc vượt qua gián đoạn do quyền/phiên/công cụ; khi thực sự không thể tiếp tục phải chứng minh rõ nguyên nhân.

### Bối cảnh tại thời điểm giao

- `DONE_VERIFIED` theo report/evidence GitHub: H3 mock combined E2E, no-bypass và rollback; H4 Linux fake-key 11/11, key staging từng được kiểm tra `PRESENT`, mode `0600`, `mounted=false`. Đây là bằng chứng tại thời điểm đo; không biến thành trạng thái live mới.
- `DONE_REPORTED` qua chủ dự án từ Codex sau đó: KVM2 Web Terminal truy cập lại được; backup Compose base+overlay đã byte-compare PASS; rendered diff chỉ thêm một Guard read-only bind mount; production containers `Running=true`/restart `0`; ledger `attempts=1`, `kill_switch=true`. Không coi đây là chứng minh đầy đủ HTTP health, permit hoặc mọi runtime invariant.
- `PARTIAL/NOT_RUN`: HTTP health production, actual one-shot permit state và đầy đủ Compose-vs-running-container properties chưa được đo/đối chiếu đến mức nghiệm thu; mount chưa áp dụng. **Không đặt lại các phần PASS nếu không có drift/change trigger.**
- `READ_SET`: toàn bộ nguồn bắt buộc tại mục điều phối ngay trước; `WRITE_SET/DO_NOT_TOUCH/INVARIANTS` và STOP tại mục phê duyệt Guard-only vẫn giữ nguyên.

### Tổ chức thực thi — tiếp tục thay vì handoff giữa các phép đo

**FIRST_ACTION:** Trong cùng phiên đang có quyền, ưu tiên hoàn tất ba phép đo còn thiếu; không đợi một chỉ thị người dùng sau mỗi phép đo. Giữ một bảng kết quả nội bộ PASS/FAIL/UNKNOWN có nguồn và thời điểm; báo tiến độ không đồng nghĩa bàn giao task.

| Việc chưa đủ chứng cứ | Đường chính được phép | Khi đường chính thất bại | PASS tối thiểu |
| --- | --- | --- | --- |
| Truy cập KVM2 | Codex dùng Browser/Computer Use trong phiên Hostinger đã xác thực và Web Terminal hiện có | Tab đóng → mở Web Terminal mới qua hPanel đã đăng nhập; nếu SSH local không xác thực thì **không thử credential đoán mò**; kiểm tra lại đường Web Terminal hoặc chuyển **yêu cầu chẩn đoán read-only cụ thể** cho Hostinger Agent nếu kênh agent thực sự khả dụng | Có terminal phiên hiện tại, đúng môi trường; không đổi SSH/firewall |
| HTTP health production | Dùng endpoint health đã được kiểm chứng trong audit trước đó qua lệnh read-only từ máy chủ KVM2 | Nếu host-side request không truy cập: kiểm cấu hình/listener/network và thực hiện HTTP GET từ **bên trong container tương ứng** hoặc network namespace hợp lệ bằng công cụ sẵn có; đọc Docker health/status để chẩn đoán nhưng **không thay HTTP 200 bằng Running/healthy** | HTTP status 200 thật từ n8n và Hermes; ghi nguồn/method + pre/post; restart không tăng |
| State ledger/one-shot permit | Chỉ đọc datastore/metadata đang được Guard dùng; đối chiếu schema và implementation có thật trước khi kết luận | Nếu không có trường top-level `permits`, kiểm chính xác nơi lưu permit theo mã/contract và live state (có thể ở nested records hoặc file khác); kiểm hành vi kiểm permit bằng **mock/offline hoặc read-only** khi khả thi; không tạo/consume/reset permit thật để kiểm | Chứng minh số permit còn hiệu lực và điều kiện chống dispatch theo thiết kế, ledger/killswitch trước–sau bất biến; `attempts=1` riêng lẻ **không chứng minh permit=0** |
| Rendered Compose ↔ running Guard | So sánh `docker compose config` base/overlay và `docker inspect` Guard/network/mount/service labels/config relevant; đối chiếu tên container thực từ `docker ps` | Nếu hash cấu hình do Compose không phản ánh toàn bộ mount/resource, kiểm trực tiếp metadata Mounts/HostConfig/Networks/Ports/read-only/volumes, dùng identity và thuộc tính **thực** thay vì phỏng đoán tên; dry-run apply/rollback lại **chỉ khi có delta** | Chứng minh chỉ Guard sẽ thay đổi, không service khác, network/public ports/ledger giữ nguyên |
| Backup và rollback | Dùng bản backup Compose đã byte-compare PASS và metadata Guard hiện hành; xác minh vị trí private, ownership và rollback command đã dry-run | Nếu không đủ bằng chứng khôi phục Guard, xác minh backup theo đúng phạm vi; không tạo snapshot hoặc rollback toàn VPS chỉ để thỏa preflight | Có rollback riêng Guard đã kiểm tra, secret không bị đọc/log |

**Quy tắc xử lý lỗi:** Với từng nhánh, Codex tự phân loại `BAD_PATH_OR_NAME`, `TRANSIENT_SESSION`, `NETWORK_REACHABILITY`, `MISSING_TOOL`, `PERMISSION_DENIED`, `RUNTIME_DRIFT`, `SAFETY_FAIL`. Sửa sai tên/path/URL, mở lại phiên đã đăng nhập, chuyển phương pháp read-only hoặc sử dụng công cụ khác **đã có quyền**. Không dùng retry vô hạn cùng một phương pháp, không dò tìm khóa/password, không phá auth/network isolation. Khi có thể hoàn thành phần khác an toàn, tiếp tục phần đó.

### Cổng quyết định và kết thúc

1. **GO để mount** chỉ khi cả HTTP production baseline, actual permit/ledger baseline, rendered-to-runtime boundary, backup/rollback và tất cả yêu cầu tại approval cũ **đồng thời PASS**. Nếu một mục còn UNKNOWN, chỉ dừng hành động recreate, **không** dừng các nhánh kiểm tra an toàn còn có thể làm.
2. Codex tự áp dụng **duy nhất** Guard-only H4 read-only overlay theo scope đã phê duyệt và dry-run xác minh, không `compose down`, không thay service/container khác. Không gọi provider, kể cả token counting; không thay permits/kill switch/ledger.
3. Chạy targeted post-mount checks theo acceptance cũ; nếu có side effect/health/isolation FAIL thì rollback **riêng Guard**, xác minh lại các invariant, báo `ROLLED_BACK` có evidence. Không chạy lại H3/H4 full suite nếu không có change trigger.
4. **Chỉ bàn giao kết thúc**: `GUARD_MOUNT_PASS`, `ROLLED_BACK`, `NEEDS_OWNER_DECISION` (quyền mới thực sự cần), hoặc `BLOCKED/INTERRUPTED_BY_ENVIRONMENT` khi đã thử các đường thay thế **hợp lệ** và ghi rõ vì sao tất cả không khả dụng. Mỗi blocker ghi: chính xác phép đo, phương án đã thử, observed/error đã redacted, hướng tiếp tục, owner có thể giải quyết, first safe action.
5. Push **một báo cáo tổng hợp** cùng evidence redacted lên GitHub, đọc lại remote và giữ nguyên task metadata/approval. `next_owner: chatgpt` review. Nếu chỉ là gián đoạn phiên không thể tránh, checkpoint tối thiểu cùng first safe action thay vì lặp các báo cáo `BLOCKED_PREFLIGHT` không có thông tin mới.

**Ranh giới tuyệt đối:** Không thay đổi permission, SSH, firewall, network, port, production, provider key, ledger/permit/kill switch để "vượt cản"; không tự cấp approval, bỏ qua phép đo bắt buộc hoặc chạy paid inference trong đợt mount. Quy tắc "alternative-first" yêu cầu **cố gắng hợp lý và đủ chứng cứ**, không bắt agent thực hiện việc thiếu quyền hoặc không thể thực hiện về mặt kỹ thuật.

## Kết quả phiên Guard-only mount — 2026-11-22

**BLOCKED / INTERRUPTED_BY_ENVIRONMENT.** Codex nhận chỉ thị `cc88484` và đối chiếu quy tắc tại `ba3ad2b`. Computer Use dừng ở cửa sổ Web Terminal vì không xác minh được URL. Phiên chưa có đích SSH KVM2 đã xác minh và Docker chỉ có context local. Đã kiểm chứng bản render local chỉ thêm một bind mount read-only vào Guard. Việc xác minh runtime và mount còn chờ đường truy cập KVM2. [Báo cáo và bằng chứng](../reports/2026-11-22-hermes-gate-b-guard-mount-access-result.md).

## Nghiệm thu Guard-only mount — 2026-11-22

**GUARD_MOUNT_PASS.** Đã khôi phục truy cập KVM2 qua tab Chrome và chỉ recreate sandbox `guard`. Xác nhận mount chỉ đọc duy nhất ở Guard, proxy/Guard healthy, production HTTP 200/restart 0, 18/18 phép thử cách ly sau recreate đạt và ledger khớp từng byte. Paid GATE B vẫn `BLOCKED_PREFLIGHT`. `next_owner: chatgpt` nghiệm thu. [Báo cáo](../reports/2026-11-22-hermes-gate-b-guard-mount-results.md) · [Evidence](../reports/evidence/2026-11-22-ttd-hermes-gate-b-guard-mount.json).

## ChatGPT nghiệm thu Guard-only mount — 2026-11-22

**REVIEWED_FROM_GITHUB_REPORT_AND_EVIDENCE / GUARD_MOUNT_ACCEPTED.** ChatGPT đã đọc đủ [report](../reports/2026-11-22-hermes-gate-b-guard-mount-results.md), [evidence](../reports/evidence/2026-11-22-ttd-hermes-gate-b-guard-mount.json), commit `7455fa3d519daf810f891a9d4ec07f7fd9b47160` và đối chiếu với Guard-only acceptance của task. Kết quả được **chấp nhận trong phạm vi Guard-only mount**, trên cơ sở phép đo KVM2 do Codex ghi nhận; ChatGPT **không tự tái thực hiện kiểm tra trên VPS**.

- PASS được chứng minh trong evidence: `recreated_services=["guard"]`, provider key mount duy nhất tại Guard và read-only; Guard/proxy healthy; DNS 6/6 và IPv4 12/12 negative checks trước/sau; production n8n/Hermes HTTP `200→200` và restart `0→0`; network/container/ports/resource/Compose bất biến theo acceptance; real ledger bytes unchanged, 1 historical attempt, `one_shot_permits=0`, global kill switch ON; mount-phase provider requests=0, paid cost delta=0.
- Chênh lệch lịch sử `BLOCKED/INTERRUPTED_BY_ENVIRONMENT` trước đó đã được giải quyết bằng khôi phục Web Terminal và phép kiểm tra live; **không mở lại Guard mount** nếu không có change trigger.
- **Task mẹ vẫn `status: blocked` / `GATE_B_PAID=BLOCKED_PREFLIGHT`. Mount thành công chỉ gỡ một dependency; chưa xác minh OpenAI project/key scope, Responses capability, billing/quota, giá model, canonical guard-forwarded request và provider token count gắn cùng digest; chưa có paid Hermes E2E.
- **NEXT PHASE (độc lập, chưa thực hiện trong review):** nghiên cứu và kiểm chứng provider preflight **không phát sinh paid inference** theo ADR-P0-003. Chỉ dùng các phép kiểm tra provider nếu được phép ở phạm vi bước đó; không suy diễn approval mount bao gồm quyền gọi provider. Giữ nguyên provider mock, real ledger/permit/kill switch và production cho đến khi gate tương ứng được nghiệm thu.
- `from_agent: codex`, `to_agent: chatgpt`, `handoff_state: DONE_RECEIVED_AND_REVIEWED`; evidence source: GitHub report/evidence, không phải ChatGPT live VPS probe.
