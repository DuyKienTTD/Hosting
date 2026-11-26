import { Budget } from "../budget.js";
import { agents, day, vietnam, type Config } from "../config.js";
import { requestInputEstimate, type Provider } from "../provider.js";
import type { Store } from "../store.js";
import type { Operator } from "./http.js";

const actions = {
  router: "route_for_review", support: "support_ticket", sales: "sales_ticket", crm: "label_proposal",
  report: "daily_summary", campaign: "read_only", community: "read_only", listen: "read_only",
} as const;
type Role = keyof typeof actions;
const roles: readonly Role[] = ["router", ...agents];
const proposalRoles: readonly Role[] = ["router", "support", "sales", "crm"];
const labels = { router: "Điều phối", support: "CSKH", sales: "Bán hàng", crm: "CRM",
  report: "Báo cáo", campaign: "Chiến dịch", community: "Cộng đồng", listen: "Lắng nghe" };

function roleOf(value: unknown): Role | undefined {
  if (typeof value !== "string") return;
  const name = value.toLowerCase();
  const role = name === "claude" ? "router" : name;
  return Object.hasOwn(actions, role) ? role as Role : undefined;
}

export class WebRoomAgents {
  private readonly budget: Budget;
  private busy = false;
  constructor(private readonly store: Store, private readonly config: Config, private readonly provider: Provider,
    private readonly live: boolean, private readonly clock = Date.now) {
    this.budget = new Budget(store, config.budget, clock);
  }

  roster() {
    return roles.map(label => ({ label, role: labels[label],
      status: this.store.stopped(label) ? "Đang dừng" : "Có thể giao việc" }));
  }

  ownerView(actor: Operator, exchange: number) {
    if (actor.role !== "owner") return;
    const costs = this.store.db.prepare("SELECT agent_role,sum(amount) AS amount FROM ledger WHERE date=? AND provider=? GROUP BY agent_role")
      .all(vietnam(this.clock()).date, this.config.budget.provider);
    const amount = (role: string | null) => Number(costs.find(row => row.agent_role === role)?.amount ?? 0);
    return {
      unassignedUsd: amount(null) / 1e9,
      agents: roles.map(id => ({ id, model: this.config.budget.byAgent[id], permission: proposalRoles.includes(id) ? "propose" : "read",
        enabled: !this.store.setting(id), blocked: this.store.stopped(id), usedUsd: amount(id) / 1e9,
        usedVnd: exchange ? Math.round(amount(id) * exchange / 1e9) : null })),
    };
  }

  toggle(actor: Operator, agent: string, enabled: boolean) {
    if (actor.role !== "owner" || !roles.includes(agent as Role)) return false;
    this.store.stop(agent, !enabled);
    return true;
  }

  private ticket(actor: Operator, title: string, agent: Role | "A1" | "A2") {
    const { db } = this.store;
    const id = String(db.prepare("INSERT INTO tasks(created_by,title) VALUES(?,?) RETURNING id").get(actor.id, title)!.id);
    db.prepare("INSERT INTO web_task_agents(task_id,agent) VALUES(?,?)").run(id, agent);
    if (roleOf(agent)) db.prepare("INSERT INTO web_agent_runs(task_id) VALUES(?)").run(id);
    return { id, title, agent, status: "new" };
  }

  post(actor: Operator, text: string) {
    if (actor.role !== "owner" || !text.trim() || text.length > 1000) return;
    return this.store.atomic(() => {
      const id = this.store.db.prepare("INSERT INTO web_room_messages(operator_id,body) VALUES(?,?) RETURNING id").get(actor.id, text)?.id;
      const mention = /^@([a-z][a-z0-9_-]*)\s+(.+)$/isu.exec(text.trim());
      const role = roleOf(mention?.[1]);
      const title = mention?.[2].trim().slice(0, 250);
      const task = role && title ? this.ticket(actor, title, role) : undefined;
      return { id, author: actor.label, text, ...(task ? { task } : {}) };
    });
  }

  assign(actor: Operator, title: string, name: string) {
    if (actor.role !== "owner" || !title.trim() || title.length > 250) return;
    const agent = roleOf(name) ?? (name === "A1" || name === "A2" ? name : undefined);
    if (agent) return this.store.atomic(() => this.ticket(actor, title, agent));
  }

  review(actor: Operator, id: string, decision: "accept" | "dismiss") {
    if (actor.role !== "owner" || !["accept", "dismiss"].includes(decision)) return false;
    return this.store.atomic(() => {
      const { db } = this.store;
      const moved = db.prepare("UPDATE tasks SET state='done' WHERE id=? AND state='review' AND EXISTS (SELECT 1 FROM web_agent_runs r WHERE r.task_id=tasks.id AND r.result IS NOT NULL)").run(id);
      if (!moved.changes) return false;
      db.prepare("UPDATE web_agent_runs SET reviewed_by=?,review_decision=?,reviewed_at=clock_timestamp() WHERE task_id=?")
        .run(actor.id, decision, id);
      return true;
    });
  }

