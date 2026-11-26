import { createHash, randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import { Store } from "../dist/ttd-zalo-agent-server/src/store.js";
import { LocalStore } from "../dist/ttd-zalo-agent-server/src/local-store.js";
import { PostgresRuntimeDatabase } from "../dist/ttd-zalo-agent-server/src/data/runtime-database.js";

export const usesPostgres = process.env.RUN_POSTGRES_TESTS === "1";
const migrations = usesPostgres ? ["001.sql", "002-runtime.sql"].map(file =>
  readFileSync(new URL("../postgres/" + file, import.meta.url), "utf8")) : [];
const schemas = new Map();

export function fixtureStore(t, path, key) {
  if (!usesPostgres) {
    const store = new LocalStore(path, key);
    t.after(() => store.db.close());
    return store;
  }
  const mapped = path !== ":memory:" && schemas.get(path);
  const schema = mapped || "fixture_" + createHash("sha256").update(randomUUID()).digest("hex").slice(0, 20);
  const db = new PostgresRuntimeDatabase({}, schema);
  if (!mapped) {
    db.exec("CREATE SCHEMA " + schema);
    for (const migration of migrations) db.exec(migration);
    if (path !== ":memory:") schemas.set(path, schema);
  }
  t.after(() => {
    try {
      if (!mapped) {
        db.exec("DROP SCHEMA " + schema + " CASCADE");
        schemas.delete(path);
      }
    } finally { db.close(); }
  });
  const store = new Store(db, key);
  const original = store.consent.bind(store);
  store.consent = (...args) => original(...args, {
    displayedText: "Fixture consent", policyVersion: "fixture-1", evidence: { source: "fixture" },
  });
  return store;
}
