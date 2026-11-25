import { day, light, vietnam, type Config } from "./config.js";
import type { Store } from "./store.js";

export type Usage = { input: number; output: number; creation: number; read: number };
export type Model = keyof Config["budget"]["models"];
const usd = 1_000_000_000;

export class Budget {
  constructor(private store: Store, private cfg: Config["budget"], private clock: () => number) {}
  cycle(at = this.clock()) {
    const date = vietnam(at).date;
    const [year, month, dateOfMonth] = date.split("-").map(Number);
    const start = this.cfg.cycleStartDay;
    const offset = dateOfMonth < start ? -1 : 0;
    const cycle = new Date(Date.UTC(year, month - 1 + offset, start)).toISOString().slice(0, 10);
    const left = (Date.UTC(year, month + offset, start) - Date.parse(date)) / day;
    return { cycle, date, left };
  }
  reserve(id: string, agent: keyof Config["budget"]["byAgent"], inbound: boolean, batch: boolean): { id: string; model: Model; batch: boolean } | undefined {
    return this.store.atomic(() => {
      const { db } = this.store;
      const { cycle, date, left } = this.cycle();
      if (this.store.setting("budgetStop") || db.prepare("SELECT 1 FROM ledger WHERE id=?").get(id)) return;
      const usage = db.prepare(`SELECT coalesce(sum(CASE WHEN cycle<>? OR date<? THEN amount ELSE 0 END),0) prior,
        coalesce(sum(CASE WHEN cycle=? AND date=? THEN amount ELSE 0 END),0) today FROM ledger
        WHERE cycle=? OR (cycle<? AND (settled_cycle=? OR state IN ('reserved','batch')))`).get(cycle, date, cycle, date, cycle, cycle, cycle)!;
      const prior = Number(usage.prior);
      const today = Number(usage.today);
      const cap = this.cfg.stopUsd * usd;
      const fraction = (prior + today) / cap;
      if (fraction >= 1) {
        this.store.notice(`budget:${cycle}`, this.clock(), "Đã chạm giới hạn an toàn của ngân sách AI.");
        return;
      }
      if (fraction > this.cfg.inboundOnly && !inbound) return;
      const model: Model = fraction > this.cfg.downgrade ? light : this.cfg.byAgent[agent] as Model;
      const rate = this.cfg.models[model];
      // Use on-demand rates for reservation even for batch. Unknown billing remains reserved.
      const amount = rate.context * Math.max(rate.input, rate.creation, rate.read) + this.cfg.maxOutputTokens * rate.output;
      if (today + amount > Math.floor((cap - prior) / left)) {
        if (prior + today + amount > cap) this.store.notice(`budget:${cycle}`, this.clock(), "Đã chạm giới hạn an toàn của ngân sách AI.");
        return;
      }
      db.prepare("INSERT INTO ledger(id,cycle,date,model,amount,state) VALUES(?,?,?,?,?,'reserved')")
        .run(id, cycle, date, model, amount);
      return { id, model, batch };
    });
  }
  batch(id: string, key: string) {
    this.store.db.prepare("UPDATE ledger SET batch=?,state='batch' WHERE id=? AND state='reserved'").run(key, id);
  }
  settle(id: string, usage: Usage) {
    this.store.atomic(() => {
      const { db } = this.store;
      const row = db.prepare("SELECT model,amount,state FROM ledger WHERE id=?").get(id);
      if (!row || !["reserved", "batch"].includes(String(row.state))) return;
      const rate = this.cfg.models[row.model as Model];
      const { input, output, creation, read } = usage;
      if ([input, output, creation, read].some(n => !Number.isSafeInteger(n) || n < 0) ||
        input + creation + read > rate.context || output > this.cfg.maxOutputTokens) {
        this.store.set("budgetStop", 1);
        this.store.notice("unknown-billing", this.clock(), "Anthropic trả số token ngoài hạn mức dự kiến.");
        return;
      }
      const onDemand = input * rate.input + output * rate.output + creation * rate.creation + read * rate.read;
      const amount = row.state === "batch" ? Math.ceil(onDemand * this.cfg.batchMultiplier) : onDemand;
      db.prepare("UPDATE ledger SET input=?,output=?,cache_write=?,cache_read=?,amount=?,state='settled',settled_cycle=? WHERE id=?")
        .run(input, output, creation, read, amount, this.cycle().cycle, id);
    });
  }
}
