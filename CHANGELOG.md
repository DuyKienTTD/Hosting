# Lịch sử cập nhật

## 2026-11-23

- ENG-01A-S1 đạt 8/8 kiểm thử offline, gồm bốn cửa sổ worker crash/restart, replay không dispatch lặp và receipt bất biến. Chờ ChatGPT Điều phối nghiệm thu. [Báo cáo](reports/2026-11-23-eng-01a-s1-offline-connector-contract.md).

- Nghiệm thu B2-O fake local tại `d95f161` và chuẩn bị B2-P preflight chỉ đọc.

## 2026-11-22

- Phân vai WS-02: Hostinger Agent xác minh hiện trạng qua hPanel độc lập, Work soạn runbook và diễn tập. [Task Hostinger](tasks/2026-11-22-hostinger-ws02-infrastructure-baseline.md).

- Chuẩn bị WS-02 giám sát và triage cho Work với nghiệm thu riêng, song song Codex B2-O. [Task Work](tasks/2026-11-22-work-ws02-monitoring-and-triage.md).

- Nghiệm thu QA B2-N của Work tại `00f5649` trong phạm vi đã đo và chuẩn bị Work review độc lập tuyến B2-O trên PR #4.

- Review Codex B2-N active restart tại `029f80e` và chuẩn bị B2-O local để đo deadline và callback tự động trên tuyến fake tích hợp.

- Tiếp nhận bảng tiêu chí provenance Work tại `c265340` và bổ sung lượt review độc lập bằng chứng runtime B2-N `a19765f` trên PR #4 hiện có.

- Đối chiếu kết quả B2-N tại `a19765f`, ghi phạm vi fake runtime đã đo và đặc tả delta restart lúc run active cho Codex.

- Tiếp nhận QA source B2-N của Work tại `ff2a1a9` và bổ sung tiêu chí đọc kết quả provenance trên task Work hiện có.

- Review PR #4/#5, ghi blocker n8n target parity và cập nhật hai đặc tả B2-N cho Codex và Work trên các PR hiện có.

- Chuẩn bị hai luồng H6 B2-N song song, Codex kiểm contract local bằng fake provider và Work QA độc lập qua PR riêng. [Phân công](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md#handoff-song-song-h6-b2-n).

- Merge Work QA PR #3, nghiệm thu B2-M trong đúng cửa sổ đo và mở B2-N kiểm contract Hermes/n8n ngoại tuyến bằng fake provider. [Work QA](reports/2026-11-22-work-b2-m-independent-canary-qa.md).

- ChatGPT đối chiếu source và bằng chứng Codex B2-M tại `8238bd1`, ghi điểm cần xác minh trong Work QA hiện có và xác định bước fake-provider chỉ sau nghiệm thu. [Quyết định](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md#chatgpt-review-h6-b2-m--2026-11-22).

- Codex hoàn tất B2-M startup-only canary giả trên KVM2 ext4, kiểm render, 20 health bất biến, deny admission và rollback đúng inventory. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-m-kvm2-idle-canary.md).

- ChatGPT mở Work B2-M QA độc lập, chỉ đọc source/render/rollback/evidence của canary KVM2 do Codex phụ trách; write-set report/PR riêng, không can thiệp KVM2/live P0/provider/paid. [Work task](tasks/2026-11-22-work-b2-m-independent-canary-qa.md).

- ChatGPT nghiệm thu source/mock B2-K `351afa2` (6/6) + B2-L `c4d5402` (9/9) và giao B2-M KVM2 **isolated synthetic** writer startup/health canary; chưa thay live writer/ledger/provider/paid. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-k-l-chatgpt-review.md).

- Codex hoàn tất B2-L startup-only P0 writer trên fixture root-owned, health IPC xác thực chỉ đọc và crash/restart matrix. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-l-idle-writer.md).

- Codex hoàn tất B2-K cross-service mock với ba tiến trình/datastore, run-ID bền và callback/receipt xác thực. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-k-cross-service.md).

- ChatGPT nghiệm thu audit Work B2-J (PR #2 merge `0d8c0f6`), phân tách permitless writer idle/health khỏi quyền admission và mở Codex B2-L source/mock (song song độc lập với B2-K). Không có KVM2/live/P0 real/provider/paid authorization. [Review](reports/2026-11-22-work-b2-j-chatgpt-review.md).

- ChatGPT nghiệm thu B2-I `8ded770` fixture 202/status/callback (12/12 + 4/4), mở B2-K mock cross-service với adapter/Hermes/receiver tách dữ liệu; Work B2-J vẫn chuẩn bị. Không live P0/provider/paid. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-i-chatgpt-review.md).

- Codex hoàn tất H6 B2-I mock `202/status/callback` với SQLite tạm, HMAC callback và test delay, lost ACK, replay, dead-letter, unknown reserve. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-i-async-contract.md).

- Phân hai luồng độc lập: Codex B2-I triển khai/test async 202/status/callback trên fixture, Work B2-J audit idle writer startup và recovery/readiness; không chỉnh cùng source, không live P0/production/provider/paid. [Task Work](tasks/2026-11-22-work-b2-j-idle-startup-audit.md) · [Task Codex](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md).

