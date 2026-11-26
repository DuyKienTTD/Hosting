import { expect, test, type Page } from "@playwright/test";

const pages = [
  ["Tổng quan", "Hoạt động hội thoại"],
  ["Hộp thư khách", "Nẹp đồng cho cầu thang"],
  ["Báo giá", "Lập báo giá"],
  ["Khách hàng & theo sát", "Danh sách theo sát"],
  ["Phòng điều phối", "Tạo phiếu việc"],
  ["Agent & AI Router", "Hostinger AI Router"],
  ["Kênh Zalo", "Nick Zalo phụ"],
  ["Dữ liệu & quyền riêng tư", "Consent theo mục đích"],
] as const;

async function login(page: Page, role = "owner") {
  await page.goto("/");
  await page.getByLabel("Tài khoản giả lập").selectOption(role);
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(
    page.getByRole("heading", { name: "Tổng quan", exact: true }),
  ).toBeVisible();
}

async function open(page: Page, title: string) {
  const menu = page.getByRole("button", { name: "Mở điều hướng" });
  if (await menu.isVisible()) await menu.click();
  await page
    .getByRole("navigation")
    .getByRole("link", { name: title, exact: true })
    .click();
}

for (const [title, marker] of pages) {
  test("mở màn hình " + title, async ({ page }) => {
    await login(page);
    await open(page, title);
    await expect(
      page.getByRole("heading", { name: title, exact: true, level: 1 }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: marker, exact: true }),
    ).toBeVisible();
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(page.viewportSize()!.width);
  });
}

test("duyệt rồi xếp hàng và không duyệt lại một bản cũ", async ({ page }) => {
  await login(page, "support");
  await open(page, "Hộp thư khách");
  const approve = page.getByRole("button", { name: /Duyệt và/ });
  await expect(approve).toBeDisabled();
  await page.getByRole("checkbox").check();
  await approve.click();
  await expect(page.getByText("Trong hàng đợi", { exact: true })).toBeVisible();
  const status = await page.evaluate(
    async () =>
      (
        await fetch("/api/v1/conversations/CH-001/approve", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ version: 1, text: "Bản cũ" }),
        })
      ).status,
  );
  expect(status).toBe(409);
  await page.getByRole("link", { name: /Kiểm tra giao tin/ }).click();
  await expect(page.getByText(/Chưa xác định tin đã giao/)).toBeVisible();
  await expect(approve).toHaveCount(0);
});

test("bán hàng lưu báo giá và API từ chối kill switch", async ({ page }) => {
  await login(page, "sales");
  await open(page, "Báo giá");
  await page
    .getByRole("combobox", { name: /Khách hàng/ })
    .selectOption("KH-001");
  await page.getByLabel("Đơn vị").selectOption("set");
  await expect(page.getByText("20 m quy đổi")).toBeVisible();
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Lưu báo giá" }).click();
  await expect(page.getByText("BG-002 · KH-001")).toBeVisible();
  await open(page, "Kênh Zalo");
  await expect(
    page.getByRole("button", { name: "Bật kill switch" }),
  ).toHaveCount(0);
  expect(
    await page.evaluate(
      async () =>
        (await fetch("/api/v1/channels/nick/stop", { method: "POST" })).status,
    ),
  ).toBe(403);
});

test("Chủ dự án dừng nick, tạo phiếu và gửi yêu cầu xóa", async ({ page }) => {
  await login(page, "owner");
  await open(page, "Kênh Zalo");
  await page.getByRole("button", { name: "Bật kill switch" }).click();
  await page.getByRole("button", { name: "Xác nhận dừng nick" }).click();
  await expect(
    page.getByLabel("Trạng thái kênh").getByText("Đã dừng"),
  ).toBeVisible();
  await open(page, "Phòng điều phối");
  await page.getByLabel("Lời nhắn nội bộ").fill("@A1 kiểm tra bảng giá mẫu");
  await page.getByRole("button", { name: "Đăng trao đổi" }).click();
  await expect(
    page.getByRole("log").getByText("@A1 kiểm tra bảng giá mẫu"),
  ).toBeVisible();
  await page.getByLabel("Nội dung").fill("Đối chiếu mẫu dữ liệu");
  await page.getByRole("button", { name: "Tạo phiếu" }).click();
  await expect(
    page.getByText("Đối chiếu mẫu dữ liệu", { exact: true }),
  ).toBeVisible();
  await open(page, "Dữ liệu & quyền riêng tư");
  await page
    .getByRole("combobox", { name: /Khách hàng/ })
    .selectOption("KH-001");
  await page.getByLabel("Lý do").fill("Kiểm tra hồ sơ mẫu");
  await page.getByRole("button", { name: "Yêu cầu xóa", exact: true }).click();
  await expect(page.getByText("Đã yêu cầu", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Khách A · KH-001" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Đăng xuất" }).click();
  await expect(page.getByRole("heading", { name: "Đăng nhập" })).toBeVisible();
});

