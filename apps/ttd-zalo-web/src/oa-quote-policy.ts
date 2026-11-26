export type OaQuoteBlock =
  | "oa_policy_denied"
  | "oa_interaction_missing"
  | "oa_window_expired"
  | "quota_exhausted";

export const oaQuoteBlockLabels: Record<OaQuoteBlock, string> = {
  oa_policy_denied:
    "Chưa đủ điều kiện gửi qua OA. Kiểm tra consent báo giá, yêu cầu dừng liên hệ và trạng thái kênh.",
  oa_interaction_missing: "Chưa xác minh được lần tương tác OA cuối.",
  oa_window_expired: "Ngoài cửa sổ 7 ngày",
  quota_exhausted: "Hết quota tháng",
};

type Admission =
  | { window: "within_48h" | "48h_to_7d" }
  | { code: OaQuoteBlock };
export type OaQuoteGuard = (input: {
  contactAllowed: boolean;
  lastInteractionAt: number | undefined;
  now: number;
  remainingMonthlyQuota: number;
}) => Admission;

const hour = 60 * 60 * 1000;

// Same window boundaries as PR #78. The backend integration supplies the real Guard and durable quota admission.
export const checkOaQuote: OaQuoteGuard = ({
  contactAllowed,
  lastInteractionAt,
  now,
  remainingMonthlyQuota,
}) => {
  if (!contactAllowed) return { code: "oa_policy_denied" };
  if (
    lastInteractionAt === undefined ||
    !Number.isFinite(lastInteractionAt) ||
    !Number.isFinite(now) ||
    lastInteractionAt > now
  )
    return { code: "oa_interaction_missing" };
  const age = now - lastInteractionAt;
  if (age >= 7 * 24 * hour) return { code: "oa_window_expired" };
  if (age < 48 * hour) return { window: "within_48h" };
  return remainingMonthlyQuota > 0
    ? { window: "48h_to_7d" }
    : { code: "quota_exhausted" };
};
