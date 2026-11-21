---
id: ttd-ai-platform-audit-001
type: task
status: current
updated_at: 2026-11-21
sensitivity: public
owner: codex
---

# TTD-AI-PLATFORM-AUDIT-001 — Kiểm toán n8n ↔ Hermes và kiến trúc AI Automation

## Mục tiêu và bối cảnh

TTD METAL muốn vận hành hệ thống AI tự động 24/7 cho sản xuất video, quảng cáo, SEO, WordPress/WooCommerce, mạng xã hội, báo cáo và quản lý media. Hạ tầng sẵn có là Hostinger KVM 2, Ubuntu, 2 vCPU, 8 GB RAM; **n8n và Hermes đã chạy bằng Docker Compose** tại thời điểm kiểm kê 2026-11-21. **Không cài lại** khi chưa có bằng chứng cần thiết.

Điểm bắt đầu: [README](../README.md), [PROJECT](../PROJECT.md), [STATE](../STATE.md), [AGENTS](../AGENTS.md), [CATALOG](../CATALOG.yaml), [quy tắc giao việc](../rules/AGENT_WORKFLOW.md).

Nguồn đặc biệt quan trọng:
- [Kiểm kê VPS](../inventory/current-vps-state.md)
- [Báo cáo Hermes tự đánh giá](../reports/2026-11-21-hermes-self-assessment.md)
- [Bảo mật VPS](../reports/2026-11-21-vps-security-review.md)

**Đã biết:** Hermes trong phiên WebUI có nhiều tools/skills, memory/session recall và GitHub push. **Chưa biết:** exact image build/version, API live, Hermes ↔ n8n live. Lệnh curl từ shell Hermes tới localhost thất bại; **không đồng nghĩa service trên VPS bị lỗi**.

## Kết quả Codex cần tạo ra

1. **Bản đồ thực tế:** service/compose/container/image digest, runtime, API/health endpoint, mạng Docker, permissions, trạng thái workflows, storage, logs (đã khử bí mật), CPU/RAM, bảo mật và backup. Phân biệt hiện trạng đo trực tiếp, thông tin tài liệu, suy luận.
2. **Chứng minh kết nối n8n → Hermes:** test request có auth, dữ liệu giả lập, response JSON/schema, log/latency, lỗi và retry. Nếu chưa có API tương thích: xác định rõ và trình bày giải pháp thay thế.
3. **Chứng minh Hermes → n8n:** đánh giá và kiểm thử `n8n-official` MCP nếu tương thích với instance; so sánh webhook/REST/adapter. Không mặc định MCP đã bật hoặc khả dụng. Chỉ kết luận PASS khi một luồng thực sự chạy và có bằng chứng cả hai đầu.
4. **Thử một luồng end-to-end tối thiểu:** nhận dữ liệu quảng cáo giả lập → Hermes phân tích/lập kế hoạch → n8n thực hiện phép xử lý cho phép → kết quả có kiểm tra schema, task ID, execution log và trạng thái cuối. Không sử dụng tài khoản quảng cáo production.
5. **Tính bền vững:** đánh giá chạy theo lịch, background task, timeout, idempotency, queue, retry, xử lý lỗi, cảnh báo, chi phí AI và khả năng tiếp tục sau gián đoạn. Thử có giới hạn, không stress-test.
6. **Tài nguyên media VPS-first:** xem xét lưu ảnh/video/voiceover/thành phẩm trên VPS (ví dụ `/srv/ttd-media` như phương án, không bắt buộc), dung lượng an toàn, quyền file, volume mounts, tệp tạm, FFmpeg, backup ngoài VPS và kiến trúc có thể chuyển sang object storage sau này. Không tạo media storage production ở đợt kiểm toán.
7. **Kiến trúc triển khai:** phân vai Hermes/n8n/DB/media storage/monitoring/API; đề xuất các pipeline cho video (Kling/HeyGen/ElevenLabs), Google Ads và GA4, website SEO, YouTube/TikTok/Meta, báo cáo. Với mỗi connector: phân biệt đã kết nối, đã test, cần cấu hình, cần phát triển, không hỗ trợ; làm rõ giới hạn quyền/API và chi phí.
8. **Lộ trình ưu tiên và quyết định:** chọn phương án đơn giản nhất đủ dùng, tận dụng VPS đang có; chỉ đề xuất dịch vụ trả phí khi có lợi ích đo được. Đưa ra P0/P1/P2, độ khó, phụ thuộc, rủi ro và tiêu chí nghiệm thu cho từng giai đoạn.

