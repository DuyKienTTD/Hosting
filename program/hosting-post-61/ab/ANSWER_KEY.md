---
id: post61-ab-answer-key
type: knowledge
status: draft
owner: Chat Dieu phoi
task_id: HOSTING-POST-61
lifecycle: ACTIVE
retention_trigger: complete the independent A/B and retain agreed regression fixtures
updated_at: 2026-11-25
sensitivity: public
---
# Đáp án đối chiếu · riêng cho người chấm

[Quy trình](PROTOCOL.md) · [Bảng chấm](SCORECARD.md)

- **T1.** Snapshot `d7b2cc9bb2e458e31d334b362bffc40eae329ed2` = OPEN. Index L11 thiếu preflight L57–L59 và H5/H6 dùng #L307-L719. Snapshot `c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb` = CLOSED ở phạm vi F4, có #L57-L59 và #L307-L718. Tệp nguồn đều pin `097c080cc6d7fb3ca36b1849d9c10375d5cbd67f`, kết thúc ở L718. Nguồn [cũ](https://github.com/DuyKienTTD/Hosting/blob/d7b2cc9bb2e458e31d334b362bffc40eae329ed2/rules/GATE-B-INDEX.md#L11), [mới](https://github.com/DuyKienTTD/Hosting/blob/c0720d7d81d6956f2c7bcf7a65cc3a2d218a9bcb/rules/GATE-B-INDEX.md#L11), [preflight](https://github.com/DuyKienTTD/Hosting/blob/097c080cc6d7fb3ca36b1849d9c10375d5cbd67f/tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md#L57-L59), [EOF](https://github.com/DuyKienTTD/Hosting/blob/097c080cc6d7fb3ca36b1849d9c10375d5cbd67f/tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md#L718). Có link lịch sử không suy ra đã merge hay được chạy Gate B.
- **T2.** R1 ACK hợp lệ đúng task/Agent/phiên/event/time/source. R2 là review, không phải ACK thực thi. R3 sai task. R4 thiếu phiên nên UNKNOWN cho xác nhận thực thi. Chỉ R1 được tính, không tuyên bố đã thực thi từ receipt.
- **T3.** Main BLOCKED với hai lỗi 403 giả lập. Chủ dự án/quản trị quyền đọc xác minh và cấp kênh đọc hợp lệ rồi Điều phối kiểm SHA/tree. H5/H6 DONE khi đối chiếu được L719 → L718 theo source thật, có hai link tệp đã pin từ đáp án T1. Nếu thực sự không đọc được blob, báo blocker riêng với lỗi quan sát được thay vì giả DONE.
