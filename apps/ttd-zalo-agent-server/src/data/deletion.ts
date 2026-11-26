import { createHmac, randomUUID } from "node:crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import type { Pool } from "pg";
import { requireCapability, transaction, uuid } from "./repository.js";

const exec = promisify(execFile);
export type Tombstone = { id: string; conversation_id: string; event_id: string; version: number; policy_version: number };

export function deletionRequest(value: unknown) {
  if (!value || typeof value !== "object") throw Error("invalid_deletion_request");
  const req = value as Record<string, unknown>;
  const { record_id, expected_version, policy_version, reason_code } = req;
  const validVersion = (v: unknown): v is number => typeof v === "number" && Number.isInteger(v) && v > 0 && v <= 2147483647;
  if (Object.keys(req).length !== 4 || !uuid(record_id) || !validVersion(expected_version) ||
      !validVersion(policy_version) || reason_code !== "retention_elapsed") throw Error("invalid_deletion_request");
  return [record_id, expected_version, policy_version, reason_code] as const;
}

export async function requestDeletion(pool: Pool, principal: object, value: unknown) {
  requireCapability(principal, "deletion.request");
  const { rows } = await pool.query("SELECT delete_eligible($1,$2,$3,$4) AS accepted", [...deletionRequest(value)]);
  return Boolean(rows[0].accepted);
}

type Attempt = Tombstone & { purge_id: string };
type Confirmed = Attempt & { proof: string };
type Recovery = Attempt & { origin: string; xid: string; intent: string };
type Evidence = Confirmed & { status: "confirmed" | "rolled_back" };

async function writeImmutable(name: string, item: object) {
  const data = JSON.stringify(item);
  const child = exec("rclone", ["rcat", name, "--immutable", "--retries", "1"], { timeout: 20000 });
  child.child.stdin!.on("error", () => {});
  child.child.stdin!.end(data);
  try { await child; } catch { /* Read-back also handles an identical object on retry. */ }
  const existing = await exec("rclone", ["cat", name], { timeout: 20000 });
  if (existing.stdout !== data) throw Error("tombstone_archive_mismatch");
}

function receiptLedger(archiveTarget: string) {
  const target = (process.env.PURGE_RECEIPT_REMOTE ?? "").replace(/\/$/, "");
  if (!target || target === archiveTarget.replace(/\/$/, "") || /[\r\n]/.test(target)) {
    throw Error("invalid_purge_receipt_remote");
  }
  return (entry: Evidence) => writeImmutable(target + "/" + entry.purge_id + ".json", entry);
}

function remoteArchive(target: string) {
  if (!target || /[\r\n]/.test(target)) throw Error("invalid_tombstone_archive");
  const prefix = target.replace(/\/$/, "") + "/tombstones/";
  const markerTimeout = process.env.RCLONE_MARKER_TIMEOUT_SECONDS ?? "30";
  if (!/^[1-9][0-9]{0,2}$/.test(markerTimeout) || Number(markerTimeout) > 120) {
    throw Error("invalid_rclone_marker_timeout");
  }
  const format = async () => {
    const result = await exec("rclone", ["cat", prefix + "_format",
      "--retries", "1", "--low-level-retries", "2"], { timeout: Number(markerTimeout) * 1000 })
      .catch(() => { throw Error("tombstone_archive_unavailable"); });
    if (result.stdout.trim() !== "z4-tombstones-v1") throw Error("invalid_tombstone_format");
  };
  return {
    async write(phase: "pending" | "confirmed", item: Recovery | Confirmed) {
      await format();
      await writeImmutable(prefix + phase + "/" + item.purge_id + ".json", item);
    },
    async readPending(id: string): Promise<Recovery> {
      const { stdout } = await exec("rclone", ["cat", prefix + "pending/" + id + ".json"], { timeout: 10000 });
      return JSON.parse(stdout);
    },
    async expired() {
      await format();
      const { stdout } = await exec("rclone", ["lsf", prefix, "--recursive", "--files-only",
        "--include", "/pending/*.json", "--min-age", "24h"], { timeout: 20000 });
      return stdout.split("\n").flatMap(path => {
        const id = /^pending\/([0-9a-f-]+)\.json$/.exec(path)?.[1];
        return id && uuid(id) ? [id] : [];
      }).slice(0, 100);
    },
    async discard(id: string) {
      await exec("rclone", ["deletefile", prefix + "pending/" + id + ".json"], { timeout: 20000 });
    },
  };
}

