---
id: hermes-biz-01-channel-capability-matrix-2026-11-23
type: report
status: complete
updated_at: 2026-11-23
verified_at: 2026-11-23
sensitivity: public-redacted
task_id: BIZ-01
source: pr6-assignment-commit,repo-rules-and-state,official-vendor-docs,hostinger-account-inventory,hermes-session-capability-checks
---

# Hermes BIZ-01 — Ma trận năng lực tích hợp kênh cho sản phẩm Hosting

## 1. ACK thực thi

- **TASK_ID:** `BIZ-01`
- **Agent / session:** Hermes WebUI, profile `default`
- **Phạm vi nhận thực hiện:** nghiên cứu read-only về Google Ads, GA4, WordPress/WooCommerce, YouTube, TikTok, Meta, email và media tools; lập capability matrix, auth surface, quyền, giới hạn, chi phí và phương án sử dụng cho sản phẩm Hosting.
- **Giới hạn giữ nguyên:** không kết nối account production, không gọi paid API, không publish, không thay đổi production, không tạo task mới.
- **Commit phân công đã đọc:** `cdf0aed51965465601320fd57623a84065ad9c5b`
- **Base thực thi Git:** `e385c1bea2070973e3007e5717f7e980348d6ab3`
- **Tài liệu/rule đã đọc ở bản GitHub mới nhất của commit phân công:** `AGENTS.md`, `rules/AGENT_WORKFLOW.md`, `rules/REPOSITORY_SECURITY.md`, `STATE.md`, `CATALOG.yaml`, `agents/hermes.md`, `tasks/2026-11-23-multi-agent-master-allocation-review.md`
- **Công cụ/quyền thực tế trong phiên:** đọc/ghi file, terminal, web search/extract, browser automation, Git read/write qua SSH cho repo này; **không có** account connector live nào được xác minh usable trong phiên cho Ads/GA4/WordPress/social/media.
- **FIRST_ACTION đã thực hiện:** `git fetch origin`, xác minh commit phân công `cdf0aed...`, export đúng snapshot PR #6, rồi thu thập docs chính thức theo từng kênh.
- **Dependencies hiện có:** tài liệu vendor công khai; inventory Hostinger đã xác minh; quyền GitHub push còn hoạt động.
- **Blocker hiện có:** thiếu credential/account approval thực cho Ads/GA4/YouTube/TikTok/Meta/media; Hermes session không có live connector verified; BIZ-01 trên PR #6 vẫn là `NO_TASK_YET` nên bàn giao bằng report/evidence branch riêng.
- **Artifact dự kiến:**
  - `reports/2026-11-23-hermes-biz-01-channel-capability-matrix.md`
  - `reports/evidence/2026-11-23-hermes-biz-01-channel-capability-matrix.json`

## 2. Phương pháp và quy ước nhãn

### Phương pháp

1. Đọc đúng assignment/rules ở `cdf0aed...`.
2. Đối chiếu capability thực của Hermes WebUI trong repo này.
3. Thu thập tài liệu chính thức từ vendor cho từng kênh.
4. Tách rõ hai lớp bằng chứng:
   - **DOCUMENTED** = vendor docs hoặc tài liệu Hostinger mô tả khả năng.
   - **VERIFIED** = đã có bằng chứng trực tiếp trong inventory dự án hoặc chính phiên Hermes hiện tại.

### Nhãn dùng trong ma trận

- **DOCUMENTED**: docs chính thức mô tả khả năng, auth, quota, pricing hoặc giới hạn.
- **VERIFIED_IN_PROJECT**: có bằng chứng trực tiếp trong repo/inventory hiện tại.
- **VERIFIED_IN_SESSION**: có bằng chứng trực tiếp trong phiên Hermes WebUI hiện tại.
- **UNVERIFIED_ACCOUNT_ACCESS**: chưa xác minh được credential/account thật trong phiên.
- **NOT_APPROVED_FOR_WRITE**: có thể về mặt API nhưng không được phép dùng để ghi production ở nhiệm vụ này.

## 3. Tóm tắt điều hành

### Kết luận ngắn

Hermes **có thể bàn giao ngay** một ma trận tích hợp đáng tin cậy cho BIZ-01 theo hướng **discovery + design input** cho các bước sau. Trong phạm vi an toàn hiện tại, các tuyến **khả thi nhất để đi tiếp** là:

1. **GA4 read-only reporting**
2. **WordPress/WooCommerce read-only hoặc draft-first integration design**
3. **Hostinger Mail / Reach** cho email vận hành và email marketing nội bộ hệ sinh thái Hostinger
4. **Media tools** ở mức prompt/pipeline/render planning, chưa auto-publish

Các tuyến **chưa nên nhận write execution** từ Hermes ở thời điểm này:

