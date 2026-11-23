---
id: b2p-d1-work-qa-remediation-2026-11-23
type: report
status: current
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# B2-P-D1 — Q1 workflow provenance và Q2 timer

| TASK | AGENT | BASE/HEAD_SHA | EXECUTE_ACK | EXPECTED/OBSERVED | MUTATION_TESTS | EVIDENCE | VERDICT | LIMITS/BLOCKERS | PR/COMMIT | NEXT_OWNER |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2-P-D1 | Codex | `54b4e18` → commit D1 | 23/11/2026 ICT, chỉ thị `7090919796` | Timer Guard duy nhất theo task và import candidate có pin riêng | 5/5 phương thức test delta | [JSON](evidence/2026-11-23-b2p-d1-work-qa-remediation.json) | `B2P_D1_SOURCE_DELTA_PASS` | KVM2 `BLOCKED_PREFLIGHT_INPUT / NOT_MEASURED`, Work review delta còn chờ | [PR #7](https://github.com/DuyKienTTD/Hosting/pull/7) | ChatGPT Điều phối |

ACK quy tắc tại `e385c1bea2070973e3007e5717f7e980348d6ab3`, Workflow blob `69ec0db902f457f06dd547dae171220331df0f5e`. Đã fetch main và heads PR #5/#7/#10/#13, kiểm review mới và đối chiếu Work QA. Nhánh PR #7 tiếp tục xếp trên PR #5 `d95f161`. ACK D1 gắn với lượt thực thi do chủ dự án gửi, tách khỏi SHA của tài liệu. [Chỉ thị](https://github.com/DuyKienTTD/Hosting/pull/7#issuecomment-7090919796) · [Work QA](https://github.com/DuyKienTTD/Hosting/pull/7#issuecomment-7090722358).

## Q2 — đếm timer rồi kiểm role

Trong task `b2o-46`, đếm tất cả `guard_response_timer_fired`, yêu cầu đúng một event và event đó mang role Guard với timestamp nguyên. Trace gốc vẫn giữ thứ tự dispatch → timer → read-end → provider response attempt. Timer ở **45,000576181 s** sau connect, read-end sau timer **0,427156 ms**. Ca hợp lệ vẫn PASS khi chèn timer thuộc task khác.

Đã tái hiện đúng một lỗi ở code `54b4e18`: trace có timer Guard đúng cộng một timer role bridge cùng task vẫn được nhận. Code D1 từ chối ca đó, cùng ca thiếu/trùng timer, một timer sai role, timestamp sai kiểu và timer sau read-end. Phép đối chiếu dùng trace B2-O đã lưu, không chạy lại fixture.

## Q1 — pin riêng import candidate và byte staging

| Mốc | Evidence |
| --- | --- |
| Baseline B2-O lịch sử và source baseline tính lại | Cùng projection `08aa63bcfaf27f9ced2a5374ce67f4683877f615ed00dafea086f608321dde0d`. Thay timeout source bị từ chối. |
| Candidate `workflows.json` local | Toàn bộ JSON được chuẩn hóa và so với pin template B2-O synthetic `439624f3e3dede91f75ad6f12df4fbd9d3104fab1f9bc41e227846acef0cde3a` trước khi hoàn thiện và render cấu hình B2-P. Chuẩn hóa đúng bốn giá trị phát sinh, gồm webhook UUID và ba bearer giả. Ba bearer phải khớp binding fixture. Thay route admission bị từ chối. |
| Byte staging | `LOCAL_TEMPORARY_STAGED_VERIFIED`. Lấy hash của chính file đã qua projection gate và đọc lại trước/sau render. Copy đúng byte pass. Thêm newline sau copy bị từ chối dù JSON tương đương. Thiếu byte pin cũng bị từ chối. Hai lượt tạo fixture cho cùng projection nhưng khác raw digest do dữ liệu giả phát sinh. JSON evidence lưu cả hai digest. Không giữ bản file tạm. |
| KVM2 và n8n import | Staging KVM2 `NOT_PERFORMED`, n8n import `NOT_RUN`. Với lượt staging được duyệt riêng, xác minh projection trên artifact mới, ghim byte tại nguồn rồi dùng `verify_staged_workflow` đối chiếu ngay sau copy và trước import. |

```powershell
python -X utf8 -B sandbox/p0-hermes-gate-a/h6_b2p_preflight_test.py PreflightTests
python -X utf8 -B sandbox/p0-hermes-gate-a/h6_b2p_preflight.py --evidence "$env:TEMP/ttd-b2p-d1-render.json"
```

Năm test methods chạy thuần Python. Hai lần render all-profile bằng Compose v5.1.4 trên context local đã xác minh cho cùng hash redacted `fa166193…b0`, khớp B2-P trước D1. Evidence kèm SHA source và môi trường CPython 3.12.3 Windows 11 AMD64. Compose chỉ dùng `config`. PR #5, evidence B2-O, báo cáo/evidence B2-P gốc và PR #10/#13 không bị sửa.

**Handoff:** ChatGPT Điều phối tiếp nhận delta, sau đó Work review độc lập trên HEAD D1. `REAL_CONNECTOR_UNTESTED`. KVM2 vẫn `BLOCKED_PREFLIGHT_INPUT / NOT_MEASURED`; không đo headroom/health hoặc chạy fixture KVM2. Zero KVM2/production access, provider calls và USD. Paid Gate B giữ `BLOCKED_PREFLIGHT`.
