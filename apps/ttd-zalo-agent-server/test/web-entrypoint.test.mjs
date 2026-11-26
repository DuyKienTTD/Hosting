import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createHash, randomBytes, randomUUID, scryptSync } from "node:crypto";
import { once } from "node:events";
import { readFile } from "node:fs/promises";
import { createServer, request } from "node:http";
import { resolve } from "node:path";
import test from "node:test";
import { Pool } from "pg";
import { chromium } from "playwright";
import { Envelope } from "../dist/ttd-zalo-agent-server/src/channels/oa/crypto.js";
import { OaTokens } from "../dist/ttd-zalo-agent-server/src/channels/oa/tokens.js";
import { accountScope, oaTarget } from "../dist/ttd-zalo-agent-server/src/channels/oa/webhook.js";
import { PostgresRuntimeDatabase } from "../dist/ttd-zalo-agent-server/src/data/runtime-database.js";
import { Store } from "../dist/ttd-zalo-agent-server/src/store.js";

const hour = 3600000;
async function listen(handler) {
  const server = createServer(handler).listen(0, "127.0.0.1");
  await once(server, "listening");
  return server;
}
const address = server => `http://127.0.0.1:${server.address().port}`;
const close = async server => { server.closeAllConnections(); await new Promise(done => server.close(done)); };

