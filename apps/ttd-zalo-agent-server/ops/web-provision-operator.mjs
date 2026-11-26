import { readFileSync } from "node:fs";
import { randomBytes, scryptSync } from "node:crypto";
import { Client } from "pg";

const { account, label, passphrase, role } = JSON.parse(readFileSync(0, "utf8"));
if (typeof account !== "string" || !/^[a-z0-9_.@-]{1,120}$/i.test(account) ||
    typeof label !== "string" || !label.trim() || label.length > 120 ||
    typeof passphrase !== "string" || passphrase.length < 16 || passphrase.length > 256 ||
    !["owner", "sales", "support", "a0"].includes(role)) throw Error("INVALID_OPERATOR");
const salt = randomBytes(16);
const verifier = salt.toString("hex") + ":" + scryptSync(passphrase, salt, 64).toString("hex");
const db = new Client();
await db.connect();
try {
  await db.query("BEGIN");
  const result = await db.query(`INSERT INTO web_operators(account,label,role,verifier) VALUES($1,$2,$3,$4)
    ON CONFLICT(account) DO UPDATE SET label=excluded.label,role=excluded.role,verifier=excluded.verifier
    RETURNING id`, [account, label, role, verifier]);
  await db.query("DELETE FROM web_sessions WHERE operator_id=$1", [result.rows[0].id]);
  await db.query("COMMIT");
} catch (error) {
  await db.query("ROLLBACK");
  throw error;
} finally { await db.end(); }
