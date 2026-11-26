import type { IncomingMessage, ServerResponse } from "node:http";
import type { Config } from "../config.js";
import { Guard } from "../guard.js";
import type { Store } from "../store.js";
import type { OaRuntimeChannel } from "../channels/oa/adapter.js";

type Selection = {
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
  authenticate(request: IncomingMessage): Promise<{ role: string } | undefined>;
  // Resolve verified OA identity, quote consent, inbound origin and approved catalogue totals.
  resolve(selection: Selection): Promise<ApprovedQuote | undefined>;
};

const reasons = {
  oa_policy_denied: "Chính sách liên hệ hoặc trạng thái kênh đang chặn gửi báo giá.",
  oa_interaction_missing: "Chưa xác minh được lần tương tác OA cuối.",
  oa_window_expired: "Ngoài cửa sổ 7 ngày",
  quota_exhausted: "Hết quota tháng",
} as const;

async function selection(request: IncomingMessage): Promise<Selection | undefined> {
  if (request.headers["content-type"]?.split(";")[0].trim() !== "application/json") return;
  const chunks: Buffer[] = [];
  let length = 0;
  for await (const value of request.iterator({ destroyOnReturn: false })) {
    const chunk = Buffer.from(value);
    length += chunk.length;
    if (length > 4096) return;
    chunks.push(chunk);
  }
  let input;
  try { input = JSON.parse(Buffer.concat(chunks).toString("utf8")); }
  catch { return; }
  if (input?.confirmed !== true || !["metre", "bar", "set"].includes(input.unit) ||
    !Number.isFinite(input.quantity) || input.quantity < 0.001 || input.quantity > 10000 ||
    (input.unit === "metre"
      ? Math.abs(input.quantity * 1000 - Math.round(input.quantity * 1000)) > 1e-7
      : !Number.isInteger(input.quantity)) ||
    ![input.customerId, input.productId, input.priceList].every(value =>
      typeof value === "string" && value.length <= 180 && value.trim())) return;
  const { customerId, productId, quantity, unit, priceList } = input;
  return { customerId, productId, quantity, unit, priceList };
}

export function oaQuotes({ store, channel, config, authenticate, resolve, clock = Date.now }: Dependencies) {
  if (!store.db.backend) throw Error("POSTGRES_CONFIGURATION_REQUIRED");
  const guard = new Guard(store, channel, config, clock);
  return {
    // Workspace uses the same read-only policy projection. Only dispatch reserves quota.
    block: (target: string) => channel.quoteBlock(target, clock()),
    async handle(request: IncomingMessage, response: ServerResponse) {
      if (request.url !== "/api/v1/quotes/oa-send") return false;
      const json = (status: number, value: object) => {
        response.writeHead(status, { "Content-Type": "application/json", "Cache-Control": "no-store" }).end(JSON.stringify(value));
        return true;
      };
      if (request.method !== "POST") return json(405, { message: "Phương thức không hợp lệ." });
      const session = await authenticate(request);
      if (!session) return json(401, { message: "Cần đăng nhập." });
      if (session.role !== "owner" && session.role !== "sales") return json(403, { message: "Vai trò hiện tại không có quyền gửi báo giá." });
      const input = await selection(request);
      if (!input) return json(400, { message: "Dữ liệu hoặc xác nhận báo giá không hợp lệ." });
      const quote = await resolve(input);
      if (!quote) return json(409, { message: "Khách, consent hoặc bảng giá đã duyệt không hợp lệ." });
      const { target, origin, totalMillimetres, totalVnd } = quote;
      if (!Number.isSafeInteger(totalMillimetres) || totalMillimetres < 1 || !Number.isSafeInteger(totalVnd) || totalVnd < 1) {
        return json(409, { message: "Quy cách hoặc giá đã duyệt không hợp lệ." });
      }
      const id = "oa-quote:" + store.hash(JSON.stringify([target, origin, input, totalMillimetres, totalVnd]));
      const outcome = await guard.dispatch({
        agent: "support", kind: "reply", purpose: "oa_quote", id, origin, target, thread: target,
        text: `Báo giá ${input.productId}: ${totalMillimetres / 1000} m, tổng ${totalVnd} VND.`,
        epoch: store.setting("epoch"), revision: store.policy(store.hash(target), "support", clock()).revision,
      });
      if (outcome === "sent") {
        const { priceList: _priceList, ...display } = input;
        return json(201, { ...display, id, totalMillimetres, totalVnd, delivery: "sent" });
      }
      if (outcome === "duplicate" || outcome === "unknown" || outcome === "failed") {
        return json(outcome === "duplicate" ? 409 : 502, {
          code: outcome === "unknown" ? "unknown_delivery" : outcome,
          message: outcome === "unknown" ? "Chưa rõ trạng thái giao. Kiểm tra send_log trước khi xử lý." : "Báo giá đã được xử lý hoặc lượt gửi thất bại. Kiểm tra send_log.",
        });
      }
      const code = outcome === "quota_exhausted" ? outcome : channel.quoteBlock(target, clock()) ?? "oa_policy_denied";
      return json(409, { code, message: reasons[code] });
    },
  };
}
