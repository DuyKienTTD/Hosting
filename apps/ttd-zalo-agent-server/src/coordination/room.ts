import { randomUUID } from "node:crypto";
import { vietnam, type Agent } from "../config.js";
import { requireCapability } from "../data/repository.js";
import { RunDeadline } from "./deadline.js";
import { decode, prepare, type Call, type RoomProvider } from "./provider.js";
import { isTarget, reference, type Plan, type Result, type Synthesis, type Target } from "./schema.js";
import type { RoomState, RoomStore, Ticket } from "./store.js";

export type Session = { id: string; role: "operator" | "a0" | Agent; dataPrincipal: object };
type Deps = {
  store: RoomStore;
  provider: RoomProvider;
  // Resolve authenticated session state and current permissions from the host.
  session: (handle: object, signal?: AbortSignal) => Promise<Session | undefined>;
  allowed: (session: Session, action: "read" | "post" | "run" | "approve", target?: Target, signal?: AbortSignal) => Promise<boolean>;
  agentPrincipal: (agent: Agent) => Promise<object | undefined>;
  writeRename: (request: RenameRequest) => Promise<void>;
  dailyCapNanodollars: number;
  keyCapNanodollars: number;
  routerRateMultiplier: number;
  timeoutMs?: number;
  clock?: () => number;
};

export type RenameRequest = {
  ticket: string; index: number; customerId: string; name: string; expectedName: string;
  agent: Agent; principal: object; approver: object;
};

const lifetime = 15 * 60_000;
const maxTickets = 2000;

function ticketIn(state: RoomState, id: string) {
  const ticket = Object.hasOwn(state.tickets, id) ? state.tickets[id] : undefined;
  if (!ticket) throw Error("missing");
  return ticket;
}

function assertActive(state: RoomState, id: string, now: number) {
  const ticket = ticketIn(state, id);
  if (ticket.state !== "working") throw Error("conflict");
  if (ticket.leaseUntil === undefined || ticket.leaseUntil <= now) throw Error("timeout");
}

function createTicket(state: RoomState, fields: Omit<Ticket, "id" | "state" | "version">) {
  if (Object.keys(state.tickets).length >= maxTickets) throw Error("capacity");
  const ticket: Ticket = { ...fields, id: randomUUID(), state: "new", version: 1 };
  state.tickets[ticket.id] = ticket;
  return ticket;
}

export class CoordinationRoom {
  private readonly now: () => number;
  private readonly timeout: number;
  constructor(private readonly deps: Deps) {
    this.now = deps.clock ?? Date.now;
    this.timeout = deps.timeoutMs ?? 30_000;
    if (!Number.isSafeInteger(this.timeout) || this.timeout < 1 || this.timeout > 60_000 ||
        !Number.isSafeInteger(deps.dailyCapNanodollars) || deps.dailyCapNanodollars < 0 ||
        !Number.isSafeInteger(deps.keyCapNanodollars) || deps.keyCapNanodollars < 0 ||
        !Number.isFinite(deps.routerRateMultiplier) || deps.routerRateMultiplier < 1) throw Error("configuration");
  }

  private async principal(handle: object, action: Parameters<Deps["allowed"]>[1], target?: Target, signal?: AbortSignal) {
    const session = await this.deps.session(handle, signal);
    signal?.throwIfAborted();
    if (!session || (session.role !== "a0" && session.role !== "operator" &&
      (!isTarget(session.role) || String(session.role) === "claude")) ||
      !await this.deps.allowed(session, action, target, signal)) throw Error("forbidden");
    return session;
  }

  async list(handle: object) {
    await this.principal(handle, "read");
    const { revision, messages, tickets } = await this.deps.store.read();
    return { revision, messages, tickets: Object.values(tickets) };
  }

  async post(handle: object, input: unknown) {
    const actor = await this.principal(handle, "post");
    const role = requireCapability(actor.dataPrincipal, "task.create");
    if (role !== (actor.role === "a0" ? "operator" : actor.role)) throw Error("forbidden");
    if (!input || typeof input !== "object" || Array.isArray(input)) throw Error("invalid");
    const { text, dueAt, links = [], ...extra } = input as Record<string, unknown>;
    const now = this.now();
    const due = typeof dueAt === "string" ? Date.parse(dueAt) : dueAt === undefined ? now + lifetime : NaN;
    if (Object.keys(extra).length || typeof text !== "string" || !text.trim() || text.length > 2000 ||
        !Number.isFinite(due) || due <= now || due > now + 7 * 86400_000 ||
        !Array.isArray(links) || links.length > 5 || !links.every(link => typeof link === "string" && reference.test(link))) {
      throw Error("invalid");
    }
    const mentions = new Set<Target>();
    for (const match of text.matchAll(/(?:^|\s)@([\p{L}\p{N}_-]+)(?![\p{L}\p{N}_-])/gu)) {
      const target = match[1].toLowerCase();
      if (isTarget(target)) mentions.add(target);
    }
    if (mentions.size > 3) throw Error("invalid");
    for (const target of mentions) await this.principal(handle, "post", target);
    return this.deps.store.update(state => {
      const tickets = [...mentions].map(agent => createTicket(state, {
        agent, assignedBy: actor.id, instruction: text, dueAt: new Date(due).toISOString(), links,
      }).id);
      const message = { id: randomUUID(), author: actor.id, text, at: new Date(now).toISOString(), tickets };
      state.messages.push(message);
      if (state.messages.length > 200) state.messages.shift();
      return message;
    });
  }

