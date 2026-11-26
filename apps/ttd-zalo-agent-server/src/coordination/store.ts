import type { Pool, PoolClient } from "pg";
import { transaction } from "../data/repository.js";
import type { Result, Target } from "./schema.js";

export type TicketState = "new" | "working" | "review" | "done";
export type RunStep = "authorization" | "read" | "claim" | "budget" | "provider" | "plan_write" | "result_write";
export type Ticket = {
  id: string;
  parent?: string;
  assignedBy: string;
  agent: Target;
  state: TicketState;
  instruction: string;
  dueAt: string;
  links: string[];
  result?: Result;
  failure?: "timeout" | "budget" | "rejected" | "provider" | "interrupted";
  failureStep?: RunStep;
  runId?: string;
  version: number;
  leaseUntil?: number;
};
export type Message = { id: string; author: string; text: string; at: string; tickets: string[] };
export type RoomState = {
  revision: number;
  messages: Message[];
  tickets: Record<string, Ticket>;
  spending: { day: string; amount: number; total: number; held: boolean };
};

const initial = (): RoomState => ({
  revision: 0, messages: [], tickets: {}, spending: { day: "", amount: 0, total: 0, held: false },
});

export interface RoomStore {
  read(signal?: AbortSignal): Promise<RoomState>;
  update<T>(change: (state: RoomState) => T, signal?: AbortSignal): Promise<T>;
}

// For local tests. Production composition supplies PostgresRoomStore.
export class MemoryRoomStore implements RoomStore {
  private state = initial();
  async read(signal?: AbortSignal) {
    signal?.throwIfAborted();
    return structuredClone(this.state);
  }
  async update<T>(change: (state: RoomState) => T, signal?: AbortSignal) {
    signal?.throwIfAborted();
    const next = structuredClone(this.state);
    const result = change(next);
    next.revision++;
    this.state = next;
    return structuredClone(result);
  }
}

export class PostgresRoomStore implements RoomStore {
  constructor(private readonly pool: Pool) {}
  private async withClient<T>(signal: AbortSignal | undefined, work: (client: PoolClient) => Promise<T>) {
    signal?.throwIfAborted();
    const client = await this.pool.connect();
    // Drop the connection on abort so a stalled transaction releases its locks.
    const abort = () => client.release(true);
    signal?.addEventListener("abort", abort, { once: true });
    try {
      if (signal?.aborted) {
        abort();
        signal.throwIfAborted();
      }
      return await work(client);
    } finally {
      signal?.removeEventListener("abort", abort);
      if (!signal?.aborted) client.release();
    }
  }

  async read(signal?: AbortSignal) {
    return this.withClient(signal, async client => {
      const { rows } = await client.query<{ state: RoomState }>(
        "SELECT state FROM coordination_room WHERE singleton = true",
      );
      return rows[0]?.state ?? initial();
    });
  }

  async update<T>(change: (state: RoomState) => T, signal?: AbortSignal) {
    const write = async (client: PoolClient) => {
      await client.query("INSERT INTO coordination_room VALUES (true, $1) ON CONFLICT DO NOTHING", [initial()]);
      const { rows } = await client.query<{ state: RoomState }>(
        "SELECT state FROM coordination_room WHERE singleton = true FOR UPDATE",
      );
      signal?.throwIfAborted();
      const state = rows[0].state;
      const result = change(state);
      state.revision++;
      await client.query("UPDATE coordination_room SET state=$1 WHERE singleton = true", [state]);
      return result;
    };
    if (!signal) return transaction(this.pool, write);
    return this.withClient(signal, async client => {
      await client.query("BEGIN");
      try {
        const result = await write(client);
        signal.throwIfAborted();
        await client.query("COMMIT");
        return result;
      } catch (error) {
        if (!signal.aborted) await client.query("ROLLBACK");
        throw error;
      }
    });
  }
}
