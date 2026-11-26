import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import { Pool } from "pg";
import { authenticate, PostgresRepository, transaction, uuid } from "./repository.js";
import { cleanPendingPurges, requestDeletion, runRetention } from "./deletion.js";

const command = process.argv[2] ?? "serve";
const worker = command !== "serve";
const user = worker ? "data_worker" : "data_app";
const password = process.env[worker ? "DATA_WORKER_PASSWORD" : "DATA_APP_PASSWORD"];
if (!password) throw Error("database_password_required");
const pool = new Pool({
  host: process.env.PGHOST, database: process.env.PGDATABASE, user, password,
  connectionTimeoutMillis: 5000, idleTimeoutMillis: 10000,
});
const repository = new PostgresRepository(pool, Number(process.env.DATA_RETENTION_DAYS ?? "30"));
const env = {
  ...process.env,
  // The deletion credential is never accepted by the application listener.
  ...(worker ? {} : { DATA_TOKEN_RETENTION: undefined }),
};
let nextPendingCleanup = 0;
const runOnce = async () => {
  const target = process.env.BACKUP_REMOTE ?? "";
  await runRetention(pool, target);
  if (Date.now() >= nextPendingCleanup) {
    await cleanPendingPurges(pool, target);
    nextPendingCleanup = Date.now() + 60 * 60 * 1000;
  }
  // This stage acknowledges intake only. OA and AI processing are subsequent steps.
  await transaction(pool, async db => {
    await db.query(`WITH due AS (
      SELECT j.message_id FROM queue_jobs j JOIN visible_messages m ON m.id=j.message_id
      WHERE j.processed_at IS NULL ORDER BY j.created_at LIMIT 100 FOR UPDATE OF j SKIP LOCKED
    ), updated AS (
      UPDATE queue_jobs j SET processed_at=now() FROM due
      WHERE j.message_id=due.message_id RETURNING j.message_id
    ) INSERT INTO audit_log(actor,action,record_id)
      SELECT 'worker','intake.processed',message_id FROM updated`);
  });
};
if (command === "cron" || command === "delete-eligible") {
  try {
    if (command === "cron") await runOnce();
    else {
      const principal = authenticate(env.DATA_TOKEN_RETENTION ?? "", env);
      if (!principal) throw Error("forbidden");
      const accepted = await requestDeletion(pool, principal, JSON.parse(readFileSync(0, "utf8")));
      console.log(JSON.stringify({ accepted }));
      if (!accepted) process.exitCode = 1;
    }
  } finally { await pool.end(); }
} else if (command === "serve" || command === "worker") {
  let lastSuccess = 0;
  let running = false;
  let timer: NodeJS.Timeout | undefined;
  if (worker) {
    const tick = () => {
      if (running) return;
      running = true;
      void runOnce().then(() => { lastSuccess = Date.now(); }, () => {
        console.error("data_worker_cycle_failed");
      }).finally(() => { running = false; });
    };
    tick();
    timer = setInterval(tick, 30000);
  }
  const server = createServer(async (req, res) => {
    const fail = (status: number) => { res.writeHead(status).end(); };
    try {
      if (req.method === "GET" && req.url === "/health") {
        await pool.query("SELECT 1 FROM " + (worker ? "queue_jobs" : "visible_messages") + " LIMIT 1");
        fail(worker && Date.now() - lastSuccess > 120000 ? 503 : 200);
        return;
      }
      if (req.method !== "POST" ||
          !(worker ? req.url === "/retention" : ["/messages", "/tasks"].includes(req.url ?? ""))) {
        fail(404);
        return;
      }
      const principal = authenticate(req.headers.authorization?.match(/^Bearer (.+)$/)?.[1] ?? "", env);
      if (!principal) { fail(401); return; }
      let body = "";
      for await (const chunk of req) {
        body += chunk;
        if (Buffer.byteLength(body) > 32768) { fail(413); return; }
      }
      const parsed = JSON.parse(body);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) { fail(400); return; }
      if (worker) {
        fail(await requestDeletion(pool, principal, parsed) ? 202 : 409);
      } else if (req.url === "/tasks") {
        if (Object.keys(parsed).length !== 1 || typeof parsed.title !== "string" ||
            !parsed.title.trim() || parsed.title.length > 500) { fail(400); return; }
        const id = await repository.createTask(principal, parsed.title);
        res.writeHead(201, { "content-type": "application/json" }).end(JSON.stringify({ id }));
      } else {
        const { conversation_id, event_id, text } = parsed;
        if (Object.keys(parsed).length !== 3 || !uuid(conversation_id) || typeof event_id !== "string" ||
            !event_id || event_id.length > 256 || typeof text !== "string" || text.length > 16000) { fail(400); return; }
        fail(await repository.ingest(principal, conversation_id, event_id, text) ? 202 : 204);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "";
      fail(message === "forbidden" ? 403 : error instanceof SyntaxError || message === "invalid_deletion_request" ? 400 : 503);
    }
  });
  server.requestTimeout = 10000;
  server.listen(worker ? 8081 : 8080, "0.0.0.0");
  process.once("SIGTERM", () => {
    clearInterval(timer);
    server.close(() => { void pool.end(); });
  });
} else {
  await pool.end();
  throw Error("invalid_command");
}