- ChatGPT nghiệm thu QA Work B2-H độc lập và merge PR #1 `3e9ccc8`; xác nhận LIVE_INTEGRATION_NO_GO, writer startup requires permit và bridge/n8n deadline/callback mock blockers. Giữ B2-I offline, bổ sung kiểm startup idle trên dữ liệu giả; không mở provider/ledger thật/paid. [Báo cáo](reports/2026-11-22-work-b2-h-assurance.md).

- ChatGPT accepted B2-H read-only evidence at `71fdd40` with LIVE_INTEGRATION_NO_GO (bridge 20s/n8n 30s/Guard 45s; mock-only callback), authorized B2-I async deadline/callback contract offline/mock; real ledger/production/provider/paid unchanged. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-h-chatgpt-review.md).

- Codex hoàn tất H6 B2-H read-only trên KVM2, đối chiếu H4, UID/mount/proxy, Compose preview và workflow n8n đang publish. Live integration NO-GO do deadline/callback và writer mount chưa duyệt. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-h-read-only.md).

- Chủ dự án yêu cầu tăng cường ChatGPT Work; ChatGPT giao luồng Work audit độc lập B2-H song song Codex, có write set riêng, chỉ đọc, không làm thay đổi KVM2/ledger/provider/paid. [Work task](tasks/2026-11-22-work-independent-b2-h-assurance.md).

- ChatGPT accepted H6 B2-G `c3c233a` KVM2 fake TLS/rollback (13 scenarios) and opened B2-H read-only real integration readiness; no live ledger mount/provider/paid authorization. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-g-chatgpt-review.md).

- Codex hoàn tất H6 B2-G CONNECT/TLS giả trên KVM2. Xác minh chain/hostname, exact-wire POST, deadline slow-drip, no-bypass và rollback. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-g-kvm2-fake-tls.md).

- ChatGPT reviewed `b670a65` H6 B2-F source/mock (13/13 Codex PASS) and opened B2-G on KVM2 with isolated synthetic CONNECT/TLS proxy/provider, cert negative tests and rollback; no real ledger/provider or paid. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-f-chatgpt-review.md).

- Codex hoàn tất H6 B2-F source/mock cho Guard provider transport bị khóa, IPC P0 v1, reserve bền vững, exact bytes, settlement và callback mô phỏng. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-f-source-mock.md).

- ChatGPT accepts `H6_B2_E_KVM2_MOCK_PASS` and `ROLLBACK_PASS` from `e4269f0`, opens B2-F disabled-by-default real path implementation in source+fake-ledger/provider offline mocks only; KVM2 real ledger/paid remain blocked. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-e-chatgpt-review.md).

- Codex hoàn tất H6 B2-E mock cô lập trên KVM2/ext4. Kiểm pre-up, HMAC v2, Level 2, crash/replay/callback và rollback, đối chiếu pre/post GATE A, production và metadata ledger thật. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-e-kvm2-mock.md).

- ChatGPT accepted H6 B2-D actual source HMAC/mock from `cf36e59` and opened B2-E standalone KVM2 authenticated mock rehearsal with strict pre-render isolation, synthetic ledger/key, rollback and no real provider/paid. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-d-chatgpt-review.md).

- Codex tích hợp IPC HMAC hai chiều vào Guard/writer cho H6 B2-D mock-only, ký ACK theo request, kiểm Compose local và chạy hồi quy Stage A/B2-A. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-d-ipc-integration.md).

- ChatGPT chấp nhận B2-C offline tại `bca741f`, xác minh HMAC hiện **chỉ ở fixture** và mở B2-D tích hợp HMAC trong mã Guard/writer, test offline/mock; không KVM2 apply/ledger thật/provider. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-c-chatgpt-review.md).

- Codex hoàn tất H6 B2-C offline, kiểm writer UID 0 bỏ caps đối chiếu UID riêng/ACL, xác thực Unix socket, cạnh tranh Level 2 và crash/replay/rollback trên ledger giả. Bàn giao ChatGPT nghiệm thu. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-c-uid-model.md).

- ChatGPT accepts B2-B read-only evidence at `6a6e691`, keeps `BLOCKED_UID_OR_MOUNT`; opens B2-C offline-only model comparison for root UID writer with zero capabilities vs non-root ACL on synthetic ledger. No KVM2 apply/provider/paid. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-b-chatgpt-review.md).

- Codex hoàn tất B2-B chỉ đọc trên KVM2, xác minh blocker DAC cho writer UID 23062 và render preview/rollback khớp phạm vi. Bàn giao ChatGPT nghiệm thu. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-b-preflight.md).

- ChatGPT nghiệm thu B2-A offline từ `1caf096`/`c97fca2`, ghi nhận Level 2 thiếu parent directory fsync; mở B2-B chỉ-read trên KVM2 để khảo sát UID/mount/lock và render diff, **chưa** apply ledger thật/provider, paid GATE B vẫn BLOCKED_PREFLIGHT. [Review](reports/2026-11-22-hermes-gate-b-h6-b2-a-chatgpt-review.md).

- Codex hoàn tất H6 B2-A trên fixture P0 v1 do adapter Level 2 tạo. Kiểm lock/inode, một ACK khi có cạnh tranh, crash, replay, settlement, schema lỗi và Compose render offline. ChatGPT nghiệm thu theo §10. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-b2-a.md).

