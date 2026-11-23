---
id: hermes-biz02-s1-usecases-kpi-2026-11-23
type: task
status: draft_delivered_for_review
updated_at: 2026-11-23
sensitivity: public-redacted
owner: hermes-webui
next_owner: chatgpt
---

# BIZ-02/S1 — Use-case, KPI và ưu tiên kinh doanh (đặc tả bàn giao)

- **Lệnh/ACK:** `EXECUTE BIZ-02/S1`, [PR #18 comment 7091126062](https://github.com/DuyKienTTD/Hosting/pull/18#issuecomment-7091126062).
- **Rule/main SHA đọc:** `e385c1bea2070973e3007e5717f7e980348d6ab3`; **PR #6:** `03fb56b6d3b4f42a1cb65c6e3c87a19099785044`.
- **FIRST_ACTION:** fetch main/PR refs; kiểm tra không có task, report hoặc branch BIZ-02 trùng; đọc rules, BIZ-01 và GROW-01 trước khi viết.
- **Owner thực thi:** Hermes WebUI; **owner quyết định tiếp:** ChatGPT Điều phối/A0 đối với ưu tiên kinh doanh và tài trợ.

## Trạng thái kế thừa (không thử lại)

| Mục | Trạng thái | Nguồn và giới hạn |
|---|---|---|
| BIZ-01 | DONE_REPORTED/ACCEPTED_WITH_LIMITS | PR #12, commit `8c821bb`; docs/asset inventory, không live connector |
| GROW-01/S1 | DONE_REPORTED/ACCEPTED_WITH_LIMITS | PR #18, commit `3c8cb40`; P1–P3 DRAFT và 5/5 gate giả, không publish |
| ENG-01A S1/S2 | DONE_REPORTED_OFFLINE | PR #10/#13; contract và adapter GA4/WP/Woo giả, real untested |
| UX-01 S1/S2 | DONE_REPORTED_OFFLINE | PR #14/#16; spec và UI mock, backend/browser E2E chưa chứng minh |
| BIZ-02 | NOT_RUN trước lượt này | Không tìm thấy branch/path BIZ-02 sau fetch |

## Ranh giới

- **READ_SET:** AGENTS, PROJECT, GOALS_AND_ROADMAP, workflow §§7–10, security, STATE, CATALOG, agents/hermes; PR #6/#12/#18/#10/#13/#14/#16 tại SHA ghi trong báo cáo.
- **WRITE_SET:** chỉ tệp task này, `reports/2026-11-23-hermes-biz02-s1-prioritization.md`, `reports/evidence/2026-11-23-hermes-biz02-s1-priority-matrix.json` trên branch riêng.
- **DO_NOT_TOUCH:** STATE/CATALOG/CHANGELOG/rules, PR khác, website, customer data, WordPress/GA4/Ads/social/email, VPS, migration, OAuth, paid API và publishing.
- **INVARIANTS:** mọi baseline định lượng chưa có dữ liệu là `BASELINE_UNKNOWN`; giả thuyết không phải quyết định A0; công cụ mock không phải quyền live.
- **TEST_DELTA:** kiểm đủ 8 use case, phép tính trọng số, KPI numerator/denominator, gate/tier, giả lập yêu cầu social write + data join không được vào MVP; không chạy lại GROW fixture.
- **STOP:** bất kỳ thao tác live/chi phí/PII/credential nào; ghi UNKNOWN và giữ phần draft còn lại.
- **PASS:** `BIZ02_S1_PRIORITIZATION_DRAFT_READY_FOR_REVIEW`; **không** có nghĩa ROI đã đo, business approved hay connector activated.
- **HANDOFF:** [báo cáo](../reports/2026-11-23-hermes-biz02-s1-prioritization.md), [evidence](../reports/evidence/2026-11-23-hermes-biz02-s1-priority-matrix.json) → ChatGPT Điều phối; A0 quyết định sau review.
