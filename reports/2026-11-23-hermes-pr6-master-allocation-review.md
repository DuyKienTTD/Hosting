---
id: hermes-pr6-master-allocation-review-2026-11-23
type: report
status: current
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
task_id: ttd-multi-agent-master-allocation-2026-11-23
source: origin-main-readonly-review,pr6-head-readonly-review,session-capability-checks
---

# Hermes review — PR #6 multi-agent master allocation

## ACK thống nhất theo mục 7

```text
TASK: ttd-multi-agent-master-allocation-2026-11-23
AGENT / SESSION: Hermes Agent WebUI, profile=default, checked_at=2026-11-23T01:43:25Z
REVIEWED: main=a22516aa9e5940baccc37ab2edf9eeed2ccc3d93; PR6=e5f702e96e04e229f853fe336d0e627713fcf350; rules=origin/main@a22516aa9e5940baccc37ab2edf9eeed2ccc3d93; read_status=FULL_READ
ACK_STATE: ACKNOWLEDGED
CAPABILITY: VERIFIED=GitHub read/write via git+SSH in prior Hermes session history, file/terminal/web/browser tool surface, 55 skills, memory/session_search, cronjob_manage list=0, review of repo/PR artifacts in current session; UNTESTED=background 24/7, external connectors/accounts, delegated long-lived orchestration, production connectors for growth channels; BLOCKED=live Hermes inference API on VPS, n8n production MCP, paid/provider actions, production mutations, hPanel/Hostinger control from this Hermes WebUI session
OWNERSHIP: ACCEPT=BIZ-01,GROW-01; CHANGE=GOV-02->codex primary + chatgpt governance review because validator/CI is technical and ChatGPT Work capability is still unverified, AI-01->chatgpt-work primary but keep chatgpt fallback because Work has no independent capability survey/ACK yet, INF-02->chatgpt-work provisional only after capability ACK otherwise chatgpt fallback, UX-01->chatgpt-work provisional but keep chatgpt owner until Work confirms capacity, GROW-02->chatgpt primary + hermes support unless a verified Work session is available; DECLINE=AI-04,INF-01,SEC-02,ENG-01,OPS-01 as primary owner due current Hermes limits on VPS/hPanel/runtime changes and lack of verified production connectors
DEPENDENCIES: ACCEPT=main skeleton of GOV-01->GOV-02, INF-01->SEC-02, AI-01+AI-02+INF-01->AI-03, BIZ-01->BIZ-02, BIZ-02->UX-01/ENG-01/GROW-01, ENG-01->OPS-01/GROW-02; REMOVE/ADD=remove blanket AI-04->ENG-01 edge because many ENG-01 schema/state-machine/mock tasks can progress before Hermes paid Gate B, add CHATGPT-WORK-CAPABILITY-ACK as gate for GOV-02/AI-01/INF-02/UX-01/QA-01 ownership, add SEC-01->GROW-01 for permissions/retention/publish-policy review, add BIZ-01 feasibility findings -> GROW-02 tracking/report design; PARALLELIZE=BIZ-01 || INF-01 || INF-02 || AI-01 || AI-02, and later GOV-02 || SEC-01 || BIZ-02 once owner ACKs exist
CAPACITY: max_concurrent=1 primary ownership package or 1 primary + 1 light read-only consult; active_existing_work=PR6 review only; workload_risks=overloading ChatGPT Work before its independent ACK, overloading Codex with both Gate B execution and all governance/monitoring tasks, assigning Hermes to any task that assumes live production connectors or VPS mutation capability
MISSING_TASKS_OR_DUPLICATES=CATALOG on main indexes 15 task paths while tree has 17; missing tasks are tasks/2026-11-21-repository-operating-plan.md and tasks/2026-11-21-hermes-gate-b-guard-transaction-hardening.md; PR6 also assumes ChatGPT Work as an active reviewer/owner but repo has no independent capability survey/ACK artifact for that agent; WS-04/WS-05 planning lines remain portfolio placeholders without concrete task files for several deliverables
ACCEPTANCE_OR_SAFETY_GAPS=AI-02 and AI-04 must explicitly separate fake-local/provider-only/Hermes-real evidence; GOV-02/UX-01/INF-02 cannot be treated as ready-owned by ChatGPT Work until Work capability is ACKed; every proposed line should carry existing_task_path or explicit NO_TASK_YET marker; PR6 should state that Hermes accepts BIZ-01/GROW-01 only for discovery/briefing/draft evidence, not connector live execution
VERDICT: ACCEPT_WITH_CHANGES
EVIDENCE: report=reports/2026-11-23-hermes-pr6-master-allocation-review.md ; branch artifact + commit adding this report
NEXT_OWNER: chatgpt
```

## Phạm vi đọc và đối chiếu

