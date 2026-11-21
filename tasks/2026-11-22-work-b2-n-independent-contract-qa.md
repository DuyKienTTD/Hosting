---
id: ttd-work-b2-n-independent-contract-qa-001
type: task
status: prepared
approved_at: 2026-11-22
updated_at: 2026-11-22
sensitivity: public-redacted
owner: chatgpt-work
reviewer: chatgpt
depends_on: [ttd-hermes-gate-b-001]
---

# H6 B2-N — Work QA độc lập hợp đồng Hermes và n8n

**Mục tiêu.** Chuẩn bị ma trận nghiệm thu độc lập để phân biệt tính tương đương phiên bản, hành vi quan sát được và phần còn thiếu đối với contract Hermes auxiliary/n8n với fake provider. Codex sở hữu triển khai và phép thử. Work bắt đầu độc lập ngay từ nguồn hiện có, bổ sung đối chiếu bằng chứng Codex khi xuất hiện.

**FIRST_ACTION / READ_SET.** Fetch GitHub `main` mới nhất và ACK SHA đã đọc. Đọc đầy đủ AGENTS.md, Workflow §§7–10, Repository Security, PROJECT, STATE/CATALOG, hồ sơ ChatGPT/Codex, [toàn bộ task Gate B và mục B2-N](2026-11-21-hermes-gate-b-one-shot-paid-e2e.md#chatgpt-nghiệm-thu-b2-m-và-mở-b2-n--2026-11-22), [ADR-P0-003](../decisions/2026-11-21-hermes-gate-b-single-paid-call-proposal.md) và [phân công song song](2026-11-21-hermes-gate-b-one-shot-paid-e2e.md#handoff-song-song-h6-b2-n). Lấy [báo cáo B2-H](../reports/2026-11-22-hermes-gate-b-h6-b2-h-read-only.md) và [JSON](../reports/evidence/2026-11-22-ttd-hermes-gate-b-h6-b2-h-read-only.json) làm mốc cho phiên bản, deadline đã cấu hình và validator đã publish. Đọc [bridge.py](../sandbox/p0-hermes-gate-a/bridge.py), [B2-K fixture](../sandbox/p0-hermes-gate-a/h6_b2k_services.py), báo cáo B2-K/B2-L và [review](../reports/2026-11-22-hermes-gate-b-h6-b2-k-l-chatgpt-review.md), [Codex B2-M](../reports/2026-11-22-hermes-gate-b-h6-b2-m-kvm2-idle-canary.md) và [Work B2-M](../reports/2026-11-22-work-b2-m-independent-canary-qa.md). So với tài liệu hãng [Hermes Runs API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server) và [n8n Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/). Ghi URL, ngày kiểm, contract áp dụng và phần cần xác minh trên build đích.

| Mốc | Bằng chứng tái sử dụng |
| --- | --- |
| B2-H | `DONE_VERIFIED` cho metadata KVM2 ngày 22/11. Bridge poll 20 s, n8n timeout gọi bridge 30 s, callback chỉ chấp nhận mock và Guard có budget 45 s theo thiết kế. Deadline hiệu lực Hermes chưa đo. |
| B2-K/L | `DONE_VERIFIED` cho các mock đã nghiệm thu tại `351afa2` và `c4d5402`. Giữ nguyên kết quả. |
| B2-M | `DONE_VERIFIED` có giới hạn theo Codex và Work: bytes ledger giả và metadata ledger/lock giả trong cửa sổ sau start đầu đến sau 20 health và restart. Byte lock, pre-first-start và power-loss ngoài phần đã chứng minh. |
| B2-N | `NOT_RUN` cho build/workflow mục tiêu đến khi có báo cáo và trace mới. QA nguồn và ma trận bắt đầu ngay. |

**TEST_DELTA / ACCEPTANCE.** Viết bảng theo từng case, gồm nguồn/phiên bản, expected, observed, bằng chứng phải có và STOP. Khi xuất hiện PR Codex, dùng GitHub đọc toàn bộ diff, render, báo cáo và JSON đã khử nhạy cảm. Mỗi dòng ghi `VERIFIED_SOURCE`, `VERIFIED_OFFLINE_MOCK_REPORTED_BY_CODEX`, `UNKNOWN` hoặc `BLOCKED`.

1. **Tương đương bản đích và cô lập.** Đối chiếu image/build digest Hermes và n8n, revision hoặc digest fixture callback và các khác biệt so với B2-H. Kiểm các bước render đủ profile, thiết lập fake-provider, bind/volume/network, đường ra Internet và quyền cleanup theo inventory do Codex cung cấp. Thiếu provenance/fixture thì ghi chính xác điểm thiếu và tác động. Tài liệu upstream chỉ làm nguồn đối chiếu.
2. **Run ID và mất ACK.** Mỗi trace gắn cùng một job/task, idempotency key fingerprint, request digest và run ID. Kiểm bản ghi admission đã tồn tại rồi mới mô phỏng mất ACK, restart và gửi lại cùng binding. Kỳ vọng cùng run ID và recorder không tăng số fake dispatch. Cùng key với body/binding khác phải bị từ chối. Phân biệt lỗi chủ động được hệ thống trả với timeout hoặc mất kết nối.
3. **Deadline và outcome unknown.** Xác định đồng hồ bắt đầu và điểm đo từng tầng. Kiểm ca provider giả hoàn tất sau 30 s nhưng trong budget 45 s và ca chạm giới hạn 45 s khi chưa có kết quả. Tách idle timeout khỏi deadline toàn lượt, và tác động của stream chậm/heartbeat nếu fixture mô phỏng. Evidence cần có timestamps, trạng thái bền vững và số dispatch/settlement giả sau restart/reconcile. Với unknown giữ reserve giả nếu fixture có reserve, tránh dispatch lại.
4. **Callback và receipt.** Kiểm đúng/sai auth, sai job/run/digest, replay cùng event và event mâu thuẫn. Trace phải cho thấy quyết định validator, số receipt/ghi nhận trạng thái trước và sau replay, và số dispatch/settlement. ACK webhook riêng lẻ chưa đủ để chứng minh terminal state.
5. **Kết luận trên commit đã đọc.** Ghi rõ test nào có chứng cứ, giới hạn nào ảnh hưởng nghiệm thu, và phép kiểm nhỏ nhất nếu thực sự thiếu. Có thể xuất bản ngay `SOURCE_QA_COMPLETE / RUNTIME_EVIDENCE_PENDING` trên PR riêng. Khi Codex có evidence, bổ sung trên cùng PR và kết luận `GO_FOR_CHATGPT_REVIEW` hoặc `NO_GO` cho chất lượng bằng chứng B2-N. Ghi commit Codex đã kiểm. Không mở lại B2-K/L/M khi không có change trigger.

**WRITE_SET.** Branch `work/b2-n-contract-qa-2026-11-22` và PR riêng. Chỉ ghi `reports/2026-11-22-work-b2-n-independent-contract-qa.md` và tùy chọn `reports/evidence/2026-11-22-work-b2-n-independent-contract-qa.json`. Không sửa PR/source/test/report Codex, task mẹ, task Work cũ, ADR, rules hoặc STATE/CATALOG/CHANGELOG. ChatGPT tích hợp trạng thái sau review.

**DO_NOT_TOUCH / STOP / INVARIANTS.** Work chỉ dùng GitHub và tài liệu công khai để audit. Không chạy fixture, Docker hay thao tác KVM2. Không đọc dữ liệu/credential/workflow thật chưa khử nhạy cảm, gọi endpoint thật, đụng ledger/lock/permit/key, kill switch, production hoặc chi phí. Khi thấy đường ra provider, real bind, credential thật, thiếu ownership hoặc mất khả năng truy vết một claim, đánh dấu STOP cho phần đó và tiếp tục review độc lập phần còn lại. Live integration `NO_GO`, real writer mount `BLOCKED_UID_OR_MOUNT`, paid `BLOCKED_PREFLIGHT`.

**HANDOFF.** `from_agent: chatgpt` → `to_agent: chatgpt-work`; `handoff_state: PREPARED_FOR_OWNER_FORWARD`. Khi nhận, Work ACK đúng HEAD; khi bàn giao, push branch, mở PR, đối chiếu remote diff/write-set, gửi PR + commit + trạng thái cho `next_owner: chatgpt`. Báo cáo nguồn có thể giao trước; ChatGPT đối chiếu cả hai luồng trước khi nghiệm thu B2-N hoặc mở bước KVM2.

### B2-N follow-up — đối chiếu PR #5

**FIRST_ACTION.** Fetch main mới và ACK SHA theo READ_SET trên. Đọc toàn bộ [PR #5](https://github.com/DuyKienTTD/Hosting/pull/5) tại `253a795`, gồm source, report và JSON, cùng baseline [PR #4](https://github.com/DuyKienTTD/Hosting/pull/4) tại `10bf62d` và [quyết định follow-up](2026-11-21-hermes-gate-b-one-shot-paid-e2e.md#h6-b2-n-follow-up--target-parity-và-runtime-evidence). Giữ ma trận N1–N8 và chỉ cập nhật các hàng có chứng cứ mới.

- **Làm ngay.** Ghi verdict cho 3 hash Hermes, phạm vi file Runs thứ tư và 10 assertion candidate. Nêu phần candidate JS đã kiểm và phần chỉ runtime n8n mới chứng minh được. Rà phạm vi phép chiếu provenance của Codex, gồm định danh sandbox, image/version, active revision và các trường ảnh hưởng hành vi. Đối chiếu [SQLite WAL read-only](https://sqlite.org/wal.html#readonly) và [n8n Respond to Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/), ghi ngày và giới hạn áp dụng.
- **Khi PR #5 bổ sung.** Đối chiếu chính xác commit mới, projection/delta và nếu có, render/trace. Chỉ chuyển N1 khỏi blocked khi đủ image/version sandbox và bằng chứng parity; revision ID một mình chưa đáp ứng. Với N4/N8, yêu cầu cùng run ID và recorder delta qua restart, receipt gắn binding đã commit và đọc lại sau mất ACK/restart. Phân biệt baseline target-equivalent với phần sửa candidate local. HTTP 200 chỉ là một phần bằng chứng.
- **ACCEPTANCE / STOP.** Ghi từng hàng có source/observed/expected/evidence và điểm dừng. Nếu thiếu provenance, kết luận `SOURCE_QA_COMPLETE / RUNTIME_EVIDENCE_PENDING` và chỉ rõ N1 vẫn blocked. Khi có trace, kết luận `GO_FOR_CHATGPT_REVIEW` hoặc `NO_GO` cho chất lượng evidence theo commit đã audit. Thiếu một phép đo cụ thể thì yêu cầu đúng delta, giữ B2-I/K/L/M đã nghiệm thu.
- **WRITE_SET / HANDOFF.** Cập nhật báo cáo và evidence tùy chọn theo write-set ở trên, trên chính PR #4. Work chỉ đọc GitHub và nguồn công khai, phạm vi KVM2 vẫn ngoài nhiệm vụ Work. Push, remote readback, bàn giao SHA/PR cho ChatGPT. `from_agent: chatgpt`, `to_agent: chatgpt-work`, `next_owner: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD` cho lượt bổ sung. ACK cũ chỉ áp dụng cho lượt ma trận ban đầu.

### Work delta — tiêu chí đọc kết quả provenance

**Quyết định review.** Tiếp nhận [QA Work `ff2a1a9`](https://github.com/DuyKienTTD/Hosting/blob/ff2a1a97c075df4a49887678e7f4fe7b89e42ab9/reports/2026-11-22-work-b2-n-independent-contract-qa.md) cho phạm vi source. Ma trận N1–N8 đã hoàn tất; N1 còn `BLOCKED_TARGET_PARITY`, trace B2-N `NOT_RUN`. Change trigger của lượt này là probe mới ở [`dcf6854`](https://github.com/DuyKienTTD/Hosting/blob/dcf68542518797c977206536536e04f2727424d8/sandbox/p0-hermes-gate-a/h6_b2n_n8n_provenance.py) chuẩn hóa một số giá trị và trả JSON so sánh. Work có thể chuẩn bị quy tắc diễn giải JSON trước khi có kết quả chạy. Tái sử dụng ma trận đã nộp.

**FIRST_ACTION / READ_SET.** Fetch main, ACK SHA và bộ tài liệu ở READ_SET trên. Mở mục “Delta source tại `dcf6854`” trong báo cáo Work. Đọc `projected()`, `compare()` và phần phát JSON của probe ghim để xác định trường nào là điều kiện nghiệm thu và trường nào chỉ hỗ trợ chẩn đoán.

**Đầu ra nghiệm thu.** Thêm một bảng ngắn vào chính báo cáo PR #4 với JSON giả tối giản trên giấy, trường quyết định, verdict và phép xác minh nhỏ nhất còn thiếu. Bao phủ bốn tình huống:

| Tình huống | Kết luận cần phân biệt |
| --- | --- |
| Projection khớp và danh tính image đủ | Có thể đủ cho N1 phần cấu trúc nếu published revision ổn định và image local pin được. Auth có hiệu lực, binding và receipt vẫn cần trace N8. |
| Projection khớp nhưng repo digest rỗng hoặc thiếu bằng chứng pin | Kiểm xem có định danh bất biến thay thế và chứng minh tái tạo đúng image local hay không. Nếu thiếu, giữ N1 blocked. |
| Projection không khớp | Dựa vào loại delta đã khử nhạy cảm để chỉ ra node/settings/connections cần chứng minh. Không cần digest của dữ liệu published chưa khớp hoặc export thô. |
| Projection khớp sau thay bearer/route bằng mẫu | Chỉ ra cặp semantic thay đổi bắt buộc phải xuất hiện trong delta, chẳng hạn đổi logic auth hoặc đích ngoài mẫu. Nêu ranh giới giữa tương đương cấu trúc và xác thực callback thực thi. |

**WRITE_SET / STOP / HANDOFF.** Work chỉ thêm mục vào báo cáo hiện có trên [PR #4](https://github.com/DuyKienTTD/Hosting/pull/4). Không tạo task hoặc PR mới, chạy probe/test, truy cập KVM2 hay yêu cầu export thật. Đầu ra là tiêu chí review; giữ `SOURCE_QA_COMPLETE / RUNTIME_EVIDENCE_PENDING`. Nếu có evidence mới trong lúc làm, dẫn commit và để ChatGPT quyết định lượt review runtime. Work push, đọc lại diff/commit remote và bàn giao cho ChatGPT. `from_agent: chatgpt`, `to_agent: chatgpt-work`, `next_owner: chatgpt`, `handoff_state: PREPARED_FOR_OWNER_FORWARD`. Lượt này không giao thêm đầu việc Codex.
