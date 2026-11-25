export const minute = 60_000;
export const day = 1440 * minute;
export const light = "claude-haiku-4-5-20251001";
export const strong = "claude-sonnet-4-6";

export const defaults = {
  advertising: { startHour: 7, endHour: 22, perContactMs: 7 * day, daily: 8, spacingMs: 112 * minute,
    footer: "nhắn KHÔNG để dừng nhận tin", optOut: ["không", "stop", "hủy", "huỷ", "dừng", "unsubscribe"] },
  invitations: { weeklyDailyLimits: [1, 2, 3], spacingMs: 60 * minute, interestMs: 7 * day },
  anomaly: { windowMs: 15 * minute, starts: 5, errors: 3 },
  scheduling: { pollMs: 15_000, maxInboundAgeMs: day, maxQueued: 500, maxJobsPerTick: 10, maxText: 1500 },
  budget: {
    creditUsd: 200, stopUsd: 195, downgrade: 0.7, inboundOnly: 0.9, cycleStartDay: 1,
    batchMultiplier: 0.5, maxOutputTokens: 256, maxPayloadBytes: 16_384,
    source: "https://platform.claude.com/docs/en/about-claude/pricing", checked: "2026-11-26",
    // Nanodollars per token. Reserve against the entire model context, including tool overhead.
    models: {
      [light]: { input: 1000, output: 5000, creation: 1250, read: 100, context: 200_000 },
      [strong]: { input: 3000, output: 15000, creation: 3750, read: 300, context: 1_000_000 }
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