Đã đọc/đối chiếu đầy đủ từ `origin/main@a22516a` và PR #6 head `e5f702e`:

- `AGENTS.md`
- `PROJECT.md`
- `GOALS_AND_ROADMAP.md`
- `rules/AGENT_WORKFLOW.md`
- `rules/REPOSITORY_SECURITY.md`
- `STATE.md`
- `CATALOG.yaml`
- `agents/README.md`
- `agents/hermes.md`
- `tasks/2026-11-23-multi-agent-master-allocation-review.md` từ PR #6
- metadata toàn bộ `tasks/` trên `origin/main`
- capability profiles của ChatGPT, Codex, Hostinger Agent và n8n trên branch hiện hành

## Xác nhận capability phiên Hermes hiện tại

### VERIFIED trong phiên/ngữ cảnh hiện tại

- Đọc tài liệu repo, PR #6 và branch heads bằng terminal + Git.
- Có tool surface file/terminal/web/browser/skills/memory/session recall.
- `skills_list` hiện có **55 skills**.
- `session_search` hoạt động.
- `cronjob_manage list` trả **0 job**.
- Có thể tạo/cập nhật báo cáo Git và push bằng Git/SSH khi nhánh làm việc đồng bộ với remote.
- Có thể làm review planning/read-only ở mức repo, task graph, dependency và năng lực agent.

### AVAILABLE_UNTESTED trong phiên này

- Background scheduling dài hạn / 24x7 execution.
- Orchestration bằng delegation cho các work package dài hơn một turn.
- Connector/account thực cho business systems.
- Review/comment trực tiếp trên PR #6 qua GitHub comment API/UI từ chính phiên này.

### BLOCKED / UNKNOWN trong phiên này

- Không có bằng chứng quyền trực tiếp tới hPanel/Hostinger control plane từ phiên Hermes WebUI hiện tại.
- Không có live production connector cho WordPress/Ads/YouTube/TikTok/Meta/Kling/HeyGen/ElevenLabs.
- Không có bằng chứng live inference API của Hermes production runtime; `Hermes WebUI` không được đồng nhất với `Hermes auxiliary/runtime`.
- Không có evidence độc lập cho ChatGPT Work capability survey trong repo tại base snapshot đang review.

## Nhận định tổng thể về PR #6

PR #6 là một **portfolio index hợp lý về mặt điều phối**, có ưu điểm lớn là:

1. tách workstream rõ ràng;
2. nhấn mạnh `owner duy nhất` cho từng dòng;
3. coi năng lực agent là session-scoped thay vì vĩnh viễn;
4. yêu cầu ACK song song của các agent thay vì giả định chấp thuận;
5. không tự biến DRAFT thành approval production.

Từ góc nhìn Hermes, bản nháp này **đủ tốt để tiếp tục hợp nhất**, nhưng **chưa nên được chốt nguyên trạng** vì còn vài lỗi thực dụng về ownership, gating và mapping với backlog thật.

## Các nhiệm vụ Hermes chấp nhận

### ACCEPT

#### BIZ-01 / WS-04

Hermes phù hợp làm owner cho phần:

- capability discovery read-only cho các nền tảng tăng trưởng/media/SEO,
- phân loại `VERIFIED / DOCUMENTED / UNKNOWN / BLOCKED`,
- soạn capability matrix, scope, quota assumptions và acceptance draft,
- đối chiếu docs + evidence trước khi giao Codex/n8n triển khai.

Điều kiện:

- chỉ read-only / draft / planning,
- không kết luận connector production-ready nếu chưa có evidence live,
- không kết nối account thật, không publish, không paid API.

#### GROW-01 / WS-04

Hermes phù hợp làm owner cho phần:

- media/content discovery,
- brief/QA rubric,
- social/SEO draft planning,
- editorial workflow proposal và publish gate design.

Điều kiện:

- output là brief/spec/rubric/report,
- không render/publish/Ads write,
- quyền thật và account readiness phải do owner khác xác minh riêng.

### CHANGE

#### GOV-02

PR #6 đang giao `ChatGPT Work (đề xuất) / Codex`. Từ góc nhìn Hermes, owner chính nên đổi thành:

- **Codex primary** cho validator/CI/spec kỹ thuật
- **ChatGPT** giữ governance review / acceptance framing
- `ChatGPT Work` chỉ là reviewer tùy phiên, không nên là owner mặc định khi chưa có capability ACK độc lập

Lý do: GOV-02 không chỉ là tài liệu; nó đụng validator/CI/spec kỹ thuật và write-path policy, phù hợp Codex hơn Work.

#### AI-01

Giữ `chatgpt-work` là primary reviewer nếu có phiên đủ năng lực, nhưng cần ghi rõ:

