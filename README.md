# Hosting — TTD METAL

Hạ tầng và tự động hóa marketing của TTD METAL. Mục tiêu dài hạn: một nền tảng AI tự động hóa có kiểm soát cho 5 luồng việc:

1. **Media:** ý tưởng, kịch bản, ảnh/video/voiceover, QA.
2. **Quảng cáo:** Google Ads, Demand Gen và các kênh khác.
3. **Website và SEO:** WordPress/WooCommerce tại https://wroughtiron.shop/.
4. **Mạng xã hội:** YouTube, TikTok, Facebook/Instagram.
5. **Báo cáo:** tổng hợp đa kênh, cảnh báo bất thường.

Hạ tầng hiện có: VPS Hostinger chạy n8n và Hermes ([tra cứu](docs/reference/vps.md)).

Repo này **public**. Sản phẩm chăm sóc khách hàng qua Zalo nằm ở repo private `TTD-Zalo-Assistant`.

## Việc chạy thế nào

```
Trợ lý A0 viết Issue (có tiêu chí kiểm được)
  → Điều phối giao cho Codex / Claude Code / ChatGPT Work
  → agent làm trên nhánh agent/*  (hook nạp PROGRESS đầu phiên, chặn kết thúc khi tiêu chí chưa đạt)
  → mở PR → CI check + Codex review
  → merge (Điều phối; PR có nhãn risk:* thì chủ dự án)
  → Issue tự đóng; cron hằng ngày gắn nhãn "treo" cho việc đứng yên 3 ngày
```

Quy tắc cho agent: [AGENTS.md](AGENTS.md). Nhật ký: [PROGRESS.md](PROGRESS.md). Quyết định: [docs/adr](docs/adr/).

## Lịch sử

Mô hình vận hành cũ (rules, program, reports, CATALOG, STATE…) được giữ nguyên trong [archive/legacy-2026-11](archive/legacy-2026-11/) để tra cứu. Lý do thay đổi: [ADR-0001](docs/adr/0001-tai-cau-truc-repo.md).