test("production Web UI receives and replies to OA and sends an approved quote", {
  skip: process.env.RUN_POSTGRES_TESTS !== "1" || !process.env.WEB_UI_TEST_DIST,
  timeout: 120_000,
}, async t => {
  const database = "web_test_" + randomUUID().replaceAll("-", "");
  const admin = new Pool();
  await admin.query("CREATE DATABASE " + database);
  const pg = new Pool({ database });
  t.after(async () => {
    await pg.end();
    try { await admin.query("DROP DATABASE " + database + " WITH (FORCE)"); }
    finally { await admin.end(); }
  });
  for (const name of ["001.sql", "002-runtime.sql", "runtime-grants.sql", "006-oa.sql", "007-oa-quota.sql", "009-web-operator.sql", "010-web-accounts.sql", "011-web-oa-inbox.sql"]) {
    let sql = await readFile(new URL("../postgres/" + name, import.meta.url), "utf8");
    if (name === "runtime-grants.sql") sql = sql.split("\n").filter(line => line.startsWith("GRANT ")).join("\n");
    await pg.query(sql);
  }
  const calls = [];
  const upstream = await listen(async (req, res) => {
    if (req.method !== "POST" || req.url !== "/v3.0/oa/message/cs") return res.writeHead(404).end();
    const parts = [];
    for await (const chunk of req) parts.push(chunk);
    const data = JSON.parse(Buffer.concat(parts));
    calls.push(data);
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ error: 0, data: { message_id: "fixture_" + calls.length, user_id: data.recipient.user_id } }));
  });
  t.after(() => close(upstream));

  const key = randomBytes(32).toString("hex");
  const oaKey = randomBytes(32);
  const account = { appId: "fixture_app", oaId: "fixture_oa", webhookSecret: randomUUID() };
  const appSecret = randomUUID();
  const now = Date.now();
  await new OaTokens(pg, new Envelope(oaKey), accountScope(account), account.appId, appSecret)
    .install({ access: randomUUID(), refresh: randomUUID(), seconds: 90_000 }, now);
  const password = randomBytes(20).toString("hex");
  for (const role of ["owner", "sales", "support", "a0"]) {
    const salt = randomBytes(16);
    await pg.query("INSERT INTO web_operators(account,label,role,verifier) VALUES($1,$1,$1,$2)",
      [role, salt.toString("hex") + ":" + scryptSync(password, salt, 64).toString("hex")]);
  }
  const runtime = new Store(new PostgresRuntimeDatabase({ database, user: "data_runtime",
    password: process.env.DATA_RUNTIME_PASSWORD }), key);
  t.after(() => runtime.db.close());
  runtime.stop("global", false);
  await pg.query(`INSERT INTO catalogue(id,sku,kind,title,summary,version,effective,origin)
    VALUES('fixture-product','FIX','product','Sản phẩm thử','Fixture','1','2020-01-01','fixture')`);
  await pg.query(`INSERT INTO web_approved_prices(catalogue_id,price_list,millimetres_per_bar,bars_per_set,vnd_per_metre)
    VALUES('fixture-product','fixture-price',2500,4,120000)`);

  async function customer(uid, age, optOut = false) {
    const target = oaTarget(account, uid);
    const hash = runtime.hash(target);
    runtime.consent(hash, now + 24 * hour, true, true, true, false,
      { displayedText: "Fixture", policyVersion: "fixture", evidence: { source: "fixture" } });
    const { customer_id: id } = runtime.db.prepare("SELECT customer_id FROM runtime_customer WHERE target=?").get(hash);
    const at = now - age * hour;
    const inbound = runtime.eventKey(target, target, "inbound-" + uid);
    runtime.db.prepare("INSERT INTO inbound VALUES(?,?,?)").run(inbound, hash, at);
    runtime.retainMessage(hash, target, "oa", inbound, "Tin fixture", at);
    await pg.query("UPDATE customers SET display_name=$2 WHERE id=$1", [id, uid]);
    await pg.query("INSERT INTO channel_identities VALUES('oa',$1,$2,$3)", [account.oaId, uid, id]);
    await pg.query("INSERT INTO oa_contacts(scope,target,interaction_at) VALUES($1,$2,$3)", [accountScope(account), hash, at]);
    if (optOut) runtime.optOut(hash);
    return { id, inbound };
  }
  const free = await customer("fixture_free", 47);
  const expired = await customer("fixture_expired", 8 * 24);
  const late = await customer("fixture_late", 49);
  const opted = await customer("fixture_opted", 1, true);
  const recent = await customer("fixture_recent", 1);
  const draft = (await pg.query(`INSERT INTO web_reply_drafts(conversation_id,inbound_id,body)
    SELECT id,$2,'Bản nháp fixture' FROM conversations WHERE customer_id=$1 RETURNING id`, [recent.id, recent.inbound])).rows[0];

  const portProbe = await listen();
  const port = portProbe.address().port;
  await close(portProbe);
  const host = `http://127.0.0.1:${port}`;
  const dist = resolve(process.env.WEB_UI_TEST_DIST);
  const frontend = await listen((req, res) => {
    const forward = request(host + req.url, { method: req.method, headers: req.headers }, result => {
      res.writeHead(result.statusCode, result.headers);
      result.pipe(res);
    });
    forward.on("error", () => res.writeHead(502).end());
    req.pipe(forward);
  });
  t.after(() => close(frontend));
  const origin = address(frontend);
  const child = spawn(process.execPath, ["dist/ttd-zalo-agent-server/src/main.js", "serve"], {
    env: { ...process.env, PGDATABASE: database, IDENTITY_KEY: key, HTTP_PORT: String(port), HTTP_BIND: "local",
      CHANNEL_MODE: "oa", CHANNEL_SMOKE_ONLY: "1", WEB_ORIGIN: origin, WEB_DIST: dist, ADS_ENABLED: "false", CLAUDE_ENABLED: "0",
      AI_PROVIDER: "anthropic", OA_APP_ID: account.appId, OA_ID: account.oaId, OA_APP_SECRET: appSecret,
      OA_WEBHOOK_SECRET: account.webhookSecret, OA_ENVELOPE_KEY: oaKey.toString("hex"),
      OA_FIXTURE_ENDPOINT: address(upstream), OA_MONTHLY_QUOTA: "0" },
    stdio: ["ignore", "ignore", "pipe"],
  });
  let startup = "";
  child.stderr.on("data", data => { startup = (startup + data).slice(-2048); });
  t.after(async () => {
    if (child.exitCode === null && child.signalCode === null) {
      const exited = once(child, "exit");
      child.kill("SIGTERM");
      await exited;
    }
  });
  let ready = false;
  for (let i = 0; i < 100 && child.exitCode === null; i++) {
    ready = await fetch(host + "/health").then(r => r.ok, () => false);
    if (ready) break;
    await new Promise(done => setTimeout(done, 50));
  }
  assert.ok(ready, startup);
  const health = await fetch(origin + "/health", { method: "HEAD" });
  assert.equal(health.status, 200);
  assert.equal(await health.text(), "");
  assert.equal((await fetch(origin + "/assets/unknown.js")).status, 404);
  const post = (path, data, session, requestOrigin = origin) => fetch(origin + "/api/v1/" + path, {
    method: "POST", headers: { "Content-Type": "application/json", Origin: requestOrigin, ...(session ? { cookie: session } : {}) },
    body: JSON.stringify(data),
  });
  const read = (path, session) => fetch(origin + "/api/v1/" + path, { headers: { cookie: session } });
  async function login(role) {
    const response = await post("session", { account: role, passphrase: password });
    assert.equal(response.status, 200);
    return response.headers.get("set-cookie").split(";")[0];
  }
  const input = customerId => ({ customerId, productId: "fixture-product", unit: "bar", quantity: 2,
    priceList: "fixture-price", confirmed: true, lastInteractionAt: Date.now(), role: "owner" });
  const owner = await login("owner");
  const sales = await login("sales");
  const support = await login("support");
  const a0 = await login("a0");
  assert.equal((await read("session", owner)).status, 200);
  assert.equal((await read("workspace", owner)).status, 200);
  assert.equal((await read("agent-router", owner)).status, 200);
  assert.equal((await read("settings", a0)).status, 200);
  assert.equal((await read("agent-router", support)).status, 403);
  for (const session of [support, a0]) assert.equal((await post("quotes/oa-send", input(free.id), session)).status, 403);
  assert.equal((await post("quotes/oa-send", input(free.id), owner, "https://external.invalid")).status, 403);
  for (const [id, code] of [[expired.id, "oa_window_expired"], [late.id, "quota_exhausted"], [opted.id, "oa_policy_denied"]]) {
    const response = await post("quotes/oa-send", input(id), sales);
    assert.equal(response.status, 409);
    assert.equal((await response.json()).code, code);
  }
  assert.equal((await post("quotes", { ...input(free.id), priceList: "forged" }, sales)).status, 409);
  assert.equal((await post("quotes", input(free.id), sales)).status, 201);
  assert.equal((await post("room-messages", { text: "Trao đổi fixture" }, owner)).status, 201);
  assert.equal((await post("work-items", { title: "Việc fixture", agent: "A1" }, owner)).status, 201);
  assert.equal((await post("deletion-requests", { customerId: free.id, reason: "Fixture" }, owner)).status, 201);
  assert.equal((await post("channels/nick/stop", {}, owner)).status, 200);

  const browser = await chromium.launch({ executablePath: process.env.PLAYWRIGHT_TEST_EXECUTABLE, headless: true });
  t.after(() => browser.close());
  const ownerPage = await browser.newPage();
  await ownerPage.goto(origin);
  await ownerPage.getByLabel("Tài khoản", { exact: true }).fill("owner");
  await ownerPage.getByLabel("Mật khẩu", { exact: true }).fill(password);
  await ownerPage.getByRole("button", { name: "Đăng nhập" }).click();
  await ownerPage.getByRole("link", { name: "Cài đặt", exact: true }).click();
  await ownerPage.getByLabel("Tên tài khoản").fill("fixture-browser-sales");
  await ownerPage.getByLabel("Tên hiển thị").fill("Sales fixture");
  await ownerPage.getByLabel("Vai trò").selectOption("sales");
  await ownerPage.getByLabel("Mật khẩu mới").fill(password);
  await ownerPage.getByRole("button", { name: "Tạo tài khoản" }).click();
  await ownerPage.getByText("Đã tạo tài khoản vận hành.").waitFor();
  assert.equal((await read("session", await login("fixture-browser-sales"))).status, 200);
  const page = await browser.newPage();
  await page.goto(origin);
  await page.getByLabel("Tài khoản", { exact: true }).fill("sales");
  await page.getByLabel("Mật khẩu", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await page.getByRole("link", { name: "Báo giá", exact: true }).click();
  await page.getByRole("combobox", { name: /Khách hàng/ }).selectOption(expired.id);
  await page.getByText("Ngoài cửa sổ 7 ngày", { exact: true }).waitFor();
  await page.getByRole("combobox", { name: /Khách hàng/ }).selectOption(late.id);
  await page.getByText("Hết quota tháng", { exact: true }).waitFor();
  await page.getByRole("combobox", { name: /Khách hàng/ }).selectOption(free.id);
  await page.getByRole("checkbox").check();
  const admission = page.waitForResponse(res => res.url().endsWith("/api/v1/quotes/oa-send") && res.request().method() === "POST");
  await page.getByRole("button", { name: "Duyệt & gửi qua OA" }).click();
  assert.equal((await admission).status(), 201);
  await page.getByText(/OA đã tiếp nhận/).waitFor();
  assert.equal(calls.length, 1);
  assert.equal(calls[0].recipient.user_id, "fixture_free");
  assert.match(calls[0].message.text, /600000 VND/);
  assert.deepEqual((await pg.query("SELECT state,quota_bucket,quota_month FROM send_log")).rows,
    [{ state: "sent", quota_bucket: "free_window", quota_month: null }]);
  assert.equal((await post("conversations/" + draft.id + "/approve", { version: 1, text: "Duyệt fixture" }, support)).status, 200);
  assert.equal(calls.length, 2);
  const uid = "fixture_live_inbox";
  const rawTarget = oaTarget(account, uid);
  const targetHash = runtime.hash(rawTarget);
  const text = "Khách gửi tin fixture qua webhook";
  async function webhook(name, extra) {
    const timestamp = String(Date.now());
    const body = JSON.stringify({ app_id: account.appId, timestamp, event_name: name, ...extra });
    const signature = createHash("sha256").update(account.appId + body + timestamp + account.webhookSecret).digest("hex");
    const response = await fetch(host + "/webhooks/zalo-oa", { method: "POST",
      headers: { "Content-Type": "application/json", "x-zevent-signature": "mac=" + signature }, body });
    assert.equal(response.status, 200);
  }
  const event = { sender: { id: uid }, recipient: { id: account.oaId }, message: { msg_id: "fixture-live-event", text } };
  await webhook("user_send_text", event);
  await webhook("user_send_text", event);
  await webhook("follow", { oa_id: account.oaId, follower: { id: uid }, event_id: "fixture-follow" });
  await ownerPage.getByRole("link", { name: "Hộp thư khách", exact: true }).click();
  await ownerPage.getByText(text, { exact: true }).waitFor({ timeout: 25_000 });
  await ownerPage.getByText("Đang quan tâm OA", { exact: true }).waitFor();
  const [row] = (await pg.query("SELECT conversation_id,origin_id,retained FROM web_oa_projection WHERE target=$1", [targetHash])).rows;
  assert.ok(row.conversation_id);
  assert.equal(row.retained, false);
  assert.equal((await pg.query("SELECT count(*)::int AS n FROM web_oa_projection WHERE target=$1", [targetHash])).rows[0].n, 1);
  assert.equal((await pg.query("SELECT count(*)::int AS n FROM messages WHERE event_id=$1", [row.origin_id])).rows[0].n, 0);
  const forSales = await (await read("inbox/" + row.conversation_id, sales)).json();
  assert.equal(forSales.messages[0].text, null);
  assert.equal((await post("inbox/" + row.conversation_id + "/replies", { text: "Denied" }, sales)).status, 403);
  assert.equal((await post("inbox/" + row.conversation_id + "/replies", { text: "No consent" }, support)).status, 409);

  runtime.consent(targetHash, Date.now() + hour, true, true, true, false,
    { displayedText: "Fixture", policyVersion: "fixture", evidence: { source: "fixture" } });
  runtime.stop("support", true);
  const blocked = await (await read("inbox/" + row.conversation_id, owner)).json();
  assert.equal(blocked.sendBlock.code, "stopped");
  runtime.stop("support", false);
  await ownerPage.getByRole("button", { name: /Làm mới/ }).click();
  const reply = "Trả lời OA fixture qua giao diện";
  await ownerPage.getByLabel("Nội dung trả lời").fill(reply);
  const manual = ownerPage.waitForResponse(res => res.url().endsWith("/replies") && res.request().method() === "POST");
  await ownerPage.getByRole("button", { name: "Gửi trả lời OA" }).click();
  assert.equal((await manual).status(), 201);
  await ownerPage.getByText(reply, { exact: true }).waitFor();
  assert.equal(calls.length, 3);
  assert.equal(calls[2].recipient.user_id, uid);
  assert.equal(calls[2].message.text, reply);
  assert.equal((await post("inbox/" + row.conversation_id + "/replies", { text: reply }, support)).status, 409);
  assert.equal(calls.length, 3);
  const threadPath = "inbox/" + row.conversation_id;
  for (const [age, code] of [[49, "quota_exhausted"], [168, "oa_window_expired"]]) {
    await pg.query("UPDATE oa_contacts SET interaction_at=$1 WHERE scope=$2 AND target=$3",
      [Date.now() - age * hour, accountScope(account), targetHash]);
    assert.equal((await (await read(threadPath, owner)).json()).sendBlock.code, code);
    assert.equal((await post(threadPath + "/replies", { text: "Guard fixture" }, support)).status, 409);
  }
  assert.equal(calls.length, 3);
  await webhook("unfollow", { oa_id: account.oaId, follower: { id: uid }, event_id: "fixture-unfollow" });
  const following = await (await read("inbox/" + row.conversation_id, owner)).json();
  assert.equal(following.following, false);

  assert.equal((await fetch(origin + "/api/v1/session", { method: "DELETE", headers: { Origin: origin, cookie: owner } })).status, 204);
  assert.equal((await read("session", owner)).status, 401);
});
