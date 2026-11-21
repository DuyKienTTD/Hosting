---
id: ttd-hermes-aux-guard-bridge-approval-proposal-2026-11-21
type: decision
status: partially_approved
approved_scope: gate-a-mock-only
approved_at: 2026-11-21
updated_at: 2026-11-21
sensitivity: public
decision_owner: business-owner
related_task: ttd-hermes-e2e-hard-cap-001
---

# ADR-P0-002 — Đề xuất phê duyệt triển khai Hermes phụ, guard và bridge (KHÔNG PAID CALL)

**TRẠNG THÁI: GATE A ĐÃ ĐƯỢC CHỦ DỰ ÁN PHÊ DUYỆT (2026-11-21).** Cho phép Codex triển khai Hermes phụ, inference guard, authenticated bridge/callback và hai service secrets trên sandbox KVM2; **chỉ provider mock, giữ kill switch ON, 0 paid calls, không thay production**. **GATE B chưa được phê duyệt.** Xem [nhiệm vụ thực thi Bước A](../tasks/2026-11-21-hermes-auxiliary-guard-bridge-gate-a.md).

**KẾT QUẢ GATE A: `GATE_A_MOCK_PASS` (2026-11-21).** Mock E2E, hard cap/input bound, no-tools/no-bypass, authentication, corrected rollback và production health đều PASS; paid calls mới 0, kill switch/ledger không đổi. Xem [báo cáo nghiệm thu](../reports/2026-11-21-hermes-gate-a-mock-results.md). Kết quả không tự phê duyệt GATE B.

## Cơ sở bằng chứng

- [Feasibility report](../reports/2026-11-21-hermes-agent-e2e-hard-cap-feasibility.md) / [Evidence](../reports/evidence/2026-11-21-ttd-hermes-e2e-hard-cap-001.json), commit `6d9b71cb2e797c386917e7d3d32ecc47458329a7`.
- Hermes CLI/config stock không có hard output cap trước request; programmatic transport có thể serialize exact model `gpt-6-luna`, `max_output_tokens=600` và tools vắng mặt khi thử offline.
- Offline guard contract/rehearsal 100/100 PASS; mô phỏng concurrent requests từ **bản sao ledger** có 1 attempt: nhận 4, từ chối 6. Đây **không phải** evidence của live full Hermes request hoặc Hermes E2E.
- Production n8n/Hermes chưa đổi; kill switch vẫn bật. Provider E2E đã PASS 1 paid call USD 0.0000496 theo usage (chưa đối soát hóa đơn). Hermes E2E vẫn `BLOCKED_COST_CONTROL`.

## Phạm vi được phê duyệt — GATE A

Chủ dự án đã phê duyệt rõ ràng phạm vi bên dưới ngày 2026-11-21:

1. Trên **KVM2 sandbox hiện có**, chuẩn bị và chạy **một Hermes auxiliary runtime nguyên bản** pin image digest/commit đã xác minh, state riêng, không mount production state/credentials/data/memory/skills.
2. Một **private inference guard** là đường duy nhất đến OpenAI Responses API; không có đường provider egress trực tiếp cho Hermes hoặc bridge. Guard phải enforce trước dispatch: `gpt-6-luna`, `max_output_tokens=600` (không >2.000), input ≤4.000 billable tokens, không tools/tool choice, ≤1 turn, không auxiliary/recursive calls, không fallback model, không auto retry có thể bypass.
3. Một **authenticated bridge/callback** nối n8n sandbox ↔ Hermes auxiliary `/v1/runs` ↔ n8n callback đúng workflow hiện có, có task/correlation IDs, idempotency và JSON validation.
4. Tạo `API_SERVER_KEY` và guard service token riêng dùng CSPRNG, secret dir `700`, files `600`, không đưa lên GitHub/chat/log. Provider key chỉ ở guard, không ở Hermes auxiliary.
5. Guard dùng **đúng persistent atomic ledger P0 đang có** (đã 1 paid attempt) và giữ nguyên kill switch `ON`. Không reset hoặc tạo ledger ngân sách độc lập.
6. Phải preflight memory/CPU, backup/rollback, image pin và chứng minh không ảnh hưởng n8n/Hermes production hoặc U4S `ttdnew.tech`; không mở public inbound port, firewall, DNS, không restart/recreate service chính.
7. **Chỉ mock provider capture** (không request paid): kiểm chứng full serialized Hermes input ≤4.000 tokens, request đúng một, cap pre-dispatch, no tools, no-bypass network, auth/callback, retry/error/schema/idempotency, negative tests, stress và rollback/restore. Nếu bất kỳ gate nào fail, STOP/rollback rồi báo cáo.

## Ngoài phạm vi — GATE B chưa được duyệt

- **KHÔNG** tắt/chuyển trạng thái kill switch cho paid traffic, dù chỉ trong chốc lát.
- **KHÔNG** gọi thêm một paid Hermes inference call hoặc thay model/provider, nới trần chi phí.
- **KHÔNG** thay cấu hình/mạng/credentials của n8n/Hermes production; không thay U4S, không public port/firewall/DNS, không business connector.
- Paid Hermes pilot chỉ được xét **trong phê duyệt khác** sau khi toàn bộ mock capture PASS và cost control thực sự được chứng minh; dự kiến đúng **1 paid Hermes call** trong phần allowance còn lại, trần request 4K input/2K output và tổng P0 0,05 USD. Ledger chính không được reset; provider billing chưa đối soát nên giữ reserve bảo thủ.
- Nếu thay đổi cần restart production, mở public route, phát sinh phí dịch vụ mới, hoặc vượt CPU/RAM có thể ảnh hưởng production: STOP, xin phê duyệt riêng.

## Vai trò

**Codex:** owner triển khai kỹ thuật GATE A đã được duyệt. **Hermes:** hỗ trợ kiểm chứng agent, tool/profile/schema. **Hostinger Agent:** kiểm tra backup/runtime boundary/health. **ChatGPT:** đối chiếu evidence và nghiệm thu báo cáo theo yêu cầu. **Chủ dự án:** đã duyệt GATE A; sau mock PASS mới quyết định GATE B.

## Acceptance GATE A

- Hermes auxiliary verified real Hermes Agent; private inference guard/bridge deployed và healthy.
- Full request capture qua provider mock PASS exact model/output/input bounds, tools off, 1 turn/1 request, no direct egress/bypass, shared ledger and kill switch ON.
- Mock E2E `n8n → Hermes auxiliary → guard provider mock → n8n authenticated callback` PASS. Không gộp mock E2E với paid Hermes E2E.
- Rollback/restore và production health PASS; paid calls thêm = 0, chi phí thêm = 0; evidence redacted, report+commit GitHub.

**Chỉ sau đó** lập phiếu xin phê duyệt GATE B cho một paid Hermes call. Không đánh dấu P0 complete khi chỉ GATE A PASS. Phê duyệt GATE A không phải bằng chứng tác vụ đã được thực thi.
