import type { Agent, Config } from "./config.js";
import { day, vietnam } from "./config.js";
import type { ChannelAdapter, ChannelError, Request, Result } from "./channel.js";
import { Budget } from "./budget.js";
import { consultationWindow } from "./channels/oa/webhook.js";
import { Store } from "./store.js";

export type Kind = "reply" | "advertising" | "invite" | "group_post" | "group_create" | "group_moderate";
export type Proposal = {
  agent: Agent; kind: Kind; id: string; target: string; text?: string; message?: string;
  purpose?: Request["purpose"] | "oa_inbox_reply";
  revision: number; epoch: number; groupApproved?: boolean; origin?: string; thread?: string; memberIds?: string[];
};
export type SendGuardOutcome =
  | "sent" | "failed" | "unknown" | "stopped" | "duplicate" | "budget_held"
  | "group_denied" | "consent" | "invite_denied" | "not_friend" | "reply_denied"
  | "advertising_consent" | "hours" | "ad_limit" | "invite_limit" | "anomaly"
  | "ads_disabled" | "channel_error" | "quota_exhausted" | ChannelError;

/** Server-side send admission and dispatch for approved proposals. */
export interface SendGuard {
  dispatch(proposal: Proposal): Promise<SendGuardOutcome>;
}

export class Guard implements SendGuard {
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
  private deny(p: Proposal, target: string, friend: boolean | undefined, now: number): SendGuardOutcome | undefined {
    const { db } = this.store;
    const policy = this.store.policy(target, p.agent, now);
    const contact = this.store.contact(target, now);
    if (this.store.stopped(p.agent) || p.epoch !== this.store.setting("epoch")) return "stopped";
    if (p.kind.startsWith("group_")) {
      if (p.agent !== "community" || !p.groupApproved) return "group_denied";
    } else {
      if (p.purpose && (contact?.opted_out || contact?.ads_paused_review)) return "consent";
      if (p.revision !== policy.revision || !policy.send) return "consent";
      if (p.kind === "invite") {
        if (p.agent !== "sales" || friend || !contact?.interest || now - contact.interest > this.config.invitations.interestMs ||
          contact.opted_out || db.prepare("SELECT 1 FROM send_log WHERE target=? AND kind='invite' AND state IN ('reserved','sent','unknown_delivery','failed','committed_before_revoke')").get(target)) return "invite_denied";
      } else if (friend === false) return "not_friend";
      if (p.kind === "reply") {
        if (p.agent !== "support" || !policy.respond) return "reply_denied";
        const earliest = now - (p.purpose ? consultationWindow : this.config.scheduling.maxInboundAgeMs);
        const source = p.purpose === "oa_inbox_reply"
          ? db.prepare("SELECT 1 FROM web_oa_projection WHERE origin_id=? AND target=? AND conversation_id IS NOT NULL AND received_ms>=?")
            .get(p.origin ?? "", target, earliest)
          : db.prepare("SELECT 1 FROM inbound WHERE id=? AND target=? AND received>=?").get(p.origin ?? "", target, earliest);
        if (!source) return "reply_denied";
      }
      if (p.kind === "advertising" && (!["sales","campaign"].includes(p.agent) || !contact?.ads || contact.opted_out || contact.ads_paused_review ||
        (this.store.db.backend && contact.ad_state !== "active") || (p.agent === "sales" && !contact.accepted))) return "advertising_consent";
    }

    const recent = (kind: Kind, since: number, who?: string) => Number(db.prepare(
      "SELECT count(*) n FROM send_log WHERE kind=? AND at>=? AND state IN ('reserved','sent','unknown_delivery','failed','committed_before_revoke') AND (? IS NULL OR target=?)")
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
    const count = Number(db.prepare("SELECT count(*) n FROM send_log WHERE at>=? AND state IN ('reserved','sent','unknown_delivery','failed','committed_before_revoke')")
      .get(now - this.config.anomaly.windowMs)?.n);
    if (count >= this.config.anomaly.starts) {
      this.pause(now);
      return "anomaly";
    }
  }
  private adsDisabled(p: Proposal) {
    if (p.kind !== "advertising") return false;
    const enabled = this.store.db.backend ? this.store.setting("ADS_ENABLED") === 1 : this.config.advertising.enabled;
    if (enabled) return false;
    this.store.notice("ads_disabled", this.clock(), "ads_disabled");
    return true;
  }

  async dispatch(p: Proposal): Promise<SendGuardOutcome> {

    const target = this.store.hash(p.target);
    const { db } = this.store;
    const key = this.store.hash(p.id);
    const group = p.kind.startsWith("group_");
    // Manual OA replies share the no-paid-overflow policy of approved quotations.
    const purpose = p.purpose === "oa_inbox_reply" ? "oa_quote" : p.purpose;
    const lookup = { key, target: p.target, thread: p.thread, purpose };
    const local = group ? undefined : this.channel.localContact?.(lookup);
    const preflight = this.store.atomic(() => {
      const now = this.clock();
      if (this.adsDisabled(p)) return "ads_disabled";
      if (this.store.stopped(p.agent) || p.epoch !== this.store.setting("epoch")) return "stopped";
      if (db.prepare("SELECT 1 FROM send_log WHERE id=?").get(key)) return "duplicate";
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
    let pending: Promise<Result> | undefined;
    const decision = this.store.admit(() => {
      const now = this.clock();
      const denial = this.adsDisabled(p) ? "ads_disabled"
        : db.prepare("SELECT 1 FROM send_log WHERE id=?").get(key) ? "duplicate"
        : this.budget.blocked(now) ? "budget_held" : this.deny(p, target, friend, now);
      if (denial) return denial;
      const admission = this.channel.admitSend?.(lookup, p.kind, now);
      if (admission && "denial" in admission) return admission.denial;
      if (!this.store.reserveSend(key, target, p.agent, p.kind, now, admission?.classification)) return "duplicate";
      if (p.kind === "invite" && !this.store.setting("firstInvite")) this.store.set("firstInvite", now);
    }, denial => {
      if (denial) return;
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
    this.store.atomic(() => {
      db.prepare("UPDATE send_log SET state=? WHERE id=? AND state='reserved'")
        .run(state === "unknown" ? "unknown_delivery" : state, key);
    });
    if (!outcome.ok) this.failure();
    return state;
  }
}
