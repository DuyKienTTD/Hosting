# HOSTING — Quy tắc cốt lõi MSC

MSC candidate: áp dụng chính sách này sau nghiệm thu MSC-08 và xác minh tích hợp main. Trước đó dùng main hiện hành.

## Ba nhóm đọc ban đầu

1. File này tại main đã xác minh.
2. Hồ sơ đúng vai trò trong [danh bạ](agents/README.md). Dùng đường dẫn hồ sơ trực tiếp nếu đã biết.
3. Đặc tả đúng task, pin commit và phiên bản. Xác định mục tiêu, owner, quyền, bước đầu, phạm vi đọc/ghi, giới hạn, nghiệm thu và người nhận. Ghi ACK thật tại phiên nhận khi có work order.

Danh bạ, CATALOG và các entrypoint khác dùng để tra cứu. Chỉ đọc mục CATALOG liên quan và dùng công cụ kiểm toàn bộ khi sửa registry.

## Điều kiện thực thi

- Mặc định từ chối tác động khi thiếu quyền rõ ràng hoặc có STOP/HOLD. Quyền Git, vai trò, snapshot, mô phỏng hay comment bàn giao không tự cấp quyền. A0 giữ quyết định production, chi phí, merge và các quyền dành riêng. Không kích hoạt Agent hay đổi quyền từ bằng chứng lịch sử.
- Trước tác động, xác minh quyền và trạng thái mới nhất, người ghi duy nhất, đúng môi trường/read-set/write-set, preflight, chi phí, điểm dừng và rollback. STOP phần bị chặn khi nguồn thiếu, drift, rủi ro hoặc không rõ tác động. Tiếp tục phần an toàn độc lập.
- Kho công khai. Không đưa bí mật, PII, dữ liệu khách hàng, credential, log thô, dump hoặc IP/hostname thật chưa được duyệt vào Git. Khi có lộ lọt, ngừng ghi, giữ bằng chứng đã khử định danh và chuyển xử lý thu hồi/rotate.
- Trước sửa đọc đủ file, pin ref/blob, kiểm diff và invariant. Kiểm thử đúng delta, kiểm link, bí mật và dữ liệu bảo toàn. Không ghi đè stale, force push, bypass bảo vệ hay rewrite lịch sử. Sau push xác minh nội dung remote. Tác giả không tự nghiệm thu độc lập.
- Báo sự thật theo phạm vi và bằng chứng; phân biệt quan sát live, test giả lập, lịch sử và phần chưa biết. Chỉ ghi SENT khi có kênh gửi thực, ACK khi có receipt đúng task/phiên. Bàn giao kết quả hoặc blocker cụ thể với nguồn, tác động và chủ trì. Không đăng ký task/report/evidence trong CATALOG.

## Nguồn bắt buộc khi có điều kiện

| Khi làm | Đọc đầy đủ trước phần phụ thuộc |
|---|---|
| Điều phối, phân công, ghi dùng chung, review, thay đổi quyền hoặc chi phí | [Workflow](rules/AGENT_WORKFLOW.md) và quyết định A0 có hiệu lực |
| Git write, release, credential hoặc dữ liệu nhạy cảm | [Security](rules/REPOSITORY_SECURITY.md); thao tác Git đọc thêm [CONTRIBUTING](CONTRIBUTING.md) |
| Lưu, tái sử dụng, chuyển hoặc xóa dữ liệu quản trị | [Lifecycle](rules/DATA_LIFECYCLE_CONTEXT.md), các nguồn quyền và tham chiếu cần bảo toàn |
| Routing, dependency trạng thái, STOP/HOLD hoặc release | [STATE](STATE.md), nguồn live/authority tương ứng. Với KNG, đọc [snapshot](program/current.json) và [release gate](program/kng/release_state.py). Exact approval, main tree, merge parents và remote readback độc lập là bắt buộc; thiếu thì STOP dispatch. |
| Production, VPS, paid, destructive hoặc merge | Quyết định đúng phạm vi, [Workflow](rules/AGENT_WORKFLOW.md), runbook/rollback và bằng chứng trạng thái mới nhất. Merge cần reviewer khác tác giả, CI và remote readback theo gate. |

Đọc nguồn dùng để quyết định đến hết file. Nếu bị cắt, lấy các khoảng liên tục cùng blob; thiếu thì PARTIAL_READ và dừng phần phụ thuộc. Chỉ reuse nội dung đã đọc đủ khi còn truy cập được, blob/version giống nhau, đúng phạm vi và chưa có quyết định thay thế. Kiểm freshness bằng ref/metadata. Blob, quyền, task, vai trò, rủi ro hoặc dependency đổi, nguồn thiếu/truncated hoặc có nghi vấn thì đọc lại phần cần. Cache không thay live preflight, STOP/HOLD hoặc rollback.
