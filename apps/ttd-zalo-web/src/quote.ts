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

export function hasDimensions(product: Product) {
  return (
    Number.isSafeInteger(product.millimetresPerBar) &&
    product.millimetresPerBar > 0 &&
    Number.isSafeInteger(product.barsPerSet) &&
    product.barsPerSet > 0
  );
}

export function approvedPriceList(product?: Product) {
  return product &&
    Number.isSafeInteger(product.vndPerMetre) &&
    product.vndPerMetre > 0
    ? product.approvedPriceList
    : null;
}

export function validQuoteQuantity(unit: Unit, quantity: number) {
  return (
    Object.hasOwn(unitLabels, unit) &&
    Number.isFinite(quantity) &&
    quantity <= 10000 &&
    (unit === "metre"
      ? quantity >= 0.001 &&
        Math.abs(quantity * 1000 - Math.round(quantity * 1000)) <= 1e-7
      : quantity >= 1 && Number.isInteger(quantity))
  );
}

export function calculateQuote(
  product: Product,
  input: Pick<QuoteInput, "unit" | "quantity">,
) {
  if (!hasDimensions(product))
    throw new Error("Thiếu kích thước hoặc quy cách sản phẩm.");
  const { quantity, unit } = input;
  const units = {
    metre: 1000,
    bar: product.millimetresPerBar,
    set: product.millimetresPerBar * product.barsPerSet,
  };
  const totalMillimetres = Math.round(quantity * units[unit]);
  if (!validQuoteQuantity(unit, quantity)) {
    throw new Error(
      "Nhập từ 0,001 đến 10.000 mét hoặc số nguyên thanh/bộ từ 1 đến 10.000.",
    );
  }
  return {
    totalMillimetres,
    totalVnd: Math.round((totalMillimetres * product.vndPerMetre) / 1000),
  };
}