- Chủ dự án ủy quyền ChatGPT điều phối liên tục (quy tắc §10) và ChatGPT mở H6 Stage B2-A: Codex xây dựng/test tương thích shared P0 ledger và Level 2 writer hoàn toàn trên mock/schema giả, không chạm ledger thật, provider, production hoặc paid. [Task](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md).

- ChatGPT nghiệm thu H6 Stage B1: `H6_STAGE_B1_ACCEPTED` theo code `7a03aeb`, evidence `afcd07e`, 8/8 KVM2 mock, 6/6 bounded no-bypass và rollback PASS; Stage B2/C chưa duyệt, paid GATE B BLOCKED_PREFLIGHT. [Reviewer](reports/2026-11-22-hermes-gate-b-h6-stage-b1-chatgpt-review.md).

- Codex hoàn tất H6 Stage B1 trên KVM2 sau khi qua cổng render và kiểm trùng tài nguyên. 8/8 ca mock, 6/6 no-bypass, rollback và đối chiếu baseline PASS. ChatGPT review, paid GATE B vẫn `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-stage-b1.md).

- Chủ dự án phê duyệt **H6 Stage B1 KVM2 isolated mock**: Codex có quyền dựng và rollback một Compose project test riêng sau cổng kiểm tra rendered Compose/mount/network, chỉ dùng ledger và secrets giả; không chạm GATE A/production/ledger thật hoặc gọi provider/paid. Stage B2/C chưa duyệt. [Task](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md).

- ChatGPT review source `a411114` + evidence `5a70e3b`: **H6_STAGE_A_ACCEPTED** (8/8 isolated mock supported), không chứng minh Hermes/KVM2/provider E2E; Stage B chưa duyệt, paid GATE B BLOCKED_PREFLIGHT. [Reviewer](reports/2026-11-22-hermes-gate-b-h6-stage-a-chatgpt-review.md).

- Hoàn tất H6 Stage A với Guard/writer mock, IPC xác thực hai chiều, Compose overlay và kiểm thử offline trên ledger giả. Gate B paid giữ `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-stage-a.md).

- Chủ dự án phê duyệt H6 Stage A cho Codex: phát triển Guard/writer/Compose overlay trong repo và chạy offline/mock trên ledger giả; không KVM2 apply, không ledger live, không provider/paid/production. Phê duyệt ghi trực tiếp trong [task GATE B](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md); Stage B/C chưa duyệt, handoff PREPARED_FOR_OWNER_FORWARD.

- ChatGPT chấp nhận **phần chuẩn bị** H6 và kiến trúc writer độc lập **có điều kiện**, chưa duyệt áp dụng sandbox. Phải kiểm socket peer, inode/lock, atomic reserve, provider path và rollback qua mock; Gate B paid tiếp tục BLOCKED_PREFLIGHT. [Review](reports/2026-11-22-hermes-gate-b-h6-chatgpt-design-review.md).

- Codex hoàn tất chuẩn bị H6 bằng đối chiếu KVM2 chỉ đọc. Ghi bằng chứng về ledger mount theo file, bản backup và digest ứng viên, cùng phương án writer giới hạn và rollback để ChatGPT review. [Báo cáo](reports/2026-11-22-hermes-gate-b-h6-preparation.md).

- Theo chỉ thị chủ dự án: đóng H5 (`DONE/H5_ACCEPTED`), mở H6 (`OPEN_PREPARATION`) bên trong task GATE B hiện hành. Chuyển giao mới ở `PREPARED_FOR_OWNER_FORWARD`; không thêm quyền sandbox mutation/paid/production. [Task](tasks/2026-11-21-hermes-gate-b-one-shot-paid-e2e.md).

- ChatGPT chính thức nghiệm thu H5 `H5_ACCEPTED / PROVIDER_PREFLIGHT_PASS` theo commit `1d9a604`, giới hạn vào quyền quản trị, token count và mock; H6 paid path chưa nghiệm thu, GATE B `BLOCKED_PREFLIGHT`. [Reviewer](reports/2026-11-22-gate-b-chatgpt-provider-and-scope-review.md).

- ChatGPT read-only source/entitlement/scope review: H5 follow-up verified project/key metadata, billing and 723 candidate input tokens; live Guard remains mock-only and real ledger RO; paid NO_GO. [Review](reports/2026-11-22-gate-b-chatgpt-provider-and-scope-review.md).

- Codex hoàn tất H5 provider preflight với bằng chứng quản trị project, số token theo digest và kiểm thử one-shot đúng bytes trên ledger mock. Paid inference bằng 0. ChatGPT tiếp nhận nghiệm thu trước H6. [Báo cáo](reports/2026-11-22-hermes-gate-b-h5-preflight-followup.md).

- H5 xác minh GPT-6 Luna metadata HTTP 200 từ Guard. H5 còn bị chặn vì thiếu bằng chứng project và final forwarded digest gắn với runtime. Không phát sinh paid inference. [Báo cáo](reports/2026-11-22-hermes-gate-b-h5-provider-preflight.md).

