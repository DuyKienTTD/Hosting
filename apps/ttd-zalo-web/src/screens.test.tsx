import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Inbox, Privacy, Quotes } from "./screens";
import { initialWorkspace } from "./mocks/data";
import { calculateQuote } from "./quote";
import type { Role } from "./api";

afterEach(cleanup);
const props = (role: Role = "owner") => ({
  data: structuredClone(initialWorkspace),
  user: { id: "demo", label: "Mẫu", role },
  run: vi.fn(async () => {}),
  busy: false,
  refresh: 0,
});

describe("Quy đổi báo giá", () => {
  const product = initialWorkspace.products[0];
  it.each([
    ["metre", 5],
    ["bar", 2],
    ["set", 0.5],
  ] as const)("kiểm tra %s", (unit, quantity) => {
    if (unit === "set") {
      expect(() => calculateQuote(product, { unit, quantity })).toThrow();
      expect(calculateQuote(product, { unit, quantity: 1 })).toEqual({
        totalMillimetres: 10000,
        totalVnd: 1200000,
      });
    } else {
      expect(calculateQuote(product, { unit, quantity })).toEqual({
        totalMillimetres: 5000,
        totalVnd: 600000,
      });
    }
  });
  it("cập nhật số mét khi chọn bộ", () => {
    render(<Quotes {...props("sales")} />);
    fireEvent.change(screen.getByLabelText("Đơn vị"), {
      target: { value: "set" },
    });
    expect(screen.getByText("20 m quy đổi")).toBeTruthy();
  });
});

describe("Kiểm soát thao tác", () => {
  it("yêu cầu xác nhận lại sau khi sửa nháp", () => {
    render(<Inbox {...props("support")} selected="CH-001" />);
    const button = screen.getByRole<HTMLButtonElement>("button", {
      name: /Duyệt và/,
    });
    expect(button.disabled).toBe(true);
    fireEvent.click(screen.getByRole("checkbox"));
    expect(button.disabled).toBe(false);
    fireEvent.change(screen.getByLabelText("Nháp AI"), {
      target: { value: "Nội dung đã sửa." },
    });
    expect(button.disabled).toBe(true);
  });
  it("chặn cả khi người dùng xác nhận nhưng opt-out cần duyệt", () => {
    const fixture = props();
    fixture.data.customers[0].optOut = "review";
    render(<Inbox {...fixture} selected="CH-001" />);
    expect(screen.getByRole<HTMLInputElement>("checkbox").disabled).toBe(true);
  });
  it("unknown_delivery không có thao tác gửi lại", () => {
    render(<Inbox {...props()} selected="CH-002" />);
    expect(screen.getByText(/Chưa xác định tin đã giao/)).toBeTruthy();
    expect(screen.queryByRole("button")).toBeNull();
  });
  it("vai trò CSKH chỉ xem được mục quyền riêng tư", () => {
    render(<Privacy {...props("support")} />);
    expect(
      screen.getByRole("heading", { name: "Consent theo mục đích" }),
    ).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Yêu cầu xóa" })).toBeNull();
  });
});

it.each([
  ["oa_window_expired", "Ngoài cửa sổ 7 ngày"],
  ["quota_exhausted", "Hết quota tháng"],
] as const)("khóa gửi OA và hiển thị %s", (code, label) => {
  const fixture = props("sales");
  fixture.data.customers[0].oaQuoteBlock = code;
  render(<Quotes {...fixture} />);
  fireEvent.change(screen.getByRole("combobox", { name: /Khách hàng/ }), {
    target: { value: "KH-001" },
  });
  fireEvent.click(screen.getByRole("checkbox"));
  expect(
    screen.getByRole<HTMLButtonElement>("button", { name: "Lưu báo giá" })
      .disabled,
  ).toBe(false);
  expect(
    screen.getByRole<HTMLButtonElement>("button", {
      name: "Duyệt & gửi qua OA",
    }).disabled,
  ).toBe(true);
  expect(screen.getByText(label)).toBeTruthy();
});
