---
status: accepted
date: 2026-11-28
decision-makers: Chủ dự án (giao toàn quyền cho Claude-Điều phối ngày 28/11/2026)
---
# ADR-0003: Tách TTD Zalo Assistant ra repo private

## Bối cảnh

Zalo Assistant xử lý hội thoại và số điện thoại khách hàng thật, phải tuân thủ Nghị định 91/2020 (tin nhắn rác) và Luật Bảo vệ dữ liệu cá nhân 91/2025. Sản phẩm này không thuộc 5 luồng việc trong charter của Hosting. Mã nguồn (4 ứng dụng trong `apps/`, 7 workflow z4–z6) đang nằm trên nhánh `dev/ttd-zalo-mvp01` của một repo **public**.

## Quyết định

- Tạo repo **private** `DuyKienTTD/TTD-Zalo-Assistant` từ lịch sử nhánh `dev/ttd-zalo-mvp01` (commit `f1b8a99`, giữ nguyên lịch sử). Nhánh này đã chứa các nhánh dev/ttd-zalo-* khác.
- Chuyển sang repo đó: `program/zalo-mvp01/`, `decisions/ZALO-PRODUCT-DIRECTION-02.md` và `-04.md`, `tasks/zalo-resume-01-gov.md`. Xóa các file này khỏi `main` của Hosting.
- Repo Zalo dùng cùng mô hình vận hành ở ADR-0001 và ADR-0002.
- CI của Hosting chặn mọi đường dẫn chứa `zalo`.

## Rà soát dữ liệu (28/11/2026)

- Đã quét cây `main` và đầu 24 nhánh Zalo tìm số điện thoại Việt Nam, email cá nhân, IP công khai và token.
- Chỉ thấy số giả lập `0900000000` trong fixture test. Không phát hiện dữ liệu khách hàng thật ở đầu nhánh.
- Chưa quét toàn bộ lịch sử từng commit.

## Còn lại cho chủ dự án

- 24 nhánh Zalo cũ vẫn còn trên Hosting public. Mã ở đó đã công khai nên tách repo không thu hồi được. Nên xóa các nhánh này sau khi xác nhận repo mới đủ nội dung (danh sách trong mô tả PR tái cấu trúc).
- Không rewrite lịch sử Hosting, trừ khi phát hiện dữ liệu thật.
