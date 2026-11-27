---
id: hermes-gate-b-guard-mount-paused-checkpoint-2026-11-21
type: report
status: current
updated_at: 2026-11-21
sensitivity: public-redacted
source: owner-provided-Codex-status-and-existing-GitHub-evidence
task_id: ttd-hermes-gate-b-001
---

# TTD METAL — Checkpoint GATE B: tạm dừng trước Guard-only mount

## Trạng thái tại điểm dừng (2026-11-21)

**GUARD_MOUNT_NOT_EXECUTED / PAUSED_BEFORE_RECREATE.** GATE B paid inference tiếp tục **`BLOCKED_PREFLIGHT`**. Chủ dự án đã chấp thuận riêng một lần recreate **chỉ sandbox `guard`** để mount secret read-only, nhưng Codex **chưa thực hiện** vì chưa hoàn tất đọc bộ quy tắc hiện hành và chưa xác minh live Compose, backup, rollback trên VPS. Đây là **trạng thái do Codex báo qua chủ dự án**, chưa phải kết quả xác minh live độc lập của ChatGPT. Không có runtime mutation cần rollback; chưa có báo cáo nghiệm thu mount.

## Những việc đã hoàn tất, không làm lại nếu điều kiện không đổi

| Mốc | Bằng chứng | Kết quả / phạm vi |
| --- | --- | --- |
| H1 Hostinger | [Report H1](2026-11-21-gate-b-hostinger-consult.md) | Khảo sát read-only VPS/mount/topology; không cấp paid provider key |
| H2 Hermes | [Report H2](2026-11-21-gate-b-hermes-consult.md) | Phân biệt persisted failed replay với live mismatch chưa chứng minh; bind permit vào final guard-forwarded bytes |
| H3 Codex | [H3 report](2026-11-21-hermes-gate-b-h3-preflight.md) / [evidence](evidence/2026-11-21-ttd-hermes-gate-b-h3.json) | Combined mock E2E + callback, one-shot accounting, 1 mock dispatch, negative tests, rollback/no-bypass, production health PASS |
| H4 fake-key | [H4 report](2026-11-21-hermes-gate-b-h4-key-input-preparation.md) / [evidence](evidence/2026-11-21-ttd-hermes-gate-b-h4.json) | 11/11 Linux tests PASS; bỏ đường recreate ngoài quyền trước khi chạy; secret staging interface chỉ đọc Compose |
| H4 owner nhập key | [H4 live metadata report](2026-11-21-hermes-gate-b-h4-owner-key-live-check.md) / [evidence](evidence/2026-11-21-ttd-hermes-gate-b-h4-owner-key-live-check.json) | `PRESENT`, `0600`, `mounted=false`; không đọc/băm/đo kích thước hay tiết lộ key |
| Phê duyệt mount | [Task GATE B, mục phê duyệt cuối](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) | Chủ dự án phê duyệt **chỉ sandbox guard** mount read-only, backup/rollback/targeted checks; không provider request |

Không có cơ sở khẳng định các kết quả H3/H4 mất hiệu lực vì Codex dừng đúng điểm an toàn. Không chạy lại toàn bộ suite nếu chưa có code/config/topology change trigger.

## Điểm dừng của Codex mới nhất

- **Đã làm theo lời báo:** đối chiếu phê duyệt trên `origin/main` tại `0e564e0`; đọc overlay H4 từ repository; overlay khai báo một bind mount read-only riêng cho `guard`.
- **Chưa làm:** đọc xong toàn bộ rule mới nhất; xác minh live Compose/topology, backup và đường rollback trên KVM2; recreate sandbox `guard`; kiểm mount thật; báo cáo nghiệm thu mount.
- **Không làm theo lời báo:** không Compose mutation, provider call, paid inference, production change; chưa có gì để rollback. **Không coi lời báo này là một lần kiểm chứng production mới.**

## Mục bất biến và giới hạn quyền đã được phê duyệt

- **Owner task mẹ:** `codex`; **status:** `blocked`; **approval:** `paid_inference_approval: true` nhưng chỉ một lượt theo ADR-P0-003 **sau khi mọi preflight PASS**; phê duyệt mount **không phải phê duyệt paid dispatch**.
- Không chạm production n8n/Hermes, mạng/DNS/firewall/public port, ledger thật/permit, kill switch, container ngoài sandbox guard; không đọc/hiển thị/đo bí mật.
- Không gọi **bất kỳ provider endpoint nào trong bước mount**, kể cả token count. Chưa xác minh project, billing, Responses permission hoặc số input tokens theo final digest.
- Ledger **theo evidence gần nhất trước checkpoint:** 1 historical paid attempt, 0 real permits, kill switch ON; H3/H4 ghi 0 paid attempts mới. **Chưa có readback live riêng tại điểm dừng này**.

## Tiếp tục đúng chỗ — không lặp lại công việc

1. **Codex nhận lại cùng task gốc**, đọc trọn `README.md`, `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/codex.md`, task này và ADR-P0-003; ACK rule commit hiện tại. Nếu đọc bị cắt, lấy phần thiếu; không phỏng đoán. Không tạo task mới.
2. **Chỉ đọc trước thay đổi:** so sánh Compose base/overlay H4 với live service/config, xác minh đúng guard và secret staging metadata, current topology, trạng thái backup và đường rollback. Không đọc, hash hay đo kích thước secret. Ghi base SHA và expected diff. Nếu có bất định về guard-only, STOP.
3. Khi mọi precondition PASS, dựa trên **phê duyệt owner đã lưu** trong task, recreate **riêng sandbox guard với `--no-deps`** và overlay read-only theo lệnh được đối chiếu từ Compose hiện tại; không dùng compose down hay recreate các container khác.
4. Targeted checks **sau thay đổi**: guard-only read-only mount metadata, guard/proxy health, sáu no-bypass negative routes qua DNS/IPv4, no public port/network delta, Compose gốc byte-identical, production health/restart unchanged, real ledger/permit/kill switch unchanged, không có provider calls. FAIL → rollback riêng guard về base đã backup và kiểm tra lại targeted invariants.
5. Push **báo cáo/evidence mới** trong `reports/`, bổ sung kết quả vào **task mẹ** (không sửa owner/status/approval), cập nhật STATE/CATALOG/CHANGELOG đúng nhu cầu, đọc lại remote để xác minh; handoff ChatGPT `GUARD_MOUNT_PASS` hoặc `BLOCKED/ROLLED_BACK`.

**Sau mount PASS mới cân nhắc bước provider preflight riêng** (key/project/Responses/billing/input-token count/digest, ngân sách). Chưa cho phép mở paid inference trong bước mount. Chưa có đề xuất reboot VPS trong nhiệm vụ này.

## Handoff hiện tại

- `task_id: ttd-hermes-gate-b-001`
- `from_agent: business-owner / chatgpt checkpoint`
- `to_agent: codex`
- `handoff_state: PREPARED_FOR_OWNER_FORWARD` (người dùng chuyển link; chưa có ACK tiếp tục)
- `first_action: complete full rule read + live Compose/backup/rollback preflight`
- `next_owner_after_report: chatgpt`
- `stop_condition: any unverified runtime boundary, secret exposure, production effect, provider dispatch or need to widen approved scope`

**Checkpoint chỉ ghi bằng chứng và trạng thái đã biết; không thực thi hạ tầng.**
