# TTD METAL — Tổng quan dự án AI Automation

**Business charter (long-term) — current execution priority is KNG-01 only.**

## Dự án để làm gì?

Phát triển một **nền tảng AI tự động hóa có kiểm soát** phục vụ hoạt động của TTD METAL, làm việc liên tục trên hạ tầng do doanh nghiệp quản lý, giảm việc thao tác lặp lại và chi phí vận hành. Không có yêu cầu AI phải tự làm mọi việc ngay từ đầu; ưu tiên tính đúng, khả năng quan sát, quyền kiểm soát và giá trị kinh doanh đo được.

Các luồng ưu tiên:
1. **Sản xuất media:** ý tưởng, kịch bản, tạo ảnh/video/voiceover, QA, bản nháp và xuất bản khi được phép.
2. **Quảng cáo:** Google Ads, Demand Gen và các kênh khác; đo nguồn khách, chi phí, leads, hiệu quả creative, đề xuất tối ưu rồi thực thi trong giới hạn được cấp.
3. **Website và SEO:** WordPress/WooCommerce trên https://wroughtiron.shop/; nội dung EN/VI, kỹ thuật SEO, chất lượng landing page, báo cáo và chỉnh sửa có kiểm soát.
4. **Mạng xã hội:** YouTube/Shorts, TikTok, Facebook/Instagram; lập lịch, chuẩn bị nội dung, theo dõi hiệu quả, đăng khi có quyền.
5. **Báo cáo:** tổng hợp dữ liệu đa kênh, chỉ số hiệu quả, phát hiện bất thường, khuyến nghị và lịch báo cáo.

Mục tiêu dài hạn là chu trình `nhận mục tiêu -> lập kế hoạch -> chọn công cụ -> thực hiện -> kiểm thử -> báo cáo -> cải thiện`, với quyền và hạn mức rõ ràng.

## Ưu tiên thực thi hiện hành (2026-11-23)

**KNG-01 ONLY.** A0/Điều phối tạm dừng mọi G0/UC01/UI/Ads/media/infra feature work. [Nguồn định tuyến và owner của candidate](program/current.json); chỉ có hiệu lực trên `main` khi merge được A0 phê duyệt. Mỗi task cần ACK thật; GitHub comment không kích hoạt Agent.

## Nguồn có thẩm quyền và trạng thái

- [README](README.md) → [AGENTS](AGENTS.md) → [workflow](rules/AGENT_WORKFLOW.md) và [bảo mật](rules/REPOSITORY_SECURITY.md) → [STATE](STATE.md) → [CATALOG](CATALOG.yaml). Đọc đầy đủ quy tắc hiệu lực và đúng task trước khi viết.
- Các mục tiêu dài hạn ở trên **không phải** lệnh triển khai production hay tăng ngân sách. A0 giữ quyền phê duyệt merge, paid, production và xuất bản.
- Lịch sử trạng thái/ưu tiên của PR31 được bảo toàn tại [PROJECT.md@PR31](https://github.com/DuyKienTTD/Hosting/blob/a770de80a2467ca1789c820b63416209cf53b7d1/PROJECT.md), blob `bf8b107f7a36dd81d02f859d6a8d5e499d9c83a6`. Bản này đã ghi các thông tin host/service tại lần kiểm tra 21/11/2026; không suy ra tình trạng live ngày 23/11.
- [Inventory VPS](inventory/current-vps-state.md) và [báo cáo bảo mật](reports/2026-11-21-vps-security-review.md) là bằng chứng theo thời điểm; xác minh live riêng trước mọi quyết định sản xuất.
- A1 thực thi KNG code trên nhánh cô lập; Work độc lập QA; Chat Điều phối chịu trách nhiệm tích hợp. Hermes HOLD, Codex NOT_AUTHORIZED, Hostinger và A2 không nhận feature task mới khi KNG còn mở.

## Lưu hồ sơ

`tasks/` giao việc và tiêu chí; `reports/` và Git objects lưu evidence; `program/` lưu candidate định tuyến/roadmap; `rules/` là điều kiện an toàn bắt buộc. Repo **public**: tuyệt đối không đưa bí mật/PII, .env, dump, backup lên Git.
