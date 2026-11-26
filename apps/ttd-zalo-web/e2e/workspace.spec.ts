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
  await page.getByLabel("Khách hàng").selectOption("KH-001");
  await page.getByLabel("Đơn vị").selectOption("set");
  await expect(page.getByText("20 m quy đổi")).toBeVisible();
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

test("A0 dừng nick, tạo phiếu và gửi yêu cầu xóa", async ({ page }) => {
  await login(page, "a0");
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
  await page.getByLabel("Khách hàng").selectOption("KH-001");
  await page.getByLabel("Lý do").fill("Kiểm tra hồ sơ mẫu");
  await page.getByRole("button", { name: "Yêu cầu xóa", exact: true }).click();
  await expect(page.getByText("Đã yêu cầu", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Khách A · KH-001" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Đăng xuất" }).click();
  await expect(page.getByRole("heading", { name: "Đăng nhập" })).toBeVisible();
});
