---
id: hermes-grow-01-s1-media-workflow-2026-11-23
type: report
status: complete
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
task_id: GROW-01/S1
source: pr12-execute-comment,biz01-accepted-package,repo-rules-and-state,repo-product-context,synthetic-draft-content,session-capability-checks
---

# GROW-01/S1 — TTD METAL content and media workflow design

## 1. ACK thực thi

- **TASK_ID:** `GROW-01/S1`
- **ACK_EXECUTE:** `EXECUTE GROW-01/S1`
- **Agent / session:** Hermes WebUI, profile `default`
- **HANDOFF_STATE trong phiên Hermes:** `ACKNOWLEDGED -> IN_PROGRESS -> DONE`
- **Assignment source:** <https://github.com/DuyKienTTD/Hosting/pull/12#issuecomment-7090773585>
- **Assignment type:** PR comment handoff, not merge approval
- **MAIN_SHA đã review và dùng làm base branch:** `e385c1bea2070973e3007e5717f7e980348d6ab3`
- **ASSIGNMENT_SHA dùng lại cho package BIZ-01 đã được nghiệm thu:** `8c821bbf1842eccb8519127f54ba7673965276d5`
- **Rule/state/profile đã đọc trước khi làm:** `AGENTS.md`, `PROJECT.md`, `GOALS_AND_ROADMAP.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/README.md`, `agents/hermes.md`
- **Kết quả BIZ-01 đã tái sử dụng, không khảo sát lại:** `reports/2026-11-23-hermes-biz-01-channel-capability-matrix.md` + JSON evidence tại commit `8c821bb...`
- **Công cụ/quyền thực tế trong phiên:** Git read/write qua SSH cho repo này, file/terminal/web tools; **không có** quyền connector/account live được xác minh cho publish, Ads, analytics, WordPress write, social login hoặc media render.
- **FIRST_ACTION thực tế:** fetch `origin/main`, đọc lại rules/state/profile, lấy đặc tả từ PR #12 comment `7090773585`, kiểm tra repo xem đã có deliverable `GROW-01` hay branch xung đột chưa.
- **Giới hạn được giữ nguyên:** draft/fake-only, no paid API, no publish, no production/account mutation, no credential setup, no rewrite of BIZ-01.

## 2. Bối cảnh đã xác minh từ repo

### 2.1 Điều đã biết và có thể dựa vào

- `wroughtiron.shop` là website WordPress đã được xác minh trong inventory account Hostinger.
- Có thêm `staging.wroughtiron.shop` trong WordPress inventory.
- Hostinger Reach `1000` được xác minh gắn với `wroughtiron.shop`.
- Bốn dịch vụ email Hostinger đang hoạt động: `nepdong.com`, `nepdong.top`, `qtcty.com`, `thuanthanhdat.com`.
- Dự án TTD METAL ưu tiên media, quảng cáo, website/SEO, social và reporting theo `PROJECT.md`.

### 2.2 Điều **không** được giả định

- Không có price book được duyệt trong repo.
- Không có bảng thông số kỹ thuật/safety/certification được duyệt trong repo.
- Không có bằng chứng live về login/account access cho YouTube, TikTok, Meta, GA4, Ads, WordPress write, HeyGen, ElevenLabs hoặc Kling trong phiên Hermes này.
- Không có bằng chứng cho phép xuất bản nội dung thật, render media trả phí hoặc gửi contact thật.

Vì vậy mọi package trong gói này phải giữ các trường như giá, tồn kho, warranty, torque, khoảng cách neo, chứng chỉ kết cấu, universal fit và ranking promise ở trạng thái `UNKNOWN`, `BLOCKED` hoặc `REQUIRES_PRODUCT_ENGINEER_APPROVAL` khi phù hợp.

## 3. SOP vòng đời editorial / asset

Chuỗi chuẩn được thiết kế như sau:

`idea -> approved brief -> approved assets -> draft script/storyboard -> human QA -> approved publish package -> scheduled/published by separately authorized connector -> performance feedback`

### 3.1 Bảng vận hành

