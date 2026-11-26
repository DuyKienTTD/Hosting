import { extractSkus, FakeProvider as GroundedDraft, validatedDraft } from "../../../ttd-zalo-assistant/src/ai.js";
import { Budget } from "../budget.js";
import { vietnam, type Config } from "../config.js";
import { requestInputEstimate, type Provider } from "../provider.js";
import type { InboxDraftReader } from "./oa-inbox.js";
import type { Store } from "../store.js";

const intents = ["price", "technical", "complaint", "other"] as const;
type Intent = typeof intents[number];
type Reason = "mock" | "budget" | "consent" | "unavailable" | "no_knowledge";
type State = "pending" | "generating" | "ready" | "needs_human" | "approved";
const handoff = "Bên em chưa có dữ liệu đã xác minh cho yêu cầu này. Em sẽ chuyển nhân viên phụ trách kiểm tra.";
const manual = "Nhân viên phụ trách sẽ kiểm tra và phản hồi yêu cầu của bạn.";
const projection = `d.id,d.conversation_id AS "conversationId",d.revision AS version,d.body AS text,
  d.ai_state AS state,d.ai_intent AS intent,d.ai_reason AS reason,d.ai_source_ids AS "sourceIds",d.delivery`;
const sourceJoin = `FROM web_reply_drafts d LEFT JOIN visible_messages m ON m.id=d.ai_message_id
  JOIN inbound i ON i.id=d.inbound_id`;
const visible = "(m.id IS NOT NULL OR (d.ai_message_id IS NULL AND d.ai_state='needs_human' AND d.ai_reason='consent'))";

export class OaAiDrafts implements InboxDraftReader {
  private readonly budget: Budget;
  constructor(private readonly store: Store, private readonly config: Config, private readonly provider: Provider,
    private readonly live: boolean, private readonly clock = Date.now) {
    this.budget = new Budget(store, config.budget, clock);
  }

  enabled() { return !this.store.setting("drafts"); }

  setEnabled(enabled: boolean) {
    this.store.atomic(() => {
      if (this.enabled() === enabled) return;
      this.store.set("drafts", Number(!enabled));
      this.store.set("drafts_epoch", this.store.setting("drafts_epoch") + 1);
    });
  }

  enqueue(inbound: string, conversation: string, retain: boolean, respond: boolean) {
    const { db } = this.store;
    if (!retain) {
      db.prepare(`INSERT INTO web_reply_drafts(conversation_id,inbound_id,body,ai_state,ai_reason)
        VALUES(?,?,'','needs_human','consent') ON CONFLICT(conversation_id,inbound_id) DO NOTHING`).run(conversation, inbound);
      return false;
    }
    const inserted = db.prepare(`INSERT INTO web_reply_drafts(conversation_id,inbound_id,body,ai_message_id,ai_state,ai_reason)
      SELECT m.conversation_id,?, ?,m.id,?,? FROM messages raw JOIN visible_messages m ON m.id=raw.id
      WHERE raw.conversation_id=? AND raw.event_id=?
      ON CONFLICT(conversation_id,inbound_id) DO NOTHING`)
      .run(inbound, respond ? "" : manual, respond ? "pending" : "needs_human", respond ? null : "consent", conversation, inbound);
    return respond && inserted.changes === 1;
  }

  list(conversation: string) {
    return this.store.db.prepare(`SELECT ${projection} ${sourceJoin}
      WHERE d.conversation_id=? AND ${visible} ORDER BY i.received DESC,d.id DESC LIMIT 50`).all(conversation);
  }

