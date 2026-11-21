---
id: n8n-hermes-p0-sandbox-integration-2026-11-21
type: report
status: current
result: partial
updated_at: 2026-11-21
verified_at: 2026-11-21
sensitivity: public-redacted
source: live-hostinger-terminal-tests,repository-identity-report,official-provider-pricing
task: ttd-ai-p0-integration-001
---

# P0 sandbox n8n ↔ Hermes — kết quả Mức 1

## Kết luận

**MỨC 1 PASS / TOÀN BỘ P0 PARTIAL / AWAITING_LEVEL2_APPROVAL.**

Trên đúng KVM 2 đã xác minh, Codex đã triển khai hai service phụ `ttd-p0-n8n-sandbox` và `ttd-p0-reasoner` trên bridge `ttd-ai-p0-sandbox` có `internal=true`. Không service nào publish host port. n8n và Hermes production không bị restart/recreate, health trước/sau đều PASS và downtime bằng 0.

Đúng một workflow `fake-ads-audit-v1` đã chạy với bearer auth, schema validation, callback, timeout/retry và idempotency. Bộ test structural E2E 9/9 PASS và rollback/restore rehearsal PASS. Runtime reasoning hiện là deterministic mock, không gọi model; vì vậy **không phải bằng chứng AI reasoning thật**. Acceptance cuối vẫn bị chặn bởi phê duyệt Mức 2 cho provider/model và cost cap.

Bằng chứng máy đọc: [JSON đã khử bí mật](evidence/2026-11-21-ttd-ai-p0-integration-001.json). [Mã triển khai công khai](../sandbox/p0-level1/README.md) không chứa giá trị bí mật.

## Safety gate và bí mật

| Điều kiện | Kết quả |
|---|---|
| Identity: đúng KVM 2, không đụng U4S `ttdnew.tech` | **PASS** |
| Pre/post production health; restart count | **PASS / 0** |
| Backup và rollback trước thay đổi | **PASS** |
| Bearer token sinh bằng CSPRNG, file `600`, thư mục `700` | **PASS** |
| Khóa mã hóa sandbox sinh riêng, file `600`, data directory riêng | **PASS** |
| Không thay khóa/credential/volume của n8n production | **PASS** |
| Secret không xuất hiện trong chat, Git, report, test output hoặc application log | **PASS** |
| Public port, firewall, DNS, Hermes chính, business account | **KHÔNG ĐỔI** |
| Paid inference/API call | **0** |

Giá trị secret không được ghi lại. Repository chỉ chứa placeholder `__P0_TOKEN__`; token thật chỉ được thay trong runtime copy root-only trên VPS. n8n sandbox dùng data directory và encryption scope riêng, nên không tác động cơ chế mã hóa hiện hữu của production.

## Kiến trúc đã triển khai

```text
Internet: không route vào sandbox; network không có egress

ttd-p0-n8n-sandbox
  └─ đúng 1 authenticated webhook
       └─ private HTTP → ttd-p0-reasoner (mock only)
                              └─ authenticated callback → workflow sandbox

n8n production ─┐
Hermes production ├─ vẫn healthy; không restart/recreate/config change
U4S ttdnew.tech ─┘
```

| Service phụ | Isolation và limit |
|---|---|
| `ttd-p0-reasoner` | internal network; không egress; read-only root; drop all capabilities; no-new-privileges; 0.25 CPU; 384 MiB; 64 PID |
| `ttd-p0-n8n-sandbox` | data/key riêng; internal network; không public port; drop all capabilities; no-new-privileges; 0.5 CPU; 768 MiB; 128 PID |

Health cuối: cả hai auxiliary service `healthy`. Probe Internet từ reasoner bị chặn đúng thiết kế. n8n production trả health/readiness 200; Hermes production trả các health endpoint 200; restart count của hai service chính vẫn bằng 0.

## Test matrix Mức 1

