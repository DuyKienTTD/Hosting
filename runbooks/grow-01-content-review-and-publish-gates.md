# GROW-01 Content Review and Publish Gates

## Mục đích

Runbook này vận hành **nội dung draft/fake-only** cho TTD METAL theo chuỗi:

`idea -> approved brief -> approved assets -> draft script/storyboard -> human QA -> approved publish package -> scheduled/published by separately authorized connector -> performance feedback`

Runbook **không cấp quyền publish**. Nếu credential, quyền, claim hoặc asset rights chưa rõ thì nội dung phải dừng ở `BLOCKED` hoặc `NEEDS_REVIEW`.

## Trạng thái chuẩn

- `DRAFT`
- `NEEDS_REVIEW`
- `APPROVED`
- `BLOCKED`
- `PUBLISHED`

## Gate 1 — Idea intake

**Owner ưu tiên:** Hermes draft operator hoặc business coordinator
**Input tối thiểu:** objective, audience, region, funnel stage, channel dự kiến, source status
**Checklist:**
- mục tiêu có thật hay chỉ là giả thuyết `PROVISIONAL_FOR_BIZ02`
- không chứa dữ liệu khách hàng thật
- không yêu cầu publish/cost/render thật
- ghi rõ unknowns về giá, engineering, stock, legal claim

**Pass khi:** ý tưởng có mục tiêu, audience, channel và limit rõ ràng.
**Stop khi:** source mơ hồ, yêu cầu side effect, hoặc dùng claim chưa có nguồn.

## Gate 2 — Approved brief

**Reviewer bắt buộc:** business owner hoặc coordinator được giao
**Kiểm tra:**
- thông điệp có phù hợp ngành hàng trang trí/railing/modular decorative metal
- không hứa hẹn giá, discount, lead time, certification, warranty nếu chưa có nguồn
- không copy brand copy không được cấp quyền
- KPI chỉ ở dạng hypothesis nếu BIZ-02 chưa freeze

**Output:** brief được gắn `APPROVED` hoặc `NEEDS_REVIEW`.

## Gate 3 — Approved assets

**Kiểm tra quyền tài sản:**
- video/ảnh do nội bộ tạo hoặc có quyền dùng
- nhạc, voice, template, stock asset có license rõ ràng
- người xuất hiện trong hình/video có consent nếu nhận diện được
- placeholder synthetic asset phải ghi rõ placeholder

**Block ngay nếu:** thiếu rights, unclear consent, asset source không truy vết được.

## Gate 4 — Draft script/storyboard

**Owner:** Hermes hoặc người soạn draft
**Kiểm tra:**
- script tách rõ khỏi approved brand copy
- manufacturing/installation actions phải physically plausible
- mọi thông số kỹ thuật chưa được duyệt phải gắn `REQUIRES_PRODUCT_ENGINEER_APPROVAL`
- không có safety promise, structural certification, universal fit, ranking promise, guaranteed result

**Transition:** chỉ qua `human QA` nếu script/shot list hoàn chỉnh và đã gắn rõ unknowns/approval-needed fields.

## Gate 5 — Human QA

**Reviewers theo loại claim:**
- business claims -> business owner
- technical / install / safety -> product engineer
- rights / consent / music -> asset-rights reviewer
- channel copy / CTA -> marketing reviewer

**QA rubric tối thiểu:**
1. factual boundaries respected
2. rights/consent verified
3. CTA safe and non-deceptive
4. tracking names present
5. channel adaptation does not introduce new claims
6. all placeholders explicit

**Any FAIL =>** `BLOCKED` hoặc quay lại `DRAFT`.

## Gate 6 — Approved publish package

Một package chỉ được coi là `APPROVED` khi đủ:
- approved brief
- approved assets or approved placeholders for draft-only review
- approved script/storyboard
- QA pass signed by correct reviewers
- channel login/permission owner identified
- publish method identified (manual export hoặc connector tương lai)
- event/UTM naming present

Nếu thiếu bất kỳ mục nào ở trên, package không được rời `NEEDS_REVIEW/BLOCKED`.

## Gate 7 — Scheduled/published by separately authorized connector

**Không thuộc phạm vi Hermes GROW-01/S1.**
Chỉ diễn ra khi có:
- quyền account thật
- approval publish riêng
- connector/workflow đã được verify
- logging và rollback đã có

Nếu connector unavailable, dùng `MANUAL_EXPORT_ONLY` thay vì publish giả vờ.

## Gate 8 — Performance feedback

Thu thập read-only khi có quyền:
- impressions/views
- watch time / retention
- CTR / clicks
- lead form submits
- landing-page engagement
- source/medium/campaign event counts

Nếu account analytics chưa xác minh, ghi `UNVERIFIED_ACCOUNT_ACCESS` thay vì bịa số.

## Bảng STOP bắt buộc

| Điều kiện | Hành động |
|---|---|
| thiếu rights/consent | `BLOCKED`, không render/publish |
| có claim kỹ thuật chưa duyệt | gắn `REQUIRES_PRODUCT_ENGINEER_APPROVAL`, chặn publish |
| có giá/ưu đãi không có nguồn | xóa claim hoặc `BLOCKED` |
| credential/channel permission unknown | `MANUAL_EXPORT_ONLY` hoặc `BLOCKED` |
| cần API trả phí/render thật | dừng, không thực hiện trong GROW-01/S1 |
| package dùng dữ liệu khách hàng thật | loại bỏ dữ liệu, không tiếp tục |

## Evidence tối thiểu cần lưu

- source status của brief
- người duyệt từng lớp claim
- asset provenance / rights status
- version package
- mapping kênh và gating status
- JSON package ID trùng với report
- kết quả tabletop negative test nếu có blocker

## Rollback / recovery logic

Vì GROW-01/S1 là draft-only, rollback mặc định là:
1. giữ artifact Git đã commit,
2. đặt package về `BLOCKED` hoặc `NEEDS_REVIEW`,
3. ghi lý do fail/unknown,
4. không publish hoặc không giao connector thật.

## Khi tool/kênh không sẵn sàng

- **No channel login:** dùng mock channel mapping + manual export note.
- **No render tool:** dùng synthetic placeholder asset plan.
- **No product engineer:** mọi install/spec chi tiết giữ ở `REQUIRES_PRODUCT_ENGINEER_APPROVAL`.
- **No analytics access:** dùng KPI hypothesis và event naming only.
- **No rights proof:** dừng ở `BLOCKED`.

## Một dòng vận hành chuẩn

`Không rights rõ ràng, không claim được duyệt, không quyền channel thật => không APPROVED, không PUBLISHED.`
