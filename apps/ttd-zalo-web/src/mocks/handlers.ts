import { http, HttpResponse } from "msw";
import {
  can,
  roleLabels,
  type Action,
  type Operator,
  type ConfirmedQuote,
  type Role,
} from "../api";
import { approvedPriceList, calculateQuote } from "../quote";
import { demoRouter, initialWorkspace } from "./data";

const state = structuredClone(initialWorkspace);
const sessionKey = "ttd-zalo-demo-role";
const prefix = "/api/v1";
const error = (status: number, message: string) =>
  HttpResponse.json({ message }, { status });
const isRole = (value: unknown): value is Role =>
  typeof value === "string" && Object.hasOwn(roleLabels, value);
const operator = (role: Role): Operator => ({
  id: "demo-" + role,
  label: roleLabels[role] + " (mẫu)",
  role,
});
function session() {
  const role = sessionStorage.getItem(sessionKey);
  return isRole(role) ? operator(role) : null;
}
function denied(action?: Action) {
  const current = session();
  if (!current) return error(401, "Cần đăng nhập.");
  if (action && !can(current.role, action))
    return error(403, "Vai trò hiện tại không có quyền thao tác.");
}

export const handlers = [
  http.get(prefix + "/session", () => {
    const current = session();
    return current ? HttpResponse.json(current) : error(401, "Cần đăng nhập.");
  }),
  http.post(prefix + "/session", async ({ request }) => {
    const body = (await request.json().catch(() => null)) as {
      demoRole?: unknown;
    } | null;
    if (!isRole(body?.demoRole))
      return error(400, "Chọn tài khoản giả lập hợp lệ.");
    sessionStorage.setItem(sessionKey, body.demoRole);
    return HttpResponse.json(operator(body.demoRole));
  }),
  http.delete(prefix + "/session", () => {
    sessionStorage.removeItem(sessionKey);
    return new HttpResponse(null, { status: 204 });
  }),
  http.get(prefix + "/workspace", () => denied() ?? HttpResponse.json(state)),
  http.post(
    prefix + "/conversations/:id/approve",
    async ({ params, request }) => {
      const failure = denied("approve");
      if (failure) return failure;
      const input = (await request.json().catch(() => null)) as {
        version?: number;
        text?: string;
      } | null;
      const item = state.conversations.find(({ id }) => id === params.id);
      if (!item) return error(404, "Không tìm thấy hội thoại.");
      if (item.delivery !== "draft" || item.version !== input?.version)
        return error(409, "Nháp đã đổi trạng thái hoặc phiên bản.");
      if (
        typeof input.text !== "string" ||
        !input.text.trim() ||
        input.text.length > 2000
      )
        return error(400, "Nội dung nháp không hợp lệ.");
      const customer = state.customers.find(({ id }) => id === item.customerId);
      const channel = state.channels.find(({ id }) => id === item.channel);
      if (
        customer?.optOut !== "none" ||
        customer.consent.support !== "granted" ||
        channel?.state !== "online"
      ) {
        return error(
          409,
          "Chính sách liên hệ hoặc trạng thái kênh đang chặn gửi.",
        );
      }
      item.draft = input.text.trim();
      item.delivery = "queued";
      item.version++;
      return HttpResponse.json(item);
    },
  ),
  http.get(
    prefix + "/agent-router",
    () => denied("restrictedRead") ?? HttpResponse.json(demoRouter),
  ),
  http.get(
    prefix + "/settings",
    () => denied("restrictedRead") ?? HttpResponse.json({ adsEnabled: false }),
  ),
  ...["/quotes", "/quotes/oa-send"].map((path) =>
    http.post(prefix + path, async ({ request }) => {
      const send = path.endsWith("/oa-send");
      const failure = denied("quote");
      if (failure) return failure;
      const input = (await request
        .json()
        .catch(() => null)) as ConfirmedQuote | null;
      const product = state.products.find(({ id }) => id === input?.productId);
      const customer = state.customers.find(
        ({ id }) => id === input?.customerId,
      );
      if (!input || !product || !customer)
        return error(400, "Khách hàng hoặc sản phẩm không hợp lệ.");
      if (
        input.confirmed !== true ||
        !approvedPriceList(product) ||
        input.priceList !== product.approvedPriceList
      ) {
        return error(409, "Cần xác nhận và dùng bảng giá đã duyệt hiện hành.");
      }
      if (
        send &&
        (customer.optOut !== "none" ||
          customer.consent.quote !== "granted" ||
          !state.conversations.some(
            (item) => item.customerId === customer.id && item.channel === "oa",
          ) ||
          state.channels.find((item) => item.id === "oa")?.state !== "online")
      ) {
        return error(
          409,
          "Chính sách liên hệ hoặc trạng thái kênh đang chặn gửi báo giá.",
        );
      }
      try {
        const { customerId, productId, unit, quantity } = input;
        const quote = {
          id: "BG-" + String(state.quotes.length + 1).padStart(3, "0"),
          customerId,
          productId,
          unit,
          quantity,
          ...calculateQuote(product, input),
          ...(send ? { delivery: "queued" as const } : {}),
        };
        state.quotes.unshift(quote);
        return HttpResponse.json(quote, { status: 201 });
      } catch (err) {
        return error(400, (err as Error).message);
      }
    }),
  ),
  http.post(prefix + "/work-items", async ({ request }) => {
    const failure = denied("task");
    if (failure) return failure;
    const input = (await request.json().catch(() => null)) as {
      title?: string;
      agent?: string;
    } | null;
    if (
      typeof input?.title !== "string" ||
      !input.title.trim() ||
      input.title.length > 250 ||
      !state.agents.some(({ label }) => label === input.agent)
    )
      return error(400, "Phiếu việc không hợp lệ.");
    const item = {
      id: "PV-" + String(state.workItems.length + 1).padStart(3, "0"),
      title: input.title.trim(),
      agent: input.agent!,
      status: "new" as const,
    };
    state.workItems.unshift(item);
    return HttpResponse.json(item, { status: 201 });
  }),
  http.post(prefix + "/room-messages", async ({ request }) => {
    const failure = denied("task");
    if (failure) return failure;
    const input = (await request.json().catch(() => null)) as {
      text?: string;
    } | null;
    const current = session();
    if (!current || !can(current.role, "task"))
      return error(403, "Vai trò hiện tại không có quyền thao tác.");
    if (
      typeof input?.text !== "string" ||
      !input.text.trim() ||
      input.text.length > 1000
    ) {
      return error(400, "Nội dung trao đổi không hợp lệ.");
    }
    const item = {
      id: "RT-" + (state.roomMessages.length + 1),
      author: current.label,
      text: input.text.trim(),
    };
    state.roomMessages.push(item);
    return HttpResponse.json(item, { status: 201 });
  }),
  http.post(prefix + "/channels/nick/stop", () => {
    const failure = denied("stop");
    if (failure) return failure;
    const channel = state.channels.find(({ id }) => id === "nick")!;
    channel.state = "stopped";
    channel.detail = "Đã bật kill switch";
    return HttpResponse.json(channel);
  }),
  http.post(prefix + "/deletion-requests", async ({ request }) => {
    const failure = denied("privacy");
    if (failure) return failure;
    const input = (await request.json().catch(() => null)) as {
      customerId?: string;
      reason?: string;
    } | null;
    const customer = state.customers.find(({ id }) => id === input?.customerId);
    if (
      !customer ||
      typeof input?.reason !== "string" ||
      !input.reason.trim() ||
      input.reason.length > 500
    )
      return error(400, "Khách hàng hoặc lý do không hợp lệ.");
    if (
      state.deletionRequests.some(
        ({ customerId }) => customerId === customer.id,
      )
    )
      return error(409, "Đã tồn tại yêu cầu cho khách này.");
    const item = {
      id: "YX-" + (state.deletionRequests.length + 1),
      customerId: customer.id,
      reason: input.reason.trim(),
      status: "requested" as const,
    };
    state.deletionRequests.unshift(item);
    return HttpResponse.json(item, { status: 201 });
  }),
];
