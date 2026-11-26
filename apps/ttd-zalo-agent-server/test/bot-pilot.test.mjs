import assert from "node:assert/strict";
import { createServer } from "node:http";
import { test } from "node:test";
import { fixtureStore, usesPostgres } from "./runtime-store.mjs";
import { BotPilot, readBot } from "../dist/ttd-zalo-agent-server/src/channels/bot/pilot.js";
import { defaults } from "../dist/ttd-zalo-agent-server/src/config.js";

test("Bot starts in mock by default and live requires credentials", () => {
  assert.equal(readBot({}, false), undefined);
  assert.throws(() => readBot({ BOT_MODE: "live" }, true), /BOT_CONFIGURATION_REQUIRED/);
  assert.throws(() => readBot({ BOT_MODE: "other" }, true), /INVALID_BOT_MODE/);
});

test("authenticated Bot webhook is durable and replies go through guarded smoke admission", async t => {
  const store = fixtureStore(t, ":memory:", "fixture-bot-key");
  store.stop("global", false);
  const now = Date.now();
  const settings = readBot({ BOT_MODE: "live", ZALO_BOT_TOKEN: "fixture",
    ZALO_BOT_WEBHOOK_SECRET: "fixture-webhook", ZALO_BOT_ID: "fixture", BOT_SMOKE_ALLOWLIST: "peer" }, true);
  const target = store.hash("bot:fixture:peer");
  const calls = [];
  const bot = new BotPilot(settings, store, defaults, async (url, options) => {
    calls.push([url, JSON.parse(options.body)]);
    return Response.json({ ok: true, result: { message_id: "receipt" } });
  }, () => now);
  const server = createServer(bot.webhook);
  await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
  t.after(() => new Promise(resolve => server.close(resolve)));
  const url = `http://127.0.0.1:${server.address().port}`;
  const event = { event_name: "message.text.received", message: { message_id: "inbound", date: now,
    chat: { chat_type: "PRIVATE", id: "peer" }, from: { id: "peer", is_bot: false },
    message_type: "CHAT_TEXT", text: "fixture inbound" } };
  const post = (secret, body = JSON.stringify(event)) => fetch(url, {
    method: "POST", headers: { "X-Bot-Api-Secret-Token": secret }, body,
  });
  assert.equal((await fetch(url)).status, 405);
  assert.equal((await post("incorrect")).status, 403);
  assert.equal((await post(settings.secret, "x".repeat(17_000))).status, 413);
  assert.equal(Number(store.db.prepare("SELECT count(*) n FROM inbound").get().n), 0);
  store.consent(target, now + 60000, true, true, true, false, {
    displayedText: "fixture consent", policyVersion: "fixture", evidence: { fixture: true },
  });
  assert.equal((await post(settings.secret)).status, 200);
  assert.equal((await post(settings.secret)).status, 200);
  assert.equal(Number(store.db.prepare("SELECT count(*) n FROM inbound").get().n), 1);
  if (usesPostgres) {
    const row = store.db.prepare("SELECT c.channel,m.body FROM conversations c JOIN messages m ON m.conversation_id=c.id").get();
    assert.equal(row.channel, "bot");
    assert.equal(row.body, event.message.text);
  }
  store.stop("bot", true);
  assert.equal(await bot.reply("peer", "fixture"), "stopped");
  store.stop("bot", false);
  assert.equal(bot.status().state, "online");
  assert.equal(await bot.reply("other", "fixture"), "policy_denied");
  assert.equal(await new BotPilot({ ...settings, smokeOnly: false }, store, defaults).reply("peer", "fixture"), "policy_denied");
  assert.equal(calls.length, 0);
  assert.equal(await bot.reply("peer", "fixture"), "sent");
  assert.equal(await bot.reply("peer", "duplicate"), "duplicate");
  assert.deepEqual(calls, [["https://bot-api.zaloplatforms.com/botfixture/sendMessage", { chat_id: "peer", text: "fixture" }]]);
});
