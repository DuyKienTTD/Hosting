---
id: sec02-s2-controlled-hardening-gates
type: runbook
status: proposed-not-authorized
updated_at: 2026-11-23
sensitivity: public-redacted
---
# SEC-02/S2 — Cổng thay đổi hardening có kiểm soát (chỉ thiết kế)

**Không phải script triển khai.** Không có lệnh shell, API write, credential, URL nội bộ hoặc thao tác restore. Work order chưa có `change_id`, tất cả `NOT_AUTHORIZED`. Đặc tả [PR #11 comment 7091865470](https://github.com/DuyKienTTD/Hosting/pull/11#issuecomment-7091865470); findings nguyên bản SEC-02/S1 ở PR #11 HEAD `142f6dc5dbc033554bd0b43e3444ea0d59f60d96`.

## Cổng thời gian — từng change ID riêng

`IDENTITY_VERIFIED → BACKUP_RECOVERY_PLAN → ALTERNATE_ADMIN_ACCESS_CONFIRMED → CHANGE_APPROVAL → SINGLE_CONTROL_CHANGE → HEALTH_CHECK → ROLLBACK_DECISION`.

1. **Identity:** người sở hữu tài nguyên xác minh KVM2 khác ứng dụng Hermes managed, endpoint/backup thuộc đúng owner; ghi alias redacted, thời điểm và source. Sai hoặc mơ hồ → STOP.
2. **Recovery:** chủ backup xác minh backup mới, phân loại dữ liệu, mục tiêu cô lập, RPO/RTO do A0 quyết định; backup tồn tại **không bằng** restore PASS. Nếu order đòi restore proof mà chưa có → STOP.
3. **Alternative access:** trước bất kỳ firewall/RDP/SSH/TLS nào, hai người độc lập xác nhận console/out-of-band và đường SSH admin hợp lệ (không công khai IP), thử từ đường thay thế đã phê duyệt; lưu snapshot rule/config đã khử nhạy cảm và inverse plan. Chưa chứng minh → STOP, không đóng đường cũ.
4. **Approval:** một `change_id` chỉ cho **một control** trên một resource/window; A0 + service/credential/endpoint owner + reviewer độc lập phê duyệt có phạm vi, giới hạn thời gian và điểm dừng. Chữ ký PR/tài liệu không thay approval production. Không sử dụng một phê duyệt cho nhiều thay đổi.
5. **Single-control change (tương lai, KHÔNG trong S2):** nhân sự được cấp quyền mới triển khai một thay đổi trong window; inverse đã diễn tập và dependency đã kiểm; không tự gộp đóng port, đổi TLS và rotate credential. Không chạy bất kỳ lệnh nào theo tài liệu này.
6. **Health:** xác minh theo từng chức năng và nguồn độc lập: quyền admin/SSH, n8n readiness + job, Hermes dashboard **và inference-specific receipt** (HTTP 200 dashboard không chứng minh inference), TLS chain/SNI/backend, đường kết nối hợp lệ và chặn nguồn không hợp lệ khi được cho phép. Nếu n8n outage, TLS break, secret leak hoặc mất đường admin → STOP và chuyển owner đến quyết định rollback, không retry mù.
7. **Rollback decision:** reviewer/owner đối chiếu pre/post và chỉ đảo đúng control của `change_id` trên đúng resource nếu đã được duyệt. Resource owner/ID mơ hồ → STOP; giữ nguyên evidence và escalation. Đóng change khi chứng minh đủ access, health và audit; nếu không giữ trạng thái BLOCKED.

## Năm work order độc lập (đề xuất, không được thực thi)

| Work order | Finding | Owner và preflight | Khôi phục và điểm dừng |
|---|---|---|---|
| WO-ACCESS | F01/F02/F07 | Platform + service owners: kiểm mục đích RDP/8501/Docker published ports, authorized source, source allowlist, console/SSH fallback, dịch vụ tiêu thụ; A0 + reviewer phê duyệt **riêng firewall và port mapping** | Một control mỗi window; chụp intent trước, thử đường admin thay thế **trước** khi đóng đường cũ; mất SSH/RDP/n8n ⇒ dừng, inverse đúng change ID theo quyết định owner. Không dùng dự đoán reachability Internet. |
| WO-CREDENTIAL | F06/F07 | Credential owner kiểm kê consumer bằng metadata **không đọc giá trị**, phân loại exposure/compromise trong kênh riêng; A0/reviewer ký kế hoạch tạo replacement và cutover từng consumer | Test auth mới, chỉ sau đó revoke cũ khi owner cho phép; không ghi old secret trong rollback, không tái dùng credential cũ mù; thấy giá trị bất ngờ ⇒ STOP/redact/escalate, không đưa lên Git. |
| WO-RESTORE | F05/F07 | Recovery + data owners chốt runtime, backup, isolated target, data classification, RPO/RTO/cost và window; approval restore tách biệt | Không restore vào production; snapshot target cô lập và manifest trước; sai target/backup ⇒ STOP. Chỉ hủy fixture theo thủ tục/approval riêng. Backup metadata ≠ restore proof. |
| WO-P0 | F03/F07 | Codex/runtime owner chỉ đọc metadata exit/OOM/limit/start/health qua allow-list được cấp; preserve state; 137 và `OOMKilled=false` không đủ kết luận nguyên nhân | Không restart/recreate từ báo cáo này. Nếu cần sửa, mở change ID/runtime approval và baseline/rollback riêng. Command bị chặn ⇒ STOP, không bypass allow-list. |
| WO-TLS | F04/F02/F07 | Endpoint owner xác minh DNS/SNI/terminator/cert metadata, đường về backend và consumer; A0 + reviewer riêng | Giữ route/config cũ, độc lập kiểm TLS chain/SNI và backend; TLS break ⇒ STOP/rollback decision. Không áp TLS vào nhầm runtime. |

## Mẫu approval checklist cho mỗi work order (chưa điền, KHÔNG cấp quyền)

- `change_id=UNASSIGNED`; exact resource owner/alias/source/backup ID=`UNKNOWN`; action và inverse cụ thể có mã review=`PROPOSED_NOT_TESTED`; scope một control; window=`NOT_SCHEDULED`.
- Backup phù hợp và kết quả isolated restore=`UNKNOWN`; alternative admin path independently confirmed=`NO`; rollback tested=`UNKNOWN`; postflight probes được owner duyệt=`NO`.
- A0 quyết định impact, downtime/cost, owner ký riêng, independent reviewer ký riêng; `authorization=NOT_AUTHORIZED` cho **toàn bộ** WO-ACCESS/WO-CREDENTIAL/WO-RESTORE/WO-P0/WO-TLS.
- Evidence path của change tương lai: report redacted riêng, không upload log/secret; STOP nếu lộ giá trị hoặc công cụ allow-list chặn.

**Bàn giao:** ChatGPT Điều phối xem xét ma trận và Hostinger Agent thực thụ rà lại feasibility; A0 mới có thể quyết định từng change. Không tự merge hoặc áp dụng trên VPS.