function sign(phase: string, item: Attempt, key: string) {
  return createHmac("sha256", Buffer.from(key, "hex"))
    .update(["z4-tombstone-v2", phase, item.purge_id, item.id, item.conversation_id,
      item.event_id, item.version, item.policy_version].join("|")).digest("hex");
}

async function publish(pool: Pool, archive: ReturnType<typeof remoteArchive>, key: string, target: string) {
  const { rows } = await pool.query<Confirmed>("SELECT * FROM committed_purges()");
  if (!rows.length) return;
  const ledger = receiptLedger(target);
  for (const item of rows) {
    await ledger({ ...item, status: "confirmed" });
    await archive.write("confirmed", item);
    await pool.query("SELECT purge_published($1,$2)", [item.purge_id, sign("published", item, key)]);
  }
}

export async function runRetention(pool: Pool, target: string) {
  const key = process.env.DATA_TOMBSTONE_KEY ?? "";
  const archive = remoteArchive(target);
  if (!/^[a-f0-9]{64}$/.test(key)) throw Error("invalid_tombstone_key");
  await publish(pool, archive, key, target);
  const eligible = await pool.query<Tombstone>("SELECT * FROM purge_candidates('quarantine')");
  for (const item of eligible.rows) {
    await pool.query("SELECT delete_eligible($1,$2,$3,'retention_elapsed')", [item.id, item.version, item.policy_version]);
  }
  const candidates = await pool.query<Tombstone>("SELECT * FROM purge_candidates('purge')");
  for (const item of candidates.rows) {
    const ledger = receiptLedger(target);
    let pending: Recovery | undefined;
    try {
      await transaction(pool, async db => {
        const attempt = { purge_id: randomUUID(), ...item };
        const identity = [item.id, item.version, item.policy_version, attempt.purge_id];
        const statement = "SELECT purge_message($1,$2,$3,$4,$5) AS accepted";
        if (!(await db.query(statement, [...identity, null])).rows[0].accepted) return;
        const { origin, xid } = (await db.query("SELECT * FROM purge_intent()")).rows[0];
        pending = { ...attempt, origin, xid, intent: sign("intent:" + origin + ":" + xid, attempt, key) };
        await archive.write("pending", pending);
        const signature = sign("pending", attempt, key);
        if (!(await db.query(statement, [...identity, signature])).rows[0].accepted) throw Error("purge_rejected");
      });
    } catch (error) {
      if (pending) {
        // An ambiguous COMMIT failure is never a rollback receipt.
        try {
          const evidence = await resolveSource(pool, pending);
          if (evidence?.status === "rolled_back") await ledger(evidence);
        } catch { /* The original failure is reported; cleanup can retry evidence later. */ }
      }
      throw error;
    }
  }
  if (candidates.rows.length) await publish(pool, archive, key, target);
}

async function resolveSource(db: Pick<Pool, "query">, pending: Recovery) {
  const { purge_id, id, conversation_id, event_id, version, policy_version, origin, xid, intent } = pending;
  const { rows } = await db.query<Pick<Evidence, "status" | "proof">>(
    "SELECT * FROM purge_recovery_evidence($1,$2,$3,$4,$5,$6,$7,$8,$9)",
    [purge_id,id,conversation_id,event_id,version,policy_version,origin ?? null,xid ?? null,intent ?? null]);
  return rows[0] && { purge_id,id,conversation_id,event_id,version,policy_version,...rows[0] };
}

export async function cleanPendingPurges(pool: Pool, target: string) {
  const archive = remoteArchive(target);
  for (const id of await archive.expired()) {
    await transaction(pool, async db => {
      const discardable = (await db.query("SELECT pending_purge_discardable($1) AS discard", [id])).rows[0].discard;
      const item = await archive.readPending(id);
      if (item.purge_id !== id) throw Error("invalid_pending_identity");
      const evidence = discardable ? undefined : await resolveSource(db, item);
      if (evidence?.status === "rolled_back") await receiptLedger(target)(evidence);
      if (discardable || evidence?.status === "rolled_back") {
        try { await archive.discard(id); } catch (error) {
          if ((error as { code?: number }).code !== 4) throw error;
        }
      }
    });
  }
}
