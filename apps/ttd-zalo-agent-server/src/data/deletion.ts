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

export function remoteArchive(target: string) {
  if (!target || /[\r\n]/.test(target)) throw Error("invalid_tombstone_archive");
  return async (item: Tombstone) => {
    const prefix = target.replace(/\/$/, "") + "/tombstones/";
    const format = await exec("rclone", ["cat", prefix + "_format"], { timeout: 10000 });
    if (format.stdout.trim() !== "z4-tombstones-v1") throw Error("invalid_tombstone_format");
    const name = prefix + item.id + ".json";
    const child = exec("rclone", ["rcat", name, "--immutable", "--retries", "1"], { timeout: 20000 });
    child.child.stdin!.on("error", () => {});
    child.child.stdin!.end(JSON.stringify(item));
    try { await child; } catch {
      // A prior attempt may have written the immutable object before the DB committed.
      const existing = await exec("rclone", ["cat", name], { timeout: 20000 });
      if (existing.stdout !== JSON.stringify(item)) throw Error("tombstone_archive_mismatch");
    }
  };
}

export async function runRetention(pool: Pool, archive: (item: Tombstone) => Promise<void>) {
  const eligible = await pool.query<Tombstone>("SELECT * FROM purge_candidates('quarantine')");
  for (const item of eligible.rows) {
    await pool.query("SELECT delete_eligible($1,$2,$3,'retention_elapsed')", [item.id, item.version, item.policy_version]);
  }
  const candidates = await pool.query<Tombstone>("SELECT * FROM purge_candidates('purge')");
  for (const item of candidates.rows) {
    await transaction(pool, async db => {
      const { rows } = await db.query("SELECT authorize_purge($1,$2,$3) AS accepted", [item.id, item.version, item.policy_version]);
      if (rows[0].accepted) await archive(item);
    });
  }
}