- Bàn giao H5 provider preflight trong task GATE B hiện có: owner Codex, ChatGPT nghiệm thu, first action KVM2, model/project/Responses, forwarded digest, input_tokens, pricing, budget, one-shot readiness; không dispatch paid trong H5; handoff chỉ PREPARED_FOR_OWNER_FORWARD.

- ChatGPT nghiệm thu Guard-only mount từ report/evidence GitHub commit `7455fa3`: `GUARD_MOUNT_ACCEPTED` trong phạm vi mount; giữ paid GATE B `BLOCKED_PREFLIGHT`, không tuyên bố ChatGPT tự kiểm tra KVM2 và không phát sinh provider call.

- Nghiệm thu `GUARD_MOUNT_PASS` trên KVM2. Chỉ Guard được recreate để mount credential chỉ đọc. Production health, cách ly proxy và ledger đều đạt kiểm tra sau thay đổi. Paid GATE B vẫn `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-22-hermes-gate-b-guard-mount-results.md).

- Ghi kết quả phiên Guard-only mount bị chặn ở đường truy cập KVM2. Docker Compose local xác nhận overlay chỉ thêm một bind mount read-only cho Guard. [Báo cáo](reports/2026-11-22-hermes-gate-b-guard-mount-access-result.md).

## 2026-11-21

- Codex hoàn tất onboarding tại commit `30ccdfa`: đọc đầy đủ entrypoint, quy tắc, hồ sơ, toàn bộ tài liệu/evidence được catalog chỉ mục và các Markdown ngoài archive; ghi ACK sẵn sàng nhận task nhưng chưa tự bắt đầu GATE B hoặc thay đổi runtime. Repository validator PASS 137 tracked files.

- Mở rộng đặc tả Guard-only mount trong task GATE B hiện có theo chỉ đạo owner: Codex phải thử các đường kiểm tra an toàn thay thế (Web Terminal, HTTP từ container, permit theo schema thực tế, Compose-vs-inspect) trước khi handoff BLOCKED; không nới approval hoặc bỏ qua safety gate.

- Bổ sung phần điều phối vào task GATE B hiện có: hoàn tất backup, rendered Compose và production/ledger baseline trước Guard-only mount. Chỉ ghi REPORTED cho cập nhật Codex chưa có evidence GitHub; giữ nguyên owner/status/approval và các gate an toàn.

- Hoàn tất đồng bộ entrypoint README và hồ sơ ChatGPT/Codex với quy tắc Continuous Task Execution (AGENT_WORKFLOW mục 9). Phạm vi chỉ tài liệu điều phối; không thay task GATE B, approval, state VPS hoặc runtime. Phân biệt Codex REPORTED preflight với VERIFIED_LIVE bằng chứng.

- Bổ sung mục 9 của AGENT_WORKFLOW về **thực thi liền mạch theo kết quả**: tiếp tục mặc định với phần việc đã được phép, không coi preflight chưa làm là blocker; STOP thao tác rủi ro khi thiếu điều kiện, handoff theo sự kiện và tái sử dụng evidence. Đồng bộ AGENTS.md/CATALOG.yaml; không cấp thêm quyền production/paid và không khẳng định runtime 24/7.

- Tạo checkpoint GATE B tại điểm dừng guard mount: Codex mới đối chiếu approval/overlay từ GitHub, chưa đọc đủ rules, chưa xác minh live Compose/backup/rollback nên chưa recreate guard. Giữ nguyên H3/H4 evidence PASS và giới hạn owner phê duyệt; GATE B `BLOCKED_PREFLIGHT`. [Checkpoint](reports/2026-11-21-hermes-gate-b-guard-mount-paused-checkpoint.md).



- Chủ dự án chấp thuận bước recreate **riêng sandbox guard** để mount OpenAI API secret read-only theo H4 overlay; điều kiện bắt buộc: backup/rollback, no-bypass, no-public-port, production health và ledger/kill switch bất biến; không gọi provider hoặc paid inference. Bổ sung approval vào task mẹ, không thay owner/status/approval gốc; handoff Codex còn `PREPARED_FOR_OWNER_FORWARD`.



- Codex xác minh live metadata sau owner input: secret staging `PRESENT`, mode `0600`, chưa mount; không đọc/băm/đo kích thước key, không chạy Compose hoặc provider request. Guard-only sandbox recreate/mount chờ phê duyệt riêng; GATE B vẫn `BLOCKED_PREFLIGHT`. [Báo cáo](reports/2026-11-21-hermes-gate-b-h4-owner-key-live-check.md).

- Ghi nhận xác nhận của chủ dự án từ Hostinger Web Terminal: H4 `STORED_NOT_MOUNTED`, key đã nhập ẩn hai lần và lưu staging theo thông báo script; không công khai key/host log; chưa mount/recreate hoặc gọi provider. Chờ phê duyệt riêng để Codex mount guard, rồi mới kiểm quyền/token count. GATE B giữ `BLOCKED_PREFLIGHT`.



- ChatGPT nghiệm thu H4 tại commit `d2d00f0` bằng report/evidence và review mã `f335752`: loại bỏ Compose recreate trong giao diện, 11/11 Linux test PASS, chuẩn bị Hostinger Web Terminal owner key input và dừng ở STORED_NOT_MOUNTED. Chưa mount secret, chưa paid provider call; GATE B BLOCKED_PREFLIGHT.



- H4 GATE B `READY_FOR_OWNER_KEY_INPUT`: review mã `9596bf1` phát hiện và loại bỏ đường Compose recreate trước khi chạy; Linux fake-key 11/11, terminal no-echo lifecycle và Compose read-only PASS. Interface cuối chỉ staging secret `0600`, không mount/recreate, không public port/provider call. Fake key đã revoke; production restart 0, ledger 1 attempt/0 permit, kill switch ON, paid delta 0. [Báo cáo H4](reports/2026-11-21-hermes-gate-b-h4-key-input-preparation.md).

- Theo chỉ thị chủ dự án, đã thêm H4 vào task GATE B: Codex chuẩn bị cơ chế chủ dự án tự nhập OpenAI API Key qua giao diện kín localhost/SSH tunnel hoặc terminal không echo; guard-only secret mount, không public port, không secret trong log/Git, test fake-key trước, không phát sinh paid inference. Trạng thái mới chỉ `PREPARED_FOR_OWNER_FORWARD`.



- ChatGPT đã nghiệm thu kết quả H3 `MOCK_E2E_PASS` từ report/evidence trên GitHub và bổ sung mục nghiệm thu vào task mẹ mà không thay owner/status/approval. Paid GATE B vẫn `BLOCKED_PREFLIGHT`; credential guard và token count theo final digest chờ xác minh, không rerun bài test mock đã PASS khi không đổi điều kiện.


- Lưu điểm tiếp tục GATE B sau H3, liên kết bằng chứng đã có và ghi điều kiện gỡ chặn. [Checkpoint](reports/2026-11-21-gate-b-h3-checkpoint.md).

- Chủ dự án ban hành quy tắc tránh thao tác sai/lặp lại: đọc đủ toàn bộ tài liệu liên quan trước khi suy luận hoặc sửa; rà evidence đã PASS và chỉ rerun theo change trigger; tách dữ liệu/ownership và write-set, bảo vệ metadata task mẹ; review toàn diff, xác minh remote post-push, dừng khi output truncated hoặc quyền chưa rõ. Đã cập nhật AGENT_WORKFLOW mục 8, AGENTS, CONTRIBUTING, README, template báo cáo và CATALOG; GitHub branch protection/CI chưa được xác nhận là đã bật.


- H3 PASS combined mock E2E trên KVM2 với callback, một dispatch và one-shot accounting trong cùng lượt. Xác nhận rollback, topology cách ly và ledger thật không đổi. Paid readiness chờ credential guard và token count theo provider. [Báo cáo](reports/2026-11-21-hermes-gate-b-h3-preflight.md).

- Tổng hợp H1 Hostinger và H2 Hermes để chuẩn bị H3 trong task GATE B hiện có: chẩn đoán replay bridge task_id vs runtime mismatch, khóa forwarded Responses digest và token-count cùng digest, yêu cầu rerun combined mock callback+one-shot trên isolated topology, guard-only OpenAI credential, không nhầm với service auth keys. H3 chuẩn bị cho Codex ở PREPARED_FOR_OWNER_FORWARD; chưa gửi/ACK, chưa paid dispatch.


- Khôi phục nhiệm vụ GATE B bị H1 ghi đè nội dung/owner/status trong commit `5b8dd629`: giữ nguyên quyết định paid một attempt ở `owner: codex`, `status: blocked`, và ghi kết quả H1 read-only đã nhận từ Hostinger. Phân biệt provider OpenAI key (guard-only) với hai service-auth keys cần dùng theo vai trò. Bổ sung quy tắc tránh agent tham vấn ghi đè task mẹ. H2 Hermes chưa ACK, GATE B chưa dispatch.
- Hoàn tất handoff H2 cho `TTD-HERMES-GATE-B-001`: thêm `reports/2026-11-21-gate-b-hermes-consult.md` và `reports/evidence/2026-11-21-gate-b-hermes-consult.json`, cập nhật task/STATE/CATALOG tương ứng.
- Kết luận H2: `HERMES_RUNTIME_MISMATCH` chưa chứng minh mismatch live; bridge có thể replay lỗi cũ theo `task_id`. Canonical permit/hash phải bind vào forwarded `/v1/responses` body sau guard, và contract `POST /v1/responses/input_tokens` phải dùng cùng input surface của request inference.

- Điều phối GATE B theo rule mục 7 sau egress isolation: xác minh report/evidence `88268989`; cập nhật task hiện có để chuẩn bị hai handoff H1/H2 Hostinger Agent và Hermes Agent sau egress isolation, ghi owner, cách bắt đầu, nguồn vendor, nghiệm thu, trạng thái PREPARED_FOR_OWNER_FORWARD; chưa gửi/ACK, chưa giao Codex thực thi, 0 paid call. Giữ GATE B BLOCKED_PREFLIGHT.


- Chủ dự án phê duyệt quy tắc điều phối mới: ChatGPT tự nghiên cứu tài liệu vendor chính thức, hỏi Hostinger/Hermes trước khi giao Codex theo đúng sở trường, đặc tả có bước bắt đầu cụ thể, nhận/giao bóng ghi owner và trạng thái ACK, mọi agent đọc lại AGENTS/workflow/security/STATE/CATALOG trước task. Đã cập nhật trực tiếp `rules/AGENT_WORKFLOW.md`, `AGENTS.md`, agent directory/profile, README, catalog; quy tắc không tự cấp thêm quyền paid/production. Nguồn tham khảo chính thức ghi trong rule.


- Cô lập proxy Level 2 trên mạng riêng với guard. Kiểm tra quyền truy cập từ sáu container, mock callback, hạch toán mock và rollback egress. Paid GATE B vẫn chờ credential và token count theo provider. [Báo cáo](reports/2026-11-21-hermes-gate-b-egress-isolation.md).

- Kiểm tra lại paid GATE B. Guard mock khớp fingerprint toàn body và lưu usage hoặc trạng thái không rõ sau timeout. Dừng trước paid dispatch vì bridge chạm được proxy Level 2 và còn thiếu bằng chứng credential/cap theo provider. Ledger thật giữ nguyên và kill switch ON. [Báo cáo](reports/2026-11-21-hermes-gate-b-preflight-recheck.md).

- Hoàn tất GATE B guard remediation mock trên KVM2: shared-lock interop và 14 fault cases PASS, full n8n→Hermes→guard→provider mock→callback PASS, replay không cấp thêm admission. Sandbox rollback; production health 200/restart 0; ledger thật không đổi, kill switch ON, paid calls và chi phí mới 0. Paid GATE B vẫn chờ preflight riêng.

- Chạy one-shot Linux unit trên KVM2 với ledger copy: 20 tiến trình, đúng 1 admitted, 19 rejected, fault/replay và hai crash boundary PASS; đối chiếu live ledger 1 attempt/kill switch ON, production health 200/restart 0. Guard mock E2E và full crash matrix còn pending, 0 paid calls.

- Thêm bản nháp one-shot transaction trên ledger copy cho GATE B. Local Windows thiếu `fcntl` và Docker daemon không chạy, nên mock/live chưa xác minh; dừng ở `BLOCKED_PREFLIGHT`, 0 paid calls và không đổi runtime.

- Đối chiếu GATE B `BLOCKED_PREFLIGHT` (0 Hermes paid attempts mới, 0 USD phát sinh). Guard hiện thiếu one-shot permit và reserve ngân sách trên shared ledger; ledger/kill switch/production chưa xác minh live. Giao Codex task `TTD-HERMES-GATE-B-GUARD-REMEDIATION-001` để sửa và kiểm thử mock-only, không mở paid dispatch hoặc nới phạm vi.

- GATE B preflight `BLOCKED_PREFLIGHT`: guard GATE A chưa triển khai atomic one-shot permit và reservation trên shared ledger; dừng trước dispatch, 0 paid Hermes attempt, 0 chi phí API mới. Thêm báo cáo/evidence và cập nhật task/ADR/state.

- Chủ dự án phê duyệt GATE B theo ADR-P0-003: Codex được thực hiện tối đa một paid Hermes Agent call qua `gpt-6-luna`, ≤4K input và max_output_tokens=600, fake data, shared P0 USD 0.05 cap, không tools/retry/production change; one-shot permit phải tự tiêu thụ và khóa lại trước dispatch, global kill switch luôn ON. Tạo task `TTD-HERMES-GATE-B-001`; chưa có evidence paid Hermes E2E mới.

- Đối chiếu GATE A Hermes auxiliary+guard+bridge mock PASS với evidence và commit `ab319ee`; cập nhật đề xuất ADR-P0-003 (PROPOSED), chỉ cho một Hermes Agent paid call nếu chủ dự án phê duyệt riêng, có one-shot permit/atomic ledger/kill-switch, không đổi production. Chưa thực hiện GATE B.

- Hoàn tất `TTD-HERMES-GATE-A-001`: triển khai Hermes auxiliary, private guard, authenticated bridge và provider mock trên internal sandbox; exact model, cap 600, full request ≤4K, no-tools/no-bypass, auth, fault/idempotency/concurrency và mock E2E đều PASS.
- Phát hiện ownership workflow trong rollback rehearsal đầu, sửa script và chạy lại corrected rollback/restore PASS; redeploy smoke PASS. Production n8n/Hermes HTTP 200, restart/downtime 0; kill switch/ledger không đổi, paid calls và chi phí mới bằng 0.
- Ghi trạng thái `GATE_A_MOCK_PASS / GO_FOR_GATE_B_APPROVAL`; GATE B không được thực hiện và vẫn cần phê duyệt riêng cho đúng một paid Hermes call.

- Chủ dự án phê duyệt GATE A theo ADR-P0-002: Codex triển khai Hermes auxiliary, private guard, authenticated bridge và hai service secrets chỉ trên KVM2 sandbox; mock capture, kill switch ON, paid calls 0, không đổi production. Tạo task `TTD-HERMES-GATE-A-001`; GATE B chưa được phê duyệt. Việc ghi nhận GitHub không có nghĩa VPS đã được thay đổi.

- Review feasibility Hermes hard cap và lập ADR-P0-002 ở trạng thái PROPOSED: đề xuất GATE A cho Hermes auxiliary, guard, bridge và provider mock capture (kill switch bật, 0 paid call); paid Hermes call GATE B yêu cầu phê duyệt riêng. Không thực hiện thay đổi VPS.

- Hoàn tất `TTD-HERMES-E2E-HARD-CAP-001` ở chế độ read-only/offline: xác minh Hermes `0.22.5`, exact-model/no-tools serialization và kết luận CLI/config upstream không đủ hard output cap.
- Thêm offline guard contract rehearsal PASS cho kill switch, validation-before-reservation, idempotency và 10-way concurrency dùng bản sao shared ledger; paid call mới 0, production change 0.
- Đề xuất Hermes auxiliary nguyên bản + private pre-dispatch guard + authenticated bridge/callback ở trạng thái `GO_FOR_SEPARATE_IMPLEMENTATION_APPROVAL`; Hermes E2E vẫn `BLOCKED_COST_CONTROL` cho tới khi mock/full-input/no-bypass và paid-test riêng được duyệt.

- Đối chiếu Provider E2E PASS (1 call, USD 0.0000496 theo usage, chưa đối soát hóa đơn) và Hermes Agent E2E `BLOCKED_COST_CONTROL`. Tạo `TTD-HERMES-E2E-HARD-CAP-001` để Codex khảo sát read-only cơ chế hard output cap trước request và shared budget gate; chưa cấp quyền triển khai thêm hoặc paid inference.

- Hoàn tất Mức 2 Provider E2E trên sandbox: đúng 1 GPT-6 Luna call, authenticated n8n callback/schema PASS, 131 input + 73 output + 0 reasoning token, usage-based cost USD 0,0000496; replay/conflict không phát sinh call mới.
- Thêm persistent atomic ledger, allowlist CONNECT proxy và kill switch đã bật; task mới bị chặn trước provider, không public port/firewall/DNS/production change, n8n/Hermes production restart 0.
- Ghi `HERMES_E2E_BLOCKED_COST_CONTROL`: Hermes CLI thật chưa chứng minh hard output cap trước request và chưa có private inference callback route; không dùng Provider PASS làm bằng chứng Hermes.

- Chủ dự án phê duyệt Mức 2 GPT-6 Luna: ≤5 paid calls, ≤4K input + 2K output tokens/call, hard target USD 0.05/ngày và USD 0.05 tổng P0, fake data; dừng nếu không kiểm soát được chi phí/quyền. Tạo task Codex `TTD-AI-P0-LEVEL2-001`, nghiệm thu provider E2E và Hermes Agent E2E độc lập; chưa có bằng chứng live paid inference.

- Phân biệt provider E2E và Hermes Agent E2E trong [review P0 Mức 1](reports/2026-11-21-p0-level1-review-and-level2-criteria.md); GPT-6 Luna model/pricing đã đối chiếu tài liệu OpenAI, Mức 2 vẫn chưa được duyệt.

- Hoàn tất P0 Mức 1 trên KVM 2: triển khai n8n sandbox độc lập và reasoner mock cô lập trên internal network, đúng một authenticated webhook, structural E2E 9/9 và rollback/restore PASS.
- Xác minh không restart/downtime production, không public port/firewall/DNS/business change và không paid inference; cập nhật task thành `blocked` chỉ vì real reasoning còn chờ phê duyệt Mức 2.
- Thêm mã triển khai secret-free trong `sandbox/p0-level1`, cập nhật report/evidence/inventory/state/catalog và bảng provider/model cùng đề xuất cap USD 0.05 cho P0 Mức 2.

- Chủ dự án phê duyệt **Mức 1** của ADR-P0-001: Codex được tiếp tục kỹ thuật sandbox n8n ↔ Hermes với inference runtime cô lập và một authenticated webhook, có preflight/backup/rollback. Mức 2 (provider/model, cost cap, paid inference) và thay đổi gây downtime/public production vẫn chưa được phê duyệt. Chưa có thay đổi VPS do ChatGPT thực hiện tại bước ghi nhận này.

- Lập ADR-P0-001 ở trạng thái PROPOSED sau P0 network PASS/E2E BLOCKED: Hermes inference cô lập, n8n authenticated webhook, nghiên cứu provider/model và cost cap; chưa phê duyệt hay thay production.

- Triển khai network-only P0 `ttd-ai-p0-sandbox` ở chế độ internal, gắn live n8n/Hermes bằng private DNS; health, negative auth và rollback preparation PASS, không restart/downtime/public port/firewall change và không gọi paid API.
- Ghi `PARTIAL / BLOCKED_BY_BUDGET_AND_RUNTIME`: Hermes chưa expose inference API, n8n MCP còn disabled và chưa có workflow/callback; thêm report/evidence, cập nhật task/state/catalog.
- Đồng bộ catalog/state với kết quả định danh đã complete: `ttdnew.tech` U4S Hermes tách biệt KVM 2; thêm catalog entry cho báo cáo identity.

- Tạo nhiệm vụ định danh resource `ttdnew.tech` (Hostinger Agent owner) và P0 sandbox n8n ↔ Hermes (Codex owner), có identity gate, backup/rollback, không phát sinh phí chưa duyệt.
- P0 chưa được thực thi; ghi rõ trạng thái BLOCKED cho tới khi resource được xác minh và các điều kiện an toàn đạt.

- Mở rộng hồ sơ Hostinger Agent theo account inventory 2026-11-21; ghi nhận Cloud Startup/WordPress, VPS, Docker/AI, domains, email, Reach và giới hạn quyền filesystem.
- Liên kết báo cáo `reports/2026-11-21-hostinger-account-capability-inventory.md` vào catalog, danh bạ và trạng thái chung; giữ mâu thuẫn OpenClaw vs `u4s-hermes-agent` ở trạng thái chưa xác minh.

- Thêm `reports/2026-11-21-hermes-capability-survey.md`, cập nhật `agents/hermes.md`, `CATALOG.yaml` và `STATE.md` cho khảo sát bổ sung theo task `TTD-AGENT-CAPABILITY-SURVEY-001`.
- Ghi nhận rõ khác biệt giữa Hermes WebUI session và Hermes VPS container `0.22.5`; xác minh lại GitHub write, skills/memory/session recall và giữ trạng thái BLOCKED/UNKNOWN cho inference API, n8n MCP và connector business.
- Hoàn tất khảo sát Codex theo `TTD-AGENT-CAPABILITY-SURVEY-001`; ghi rõ runtime, local/Git/browser/hPanel/VPS permissions, n8n/Hermes evidence, background limits và approval boundaries.
- Cập nhật `agents/codex.md`, danh bạ agent, state và catalog; thêm catalog entry cho báo cáo Hostinger Agent đã có trên remote.
- Xác nhận Codex app build hiện tại, Git HTTPS read/write và Computer Use; ghi `BLOCKED/UNKNOWN` cho local Docker daemon, exact model, persistent execution và các connector marketing chưa test.
- Không thay đổi production hoặc tạo connector/automation/paid API call.

- Thêm danh bạ vai trò `agents/` cho ChatGPT, Codex, Hermes, Hostinger/Hostinger Agent và n8n, phân biệt capability verified/reported/unknown.
- Đưa lên GitHub task `TTD-AGENT-CAPABILITY-SURVEY-001` để chủ dự án chuyển câu hỏi đến từng tác nhân và nhận báo cáo tự đánh giá.
- Liên kết các hồ sơ vào README, PROJECT, AGENTS, STATE và CATALOG.

- Hoàn tất `TTD-AI-PLATFORM-AUDIT-001` và thêm báo cáo/evidence đã khử định danh cho kiểm toán live n8n ↔ Hermes.
- Xác minh n8n `2.45.7`, Hermes `0.22.5`, network/auth hai chiều và trạng thái runtime; ghi rõ MCP, inference API và end-to-end còn `BLOCKED`.
- Đề xuất kiến trúc n8n control plane + Hermes reasoning + internal network + policy/approval gate + media-worker; cập nhật `PROJECT.md`, `STATE.md`, inventory và catalog.
- Không thay đổi production, không gọi model/media trả phí và không kết nối tài khoản marketing.

- Tạo task `TTD-AI-PLATFORM-AUDIT-001` kiểm toán live n8n ↔ Hermes và thiết kế hệ thống AI Automation dựa trên báo cáo tự đánh giá Hermes.

- Thêm `reports/2026-11-21-hermes-self-assessment.md`, catalog tương ứng và cập nhật `STATE.md` cho đợt tự đánh giá năng lực Hermes Agent hiện tại.
- Ghi nhận đã xác minh được skills, session recall và GitHub push của agent; đồng thời giữ trạng thái chưa kiểm chứng cho exact Hermes build/version, live API endpoint và live n8n integration.

- Thêm `PROJECT.md` xác định mục tiêu nền tảng AI TTD METAL và tiến độ thực tế.
- Thêm `rules/AGENT_WORKFLOW.md` thống nhất giao task qua GitHub, báo cáo trở lại GitHub, quy định tối thiểu không khóa phương pháp.
- Liên kết entrypoint và danh mục cho mọi tác nhân; chuẩn bị `tasks/` cho các đặc tả tiếp theo.

- Tổ chức repository thành nguồn tri thức cho nhiều tác nhân với `AGENTS.md`, `STATE.md` và `CATALOG.yaml`.
- Thêm quy trình đóng góp, cấu trúc inventory/report/knowledge/runbook/decision/reference/archive và các mẫu tài liệu.
- Thêm trình kiểm tra repository để phát hiện metadata, liên kết, catalog hoặc dấu hiệu bí mật không hợp lệ.
- Chuẩn hóa tên file và chuyển báo cáo bảo mật có ngày từ `inventory/` sang `reports/`.
- Khởi tạo cấu trúc tài liệu vận hành cho repository.
- Ghi nhận kiểm kê trực tiếp VPS Hostinger sau khi xóa `CHUNG_KHOAN_PRO` và Alibaba OneTalk.
- Ghi nhận cấu hình n8n, Hermes Agent, Docker, PostgreSQL, Nginx, UFW, Fail2ban, SSH và sao lưu.
- Thêm đánh giá bảo mật và lộ trình cải thiện.
- Thêm quy tắc chống commit bí mật và script kiểm kê chỉ đọc.