## Cách thực hiện và phạm vi quyền

- Codex chủ động lựa chọn công cụ/kỹ thuật tối ưu; các phương án ở đây **là gợi ý**, không phải danh sách thao tác bắt buộc. Không đọc lại/kiểm chứng những gì Hermes đã chứng minh nếu không có lý do.
- Giai đoạn này là **audit và kiểm thử an toàn**. Được phép đọc hiện trạng, gọi health/API chỉ đọc, kiểm tra mạng và chạy thử trên tài nguyên cô lập nếu không ảnh hưởng hệ thống hiện hữu.
- **Không** restart/recreate container production, nâng cấp image, chỉnh firewall/SSH, đổi credentials, kích hoạt workflow production, thay đổi Google Ads/WordPress, publish media, tải/gỡ dịch vụ, hay phát sinh chi phí mới khi chưa được phê duyệt.
- Nếu kiểm thử cần tạo cấu hình, workflow, bridge hay sửa mạng có ảnh hưởng production: chuẩn bị phương án, đánh dấu `APPROVAL_REQUIRED` và không tự triển khai. Nếu có sandbox thực sự tách biệt và được phép thì có thể kiểm thử tại đó.
- Không ghi mật khẩu, token, API key, nội dung .env, log thô có bí mật, dữ liệu khách hàng vào repo public. Báo cáo đủ bằng chứng nhưng đã khử định danh.
- Chỉ đánh dấu `PASS` khi có bằng chứng thực thi; `FAIL` khi đã thử đúng cách và thất bại; `BLOCKED` khi thiếu môi trường/quyền; `NOT_TESTED` khi chưa làm. Đặc biệt không xem tài liệu Hermes upstream là bằng chứng instance Hostinger có cùng endpoint.

## Báo cáo nghiệm thu

Tạo `reports/2026-11-21-n8n-hermes-integration-audit.md` (hoặc file ngày thực hiện thực tế, có task ID); trong đó có:
- Summary (PASS/PARTIAL/BLOCKED), thời gian và điểm quan sát VPS.
- Matrix test từng chiều n8n ↔ Hermes, input giả lập, response/error đã khử bí mật, endpoint ở dạng an toàn, phương án auth, thời gian phản hồi.
- Bảng current capabilities vs missing components; kiểm kê workflows, tool/skills và media storage.
- Kiến trúc đề xuất, lựa chọn kỹ thuật và lý do, chi phí dự kiến, backlog P0/P1/P2.
- Những gì **đã thay đổi**, những gì **chỉ đề xuất**, những gì **chưa được kiểm chứng**.
- Link các artifact/script thử nghiệm an toàn nếu có.

Sau khi hoàn tất: push report và cập nhật `STATE.md`, `CATALOG.yaml`, `CHANGELOG.md` theo quy tắc. Trả lời người giao việc ngắn gọn: trạng thái, URL report, URL commit/PR, quyết định còn chờ.

**Tiêu chí thành công của đợt này:** Có kết luận có chứng cứ về tình trạng hai chiều, không ảnh hưởng production; nếu không thể kết nối do giới hạn quyền, phải chỉ ra chính xác blocker, bước cần duyệt và thiết kế khả thi để tiến lên. Không đòi mọi integration marketing phải hoàn thiện trong cùng audit.
