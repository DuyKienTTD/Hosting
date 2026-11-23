---
id: ttd-a1-cost-first-master-allocation-2026-11-23
type: task
status: proposed_governance_with_agent_evidence
updated_at: 2026-11-23
owner: chatgpt
sensitivity: public
approval_scope: governance_and_safe_offline_only
---

# Master allocation v2 — thêm A1, Codex exception-only

**A0 directive 23/11/2026:** hủy/thu hồi mọi **phân công Codex chưa thực hiện thuộc loại đơn giản**, không xóa mã và bằng chứng đã hoàn thành. Codex chỉ được dùng sau khi chứng minh không tác nhân khác nào có năng lực/công cụ thực thi an toàn và A0 chấp thuận chi phí của đúng gói đặc biệt. Quyết định áp dụng cho **các giao việc mới và phần việc còn lại**, không sửa lịch sử kết quả.

## Danh bạ sáu AI vai trò

| Vai trò | Agent | Chủ trì | Giới hạn |
|---|---|---|---|
| A0 | Chủ dự án, người ra quyết định | quyền, ngân sách, publish, lựa chọn nghiệp vụ | Không phải agent |
| Điều phối | ChatGPT Điều phối | điều hành, triage, GitHub governance, nghiệm thu, chọn agent | Không có quyền tự mở phiên agent hay phê duyệt chi phí |
| **A1** | **ChatGPT Thông thường, phiên riêng** | công việc tài liệu/JSON/code nhỏ, metadata, QA nguồn, kế hoạch | A1 tự báo cáo GitHub/Workspace/Ads/WordPress/media đã kết nối; từng task kiểm quyền thật, không tự chạy nền |
| Work | ChatGPT Work | đa bước, browser/UI, source QA độc lập, kiểm thử offline | Theo quyền và công suất phiên; không QA code của mình |
| Hermes | Hermes WebUI | code/validator offline phù hợp, media/content/business, schema và mock | Đúng profile/credential; không live/publish mặc định |
| Hostinger | Hostinger Agent | VPS/hPanel/hosting, OPS, SEC theo capability lịch sử | **PAUSED A0 2026-11-23**, chưa có ACK pause trong phiên; không giao mới/tiếp tục |
| **Codex — ngoại lệ** | Codex | case không thể làm bằng 4 lựa chọn trên (ví dụ race/fault phức tạp, low-level runtime) | **CODEX_NOT_AUTHORIZED** mặc định, cần chứng minh và A0 duyệt từng việc |

**n8n là workflow engine, không tính là AI Agent.** A1 bổ sung chứ không đổi tên ChatGPT Điều phối hoặc Work.

## A1 capability update (self-reported 2026-11-23)

