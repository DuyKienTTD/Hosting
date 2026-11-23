---
id: ttd-parallelism-dependencies-bottlenecks-2026-11-23
type: report
status: proposed
updated_at: 2026-11-23
sensitivity: public-redacted
---
# Bản đồ công việc song song, phụ thuộc và điểm nghẽn

## Phạm vi
Đối chiếu CATALOG.yaml, STATE.md, roadmap, portfolio và đề xuất phân bổ trên `main`, cùng các trạng thái được ghi cho Gate B và nhóm B2. PR #6 vẫn là draft, nên bản đồ này là kế hoạch điều phối, không thay đổi owner/status và không mở quyền thực thi. Các kết quả mock/fake được coi là đầu vào có giới hạn, không phải bằng chứng production.

## Có thể triển khai song song ngay, nếu xác nhận owner và input

### Nhóm A: discovery, governance và baseline chỉ đọc
- GOV-01: tổng hợp governance, owner, acceptance criteria.
- INF-01: baseline hạ tầng Hostinger/VPS/Docker chỉ đọc.
- BIZ-01: discovery kênh và phạm vi use-case.
- UX-01: user stories/mock nếu đầu vào nghiệp vụ đã đủ, không triển khai.
- ENG-01A: thiết kế offline/fake adapter.
- GROW-02A: kế hoạch event và đo lường offline.
- QA-01: chuẩn hóa tiêu chí review, miễn là reviewer không tự QA sản phẩm của mình.

Các việc trên có thể chạy song song vì không cần paid inference, connector thật hoặc thay đổi production. Chúng vẫn phải dùng SHA và evidence rõ ràng, tránh tạo nhiều bản đo cùng một đầu ra.

### Nhóm B: các kiểm tra B2 độc lập có thể tiếp tục theo fixture
- B2-H assurance, B2-J idle/startup/recovery, B2-K cross-service mock và B2-L fixture writer đã có evidence/readiness được ghi. B2-M canary QA và B2-N contract QA có thể chuẩn bị hoặc review độc lập trên phạm vi cô lập, nhưng không được nâng trạng thái live chỉ từ fake canary.
- Hostinger WS02 baseline và Work monitoring/triage có thể chạy song song ở mức tài liệu/read-only; kết quả baseline là input cho runbook, không phải điều kiện để viết mọi phần của runbook.

### Nhóm C: chuẩn bị kỹ thuật chưa chạm production
- AI-02 preflight/fake-only, AI-03 tổng hợp quyết định, ENG-01A và các thiết kế rollback có thể chuẩn bị song song khi không gọi paid provider.
- SEC-01 policy/classification có thể chạy song song với INF-01; SEC-02 chỉ nên bắt đầu phần thiết kế, không coi là restore/hardening live.

## Chuỗi phụ thuộc chính

1. **AI/Gate B:**
   `AI-01 (QA đầu vào) + AI-02 (preflight/fake) + baseline hạ tầng` → `AI-03 synthesis/decision` → `AI-03F fixture có điều kiện` → `AI-04 paid/live preflight` → paid Gate B.
   Gate B hiện vẫn `BLOCKED_PREFLIGHT` theo trạng thái đã ghi. Provider credential guard, token count, secret mount/strict isolation, redeploy/rollback và no-bypass là các điều kiện khác nhau; không gộp thành một PASS duy nhất.

2. **Kỹ thuật connector:**
   `ENG-01A offline design` → kiểm tra contract/semantics → `ENG-01B connector thật` → dữ liệu thật và phê duyệt riêng.
   ENG-01B không phụ thuộc vào việc mọi nội dung UX/GROW hoàn thành, nhưng phụ thuộc scope, consent, quyền dữ liệu và approval.

3. **Tăng trưởng/đo lường:**
   `BIZ-01 discovery` → `BIZ-02 use-case/KPI` → `GROW-01 brief/draft` hoặc `GROW-02A offline measurement plan` → `GROW-02B real pipeline`.
   GROW-02B không nên mở khi connector, dữ liệu và quyền truy cập chưa sẵn sàng.

