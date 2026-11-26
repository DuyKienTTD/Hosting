import { createHash, randomBytes } from "node:crypto";
import type { IncomingMessage, ServerResponse } from "node:http";
import type { OaAccount } from "../channels/oa/webhook.js";
import type { OaTokens } from "../channels/oa/tokens.js";
import { json, type operatorSessions } from "./http.js";

// https://docs.zaloplatforms.com/docs/OA/bat-dau/xac-thuc-va-uy-quyen-cho-ung-dung-new
// https://github.com/zaloplatform/zalo-php-sdk/blob/6bacb1bea670ce1fa9f1ae616bbbfd92742e20aa/src/Authentication/OAuth2Client.php#L109-L121
const permissionUrl = "https://oauth.zaloapp.com/v4/oa/permission";
const tokenUrl = "https://oauth.zaloapp.com/v4/oa/access_token";
const callback = "/api/v1/oa/oauth/callback";
const start = "/api/v1/oa/oauth/start";
const cookieName = "ttd_oa_oauth";
const ttl = 600_000;
export type OaOAuth = { account: OaAccount; appSecret: string; tokens: Pick<OaTokens, "install"> };

export function oaOAuth(origin: string, sessions: ReturnType<typeof operatorSessions>, oa: OaOAuth, fetcher = fetch) {
  const flows = new Map<string, { browser: string; verifier: string; session: string; expires: number }>();
  const redirectUri = new URL(callback, origin).href;
  const cookie = (browser: string, age: number) =>
    `${cookieName}=${browser}; Path=${callback}; HttpOnly; SameSite=Lax; Max-Age=${age}${origin.startsWith("https:") ? "; Secure" : ""}`;

  return async (request: IncomingMessage, response: ServerResponse) => {
    const url = new URL(request.url ?? "/", origin);
    if (url.pathname !== start && url.pathname !== callback) return false;
    response.setHeader("Cache-Control", "no-store");
    response.setHeader("Referrer-Policy", "no-referrer");
    if (url.pathname === start) {
      if (request.method !== "POST") return json(response, 405, {});
      if (!sessions.allowWrite(request)) return json(response, 403, {});
      const session = sessions.sessionDigest(request);
      if (!session || sessions.authenticateDigest(session)?.role !== "owner") return json(response, 403, {});
      const now = Date.now();
      for (const [state, flow] of flows) {
        if (flow.expires <= now || flow.session === session) flows.delete(state);
      }
      if (flows.size >= 256) return json(response, 429, {});
      const state = randomBytes(32).toString("hex");
      const browser = randomBytes(32).toString("hex");
      const verifier = randomBytes(32).toString("base64url");
      const challenge = createHash("sha256").update(verifier, "ascii").digest("base64url");
      flows.set(state, { browser, verifier, session, expires: now + ttl });
      const target = new URL(permissionUrl);
      target.search = new URLSearchParams({ app_id: oa.account.appId, redirect_uri: redirectUri,
        code_challenge: challenge, state }).toString();
      response.setHeader("Set-Cookie", cookie(browser, ttl / 1000));
      return json(response, 200, { authorizationUrl: target.href });
    }
    if (request.method !== "GET") return json(response, 405, {});
    const state = url.searchParams.get("state") ?? "";
    const flow = flows.get(state);
    const browser = new RegExp(`(?:^|;\\s*)${cookieName}=([a-f0-9]{64})(?:;|$)`).exec(request.headers.cookie ?? "")?.[1];
    if (!flow || flow.expires <= Date.now() || !browser || browser !== flow.browser ||
        sessions.authenticateDigest(flow.session)?.role !== "owner") return json(response, 403, { message: "Phiên kết nối OA không hợp lệ." });
    flows.delete(state);
    response.setHeader("Set-Cookie", cookie("", 0));
    const code = url.searchParams.get("code");
    if (!code || code.length > 4096 || url.searchParams.getAll("code").length !== 1 ||
        url.searchParams.getAll("state").length !== 1 || url.searchParams.getAll("oa_id").length !== 1 ||
        url.searchParams.get("oa_id") !== oa.account.oaId) return json(response, 400, { message: "OA chưa cấp quyền hoặc không đúng tài khoản." });
    try {
      const result = await fetcher(tokenUrl, { method: "POST", redirect: "error", signal: AbortSignal.timeout(5000),
        headers: { secret_key: oa.appSecret, "content-type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ code, app_id: oa.account.appId, grant_type: "authorization_code", code_verifier: flow.verifier }) });
      if (!result.ok) throw Error("OA_TOKEN_HTTP");
      const data = await result.json();
      const seconds = Number(data.expires_in ?? data.expire_in);
      if ((data.error !== undefined && data.error !== 0) || typeof data.access_token !== "string" || !data.access_token ||
          typeof data.refresh_token !== "string" || !data.refresh_token || !Number.isSafeInteger(seconds) ||
          seconds < 1 || sessions.authenticateDigest(flow.session)?.role !== "owner") throw Error("OA_TOKEN_INVALID");
      await oa.tokens.install({ access: data.access_token, refresh: data.refresh_token, seconds }, Date.now());
      response.writeHead(303, { Location: "/#channels" }).end();
      return true;
    } catch { return json(response, 502, { message: "Không thể hoàn tất kết nối OA. Hãy bắt đầu lại." }); }
  };
}
