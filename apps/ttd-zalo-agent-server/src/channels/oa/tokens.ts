import { randomUUID } from "node:crypto";
import type { Pool, PoolClient } from "pg";
import { Envelope } from "./crypto.js";

// https://docs.zaloplatforms.com/docs/OA/bat-dau/xac-thuc-va-uy-quyen-cho-ung-dung-new
const oauthUrl = "https://oauth.zaloapp.com/v4/oa/access_token";
const accessLifetime = 90_000;
const refreshHeadroom = 60_000;

type TokenRow = {
  generation: string; access_cipher: Buffer | null; refresh_cipher: Buffer | null;
  access_until: Date; refresh_until: Date;
};
export type Access = { value: string; generation: string; expires: number };
type Pair = { access: string; refresh: string; seconds: number };

export class OaTokens {
  constructor(private readonly pool: Pool, private readonly box: Envelope, readonly scope: string,
    private readonly appId: string, private readonly appSecret: string,
    private readonly endpoint = oauthUrl, private readonly clock = Date.now) {}

  private async locked<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
    const client = await this.pool.connect();
    let unlocked = false;
    try {
      await client.query("SELECT pg_advisory_lock(hashtextextended($1,0))", ["oa:oauth:" + this.scope]);
      try { return await fn(client); }
      finally {
        await client.query("SELECT pg_advisory_unlock(hashtextextended($1,0))", ["oa:oauth:" + this.scope]);
        unlocked = true;
      }
    } finally { client.release(!unlocked); }
  }

  private context(generation: string, kind: "access" | "refresh") {
    return JSON.stringify(["oa-oauth", this.scope, generation, kind]);
  }

  private async save(client: PoolClient, pair: Pair, issued: number): Promise<Access> {
    if (!pair.access || !pair.refresh || !Number.isInteger(pair.seconds) || pair.seconds < 1) throw Error("OA_INVALID_TOKEN_PAIR");
    const generation = randomUUID();
    const expires = issued + Math.min(pair.seconds, accessLifetime) * 1000;
    await client.query(`INSERT INTO oa_oauth VALUES ($1,$2,$3,$4,$5,$6::timestamptz + interval '3 months')
      ON CONFLICT(scope) DO UPDATE SET generation=excluded.generation,access_cipher=excluded.access_cipher,
      refresh_cipher=excluded.refresh_cipher,access_until=excluded.access_until,refresh_until=excluded.refresh_until`,
    [this.scope, generation, this.box.seal(pair.access, this.context(generation, "access")),
      this.box.seal(pair.refresh, this.context(generation, "refresh")), new Date(expires), new Date(issued)]);
    return { value: pair.access, generation, expires };
  }

  /** Called by the trusted authorization bootstrap after the OAuth code exchange. */
  async install(pair: Pair, issued: number) {
    await this.locked(client => this.save(client, pair, issued));
  }

  async invalidate(generation: string) {
    await this.pool.query("UPDATE oa_oauth SET access_cipher=NULL WHERE scope=$1 AND generation=$2",
      [this.scope, generation]);
  }

  async current(): Promise<Access> {
    return this.locked(async client => {
      const { rows: [row] } = await client.query<TokenRow>("SELECT * FROM oa_oauth WHERE scope=$1", [this.scope]);
      const now = this.clock();
      if (row?.access_cipher && +row.access_until > now + refreshHeadroom) {
        return { value: this.box.open(row.access_cipher, this.context(row.generation, "access")),
          generation: row.generation, expires: +row.access_until };
      }
      if (!row?.refresh_cipher || +row.refresh_until <= now) throw Error("OA_REAUTHORIZATION_REQUIRED");

      const refresh = this.box.open(row.refresh_cipher, this.context(row.generation, "refresh"));
      // Commit consumption before the remote call. After a crash or ambiguous response,
      // the old one-time refresh token must never be presented again.
      await client.query("UPDATE oa_oauth SET refresh_cipher=NULL,access_cipher=NULL WHERE scope=$1", [this.scope]);
      try {
        const result = await fetch(this.endpoint, {
          method: "POST", redirect: "error", signal: AbortSignal.timeout(5000),
          headers: { secret_key: this.appSecret, "content-type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ grant_type: "refresh_token", app_id: this.appId, refresh_token: refresh }),
        });
        if (!result.ok) throw Error();
        const data = await result.json();
        if (typeof data?.access_token !== "string" || typeof data.refresh_token !== "string" ||
          data.refresh_token === refresh || (data.error !== undefined && data.error !== 0)) throw Error();
        return await this.save(client, {
          access: data.access_token, refresh: data.refresh_token,
          seconds: Number(data.expires_in ?? data.expire_in),
        }, now);
      } catch { throw Error("OA_REAUTHORIZATION_REQUIRED"); }
    });
  }
}