| Stage | Owner chính | Trigger | Inputs chính | Validation | Transition criteria | Approval gate | Evidence / audit | Stop / rollback | Khi tool không sẵn |
|---|---|---|---|---|---|---|---|---|---|
| `idea` | Hermes draft operator hoặc coordinator | có giả thuyết growth mới | objective, audience, region, funnel, channel_guess, source_status | không dùng dữ liệu khách hàng thật; không yêu cầu side effect; unknowns được đánh dấu | đủ khung brief | business scope check | idea_id, source_status, created_at | dừng nếu source mơ hồ hoặc đòi cost/publish | nhập brief thủ công |
| `approved brief` | business owner / coordinator | idea đã hình thành | message angle, KPI hypothesis, CTA boundary | không có giá bịa, ranking promise, unsupported claim | brief = `APPROVED` hoặc `NEEDS_REVIEW` | business claim signoff | reviewer, decision, revision notes | trả lại `DRAFT` | review trên Markdown |
| `approved assets` | asset-rights reviewer | brief được chấp thuận | asset list, provenance, rights, consent | traceable rights; consent known; placeholder được gắn nhãn | assets có decision rõ | rights/IP gate | asset_id, rights_status | `BLOCKED` nếu thiếu rights | placeholder-only draft |
| `draft script/storyboard` | Hermes / drafter | brief + asset plan sẵn | brief, asset plan, channel format, language | hành động phải plausible; thông số chưa duyệt phải gắn approval | script + shot list đầy đủ | technical sensitivity check | version, language, placeholder markers | về `DRAFT` nếu có forbidden claim | text-only storyboard |
| `human QA` | business + kỹ thuật + rights reviewers | draft hoàn chỉnh | script, shot list, claim map, rights map, tracking names | claim review, rights review, CTA review, tracking review | tất cả reviewer pass | multi-role signoff | QA result, issues | `BLOCKED` hoặc quay lại `DRAFT` | checklist thủ công |
| `approved publish package` | coordinator | QA pass | approved brief/assets/script, channel mapping, tracking names | owner channel được xác định; publish path được xác định; không còn claim chưa duyệt | package complete | publish readiness check | package_id, approval summary | `NEEDS_REVIEW` nếu thiếu field | `MANUAL_EXPORT_ONLY` |
| `scheduled/published by separately authorized connector` | publisher / connector được cấp quyền riêng | có publish approval riêng | approved package + credential + connector | connector verified, logging enabled | nội dung thật sự được lên lịch/xuất bản | external side-effect authorization | publish_id, scheduled_at | **ngoài phạm vi GROW-01/S1** | manual export only |
| `performance feedback` | analytics/reporting owner | nội dung live | channel metrics, event counts | source/medium integrity; analytics access verified | feedback loop documented | read-only data sufficiency | views/clicks/leads/notes | `UNKNOWN` nếu chưa có analytics access | import thủ công sau |

## 4. Approval matrix và asset governance

### 4.1 Status model

- `DRAFT`
- `NEEDS_REVIEW`
- `APPROVED`
- `BLOCKED`
- `PUBLISHED`

### 4.2 Ai duyệt cái gì

| Hạng mục | Người/phần duyệt bắt buộc | Lý do |
|---|---|---|
| Business claims / offer framing | business owner | tránh hứa giá, discount, SLA, promise không có nguồn |
| Technical / install / safety claim | product engineer | tránh bịa torque, khoảng cách neo, universal fit, structural certification |
| Music / footage / design rights | asset-rights reviewer | tránh false reuse, copyright và music-license vi phạm |
| Consent / privacy / retention | privacy-compliance reviewer hoặc owner delegate | tránh dùng mặt người/dữ liệu khách hàng không có phép |
| Channel login / permission | account owner | BIZ-01 chưa xác minh live account access |
| Cost / render execution | budget owner | không mở paid render ngoài phạm vi |
| Final publication | separately authorized publisher | GROW-01/S1 không có publish approval |

### 4.3 Default deny rule

Nếu bất kỳ mục nào sau đây là `UNKNOWN`, package **không được** đi tiếp đến `APPROVED/PUBLISHED`:

1. rights/consent,
2. technical approval,
3. business claim approval,
4. channel permission,
5. cost/render approval.

## 5. Ba gói nội dung mẫu

Tất cả package bên dưới đều là **synthetic draft**, distinct from approved brand copy, không dùng dữ liệu khách hàng thật và không hứa hẹn ngoài nguồn.