A1 **đã xác nhận nhận vai trò** và bàn giao capability survey cho Điều phối. GitHub (branch/commit/PR), Drive, Gmail, Calendar, WordPress staging/production, Google Ads read-only, Canva/HeyGen, vidIQ/YouTube và QA tooling được A1 **tự báo cáo đã kiểm tra**. Xem [hồ sơ A1](../agents/a1.md) để phân biệt từng scope `SELF_REPORTED_VERIFIED_BY_A1` với quyền ghi/chi phí `NOT_TESTED`; đã có [PR #32](https://github.com/DuyKienTTD/Hosting/pull/32) và Work QA offline PASS_WITH_LIMITS; quyền và test của tác vụ khác vẫn phải xác minh.

**Routing mở rộng:** ưu tiên A1 cho Google Workspace, read-only Ads analysis, WordPress staging/SEO QA, GitHub technical QA và content analytics theo đúng task approval. Các thay đổi Ads, publish YouTube, production WP, AI media trả phí, email gửi ra ngoài vẫn có gate theo công việc; không gán cho A1 quyền production hoặc ngân sách tự động.

**Handoff status hiện hành:** A1 `ROLE_ACTIVE`; `A1-GOV02-QA01=AUTHOR_DONE + WORK_QA_PASS_WITH_LIMITS` trên PR #32 (chưa merge); `A1-GOV02-S2-A=PROPOSAL_DONE + HERMES_QA_PASS_WITH_LIMITS` tại PR #33 (không có Phase B). `A1-OPS01A-S2-D2=PREPARED_FOR_OWNER_FORWARD` tới khi có task-specific ACK. GitHub comment không tự giao việc.

## A0 override — Hostinger PAUSED / ownership (2026-11-23)

[OPS pause](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7093337445) và [SEC pause](https://github.com/DuyKienTTD/Hosting/pull/29#issuecomment-7093338761) thu hồi các lệnh Hostinger chưa hoàn tất. **Không suy ra phiên Hostinger đã ACK dừng.** Năng lực, code, QA và feasibility lịch sử được giữ nguyên.

[A1 được giao OPS-01A/S2-D2](https://github.com/DuyKienTTD/Hosting/pull/24#issuecomment-7093346631) trên **branch A1 riêng stacked PR24** tại HEAD `e9c2d8f759850ea9c654de7e103549e041f66679`. Work đã QA D1 bằng 18 nhóm synthetic và báo `NEEDS_HOSTINGER_DELTA`; A1 sửa F1–F3 trên branch riêng, **không sửa branch Hostinger**; Work re-QA sau handoff. P0-R1 và năm SEC work orders giữ `NOT_AUTHORIZED`/PAUSED. Chỉ A0 mới có thể cho Hostinger resume, cần ACK rồi mới giao việc.

## Thu hồi và chuyển việc Codex tại checkpoint

| Công việc | Bằng chứng lịch sử | Quyết định áp dụng phần còn lại | Owner ưu tiên/QA |
|---|---|---|---|
| GOV-02/S1 validator PR #28 | Codex `6dafae5`; Work QA `NEEDS_CODEX_DELTA` `GOV02-QA-01` | **CANCEL_CODEX_REWORK**; giữ mã/báo cáo; chuyển sửa cross-package document-ID | **A1** nếu Git/Python verified, nếu không Hermes; **Work** QA độc lập |
| GOV-02/S2 Phase A PR #30 | Source plan delivered; không phải metadata patch đã duyệt | **CANCEL_CODEX_PHASE_B_AND_FURTHER_DISPATCH**; tái sử dụng Phase A | **A1 + ChatGPT Điều phối** xử lý metadata plan; reviewer Work |
| ENG-01A S1/S2/S3/S4 PR #10/#13/#19/#21 | Offline code và PASS lịch sử, S3-D1 Work QA, S4 Linux NOT_RUN | **PRESERVE_COMPLETED_ARTIFACTS**, không giao Codex cho index/README/doc/refactor hoặc rerun thường lệ; không merge mặc định | A1/Hermes/Work làm tài liệu, kiểm tra source; chỉ cân nhắc Codex cho khuyết điểm runtime thực sự độc quyền |
| AI-02/B2-P PR #7 và PR #5; AI-03F, AI-04 | Fake/source evidence; KVM2 `NO_GO`, paid Gate B `BLOCKED_PREFLIGHT` | **NO_NEW_CODEX_DISPATCH**, giữ blocker, không tự mở fake KVM2/paid | ChatGPT gate; Work QA; **Hostinger preflight PAUSED, chỉ tiếp tục sau A0 resume + Agent ACK**; ngoại lệ Codex phải phê duyệt mới |
| ENG-01B real connector, OPS-01B live, GROW-02B scheduled, GOV-02 CI | Chưa có quyền triển khai/live tương ứng | **DEFER_NOT_AUTHORIZED**, không giữ Codex làm mặc định | Agent hợp quyền khi gate mở; Codex ngoại lệ sau đánh giá |
| Hạng mục đơn giản khác trong backlog gắn Codex (docs, JSON, tests nhỏ, mock, lint, Git index) | Phải đối chiếu task SHA mới nhất | **CANCEL_CODEX_ASSIGNMENT_IF_NOT_STARTED**, không xóa deliverable đã làm | A1/Work/Hermes phù hợp; **Hostinger PAUSED**, chỉ sau A0 resume + ACK |

**Không xóa PR, commit, report, QA, branch.** `CANCEL_CODEX_*` chỉ là **thu hồi/không phát hành lệnh điều phối**, không chứng minh Codex đã nhận được thông báo dừng; mọi task active ở phiên khác cần người sở hữu chuyển chỉ thị dừng và nhận ACK. Không dùng một comment để ghi đè owner/status của task đã thực hiện bởi agent khác.

## Gói công việc cho A1 (lịch sử đã thực hiện; không giao lại)

**Task:** `A1-GOV02-QA01` — sửa validator lỗi ID trùng giữa các package tại PR #28 theo Work [finding](https://github.com/DuyKienTTD/Hosting/pull/28#issuecomment-7092060267). **Owner A1 provisional**, fallback Hermes nếu A1 thiếu local Git/Python và GitHub write. **FIRST_ACTION:** đọc rules/main/PR #28 SHA `6dafae50bd17bc1a18080b13b86c5b8c35573580`, nguồn `sandbox/repo-metadata-validator/validate.py` và fixtures, check quyền trong phiên. Đọc `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/a1.md`, báo cáo Work và Codex; ghi rule/base SHA. **WRITE_SET:** nhánh riêng với source validator + đúng fixture affected, báo cáo delta riêng; không sửa trực tiếp PR #28 nếu không được điều phối phê duyệt; không sửa main/index. **TEST_DELTA:** hai package khác path cùng report ID phải báo `DUPLICATE_DOCUMENT_ID`; cùng path thấy qua hai snapshot không được báo false duplicate; lỗi sha/source vẫn chặn, ID task riêng không bị lẫn ID report; chạy targeted positive+negative offline. **PASS:** source SHA và test thực chạy + GitHub readback; Work QA độc lập (nếu Work đã đọc finding thì được QA code của A1, không QA code tự viết). **STOP:** thiếu tool/owner branch/conflict -> `BLOCKED_CAPABILITY` và chuyển Hermes. **NEXT_OWNER:** ChatGPT Điều phối.

## Các nhiệm vụ khác theo hiệu quả/chi phí

| Hạng mục | Primary | Review/giới hạn |
|---|---|---|
| CATALOG/STATE/CHANGELOG đối chiếu, 5 dòng `NO_TASK_YET`, metadata PR #10/#13 | A1 và ChatGPT Điều phối (mỗi file đúng một writer) | Work review; **chưa merge hoặc sửa shared index khi có conflict** |
| BIZ-02, GOV-01/A0 choices, GROW-01/S2 | Hermes, A1 hỗ trợ tài liệu | A0 duyệt lựa chọn; Work reviewer theo slot |
| UX Operator Console, browser QA, integration demo | Work | A1/Hermes review độc lập, không giả định browser PASS |
| OPS-01A/S2-D1 và SEC-02/S2 feasibility | **Historical Hostinger DONE_WITH_LIMITS; Agent PAUSED** | Work 18-case D1 QA còn 3 finding; A1 D2 sole writer; Hostinger feasibility PR29 source review đã hoàn tất |
| GROW-02A event dictionary/UTM | Hermes đã làm; Work QA đã PASS offline | Không triển khai tracking live |
| ENG-01A offline release/Linux test | Work/A1 nếu verified toolchain Linux/Git (Hostinger PAUSED) | Chỉ khi không agent nào làm được mới đề xuất Codex với bằng chứng |
| AI-03, paid Gate B | ChatGPT gate; Work input (Hostinger PAUSED) | `NO_GO_CURRENT_PREFLIGHT`/`BLOCKED_PREFLIGHT`; Codex không được tự kích hoạt |

## Bắt buộc trước mỗi đề xuất Codex

`ALTERNATIVES_CHECKED` (A1, Work, Hermes, Hostinger, ChatGPT và tool evidence), `WHY_ONLY_CODEX` (hạn chế xác minh cụ thể), `MAX_SCOPE`, `ESTIMATED_COST_OR_CALL_CAP`, `STOP`, `ACCEPTANCE`, `INDEPENDENT_REVIEWER`, `A0_APPROVAL_ID`. Nếu thiếu bất kỳ mục nào: `CODEX_NOT_AUTHORIZED`. Không suy ra giá token, mức giá cụ thể hay quyền từ tên model.

**Tất cả task:** `TO/OWNER, MODE, FIRST_ACTION, BASE_SHA, READ_SET, WRITE_SET, PREVIOUSLY_VERIFIED, DO_NOT_TOUCH, TEST_DELTA, INVARIANTS, STOP, ACCEPTANCE, EVIDENCE, NEXT_OWNER`. `PREPARED_FOR_OWNER_FORWARD` cho tới khi có bằng chứng Agent nhận. Không triển khai production/paid/merge theo văn bản này.

## Tiêu chuẩn chốt điều phối

A1 xuất hiện trong directory/rules/portfolio và có handoff sẵn; Codex assignment đơn giản được thu hồi rõ, không xóa lịch sử; tất cả quyền/safety gate giữ nguyên. Đây là **đề xuất cập nhật governance qua PR**, chưa merge main. 