  async find(conversationId: string, operator: Parameters<InboxDraftReader["find"]>[1]) {
    if (operator.role !== "owner" && operator.role !== "support") return null;
    const row = this.store.db.prepare(`SELECT ${projection},i.target,d.ai_message_id ${sourceJoin}
      WHERE d.conversation_id=? AND ${visible}
      ORDER BY i.received DESC,d.id DESC LIMIT 1`).get(conversationId);
    if (!row ||
        row.ai_message_id !== null && this.store.contact(String(row.target), this.clock())?.retain !== 1) return null;
    return { id: String(row.id), version: Number(row.version), text: String(row.text), state: String(row.state),
      intent: row.intent === null ? null : String(row.intent), reason: row.reason === null ? null : String(row.reason),
      sourceIds: Array.isArray(row.sourceIds) ? row.sourceIds.filter((value): value is string => typeof value === "string") : [],
      delivery: String(row.delivery) };
  }

  get(id: string) {
    return this.store.db.prepare(`SELECT ${projection} ${sourceJoin} WHERE d.id=? AND ${visible}`).get(id);
  }

  async process(inbound: string) {
    const row = this.store.db.prepare(`SELECT d.id,d.revision ${sourceJoin}
      WHERE d.inbound_id=? AND (d.ai_state='pending' OR
        (d.ai_state='generating' AND d.ai_started_at < clock_timestamp()-interval '2 minutes'))`).get(inbound);
    if (row) await this.generate(String(row.id), Number(row.revision), false);
  }

  async regenerate(id: string, version: number) {
    return this.generate(id, version, true);
  }

  approve(id: string, version: number, operator: string, editedText?: string) {
    const row = this.store.db.prepare(`UPDATE web_reply_drafts d SET ai_state='approved', revision=revision+1,
      ai_approved_by=?,body=coalesce(?::text,body),ai_approved_at=clock_timestamp()
      WHERE d.id=? AND d.revision=? AND d.delivery='draft' AND (d.ai_state='ready' OR (d.ai_state='needs_human' AND d.ai_reason='no_knowledge'))
        AND EXISTS(SELECT 1 FROM visible_messages m WHERE m.id=d.ai_message_id)
      RETURNING d.id,d.conversation_id AS "conversationId",d.revision AS version,d.body AS text`).get(operator, editedText ?? null, id, version);
    return row;
  }

  private async choose(key: string, agent: "router" | "support" | "sales", data: object, choices: readonly string[],
    denied: () => Reason | undefined) {
    let pending: ReturnType<Provider["decide"]> | undefined;
    let reason: Reason | undefined;
    try {
      this.store.admit(() => {
        reason = denied();
        if (reason) return;
        return this.budget.reserve(key, agent, true, false, requestInputEstimate(this.config.budget, data, choices));
      }, reservation => {
        if (reservation) pending = this.provider.decide({ ...reservation, data, choices });
      });
      if (!pending) return { reason: reason ?? "budget" as const };
      const result = await pending;
      if (!this.budget.settle(key, result.usage)) return { reason: "budget" as const };
      if (!choices.includes(result.choice)) return { reason: "unavailable" as const };
      return { choice: result.choice };
    } catch (error) {
      if (error instanceof Error && ["PROVIDER_MODEL", "PROVIDER_USAGE"].includes(error.message)) this.budget.hold();
      return { reason: "unavailable" as const };
    }
  }