---

## 5.1 Package P1 — Vertical short tiếng Việt về craftsmanship

- **Package ID:** `P1-short-vi-craftsmanship`
- **Audience / region:** Việt Nam; homeowner, kiến trúc sư, người đang xem short-form video về chi tiết hoàn thiện nội thất/ngoại thất.
- **Objective / KPI:** `PROVISIONAL_FOR_BIZ02` — kiểm thử giả thuyết nội dung xưởng/thủ công có thể tạo engagement và tò mò đủ điều kiện cho bước hỏi thêm.
- **Funnel stage:** top-mid funnel.
- **Format:** vertical `9:16`, `15–30s`.
- **Hook:** `Từ thép thô đến chi tiết hoàn thiện: 20 giây nhìn vào nhịp làm việc của xưởng.`

### Script draft

1. `0–3s` — cận cảnh thước đo, phấn dấu, thép được đặt lên bàn gia công. Text: `Một chi tiết đẹp bắt đầu từ bước đo chuẩn`.
2. `3–8s` — cắt, làm sạch mép, thử ráp khô module trang trí. Text: `Đo, cắt, thử ráp trước khi hoàn thiện bề mặt`.
3. `8–14s` — người thợ kiểm tra đường nét và bề mặt. Text: `Tập trung vào độ đều, độ sạch và tính đồng bộ`.
4. `14–20s` — close-up chi tiết hoàn thiện. Text: `Nội dung này mô tả quy trình thủ công ở mức draft, không phải cam kết kỹ thuật`.
5. `20–25s` — CTA mềm: `Muốn xem thêm ý tưởng ứng dụng cho không gian của bạn? Theo dõi để xem bản demo tiếp theo.`

### Visual / shot list

- macro đo kích thước và đánh dấu,
- cắt hoặc chuẩn bị cắt với framing an toàn,
- thử ráp khô module trang trí,
- làm sạch bề mặt / kiểm tra detail,
- close-up chi tiết hoàn thiện trên nền trung tính.

### Required assets / permissions

- footage nội bộ hoặc placeholder synthetic clips,
- nhạc có quyền hoặc version không nhạc,
- consent nếu lộ mặt người thật.

### Forbidden claims

- guarantee về độ bền hoặc chứng nhận an toàn,
- promise cho khách hàng không có nguồn,
- giá, lead time, warranty, installation outcome,
- mô tả footage là production thật nếu đang dùng placeholder.

### QA rubric

- thao tác phải physically plausible,
- không có safety promise,
- source/placeholder status rõ,
- CTA không lừa dối.

### Publish gate

Cần business review + asset-rights review + channel owner rõ trước khi có bất kỳ export/publish ngoài draft.

### Tracking proposal

- `utm_source`: `youtube_shorts` / `tiktok` / `facebook_reels`
- `utm_medium`: `organic_short_video`
- `utm_campaign`: `prov_biz02_craftsmanship_series`
- `event_name`: `short_craftsmanship_hook_click`

### Channel adaptations

- **YouTube Shorts:** overlay ngắn, có thể thêm EN subtitle sau.
- **TikTok:** mở bằng cut nhanh hơn, khung đầu tiên nổi bật hơn.
- **Facebook Reels:** caption có thể chuyển từ `follow` sang `xem thêm / hỏi thêm` nếu owner duyệt.

### Version / source status

- **Version:** `v0.1-draft`
- **Source status:** synthetic draft từ bối cảnh repo; không tái sử dụng approved brand copy.

---

## 5.2 Package P2 — English installation/how-to draft

- **Package ID:** `P2-install-howto-en`
- **Audience / region:** English-speaking homeowners, installers, resellers.
- **Objective / KPI:** `PROVISIONAL_FOR_BIZ02` — communicate install-planning logic without pretending to be certified structural guidance.
- **Funnel stage:** mid funnel.
- **Format:** `9:16` or `16:9`, about `30s`.
- **Hook:** `Planning a decorative railing module install? Start with fit, layout, and review — not assumptions.`

### Script draft (English)

