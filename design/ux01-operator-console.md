---
id: ux01-operator-console
type: knowledge
status: draft
updated_at: 2026-11-23
sensitivity: public
---

# UX-01/S1 — Giao diện điều hành và Workflow Builder

Phạm vi: đặc tả developer triển khai bằng dữ liệu giả. Mặc định chọn **Sandbox · dữ liệu giả**. Staging/Production chỉ hiện dưới dạng lựa chọn bị khóa kèm lý do. Auth, API console, scheduler, integrations và activation thật đều **UNIMPLEMENTED** trong S1. Mọi KPI kinh doanh, attribution, mục tiêu chuyển đổi và baseline chưa chốt mang nhãn `PROVISIONAL_BIZ02`; dữ liệu giả không được trộn với số liệu thật. Audit n8n trước đây quan sát 0 workflow production; trạng thái hiện tại chưa xác minh.

## 1. Màn hình và navigation

O = owner, A = admin, P = operator, R = reviewer. Các chữ dưới đây chỉ vai trò đề xuất. Mọi route và đối tượng vẫn phải kiểm scope theo workspace và môi trường. Menu ẩn đích không có quyền xem; URL trực tiếp trả 403 hoặc 404 theo chính sách chống lộ đối tượng.

| Route | Desktop | Mobile | Ai xem / trọng tâm |
| --- | --- | --- | --- |
| /dashboard | Tóm tắt sandbox, runs gần đây, hàng chờ duyệt và incident | Một cột, danh sách theo mức ưu tiên | O A P R; chỉ hiện dữ liệu trong scope |
| /agents | Danh sách agent, capability và nguồn bằng chứng | Danh sách → chi tiết toàn màn | O A P R; inspect nguồn và freshness |
| /workflows | Danh sách, Builder canvas + panel node | Builder theo danh sách node có thứ tự; chi tiết mở màn riêng | O A P chỉnh draft theo scope, R chỉ xem |
| /connections | Danh sách theo source, environment, consent và quyền | Danh sách → bảng scope | O A quản lý, P/R chỉ đọc metadata được chia sẻ |
| /approvals | Queue và chi tiết version/diff, phạm vi, ngân sách | Chi tiết duyệt ở màn riêng | O A R theo scope duyệt; P xem yêu cầu của mình |
| /runs | Lọc, timeline, evidence và reconciliation | Timeline dọc, fact sheet riêng | O A P R theo scope; quyền reconcile riêng |
| /incidents | Queue tín hiệu, runbook, timeline xử lý | Incident card và nút nhận xử lý | O A P R theo scope; R chỉ xem |
| /content | Nội dung theo draft/version/channel, preview và trạng thái duyệt | Draft list → preview | O A P R trong scope; publish bị khóa nếu thiếu gate |
| /settings/audit | Vai trò, môi trường, audit và trạng thái kill switch | Audit trong mục Thêm; bảng chuyển danh sách chi tiết | O A cấu hình theo scope; R đọc audit được cấp |

Desktop ≥1024 px: sidebar cố định, header workspace/env, vùng nội dung. 768–1023 px: sidebar thu gọn, panel dạng drawer. 360–767 px: Dashboard, Runs, Approvals, Thêm; phần còn lại từ Thêm. Trong Builder, thứ tự tab và focus giữ nguyên qua đổi kích thước. [Wireframes và hành vi cụ thể](ux01-wireframes.md).

| State chung | Hành vi |
| --- | --- |
| Loading | Giữ tiêu đề và bộ lọc, aria-busy, khóa hành động ghi cho tới khi có snapshot và version |
| Empty | Nêu dữ liệu còn thiếu, ví dụ “Chưa có run giả”; CTA chỉ hiện khi có scope |
| Error | Ghi mã lỗi an toàn và thời điểm, nút tải lại cho thao tác đọc; giữ draft chưa lưu trong bộ nhớ phiên |
| Blocked | Hiện lý do, môi trường, gate còn thiếu và đường tới evidence/yêu cầu duyệt khi có quyền |
| Stale/conflict | Hiện version snapshot đã cũ; lấy lại revision, xem diff rồi lưu lại có chủ ý; giữ bản chỉnh sửa đang mở |

## 2. Permission, approval và capability

| Vai trò đề xuất | Đọc | Ghi |
| --- | --- | --- |
| Owner | Workspace, audit, quyền và mọi đối tượng trong scope | Quản trị vai trò/consent và kill switch theo policy; có thể duyệt yêu cầu người khác nếu đủ scope |
| Admin | Metadata cấu hình và audit cấp workspace | Quản lý cấu hình/consent được ủy quyền; duyệt khi có scope riêng; không vượt budget/env |
| Operator | Workflows/runs/incidents được giao | Draft, validate, simulate, yêu cầu duyệt; nhận incident/reconcile nếu có scope |
| Reviewer | Version, diff, evidence đã lược bỏ dữ liệu và approval được giao | Approve/reject nếu có scope; không sửa version đang duyệt |