- Google Ads live mutation
- YouTube/TikTok/Meta publishing
- account linking/credential setup cho social/media APIs
- bất kỳ thao tác nào cần approval sản xuất, chi phí hoặc content publish

## 4. Ma trận capability theo kênh

| Kênh | Trạng thái tổng quan | Evidence trực tiếp hiện có | Auth / quyền / scope chính | Giới hạn / chi phí đáng chú ý | Cách dùng an toàn cho Hosting bây giờ |
|---|---|---|---|---|---|
| **Google Ads API** | `DOCUMENTED`, `UNVERIFIED_ACCOUNT_ACCESS`, `NOT_APPROVED_FOR_WRITE` | Hermes chưa có connector/account Ads được xác minh trong phiên. | Docs quickstart yêu cầu **Google Cloud project**, **Google Ads manager account**, **client account**, OAuth 2.0/service account và access level. | Docs access-level nêu: `Test=15,000 ops/day`, `Explorer=2,880 ops/day` cho production, `Basic=15,000 ops/day`, `Standard=unlimited`; permissible use tách `ad creation`, `reporting`, `keyword research`. | Dùng cho **mapping use-case/reporting/keyword research design**. Chưa giao live campaign write. |
| **GA4 Data API** | `DOCUMENTED`, `UNVERIFIED_ACCOUNT_ACCESS` | Hermes chưa có property/account GA4 usable được xác minh trong phiên. | Google Analytics Data API dùng Google Cloud project; quota áp dụng cho OAuth 2.0 hoặc API key. | Standard property: `200,000 tokens/day`, `40,000/hour`, `10 concurrent requests/property`; có `returnPropertyQuota=true` để xem quota. | Phù hợp nhất cho **read-only KPI/reporting/attribution design** và làm nguồn cho dashboard/report. |
| **WordPress REST API** | `DOCUMENTED`; WordPress presence trong hạ tầng là `VERIFIED_IN_PROJECT`; credential REST là `UNVERIFIED_ACCOUNT_ACCESS` | Inventory đã xác minh nhiều site WordPress trong tài khoản Hostinger (`wroughtiron.shop`, `qtcty.com`, `thuanthanhdat.com`, `nepdong.com`, staging `staging.wroughtiron.shop`). | WordPress docs hỗ trợ cookie + nonce nội bộ, và **Application Passwords** qua Basic Auth trên HTTPS; plugin có thể mở thêm OAuth/JWT. | Không thấy pricing API riêng; write phụ thuộc capability của user WordPress. | Có thể đi tiếp bằng **schema + endpoint mapping + read-only content/product sync design**. Write production cần app password riêng + approval. |
| **WooCommerce REST API** | `DOCUMENTED`, `UNVERIFIED_ACCOUNT_ACCESS` | Repo/inventory chưa xác minh trực tiếp một WooCommerce store đang expose API usable cho Hermes session. | WooCommerce dùng **Consumer Key / Consumer Secret**, gắn với user WordPress; quyền `Read`, `Write`, `Read/Write`. | Key secret chỉ hiện một lần khi tạo; legacy REST API không còn mặc định trong core. | Phù hợp cho **contract design orders/products/customers** và fake adapter spec; chưa nên nhận live order/product mutation. |
| **YouTube Data API** | `DOCUMENTED`, `UNVERIFIED_ACCOUNT_ACCESS`, `NOT_APPROVED_FOR_WRITE` | Không có OAuth client/channel access được xác minh trong phiên. | Public data dùng **API key**; insert/update/delete và private data dùng **OAuth 2.0**. Scope có `youtube.readonly`, `youtube.upload`, `youtube`, `youtube.force-ssl`... | Docs quota nêu mặc định `100 search.list/day`, `100 videos.insert/day`, `10,000 quota units/day` cho phần còn lại. | Hiện phù hợp cho **content workflow design, metadata planning, upload gate design**; chưa publish. |
| **TikTok Content Posting API** | `DOCUMENTED`, `UNVERIFIED_ACCOUNT_ACCESS`, `NOT_APPROVED_FOR_WRITE` | Không có app approval/token người dùng TikTok được xác minh trong phiên. | Cần app đã đăng ký, bật Content Posting API, được duyệt scope `video.publish`, user authorise app. | Docs nêu client **chưa audit** chỉ post ở chế độ **private viewing**; muốn bỏ hạn chế phải qua audit. Hỗ trợ video và photo direct post. | Phù hợp cho **design capability matrix + approval checklist**; chưa đủ điều kiện cho auto-post production. |
| **Meta / Facebook Page Feed** | `DOCUMENTED`, `UNVERIFIED_ACCOUNT_ACCESS`, `NOT_APPROVED_FOR_WRITE` | Không có page token/business app usable nào được xác minh trong phiên. | Đọc feed cần task/quyền Page phù hợp; docs nêu các permission như `pages_read_engagement`, `pages_read_user_content`; publish yêu cầu vai trò tạo nội dung/quản lý trên Page. | Feed read giới hạn tối đa 100 posts/request; nếu không sở hữu/quản lý Page cần Page Public Content Access. | Phù hợp cho **design posting/review pipeline** và mapping approval; chưa publish live. |
| **Hostinger Mail API / Email** | `DOCUMENTED`, `VERIFIED_IN_PROJECT`, `UNVERIFIED_ACCOUNT_ACCESS` | Inventory đã xác minh 4 dịch vụ email đang hoạt động: `nepdong.com`, `nepdong.top`, `qtcty.com`, `thuanthanhdat.com`. Hermes session chưa có API key mailbox usable được xác minh. | Hostinger Mail API dùng **Bearer API key**; docs cho biết có REST API, SDKs, CLI, webhooks và MCP server. | Docs nêu `429` nếu vượt rate; repeated limit hit có thể bị block IP tạm thời. Trang pricing nêu Starter `1,000 emails/day/mailbox`, Standard/Premium `3,000/day/mailbox`. | Đây là tuyến **thực dụng nhất** cho email workflow sau này: inbox ops, notifications, drafts, triage, human-in-loop. Trong BIZ-01 chỉ nên giữ ở mức design/readiness. |
| **Hostinger Reach / email marketing** | `DOCUMENTED`, `VERIFIED_IN_PROJECT`, `UNVERIFIED_ACCOUNT_ACCESS` | Inventory xác minh có `Reach 1000` gắn với `wroughtiron.shop`. | Reach public API cần **Hostinger API token** + **profile ID**; docs nói có sync WordPress, AI Builder, store, API, Hostinger Connector. | Free/paid tiers khác nhau; nhiều tính năng như automation scheduling/HTML editor/collaborators cần paid; AI actions dùng **Hostinger Credits**. | Phù hợp cho **CRM/contact sync + campaign design + abandoned-cart/email marketing planning**. Có giá trị cao cho Hosting product nhưng chưa nên bật live token từ Hermes session. |
| **HeyGen** | `DOCUMENTED`, `UNVERIFIED_ACCOUNT_ACCESS` | Chưa có API key/account HeyGen verified trong phiên. | Docs landing page nêu self-serve qua **API key**, REST/CLI/MCP, webhooks, batch APIs. | Docs nêu batch APIs **tối đa 100 requests/call**; pricing cụ thể không được thu thập ở lượt này. | Phù hợp cho **avatar video SOP / sales explainer / onboarding video** ở mức draft pipeline. |
| **ElevenLabs TTS** | `DOCUMENTED`, `UNVERIFIED_ACCOUNT_ACCESS` | Không có account/API key ElevenLabs verified trong phiên. | API TTS, hosted MCP, nhiều model/voice options. | Paid plan mới có commercial use; char limits theo model như `5,000`, `10,000`, `40,000`, `100,000`; higher-quality audio chỉ ở paid tiers. | Phù hợp cho **voiceover pipeline** cho video/email/audio assets; chưa render production. |
| **Kling AI API** | `DOCUMENTED`, `UNVERIFIED_ACCOUNT_ACCESS` | Không có AccessKey/SecretKey verified trong phiên. | Docs nêu auth bằng **AccessKey + SecretKey**, tạo **JWT bearer token**; endpoint ngoài Trung Quốc là `https://api-singapore.klingai.com`. | Docs nêu prompt/negative prompt tối đa `2500` ký tự; 4K mode tính phí `3 units/second`; output được lưu `30 ngày`. | Phù hợp cho **render design / effect catalog review / prompt template**; chưa nên auto-render hay publish. |

