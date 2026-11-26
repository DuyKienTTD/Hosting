import type { Operator } from "./http.js";

/** Build financial response fields only for the authenticated owner. */
export function ownerAiCosts<T extends object>(operator: Operator, read: () => T): T | undefined {
  return operator.role === "owner" ? read() : undefined;
}
