export const minute = 60_000;
export const day = 1440 * minute;
export const light = "claude-haiku-5-5";
export const strong = "claude-sonnet-5-5";

export type ProviderMode = "anthropic" | "anthropic-compatible";

export const defaults = {
  advertising: { startHour: 7, endHour: 22, perContactMs: 7 * day, daily: 8, spacingMs: 112 * minute,
    footer: "Nhắn DỪNG NHẬN TIN để không nhận ưu đãi",
    optOutWords: ["stop", "huy", "dung", "unsubscribe"],
    optOutPhrases: [
      ...["dung", "ngung", "stop"].flatMap(verb => [
        "gui", "nhan", "nhan tin", "nhan uu dai", "gui tin", "gui quang cao", "gui uu dai", "gui khuyen mai",
        "nhan quang cao", "nhan khuyen mai", "nhan qc", "gui qc", "nt", "gui tn", "gui tin nhan",
      ].map(object => verb + " " + object)),
      ...["khong", "ko", "k", "khong muon"].flatMap(verb => [
        "nhan", "nhan tin", "nhan uu dai", "nhan quang cao", "nhan khuyen mai", "nhan qc", "nhan tn", "nhan tin nhan",
      ].map(object => verb + " " + object)),
      "huy dang ky", "huy dk", "huy nhan tin", "huy nhan quang cao",
    ] },
  invitations: { weeklyDailyLimits: [1, 2, 3], spacingMs: 60 * minute, interestMs: 7 * day },
  anomaly: { windowMs: 15 * minute, starts: 5, errors: 3 },
  scheduling: { pollMs: 15_000, maxInboundAgeMs: day, maxQueued: 500, maxJobsPerTick: 10, maxText: 1500 },
  budget: {
    creditUsd: 200, stopUsd: 195, downgrade: 0.7, inboundOnly: 0.9, cycleStartDay: 1,
    // Inclusive percentages of stopUsd. At the cap or budgetStop, every new
    // channel write is held. Customer replies stay queued for a fresh AI decision.
    holdNotice: "Ngân sách AI đang bị chặn. Lượt gửi tạm dừng và tin khách chưa trả lời vẫn ở hàng chờ.",
    provider: "anthropic" as ProviderMode, compatibleDailyUsd: 0, compatibleRateMultiplier: 1,
    inputOverheadTokens: 2048, maxEstimatedInputTokens: 100_000,
    batchMultiplier: 0.5, maxOutputTokens: 256, maxPayloadBytes: 16_384,
    source: "https://platform.claude.com/docs/en/about-claude/pricing", checked: "2026-11-26",
    // Nanodollars per token. Only the standard tier is admitted; use long-tier rates
    // to reconcile Haiku usage if a provider breaches the request estimate.
    models: {
      [light]: { input: 100, output: 500, creation: 125, read: 10 },
      [strong]: { input: 2000, output: 10000, creation: 2500, read: 100 }
    },
    byAgent: { router: strong, support: light, crm: light, campaign: strong, community: light,
      listen: light, sales: strong, report: light }
  }
};
export type Config = typeof defaults;
export const agents = ["support", "crm", "campaign", "community", "listen", "sales", "report"] as const;
export type Agent = typeof agents[number];

export function vietnam(now: number) {
  const shifted = new Date(now + 7 * 60 * minute);
  return { date: shifted.toISOString().slice(0, 10), hour: shifted.getUTCHours(), midnight: Math.floor(+shifted / day) * day - 7 * 60 * minute };
}
