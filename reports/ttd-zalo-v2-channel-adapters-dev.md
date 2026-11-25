---
id: ttd-zalo-v2-channel-adapters-dev
type: report
status: draft
owner: ChatGPT Work
task_id: V2-02B-CHANNEL-ADAPTERS
lifecycle: ACTIVE
retention_trigger: A0 completes channel acceptance
updated_at: 2026-11-26
sensitivity: public
---

# V2-02B-CHANNEL-ADAPTERS · Bàn giao developer

A0 giao trực tiếp trong phiên ngày 26/11/2026. Base [caa7cb6](https://github.com/DuyKienTTD/Hosting/commit/caa7cb67f096064a7a753444cda0262b950ee159) từ PR #71. Phạm vi ghi là runtime server và báo cáo này. Đối chiếu [hợp đồng V2-01](https://github.com/DuyKienTTD/Hosting/blob/367c36454e021dbf11ea30afb72ebff0f1131afc/program/zalo-mvp01/v2-01-channel/ADAPTER_CONTRACT.ts), [ma trận](https://github.com/DuyKienTTD/Hosting/blob/367c36454e021dbf11ea30afb72ebff0f1131afc/program/zalo-mvp01/v2-01-channel/CAPABILITY_MATRIX.md) và [smoke](https://github.com/DuyKienTTD/Hosting/blob/367c36454e021dbf11ea30afb72ebff0f1131afc/program/zalo-mvp01/v2-01-channel/SMOKE_TEST.md). [Work order tiền nhiệm](https://github.com/DuyKienTTD/Hosting/blob/6eb9efb3b45ae81afde5373de78bc8e96a9645db/tasks/zalo-resume-01-gov.md) ghi bối cảnh trước ZALO-PRODUCT-DIRECTION-02.

| Nguồn | Lệnh và bằng chứng |
|---|---|
| API Subiz | `receiveMessage`, `sendMessage`, `getContact`. Test HTTP loopback theo thuật toán HMAC và payload docs. Route allowlist khóa account/source/CID/user/profile. GET xác minh hội thoại trước POST, tình trạng bạn bè do người vận hành đối chiếu và có hạn. PAT lấy từ env. Gửi trả `accepted`, chưa chứng minh delivery Zalo. |
| Bot Zalo | `readGroupMessages`, `postToGroup` cho nhóm Beta đã duyệt, có `getMe.can_join_groups`. Đọc tin mới qua webhook. Kiểm payload bằng fixture API. Bot công khai chưa có route kiểm duyệt được xác nhận. |
| UI Subiz | `createGroup`, `postToGroup`, `sendFriendRequest`, `onFriendAccepted`. `listMembers` là chẩn đoán riêng ngoài hợp đồng. Playwright Chromium đã chạy trên HTML loopback. Selector phải khớp workspace, panel, đích và receipt. Sai lệch khóa bền vững cấu hình selector, chụp trang chẩn đoán sạch. |
| Chưa hỗ trợ | `listGroups`, `moderateGroup`, đọc lịch sử nhóm và các route chưa cấu hình. Trả `not_supported`. |

Router chọn đúng một adapter cho mỗi lệnh, không tự thử kênh khác. Mọi lượt gửi từ runtime và smoke qua Guard trước khi bắt đầu transport. SQLite lưu dedup và mã hóa inbox/receipt, giữ dấu unknown delivery để ngăn phát lại. Ghi inbox trước ACK, dedup theo provider event và scope, xóa dữ liệu inbound hết hạn sau 24 giờ. Cổng Guard chặn ưu đãi khi webhook opt-out đã xác thực tới trong lúc xác minh contact. Lệnh smoke dùng một nonce, một contact và một CID, cho kết quả auth/receive/API acceptance và yêu cầu đối chiếu màn hình ở đích.

[DEPLOY.md](../apps/ttd-zalo-agent-server/DEPLOY.md) ghi biến môi trường, HTTPS, cách cài Chromium và điều kiện bật. Provider thật, mã định tuyến Personal, quyền nhóm Bot, selector Subiz live, delivery tới Zalo và build Docker cần phép thử trên pilot của A0. Phiên này dùng fixture và HTML cục bộ.

| Lệnh | Exit | Kết quả |
|---|---:|---|
| Server `npm ci --no-audit --no-fund`, `npm run typecheck`, `npm run build` | 0 | Cài đặt, kiểm kiểu, biên dịch |
| Server `PLAYWRIGHT_TEST_EXECUTABLE=/tmp/chromium npm test` | 0 | 39/39 gồm 31 runtime hồi quy và 8 ca adapter/router/Playwright/smoke |
| Desktop `ELECTRON_SKIP_BINARY_DOWNLOAD=1 npm ci --no-audit --no-fund`, `npm run typecheck`, `npm run build`, `npm test` | 0 | 20/20 |
| Desktop `node scripts/evaluate-corpus.mjs` | 0 | 48/48 |

INCIDENT: CDN Playwright trả 403 và Chromium hệ thống thiếu binary. Test Playwright chạy đạt với Chromium headless từ gói npm tạm ngoài cây Git. Sandbox thiếu Docker nên chưa chạy image/Compose.