## 5. Diễn giải theo tuyến ưu tiên

### 5.1 Tuyến nên ưu tiên sau BIZ-01

#### A. GA4 read-only + attribution planning

- Giá trị: đo hiệu quả website/content/growth mà không chạm publish.
- Đầu ra khả thi tiếp theo: KPI matrix, event dictionary, naming/UTM plan.
- Owner kỹ thuật tiếp theo phù hợp: ChatGPT/Codex cho spec; account owner cho OAuth/property access.

#### B. WordPress/WooCommerce contract-first

- Giá trị: dữ liệu sản phẩm/nội dung nằm gần business flow của Hosting.
- Đầu ra khả thi tiếp theo: endpoint map cho posts/pages/products/orders/customers, permission matrix, fake payload set.
- Hướng an toàn: read-only hoặc draft-only trước; không cập nhật nội dung trực tiếp.

#### C. Hostinger Mail + Reach

- Giá trị: cùng hệ sinh thái hiện hữu, đã có inventory xác minh plan/email domains.
- Dùng tốt cho: inbox workflow, follow-up, contact sync, newsletter/campaign design, abandoned-cart/email marketing readiness.
- Rủi ro: cần API token thật, mailbox/reach workspace mapping, consent/deliverability handling.

### 5.2 Tuyến nên giữ ở mức thiết kế

