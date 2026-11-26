import type { IncomingMessage, ServerResponse } from "node:http";
import { createHash, randomBytes, scrypt, timingSafeEqual } from "node:crypto";
import { promisify } from "node:util";
import type { Store } from "../store.js";

const derive = promisify(scrypt);
const digest = (text: string) => createHash("sha256").update(text).digest("hex");
const sessionName = "ttd_operator_session";
export type Operator = { id: string; label: string; role: "owner" | "sales" | "support" | "a0" };

export function json(response: ServerResponse, status: number, value?: unknown) {
  response.writeHead(status, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff" }).end(value === undefined ? undefined : JSON.stringify(value));
  return true;
}

export async function readJson(request: IncomingMessage): Promise<Record<string, unknown> | undefined> {
  if (request.headers["content-type"]?.split(";")[0].trim() !== "application/json") return;
  const chunks: Buffer[] = [];
  let length = 0;
  for await (const value of request.iterator({ destroyOnReturn: false })) {
    const chunk = Buffer.from(value);
    length += chunk.length;
    if (length > 4096) return;
    chunks.push(chunk);
  }
  try {
    const value = JSON.parse(Buffer.concat(chunks).toString("utf8"));
    return value && typeof value === "object" && !Array.isArray(value) ? value : undefined;
  } catch { return; }
}

export function operatorSessions(store: Store, configuredOrigin: string) {
  const origin = new URL(configuredOrigin);
  const loopback = origin.protocol === "http:" && ["localhost", "127.0.0.1", "[::1]"].includes(origin.hostname);
  if ((!loopback && origin.protocol !== "https:") || origin.origin !== configuredOrigin) throw Error("INVALID_WEB_ORIGIN");
  const ttl = 8 * 60 * 60;
  const cookie = (value: string, age: number) => `${sessionName}=${value}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${age}${loopback ? "" : "; Secure"}`;
  const token = (req: IncomingMessage) => new RegExp(`(?:^|;\\s*)${sessionName}=([0-9a-f]{64})(?:;|$)`).exec(req.headers.cookie ?? "")?.[1];
  const db = store.db;
  // Bound expensive password verification, independent of client-provided account names.
  let attempts = 0;
  let minute = 0;
  const fakeVerifier = randomBytes(16).toString("hex") + ":" + randomBytes(64).toString("hex");
  const authenticate = async (req: IncomingMessage): Promise<Operator | undefined> => {
    const value = token(req);
    if (!value) return;
    const row = db.prepare(`SELECT o.id,o.label,o.role FROM web_sessions s JOIN web_operators o ON o.id=s.operator_id
      WHERE s.digest=? AND o.enabled AND s.expires_at>clock_timestamp()`).get(digest(value));
    return row as Operator | undefined;
  };
  return {
    authenticate,
    allowWrite: (req: IncomingMessage) => req.headers.origin === configuredOrigin && req.headers["sec-fetch-site"] !== "cross-site",
    async handle(req: IncomingMessage, res: ServerResponse) {
      if (req.method === "GET") {
        const account = await authenticate(req);
        return account ? json(res, 200, account) : json(res, 401, { message: "Cần đăng nhập." });
      }
      if (req.method === "DELETE") {
        const value = token(req);
        if (value) db.prepare("DELETE FROM web_sessions WHERE digest=?").run(digest(value));
        res.setHeader("Set-Cookie", cookie("", 0));
        return json(res, 204);
      }
      if (req.method !== "POST") return json(res, 405, { message: "Phương thức không hợp lệ." });
      const input = await readJson(req);
      if (typeof input?.account !== "string" || typeof input.passphrase !== "string" ||
          input.account.length > 120 || input.passphrase.length > 256) return json(res, 400, { message: "Dữ liệu đăng nhập không hợp lệ." });
      const currentMinute = Math.floor(Date.now() / 60000);
      if (currentMinute !== minute) { minute = currentMinute; attempts = 0; }
      if (++attempts > 30) return json(res, 429, { message: "Quá nhiều lần đăng nhập. Thử lại sau." });
      const row = db.prepare("SELECT id,label,role,verifier FROM web_operators WHERE account=? AND enabled").get(input.account);
      const [salt, expected] = String(row?.verifier ?? fakeVerifier).split(":");
      const actual = await derive(input.passphrase, Buffer.from(salt, "hex"), 64) as Buffer;
      if (!timingSafeEqual(actual, Buffer.from(expected, "hex")) || !row) return json(res, 401, { message: "Thông tin đăng nhập không hợp lệ." });
      const value = randomBytes(32).toString("hex");
      const prior = token(req);
      store.atomic(() => {
        db.prepare("DELETE FROM web_sessions WHERE expires_at<=clock_timestamp() OR digest=?").run(prior ? digest(prior) : "");
        db.prepare("INSERT INTO web_sessions VALUES(?,?,clock_timestamp() + interval '8 hours')").run(digest(value), String(row.id));
      });
      res.setHeader("Set-Cookie", cookie(value, ttl));
      return json(res, 200, { id: row.id, label: row.label, role: row.role });
    },
  };
}
