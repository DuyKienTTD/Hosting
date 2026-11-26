// @vitest-environment node
import { afterAll, afterEach, beforeAll, expect, it, vi } from "vitest";
import { setupServer } from "msw/node";
import { createHandlers } from "./mocks/handlers";

const server = setupServer();
const hour = 3600000;
let role = "owner";
let now = Date.parse("2026-11-26T09:00:00Z");

beforeAll(() => {
  vi.stubGlobal("sessionStorage", { getItem: () => role });
  server.listen({ onUnhandledRequest: "error" });
});
afterEach(() => {
  server.resetHandlers();
  role = "owner";
  now = Date.parse("2026-11-26T09:00:00Z");
});
afterAll(() => {
  server.close();
  vi.unstubAllGlobals();
});

function configure(ageHours: number, monthlyQuota = 1) {
  const last = now - ageHours * hour;
  server.use(
    ...createHandlers({
      origin: "http://localhost",
      clock: () => now,
      monthlyQuota,
      lastOaInteractions: { "KH-001": last, "KH-003": last },
    }),
  );
}

function send(customerId = "KH-001", extra = {}) {
  return fetch("http://localhost/api/v1/quotes/oa-send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      customerId,
      productId: "ND-01",
      quantity: 2,
      unit: "bar",
      confirmed: true,
      priceList: "BG-ND-2026-01",
      ...extra,
    }),
  });
}

async function block(res: Response, code: string) {
  expect(res.status).toBe(409);
  expect(await res.json()).toMatchObject({ code });
}

async function workspace() {
  const response = await fetch("http://localhost/api/v1/workspace");
  return response.json();
}

it.each(["owner", "sales"])(
  "áp dụng các mốc OA khi gọi trực tiếp với %s",
  async (operator) => {
    role = operator;
    for (const age of [47, 48, 49, 6 * 24 + 23, 7 * 24, 7 * 24 + 1, 8 * 24]) {
      configure(age);
      const response = await send("KH-001", {
        lastInteractionAt: now,
        remainingMonthlyQuota: 500,
      });
      if (age < 7 * 24) {
        expect(response.status).toBe(201);
        expect(await response.json()).toMatchObject({ delivery: "queued" });
      } else {
        await block(response, "oa_window_expired");
      }
    }
  },
);

it("xếp hàng đồng thời chỉ tiêu một suất quota, sau đó workspace báo hết", async () => {
  configure(49);
  const responses = await Promise.all([send(), send()]);
  expect(responses.map((response) => response.status).sort()).toEqual([
    201, 409,
  ]);
  await block(
    responses.find((response) => response.status === 409)!,
    "quota_exhausted",
  );
  expect((await workspace()).customers[0].oaQuoteBlock).toBe("quota_exhausted");
});

it("trong 48 giờ không dùng quota tháng và ngoài 48 giờ chặn khi đã hết", async () => {
  configure(47, 0);
  expect((await send()).status).toBe(201);
  now += 2 * hour;
  await block(await send(), "quota_exhausted");
});

it("kiểm tra lại đồng hồ server khi yêu cầu tới sau khi workspace đã tải", async () => {
  configure(167);
  expect((await workspace()).customers[0].oaQuoteBlock).toBeNull();
  now += 2 * hour;
  await block(await send(), "oa_window_expired");
  expect((await workspace()).customers[0].oaQuoteBlock).toBe(
    "oa_window_expired",
  );
});

it("opt-out chặn cả khi thời điểm hợp lệ và quota còn", async () => {
  configure(47);
  await block(await send("KH-003"), "oa_policy_denied");
});

it("thiếu thời điểm hợp lệ thì chặn", async () => {
  configure(-1);
  await block(await send(), "oa_interaction_missing");
});

it.each(["support", "a0"])("API từ chối vai trò %s", async (operator) => {
  configure(47);
  role = operator;
  expect((await send()).status).toBe(403);
});
