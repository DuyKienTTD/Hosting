---
id: hermes-grow01-s2-d1-contract-remediation-2026-11-23
type: report
status: author-tested-offline-pending-independent-qa
updated_at: 2026-11-23
sensitivity: public-redacted
task_id: GROW-01/S2-D1
owner: hermes-webui
next_owner: chatgpt
---
# GROW-01/S2-D1 — sửa contract offline sau QA độc lập A1

**ACK:** `EXECUTE GROW-01/S2-D1`. [Lệnh #7093352519](https://github.com/DuyKienTTD/Hosting/pull/34#issuecomment-7093352519); [A1 QA #7093292211](https://github.com/DuyKienTTD/Hosting/pull/34#issuecomment-7093292211). PR #34 pre-HEAD `f7881d843b85d69c1f5ed6f6ff45e85ffac6541d`, `contract.py` blob `e65b74cd7443b657825f60f9f1ce07a3b9595827`, main `e385c1bea2070973e3007e5717f7e980348d6ab3`; PR #31 governance chưa merge. Quy tắc main `AGENTS.md`, workflow/security/STATE/CATALOG/Hermes profile tại cùng main; nguồn S1 PR #18, BIZ PR #25, UX PR #16, GROW02A PR #23, GOV A0 PR #27 ghim trong [evidence gốc](evidence/2026-11-23-hermes-grow01-s2-package-fixtures.json). Chỉ sửa code/schema/test của PR #34 và thêm report/evidence D1, không sửa S1/A0/shared metadata.

## Delta và error semantics

| Finding | Trước (A1 thực thi) | Sau (Hermes tự test offline) |
|---|---|---|
| F01 — READY giả và 5 status tự gán | `APPROVED_FOR_OFFLINE_HANDOFF` dù log rỗng | `INVALID_PROVENANCE`, không thêm entry; `MockLedger` giữ snapshot fixture, check equality trước replay/transition. Direct approved-state/owner field giả bị từ chối. |
| F01 — log review có vẻ hợp lệ nhưng tự chế | Không được kiểm trước QA | `validate()` chỉ kiểm cấu trúc/history; `transition()` cần **MockLedger nội bộ** và trả `UNTRUSTED_STATE` nếu snapshot không khớp. Dict tùy ý cũng `UNTRUSTED_STATE`. Mọi log hiện bind `package_id/revision/content_digest/role/action/idempotency_key/review_tokens` ở mức mock; fork đăng ký revision mới, reset mọi review. |
| F02 — external asset/unknown keys | `validate()` chấp nhận | `INVALID_FIELD` cho nested/top-level property lạ, asset khác `synthetic_placeholder/UNVERIFIED`, URI và source_ref không thuộc fixture. `transition()` gọi cùng validator trước mutation. |
| F03 — NaN/type/HTML note | native `ValueError`, hoặc HTML note được nhận | typed `ContractError('INVALID_FIELD')`; ở **mock này** cấm `<`, `>` và `&` trong `content_note`. Không có renderer; mọi UI tương lai vẫn phải escape theo ngữ cảnh. |

`MISSING_FIXTURE_REVIEW` khi thiếu một trong năm token; `SELF_APPROVAL` nếu editor tự gọi owner action; `STALE_REVISION`, `STALE_DIGEST`, `KEY_COLLISION`, `UNKNOWN_CALLBACK`, `FORBIDDEN_SIDE_EFFECT` giữ nguyên. `BAD_DIGEST`/`OVERSIZE` cho digest mismatch / package >16384 UTF-8 bytes. Transition dựng bản sao, validate rồi mới cập nhật package và ledger, nên lỗi không mutate. Canonical JSON giữ `sort_keys`, compact, Unicode và `allow_nan=False`.

**Giới hạn rất quan trọng:** `MockLedger` là đối tượng Python trong memory, khởi tạo từ ba fixture; các method của nó và state trong cùng process **không có ranh giới an ninh** chống code Python độc hại. Role/token `*-fixture` không xác thực danh tính, chữ ký, quyền asset/consent, product engineer signoff hay quyết định A0. `validate()` **không** là phép xác thực provenance độc lập: log giả với cấu trúc hợp lệ có thể qua `validate()`, nhưng bị `transition()` chặn nếu không tồn tại trong snapshot ledger. API gọi `fork_revision(..., ledger)` là breaking change so với S2 ban đầu; ngoài mock này cần server IAM, authenticated actor, durable append-only ledger/atomic revision và escrow/rights verification trước bất kỳ integration. Schema JSON chỉ là proposal; nó không tự thực thi trusted-state/cross-field equality/byte-bound, và không chạy bằng engine. Bản report S2 và evidence 15/15 cũ là **snapshot lịch sử**, không phải minh chứng QA độc lập hay tài liệu runtime D1 hiện hành.

## Kiểm thử, provenance và bàn giao

RED trước sửa: trên source cũ + 6 test A1 vừa thêm, **21 ca: 15 PASS, 5 FAIL, 1 ERROR** (NaN native `ValueError`). Sau delta, `python3 -B -m unittest discover -s sandbox/grow01-package-contract -p test_contract.py -v` cho **31/31 PASS** tác giả chạy offline. Bốn test cũ #03–#06 được đổi setup: không còn tự tạo READY bằng field mutation, mà đi qua `submit_review`/`mark_ready` và kiểm thiếu token/self-approval; không mạo nhận chúng nguyên dạng so với historical suite 15/15. Có thêm sáu A1 probes và 10 ca regression/safety, gồm forged plausible log, tampering sau review, nested asset, malformed type, raw dict ledger, fork revision, atomic token failure, Unicode/16384 bytes và drift. [Evidence theo từng case](evidence/2026-11-23-hermes-grow01-s2-d1-contract-remediation.json) chứa expected/observed, Python/platform, blobs code/test/schema, 0 side effects. P1/P2/P3 evidence gốc giữ nguyên DRAFT/UNVERIFIED; năm A0 vẫn `AWAITING_A0_DECISION`.

**Verdict:** `GROW01_S2_D1_AUTHOR_TESTS_PASS_OFFLINE_PENDING_INDEPENDENT_QA`. Không publish, paid API, HTTP, browser/UI E2E, real IAM, VPS hay Codex. Cần A1/Work re-QA trên đúng PR34 post-HEAD, đặc biệt xem giới hạn mô phỏng của `MockLedger` và việc schema proposal khác runtime. `TASK=GROW-01/S2-D1 | AGENT=Hermes | ACK=ACKNOWLEDGED | PR34_PRE_HEAD=f7881d843b85d69c1f5ed6f6ff45e85ffac6541d | PR34_POST_HEAD=see linked commit | F01=mock provenance checked | F02=runtime boundary fail-closed | F03=typed errors + mock rejects markup | TEST_COUNT=31/31 author offline | EVIDENCE=reports/evidence/2026-11-23-hermes-grow01-s2-d1-contract-remediation.json | VERDICT=GROW01_S2_D1_AUTHOR_TESTS_PASS_OFFLINE_PENDING_INDEPENDENT_QA | NEXT_OWNER=ChatGPT Điều phối → A1/Work independent re-QA`.
