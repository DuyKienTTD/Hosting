import type { IncomingMessage, ServerResponse } from "node:http";
import type { Config } from "../config.js";
import { json, readJson, type Operator } from "./http.js";
import { Guard } from "../guard.js";
import type { Store } from "../store.js";
import type { OaRuntimeChannel } from "../channels/oa/adapter.js";

export type Selection = {
  customerId: string;
  productId: string;
  quantity: number;
  unit: "metre" | "bar" | "set";
  priceList: string;
};
type ApprovedQuote = {
  target: string;
  origin: string;
  totalMillimetres: number;
  totalVnd: number;
};
type Dependencies = {
  store: Store;
  channel: OaRuntimeChannel;
  config: Config;
  clock?: () => number;
  // The host verifies the session, request origin and current operator role.
  authenticate(request: IncomingMessage): Promise<Operator | undefined>;
  // Resolve verified OA identity, quote consent, inbound origin and approved catalogue totals.
  resolve(selection: Selection): Promise<ApprovedQuote | undefined>;
  record?(id: string, selection: Selection, totals: ApprovedQuote, actor: string): void;
};

const reasons = {
  oa_policy_denied: "Chính sách liên hệ hoặc trạng thái kênh đang chặn gửi báo giá.",
  oa_interaction_missing: "Chưa xác minh được lần tương tác OA cuối.",
  oa_window_expired: "Ngoài cửa sổ 7 ngày",
  quota_exhausted: "Hết quota tháng",
} as const;

export async function selection(request: IncomingMessage): Promise<Selection | undefined> {
  const input = await readJson(request);
  if (input?.confirmed !== true || !(input.unit === "metre" || input.unit === "bar" || input.unit === "set") ||
    typeof input.quantity !== "number" || !Number.isFinite(input.quantity) || input.quantity < 0.001 || input.quantity > 10000 ||
    (input.unit === "metre"
      ? Math.abs(input.quantity * 1000 - Math.round(input.quantity * 1000)) > 1e-7
      : !Number.isInteger(input.quantity)) ||
    ![input.customerId, input.productId, input.priceList].every(value =>
      typeof value === "string" && value.length <= 180 && value.trim())) return;
  const { customerId, productId, quantity, unit, priceList } = input;
  return { customerId: customerId as string, productId: productId as string, quantity, unit, priceList: priceList as string };
}

export function oaQuotes({ store, channel, config, authenticate, resolve, record, clock = Date.now }: Dependencies) {
  if (!store.db.backend) throw Error("POSTGRES_CONFIGURATION_REQUIRED");
  const guard = new Guard(store, channel, config, clock);
  return {
    // Workspace uses the same read-only policy projection. Only dispatch reserves quota.
    block: (target: string) => channel.quoteBlock(target, clock()),
    async handle(request: IncomingMessage, response: ServerResponse) {
      if (request.url !== "/api/v1/quotes/oa-send") return false;
      if (request.method !== "POST") return json(response, 405, { message: "Phương thức không hợp lệ." });
      const session = await authenticate(request);
      if (!session) return json(response, 401, { message: "Cần đăng nhập." });
      if (session.role !== "owner" && session.role !== "sales") return json(response, 403, { message: "Vai trò hiện tại không có quyền gửi báo giá." });
      const input = await selection(request);
      if (!input) return json(response, 400, { message: "Dữ liệu hoặc xác nhận báo giá không hợp lệ." });
      const quote = await resolve(input);
      if (!quote) return json(response, 409, { message: "Khách, consent hoặc bảng giá đã duyệt không hợp lệ." });
      const { target, origin, totalMillimetres, totalVnd } = quote;
      if (!Number.isSafeInteger(totalMillimetres) || totalMillimetres < 1 || !Number.isSafeInteger(totalVnd) || totalVnd < 1) {
        return json(response, 409, { message: "Quy cách hoặc giá đã duyệt không hợp lệ." });
      }
      const id = "oa-quote:" + store.hash(JSON.stringify([target, origin, input, totalMillimetres, totalVnd]));
      const outcome = await guard.dispatch({
        agent: "support", kind: "reply", purpose: "oa_quote", id, origin, target, thread: target,
        text: `Báo giá ${input.productId}: ${totalMillimetres / 1000} m, tổng ${totalVnd} VND.`,
        epoch: store.setting("epoch"), revision: store.policy(store.hash(target), "support", clock()).revision,
      });
      if (outcome === "sent" || outcome === "unknown" || outcome === "failed" || outcome === "duplicate") {
        record?.(id, input, quote, session.id);
      }
      if (outcome === "sent") {
        const { priceList: _priceList, ...display } = input;
        return json(response, 201, { ...display, id, totalMillimetres, totalVnd, delivery: "sent" });
      }
      if (outcome === "duplicate" || outcome === "unknown" || outcome === "failed") {
        return json(response, outcome === "duplicate" ? 409 : 502, {
          code: outcome === "unknown" ? "unknown_delivery" : outcome,
          message: outcome === "unknown" ? "Chưa rõ trạng thái giao. Kiểm tra send_log trước khi xử lý." : "Báo giá đã được xử lý hoặc lượt gửi thất bại. Kiểm tra send_log.",
        });
      }
      const code = outcome === "quota_exhausted" ? outcome : channel.quoteBlock(target, clock()) ?? "oa_policy_denied";
      return json(response, 409, { code, message: reasons[code] });
    },
  };
}
