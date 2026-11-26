import { classifyOptOut, hasNegatedStop } from "./opt-out.js";
import { randomUUID } from "node:crypto";
import { extractSkus, FakeProvider as GroundedDraft, questionDate, validatedDraft } from "../../ttd-zalo-assistant/src/ai.js";
import { validField } from "../../ttd-zalo-assistant/src/customer.js";
import { Budget } from "./budget.js";
import type { ChannelAdapter, Event } from "./channel.js";
import { day, vietnam, type Agent, type Config } from "./config.js";
import { Guard, type Kind } from "./guard.js";
import { isAgent, requestInputEstimate, type Provider } from "./provider.js";
import { Store } from "./store.js";

const choices = {
  support: ["none", "answer"], crm: ["none", "need", "follow-up"], campaign: ["none", "offer", "check-in", "new-product"],
  community: ["none", "apply"], listen: ["none", "product-interest"], sales: ["none", "invite", "offer"],
  report: ["none", "highlight-activity", "highlight-blocks"],
} as const;
const deferredSend = ["hours", "ad_limit", "budget_held"];
type ScheduleKind = "advertising" | "group_post" | "group_create" | "group_moderate";
export type Schedule = { key: string; agent: "campaign" | "community"; kind: ScheduleKind; at: number;
  target: string; text?: string; message?: string; memberIds?: string[]; campaign?: "offer" | "check-in" | "new-product" };
function sanitized(text: string) {
  return text.replace(/(?:\+?\d[\d.() -]{7,}\d)/gu, "[số đã ẩn]")
    .replace(/[\w.+-]+@[\w.-]+\.[a-z]+/giu, "[email đã ẩn]").replace(/https?:\/\/\S+/giu, "[link đã ẩn]");
}

export class Runtime {
  readonly guard: Guard;
  readonly budget: Budget;
  private pending = new Map<string, { event: Event; revision: number; epoch: number }>();
  private busy = false;
  private reading = false;
  constructor(readonly store: Store, private channel: ChannelAdapter, private provider: Provider,
    private config: Config, private clock = Date.now, private schedule: readonly Schedule[] = [], private reviewOaReplies = false) {
    this.budget = new Budget(store, config.budget, clock);
    this.guard = new Guard(store, channel, config, clock, this.budget);
  }

  private async decide(id: string, agent: Agent | "router", data: object, options: readonly string[], inbound = false) {
    if (this.store.stopped(agent)) return;
    const reservation = this.budget.reserve(id, agent, inbound, false, requestInputEstimate(this.config.budget, data, options));
    if (!reservation) return;
    try {
      const decision = await this.provider.decide({ ...reservation, data, choices: options });
      if (!this.budget.settle(id, decision.usage)) return;
      return options.includes(decision.choice) ? decision.choice : "none";
    } catch (error) {
      if (error instanceof Error && ["PROVIDER_MODEL", "PROVIDER_USAGE"].includes(error.message)) this.budget.hold();
      this.store.notice("ai-unavailable", this.clock(), "Một yêu cầu AI chưa đối soát được.");
      return this.config.budget.manualReviewOnBudget ? undefined : "none";
    }
  }

  private disableAds(target: string) {
    // Called inside the same transaction as inbound persistence or AI admission.
    this.store.optOut(target);
    this.store.db.prepare("DELETE FROM jobs WHERE target=?").run(target);
  }

  private flagOptOut(target: string, id: string) {
    this.store.pauseAdsForReview(target, id);
    this.store.notice("review-opt-out:" + id, this.clock(), "Cần xem lại ý định ngừng nhận ưu đãi của tin nhắn này.");
  }

  private discardPending(contact: string) {
    for (const [key, item] of this.pending) if (item.event.contact === contact) this.pending.delete(key);
  }