1. `0–5s` — `Before any fasteners go in, confirm your opening, layout, and approved module dimensions.`
2. `5–10s` — `Dry-fit the decorative section and check spacing, orientation, and visual alignment.`
3. `10–16s` — `Mark anchor points only after the product engineer or approved drawing confirms the mounting approach.`
4. `16–22s` — `Fastener type, spacing, torque, substrate suitability, and load requirements: REQUIRES_PRODUCT_ENGINEER_APPROVAL.`
5. `22–27s` — `Do not treat this draft as a structural instruction or universal-fit guarantee.`
6. `27–30s` — `Use the approved site-specific drawing and hardware checklist before installation.`

### Visual / shot list

- measuring the opening,
- dry-fit of module,
- alignment check with level/straightedge,
- close-up note `REQUIRES_PRODUCT_ENGINEER_APPROVAL`,
- placeholder approved-drawing/checklist frame.

### Required assets / permissions

- approved product drawing or synthetic placeholder drawing,
- installer consent if identifiable,
- rights-cleared music or silent version.

### Forbidden claims

- exact torque values,
- structural certification,
- universal fit,
- code-compliance or warranty claim without approved source.

### QA rubric

- exact technical specs remain gated,
- wording stays planning-oriented,
- no universal fit or safety guarantee.

### Publish gate

Không được lên `APPROVED` nếu chưa có product engineer signoff cho mọi technical instruction và business owner signoff cho framing public.

### Tracking proposal

- `utm_source`: `youtube` / `meta_video`
- `utm_medium`: `organic_howto_video`
- `utm_campaign`: `prov_biz02_install_planning_en`
- `event_name`: `install_guide_cta_click`

### Channel adaptations

- **YouTube:** có thể thêm chapter markers sau khi duyệt.
- **Meta video:** giữ disclaimer trên màn hình lâu hơn.
- **Website embed:** ghép cùng FAQ/CTA xin bản vẽ hoặc review bản vẽ.

### Version / source status

- **Version:** `v0.1-draft`
- **Source status:** English draft guidance only; exact install specs intentionally withheld pending engineer approval.

---

## 5.3 Package P3 — EN/VI landing-page / SEO brief

- **Package ID:** `P3-landing-brief-envi`
- **Audience / region:** Việt Nam + visitor/inquiry quốc tế.
- **Objective / KPI:** `PROVISIONAL_FOR_BIZ02` — tăng khả năng lead capture và clarity cho nội dung landing page/SEO về modular decorative railing.
- **Funnel stage:** mid-bottom funnel.
- **Format:** EN/VI article or landing-page brief.
- **Hook:** `A modular decorative railing page should answer fit, style, process, and inquiry questions without inventing price or certification claims.`

### Suggested page sections

1. **Hero**
   - EN: `Decorative railing modules for custom projects`
   - VI: `Giải pháp module lan can trang trí cho công trình theo yêu cầu`
2. **Use-case overview** — style direction, không hứa outcome kỹ thuật.
3. **Modular design logic** — khi nào module giúp việc phối hợp thiết kế/thi công dễ hơn.
4. **Detail and finish explanation** — mô tả dạng craftsmanship/process, không claim chứng nhận.
5. **Inquiry CTA** — mời gửi kích thước sơ bộ, ảnh tham khảo, phong cách mong muốn.
6. **FAQ** — fit, style, review flow, what requires engineer approval.
7. **Gallery / proof placeholders** — chỉ là placeholder nếu chưa có asset rights approved.

### Keyword intent hypotheses

- **EN:** `decorative railing modules`, `modular wrought iron railing`, `custom baluster panel`, `decorative railing for stairs`
- **VI:** `module lan can trang trí`, `lan can sắt mỹ thuật lắp ghép`, `con tiện sắt trang trí`, `lan can cầu thang sắt nghệ thuật`

### Customer-question hypotheses

- `Can the style be adapted to my space?`
- `What should I prepare before requesting a quote or drawing review?`
- `Which details require engineering confirmation before installation?`
- `How should I share reference images or dimensions?`

### Required assets / permissions

- rights-cleared gallery images or placeholders,
- bilingual copy review,
- reviewed form/privacy text.

### Forbidden claims

- fixed pricing,
- stock availability,
- delivery guarantee,
- SEO ranking promise,
- certification or universal-compliance claim.

### QA rubric