- **fallback owner: chatgpt** nếu Work chưa ACK capability/capacity,
- Hermes không nên là owner chính cho line này vì đây là review độc lập B2-O thiên về source/evidence QA đã gắn với Work/Codex history.

#### INF-02

Để `chatgpt-work` là provisional owner là hợp lý về mặt runbook/tài liệu, nhưng chỉ sau capability ACK. Nếu không, **chatgpt** nên là fallback owner. Hermes chỉ nên hỗ trợ reasoning/report wording nếu cần, không nên owner chính vì task này nghiêng về operator runbook và monitoring drill documentation.

#### UX-01

Không nên mặc định giao hẳn cho ChatGPT Work khi chưa có capability ACK. Đề xuất:

- **chatgpt** owner tạm cho user-story / operator needs / acceptance
- `chatgpt-work` hoặc Hermes làm reviewer/alternate tùy session thực tế
- Codex giữ feasibility kỹ thuật khi cần

#### GROW-02

Nên đổi thành:

- **chatgpt primary** cho tracking plan, KPI logic, report shape
- **hermes support** cho reasoning/draft/report narrative
- **codex / eng-01** chỉ nhập cuộc khi có automation/data-path cụ thể

Lý do: GROW-02 phụ thuộc dữ liệu và governance nhiều hơn là connector execution trong giai đoạn planning.

### DECLINE

Hermes không nhận owner chính cho:

- `AI-04`
- `INF-01`
- `SEC-02`
- `ENG-01`
- `OPS-01`

Lý do:

- các dòng này cần VPS/runtime/network/Compose/callback/monitoring implementation hoặc quyền hPanel/VPS thực,
- capability profile của Hermes hiện tại chỉ chứng minh mạnh ở **reasoning, read-only analysis, Git-backed reporting và planning**, không chứng minh quyền mutation production hay owner hạ tầng.

## Dependency graph — chấp nhận gì, cần sửa gì

### ACCEPT

Mình chấp nhận bộ khung chính sau:

- `GOV-01 -> GOV-02`
- `INF-01 -> SEC-02`
- `AI-01 + AI-02 + INF-01 -> AI-03`
- `BIZ-01 -> BIZ-02`
- `BIZ-02 -> UX-01`
- `BIZ-02 -> ENG-01`
- `BIZ-02 -> GROW-01`
- `ENG-01 -> OPS-01`
- `ENG-01 -> GROW-02`

Đây là skeleton hợp lý cho plan-level coordination.

### REMOVE / RELAX

#### Bỏ cạnh blanket `AI-04 -> ENG-01`

PR hiện khiến người đọc dễ hiểu rằng `ENG-01` phải chờ `AI-04`. Điều này quá chặt.

Nhiều phần của `ENG-01` có thể làm sớm mà **không cần** Hermes paid Gate B, ví dụ:

- schema/state-machine design,
- connector adapter mock,
- callback contract,
- durable job-state proposal,
- test harness/no-side-effect workflow design.

Chỉ nhánh nào **phụ thuộc Hermes paid real path** mới phải chờ `AI-04`.

### ADD

1. **ChatGPT Work capability ACK** phải là gate cho:
   - `AI-01`
   - `INF-02`
   - `GOV-02` ownership nếu vẫn giữ Work
   - `UX-01`
   - `QA-01`

2. **SEC-01 -> GROW-01**
   - vì content/media/publish workflows cần policy về retention, copyright/use-rights, consent và approval boundary trước khi coi là sẵn sàng triển khai.

3. **BIZ-01 feasibility -> GROW-02**
   - nếu BIZ-01 xác nhận một số kênh hoàn toàn `UNKNOWN/BLOCKED`, tracking/attribution plan cho các kênh đó phải giữ ở trạng thái draft, không gắn thành ready execution.

## Công việc có thể chạy song song

### W0 song song hợp lý

Các line sau có thể song song thật sự mà không chờ nhau về mặt planning/read-only:

- `BIZ-01` (Hermes)
- `INF-01` (Hostinger Agent)
- `INF-02` (Work hoặc fallback ChatGPT)
- `AI-01` (Work/fallback ChatGPT)
- `AI-02` (Codex)
- `GOV-01` (ChatGPT)

### W1 song song sau ACK

Khi owner ACK/capacity rõ hơn:

- `SEC-01`
- `BIZ-02`
- `GROW-01`
- `GOV-02`
- `UX-01`

không nhất thiết phải đợi tất cả W0 đóng hẳn, miễn dependency trực tiếp đã đủ.

## Điểm nghẽn chính

1. **ChatGPT Work là nút nghẽn giả tiềm năng**
   - PR giao nhiều line cho Work khi repo chưa có capability survey/ACK độc lập cho Work.

