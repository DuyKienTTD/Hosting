import type { Product, QuoteInput, Unit } from "./api";

export const unitLabels: Record<Unit, string> = {
  metre: "Mét",
  bar: "Thanh",
  set: "Bộ",
};
export const money = (value: number) =>
  new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(
    value,
  );
export const number = (value: number) =>
  new Intl.NumberFormat("vi-VN").format(value);

export function calculateQuote(
  product: Product,
  input: Pick<QuoteInput, "unit" | "quantity">,
) {
  const { quantity, unit } = input;
  const units = {
    metre: 1000,
    bar: product.millimetresPerBar,
    set: product.millimetresPerBar * product.barsPerSet,
  };
  const totalMillimetres = Math.round(quantity * units[unit]);
  if (
    !Number.isFinite(quantity) ||
    quantity <= 0 ||
    quantity > 10000 ||
    !Object.hasOwn(units, unit) ||
    (unit === "metre"
      ? Math.abs(quantity * 1000 - totalMillimetres) > 1e-7
      : !Number.isInteger(quantity))
  ) {
    throw new Error(
      "Nhập từ 0,001 đến 10.000 mét hoặc số nguyên thanh/bộ từ 1 đến 10.000.",
    );
  }
  return {
    totalMillimetres,
    totalVnd: Math.round((totalMillimetres * product.vndPerMetre) / 1000),
  };
}