Scope gợi ý: `workflow:read/draft/validate/simulate/activate`, `approval:request/decide`, `connection:read/propose/consent/revoke`, `run:read/reconcile`, `incident:read/update`, `content:read/draft/publish`, `audit:read`, `policy:manage`. Quyền theo workspace, resource, env và operation. Token/secret lưu ở vault phía server; UI chỉ nhận alias, trạng thái và metadata đã lược bỏ. Consent xác nhận actor, account alias, phạm vi read/write, purpose, expiry/revoke và môi trường. GA4 S1 dùng fixture đọc giả, không bật OAuth; tách quyền đọc dữ liệu khỏi quyền liên kết tài khoản.

Approval bind theo workspace, action, version/digest, target/env, scope, currency, trần tiền, số lần tối đa, valid-from/expiry, approver và audit ID. Design mặc định tách requester khỏi approver. Thay version/tài khoản/chi phí, hết hạn, thu hồi consent hoặc scope thay đổi làm gate cũ mất hiệu lực. Budget unknown chặn hành động tính phí. Review draft media chỉ bind action `content.review`; publish là action riêng.

Server kiểm quyền hiện hành, scope + consent, version, capability của môi trường, approval, budget, kill switch ngay trước side effect và giữ chỗ budget/ghi audit theo hợp đồng triển khai. Khi policy chưa load, không có server decision, có race hoặc gate lỗi, UI khóa Activate/Publish và server từ chối request. Audit ghi actor, time, request/correlation ID, env, action, decision/reason và digest đã lược bỏ dữ liệu. Checkpoint rollback chỉ chạy qua action đã duyệt riêng.

| Badge năng lực | Cách dùng |
| --- | --- |
| DOCUMENTED | Vendor tài liệu có hỗ trợ; hiện nguồn và ngày kiểm |
| VERIFIED_IN_PROJECT | Có report dự án, ghim SHA, môi trường và phạm vi bằng chứng |
| VERIFIED_IN_SESSION | Đã xác minh trong phiên được ghi kèm thời điểm, quyền và env |
| UNVERIFIED_ACCOUNT_ACCESS | Chưa xác minh quyền tài khoản đích; live control bị khóa |

