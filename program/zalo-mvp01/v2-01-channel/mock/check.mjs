import assert from "node:assert/strict";
import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";
import { readFileSync } from "node:fs";
import { createServer } from "node:http";
import { createRequire } from "node:module";
import { test } from "node:test";

const fixtures = JSON.parse(readFileSync(new URL("./payloads.json", import.meta.url)));
const subizKey = randomBytes(32);
const botSecret = randomBytes(24).toString("hex");
const signature = (raw) => createHmac("sha256", subizKey).update(raw).digest();
const subizThread = "/4.0/conversations/synthetic-thread/messages";
const subizSend = "/4.1/conversations/synthetic-thread/messages";
const account = "synthetic-account";
const botId = "synthetic-bot";

function validSignature(header, raw) {
  if (!header?.startsWith("sha256=")) return false;
  const candidates = header.slice(7).split(",");
  return candidates.every((value) => /^[a-f0-9]{64}$/.test(value)) &&
    candidates.some((value) => timingSafeEqual(Buffer.from(value, "hex"), signature(raw)));
}

test("Loopback HTTP contracts and optional official SDK", async (t) => {
  const seen = new Set();
  const server = createServer(async (req, res) => {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const raw = Buffer.concat(chunks);
    const reply = (status, result, headers = {}) => {
      res.writeHead(status, { "content-type": "application/json", ...headers });
      res.end(JSON.stringify(result));
    };
    const url = new URL(req.url, "http://localhost");
    if (req.method === "POST" && url.pathname === "/webhook/subiz") {
      if (!validSignature(req.headers["x-hub-signature-256"], raw)) return reply(403, {});
      const { events } = JSON.parse(raw);
      const accepted = [];
      for (const event of events) {
        if (event.account_id !== account || event.type !== "message_sent" ||
            event.by?.type !== "user" || event.data?.message?.is_internal || seen.has(event.id)) continue;
        seen.add(event.id);
        accepted.push(event.id);
      }
      return reply(200, { accepted });
    }
    if (req.method === "POST" && url.pathname === "/webhook/bot") {
      if (req.headers["x-bot-api-secret-token"] !== botSecret) return reply(403, {});
      return reply(200, { accepted: JSON.parse(raw).message.message_id });
    }
    if (["/4.1/me", subizThread, subizSend].includes(url.pathname)) {
      if (req.headers.authorization !== "Bearer synthetic") {
        const code = "access_deny,internal";
        return reply(400, { code, class: 500, error: { code } });
      }
      if (req.method === "GET" && url.pathname === "/4.1/me") {
        return reply(200, { id: "synthetic-agent", account_id: account, fullname: "Fixture" });
      }
      if (req.method === "GET" && url.pathname === subizThread) {
        return reply(200, [fixtures.subizWebhook.events[0], fixtures.subizReceipt]);
      }
      if (req.method === "POST" && url.pathname === subizSend) {
        if (req.headers["x-fixture-scenario"] === "limit") {
          return reply(429, { class: 400, error: { code: "rate_limited" } }, { "retry-after": "2" });
        }
        if (req.headers["x-fixture-scenario"] === "disconnect") return res.destroy();
        const payload = JSON.parse(raw);
        if (payload.type !== "message_sent" || payload.data?.message?.text !== fixtures.subizSend.data.message.text) {
          return reply(400, { class: 400, error: { code: "invalid_input" } });
        }
        return reply(200, fixtures.subizReceipt);
      }
    }
    if (req.method === "POST" && url.pathname.startsWith("/bot")) {
      const [identity, operation] = url.pathname.slice(1).split("/");
      if (identity !== "bot" + botId) {
        return reply(200, { ok: false, error_code: 404, description: "Not Found" });
      }
      if (operation === "getMe") {
        return reply(200, { ok: true, result: { id: botId, account_name: "bot.fixture", account_type: "BASIC", can_join_groups: false } });
      }
      if (operation === "getUpdates") return reply(200, { ok: true, result: fixtures.botUpdate });
      if (operation === "sendMessage") {
        const payload = JSON.parse(raw);
        if (payload.chat_id === fixtures.botSend.chat_id && payload.text === fixtures.botSend.text) {
          return reply(200, fixtures.botReceipt);
        }
      }
    }
    return reply(404, {});
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(() => new Promise((resolve) => server.close(resolve)));
  const base = "http://127.0.0.1:" + server.address().port;
  const post = (path, body, headers = {}) => fetch(base + path, {
    method: "POST", body, headers: { "content-type": "application/json", ...headers },
  });
  const json = (path, payload, headers) => post(path, JSON.stringify(payload), headers);
  const auth = { authorization: "Bearer synthetic" };

  await t.test("Subiz auth, send acceptance, history and failure cases", async () => {
    const anonymous = await fetch(base + "/4.1/me");
    assert.equal(anonymous.status, 400);
    assert.equal((await anonymous.json()).error.code, "access_deny,internal");
    assert.equal((await (await fetch(base + "/4.1/me", { headers: auth })).json()).account_id, account);
    const sent = await json(subizSend, fixtures.subizSend, auth);
    assert.equal(sent.status, 200);
    assert.equal((await sent.json()).id, fixtures.subizReceipt.id);
    const history = await fetch(base + subizThread, { headers: auth });
    assert.equal(history.status, 200);
    assert.equal((await history.json()).length, 2);
    const limited = await json(subizSend, fixtures.subizSend, { ...auth, "x-fixture-scenario": "limit" });
    assert.equal(limited.status, 429);
    assert.equal(limited.headers.get("retry-after"), "2");
    await assert.rejects(json(subizSend, fixtures.subizSend, { ...auth, "x-fixture-scenario": "disconnect" }));
  });

  await t.test("Subiz HMAC, rotation, echo/internal filter and replay", async () => {
    const raw = JSON.stringify(fixtures.subizWebhook);
    const header = { "x-hub-signature-256": "sha256=" + "0".repeat(64) + "," + signature(raw).toString("hex") };
    assert.equal((await post("/webhook/subiz", raw)).status, 403);
    assert.equal((await post("/webhook/subiz", raw + " ", header)).status, 403);
    assert.deepEqual(await (await post("/webhook/subiz", raw, header)).json(), { accepted: ["subiz-inbound"] });
    assert.deepEqual(await (await post("/webhook/subiz", raw, header)).json(), { accepted: [] });
  });

  await t.test("Bot polling, private send, token error and webhook header", async () => {
    const wrong = await json("/botINVALID/getMe", {});
    assert.equal(wrong.status, 200);
    assert.equal((await wrong.json()).error_code, 404);
    assert.deepEqual(await (await json("/bot" + botId + "/getUpdates", { timeout: "1" })).json(),
      { ok: true, result: fixtures.botUpdate });
    assert.deepEqual(await (await json("/bot" + botId + "/sendMessage", fixtures.botSend)).json(), fixtures.botReceipt);
    assert.equal((await json("/webhook/bot", fixtures.botUpdate)).status, 403);
    assert.deepEqual(await (await json("/webhook/bot", fixtures.botUpdate,
      { "x-bot-api-secret-token": botSecret })).json(), { accepted: "bot-inbound" });
  });

  await t.test("Official SDK getMe, getUpdates, processUpdate and sendMessage", {
    skip: !process.env.V201_SDK_MODULE,
  }, async () => {
    const require = createRequire(import.meta.url);
    const Bot = require(process.env.V201_SDK_MODULE);
    const sdk = new Bot(botId, { baseApiUrl: base, polling: false, request: { proxy: false, timeout: 2000 } });
    assert.equal((await sdk.getMe()).id, botId);
    const update = await sdk.getUpdates({ timeout: "1" });
    assert.deepEqual(update, fixtures.botUpdate);
    let received;
    sdk.on("message", (message) => { received = message; });
    sdk.processUpdate(update);
    assert.equal(received.message_id, "bot-inbound");
    const sent = await sdk.sendMessage(fixtures.botSend.chat_id, fixtures.botSend.text);
    assert.equal(sent.message_id, "bot-outbound");
  });
});