- EN/VI copy giữ cùng boundary về claim,
- CTA không giả định quote tức thì nếu chưa owner-duyệt,
- keyword ideas chỉ là hypothesis.

### Publish gate

Business owner phải duyệt claim + legal/privacy text + lead capture handling trước khi package được `APPROVED`.

### Tracking proposal

- `utm_source`: `organic_search` / `shorts_referral` / `email_reach`
- `utm_medium`: `landing_page`
- `utm_campaign`: `prov_biz02_modular_railing_landing`
- `event_name`: `lead_form_start_modular_railing`

### Channel adaptations

- **WordPress page:** đích triển khai tương lai nếu claim + credential được duyệt.
- **SEO article:** mở rộng FAQ/process explanation.
- **Email Reach teaser:** route về landing page khi account + consent path được duyệt.

### Version / source status

- **Version:** `v0.1-draft`
- **Source status:** bilingual content brief only; prices, stock, certification and final SEO targets remain unknown.

## 6. Channel feasibility mapping từ BIZ-01

### 6.1 Package P1

| Channel / tool | Mapping | Ghi chú |
|---|---|---|
| YouTube Shorts | `DOCUMENTED + UNVERIFIED_ACCOUNT_ACCESS` | docs có, account chưa verify |
| TikTok | `DOCUMENTED + UNVERIFIED_ACCOUNT_ACCESS` | docs có, publish thật cần account/app approval |
| Meta Reels | `DOCUMENTED + UNVERIFIED_ACCOUNT_ACCESS` | docs có, Page/token chưa verify |
| HeyGen | `DOCUMENTED + UNVERIFIED_ACCOUNT_ACCESS` | draft-only pipeline planning |
| ElevenLabs TTS | `DOCUMENTED + UNVERIFIED_ACCOUNT_ACCESS` | không render thật |
| Kling | `DOCUMENTED + UNVERIFIED_ACCOUNT_ACCESS` | không render thật |

**Future step required:** owner account OAuth/login, rights-cleared assets, manual export hoặc connector thật ở phase sau.

### 6.2 Package P2

| Channel / tool | Mapping | Ghi chú |
|---|---|---|
| YouTube video | `DOCUMENTED + UNVERIFIED_ACCOUNT_ACCESS` | publish thật chưa được phép |
| Meta video | `DOCUMENTED + UNVERIFIED_ACCOUNT_ACCESS` | publish thật chưa được phép |
| WordPress embed/page | `DOCUMENTED + VERIFIED_IN_PROJECT + UNVERIFIED_ACCOUNT_ACCESS` | site có thật trong inventory nhưng write access chưa verify |

**Future step required:** engineer signoff, owner channel approval, offline contract/schema support nếu Codex được giao.

### 6.3 Package P3

| Channel / tool | Mapping | Ghi chú |
|---|---|---|
| WordPress page | `DOCUMENTED + VERIFIED_IN_PROJECT + UNVERIFIED_ACCOUNT_ACCESS` | khả thi nhất về business fit, nhưng credential chưa verify |
| WooCommerce context | `DOCUMENTED + UNVERIFIED_ACCOUNT_ACCESS` | useful for product/lead relation, chưa có API usable |
| GA4 measurement | `DOCUMENTED + UNVERIFIED_ACCOUNT_ACCESS` | event naming only, chưa có property access |
| Hostinger Reach | `DOCUMENTED + VERIFIED_IN_PROJECT + UNVERIFIED_ACCOUNT_ACCESS` | plan có thật, token/profile chưa verify |

**Future step required:** verify account credential path, decide manual content entry hay connector thật, then implement draft contract offline nếu approved.

## 7. Draft machine-readable contract proposals

JSON evidence tại `reports/evidence/2026-11-23-hermes-grow-01-s1-content-packages.json` chứa example contract proposals cho:

- `content_asset`
- `channel_event`
- `campaign`
- `lead`

Các object này là **draft contract proposals only**, không phải implementation và không chồng phạm vi với ENG-01A. Mục tiêu là giúp ChatGPT/Codex có structure chung nếu sau này muốn tạo fake adapter hoặc schema offline.

## 8. Acceptance checklist

### Expected

