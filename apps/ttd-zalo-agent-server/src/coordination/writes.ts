import type { Pool } from "pg";
import { requireCapability, transaction } from "../data/repository.js";
import type { RenameRequest } from "./room.js";

export function checkedRename(pool: Pool) {
  return async (request: RenameRequest) => {
    if (requireCapability(request.approver, "customer.rename") !== "operator" ||
        requireCapability(request.principal, "customer.rename") !== request.agent) throw Error("forbidden");
    await transaction(pool, async db => {
      const receipt = await db.query(
        "INSERT INTO coordination_applied_rename(ticket_id, proposal_index) VALUES ($1,$2) ON CONFLICT DO NOTHING",
        [request.ticket, request.index],
      );
      if (!receipt.rowCount) throw Error("conflict");
      const updated = await db.query("UPDATE customers SET display_name=$2 WHERE id=$1 AND display_name=$3",
        [request.customerId, request.name, request.expectedName]);
      if (!updated.rowCount) throw Error("conflict");
      await db.query("INSERT INTO audit_log(actor,action,record_id) VALUES($1,'customer.rename',$2)",
        [request.agent, request.customerId]);
    });
  };
}