| Case | Kỳ vọng | Kết quả | Thời gian quan sát |
|---|---|---|---:|
| Thiếu bearer token | 401 | **PASS** | 318 ms |
| Sai bearer token | 401 | **PASS** | 304 ms |
| Input sai schema | 422 | **PASS** | 510 ms |
| Request hợp lệ → callback schema hợp lệ | 200 | **PASS** | 905 ms |
| Replay cùng task/input | cached, không callback lần hai | **PASS** | 469 ms |
| Cùng task, input khác | 409 | **PASS** | 2 ms |
| Callback output sai schema | reasoner nhận 502 | **PASS** | 317 ms |
| Timeout làm n8n retry | retry được deduplicate | **PASS** | 3,114 ms |
| Hoàn tất sau timeout | đúng một callback, replay cached | **PASS** | 2 ms |

Khi phát hiện khả năng retry trùng callback, adapter được sửa để ghi trạng thái `inflight` trước delay/callback. Chỉ container phụ reasoner được recreate; không service production nào bị tác động. Một thử nghiệm import dùng tùy chọn CLI không được image hỗ trợ đã fail safe; workflow sau đó được import và publish bằng lệnh tương thích.

## Backup, rollback và restore

- Baseline, source/config sandbox và rollback script được đặt trong thư mục root-only trên VPS.
- Rollback dừng đúng hai auxiliary containers, không xóa dữ liệu và không chạm production.
- Diễn tập rollback thực tế PASS: hai service phụ dừng; n8n/Hermes production tiếp tục chạy, restart count 0.
- Restore bằng Compose PASS; cả hai service phụ trở lại `healthy`. n8n sandbox cần khoảng nửa phút để qua healthcheck sau startup.

## Provider/model và đề xuất Mức 2

Giá standard text tại thời điểm khảo sát, tính theo mỗi một triệu đơn vị văn bản đầu vào/đầu ra.

| Provider/model | Input | Output | Ghi chú |
|---|---:|---:|---|
| [OpenAI GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) | USD 0.10 | USD 0.50 | Structured outputs, function calling và MCP được tài liệu chính thức liệt kê |
| [Anthropic Claude Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5) | USD 0.10 | USD 0.50 | Mức này áp dụng prompt không quá 100K token |
| [Google Gemini 3.1 Flash-Lite](https://ai.google.dev/gemini-api/docs/pricing) | USD 0.25 | USD 1.50 | Free tier có điều khoản dữ liệu khác paid tier; không dùng dữ liệu kinh doanh trước khi review |

Đề xuất kỹ thuật: **GPT-6 Luna** làm ứng viên đầu tiên do giá thấp và hỗ trợ structured outputs; Claude Haiku 5.5 là phương án tương đương về đơn giá. Với tối đa 4K input + 2K output, chi phí ước tính của hai model này là USD 0.0014/call; 5 call là USD 0.007. Gemini 3.1 Flash-Lite tương ứng khoảng USD 0.004/call; 5 call là USD 0.02.

Đề xuất approval Mức 2:

- tối đa 5 fake-data calls;
- tối đa 4K input và 2K output mỗi call;
- hard cap USD 0.01/job;
- cap USD 0.05/ngày và USD 0.05 tổng cho P0;
- không grounding, web search, media generation hoặc tool tính phí;
- dừng ngay khi chạm cap, schema fail hoặc provider trả lỗi billing/quota;
- API key chỉ lưu root-only trên VPS, không commit; chỉ khi phê duyệt mới mở egress cho đúng provider endpoint.

## Acceptance và blocker

| Tiêu chí | Trạng thái |
|---|---|
| Identity, isolation, auth, schema, callback, retry/idempotency | **PASS** |
| Backup/rollback/restore; production health | **PASS** |
| Không phí, không public/network/business mutation | **PASS** |
| AI reasoning thật qua private runtime | **BLOCKED_BY_LEVEL2_APPROVAL** |

Quyết định còn cần chủ dự án: phê duyệt **GPT-6 Luna + cap đề xuất** (hoặc chọn model khác trong bảng). Sau approval, Codex có thể thay mock provider client trong runtime phụ, cấp egress allowlist tối thiểu và chạy cùng bộ test; không cần thay Hermes chính hoặc restart production theo thiết kế hiện tại.