4. **Vận hành:**
   `INF-01 baseline` → `INF-02 runbook/triage` → `OPS-01A health/SLO design` → `OPS-01B live scheduler/monitoring`.
   OPS-01B còn cần quyền, preflight, rollback và phê duyệt tác động; không suy ra từ một baseline thành công.

5. **B2/canary:**
   `B2-H/B2-J/B2-K/B2-L evidence` → review độc lập `B2-M/B2-N` → quyết định readiness riêng.
   B2-M prepared không đồng nghĩa live canary đã chạy; cần evidence đúng SHA và phạm vi KVM2 cô lập.

6. **Di trú Hermes:**
   `resource identity + source/target inventory + backup/rollback design + compatibility check` → phê duyệt riêng → migration execution → post-migration validation.
   Task di trú trên main đang bị chặn; không chạy song song với thay đổi guard/Gate B nếu cùng chạm runtime hoặc dữ liệu.

## Điểm nghẽn
- **Gate B paid:** điểm nghẽn lớn nhất. Chưa có bằng chứng live đầy đủ cho strict credential isolation, provider token count, secret mount đúng guard, no-bypass và redeploy/rollback. Không được dùng kết quả mock để mở paid dispatch.
- **Quyền và input chủ sở hữu:** credential, consent, approval và quyền dữ liệu không thể tự suy ra từ hồ sơ Agent hoặc từ GitHub write. Đây là điểm nghẽn ngoài khả năng tự động của các Agent.
- **Tách runtime:** Hermes trên U4S/ttdnew.tech và Hermes trên KVM2 là hai runtime riêng. Inventory hoặc kết quả của một runtime không thay thế kiểm tra runtime còn lại.
- **Evidence/metadata lệch:** CATALOG, STATE và task B2-M có trạng thái khác nhau; cần một người đồng bộ theo evidence trước khi gọi là ready.
- **Tải Codex:** nhiều gói code/live đều hướng về Codex. Chỉ mở một gói kỹ thuật chính mỗi đợt, ưu tiên AI-02, rồi mới chọn AI-03F/AI-04 hoặc ENG/OPS.
- **Reviewer độc lập:** QA-01, B2-M và B2-N bị nghẽn nếu người thực hiện đồng thời làm reviewer. Phải giữ reviewer tách khỏi implementer và cố định SHA.
- **Thay đổi có tác động:** restore, migration, connector thật, scheduler live, paid API và restart/redeploy đều là các cổng phê duyệt riêng. Không coi chúng là bước tiếp theo tự động sau một báo cáo read-only.

## Lịch điều phối đề xuất
- **Đợt 1 song song:** GOV-01, INF-01, BIZ-01, AI-01, AI-02 fake-only, B2-M/B2-N preparation/review, UX-01 hoặc GROW-02A chỉ chọn một cho Work.
- **Đợt 2:** AI-03 synthesis sau khi nhận AI-01/AI-02/baseline; INF-02 và OPS-01A từ baseline; ENG-01A; BIZ-02.
- **Đợt 3 có điều kiện:** AI-03F và AI-04; ENG-01B; GROW-01/GROW-02B; OPS-01B; migration execution. Chỉ mở từng nhánh khi dependency và approval tương ứng đã PASS.

## Quy tắc chống nghẽn và chống chạy nhầm
- Mỗi output chỉ có một owner chính, reviewer độc lập và evidence path.
- Dùng `blocked`, `prepared`, `in_progress`, `complete` đúng nghĩa; không biến `prepared` thành `complete` do có mock evidence.
- Không xếp một Agent vào hai gói kỹ thuật có khả năng thay đổi runtime cùng một đợt.
- Chốt dependency bằng task ID/SHA, không bằng tên Agent hoặc suy đoán từ capability survey cũ.
- Không coi báo cáo này là ủy quyền chạy paid API, migration, restore, restart, redeploy hoặc thay đổi production.

## Giới hạn
Đây là bản đồ điều phối dựa trên tài liệu và evidence được lưu trong repository. Chưa xác minh lại toàn bộ runtime live, capacity của từng Agent trong phiên hiện tại, hoặc approval của chủ dự án cho các thao tác có tác động.