Badge có thể cùng tồn tại; bằng chứng mock ghi rõ mock. Kiểm tra quá hạn chuyển về trạng thái chưa đủ để cấp quyền. [BIZ-01 PR #12](https://github.com/DuyKienTTD/Hosting/pull/12).

## 3. Run, timeline và phục hồi

Trình tự đề xuất: pending → working → sending → completed | failed | outcome_unknown. Lỗi xác định trước dispatch có thể working → failed; timeout có khả năng đã dispatch có thể working → outcome_unknown. Khi đã lưu outcome, sending có thể phục hồi việc gửi cùng callback identity/receipt theo policy; command tạo dispatch mới là đường riêng và bị khóa khi outcome chưa xác định. Event version tăng, thứ tự server dựa trên sequence/event ID và timestamp hiển thị có timezone. Không dùng thứ tự client nhận sự kiện để suy causal order.

Timeline hiển thị job/task/run/correlation, workflow version, request digest, attempt, decision, dispatch/receipt count khi có evidence, callback status, event digest và receipt ID. Callback server xác minh auth/signature, freshness, job/run/correlation/digest và callback ID. Thiếu identity trả lỗi schema dự kiến 422, mâu thuẫn binding/replay trả 409. Replay giống hệt trả receipt đã commit. Late success hoặc disputed result tạo event riêng và mở reconciliation; UI giữ nguyên recorded outcome, hiển thị review decision riêng và mọi resolution có audit. Timeout không đồng nghĩa refund, fail chắc chắn hay an toàn để chạy lại. Kill switch chặn admission/side effect mới theo policy; incident escalation gắn owner, lý do và evidence. UI không hứa exactly-once cho API thật. [Phạm vi fixture ENG-01A-S1](https://github.com/DuyKienTTD/Hosting/pull/10).

## 4. Bảng khả thi theo control

Mỗi mục trong nhóm control có chung scope/gate hiển thị dưới đây. Ký hiệu: S = UI_SPEC_ONLY; M = OFFLINE_MOCK_AVAILABLE; B = BACKEND_NOT_IMPLEMENTED; E = EXTERNAL_ACCOUNT_UNVERIFIED; P = PRODUCTION_APPROVAL_REQUIRED. Giai đoạn I = MVP_IMPLEMENT_NOW (chỉ mock/design đã được phép qua task sau), N = NEXT_AFTER_MOCK, L = LATER_AFTER_REAL_AUTH. Những endpoint mới đều B. Hàng M chỉ dựa trên fixture/hồ sơ được ghi rõ.

| ID | Control | Khả thi / giai đoạn | Server check hoặc UI stub |
| --- | --- | --- | --- |
| C01 | Menu, workspace/env, bộ lọc, tìm kiếm, refresh, mở chi tiết | S / I | Scope từng route/resource, env ngoài sandbox bị khóa |
| C02 | Agent inspect, badge, xem nguồn evidence | S / I | Capability read scope và metadata redaction |
| C03 | New workflow, fork version, mở/so sánh version | S+B / I | Mock; server về sau kiểm workspace, role và immutable version |
| C04 | Add/edit/remove/reorder node, connect/remove port, mapping, canvas zoom | S / I | Client kiểm kiểu, server validate authoritative khi có backend |
| C05 | Save draft, tải version mới khi conflict | S+B / I | Mock ETag/If-Match, 409/412 giữ local draft |
| C06 | Validate | S+B / I | Mock validator; server trả issues theo node/port và snapshot digest |
| C07 | Simulate, xem kết quả | S+M+B / I | Synthetic fixture; kiểm scope, env, zero-cost/no-egress policy, không dispatch thật |
| C08 | Request approval, mở queue, xem diff, approve/reject | S+B / N | Kiểm approver scoped và độc lập, version/action/env/budget/expiry, audit |
| C09 | Activate, schedule, pause activation | S+B+P / L | Stub disabled; policy decision phía server và idempotent command |
| C10 | Connections inspect, chọn GA4 fixture, lưu read-only proposal | S+B / I | Schema & scope read, fixture alias, không gửi OAuth |
| C11 | Connect/OAuth, verify access, revoke consent | S+B+E / L | Stub chế độ giả; server consent, vault, revocation khi triển khai |
| C12 | Runs timeline, evidence preview, copy public IDs/digest | S+M+B / I | Read-scoped, redacted, stable event order |
| C13 | Request reconciliation, replay callback | S+M+B / N | Same callback binding; replay UI chỉ ghi yêu cầu khi có policy; server tự quyết |
| C14 | Retry dispatch / rollback | S+B+P / L | Block unknown retry; rollback plan, approval và ownership riêng |
| C15 | Incident nhận xử lý, note, chuyển owner, đóng | S+B / N | Mock; server transition, audit và recovery rule theo signal |
| C16 | Draft media, preview, chọn channel giả | S+B / I | Draft version scoped, source mock; chưa gọi render hoặc account |
| C17 | Approve media draft | S+B / N | Cùng C08 với action review riêng |
| C18 | Publish | S+B+E+P / L | Stub disabled; separate publish scope, owner approval, consent và version digest |
| C19 | Settings roles, audit filter/view, kill switch | S+B+P / N hoặc L | View audit mock ở N; role/kill switch action môi trường thật ở L với policy/approval |
| C20 | Retry tải màn, dismiss panel, helper keyboard, reset lọc | S / I | Retry chỉ GET; disabled reason đọc được bằng bàn phím |

## 5. Developer handoff

Components: AppShell, RoleNav, EnvironmentBadge, DataState, CapabilityBadge, EvidenceLink, FlowCanvas/FlowList, NodeInspector, PortMapping, ValidationSummary, VersionDiff, ApprovalPanel, RunTimeline, ReceiptPanel, IncidentQueue, ContentPreview, AuditReadView, GateReason. Dùng cùng state/validation contract cho canvas và mobile list.

| Entity | Trường tối thiểu và quan hệ |
| --- | --- |
| agent / capability | agent_id, workspace_id, name, capability_ids; capability_id, operation, env, evidence level, source SHA, observed_at, expiry |
| workflow / workflow_version | workflow_id, owner_id, env; version_id, parent_id, graph, schema_version, digest, status, ETag |
| connector | connector_id, capability_id, source, env, account_alias, consent_state, scope metadata và expiry |
| run | job_id, task_id, run_id, correlation_id, workflow_version_id, digest, state, attempt, timestamps |
| approval | approval_id, requester_id, approver_id, operation, version/digest, env, budget/window, decision |
| event / receipt | event_id, run_id, sequence, kind, observed_at, payload_digest; receipt_id, callback_id, binding_digest, committed_at, outcome |
| incident | incident_id, signal, severity, status, owner_id, samples, linked_run_id, runbook, recovery evidence |

API boundary đề xuất, toàn bộ **UNIMPLEMENTED**: GET /workspaces/{id}/{resource} có scope và cursor; POST /workflows và PUT /versions/{id}/draft với If-Match; POST /versions/{id}/validate hoặc /simulate với digest; POST /approvals và /approvals/{id}/decision; GET /runs/{id}/events và /receipt; POST /runs/{id}/reconciliation-requests; PATCH /incidents/{id} có ETag. POST /versions/{id}/activate và /content/{id}/publish giữ stub khóa ở S1. Callback internal server-to-server, không expose action “gửi callback tùy ý” từ browser. 403 scope/consent, 409 binding hoặc unknown retry, 412 stale version, 422 invalid graph/shape; 503 policy unavailable. API response dùng stable reason code và correlation ID. Dữ liệu hiển thị chỉ từ fixtures hoặc backend scoped đã có ở giai đoạn sau.

Developer kế tiếp được Điều phối phân công theo task riêng; Work là owner bản thiết kế, ChatGPT Điều phối reviewer. [Wireframes và acceptance paths](ux01-wireframes.md) · [Tabletop report](../reports/2026-11-23-work-ux01-s1-product-ux-review.md).
