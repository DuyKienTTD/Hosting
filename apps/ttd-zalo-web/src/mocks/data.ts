import type { Workspace } from "../api";

export const initialWorkspace: Workspace = {
  adsEnabled: false,
  customers: [
    {
      id: "KH-001",
      label: "Khách A",
      segment: "Nhà thầu",
      followUp: "Xác nhận chiều dài nẹp cho công trình mẫu",
      optOut: "none",
      consent: { support: "granted", quote: "granted", marketing: "unknown" },
    },
    {
      id: "KH-002",
      label: "Khách B",
      segment: "Đại lý",
      followUp: "Chờ xác minh yêu cầu ngừng nhận tin",
      optOut: "review",
      consent: { support: "granted", quote: "unknown", marketing: "unknown" },
    },
    {
      id: "KH-003",
      label: "Khách C",
      segment: "Chủ nhà",
      followUp: "Dừng liên hệ",
      optOut: "stop",
      consent: {
        support: "withdrawn",
        quote: "withdrawn",
        marketing: "withdrawn",
      },
    },
  ],
  conversations: [
    {
      id: "CH-001",
      customerId: "KH-001",
      subject: "Nẹp đồng cho cầu thang",
      channel: "oa",
      time: "09:42",
      message:
        "Mình cần 12 mét nẹp đồng cho cầu thang. Một thanh dài bao nhiêu?",
      draft:
        "Dạ, mẫu NĐ-01 dài 2,5 m/thanh. Anh/chị cho em xin kích thước rãnh để em kiểm tra mẫu phù hợp trước khi báo giá nhé.",
      version: 1,
      delivery: "draft",
    },
    {
      id: "CH-002",
      customerId: "KH-002",
      subject: "Kiểm tra giao tin",
      channel: "nick",
      time: "09:16",
      message: "Bên mình đang xem lại mẫu bản lề.",
      draft: "",
      version: 2,
      delivery: "unknown_delivery",
    },
    {
      id: "CH-003",
      customerId: "KH-003",
      subject: "Yêu cầu dừng nhận tin",
      channel: "oa",
      time: "08:54",
      message: "Dừng nhắn tin cho tôi.",
      draft: "",
      version: 1,
      delivery: "blocked",
      reason: "Khách đã yêu cầu dừng liên hệ.",
    },
  ],
  products: [
    {
      id: "ND-01",
      label: "Nẹp đồng chữ T · NĐ-01",
      millimetresPerBar: 2500,
      barsPerSet: 4,
      vndPerMetre: 120000,
    },
    {
      id: "NN-02",
      label: "Nẹp nhôm chữ L · NN-02",
      millimetresPerBar: 3000,
      barsPerSet: 5,
      vndPerMetre: 75000,
    },
  ],
  quotes: [
    {
      id: "BG-001",
      customerId: "KH-001",
      productId: "ND-01",
      unit: "bar",
      quantity: 2,
      totalMillimetres: 5000,
      totalVnd: 600000,
    },
  ],
  roomMessages: [
    {
      id: "RT-1",
      author: "Claude",
      text: "@A1 kiểm tra nguồn quy cách NĐ-01 trước khi bàn giao báo giá mẫu.",
    },
    {
      id: "RT-2",
      author: "A1",
      text: "Đang đối chiếu chiều dài thanh với danh mục sản phẩm.",
    },
  ],
  workItems: [
    {
      id: "PV-001",
      title: "Kiểm tra nguồn thông số NĐ-01",
      agent: "A1",
      status: "active",
    },
    {
      id: "PV-002",
      title: "Duyệt nội dung bàn giao ca",
      agent: "Claude",
      status: "review",
    },
    { id: "PV-003", title: "Rà soát mẫu báo giá", agent: "A2", status: "new" },
  ],
  channels: [
    {
      id: "oa",
      label: "Zalo OA",
      state: "online",
      detail: "Kênh tư vấn chính · OpenAPI",
    },
    {
      id: "nick",
      label: "Nick Zalo phụ",
      state: "online",
      detail: "Worker Windows · Có heartbeat",
    },
    {
      id: "bot",
      label: "Zalo Bot",
      state: "offline",
      detail: "Pilot nhóm nhỏ · Chưa kết nối",
    },
  ],
  deletionRequests: [],
  agents: [
    { label: "Claude", role: "Điều phối", status: "Sẵn sàng" },
    { label: "A1", role: "Kỹ thuật", status: "Đang làm" },
    { label: "A2", role: "Sản phẩm", status: "Sẵn sàng" },
  ],
  router: {
    provider: "anthropic-compatible",
    budgetVnd: 100000,
    usedVnd: 24000,
    model: "Mô hình pilot (giả lập)",
  },
  activity: [
    { day: "T2", received: 18, answered: 13 },
    { day: "T3", received: 25, answered: 19 },
    { day: "T4", received: 20, answered: 14 },
    { day: "T5", received: 34, answered: 28 },
    { day: "T6", received: 30, answered: 24 },
    { day: "T7", received: 39, answered: 33 },
    { day: "CN", received: 27, answered: 22 },
  ],
};
