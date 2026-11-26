import { randomBytes } from "node:crypto";
import type { Store } from "../store.js";

const valid = (value: unknown): value is string =>
  typeof value === "string" && /^[a-f0-9]{64}$/.test(value);

export function nickPairing(store: Store) {
  const db = store.db;
  const digest = (kind: string, value: string) => store.hash(`nick:${kind}:${value}`);
  return {
    issue() {
      const code = randomBytes(32).toString("hex");
      const expiresAt = Date.now() + 10 * 60_000;
      db.prepare(`INSERT INTO nick_enrollment(singleton,code_hash,expires_at) VALUES (1,?,?)
        ON CONFLICT(singleton) DO UPDATE SET code_hash=excluded.code_hash,expires_at=excluded.expires_at`)
        .run(digest("code", code), expiresAt);
      return { code, expiresAt };
    },
    exchange(code: unknown) {
      if (!valid(code)) return;
      const credential = randomBytes(32).toString("hex");
      const row = store.atomic(() => {
        const redeemed = db.prepare(`UPDATE nick_enrollment SET code_hash=NULL,expires_at=NULL,credential_hash=?
          WHERE singleton=1 AND code_hash=? AND expires_at>? RETURNING singleton`)
          .get(digest("credential", credential), digest("code", code), Date.now());
        if (redeemed) store.stop("nick", true);
        return redeemed;
      });
      if (row) return { credential };
    },
    accepts(credential: string) {
      return valid(credential) && !!db.prepare("SELECT 1 FROM nick_enrollment WHERE credential_hash=?")
        .get(digest("credential", credential));
    },
    revoke() {
      store.atomic(() => {
        db.prepare("DELETE FROM nick_enrollment WHERE singleton=1").run();
        store.stop("nick", true);
      });
    },
  };
}
