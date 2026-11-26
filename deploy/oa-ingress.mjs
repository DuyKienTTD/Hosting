// Production packaging entry point for the already-merged OA inbox.
import { createHmac } from "node:crypto";
import { readFileSync } from "node:fs";
import { createServer } from "node:http";
import pg from "pg";
import { Envelope } from "./dist/ttd-zalo-agent-server/src/channels/oa/crypto.js";
import { OaTokens } from "./dist/ttd-zalo-agent-server/src/channels/oa/tokens.js";
import { accountScope, OaInbox, oaWebhook, oaWebhookMaxSkewMs } from "./dist/ttd-zalo-agent-server/src/channels/oa/webhook.js";

import { loginClientAddress } from "./dist/ttd-zalo-agent-server/src/web/login-limits.js";

const account = { appId: process.env.ZALO_APP_ID, oaId: process.env.ZALO_OA_ID,
  webhookSecret: process.env.ZALO_WEBHOOK_SECRET };
const key = process.env.ZALO_OA_ENCRYPTION_KEY ?? "";
if (!/^[a-f0-9]{64}$/i.test(key)) throw Error("OA_INVALID_ENCRYPTION_KEY");
const box = new Envelope(Buffer.from(key, "hex"));
const pool = new pg.Pool({ user: "data_runtime", password: process.env.DATA_RUNTIME_PASSWORD,
  max: 4, connectionTimeoutMillis: 500, statement_timeout: 1100, query_timeout: 1200 });
pool.on("error", () => console.error("OA database connection lost"));
const identity = { hash: value => createHmac("sha256", process.env.IDENTITY_KEY).update(value).digest("hex") };
const maxSkewMs = oaWebhookMaxSkewMs(process.env.OA_WEBHOOK_MAX_SKEW_SECONDS);
const clientAddress = loginClientAddress(process.env.TRUSTED_PROXY);
const handler = oaWebhook(new OaInbox(pool, identity, box, account, Date.now, maxSkewMs),
  request => clientAddress(request.socket.remoteAddress, request.headers["x-forwarded-for"]));

if (process.argv[2] === "install-tokens") {
  try {
    const token = JSON.parse(readFileSync(0, "utf8"));
    if (typeof token.access !== "string" || typeof token.refresh !== "string" ||
        !Number.isSafeInteger(token.issued) || token.issued > Date.now()) throw Error("invalid token input");
    await new OaTokens(pool, box, accountScope(account), account.appId, process.env.ZALO_APP_SECRET)
      .install({ access: token.access, refresh: token.refresh, seconds: token.seconds }, token.issued);
    console.log("OA token pair installed");
  } catch {
    console.error("OA token installation failed");
    process.exitCode = 1;
  } finally {
    await pool.end();
  }
} else if (process.argv[2] === "serve") {
  const server = createServer((req, res) => {
    if (req.method === "GET" && req.url === "/health") {
      void pool.query("SELECT 1 FROM oa_inbox LIMIT 0").then(() => res.writeHead(200).end("ok"),
        () => res.writeHead(503).end());
      return;
    }
    handler(req, res);
  });
  server.listen(8080, "0.0.0.0");
  process.once("SIGTERM", () => server.close(() => { void pool.end(); }));
} else {
  await pool.end();
  throw Error("invalid OA ingress command");
}