- Google Ads live mutation
- YouTube/TikTok/Meta publish
- HeyGen/ElevenLabs/Kling render production tự động
- bất kỳ connector nào cần secret/account chưa được xác minh

## 6. Gap và blocker cụ thể

1. **Không có account connector live đã verified trong Hermes session** cho Ads/GA4/WordPress/social/media.
2. **BIZ-01 chưa có existing task file riêng** trên `main`; PR #6 ghi `NO_TASK_YET`, nên kết quả này là report bàn giao để ChatGPT Điều phối dùng làm đầu vào tiếp theo.
3. **WordPress sites đã được inventory xác minh** nhưng **không đồng nghĩa** Hermes đang có REST credential usable.
4. **Reach và Mail** có dấu hiệu phù hợp nhất về mặt hệ sinh thái, nhưng vẫn cần token riêng và approval để vận hành.
5. **Social publish APIs** đều cần approval/account-scoped auth, nên không phù hợp để Hermes tự động thực thi trong phạm vi hiện tại.

## 7. Đề xuất bàn giao cho bước kế tiếp

### Cho ChatGPT Điều phối

1. Dùng report này làm input cho **BIZ-02** (ROI/KPI/use-case priority).
2. Chốt thứ tự triển khai khuyến nghị:
   - `GA4 read-only`
   - `WordPress/WooCommerce contract design`
   - `Hostinger Mail/Reach readiness`
   - `social/media publish design only`
3. Giữ social/media publish ở phase sau, sau khi có consent/approval/account owner rõ ràng.

### Cho Codex / ENG-01A

Nếu mở gói kỹ thuật offline kế tiếp, ưu tiên tạo:

- schema hợp nhất cho `contact`, `lead`, `campaign`, `content_asset`, `product`, `order`, `channel_event`
- fake adapters cho:
  - GA4 reporting
  - WordPress/WooCommerce read
  - Reach contacts/segments
  - Mail send/draft webhook events

### Điều kiện nghiệm thu tối thiểu trước khi mở write execution

Mỗi kênh phải có đủ:

1. account owner rõ ràng
2. credential path không đẩy secret lên Git
3. scope tối thiểu cần thiết
4. rollback hoặc kill-switch
5. logging/audit trail
6. acceptance test không chạm production trước

## 8. Kết luận

BIZ-01 ở phạm vi Hermes **đã hoàn thành đúng giới hạn**: có ACK, có đọc đúng commit phân công mới nhất, có ma trận kênh tách `DOCUMENTED` với `VERIFIED`, có blocker/dependency rõ ràng, và không thực hiện bất kỳ kết nối hay thay đổi production nào.

## 9. Chuẩn bàn giao cuối cùng

`TASK | AGENT | BASE_SHA | OBSERVED | EXPECTED | TEST_RESULTS | EVIDENCE | VERDICT | BLOCKERS | NEXT_OWNER`

`BIZ-01 | Hermes WebUI | e385c1bea2070973e3007e5717f7e980348d6ab3 | Đã thu thập và đối chiếu capability docs cho Google Ads, GA4, WordPress/WooCommerce, YouTube, TikTok, Meta, Hostinger Mail, Reach và media tools; đã tách DOCUMENTED với VERIFIED; đã xác nhận inventory email/Reach/WordPress và giới hạn session Hermes | Ma trận kênh phục vụ discovery/draft cho sản phẩm Hosting, không chạm production hay paid API | PASS: fetched assignment commit, read required rules/state/profile, collected vendor docs, produced matrix, committed to branch, remote verification pending at write time | reports/2026-11-23-hermes-biz-01-channel-capability-matrix.md ; reports/evidence/2026-11-23-hermes-biz-01-channel-capability-matrix.json | PASS_READ_ONLY_DISCOVERY | thiếu live account credentials/approval cho Ads/GA4/WordPress/social/media; BIZ-01 chưa có task file riêng trên main | ChatGPT Điều phối`

## 10. Nguồn chính

- Assignment PR #6 commit `cdf0aed51965465601320fd57623a84065ad9c5b`
- `reports/2026-11-21-hostinger-account-capability-inventory.md`
- `reports/2026-11-21-hermes-capability-survey.md`
- Google Ads API docs
- Google Analytics Data API docs
- WordPress REST API docs
- WooCommerce REST API docs
- YouTube Data API docs
- TikTok for Developers docs
- Meta for Developers docs
- Hostinger Mail API / Reach docs
- HeyGen / ElevenLabs / Kling docs
