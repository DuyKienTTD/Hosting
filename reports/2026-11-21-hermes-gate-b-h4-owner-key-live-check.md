---
id: hermes-gate-b-h4-owner-key-live-check-2026-11-21
type: report
status: current
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
source: KVM2-sandbox-Web-Terminal-metadata-only-readback
---

# GATE B H4 — kiểm tra live sau khi chủ dự án nhập key

## Tóm tắt

**VERIFIED_LIVE_STORED_NOT_MOUNTED / BLOCKED_APPROVAL.** Codex chạy đúng lệnh
status chỉ đọc của giao diện H4 trong terminal sandbox đã xác thực. Kết quả cho
thấy secret staging tồn tại, mode `0600`, chưa mount; vì chưa có mount nên trạng
thái guard-only read-only là false. Không đọc, băm, đo kích thước hay ghi lại giá
trị secret. GATE B vẫn `BLOCKED_PREFLIGHT`.

## Phạm vi

- ACK handoff tiếp theo sau khi chủ dự án báo đã nhập xong.
- Chỉ kiểm tra presence/mode/mount metadata qua `owner_key_input.py status`.
- Không chạy Docker Compose mutation, không đọc provider credential, không gọi
  provider và không thay production, ledger, permit hoặc kill switch.

## Evidence reuse / test delta

- Tái sử dụng [H4 sandbox-test report](2026-11-21-hermes-gate-b-h4-key-input-preparation.md)
  và [evidence](evidence/2026-11-21-ttd-hermes-gate-b-h4.json): 11/11 Linux tests,
  fake-key lifecycle, Compose read-only boundary và live invariants đã PASS.
- Không có thay đổi mã, Compose, topology hoặc request fixture sau H4; do đó
  không rerun H3 combined mock, H4 fake-key suite hay network tests.
- `test_delta`: chỉ xác minh metadata của secret thật sau owner input. Nếu mount
  guard được phê duyệt và áp dụng, đó là `change_trigger` cho targeted mount,
  no-bypass và health checks.

## Bằng chứng

- Rule ACK: đã đọc đầy đủ quy tắc, trạng thái, catalog, hồ sơ Codex, task và H4
  report/evidence tại commit
  `e93cd2939fa672f3312c37a77672e6d30401d702`.
- Lệnh read-only: `./owner_key_input.py status` trong sandbox H4.
- Output đã khử nhạy cảm: `PRESENT`, mode `0600`, `mounted=false`,
  `guard_only_read_only=false`.
- Không ghi owner, kích thước, digest, đường dẫn máy chủ hoặc giá trị secret vào
  evidence. Lệnh status không xác minh project/key scope, Responses permission,
  billing hoặc quota.

Machine-readable evidence:
[2026-11-21-ttd-hermes-gate-b-h4-owner-key-live-check.json](evidence/2026-11-21-ttd-hermes-gate-b-h4-owner-key-live-check.json).

## Phát hiện

Staging hoàn tất đúng ranh giới H4. Credential chưa đi vào container, nên bridge,
Hermes, n8n và guard đều chưa được cấp provider access bởi bước này. Không có cơ
sở chạy token count trước khi mount guard-only được phê duyệt.

## Rủi ro

- Presence và mode không chứng minh credential hợp lệ hoặc thuộc đúng project.
- Recreate/mount guard là thay đổi runtime sandbox riêng, chưa được phê duyệt.
- Provider token count, pricing/tier và budget reservation vẫn chưa xác minh.

## Khuyến nghị

Chủ dự án quyết định riêng việc cho phép recreate **chỉ service `guard` trong
sandbox** với overlay H4. Nếu duyệt, phạm vi phải giữ nguyên no-public-port và
network hiện có; kiểm mount chỉ ở guard/read-only bằng metadata, chạy targeted
no-bypass + health, và rollback về base Compose nếu lỗi. Bước mount không được
gọi provider hoặc tạo paid permit.

## Việc đã thực hiện

- Xác nhận live metadata của secret staging bằng lệnh read-only.
- Không chụp màn hình, sao chép terminal log thô hoặc truy cập nội dung secret.
- Không chạy `docker compose up/down/recreate` và không gọi OpenAI API.

## Toàn vẹn dữ liệu và handoff

`read_complete: true`; `base_commit: e93cd2939fa672f3312c37a77672e6d30401d702`;
`write_set: H4 live-check report/evidence + task result + STATE/CATALOG/CHANGELOG`;
`invariants_checked: task owner/status/approval unchanged, no secret value/digest/size, no runtime mutation`;
`remote_readback: pending documentation push`;
`next_owner: business-owner`; `handoff_state: NEEDS_OWNER_DECISION`.

## Việc còn lại

1. Chủ dự án phê duyệt hoặc từ chối riêng guard-only sandbox recreate/mount.
2. Nếu được duyệt, Codex áp dụng mount tối thiểu và chạy targeted boundary tests.
3. Chỉ sau đó mới làm no-cost provider preflight/token count; không gọi
   `POST /v1/responses` trong các bước này.