  // Check the signal inside the mutation as well as racing its acknowledgement.
  private updateRun<T>(deadline: RunDeadline, step: Parameters<RunDeadline["during"]>[0], change: (state: RoomState) => T) {
    return deadline.during(step, signal => this.deps.store.update(state => {
      signal.throwIfAborted();
      return change(state);
    }, signal));
  }

  private async invoke(handle: object, target: Target, root: string, call: Call, deadline: RunDeadline) {
    await deadline.during("authorization", signal => this.principal(handle, "run", target, signal));
    const request = prepare(call, this.deps.routerRateMultiplier);
    await this.updateRun(deadline, "budget", state => {
      assertActive(state, root, this.now());
      const day = vietnam(this.now()).date;
      if (day > state.spending.day) state.spending = { ...state.spending, day, amount: 0 };
      const { held, amount, total } = state.spending;
      if (day !== state.spending.day || held || request.amount > this.deps.dailyCapNanodollars - amount ||
          request.amount > this.deps.keyCapNanodollars - total) throw Error("budget");
      state.spending.amount += request.amount;
      state.spending.total += request.amount;
    });
    const response = await deadline.during("provider", signal => this.deps.provider.complete(request.body, signal));
    try {
      return decode(response, request);
    } catch (error) {
      if (error instanceof Error && error.message === "billing") {
        await this.updateRun(deadline, "budget", state => { state.spending.held = true; });
        throw Error("budget");
      }
      throw error;
    }
  }

  private claim(id: string, runId: string, runUntil: number, deadline: RunDeadline) {
    return this.updateRun(deadline, "claim", state => {
      const ticket = ticketIn(state, id);
      if (ticket.parent) assertActive(state, ticket.parent, this.now());
      if (ticket.state !== "new" || Date.parse(ticket.dueAt) <= this.now()) throw Error("conflict");
      ticket.state = "working";
      ticket.leaseUntil = Math.min(runUntil, Date.parse(ticket.dueAt));
      ticket.runId = runId;
      ticket.version++;
      return ticket;
    });
  }

  private finish(id: string, result: Result, deadline: RunDeadline) {
    return this.updateRun(deadline, "result_write", state => {
      const ticket = ticketIn(state, id);
      assertActive(state, id, this.now());
      if (ticket.parent) assertActive(state, ticket.parent, this.now());
      Object.assign(ticket, { result, state: "review", version: ticket.version + 1 });
      delete ticket.leaseUntil;
      delete ticket.runId;
      return ticket;
    });
  }

  private async work(handle: object, ticket: Ticket, agent: Agent, deadline: RunDeadline) {
    const result = await this.invoke(handle, agent, ticket.parent ?? ticket.id, {
      phase: "work", agent, data: { instruction: ticket.instruction, links: ticket.links },
    }, deadline) as Result;
    if (result.links.some(link => !ticket.links.includes(link)) ||
        result.proposals.some(proposal => !ticket.links.includes(proposal.customer))) throw Error("rejected");
    return result;
  }