  ingest(event: Event) {
    const now = this.clock();
    if (!["dm", "group", "accepted", "spam"].includes(event.kind) || !Number.isSafeInteger(event.at) ||
      event.at > now || typeof event.contact !== "string" || !event.contact || typeof event.thread !== "string" ||
      !event.thread || typeof event.id !== "string" || !event.id) return;
    if ((event.kind === "dm" || event.kind === "group") && typeof event.text !== "string") return;
    const { store } = this;
    const id = store.eventKey(event.contact, event.thread, event.id);
    const target = store.hash(event.contact);
    const optOut = event.kind === "dm" ? classifyOptOut(event.text, this.config.advertising) : "none";
    const record = store.atomic(() => {
      if (!store.db.prepare("INSERT OR IGNORE INTO inbound VALUES(?,?,?)").run(id, target, event.at).changes) {
        if (this.pending.has(id) || event.at < now - this.config.scheduling.maxInboundAgeMs) return;
        const job = store.db.prepare("SELECT revision,epoch FROM jobs WHERE id=? AND status='queued'").get(id);
        if (typeof job?.revision === "number" && typeof job.epoch === "number") {
          return { revision: job.revision, epoch: job.epoch };
        }
        return;
      }
      if (optOut === "stop") {
        this.disableAds(target);
        return;
      }
      if (optOut === "review") this.flagOptOut(target, id);
      if (event.kind === "spam") return { spam: true } as const;
      if (event.at < now - this.config.scheduling.maxInboundAgeMs) return;
      if (event.kind === "accepted") {
        if (!store.db.prepare("SELECT 1 FROM send_log WHERE target=? AND kind='invite' AND at<=? AND state IN ('reserved','sent','unknown_delivery')").get(target, event.at)) return;
        if (!store.db.prepare("UPDATE contact SET accepted=1,revision=revision+1 WHERE target=? AND opted_out=0 AND accepted=0").run(target).changes) return;
      }
      const agent = event.kind === "dm" ? "support" : event.kind === "group" ? "listen" : "sales";
      const policy = store.policy(target, agent, now);
      if (event.kind === "dm" && policy.retain) {
        store.retainMessage(target, event.thread, event.channel ?? "oa", id, event.text, event.at);
      }
      if (!policy.respond) return;
      const epoch = store.setting("epoch");
      store.db.prepare("INSERT INTO jobs VALUES(?,?,?,'queued',?,?,?,NULL)").run(id, event.kind, target, event.at, policy.revision, epoch);
      return { revision: policy.revision, epoch };
    });
    if (!record) {
      if (optOut === "stop") this.discardPending(event.contact);
      return;
    }
    if ("spam" in record) { this.guard.spam(); return; }
    if (this.pending.size >= this.config.scheduling.maxQueued) {
      store.db.prepare("UPDATE jobs SET status='overflow' WHERE id=?").run(id);
      store.notice("queue-overflow", now, "Hàng chờ AI đã đầy.");
      return;
    }
    this.pending.set(id, { event, ...record });
  }

