---
id: hermes-grow01-s2-package-contract-2026-11-23
type: report
status: draft-ready-for-review
updated_at: 2026-11-23
sensitivity: public-redacted
task_id: GROW-01/S2
owner: hermes-webui
next_owner: chatgpt
---
# GROW-01/S2 — Hợp đồng bàn giao package nội dung offline

## ACK / provenance / giới hạn

Nhận [lệnh PR #18 #7092051626](https://github.com/DuyKienTTD/Hosting/pull/18#issuecomment-7092051626). Base `origin/main@e385c1bea2070973e3007e5717f7e980348d6ab3`; nguồn S1 [PR #18@3c8cb40](https://github.com/DuyKienTTD/Hosting/commit/3c8cb40357ee23d13a2c1aa7e07e6848ff5256dd); BIZ-02/S2 [PR #25@6b2a770](https://github.com/DuyKienTTD/Hosting/pull/25); GOV-01/S2 [PR #27@b8c6465](https://github.com/DuyKienTTD/Hosting/pull/27); UX-01/S2 [PR #16@9a629fb](https://github.com/DuyKienTTD/Hosting/pull/16); GROW-02A [PR #23@f2f092a](https://github.com/DuyKienTTD/Hosting/pull/23). Quy tắc main và hồ sơ Hermes đã đọc; Git SSH push sẵn, GitHub browser PR write chưa xác minh. Không có S2 branch/path trùng tại checkpoint. Chỉ thiết kế và chạy stdlib Python trên fixture; **không có server, browser integration, quyền tài sản, xác nhận kỹ thuật, publish, API thật, chi phí hoặc quyền A0**.

## Package schema v0-proposal

[Schema JSON](../sandbox/grow01-package-contract/schema-v0-proposal.json) định nghĩa required: `package_id, source_ref, source_sha, revision, language, target_channel, asset_refs, asset_rights_status, technical_review_status, marketing_review_status, owner_approval_status, consent_status, channel_status, proposed_cost, state, decision_log, idempotency_key, content_digest, created_at_utc, updated_at_utc, content_note`. Optional trong v0: không có field tự do; `idempotency_key` và `proposed_cost` nhận null (cost luôn null trong mock); `decision_log` mảng. `asset_refs` chỉ placeholder synthetic (không phải asset thật/URI). JSON Schema là **đặc tả, chưa chạy bằng JSON Schema engine**; Python validator kiểm tập con semantic và kích thước canonical toàn package tối đa **16384 UTF-8 bytes**. Interface không cấp thực quyền qua trạng thái field.

- `package_id` giữ ID P1/P2/P3 đã có, ASCII và cố định; `source_ref` là path+anchor của S1, `source_sha` ghim commit 40 hex, revision int >=1. `content_digest` SHA-256 của UTF-8 JSON canonical (`sort_keys`, compact separators, `ensure_ascii=False`, `allow_nan=False`) trên `package_id/source_ref/source_sha/revision/language/target_channel/asset_refs/content_note`; status/review log và timestamp **không nằm trong digest**. Đây là integrity mock, không phải chữ ký xác thực. `fork_revision` tăng revision, đổi note, tính lại digest và hủy mọi review. Không cho edit in-place bỏ qua fork; trong backend tương lai phải thực thi immutable revision/digest atomically.
- `created_at_utc`/`updated_at_utc` trong fixture là mốc giả cố định `2026-11-23T00:00:00Z`, không phải thời điểm sự kiện kinh doanh; event ledger durable/real timestamps chưa có. Log chỉ lưu alias role, action, digest, revision, scope synthetic; không lưu PII/credential. UI cần escape/encode mọi chuỗi, không render raw HTML; redaction loại customer text, exact asset, secret và bản ghi consent thật. Không dùng ID fixture làm identity thực.
- S1 có status_model `APPROVED/PUBLISHED` như lifecycle tương lai; S2 tách riêng `APPROVED_FOR_OFFLINE_HANDOFF` (mock package only). S1 F5 `APPROVED` là fixture, không hề duyệt P1–P3; cả ba bản ghi S2 vẫn `DRAFT`/`UNVERIFIED`. P2 instruction lắp đặt vẫn cần product engineer, P3 privacy/form copy vẫn cần owner; các claim gốc chỉ tham chiếu SHA/path, **không viết lại nội dung**.

| Package nguồn | Ngôn ngữ/kênh đề xuất, không phát hành | trạng thái S2 | Rào cản |
|---|---|---|---|
| `P1-short-vi-craftsmanship` | `vi / youtube_shorts` | `DRAFT` | footage/music/worker consent và channel owner UNVERIFIED |
| `P2-install-howto-en` | `en / youtube_video` | `DRAFT` | rights UNVERIFIED; hardware/installation engineer signoff thiếu |
| `P3-landing-brief-envi` | `en-vi / wordpress_page` | `DRAFT` | image/copy privacy/form/claims và WP owner UNVERIFIED |

## State machine và cổng chuyển

| From → To (action) | Vai trò *giả lập* / guard | Kết quả nếu thiếu |
|---|---|---|
| `DRAFT → IN_REVIEW` (`submit_review`) | `editor`, exact revision/digest, unique idempotency key | `STALE_*`/`ROLE_FORBIDDEN`, no mutation |
| `IN_REVIEW → NEEDS_CHANGES` (`request_changes`) | `reviewer`, exact revision/digest | hold; sửa nội dung chỉ qua `fork_revision` → new `DRAFT` |
| `IN_REVIEW → READY_FOR_OWNER_REVIEW` (`mark_ready`) | reviewer role và **năm fixture review tokens** riêng rights/technical/marketing/consent/channel | `MISSING_FIXTURE_REVIEW`; không thay quyền thực |
| `READY_FOR_OWNER_REVIEW → APPROVED_FOR_OFFLINE_HANDOFF` (`decide_owner`) | owner role khác editor, exact revision/digest; tất cả fixture reviews `VERIFIED_FIXTURE` | `RIGHTS_UNVERIFIED`, `TECHNICAL_UNVERIFIED`, `CHANNEL_UNVERIFIED`...; no publish |
| `IN_REVIEW → BLOCKED` (`block`), `READY_FOR_OWNER_REVIEW → REJECTED` (`reject`) | reviewer hoặc owner theo nhánh | stop với audit giả, không external callback |
| mọi state → publish/upload/schedule/paid_render | **Không có transition** trong S2 | `FORBIDDEN_SIDE_EFFECT` |

Callback thiếu/lộn thứ tự/unknown → `UNKNOWN_CALLBACK`, không tạo approval hay tự retry. Idempotency key gắn với `package_id`, action, role, revision/digest và review tokens; replay cùng request trả snapshot cũ, key trùng payload khác → `KEY_COLLISION`. **Ledger in-memory**, không durable, concurrency/multi-user chưa có. Role gửi từ client là input của mock, **không phải xác thực server**; Codex phải triển khai server-side identity, authorization/segregation of duties, atomic revision/receipt binding, durable ledger, callback provenance trước triển khai; UX selector không thể là authority.

## Offline UI handoff interface — đề xuất, không có HTTP transport

Tất cả ví dụ sau là request/response **in-process mock** và chỉ chứa ID giả. Định dạng response đề xuất `{status, package, receipt, error}`; status lỗi là code hợp đồng, không phải HTTP code đã vận hành. `get_package({package_id:"P2-install-howto-en", revision:1}) → {status:"OK_OFFLINE",package:{state:"DRAFT",source_sha:"3c8cb40...",asset_rights_status:"UNVERIFIED"},receipt:null}`. `list_packages({state:"DRAFT"}) → {status:"OK_OFFLINE",package_ids:["P1-short-vi-craftsmanship","P2-install-howto-en","P3-landing-brief-envi"]}`.

| Operation | Request bắt buộc | Response / error chính | Chủ quyền còn thiếu |
|---|---|---|---|
| `get_package` | package_id, revision optional | `OK_OFFLINE` hoặc `NOT_FOUND`, không trả nội dung PII | server resource auth |
| `list_packages` | state filter optional | chỉ metadata và source watermark, `BAD_FILTER` | workspace/role filters |
| `submit_review` | package_id, expected_revision, expected_digest, idempotency_key, actor_role=`editor` | `IN_REVIEW` + mock audit / `STALE_REVISION`, `STALE_DIGEST`, `ROLE_FORBIDDEN` | authenticated actor, durability |
| `decide_review` | package_id, action=`request_changes/mark_ready/decide_owner/block/reject`, role, expected revision/digest, key, fixture tokens chỉ cho mark_ready | state + mock audit / `MISSING_FIXTURE_REVIEW`, `SELF_APPROVAL`, `KEY_COLLISION`, `FORBIDDEN_SIDE_EFFECT` | signed reviewer identity, distinct owner, real rights |
| `fork_revision` | package_id, editor role, synthetic content_note | new revision=`2`, state=`DRAFT`, review reset / `BAD_FORK` | atomic compare-and-swap and audit |
| `get_audit` | package_id, revision | synthetic decision_log, not production proof / `NOT_FOUND` | redaction, retention, server audit |

Ví dụ `submit_review({package_id:"P2-install-howto-en",expected_revision:1,expected_digest:"<64-hex from fixture>",idempotency_key:"draft-p2-01",actor_role:"editor"}) → {status:"IN_REVIEW",receipt:{scope:"SYNTHETIC_OFFLINE_ONLY",action:"submit_review"},error:null}`. `decide_review({package_id:"P2-install-howto-en",action:"decide_owner",actor_role:"owner",expected_revision:1,expected_digest:"<same fixture digest>",idempotency_key:"owner-p2-01"}) → {status:"BLOCKED",package:null,receipt:null,error:"RIGHTS_UNVERIFIED"}`; trạng thái gốc không bị đổi. Audit canonical synthetic ví dụ `{package_id:"P2-install-howto-en",revision:1,content_digest:"<fixture SHA256>",action:"submit_review",actor_role:"editor",at_utc:"2026-11-23T00:00:00Z",scope:"SYNTHETIC_OFFLINE_ONLY"}`. Chuỗi `<...>` là placeholder trong tài liệu, không phải digest thực hay signed receipt.

## Traceability và độc lập nghiệm thu

| P1–P3 → BIZ-02/S2 | UX #16 screen/control | GROW-02A #23 event name đề xuất | A0 #27 | Giới hạn |
|---|---|---|---|---|
| Cả 3 P1/P2/P3 → **J4** bilingual draft/reviewer; **J1** approval queue chỉ kề bên, không có E2E nối | C16 Content draft/channel, C17 Media review, C18 Publish locked, C08 approval queue | `content_draft_submitted`, `content_review_decided`, `publish_handoff_requested` (không emit thật) | A0-1, A0-4, A0-5 `AWAITING_A0_DECISION` | `CONTRACT_READY_FOR_REVIEW`; `UI_INTEGRATION_NOT_RUN`; `SERVER_AUTH_UNIMPLEMENTED`; `REAL_PUBLISH_BLOCKED` |

A0-2/A0-3 cũng tiếp tục pending trong [GOV register #27](https://github.com/DuyKienTTD/Hosting/pull/27); S2 không đổi bất kỳ câu hỏi/trạng thái/quyền nào. UX #16 browser E2E chưa xác minh; đây **không** phải backend hay UI integration. Sau review, ChatGPT Điều phối có thể giao Work chạy browser fixture J4/C16–C18/C08, rồi Codex kiểm backend contract IAM/durable ledger trong nhiệm vụ riêng; đây chỉ là khuyến nghị, chưa giao task cho họ.

## Kiểm thử và bàn giao

Đã chạy `python3 -B -m unittest discover -s sandbox/grow01-package-contract -p test_contract.py -v`: **15/15 PASS** tại worktree local, gồm DRAFT→review, thiếu rights/technical/channel, self approval, stale digest/revision, replay/key conflict, fork invalidation, publish/paid blocked, unknown callbacks, role giả mạo, mock owner sequence và canonical audit. [Evidence JSON](evidence/2026-11-23-hermes-grow01-s2-package-fixtures.json) ghi exact source SHA/blob, test cases/expected/observed, Python/platform và source-code blob. Một lần chạy trước đó fail do hai test setup không thỏa state/key format; đã sửa fixture test và chạy lại đạt, không giấu lỗi lịch sử. Không chạy lại suite S1, không gọi API/production.

**Verdict:** `GROW01_S2_OFFLINE_PACKAGE_CONTRACT_PASS_READY_FOR_REVIEW` áp dụng **source+fixture local**, không phải IAM thật, durable handoff, browser E2E hay quyền publish. `NEXT_OWNER=ChatGPT Điều phối` để rà nội dung, Work review giao diện và Codex đánh giá backend gate nếu được giao. `TASK=GROW-01/S2 | AGENT=Hermes | ACK=ACKNOWLEDGED | BASE_SHA=e385c1bea2070973e3007e5717f7e980348d6ab3 | SOURCE_SHAS=PR18/25/27/16/23 in JSON | PACKAGE_SCHEMA=v0-proposal | STATE_MACHINE=7 states/no PUBLISHED | ACTUAL_TESTS=15/15 offline | EVIDENCE=reports/evidence/2026-11-23-hermes-grow01-s2-package-fixtures.json | VERDICT=GROW01_S2_OFFLINE_PACKAGE_CONTRACT_PASS_READY_FOR_REVIEW | PR_URL=if available; otherwise compare URL | NEXT_OWNER=ChatGPT Điều phối`.
