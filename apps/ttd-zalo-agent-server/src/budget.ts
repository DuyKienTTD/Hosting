import { day, light, vietnam, type Config } from "./config.js";
import type { Store } from "./store.js";

export type Usage = { input: number; output: number; creation: number; read: number };
export type Model = keyof Config["budget"]["models"];
// Upper bound across supported live configurations, including unsettled requests
// started before a worker restarted with a lower configured output limit.
export const liveOutputCeiling = 256;
const usd = 1_000_000_000;
const legacyRates: Record<string, Config["budget"]["models"][Model]> = {
  "claude-haiku-4-5-20251001": { input: 1000, output: 5000, creation: 1250, read: 100 },
  "claude-sonnet-4-6": { input: 3000, output: 15000, creation: 3750, read: 300 },
};

export class Budget {
  private readonly attributed: boolean;
  constructor(private store: Store, private cfg: Config["budget"], private clock: () => number) {
    this.attributed = store.db.backend === "postgres" && !!store.db.prepare(
      "SELECT 1 FROM pg_attribute WHERE attrelid='ledger'::regclass AND attname='agent_role' AND NOT attisdropped",
    ).get();
  }
  cycle(at = this.clock()) {
    const date = vietnam(at).date;
    const [year, month, dateOfMonth] = date.split("-").map(Number);
    const start = this.cfg.cycleStartDay;
    const offset = dateOfMonth < start ? -1 : 0;
    const cycle = new Date(Date.UTC(year, month - 1 + offset, start)).toISOString().slice(0, 10);
    const left = (Date.UTC(year, month + offset, start) - Date.parse(date)) / day;
    return { cycle, date, left };
  }
  private balance(at: number) {
    const { cycle, date, left } = this.cycle(at);
    const usage = this.store.db.prepare(`SELECT coalesce(sum(CASE WHEN cycle<>? OR date<? THEN amount ELSE 0 END),0) prior,
      coalesce(sum(CASE WHEN cycle=? AND date=? THEN amount ELSE 0 END),0) today FROM ledger
      WHERE cycle=? OR (cycle<? AND (settled_cycle=? OR state IN ('reserved','batch')))`).get(cycle, date, cycle, date, cycle, cycle, cycle)!;
    return { cycle, date, left, prior: Number(usage.prior), today: Number(usage.today), cap: this.cfg.stopUsd * usd };
  }

  private notifyHold(cycle: string, at: number) {
    this.store.notice(`budget:${cycle}`, at, this.cfg.holdNotice);
  }

  private isBlocked(balance: ReturnType<Budget["balance"]>) {
    return Boolean(this.store.setting("budgetStop")) || balance.prior + balance.today >= balance.cap;
  }

  // The guard calls this inside its transport admission transaction.
  blocked(at = this.clock()) {
    const balance = this.balance(at);
    if (!this.isBlocked(balance)) return false;
    this.notifyHold(balance.cycle, at);
    return true;
  }

