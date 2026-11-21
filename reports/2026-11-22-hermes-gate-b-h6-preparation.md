---
id: hermes-gate-b-h6-preparation-2026-11-22
type: report
status: current
updated_at: 2026-11-22
verified_at: 2026-11-22
sensitivity: public-redacted
task_id: ttd-hermes-gate-b-001
owner: codex
---

# GATE B H6 — Chuẩn bị tuyến provider sandbox

**H6_PREPARATION_COMPLETE / NEEDS_OWNER_DECISION.** Codex nhận `H6_SANDBOX_PROVIDER_ROUTE` qua chủ dự án. ACK quy tắc và task tại `15637451a758ce8f7208bfae52699157ddd6d9f5`, mục bàn giao H6 tại `d8fdd23`. Phiên này truy cập được GitHub và Web Terminal KVM2 đã xác thực. Phạm vi thực tế gồm đối chiếu mã, đo trạng thái KVM2 chỉ đọc và thiết kế delta. H5 đã được nghiệm thu. Gate B paid vẫn `BLOCKED_PREFLIGHT`. [Task](../tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md) · [ADR-P0-003](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md) · [Evidence](evidence/2026-11-22-ttd-hermes-gate-b-h6-preparation.json).

## Đối chiếu hiện trạng

| Điều kiện | Kết quả |
| --- | --- |
| Guard và production | Guard live SHA-256 `15c51be630350077ee30b6cbeaa327d8d4d7a26792934b9244e1346129faa939`, khớp `1953a81`. Guard/proxy healthy, membership và Compose khớp baseline. Credential mode `0600`, mount chỉ đọc duy nhất ở Guard. Hai production services HTTP 200, restart count 0. Dùng lại bằng chứng 18/18 no-bypass H4 vì topology không đổi. |
| Backup và rollback hiện hành | Compose base và H4 overlay khớp từng byte với backup lưu riêng trên KVM2. Dry-run rollback chỉ Guard đã kiểm ở H4. Rollback của delta H6 vẫn cần riêng vì có ranh giới writer mới. [H4 Guard mount](2026-11-22-hermes-gate-b-guard-mount-results.md). |
| Ledger | Bản đọc từ Guard khớp byte với baseline. Bản trên host có 1 attempt lịch sử, 0 permit, kill switch ON. Guard mount ledger theo **file** chỉ đọc. Container `reasoner` Level 2 đang dừng và là container có mount ghi bao phủ file này trong phép đối chiếu mounts. Phép dò ban đầu chỉ tìm mount theo thư mục, sau đó kiểm tra cả target file và tìm được mount thực tế. |
| Khoảng cách mã | Guard trong Git tại `69dd952` có canonical freeze và atomic admission khi bật nhánh mock, nhưng dispatch vẫn trỏ `MOCK_URL` và dùng `settle_mock`. `one_shot.py` dùng lock cạnh file, ghi file tạm, fsync, rename và fsync thư mục. Đổi bind mount hiện tại sang ghi vẫn không đáp ứng hợp đồng này. File bind cũng có thể tiếp tục trỏ inode cũ sau khi writer rename. |
| Request H5 | Bản ứng viên riêng trên VPS còn nguyên 3.304 bytes và mode `0600`, SHA-256 `e66603e05a4a9b0d7a4bbd7b9142a89e15e38176c2fe1fddbf3dd5764ff1a929`. Tái sử dụng 723 input tokens, cap 600 output, reserve 0,0035 USD và exact-byte mock của H5. H6 cần kiểm lại cùng task/idempotency và bytes trên đường tích hợp. [H5](2026-11-22-hermes-gate-b-h5-preflight-followup.md). |

## Thay đổi đề xuất để nghiệm thu

1. **Tách quyền ghi ledger khỏi Guard.** Dùng writer nhỏ trong sandbox với mount ghi khoanh vào thư mục ledger hiện có, không có mạng hoặc provider key. Guard chỉ có IPC qua Unix socket riêng và giao diện admission/settlement giới hạn thao tác. Không expose socket cho Hermes, bridge, mock hoặc production. Writer mở ledger hiện hành theo đường dẫn dưới cùng lock với Level 2, giữ nguyên schema và cap. Guard lấy trạng thái ledger từ writer hoặc một đường đọc quan sát cùng file sau rename. Xác minh điều kiện Level 2 tiếp tục dừng và thử tương thích lock trên bản sao trước khi cho writer tiếp cận ledger thật.
2. **Chốt đúng bytes và một lượt gửi.** Guard xác thực request nội bộ, khóa task/idempotency/model/digest, xử lý trường động theo quy tắc đã chứng minh ở H5 và ràng buộc số đếm với bytes sau enforcement. Transport chuẩn bị ở chế độ mặc định tắt, chỉ có đích OpenAI Responses cố định qua proxy allowlist với TLS xác minh. Dùng đúng buffer đã kiểm digest, reserve và consume permit bền vững trước khi gửi, không redirect, retry, fallback hoặc mở kill switch. Tách mock usage khỏi hạch toán provider. Khi kết quả không rõ, timeout hoặc crash, giữ reservation và permit đã consume, đối soát trước mọi thay đổi tiếp.
3. **Kiểm thử delta trước khi áp dụng.** Trên ledger giả, chứng minh inode thay mới đọc được, lock liên thông, credential/proxy và TCP không tới được từ writer, socket chỉ ở Guard, đúng bytes đến mock một lần, tamper/replay/race không phát sinh lượt hai, restart/crash/response cắt giữ reserve và callback authenticated. Tái sử dụng kết quả H3/H4/H5 tương đương. Sau khi có bản vá, đo diff Compose để giới hạn đúng Guard sandbox và writer, xác minh rollback dry-run rồi mới trình phiên bản áp dụng. Nếu input-affecting bytes đổi, khóa lại digest và dùng phép đếm miễn phí đã được phê duyệt trước khi đề nghị paid readiness.
4. **Rollback tối thiểu.** Vô hiệu hóa tuyến mới, khôi phục compose/code Guard đã backup và chỉ recreate service bị ảnh hưởng theo cấu hình được duyệt. Nếu có writer mới, dừng nó sau khi đối soát pending state. Giữ lịch sử ledger, permit đã consume và reserve qua rollback, kể cả khi kết quả không xác định. Không dùng bản backup để ghi đè ledger. Kiểm health, mount, mạng, không bypass và production HTTP/restart sau rollback.

## Bàn giao

**Việc cần quyết định:** ChatGPT review ranh giới Guard/writer, thứ tự ghi durable và kế hoạch kiểm thử. Sau review, chủ dự án phê duyệt riêng bản vá/phạm vi apply chỉ sandbox Guard và writer, bao gồm quyền ghi có giới hạn, nếu chấp thuận phương án. Chỉ xin quyết định paid riêng sau khi nghiệm thu runtime và các gate.

Run này có **0 provider calls, 0 paid attempts, 0 permit live được tạo và 0 USD chi phí mới**. H6 chưa có bản vá hoặc kết quả mock cho writer/transport mới. H3/H5 là bằng chứng mock được tái sử dụng. Docker Desktop local chưa chạy trong phép kiểm khả năng test container. KVM2 vẫn truy cập được qua Web Terminal, và các phép kiểm chỉ đọc đã hoàn tất.

`from_agent: codex`, `to_agent: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`.