  async run(handle: object, id: string) {
    const deadline = new RunDeadline(this.timeout);
    const runUntil = this.now() + this.timeout;
    const runId = randomUUID();
    let claiming = false;
    let claimedRoot = false;
    try {
      const actor = await deadline.during("authorization", signal => this.principal(handle, "run", undefined, signal));
      requireCapability(actor.dataPrincipal, "task.update");
      const pending = ticketIn(await deadline.during("read", signal => this.deps.store.read(signal)), id);
      if (pending.parent || pending.state !== "new" || Date.parse(pending.dueAt) <= this.now()) throw Error("conflict");
      const target = pending.agent;
      deadline.limit(Date.parse(pending.dueAt) - this.now());
      await deadline.during("authorization", signal => this.principal(handle, "run", target, signal));
      claiming = true;
      const claim = await this.claim(id, runId, runUntil, deadline);
      claimedRoot = true;
      // Load the committed claim before using the instruction or links.
      const ticket = ticketIn(await deadline.during("read", signal => this.deps.store.read(signal)), id);
      if (ticket.runId !== runId) throw Error("conflict");
      let result: Result;
      if (target === "claude") {
        const plan = await this.invoke(handle, target, id, {
          phase: "plan", data: { instruction: ticket.instruction, links: ticket.links },
        }, deadline) as Plan;
        for (const task of plan.tasks) {
          await deadline.during("authorization", signal => this.principal(handle, "run", task.agent, signal));
        }
        const children = await this.updateRun(deadline, "plan_write", state => {
          assertActive(state, id, this.now());
          return plan.tasks.map(task => createTicket(state, {
            agent: task.agent, assignedBy: "claude", parent: id, dueAt: ticket.dueAt,
            instruction: task.instruction, links: ticket.links,
          }));
        });
        const results: { id: string; summary: string }[] = [];
        for (const child of children) {
          if (child.agent === "claude") throw Error("rejected");
          const claimed = await this.claim(child.id, runId, claim.leaseUntil!, deadline);
          const childResult = await this.work(handle, claimed, child.agent, deadline);
          await this.finish(child.id, childResult, deadline);
          results.push({ id: child.id, summary: childResult.summary });
        }
        const synthesis = await this.invoke(handle, target, id, {
          phase: "synthesis", data: { instruction: ticket.instruction, results },
        }, deadline) as Synthesis;
        result = { summary: synthesis.summary, links: ticket.links, proposals: [] };
      } else {
        result = await this.work(handle, ticket, target, deadline);
      }
      return await this.finish(id, result, deadline);
    } catch (error) {
      if (!claiming) throw error;
      const reason = error instanceof Error ? error.message : "";
      const failure = deadline.signal.aborted || reason === "timeout" ? "timeout" : reason === "budget" ? "budget" :
        ["rejected", "forbidden"].includes(reason) ? "rejected" : "provider";
      // Record failure independently of the cancelled step. Bound cleanup too
      // so a full database outage cannot keep the request open indefinitely.
      const cleanup = new RunDeadline(1000);
      try {
        return await this.updateRun(cleanup, "result_write", state => {
          const current = ticketIn(state, id);
          if (current.runId !== runId) {
            if (claimedRoot && failure === "timeout" && current.state === "review") return current;
            throw error;
          }
          for (const item of Object.values(state.tickets)) {
            const claimed = item.runId === runId;
            const pending = item.parent === id && item.state === "new";
            if (claimed || pending) {
              item.state = "review";
              item.failure = claimed ? failure : "interrupted";
              if (claimed && failure === "timeout") item.failureStep = deadline.step;
              item.version++;
              delete item.leaseUntil;
              delete item.runId;
            }
          }
          return current;
        });
      } finally {
        cleanup.close();
      }
    } finally {
      deadline.close();
    }
  }

  async recover(handle: object, id: string, version: number) {
    const actor = await this.principal(handle, "approve");
    requireCapability(actor.dataPrincipal, "task.update");
    return this.deps.store.update(state => {
      const ticket = ticketIn(state, id);
      const expiry = ticket.state === "new" ? Date.parse(ticket.dueAt) : ticket.leaseUntil;
      if (ticket.parent || ticket.version !== version || expiry === undefined || expiry >= this.now()) throw Error("conflict");
      for (const item of Object.values(state.tickets)) {
        if ((item.id === id || item.parent === id) && (item.state === "new" || item.state === "working")) {
          item.state = "review";
          item.failure = "interrupted";
          item.version++;
          delete item.leaseUntil;
          delete item.runId;
        }
      }
      return ticket;
    });
  }

  async approve(handle: object, id: string, version: number) {
    const actor = await this.principal(handle, "approve");
    requireCapability(actor.dataPrincipal, "task.update");
    return this.deps.store.update(state => {
      const ticket = ticketIn(state, id);
      if (ticket.version !== version || ticket.state !== "review") throw Error("conflict");
      ticket.state = "done";
      ticket.version++;
      return ticket;
    });
  }

  // Explicit user approval of a single domain write. The repository checks the
  // originating agent's capability again at execution and audits that agent.
  async applyRename(handle: object, id: string, index: number, expectedName: string) {
    const actor = await this.principal(handle, "approve");
    requireCapability(actor.dataPrincipal, "customer.rename");
    const ticket = ticketIn(await this.deps.store.read(), id);
    if (!Number.isSafeInteger(index) || index < 0 || typeof expectedName !== "string" || expectedName.length > 120) {
      throw Error("invalid");
    }
    const proposal = ticket.result?.proposals[index];
    if (ticket.state !== "done" || ticket.agent === "claude" || !proposal) throw Error("conflict");
    const agent = await this.deps.agentPrincipal(ticket.agent);
    if (!agent || requireCapability(agent, "customer.rename") !== ticket.agent) throw Error("forbidden");
    await this.principal(handle, "approve", ticket.agent);
    await this.deps.writeRename({
      ticket: id, index, customerId: proposal.customer.slice("customer:".length), name: proposal.name,
      expectedName, agent: ticket.agent, principal: agent, approver: actor.dataPrincipal,
    });
  }
}