  private async run(id: string, payload: { event: Event; revision: number; epoch: number }) {
    const { event, revision, epoch } = payload;
    const { store } = this;
    const now = this.clock();
    const target = store.hash(event.contact);
    const allowed: Agent[] = event.kind === "dm" ? ["support", "crm"] : event.kind === "group" ? ["listen"] : ["sales"];
    const valid = (agent: Agent) => {
      const policy = store.policy(target, agent, this.clock());
      return policy.respond && revision === policy.revision && epoch === store.setting("epoch");
    };
    const send = (agent: Agent, kind: Kind, text?: string) =>
      this.guard.dispatch({ id, agent, kind, text, target: event.contact, revision, epoch, origin: id, thread: event.kind === "dm" ? event.thread : undefined });
    if (event.at < now - this.config.scheduling.maxInboundAgeMs || !allowed.some(valid)) return true;
    const contact = store.contact(target, now);
    const inbound = event.kind === "dm";
    const question = event.kind === "dm" || event.kind === "group" ? sanitized(event.text).slice(0, this.config.scheduling.maxText) : "";
    const permitted = allowed.filter(agent => valid(agent) && (agent !== "crm" || !!contact?.retain));
    const stored = store.db.prepare("SELECT body FROM jobs WHERE id=?").get(id)?.body;
    let attempt = id;
    let routed: string | undefined;
    if (typeof stored === "string") {
      if (stored.startsWith("retry:")) {
        const [retry, route] = stored.split("|", 2);
        attempt = id + "-" + retry;
        routed = route;
      } else routed = stored;
    }
    const holdReply = () => {
      if (inbound && this.config.budget.manualReviewOnBudget) {
        this.store.db.prepare("UPDATE jobs SET status='review',body='ai_admission_hold' WHERE id=? AND status='queued'").run(id);
        this.store.notice("ai-review:" + id, this.clock(), "Tin nhắn đang chờ người duyệt do giới hạn hoặc lỗi AI.");
        return true;
      }
      // Leave the ledger and transport key intact. Only invalidate the AI decision.
      if (inbound && routed) {
        store.db.prepare("UPDATE jobs SET body=? WHERE id=?").run("retry:" + randomUUID(), id);
      }
      return false;
    };
    if (this.budget.blocked()) return holdReply();
    if (inbound) {
      const profile = await this.channel.getContact({ key: id, target: event.contact }).catch(() => undefined);
      if (this.budget.blocked()) return holdReply();
      if (!profile?.ok) { this.guard.failure(); return true; }
      if (!profile.value.friend || profile.value.id !== event.contact) return true;
    }
    if (typeof routed !== "string") {
      if (!permitted.some(valid)) return true;
      const options: string[] = [...permitted, "none"];
      if (inbound) {
        options.push("review-opt-out");
        if (!hasNegatedStop(event.text)) options.push("opt-out");
      }
      routed = await this.decide(attempt + "-route", "router", { event: event.kind, question }, options, inbound);
      if (!routed) return this.config.budget.manualReviewOnBudget ? holdReply() : false;
      if (inbound && (routed === "opt-out" || routed === "review-opt-out")) {
        const disabled = store.atomic(() => {
          if (this.clock() - event.at > this.config.scheduling.maxInboundAgeMs || !permitted.some(valid) ||
            !store.db.prepare("SELECT 1 FROM jobs WHERE id=? AND target=? AND status='queued'").get(id, target)) return false;
          if (routed === "opt-out") {
            this.disableAds(target);
            return true;
          }
          this.flagOptOut(target, id);
          return false;
        });
        if (disabled) this.discardPending(event.contact);
        return true;
      }
      store.db.prepare("UPDATE jobs SET body=? WHERE id=?").run(attempt === id ? routed : attempt.slice(id.length + 1) + "|" + routed, id);
    }
    if (routed === "sales-ready" && valid("sales")) {
      const outcome = await send("sales", "advertising",
        "Cảm ơn bạn đã kết bạn với TTD METAL. Bạn muốn xem bộ sưu tập lan can sắt mỹ thuật hay nhận báo giá theo mẫu?");
      return !deferredSend.includes(outcome);
    }
    if (typeof routed !== "string" || !isAgent(routed) || !permitted.includes(routed) || !valid(routed)) return true;
    if (routed === "listen") {
      const canInvite = /(?:kết bạn|liên hệ|inbox|nhắn riêng).*(?:tôi|mình|em)|(?:tôi|mình|em).*(?:kết bạn|inbox|nhắn riêng)/iu.test(question)
        && /lan can|sản phẩm|báo giá|mẫu|sku/iu.test(question);
      await this.batch(id, "listen", { question: question.slice(0, 400) });
      if (!canInvite || !valid("listen") || !valid("sales")) return true;
      if (this.store.db.prepare("SELECT 1 FROM ledger WHERE id=?").get(id + "-sales")) return true;
      const decision = await this.decide(id + "-sales", "sales", { intent: "asked-for-contact", question }, choices.sales);
      if (decision === undefined) return false;
      if (decision === "invite" && valid("sales")) {
        store.db.prepare("UPDATE contact SET interest=? WHERE target=?").run(event.at, target);
        await send("sales", "invite");
      }
      return true;
    }
    const skuList = extractSkus(question);
    const sku = skuList.length === 1 ? skuList[0] : undefined;
    const date = questionDate(question, vietnam(now).date);
    const sources = routed === "support" ? [
      ...(sku ? store.knowledge.bySku(sku) : []), ...store.knowledge.policies(), ...store.knowledge.findDocuments(question, date, sku),
    ] : [];
    const draft = routed === "support" ? validatedDraft(new GroundedDraft(), { question, sku, date, sources }) : undefined;
    const decision = await this.decide(attempt + "-" + routed, routed,
      { event: event.kind, question, sourceIds: draft?.sourceIds, draftAction: draft?.action }, choices[routed], inbound && routed === "support");
    if (decision === undefined) return this.config.budget.manualReviewOnBudget ? holdReply() : false;
    if (!valid(routed)) return true;
    if (inbound && this.budget.blocked()) return holdReply();
    if (routed === "support" && decision === "answer" && draft && ["trả lời", "hỏi lại"].includes(draft.action)) {
      const text = draft.text + (draft.sourceIds.length ? "\nNguồn: " + draft.sourceIds.join(", ") : "");
      if (this.reviewOaReplies && event.channel === "oa") {
        store.db.prepare(`INSERT INTO web_reply_drafts(conversation_id,inbound_id,body)
          SELECT conversation_id,?,? FROM messages WHERE event_id=?
          ON CONFLICT(conversation_id,inbound_id) DO NOTHING`).run(id,text,id);
        return true;
      }
      const outcome = await send("support", "reply", text);
      if (outcome === "budget_held") return holdReply();
    } else if (routed === "crm" && validField(decision) && store.policy(target, "crm", this.clock()).retain && sku) {
      store.db.prepare("INSERT OR IGNORE INTO customer_field(target,source,kind,value,created) VALUES(?,?,?,?,?)")
        .run(target, id, decision, sku, now);
    } else if (routed === "sales" && decision === "offer") {
      const outcome = await send("sales", "advertising",
        "Cảm ơn bạn đã kết bạn với TTD METAL. Bạn muốn xem bộ sưu tập lan can sắt mỹ thuật hay nhận báo giá theo mẫu?");
      if (deferredSend.includes(outcome)) {
        store.db.prepare("UPDATE jobs SET body='sales-ready' WHERE id=?").run(id);
        return false;
      }
    }
    return true;
  }