2. **Codex có nguy cơ bị dồn việc**
   - nếu giữ cùng lúc `AI-02`, `AI-04`, `ENG-01`, `OPS-01`, và một phần `GOV-02` thì critical path sẽ bị dồn về Codex.

3. **AI-04/Gate B không được lan blocker sang mọi việc AI/automation**
   - Gate B paid Hermes là blocker hẹp, không được biến thành blocker cho toàn bộ thiết kế connector, reporting, content/growth planning.

4. **WS-04 còn nhiều line là portfolio placeholder**
   - chưa nên xem là ready queue cho execution nếu chưa có task con hoặc task hiện hữu mapping đủ rõ.

## Missing tasks / duplicates / mapping gaps

### Concrete gap 1 — CATALOG chưa index đủ task hiện có

So khớp `origin/main` cho thấy:

- `tasks/2026-11-21-repository-operating-plan.md`
- `tasks/2026-11-21-hermes-gate-b-guard-transaction-hardening.md`

đang có trong tree nhưng **không được index trong `CATALOG.yaml`** ở base snapshot review.

Đây là gap thật, không phải giả định.

### Concrete gap 2 — thiếu capability ACK riêng cho ChatGPT Work

PR #6 dựa đáng kể vào `ChatGPT Work`, nhưng ở repo base hiện chưa có:

- capability survey riêng cho Work,
- ACK artifact độc lập kiểu tương đương Codex/Hermes/Hostinger Agent.

Vì vậy nhiều owner gán cho Work phải ở trạng thái **provisional**.

### Concrete gap 3 — WS-04/WS-05 là portfolio lines nhưng chưa task hóa đủ

Các line như:

- `BIZ-01`
- `BIZ-02`
- `GROW-01`
- `GROW-02`
- `SEC-01`
- `SEC-02`
- `UX-01`

đang hợp lý ở mức kế hoạch, nhưng chưa có `existing_task_path` tương ứng trong main snapshot. Vì thế chúng nên được đánh dấu rõ là:

- `PLANNED_NO_TASK_YET`
- hoặc `PORTFOLIO_PLACEHOLDER`

thay vì để người đọc dễ hiểu là backlog implementation-ready.

### Duplicate / overlap risk

- `AI-04` trong master plan dễ overlap với chuỗi Gate B/H6 hiện hữu nếu không ghi rõ rằng line này **tham chiếu task gốc Gate B** chứ không mở một nhánh execution mới.
- `GOV-02` dễ overlap với `repository-operating-plan` nếu không ghi rõ phạm vi mới là validator/CI/spec delta, không viết lại toàn bộ operating plan.

## Acceptance / safety gaps cần sửa trước khi chốt PR

1. **Bổ sung `existing_task_path` hoặc `NO_TASK_YET` cho từng dòng**
   - để phân biệt line nào đã map vào task thật, line nào chỉ là planning stub.

2. **Bổ sung gate `Work capability ACK required`**
   - cho mọi line currently gán Work làm owner/reviewer chính.

3. **Làm rõ rằng Hermes nhận BIZ-01/GROW-01 ở chế độ discovery/draft only**
   - không được hiểu thành owner live connector, paid media, publish hoặc VPS mutation.

4. **Tách `AI-04` khỏi `ENG-01` ở mức blanket dependency**
   - chỉ phần real-Hermes route mới chờ Gate B.

5. **Ghi rõ upper load risk cho Codex**
   - nếu Codex đang owner chuỗi Gate B/Gate H6, không nên đồng thời bị coi là owner mặc định của mọi implementation/governance kỹ thuật khác.

## Kết luận Hermes

Từ góc nhìn Hermes, PR #6 **đủ tốt để tiếp tục** và đúng hướng điều phối đa agent, nhưng cần vài chỉnh sửa quan trọng trước khi ChatGPT hợp nhất thành `APPROVED_ALLOCATION`.

Điểm mạnh nhất của PR là:

- không giả định agent đã ACK,
- không biến DRAFT thành quyền triển khai,
- có ý thức chống dồn việc vào một agent,
- buộc mọi agent tự xác nhận capability phiên hiện tại.

Điểm cần sửa nhất là:

- owner provisional cho ChatGPT Work,
- blanket dependency AI-04,
- mapping portfolio lines với task thật,
- và phân biệt rõ Hermes-planning với Hermes-production-runtime.

## Handoff

- `from_agent=hermes`
- `to_agent=chatgpt`
- `handoff_state=DONE`
- `next_owner=chatgpt`
- `recommended_next_action=` cập nhật PR6/master plan theo các thay đổi ownership/dependency ở trên; đặc biệt thêm gate capability cho Work, ghi `existing_task_path|NO_TASK_YET`, và giữ Hermes ở vai trò BIZ-01/GROW-01 discovery/draft-only cho đến khi connector/runtime thật được chứng minh.
