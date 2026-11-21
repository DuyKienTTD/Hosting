---
id: hermes-gate-b-h4-key-input-preparation-2026-11-21
type: report
status: current
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
source: KVM2-sandbox-terminal-and-commit-f335752
---

# GATE B H4 — chuẩn bị giao diện nhập API Key an toàn

## Tóm tắt

**H4 SANDBOX TEST: PASS / READY_FOR_OWNER_KEY_INPUT.** Giao diện terminal
không echo đã sẵn sàng trong sandbox xác thực. Nó chỉ validate Compose ở chế độ
đọc và lưu credential vào file root-only; không tự mount secret, không chạy
`docker compose up/down`, không mở listener/port và không gọi OpenAI. GATE B
vẫn `BLOCKED_PREFLIGHT`.

## Phạm vi

- Review toàn bộ mã H4 tại `9596bf10cf7774f1954c7a4992359f17122d6acd`.
- Sửa ranh giới an toàn, chạy unit/fake-key test trên Windows và Linux KVM2.
- Validate Compose read-only, mount/network boundary và trạng thái live sau test.
- Không dùng key thật, không paid inference, không restart/recreate production,
  không đổi firewall/DNS/public port, ledger, kill switch hoặc paid permit.

## Evidence reuse / test delta

- Tái sử dụng H3 combined mock/no-bypass/ledger evidence vì H4 không đổi
  guard/bridge/request route hoặc topology đang chạy.
- `change_trigger`: mã H4 ban đầu có đường gọi `compose up --force-recreate`,
  trái với phê duyệt sandbox-test mới. Đường mutation chưa được chạy và đã bị
  loại bỏ tại `f335752d40c7ce88efede5bf7d743246b2423f5f` trước live test.
- Test delta chỉ gồm giao diện no-echo, fake secret lifecycle, static leak/error
  cases, Compose config/mount/network và live read-only invariants.

## Bằng chứng

- Rule ACK: đọc đầy đủ quy tắc/hồ sơ/task tại commit
  `9596bf10cf7774f1954c7a4992359f17122d6acd`.
- Local: Python compile PASS; 11 unit tests PASS, 1 symlink case skipped do
  Windows không cho tạo symlink trong phiên; repository validator PASS.
- Linux sandbox: Python compile PASS; 11/11 unit tests PASS, gồm symlink,
  invalid/cancel/expiry, rotate/revoke, no listener và no Compose mutation.
- Compose: `config --quiet` exit 0. Rendered overlay có đúng một target
  `guard/read_only=true`, `guard` không publish port, giữ ba network đã có.
- Terminal smoke: fake key nhập hai lần không echo; file tạm mode `0600`, UID
  root, chưa mount; revoke PASS. Final secret status `ABSENT`, target mount vắng
  trên mọi container. Không lưu key hoặc digest key vào evidence.
- Live sandbox: base Compose SHA-256 trước/sau cùng
  `c3a5234f556abaf531849fdd377c87815e6c39c8aed7afe55c364da9e324abb2f`;
  private guard network `internal=true`, chỉ guard và egress proxy là members.
- Production: n8n và Hermes đều `running=true`, restart count 0 sau H4. Không
  service/container nào được recreate bởi H4.
- Ledger hiện vẫn 1 attempt, 0 permit, kill switch ON; H4 không mở/ghi ledger.
  Paid inference/API request mới: 0; chi phí mới: USD 0.

Machine-readable evidence:
[2026-11-21-ttd-hermes-gate-b-h4.json](evidence/2026-11-21-ttd-hermes-gate-b-h4.json).

## Phát hiện

Phương án localhost/SSH tunnel chưa được dùng vì direct SSH chưa được xác minh
trong phiên. Fallback được task cho phép là Hostinger Web Terminal đã xác thực +
`getpass`, không có listener. Mã cuối chỉ staging secret; mount vào guard sẽ cần
phê duyệt riêng cho guard recreate.

## Rủi ro

- Project identity trong giao diện là nhãn để chủ dự án đối chiếu dashboard;
  chưa chứng minh project/key scope, billing/quota hoặc Responses permission.
- Credential thật sau khi nhập vẫn **chưa mount**; token count và budget
  reservation chưa được thực hiện.
- Python không thể bảo đảm xóa mọi bản sao immutable string trong process
  memory, nhưng không echo/log/CLI-arg/env và process kết thúc ngay sau thao tác.

## Khuyến nghị

Chủ dự án chỉ nhập key qua prompt ẩn trong Web Terminal; không gửi qua chat.
Sau đó dừng và bàn giao lại. Codex chỉ mount guard hoặc làm provider preflight
khi có phê duyệt riêng; không gọi `POST /v1/responses`.

## Việc đã thực hiện

- Thêm interface, fake-key tests, secret-ignore path và guard-only overlay ở
  commit `9596bf1`.
- Loại bỏ mọi container mutation khỏi interface ở commit `f335752`.
- Deploy đúng checksum của `f335752` vào sandbox, test, revoke fake key và để
  terminal ở prompt; không để lại listener/process nhập key.

## Toàn vẹn dữ liệu và handoff

`read_complete: true`; `base_commit: 9596bf10cf7774f1954c7a4992359f17122d6acd`;
`write_set: sandbox H4 code + H4 task result + report/evidence + STATE/CATALOG/CHANGELOG`;
`invariants_checked: task owner/status/approval, production, base Compose, live ledger/kill switch, no public port`;
`remote_readback: pending final documentation commit`;
`next_owner: chatgpt`; `handoff_state: PREPARED_FOR_OWNER_FORWARD`.

## Việc còn lại

1. ChatGPT nghiệm thu report/evidence và giữ GATE B `BLOCKED_PREFLIGHT`.
2. Chủ dự án tự nhập key thật qua giao diện, không gửi key cho agent.
3. Xin phê duyệt riêng trước guard recreate/mount; sau đó mới kiểm tra
   guard-only scope, project/Responses/billing/quota và input-token count.
