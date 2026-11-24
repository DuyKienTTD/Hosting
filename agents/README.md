# TTD METAL — Danh bạ năng lực và nguồn hồ sơ

Danh bạ tra cứu hồ sơ, không cấp quyền. [AGENTS](../AGENTS.md) quy định ba nhóm đọc ban đầu và nguồn theo thao tác. Điều phối, Work, A2 và A0 dùng các phần vai trò trong [hồ sơ ChatGPT](chatgpt.md). [Trợ lý A0](a0-assistant.md) dùng hồ sơ riêng về thẩm định độc lập và phạm vi đại diện.

**KNG-01 ONLY:** A1 viết code/tích hợp trên nhánh được giao; Work QA độc lập; Điều phối điều hành, A0 duyệt cuối. Không tự kích hoạt G0/UC01/infra/media/Ads, Hostinger hay Codex. Quyền kỹ thuật từ hồ sơ là session-scoped, không phải authorization. Không coi GitHub comment là Work ACK, không xác nhận production/live từ dữ liệu ngày 23/11.

## Danh bạ năng lực (snapshot PR31 — KHÔNG phải current dispatch)

| Thành phần | Loại | Năng lực lịch sử | Hồ sơ | Mức xác minh |
|---|---|---|---|---|
| ChatGPT Điều phối | AI trợ lý tương tác | tư vấn, đặc tả, phân tích, điều phối bằng GitHub | [chatgpt](chatgpt.md) | GitHub write/read đã thử trong phiên; thực thi nền chưa có |
| **A1 — ChatGPT Thông thường** | AI trợ lý phiên riêng | GitHub/metadata, validator, code offline, QA độc lập theo task | [a1](a1.md) | Role ACK; PR #32 author delta, Work QA offline PASS_WITH_LIMITS; PR #33 proposal review PASS_WITH_LIMITS | 
| ChatGPT Work | Agent thực hiện đa bước | source QA độc lập, browser/UX, offline integration | [chatgpt](chatgpt.md) (profile Work riêng pending) | QA PR #32 và PR #24 đã có evidence; quyền theo phiên |
| Codex | Tác nhân kỹ thuật **ngoại lệ chi phí** | chỉ case đặc thù đã chứng minh các Agent khác không làm được | [codex](codex.md) | CODEX_NOT_AUTHORIZED cho lệnh mới nếu chưa được A0 duyệt chi phí |
| Hermes | AI agent trên VPS/WebUI | suy luận, tools, memory, thực thi tác vụ | [hermes](hermes.md) | capability survey hoàn tất; E2E với n8n chưa chạy |
| Hostinger | Nhà cung cấp / control plane + Hostinger Agent | hPanel/VPS/DNS, capability lịch sử (không giao mới) | [hostinger](hostinger.md) | **PAUSED theo A0**, chưa ACK thông báo; mọi thay đổi tiếp tục bị chặn |
| n8n | Workflow engine, **không phải AI agent** | trigger, connectors, schedule, job state | [n8n](n8n.md) | service healthy, 0 workflow, MCP tắt |

**Hostinger Agent** là trợ lý AI có giao diện trong hPanel, phải khảo sát riêng; không đồng nhất với Hostinger là nhà cung cấp hoặc với quyền root/VPS. Các hồ sơ là **bản ghi năng lực** không phải lệnh cấp quyền.

## Thang bằng chứng (snapshot PR31)

- `VERIFIED`: có phép thử trực tiếp và liên kết kết quả; ghi môi trường và thời gian.
- `REPORTED`: báo cáo của tác nhân/kiểm kê, chưa kiểm lại độc lập khi cần.
- `AVAILABLE_UNTESTED`: giao diện/docs có chức năng nhưng chưa thử end-to-end.
- `BLOCKED`: chưa thể thử do thiếu quyền/cấu hình/đầu vào.
- `UNKNOWN`: chưa biết; không được suy diễn.
- `PLANNED`: mục tiêu tương lai, không phải năng lực hiện tại.


**D5 pre-dispatch boundary:** For *manual preparation only*, use [fail-closed candidate selector](../program/kng/select_task.py) (`python3 program/kng/select_task.py --root .`), not `tasks/` glob or CATALOG `type: task` alone. Explicit `dispatch_eligible: true`, nonarchived supported task status and safe existing file are mandatory; missing/false/unknown eligibility is never eligible. Invalid catalog/schema causes STOP. Output is **not** dispatch authority; the Director must separately issue a real work order, and the recipient must ACK in its actual chat. No automatic distributor exists or is being deployed.

## Quy tắc đọc và giao việc

- Hồ sơ [A1](a1.md), [Codex](codex.md), [Work/Điều phối](chatgpt.md), [Hermes](hermes.md), [Hostinger](hostinger.md), [n8n](n8n.md) chỉ mô tả công cụ/nguồn đã quan sát; **không phải** nguồn trạng thái hoặc công việc đang hoạt động.
- Mọi task phải có chỉ thị chủ quyền/ACK thực tế, write-set, STOP và bằng chứng; không chọn nhiệm vụ chỉ vì `type: task` trong CATALOG. **Các mục `archived-inactive-not-dispatchable` hoặc `dispatch_eligible: false` phải bị loại khỏi mọi bộ chọn task.** Nếu selector không hiểu trường này, phải STOP, không được đoán.
- Bản danh bạ PR31 đầy đủ (gồm các quyết định OPS/Hostinger và Codex trước KNG) vẫn được giữ [theo commit bất biến](https://github.com/DuyKienTTD/Hosting/blob/a770de80a2467ca1789c820b63416209cf53b7d1/agents/README.md), blob `3c8a50a8b07a53bd28414a049cd5f5c366005913`. Mọi mệnh lệnh trong bản snapshot đó chỉ là bằng chứng lịch sử, không tự hoạt động lại.
