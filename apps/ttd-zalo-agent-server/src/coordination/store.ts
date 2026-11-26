import type { Pool } from "pg";
import { transaction } from "../data/repository.js";
import type { Result, Target } from "./schema.js";

export type TicketState = "new" | "working" | "review" | "done";
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
  read(): Promise<RoomState>;
  update<T>(change: (state: RoomState) => T): Promise<T>;
}

// For local tests. Production composition supplies PostgresRoomStore.
export class MemoryRoomStore implements RoomStore {
  private state = initial();
  async read() { return structuredClone(this.state); }
  async update<T>(change: (state: RoomState) => T) {
    const next = structuredClone(this.state);
    const result = change(next);
    next.revision++;
    this.state = next;
    return structuredClone(result);
  }
}

export class PostgresRoomStore implements RoomStore {
  constructor(private readonly pool: Pool) {}
  async read() {
    const { rows } = await this.pool.query<{ state: RoomState }>(
      "SELECT state FROM coordination_room WHERE singleton = true",
    );
    return rows[0]?.state ?? initial();
  }
  async update<T>(change: (state: RoomState) => T) {
    return transaction(this.pool, async client => {
      await client.query("INSERT INTO coordination_room VALUES (true, $1) ON CONFLICT DO NOTHING", [initial()]);
      const { rows } = await client.query<{ state: RoomState }>(
        "SELECT state FROM coordination_room WHERE singleton = true FOR UPDATE",
      );
      const state = rows[0].state;
      const result = change(state);
      state.revision++;
      await client.query("UPDATE coordination_room SET state=$1 WHERE singleton = true", [state]);
      return result;
    });
  }
}