  private async generate(id: string, version: number, manualRetry: boolean) {
    const { db } = this.store;
    const row = this.store.atomic(() => {
      const claim = db.prepare(`UPDATE web_reply_drafts d SET ai_state='generating',ai_started_at=clock_timestamp(),revision=revision+1
        WHERE d.id=? AND d.revision=? AND d.delivery='draft' AND (
          d.ai_state='pending' OR (?::integer=1 AND d.ai_state IN ('ready','needs_human')) OR
          (d.ai_state='generating' AND d.ai_started_at<clock_timestamp()-interval '2 minutes'))
          AND EXISTS(SELECT 1 FROM visible_messages m WHERE m.id=d.ai_message_id) RETURNING id`)
        .get(id, version, manualRetry ? 1 : 0);
      if (!claim) return;
      return db.prepare(`SELECT m.body,i.target ${sourceJoin} WHERE d.id=?`).get(id);
    });
    if (!row) return;
    const claimedVersion = version + 1;
    const target = String(row.target);
    const initial = this.store.draftPolicy(target, this.clock());
    const epoch = this.store.setting("drafts_epoch");
    const denied = (): Reason | undefined => {
      if (!this.enabled() || epoch !== this.store.setting("drafts_epoch")) return "unavailable";
      const policy = this.store.draftPolicy(target, this.clock());
      if (!initial.retain || !initial.respond || !policy.retain || !policy.respond ||
          policy.revision !== initial.revision || !this.get(id)) return "consent";
    };
    let intent: Intent | null = null;
    const finish = (state: State, text: string, reason: Reason | null, sourceIds: string[] = []) => {
      db.prepare(`UPDATE web_reply_drafts d SET body=?,ai_state=?,ai_intent=?,ai_reason=?,ai_source_ids=?::jsonb,
        ai_started_at=NULL,revision=revision+1 WHERE d.id=? AND d.revision=? AND d.ai_state='generating'
        AND EXISTS(SELECT 1 FROM visible_messages m WHERE m.id=d.ai_message_id)`)
        .run(text, state, intent, reason, JSON.stringify(sourceIds), id, claimedVersion);
      return this.get(id);
    };
    if (!this.live) return finish("needs_human", manual, "mock");
    const blocked = denied();
    if (blocked) return finish("needs_human", manual, blocked);
    const question = String(row.body).slice(0, this.config.scheduling.maxText)
      .replace(/(?:\+?\d[\d.() -]{7,}\d)/gu, "[số đã ẩn]")
      .replace(/[\w.+-]+@[\w.-]+\.[a-z]+/giu, "[email đã ẩn]").replace(/https?:\/\/\S+/giu, "[link đã ẩn]");
    const key = `oa-draft:${id}:${claimedVersion}`;
    const routed = await this.choose(key + ":route", "router", { purpose: "classify_customer_intent", customerText: question }, intents, denied);
    if (routed.reason) return finish("needs_human", manual, routed.reason);
    intent = routed.choice as Intent;
    const agent = intent === "price" ? "sales" : "support";
    const admission = denied();
    if (admission) return finish("needs_human", manual, admission);
    const candidates = extractSkus(question);
    const sku = candidates.length === 1 ? candidates[0] : undefined;
    const date = vietnam(this.clock()).date;
    const sources = [
      ...(sku ? this.store.knowledge.bySku(sku) : []), ...this.store.knowledge.policies(),
      ...this.store.knowledge.findDocuments(question, date, sku),
    ];
    let response;
    try {
      response = validatedDraft(new GroundedDraft(), { question, sku, date, sources });
    } catch {
      return finish("needs_human", handoff, "no_knowledge");
    }
    // The model selects a grounded candidate or a human handoff. It cannot
    // supply free-form facts, quote amounts, tool calls or customer identifiers.
    const priceVerified = intent !== "price" || sources.some(source =>
      source.kind === "price" && response.sourceIds.includes(source.id) && source.amount !== null);
    const complaintVerified = intent !== "complaint" || sources.some(source =>
      source.kind === "policy" && response.sourceIds.includes(source.id));
    const grounded = priceVerified && complaintVerified && response.action === "trả lời" &&
      response.text.length <= this.config.scheduling.maxText;
    if (!grounded) return finish("needs_human", handoff, "no_knowledge");
    const composed = await this.choose(key + ":compose", agent, {
      purpose: "compose_grounded_reply", intent, customerText: question,
      candidate: { text: response.text, sourceIds: response.sourceIds },
    }, ["grounded_reply", "human_handoff"], denied);
    const completion = denied();
    if (completion) return finish("needs_human", manual, completion);
    if (composed.reason) return finish("needs_human", manual, composed.reason);
    return composed.choice === "grounded_reply"
      ? finish("ready", response.text.trim(), null, response.sourceIds)
      : finish("needs_human", handoff, "no_knowledge");
  }
}
