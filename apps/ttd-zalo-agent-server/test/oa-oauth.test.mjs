import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { once } from "node:events";
import { createServer } from "node:http";
import test from "node:test";
import { oaOAuth } from "../dist/ttd-zalo-agent-server/src/web/oa-oauth.js";
import { OaInbox, oaWebhook } from "../dist/ttd-zalo-agent-server/src/channels/oa/webhook.js";

async function listen(t, run) {
  const server = createServer(run).listen(0, "127.0.0.1");
  await once(server, "listening");
  t.after(() => new Promise(resolve => server.close(resolve)));
  return "http://127.0.0.1:" + server.address().port;
}

test("owner OAuth PKCE binds state to the browser and active session, validates OA and installs once", async t => {
  const origin = "https://operator.example.invalid";
  let role = "owner";
  let enabled = true;
  const sessions = {
    allowWrite: request => request.headers.origin === origin,
    sessionDigest: request => request.headers.cookie === "owner_fixture" ? "digest_fixture" : undefined,
    authenticateDigest: () => enabled ? { role } : undefined,
  };
  const exchanges = [];
  const installs = [];
  const oa = { account: { appId: "app_fixture", oaId: "oa_fixture" }, appSecret: "fixture_only",
    tokens: { install: (...args) => installs.push(args) } };
  const handler = oaOAuth(origin, sessions, oa, (url, options) => {
    exchanges.push([url, options]);
    return Response.json({ access_token: "access_fixture", refresh_token: "refresh_fixture", expires_in: 90000 });
  });
  const endpoint = await listen(t, (req, res) => void handler(req, res));
  const start = (source = origin) => fetch(endpoint + "/api/v1/oa/oauth/start", { method: "POST",
    headers: { origin: source, cookie: "owner_fixture" } });
  assert.equal((await start("https://external.invalid")).status, 403);
  role = "support";
  assert.equal((await start()).status, 403);
  role = "owner";
  async function begin() {
    const response = await start();
    assert.equal(response.status, 200);
    const url = new URL((await response.json()).authorizationUrl);
    const cookies = response.headers.get("set-cookie");
    assert.match(cookies, /HttpOnly; SameSite=Lax; Max-Age=600; Secure/);
    assert.equal(url.origin + url.pathname, "https://oauth.zaloapp.com/v4/oa/permission");
    assert.equal(url.searchParams.get("redirect_uri"), origin + "/api/v1/oa/oauth/callback");
    return { url, cookie: cookies.split(";")[0] };
  }
  const finish = (flow, { cookie = flow.cookie, state = flow.url.searchParams.get("state"), oaId = "oa_fixture" } = {}) =>
    fetch(endpoint + "/api/v1/oa/oauth/callback?" + new URLSearchParams({ code: "fixture_code", state, oa_id: oaId }),
      { headers: { cookie }, redirect: "manual" });
  const first = await begin();
  assert.equal((await finish(first, { cookie: "" })).status, 403);
  assert.equal((await finish(first, { state: "mismatch" })).status, 403);
  enabled = false;
  assert.equal((await finish(first)).status, 403);
  enabled = true;
  assert.equal((await finish(first, { oaId: "different_oa" })).status, 400);
  assert.equal(exchanges.length, 0);
  const second = await begin();
  const result = await finish(second);
  assert.equal(result.status, 303);
  assert.equal(result.headers.get("location"), "/#channels");
  assert.equal(await result.text(), "");
  assert.equal((await finish(second)).status, 403);
  assert.equal(exchanges.length, 1);
  const [url, options] = exchanges[0];
  assert.equal(url, "https://oauth.zaloapp.com/v4/oa/access_token");
  assert.equal(options.headers.secret_key, oa.appSecret);
  assert.equal(options.body.get("grant_type"), "authorization_code");
  assert.equal(createHash("sha256").update(options.body.get("code_verifier")).digest("base64url"),
    second.url.searchParams.get("code_challenge"));
  assert.deepEqual(installs[0][0], { access: "access_fixture", refresh: "refresh_fixture", seconds: 90000 });
});

test("unsigned ingress probe is acknowledged without touching inbox and drops are IP-limited", async t => {
  const handler = oaWebhook({ accept: () => assert.fail("unsigned request reached inbox") }, req => String(req.headers["fixture-ip"]));
  const endpoint = await listen(t, handler);
  const post = ip => fetch(endpoint + "/webhooks/zalo-oa", { method: "POST", body: "{}", headers: { "fixture-ip": ip } });
  // Cross a full fixed window at most once, so a burst of 61 must hit the limit.
  const responses = await Promise.all(Array.from({ length: 61 }, () => post("source-a")));
  assert.ok(responses.some(res => res.status === 429));
  const separate = await post("source-b");
  assert.equal(separate.status, 200);
  assert.deepEqual(await separate.json(), { error: 0 });
});

test("signed webhook for another app or OA is acknowledged, counted separately and never reaches Postgres", async t => {
  const logger = t.mock.method(console, "warn", () => {});
  const account = { appId: "fixture_app", oaId: "fixture_oa", webhookSecret: "fixture_only" };
  const now = Date.now();
  let queries = 0;
  const inbox = new OaInbox({ query: async () => { queries++; } }, { hash: value => value },
    { seal: () => Buffer.from("fixture") }, account, () => now);
  const endpoint = await listen(t, oaWebhook(inbox));
  const post = async (fields, signed = true) => {
    const timestamp = String(now);
    const body = JSON.stringify({ timestamp, app_id: account.appId, recipient: { id: account.oaId },
      event_name: "user_send_text", sender: { id: "fixture_uid" },
      message: { msg_id: "fixture_message", text: "fixture body" }, ...fields });
    const signature = createHash("sha256").update(account.appId + body + timestamp + account.webhookSecret).digest("hex");
    const result = await fetch(endpoint + "/webhooks/zalo-oa", { method: "POST", body,
      headers: signed ? { "x-zevent-signature": "mac=" + signature } : {} });
    assert.equal(result.status, 200);
    assert.deepEqual(await result.json(), { error: 0 });
  };
  await post({}, false);
  await post({ recipient: { id: "another_oa" } });
  await post({ app_id: "another_app" });
  assert.equal(queries, 0);
  assert.deepEqual(logger.mock.calls.map(call => JSON.parse(call.arguments[0])), [
    { event: "oa_webhook_dropped", count: 1 },
    { event: "oa_webhook_dropped", reason: "wrong_target", count: 1 },
    { event: "oa_webhook_dropped", reason: "wrong_target", count: 2 },
  ]);
  await post({});
  assert.equal(queries, 1);
});
