---
id: hosting-progress-and-target-capabilities-2026-11-23
type: report
status: coordinator-estimate-pending-independent-qa
updated_at: 2026-11-23
owner: chatgpt-coordinator
next_owner: independent-reviewer
sensitivity: public-redacted
---

# Hosting / TTD AI Automation — tiến độ và năng lực mục tiêu ngày 23/11/2026

## 1. Phạm vi, chứng cứ và giới hạn

**Báo cáo tổng hợp ở mức danh mục, không phải xác minh live VPS, live connectors hay A0 nghiệm thu production.** Nguồn: [PROJECT](../PROJECT.md), [GOALS_AND_ROADMAP](../GOALS_AND_ROADMAP.md), [STATE](../STATE.md), [master backlog PR #6](https://github.com/DuyKienTTD/Hosting/pull/6), [allocation/cost-first PR #31](https://github.com/DuyKienTTD/Hosting/pull/31), và các PR/QA liên quan. Main tại thời điểm kiểm tra: `e385c1bea2070973e3007e5717f7e980348d6ab3`. PR #31 tại pre-change `1cdf6afecc41b3bf03437e55e4b88467bdb06209` chưa merge; lịch sử cấp quyền main và các ADR gốc không bị thay đổi. Ngày chốt: 23/11/2026.

Hồ sơ có nhiều kết quả `OFFLINE/MOCK_PASS`, `DESIGN_READY`, `PARTIAL`, `BLOCKED`, chưa triển khai. **Đếm PR hoặc bài test không phản ánh phần trăm nền tảng sử dụng được.** `STATE.md` được cập nhật lần cuối 22/11 nên một số handoff ngày 23/11 chỉ có trong comment PR: sử dụng comment mới với SHA và giới hạn để phân biệt, không coi text cũ là trạng thái mới.

## 2. Ước lượng tiến độ (phán đoán điều phối, chưa phải KPI vận hành)

Mỗi workstream được ước tính theo 5 mức: thiết kế, source/mock, QA độc lập, tích hợp thật, vận hành/khôi phục. Giá trị là **maturity estimate** từ chứng cứ, không phải đếm hạng mục đã ký hợp đồng. Trọng số là giả định để đánh giá tổng thể, cần A0 duyệt lại nếu phạm vi kinh doanh thay đổi.

| Workstream | Trọng số | Hoàn thành ước tính | Đóng góp vào tổng | Cơ sở |
|---|---:|---:|---:|---|
| WS-01 Governance / phân vai / audit | 15% | 65% | 9.75 điểm | Quy tắc, GitHub tasks/QA, PR #31 D7 độc lập PASS_WITH_LIMITS; nhiều PR draft, CI/metadata/gate merge chưa hoàn tất |
| WS-02 Infrastructure reliability | 20% | 25% | 5.00 điểm | VPS/n8n/Hermes hiện hữu; kiểm kê và một số fake canary/rollback; hardening, backup restore live, monitoring dài hạn còn chặn |
| WS-03 AI orchestration / connector / UI | 30% | 35% | 10.50 điểm | P0 sandbox; ENG #10/#13/#19/#21 official Linux 7/7 S4 + 12/12 S3 PASS offline; OPS #36 17/17 independent PASS_WITH_LIMITS; UX #16 UI mock; real connectors và production workflow chưa nghiệm thu |
| WS-04 Marketing/content/SEO/automation | 25% | 15% | 3.75 điểm | BIZ #20/#25, GROW #18/#23/#34 thiết kế/fixture; chưa chứng minh publish, media pipeline, GA4/WP/Ads live hoặc attribution end-to-end |
| WS-05 Security/data governance | 10% | 20% | 2.00 điểm | Policy/guard/no-bypass mock, SEC plan; các vấn đề VPS và durable snapshot/retention/role permission còn mở |
| **Tổng** | **100%** | | **31.00 điểm = ~31%** | **Ước tính phạm vi dự án, sai số khoảng ±10 điểm phần trăm** |

**Readiness để doanh nghiệp sử dụng luồng tự động hóa đa kênh end-to-end: 5–10% (ước tính riêng, không lấy 31% làm go-live).** Các service n8n/Hermes có thể chạy nhưng production n8n từng ghi 0 workflow ở snapshot; không có nghiệm thu mới chứng minh workflow marketing live. Trạng thái production theo snapshot phải tái xác minh trước mọi quyết định thực tế. `5–10%` chỉ biểu diễn mức thấp, không có SLA, số người dùng, conversion baseline hay mức độ sẵn sàng đã đo.

## 3. Bằng chứng quan trọng theo trạng thái

| Nhóm | Đã có bằng chứng | Chưa chứng minh / gate |
|---|---|---|
| Hạ tầng P0 | n8n/Hermes runtime audit, Level 1 9/9 mock, provider pilot, GATE A no-bypass/rollback; [STATE](../STATE.md) | GATE B paid `BLOCKED_PREFLIGHT`, Hostinger `PAUSED`, Codex `NOT_AUTHORIZED`; live reliability/restore/security chưa hoàn thành |
| ENG-01A connector abstraction | [PR10](https://github.com/DuyKienTTD/Hosting/pull/10), [PR13](https://github.com/DuyKienTTD/Hosting/pull/13), [PR19](https://github.com/DuyKienTTD/Hosting/pull/19), [PR21 Work Linux verdict](https://github.com/DuyKienTTD/Hosting/pull/21#issuecomment-7094836398): S4 7/7 + S3 12/12 official offline PASS, 2 assemblies cùng digest | Real WordPress/Woo/GA4 connectors, live auth, business data, deployment, merge `NOT_VERIFIED` |
| OPS monitoring | [PR36 independent QA](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7094319094): 17/17 mock; S3-P0 conceptual design [A1 review](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7094588077); S3-P1 read-only [limited draft](https://github.com/DuyKienTTD/Hosting/pull/36#issuecomment-7094940856) | Registry cap 256, unsigned snapshot, durable ledger, cross-process concurrency, authentic source, live notification remain not production-ready |
| Governance | [PR31 D7 QA](https://github.com/DuyKienTTD/Hosting/pull/31#issuecomment-7094529011), [owner cost-first directive](https://github.com/DuyKienTTD/Hosting/pull/31#issuecomment-7095081485) | PR31 draft/unmerged; source-status sync & final governance/CI gates pending |
| Operator console | [PR14](https://github.com/DuyKienTTD/Hosting/pull/14) UX spec; [PR16](https://github.com/DuyKienTTD/Hosting/pull/16) static UI with JS DOM mock | Chromium/browser E2E `NOT_RUN`, backend connector/auth/real approvals not present |
| Content & growth | [PR18](https://github.com/DuyKienTTD/Hosting/pull/18), [PR34](https://github.com/DuyKienTTD/Hosting/pull/34) 29/29 independent mock QA per governance; [PR23](https://github.com/DuyKienTTD/Hosting/pull/23) events/UTM; [PR20](https://github.com/DuyKienTTD/Hosting/pull/20) KPI draft | Actual assets rights, business approvals, account-scoped publishing, real leads/GA4 cost attribution and continuous operation not proven |
| Security | [PR29](https://github.com/DuyKienTTD/Hosting/pull/29), [PR35](https://github.com/DuyKienTTD/Hosting/pull/35) read-only feasibility and security reports | Root/password SSH, firewall/ports, backup restore test, permissions/monitoring, key custody: no blanket live PASS |

**Lưu ý:** Không đánh đồng `PR open` với `merged`, `TEST_DESIGNED` với `TEST_EXECUTED`, tác giả PASS với QA độc lập, tài liệu public với quyền sản xuất, và Provider E2E pilot với toàn bộ Hermes paid/Gate B.

## 4. Chức năng sản phẩm đích (khi có tích hợp và QA live riêng)

1. **Trung tâm điều hành:** dashboard nhiệm vụ/agent, hàng đợi phê duyệt, trạng thái, incident, audit, chi phí và rollback; builder kéo-thả hoặc cấu hình workflow theo trigger/owner/permission; lịch sử truy vết.
2. **AI coordinator và n8n workflow:** nhận yêu cầu, phân việc theo năng lực/chi phí, tự thực thi task trong phạm vi đã cấp quyền, quản lý callback, retry/idempotency, trạng thái UNKNOWN và người kiểm duyệt; vận hành theo lịch chỉ sau khi có scheduler thật.
3. **Website / WooCommerce / SEO:** đọc danh mục/bài/trang, phát hiện thiếu nội dung và metadata, đề xuất EN/VI và SEO, chuẩn bị bản nháp; sửa hoặc publish chỉ khi có connector ghi, quyền, backup/rollback và phê duyệt.
4. **Media & social:** xây dựng ý tưởng, kịch bản, storyboard, xử lý ảnh/video/voice theo pipeline phù hợp, QA thương hiệu/quyền sử dụng, lịch xuất bản YouTube/Shorts/TikTok/Meta nếu API/kênh được duyệt.
5. **Ads và chuyển đổi:** tổng hợp Google Ads/GA4 và UTM, phân biệt form/chat/lead đủ chuẩn, giám sát chi phí trên mỗi kết quả, đề xuất A/B và điều chỉnh có approval; không tự tăng ngân sách, không suy diễn nguồn lead từ dữ liệu thiếu.
6. **Báo cáo liên kênh:** dashboard KPI, bản tin định kỳ, cảnh báo thiếu dữ liệu hoặc sai lệch, đối chiếu phí AI/marketing, theo dõi hiệu quả nội dung, có nguồn và freshness của dữ liệu.
7. **Giám sát & bảo mật:** health/CPU/RAM/disk/containers/workflows, cảnh báo incident, chính sách least-privilege, giới hạn chi phí và kill switch, durable event/approval history, bản sao lưu/khôi phục đã kiểm chứng.
8. **Chăm sóc khách hàng (giai đoạn tùy chọn):** phân loại yêu cầu có đồng ý xử lý dữ liệu, gợi ý trả lời, chuyển sales/human; tự động phản hồi chỉ khi có chính sách, kiểm thử và phê duyệt riêng.

**Tất cả trên là năng lực mục tiêu, không phải tính năng đã có thể sử dụng end-to-end ngay hôm nay.** Không cam kết tự hoạt động 24/7 nếu chưa có scheduler, retry state, notification và vận hành được nghiệm thu.

## 5. Ưu tiên tiếp theo theo dependency / chi phí

**Ưu tiên A — nền tảng:** chốt rules/cost-first và đồng bộ current status, review/merge theo A0; xác nhận nguồn hệ thống sống; backup/rollback/security read-only → scope hardening có phê duyệt.

**Ưu tiên B — một MVP có giá trị đo được:** chọn **UC01 WordPress/Woo read-only content/product gap audit** hoặc **UC03 UTM & lead reporting** từ BIZ-02, sau khi A0 chọn mục tiêu; tích hợp nguồn **chỉ đọc**, đo baseline, một workflow n8n sandbox + operator approval và audit log, QA bởi người khác. Ưu tiên một luồng thật thay vì phát triển đồng thời tám luồng lý thuyết.

**Ưu tiên C — reliability:** durable ledger/snapshot integrity/outbox/monitoring theo thiết kế được QA, runtime test cô lập, cảnh báo suy giảm, backup restore; không nâng mock PR36 lên live mặc định.

**Ưu tiên D — growth:** marketing read connectors, content approval, media publish và Ads write từng kênh, từng quyền, từng hạn mức; chỉ triển khai khi có số liệu và người duyệt.

## 6. Những quyết định cần A0

- Chọn **một use case MVP đầu tiên**; cho biết mục tiêu là website/SEO, lead tracking hay media để tránh dàn trải.
- Xác nhận tiêu chí thành công bằng số liệu thực, ngân sách vận hành, chuẩn bảo mật dữ liệu, mức chấp nhận gián đoạn và quyền kết nối read-only.
- Phê duyệt riêng mọi merge/live/paid/credential/production action; các chỉ thị Hostinger PAUSED, Codex NOT_AUTHORIZED, Hermes HOLD_NO_NEW_TASKS vẫn giữ nguyên.

**Handoff:** Đề xuất `PORTFOLIO_PROGRESS_ESTIMATE_READY_FOR_INDEPENDENT_QA`; đây là báo cáo điều phối, không phải acceptance của A0 hoặc đo KPI trực tiếp.
