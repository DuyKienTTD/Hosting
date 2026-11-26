import { timingSafeEqual, createHash } from "node:crypto";
import type { Pool, PoolClient } from "pg";

const grants = {
  support: ["customer.read", "message.read", "task.create"],
  crm: ["customer.read", "customer.create", "customer.rename", "task.create"],
  campaign: ["customer.read", "task.create"],
  community: ["task.create"],
  listen: ["message.read", "task.create"],
  sales: ["customer.read", "task.create"],
  report: ["task.create"],
  operator: ["customer.read", "customer.create", "customer.rename", "message.read", "task.create", "task.update"],
  channel: ["message.ingest"],
  retention: ["deletion.request"],
} as const;
type Role = keyof typeof grants;
type Capability = (typeof grants)[Role][number];
const authenticated = new WeakMap<object, Role>();

export function authenticate(token: string, env: NodeJS.ProcessEnv): object | undefined {
  if (token.length < 32) return;
  const digest = (value: string) => createHash("sha256").update(value).digest();
  const roles = (Object.keys(grants) as Role[]).filter(role => {
    const expected = env["DATA_TOKEN_" + role.toUpperCase()];
    return expected && expected.length >= 32 && timingSafeEqual(digest(expected), digest(token));
  });
  if (roles.length !== 1) return;
  const principal = Object.freeze({});
  authenticated.set(principal, roles[0]);
  return principal;
}

export function requireCapability(principal: object, capability: Capability): Role {
  const role = authenticated.get(principal);
  if (!role || !(grants[role] as readonly Capability[]).includes(capability)) throw Error("forbidden");
  return role;
}

export async function transaction<T>(pool: Pool, run: (client: PoolClient) => Promise<T>): Promise<T> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const result = await run(client);
    await client.query("COMMIT");
    return result;
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}

export const uuid = (value: unknown): value is string =>
  typeof value === "string" && /^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i.test(value);

export class PostgresRepository {
  constructor(private readonly pool: Pool, private readonly retentionDays: number) {
    if (!Number.isInteger(retentionDays) || retentionDays < 1 || retentionDays > 365) throw Error("invalid_retention");
  }

  async readCustomer(principal: object, id: string) {
    requireCapability(principal, "customer.read");
    return (await this.pool.query("SELECT id,display_name FROM customers WHERE id=$1", [id])).rows[0];
  }

  async addCustomer(principal: object, name: string) {
    const actor = requireCapability(principal, "customer.create");
    return transaction(this.pool, async db => {
      const { rows } = await db.query("INSERT INTO customers(display_name) VALUES($1) RETURNING id", [name]);
      await db.query("INSERT INTO audit_log(actor,action,record_id) VALUES($1,'customer.create',$2)", [actor, rows[0].id]);
      return rows[0].id as string;
    });
  }

  async renameCustomer(principal: object, id: string, name: string) {
    const actor = requireCapability(principal, "customer.rename");
    return transaction(this.pool, async db => {
      const result = await db.query("UPDATE customers SET display_name=$2 WHERE id=$1", [id, name]);
      if (!result.rowCount) return false;
      await db.query("INSERT INTO audit_log(actor,action,record_id) VALUES($1,'customer.rename',$2)", [actor, id]);
      return true;
    });
  }

  async readMessages(principal: object, conversationId: string) {
    requireCapability(principal, "message.read");
    return (await this.pool.query("SELECT id,body,received_at FROM visible_messages WHERE conversation_id=$1 ORDER BY received_at LIMIT 100", [conversationId])).rows;
  }

  async createTask(principal: object, title: string) {
    const role = requireCapability(principal, "task.create");
    return transaction(this.pool, async db => {
      const { rows } = await db.query("INSERT INTO tasks(created_by,title) VALUES($1,$2) RETURNING id", [role, title]);
      await db.query("INSERT INTO audit_log(actor,action,record_id) VALUES($1,'task.create',$2)", [role, rows[0].id]);
      return rows[0].id as string;
    });
  }

  async updateTask(principal: object, id: string, state: string) {
    const role = requireCapability(principal, "task.update");
    return transaction(this.pool, async db => {
      const result = await db.query("UPDATE tasks SET state=$2 WHERE id=$1", [id, state]);
      if (!result.rowCount) return false;
      await db.query("INSERT INTO audit_log(actor,action,record_id) VALUES($1,'task.update',$2)", [role, id]);
      return true;
    });
  }

  async ingest(principal: object, conversationId: string, upstreamEventId: string, body: string) {
    requireCapability(principal, "message.ingest");
    const event = createHash("sha256").update(upstreamEventId).digest("hex");
    return transaction(this.pool, async db => {
      const { rows } = await db.query(
        `INSERT INTO messages(conversation_id,event_id,body,retain_until)
         SELECT $1,$2,$3,now()+make_interval(days=>$4)
         WHERE NOT EXISTS (SELECT 1 FROM restore_tombstones WHERE conversation_id=$1 AND event_id=$2)
         ON CONFLICT(conversation_id,event_id) DO NOTHING RETURNING id`,
        [conversationId, event, body, this.retentionDays],
      );
      if (!rows.length) return false;
      await db.query("INSERT INTO queue_jobs(message_id) VALUES($1)", [rows[0].id]);
      return true;
    });
  }
}
