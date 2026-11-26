import { Worker } from "node:worker_threads";
import type { ClientConfig } from "pg";
import type { Parameter, Row, RuntimeDatabase } from "../sql.js";

export class PostgresRuntimeDatabase implements RuntimeDatabase {
  readonly backend = "postgres";
  private readonly worker: Worker;
  private readonly shared = new SharedArrayBuffer(4 * 1024 * 1024);
  private closed = false;
  constructor(config: ClientConfig, schema = "public") {
    if (!/^[a-z][a-z0-9_]{0,60}$/.test(schema)) throw Error("INVALID_RUNTIME_SCHEMA");
    this.worker = new Worker(new URL("./sql-worker.js", import.meta.url), {
      workerData: { ...config, options: "-c search_path=" + schema },
    });
    this.worker.on("error", () => { this.closed = true; });
    this.worker.unref();
  }
  // A connection is dedicated to this runtime so synchronous policy callbacks
  // remain indivisible. A deadline terminates the connection instead of retrying.
  private request(sql: string, parameters?: Parameter[], close = false): { rows: Row[]; changes: number } {
    if (this.closed) throw Error("REPOSITORY_CLOSED");
    const header = new Int32Array(this.shared, 0, 2);
    Atomics.store(header, 0, 0);
    this.worker.postMessage({ sql, parameters, close, shared: this.shared });
    if (Atomics.wait(header, 0, 0, 6000) === "timed-out") {
      this.closed = true;
      void this.worker.terminate();
      throw Error("REPOSITORY_TIMED_OUT");
    }
    const bytes = new Uint8Array(this.shared, 8, Atomics.load(header, 1));
    const payload = Buffer.from(bytes).toString("utf8");
    if (Atomics.load(header, 0) !== 1) throw Error("POSTGRES_" + payload);
    return JSON.parse(payload);
  }
  prepare(statement: string) {
    let parameter = 0;
    // Common statements use positional placeholders and standard SQL. SQLite's
    // insert-ignore forms are supported for existing local fixtures.
    const ignore = /^INSERT OR IGNORE INTO /i.test(statement);
    const sql = statement.replace(/^INSERT OR IGNORE INTO /i, "INSERT INTO ")
      .replace(/\?( IS NULL)?/g, (_, nullable) => "$" + ++parameter + (nullable ? "::text IS NULL" : "")) +
      (ignore ? " ON CONFLICT DO NOTHING" : "");
    return {
      get: (...values: Parameter[]) => this.request(sql, values).rows[0],
      all: (...values: Parameter[]) => this.request(sql, values).rows,
      run: (...values: Parameter[]) => ({ changes: this.request(sql, values).changes }),
    };
  }
  exec(sql: string) { this.request(sql); }
  close() {
    if (this.closed) return;
    try { this.request("", [], true); }
    finally { this.closed = true; void this.worker.terminate(); }
  }
}