const sharedRoutes = [
  ["overview", "Tổng quan"],
  ["inbox", "Hộp thư khách"],
  ["quotes", "Báo giá"],
  ["customers", "Khách hàng & theo sát"],
  ["coordination", "Phòng điều phối"],
  ["channels", "Kênh Zalo"],
  ["privacy", "Dữ liệu & quyền riêng tư"],
] as const;

for (const role of ["owner", "support", "sales", "a0"]) {
  test("quyền truy cập theo vai trò " + role, async ({ page }) => {
    await login(page, role);
    for (const [route, title] of sharedRoutes) {
      await page.goto("/#" + route);
      await expect(
        page.getByRole("heading", { name: title, exact: true, level: 1 }),
      ).toBeVisible();
    }
    const permitted = role === "owner" || role === "a0";
    for (const [route, title, endpoint] of [
      ["agents", "Agent & AI Router", "/agent-router"],
      ["settings", "Cài đặt", "/settings"],
    ]) {
      await page.goto("/#" + route);
      await expect(
        page.getByRole("heading", {
          name: permitted ? title : "Không có quyền truy cập",
          exact: true,
          level: 1,
        }),
      ).toBeVisible();
      await expect(
        page
          .getByRole("navigation", { includeHidden: true })
          .getByRole("link", { name: title, exact: true, includeHidden: true }),
      ).toHaveCount(permitted ? 1 : 0);
      expect(
        await page.evaluate(
          async (path) => (await fetch("/api/v1" + path)).status,
          endpoint,
        ),
      ).toBe(permitted ? 200 : 403);
    }
    const workspace = await page.evaluate(async () =>
      (await fetch("/api/v1/workspace")).json(),
    );
    expect(workspace).not.toHaveProperty("router");
    if (role === "support" || role === "a0") {
      await page.goto("/#quotes");
      await expect(
        page.getByRole("button", { name: "Duyệt & gửi qua OA" }),
      ).toHaveCount(0);
      for (const path of [
        "/quotes",
        "/quotes/oa-send",
        "/channels/nick/stop",
      ]) {
        expect(
          await page.evaluate(
            async (endpoint) =>
              (await fetch("/api/v1" + endpoint, { method: "POST" })).status,
            path,
          ),
        ).toBe(403);
      }
    }
  });
}

test("cả hai nút báo giá khóa theo từng điều kiện và gửi OA sau xác nhận", async ({
  page,
}) => {
  await login(page, "sales");
  await open(page, "Báo giá");
  const save = page.getByRole("button", { name: "Lưu báo giá" });
  const send = page.getByRole("button", { name: "Duyệt & gửi qua OA" });
  const confirm = page.getByRole("checkbox");
  const locks = async (reason: string) => {
    await expect(save).toBeDisabled();
    await expect(send).toBeDisabled();
    await expect(page.getByText(reason, { exact: true })).toBeVisible();
  };
  await confirm.check();
  await locks("Chọn khách hàng.");
  await page
    .getByRole("combobox", { name: /Khách hàng/ })
    .selectOption("KH-001");
  await locks("Tích xác nhận báo giá.");
  await page.getByRole("spinbutton", { name: "Số lượng" }).clear();
  await confirm.check();
  await locks("Nhập số lượng hợp lệ.");
  await page.getByRole("spinbutton", { name: "Số lượng" }).fill("2");
  await page.getByLabel("Sản phẩm").selectOption("ND-03");
  await confirm.check();
  await locks("Thiếu kích thước hoặc quy cách sản phẩm.");
  await page.getByLabel("Sản phẩm").selectOption("NN-02");
  await confirm.check();
  await locks("Giá chưa có trong bảng giá đã duyệt.");
  await page.getByLabel("Sản phẩm").selectOption("ND-01");
  await confirm.check();
  for (const path of ["/quotes", "/quotes/oa-send"]) {
    const status = await page.evaluate(async (endpoint) => {
      const response = await fetch("/api/v1" + endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customerId: "KH-001",
          productId: "ND-01",
          unit: "bar",
          quantity: 2,
          priceList: "BG-ND-2026-01",
          confirmed: false,
        }),
      });
      return response.status;
    }, path);
    expect(status).toBe(409);
  }
  await expect(save).toBeEnabled();
  await expect(send).toBeEnabled();
  await send.click();
  await expect(page.getByRole("status")).toHaveText(
    "Đã duyệt và xếp hàng gửi qua OA.",
  );
  await expect(page.getByText(/Chờ gửi OA/)).toBeVisible();
  await locks("Tích xác nhận báo giá.");
});