1. Có đúng 3 packages.
2. Mỗi package có đủ audience, objective, funnel, format, hook, script/outline, shot list, assets/permissions, forbidden claims, QA rubric, publish gate, UTM/event naming, channel adaptations, version, source status.
3. Không package nào bịa giá, stock, universal fit, structural certification, ranking promise hoặc live connector access.
4. Tái sử dụng BIZ-01 capability classes thay vì resurvey vendors.
5. Có negative tabletop test chặn publish.
6. Có evidence `0 publish / 0 paid render / 0 account mutation`.

### Observed

- Đã tạo đủ 3 packages với trường thống nhất.
- Đã giữ mọi technical/install specifics chưa có nguồn ở trạng thái gated hoặc `REQUIRES_PRODUCT_ENGINEER_APPROVAL`.
- Đã dùng mapping `DOCUMENTED / VERIFIED_IN_PROJECT / VERIFIED_IN_SESSION / UNVERIFIED_ACCOUNT_ACCESS` từ BIZ-01 làm nền.
- Đã giữ toàn bộ package ở phạm vi draft/fake-only, không publish và không dùng paid API.

## 9. Tabletop negative test

### Scenario

P2 được yêu cầu thêm exact anchor spacing và claim `universal fit` khi repo không có approved hardware spec hoặc product-engineer approval.

### Expected

Package phải chuyển sang `BLOCKED` và **không được** lên `APPROVED/PUBLISHED`.

### Observed

- Runbook và JSON evidence đều định nghĩa đường dừng này.
- Các field kỹ thuật ở P2 vẫn giữ `REQUIRES_PRODUCT_ENGINEER_APPROVAL`.
- Không có path nào trong gói này cho phép bỏ qua gate và publish.

### Result

`PASS`

## 10. Việc không thực hiện trong GROW-01/S1

- Không login vào YouTube/TikTok/Meta/Google/WordPress.
- Không tạo campaign, post, page, email hoặc lead thật.
- Không dùng Kling/HeyGen/ElevenLabs render thật.
- Không thay production website hoặc account.
- Không sửa `CATALOG.yaml`, `STATE.md`, `CHANGELOG.md` theo chỉ thị write-set.

## 11. Đề xuất index update cho coordinator, chưa thực hiện

Nếu coordinator muốn hợp thức hóa artifact này vào `main`, có thể bổ sung sau khi review:

- `CATALOG.yaml`: thêm task/report/evidence/runbook GROW-01/S1.
- `STATE.md`: ghi nhận một gói draft workflow/content packages đã sẵn sàng review.
- `CHANGELOG.md`: thêm entry read-only delivery cho GROW-01/S1.

## 12. Kết luận

GROW-01/S1 đã được thực hiện đúng phạm vi **read-only/draft-only**: có SOP vòng đời nội dung, approval matrix, 3 content packages cụ thể, channel feasibility mapping tái sử dụng BIZ-01, draft contract/schema example và negative tabletop test chặn publish khi thiếu rights hoặc technical approval.

## 13. Chuẩn bàn giao cuối cùng

`TASK | AGENT | MAIN_SHA | ASSIGNMENT_SHA | ACK_EXECUTE | OBSERVED/EXPECTED | 3_PACKAGES | TABLETOP_TEST | EVIDENCE_PATH | VERDICT | BLOCKERS | NEXT_OWNER=chatgpt`

`GROW-01/S1 | Hermes WebUI | e385c1bea2070973e3007e5717f7e980348d6ab3 | 8c821bbf1842eccb8519127f54ba7673965276d5 | EXECUTE GROW-01/S1 | Observed: repo-backed draft workflow and 3 synthetic packages were produced without live connector use, paid render, account mutation or production writes. Expected: reusable content/media workflow design with governance and package-level gates for later review. | P1 craftsmanship short (VI), P2 install-planning draft (EN), P3 EN/VI landing-page SEO brief | PASS: missing rights or unapproved technical claim remains BLOCKED and cannot transition to APPROVED/PUBLISHED | reports/evidence/2026-11-23-hermes-grow-01-s1-content-packages.json | GROW01_S1_DRAFT_WORKFLOW_READY_FOR_REVIEW | no verified live channel credentials; no approved technical specs/pricing/rights package in repo; publish and paid render remain out of scope | chatgpt`
