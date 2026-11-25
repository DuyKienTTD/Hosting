import type { Agent, Config } from "./config.js";
import { day, vietnam } from "./config.js";
import type { ChannelAdapter, Request, Result } from "./channel.js";
import { Budget } from "./budget.js";
import { Store } from "./store.js";

export type Kind = "reply" | "advertising" | "invite" | "group_post" | "group_create" | "group_moderate";
export type Proposal = {
  agent: Agent; kind: Kind; id: string; target: string; text?: string; message?: string;
  revision: number; epoch: number; groupApproved?: boolean; origin?: string; thread?: string; memberIds?: string[];
};
export class Guard {
  constructor(private store: Store, private channel: ChannelAdapter, private config: Config,
    private clock: () => number, private budget = new Budget(store, config.budget, clock)) {}

  failure(now = this.clock()) {
    this.store.atomic(() => {
      const { db } = this.store;
      db.prepare("INSERT INTO failures VALUES(?)").run(now);
      db.prepare("DELETE FROM failures WHERE at<?").run(now - this.config.anomaly.windowMs);
      if (Number(db.prepare("SELECT count(*) n FROM failures").get()?.n) >= this.config.anomaly.errors) this.pause(now);
    });
  }
  spam() { this.store.atomic(() => this.pause(this.clock())); }
  private pause(now: number) {
    this.store.set("global", 1);
    this.store.set("epoch", this.store.setting("epoch") + 1);
    this.store.notice("channel-paused", now, "Kênh đã tự tạm dừng.");
  }
  private deny(p: Proposal, target: string, friend: boolean | undefined, now: number): string | undefined {
    const { db } = this.store;
    const policy = this.store.policy(target, p.agent, now);
    const contact = this.store.contact(target);
    if (this.store.stopped(p.agent) || p.epoch !== this.store.setting("epoch")) return "stopped";
    if (p.kind.startsWith("group_")) {
      if (p.agent !== "community" || !p.groupApproved) return "group_denied";
    } else {
      if (p.revision !== policy.revision || !policy.send) return "consent";
      if (p.kind === "invite") {
        if (p.agent !== "sales" || friend || !contact?.interest || now - contact.interest > this.config.invitations.interestMs ||
          contact.opted_out || db.prepare("SELECT 1 FROM outbound WHERE target=? AND kind='invite' AND state IN ('started','sent','unknown','failed')").get(target)) return "invite_denied";
      } else if (friend === false) return "not_friend";
      if (p.kind === "reply" && (p.agent !== "support" || !policy.respond ||
        !db.prepare("SELECT 1 FROM inbound WHERE id=? AND target=? AND received>=?").get(p.origin ?? "", target, now - this.config.scheduling.maxInboundAgeMs))) return "reply_denied";
      if (p.kind === "advertising" && (!["sales","campaign"].includes(p.agent) || !contact?.ads || contact.opted_out ||
        (p.agent === "sales" && !contact.accepted))) return "advertising_consent";
    }

    const recent = (kind: Kind, since: number, who?: string) => Number(db.prepare(
      "SELECT count(*) n FROM outbound WHERE kind=? AND at>=? AND state IN ('started','sent','unknown','failed') AND (? IS NULL OR target=?)")
      .get(kind, since, who ?? null, who ?? null)?.n);
    const local = vietnam(now);
    if (p.kind === "advertising") {
      const limits = this.config.advertising;
      if (local.hour < limits.startHour || local.hour >= limits.endHour) return "hours";
      if (recent(p.kind, now - limits.perContactMs + 1, target) || recent(p.kind, now - limits.spacingMs + 1) ||
        recent(p.kind, local.midnight) >= limits.daily) return "ad_limit";
    }
    if (p.kind === "invite") {
      const limits = this.config.invitations;
      const start = this.store.setting("firstInvite") || now;
      const week = Math.min(limits.weeklyDailyLimits.length - 1, Math.floor(Math.max(0, now - start) / (7 * day)));
      if (recent(p.kind, local.midnight) >= limits.weeklyDailyLimits[week] || recent(p.kind, now - limits.spacingMs + 1)) return "invite_limit";
    }
    const count = Number(db.prepare("SELECT count(*) n FROM outbound WHERE at>=? AND state IN ('started','sent','unknown','failed')")
      .get(now - this.config.anomaly.windowMs)?.n);
    if (count >= this.config.anomaly.starts) {
      this.pause(now);
      return "anomaly";
    }
  }
  async dispatch(p: Proposal) {
    const target = this.store.hash(p.target);
    const { db } = this.store;
    const key = this.store.hash(p.id);
    const group = p.kind.startsWith("group_");
    const lookup = { key, target: p.target, thread: p.thread };
    const local = group ? undefined : this.channel.localContact?.(lookup);
    const preflight = this.store.atomic(() => {
      const now = this.clock();
      if (this.store.stopped(p.agent) || p.epoch !== this.store.setting("epoch")) return "stopped";
      if (db.prepare("SELECT 1 FROM outbound WHERE id=?").get(key)) return "duplicate";
      if (this.budget.blocked(now)) return "budget_held";
      if (local && !local.ok) return local.error;
      return this.deny(p, target, local?.value.friend, now);
    });
    if (preflight) return preflight;
    let friend = false;
    if (!group) {
      let result;
      try { result = await this.channel.getContact(lookup); }
      catch { this.failure(); return "channel_error"; }
      if (!result.ok || result.value.id !== p.target) { this.failure(); return "channel_error"; }
      friend = result.value.friend === true;
    }
    // Persist before starting any transport. A crash leaves a non-retryable reservation.
    const reserved = db.prepare("INSERT OR IGNORE INTO outbound VALUES(?,?,?,?,?,'reserved')")
      .run(key, target, p.agent, p.kind, this.clock());
    if (!reserved.changes) return "duplicate";
    let pending: Promise<Result> | undefined;
    const decision = this.store.atomic(() => {
      const now = this.clock();
      const denial = this.budget.blocked(now) ? "budget_held" : this.deny(p, target, friend, now);
      if (denial) {
        db.prepare("DELETE FROM outbound WHERE id=? AND state='reserved'").run(key);
        return denial;
      }
      db.prepare("UPDATE outbound SET at=?,state='started' WHERE id=?").run(now, key);
      if (p.kind === "invite" && !this.store.setting("firstInvite")) this.store.set("firstInvite", now);
      const request: Request = { key, target: p.target, message: p.message, thread: p.thread, memberIds: p.memberIds,
        text: p.kind === "advertising" ? `${p.text}\n\n${this.config.advertising.footer}` : p.text };
      const methods = {
        reply: "sendMessage", advertising: "sendMessage", invite: "sendFriendRequest",
        group_post: "postToGroup", group_create: "createGroup", group_moderate: "moderateGroup",
      } as const;
      try { pending = this.channel[methods[p.kind]](request); }
      catch { pending = Promise.resolve({ ok: false, error: "unknown_delivery" }); }
    });
    if (decision) return decision;
    let outcome: Result;
    try { outcome = await pending!; }
    catch { outcome = { ok: false, error: "unknown_delivery" }; }
    const state = outcome.ok ? "sent" : outcome.error === "unknown_delivery" ? "unknown" : "failed";
    db.prepare("UPDATE outbound SET state=? WHERE id=?").run(state, key);
    if (!outcome.ok) this.failure();
    return state;
  }
}
