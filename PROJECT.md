# TTD METAL — Tổng quan dự án AI Automation

**Điểm bắt đầu cho mọi tác nhân** | Cập nhật: 2026-11-21

## Dự án để làm gì?

Phát triển một **nền tảng AI tự động hóa có kiểm soát** phục vụ hoạt động của TTD METAL, làm việc liên tục trên hạ tầng do doanh nghiệp quản lý, giảm việc thao tác lặp lại và chi phí vận hành. Không có yêu cầu AI phải tự làm mọi việc ngay từ đầu; ưu tiên tính đúng, khả năng quan sát, quyền kiểm soát và giá trị kinh doanh đo được.

Các luồng ưu tiên:
1. **Sản xuất media:** ý tưởng, kịch bản, tạo ảnh/video/voiceover, QA, bản nháp và xuất bản khi được phép.
2. **Quảng cáo:** Google Ads, Demand Gen và các kênh khác; đo nguồn khách, chi phí, leads, hiệu quả creative, đề xuất tối ưu rồi thực thi trong giới hạn được cấp.
3. **Website và SEO:** WordPress/WooCommerce trên https://wroughtiron.shop/; nội dung EN/VI, kỹ thuật SEO, chất lượng landing page, báo cáo và chỉnh sửa có kiểm soát.
4. **Mạng xã hội:** YouTube/Shorts, TikTok, Facebook/Instagram; lập lịch, chuẩn bị nội dung, theo dõi hiệu quả, đăng khi có quyền.
5. **Báo cáo:** tổng hợp dữ liệu đa kênh, chỉ số hiệu quả, phát hiện bất thường, khuyến nghị và lịch báo cáo.

Mục tiêu dài hạn là chu trình `nhận mục tiêu -> lập kế hoạch -> chọn công cụ -> thực hiện -> kiểm thử -> báo cáo -> cải thiện`, với quyền và hạn mức rõ ràng.

## Hạ tầng đã biết (bằng chứng theo đợt kiểm kê 2026-11-21)

- Hostinger VPS KVM 2 ở Kuala Lumpur; Ubuntu 24.04.4 LTS, 2 vCPU, 8 GB RAM, 100 GB SSD.
- n8n và Hermes Agent **đã cài và đang chạy qua Docker Compose tại thời điểm kiểm kê**. Không cài lại trước khi kiểm tra.
- Docker, PostgreSQL, Nginx cùng các dịch vụ hệ thống: đọc chi tiết trong [kiểm kê VPS](inventory/current-vps-state.md).
- Hai container có Docker networks tách biệt. Audit live đã chứng minh network hai chiều qua host bridge, nhưng chưa có service discovery nội bộ hoặc luồng AI end-to-end production-ready.
- Có tồn đọng hardening VPS; đọc [đánh giá bảo mật](reports/2026-11-21-vps-security-review.md). Chưa tự ý thực hiện thay đổi production.

## Chúng ta đang ở đâu?

- **Đã có:** hạ tầng VPS, bản kiểm kê, quy tắc an toàn, hệ thống tri thức GitHub, n8n `2.45.7`, Hermes `0.22.5` và [kiểm toán live hai chiều](reports/2026-11-21-n8n-hermes-integration-audit.md).
- **Đã xác minh:** hai runtime độc lập khỏe; network/auth n8n → Hermes dashboard và Hermes → n8n readiness hoạt động.
- **Chưa hoàn tất:** Hermes inference API chưa expose; n8n MCP đang tắt; n8n có 0 workflow; chưa có luồng AI end-to-end, monitoring hoặc connector marketing đã test.
- **Công việc kỹ thuật ưu tiên kế tiếp:** phê duyệt P0 sandbox change window để tạo internal network, bật Hermes API private, bật n8n MCP cho một workflow giả lập và chạy lại test end-to-end.
- Đây là định hướng; **chưa phải phê duyệt** để sửa cấu hình VPS, quảng cáo, website, publish video hay phát sinh chi phí.

## Phân vai và cách phối hợp

Xem [danh bạ tác nhân](agents/README.md). ChatGPT phụ trách tư vấn/đặc tả/review theo yêu cầu; Codex ưu tiên kỹ thuật/kiểm thử; Hermes ưu tiên AI reasoning/tool execution; n8n là workflow engine; Hostinger là nền tảng VPS, còn Hostinger Agent cần khảo sát năng lực độc lập. Phân vai mang tính ưu tiên, không khóa cứng; quyền production/chi phí do chủ dự án cấp cụ thể. Trong giai đoạn khảo sát, chủ dự án chuyển tiếp lời giao việc giữa các tác nhân. Tất cả bàn giao tài liệu và kết quả qua GitHub nếu có quyền, trạng thái job realtime qua n8n/DB khi đã triển khai.

## Tài liệu nào cần đọc?

1. [README](README.md) — bản đồ repository.
2. [STATE](STATE.md) — trạng thái và vướng mắc cập nhật thường xuyên.
3. [CATALOG](CATALOG.yaml) — xác định tài liệu có thẩm quyền.
4. [AGENTS](AGENTS.md) và [Quy ước giao/bàn giao](rules/AGENT_WORKFLOW.md) — cách nhận việc, ghi kết quả và phối hợp.
5. [Kiểm kê VPS](inventory/current-vps-state.md) — bối cảnh kỹ thuật, [Bảo mật](reports/2026-11-21-vps-security-review.md) khi cần.
6. Sau đó đọc **task cụ thể** trong `tasks/`; không cần đọc mọi report cũ.

## Quy trình đơn giản

- **Giao việc:** đặc tả trên GitHub -> gửi link cho tác nhân.
- **Làm việc:** truy cập đúng nguồn, tự chọn cách làm trong giới hạn được giao, lưu bằng chứng.
- **Bàn giao:** commit/push báo cáo vào `reports/`, cập nhật `STATE.md` khi cần -> trả link ngắn.
- Mọi kết luận phải tách **thực tế đã kiểm thử**, **ước tính**, **kế hoạch**, **chưa xác minh**.

## Không gian tài liệu

- `tasks/`: đặc tả/công việc đang và sẽ thực hiện.
- `reports/`: báo cáo, kết quả test, checkpoint có ngày.
- `inventory/`: tình trạng hệ thống hiện hành.
- `knowledge/`, `runbooks/`, `decisions/`: tri thức, vận hành, quyết định.
- `rules/`: giới hạn chung.
- `scripts/`: công cụ có thể xem và kiểm tra.

**Không đưa bí mật hoặc dữ liệu nhạy cảm chưa được xử lý vào Git public.** Xem chính sách hiện hữu.