  private report() {
    const midnight = vietnam(this.clock()).midnight;
    return this.store.db.prepare("SELECT count(DISTINCT conversation_id)::int AS conversations,count(*)::int AS messages FROM visible_messages WHERE received_at>=to_timestamp(?::double precision/1000) AND received_at<to_timestamp(?::double precision/1000)")
      .get(midnight, midnight + day);
  }

  private finish(id: string, result: string) {
    this.store.atomic(() => {
      const { db } = this.store;
      if (db.prepare("UPDATE tasks SET state='review' WHERE id=? AND state='in_progress'").run(id).changes) {
        db.prepare("UPDATE web_agent_runs SET result=? WHERE task_id=?").run(result, id);
      }
    });
  }

  async tick() {
    if (this.busy) return;
    this.busy = true;
    try {
      const { db } = this.store;
      const row = this.store.atomic(() => {
        const stale = db.prepare("SELECT r.task_id FROM web_agent_runs r JOIN tasks t ON t.id=r.task_id WHERE t.state='in_progress' AND r.started_at<clock_timestamp()-interval '90 seconds' LIMIT 10").all();
        for (const item of stale) this.finish(String(item.task_id), "Lượt xử lý hết hạn. Cần người xem lại.");
        const next = db.prepare("SELECT t.id,t.title,t.created_by,a.agent FROM tasks t JOIN web_agent_runs r ON r.task_id=t.id JOIN web_task_agents a ON a.task_id=t.id WHERE t.state='new' ORDER BY t.created_at,t.id LIMIT 1").get();
        if (!next) return;
        db.prepare("UPDATE tasks SET state='in_progress' WHERE id=? AND state='new'").run(next.id);
        db.prepare("UPDATE web_agent_runs SET started_at=clock_timestamp() WHERE task_id=?").run(next.id);
        return next;
      });
      if (row) await this.execute(String(row.id), row.agent, String(row.title), String(row.created_by));
    } finally {
      this.busy = false;
    }
  }

  private async execute(id: string, agent: unknown, title: string, assignedBy: string) {
    const role = roleOf(agent);
    const finish = (result: string) => this.finish(id, result);
    const authorized = () => this.store.db.prepare("SELECT 1 FROM web_operators WHERE id::text=? AND role='owner' AND enabled")
      .get(assignedBy);
    if (!authorized()) return finish("Quyền giao phiếu đã thay đổi. Cần người xử lý.");
    if (!role || this.store.stopped(role)) return finish("Agent đang dừng. Cần người xử lý.");
    if (!this.live) return finish("Kết quả giả lập · " + labels[role] + " đã tiếp nhận phiếu. Chờ người duyệt.");

    const action = actions[role];
    const choices = [action, "needs_human"];
    const epoch = this.store.setting("epoch");
    const summary = role === "report" ? this.report() : undefined;
    const command = title.replace(/https?:\/\/\S+|[\w.+-]+@[\w.-]+\.[a-z]+|\+?\d[\d .()-]{7,}\d/giu, "[đã ẩn]");
    const canPropose = proposalRoles.includes(role);
    const data = { purpose: "internal_operator_task_only", agent: role, capability: canPropose ? "propose" : "read",
      command, ...(summary ? { aggregate: summary } : {}) };
    const key = "room-agent:" + id;
    try {
      let pending: ReturnType<Provider["decide"]> | undefined;
      this.store.admit(() => {
        if (!authorized() || this.store.stopped(role) || this.store.setting("epoch") !== epoch) return;
        return this.budget.reserve(key, role, false, false, requestInputEstimate(this.config.budget, data, choices));
      }, reserved => {
        if (reserved) pending = this.provider.decide({ ...reserved, data, choices });
      });
      if (!pending) return finish("Lượt chạy bị chặn bởi STOP hoặc ngân sách. Cần người xử lý.");
      const decision = await pending;
      if (!this.budget.settle(key, decision.usage)) return finish("Chưa đối soát được chi phí. Cần người xử lý.");
      if (!authorized() || this.store.stopped(role) || this.store.setting("epoch") !== epoch || decision.choice !== action) {
        return finish("Chưa có kết quả phù hợp. Cần người xử lý.");
      }
      if (!canPropose) {
        return finish(summary ? "Hôm nay có " + summary.conversations + " hội thoại và " + summary.messages + " tin được lưu."
          : "Agent chỉ có quyền đọc. Cần người xem yêu cầu.");
      }
      // The proposal stays on this task. The model has no domain write or transport.
      const proposal = role === "crm" ? "Đề xuất gắn nhãn theo yêu cầu trong phiếu"
        : role === "router" ? "Đề xuất điều phối yêu cầu trong phiếu" : "Đề xuất xử lý yêu cầu trong phiếu";
      finish(proposal + ". Chờ người duyệt.");
    } catch (error) {
      if (error instanceof Error && ["PROVIDER_MODEL", "PROVIDER_USAGE"].includes(error.message)) this.budget.hold();
      finish("AI Router chưa trả kết quả hợp lệ. Cần người xử lý.");
    }
  }
}