  reserve(id: string, agent: keyof Config["budget"]["byAgent"], inbound: boolean, batch: boolean, inputTokens: number): { id: string; model: Model; batch: boolean } | undefined {
    return this.store.atomic(() => {
      const { db } = this.store;
      const now = this.clock();
      const balance = this.balance(now);
      const { cycle, date, left, prior, today, cap } = balance;
      if (this.isBlocked(balance)) {
        this.notifyHold(cycle, now);
        return;
      }
      if (db.prepare("SELECT 1 FROM ledger WHERE id=?").get(id)) return;
      const fraction = (prior + today) / cap;
      if (fraction >= this.cfg.inboundOnly && !inbound) return;
      const model: Model = fraction >= this.cfg.downgrade && (this.cfg.allowedModels?.includes(light) ?? true) ? light : this.cfg.byAgent[agent] as Model;
      if (!Number.isSafeInteger(inputTokens) || inputTokens < 1 || inputTokens > this.cfg.maxEstimatedInputTokens) return;
      if (this.cfg.allowedModels && !this.cfg.allowedModels.includes(model)) return;
      const rate = this.cfg.models[model];
      const { provider, compatibleRateMultiplier, compatibleDailyUsd } = this.cfg;
      const multiplier = provider === "anthropic-compatible" ? compatibleRateMultiplier : 1;
      if (!Number.isFinite(multiplier) || multiplier < 1) return;
      // Reserve on-demand rates, including a possible five-minute cache write.
      const amount = Math.ceil((inputTokens * Math.max(rate.input, rate.creation, rate.read) +
        this.cfg.maxOutputTokens * rate.output) * multiplier);
      if (today + amount > Math.floor((cap - prior) / left)) {
        if (prior + today + amount > cap) this.notifyHold(cycle, now);
        return;
      }
      if (provider === "anthropic-compatible") {
        if (batch) return;
        const { dailyTokens, monthlyTokens } = this.cfg;
        if (dailyTokens || monthlyTokens) {
          const totals = db.prepare(`SELECT
            coalesce(sum(CASE WHEN date=? OR state IN ('reserved','batch') THEN tokens ELSE 0 END),0) AS daily,
            coalesce(sum(tokens),0) AS monthly FROM (
              SELECT date,state,CASE WHEN state IN ('reserved','batch')
                THEN coalesce(input_bound,100000)+?
                ELSE coalesce(input,0)+coalesce(output,0)+coalesce(cache_write,0)+coalesce(cache_read,0) END AS tokens
              FROM ledger WHERE provider=? AND (cycle=? OR settled_cycle=? OR state IN ('reserved','batch'))
            ) requests`).get(date, liveOutputCeiling, provider, cycle, cycle)!;
          const bound = inputTokens + liveOutputCeiling;
          if ((dailyTokens && Number(totals.daily) + bound > dailyTokens) ||
              (monthlyTokens && Number(totals.monthly) + bound > monthlyTokens)) {
            this.store.notice(`router-tokens:${date}`, now, "Đã chạm hạn mức token của AI Router.");
            return;
          }
        }
        const used = Number(db.prepare("SELECT coalesce(sum(amount),0) n FROM ledger WHERE date=? AND provider=?").get(date, provider)?.n);
        if (!Number.isFinite(compatibleDailyUsd) || compatibleDailyUsd <= 0 || used + amount > Math.floor(compatibleDailyUsd * usd)) {
          this.store.notice(`router-budget:${date}`, now, "Đã chạm hạn mức ngày của AI Router.");
          return;
        }
      }
      const columns = "id,cycle,date,model,amount,state,provider,rate_multiplier,input_bound";
      const values = "?,?,?,?,?,'reserved',?,?,?";
      db.prepare(this.attributed
        ? "INSERT INTO ledger(" + columns + ",agent_role) VALUES(" + values + ",?)"
        : "INSERT INTO ledger(" + columns + ") VALUES(" + values + ")")
        .run(id, cycle, date, model, amount, provider, multiplier, inputTokens, ...(this.attributed ? [agent] : []));
      return { id, model, batch };
    });
  }
  batch(id: string, key: string) {
    this.store.db.prepare("UPDATE ledger SET batch=?,state='batch' WHERE id=? AND state='reserved'").run(key, id);
  }
  hold() {
    this.store.set("budgetStop", 1);
    this.store.notice("unknown-billing", this.clock(), "Model hoặc usage vượt giới hạn đã xác minh. Hệ thống tạm dừng.");
  }
  settle(id: string, usage: Usage) {
    return this.store.atomic(() => {
      const { db } = this.store;
      const row = db.prepare("SELECT model,amount,state,input_bound,rate_multiplier,provider FROM ledger WHERE id=?").get(id);
      if (!row || !["reserved", "batch"].includes(String(row.state))) return false;
      const name = String(row.model);
      const rate = this.cfg.models[name as Model] ?? legacyRates[name];
      const { input, output, creation, read } = usage;
      if (!rate || [input, output, creation, read].some(n => !Number.isSafeInteger(n) || n < 0 || n > 1_000_000)) {
        this.hold();
        return false;
      }
      const totalInput = input + creation + read;
      const tier = name === light && totalInput > 100_000 ? 5 : 1;
      const onDemand = (input * rate.input + output * rate.output + creation * rate.creation + read * rate.read) * tier;
      const discount = row.state === "batch" && row.provider === "anthropic" ? this.cfg.batchMultiplier : 1;
      const amount = Math.ceil(onDemand * discount * Number(row.rate_multiplier));
      db.prepare("UPDATE ledger SET input=?,output=?,cache_write=?,cache_read=?,amount=?,state='settled',settled_cycle=? WHERE id=?")
        .run(input, output, creation, read, amount, this.cycle().cycle, id);
      if (amount > Number(row.amount) || (row.input_bound !== null && totalInput > Number(row.input_bound)) ||
        output > this.cfg.maxOutputTokens) {
        this.hold();
        return false;
      }
      return true;
    });
  }
}