  private batchId(id: string, agent: "listen" | "report") { return this.store.hash(agent + ":" + id).slice(0, 60); }
  private async batch(id: string, agent: "listen" | "report", data: object) {
    if (this.store.stopped(agent)) return;
    const key = this.batchId(id, agent);
    if (this.config.budget.provider === "anthropic-compatible") {
      const choice = await this.decide(key, agent, data, choices[agent]);
      if (choice && choice !== "none") this.store.notice("batch:" + key, this.clock(), choice);
      return;
    }
    const reservation = this.budget.reserve(key, agent, false, true, requestInputEstimate(this.config.budget, data, choices[agent]));
    if (!reservation) return;
    try { this.budget.batch(key, await this.provider.submit(key, { ...reservation, data, choices: choices[agent] })); }
    catch { this.store.notice("batch-unavailable", this.clock(), "Yêu cầu batch chưa đối soát được."); }
  }
  private async pollBatches() {
    if (this.store.setting("budgetStop") || this.config.budget.provider === "anthropic-compatible") return;
    const { db } = this.store;
    for (const row of db.prepare("SELECT id,batch,model FROM ledger WHERE state='batch' AND provider='anthropic' LIMIT 25").all()) {
      const id = String(row.id);
      const key = String(row.batch);
      try {
        const outcome = await this.provider.poll(id, key, [...choices.listen, ...choices.report], String(row.model));
        if (!outcome) continue;
        if (!this.budget.settle(id, outcome.usage)) return;
        if (outcome.choice !== "none") this.store.notice("batch:" + id, this.clock(), outcome.choice);
      } catch (error) {
        if (error instanceof Error && ["PROVIDER_MODEL", "PROVIDER_USAGE"].includes(error.message)) this.budget.hold();
        this.store.notice("batch-poll", this.clock(), "Chưa lấy được kết quả batch.");
      }
    }
  }
  private async scheduled(now: number) {
    for (const task of this.schedule) {
      if (task.at > now || task.at < now - day || this.store.stopped(task.agent)) continue;
      const id = "schedule:" + task.key;
      const target = this.store.hash(task.target);
      const revision = this.store.contact(target)?.revision ?? 0;
      const epoch = this.store.setting("epoch");
      const expected = task.agent === "campaign" ? task.campaign ?? "offer" : "apply";
      const { db } = this.store;
      let decision = db.prepare("SELECT body FROM jobs WHERE id=?").get(id)?.body;
      if (typeof decision !== "string") {
        decision = await this.decide(id, task.agent, { type: task.kind, template: expected }, [expected, "none"]);
        if (!decision) continue;
        db.prepare("INSERT OR IGNORE INTO jobs VALUES(?,?,?,'scheduled',?,?,?,?)")
          .run(id, task.kind, target, task.at, revision, epoch, decision);
      }
      const snapshot = db.prepare("SELECT revision,epoch,status FROM jobs WHERE id=?").get(id);
      if (decision !== expected || snapshot?.status !== "scheduled" || snapshot.revision !== revision ||
        snapshot.epoch !== epoch) continue;
      const outcome = await this.guard.dispatch({ ...task, id, revision, epoch, groupApproved: task.agent === "community" });
      if (!deferredSend.includes(outcome)) db.prepare("UPDATE jobs SET status=? WHERE id=?").run(outcome, id);
    }
  }
  async readChannel() {
    if (this.reading) return false;
    this.reading = true;
    try {
      const now = this.clock();
      const req = { key: String(now), target: "channel" };
      const reads = await Promise.allSettled([this.channel.receiveMessage(req), this.channel.onFriendAccepted(req)]);
      let okay = true;
      for (const [index, read] of reads.entries()) {
        if (read.status !== "fulfilled" || !read.value.ok) { this.guard.failure(); okay = false; continue; }
        for (const event of read.value.value) this.ingest(event);
        this.channel.acknowledge?.(index === 0 ? "message" : "friend");
      }
      return okay;
    } finally { this.reading = false; }
  }
  async tick(read = true) {
    if (this.busy) return false;
    this.busy = true;
    try {
      if (read && !await this.readChannel()) return false;
      const now = this.clock();
      for (const [id, payload] of [...this.pending].slice(0, this.config.scheduling.maxJobsPerTick)) {
        if (!this.pending.has(id)) continue;
        if (await this.run(id, payload)) {
          this.pending.delete(id);
          this.store.db.prepare("UPDATE jobs SET status='processed',body=NULL WHERE id=? AND status='queued'").run(id);
        } else if (this.pending.delete(id)) {
          this.pending.set(id, payload);
        }
      }
      await this.scheduled(now);
      await this.pollBatches();
      const { date, midnight } = vietnam(now);
      const reportKey = "report:" + date;
      if (!this.store.stopped("report") && !this.store.db.prepare("SELECT 1 FROM notices WHERE key=?").get(reportKey)) {
        const counts = this.store.db.prepare("SELECT kind,state,count(*) n FROM send_log WHERE at>=? AND at<? GROUP BY kind,state")
          .all(midnight - day, midnight);
        this.store.notice(reportKey, now, JSON.stringify({ date: vietnam(midnight - day).date, counts }));
      }
      const report = this.store.db.prepare("SELECT body FROM notices WHERE key=?").get(reportKey);
      if (report) await this.batch(date, "report", JSON.parse(String(report.body)));
      return true;
    } finally { this.busy = false; }
  }
}
