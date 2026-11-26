import { parentPort, workerData } from "node:worker_threads";
import { Client, types } from "pg";

types.setTypeParser(20, Number);
types.setTypeParser(1700, Number);
const client = new Client({ ...workerData, connectionTimeoutMillis: 4000,
  statement_timeout: 4500, lock_timeout: 3500, query_timeout: 5000,
  idle_in_transaction_session_timeout: 10000 });
client.on("error", () => { /* The next command fails closed. */ });
const connected = client.connect();
void connected.catch(() => {});
parentPort!.on("message", async ({ sql, parameters, shared, close }) => {
  const header = new Int32Array(shared, 0, 2);
  const data = new Uint8Array(shared, 8);
  try {
    await connected;
    const result = close ? await client.end() : await client.query(sql, parameters);
    const bytes = Buffer.from(JSON.stringify({ rows: result?.rows ?? [], changes: result?.rowCount ?? 0 }));
    if (bytes.length > data.length) throw Error("REPOSITORY_RESULT_LIMIT");
    data.set(bytes);
    Atomics.store(header, 1, bytes.length);
    Atomics.store(header, 0, 1);
  } catch (error) {
    const code = (error as { code?: string }).code;
    const bytes = Buffer.from(typeof code === "string" && /^[A-Z0-9]{5}$/.test(code) ? code : "QUERY_FAILED");
    data.set(bytes);
    Atomics.store(header, 1, bytes.length);
    Atomics.store(header, 0, 2);
  } finally { Atomics.notify(header, 0); }
});
