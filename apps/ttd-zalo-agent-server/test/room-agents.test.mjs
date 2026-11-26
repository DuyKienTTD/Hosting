import assert from "node:assert/strict";
import { createHash, randomBytes } from "node:crypto";
import { readFileSync } from "node:fs";
import { createServer } from "node:http";
import test from "node:test";
import { defaults, light, strong } from "../dist/ttd-zalo-agent-server/src/config.js";
import { liveProvider, readLiveWiring } from "../dist/ttd-zalo-agent-server/src/live-wiring.js";
import { MockChannel } from "../dist/ttd-zalo-agent-server/src/channel.js";
import { Runtime } from "../dist/ttd-zalo-agent-server/src/runtime.js";
import { webApi } from "../dist/ttd-zalo-agent-server/src/web/api.js";
import { WebRoomAgents } from "../dist/ttd-zalo-agent-server/src/web/room-agents.js";
import { fixtureStore, usesPostgres } from "./runtime-store.mjs";

test("room mentions, role-scoped Router, review, owner-only costs and STOP",
  { skip: !usesPostgres }, async t => {
    const store = fixtureStore(t, ":memory:", randomBytes(32).toString("hex"));
    for (const migration of ["009-web-operator.sql", "015-room-agents.sql"]) {
      store.db.exec(readFileSync(new URL("../postgres/" + migration, import.meta.url), "utf8"));
    }
    store.stop("global", false);
    const config = structuredClone(defaults);
    const wiring = readLiveWiring({
      AI_MODE: "live", AI_ROUTER_API_KEY: randomBytes(32).toString("hex"), AI_MODEL_ALLOWLIST: [light, strong].join(","),
      MODEL_REPORT: strong, MODEL_CRM: light, AI_ROUTER_MONTHLY_USD: "30", AI_ROUTER_DAILY_USD: "1",
      AI_ROUTER_RATE_MULTIPLIER: "1", AI_DAILY_TOKENS: "50000", AI_MONTHLY_TOKENS: "500000",
    }, config, false, "mock");
    const calls = [];
    let responseChoice;
    const provider = liveProvider(wiring, config, async (_url, init) => {
      const body = JSON.parse(init.body);
      const data = JSON.parse(body.messages[0].content);
      const options = body.tools[0].input_schema.properties.choice.enum;
      calls.push({ model: body.model, data, options });
      return Response.json({ model: body.model, stop_reason: "tool_use", usage: { input_tokens: 100, output_tokens: 20 },
        content: [{ type: "tool_use", name: "propose", input: { choice: responseChoice ?? options[0] } }] });
    });
    const room = new WebRoomAgents(store, config, provider, true);
    const mock = new WebRoomAgents(store, config, provider, false);
    const origin = "https://fixture.invalid";
    const api = webApi(store, config, origin, undefined, 25000, undefined, undefined, undefined, undefined, undefined, room);
    const server = createServer((req, res) => void api(req, res).catch(() => res.writeHead(500).end()));
    await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
    t.after(() => server.close());
    const endpoint = "http://127.0.0.1:" + server.address().port + "/api/v1";
    function session(role) {
      const id = store.db.prepare("INSERT INTO web_operators(account,label,role,verifier) VALUES(?,?,?,?) RETURNING id")
        .get(role, role, role, randomBytes(16).toString("hex") + ":" + randomBytes(64).toString("hex")).id;
      const cookie = randomBytes(32).toString("hex");
      store.db.prepare("INSERT INTO web_sessions VALUES(?,?,now()+interval '1 day')")
        .run(createHash("sha256").update(cookie).digest("hex"), id);
      return { id, role, label: role, headers: { origin, "content-type": "application/json", cookie: "ttd_operator_session=" + cookie } };
    }
    const owner = session("owner");
    const support = session("support");
    const a0 = session("a0");
    const get = (path, headers) => fetch(endpoint + path, { headers });
    const post = (path, data, headers = owner.headers) =>
      fetch(endpoint + path, { method: "POST", headers, body: JSON.stringify(data) });
    const contact = "fixture-customer";
    store.consent(store.hash(contact), Date.now() + 3600_000, true, true, false, false);
    const channel = new MockChannel();
    const runtime = new Runtime(store, channel, provider, config);
    runtime.ingest({ id: "customer", contact, thread: "thread", kind: "dm", channel: "oa", at: Date.now(),
      text: "@crm gắn nhãn khách. Customer-only injection." });
    assert.equal(store.db.prepare("SELECT count(*)::int AS n FROM tasks").get().n, 0);
    assert.equal((await post("/room-messages", { text: "@report tóm tắt" }, support.headers)).status, 403);
    assert.equal((await post("/room-messages", { text: "@report tóm tắt" }, { ...owner.headers, origin: "https://other.invalid" })).status, 403);
    const report = (await (await post("/room-messages", { text: "@report tóm tắt hội thoại hôm nay" })).json()).task;
    await Promise.all([room.tick(), room.tick()]);
    assert.equal(calls.length, 1);
    assert.equal(calls[0].model, strong);
    assert.equal(calls[0].data.capability, "read");
    assert.deepEqual(calls[0].data.aggregate, { conversations: 1, messages: 1 });
    assert.doesNotMatch(JSON.stringify(calls[0]), /Customer-only injection/);
    const workspace = await (await get("/workspace", owner.headers)).json();
    assert.match(workspace.workItems.find(task => task.id === report.id).result, /1 hội thoại/);
    assert.equal((await post("/work-items/" + report.id + "/review", { decision: "accept" }, support.headers)).status, 403);
    assert.equal((await post("/work-items/" + report.id + "/review", { decision: "accept" })).status, 200);
    assert.equal((await post("/work-items/" + report.id + "/review", { decision: "accept" })).status, 409);
    const costs = await (await get("/agent-router", owner.headers)).json();
    assert.ok(costs.agents.find(agent => agent.id === "report").usedUsd > 0);
    assert.equal((await (await get("/agent-router", a0.headers)).json()).agents, undefined);
    assert.equal((await post("/agent-router/crm/enabled", { enabled: false }, a0.headers)).status, 403);
    assert.equal((await post("/agent-router/crm/enabled", { enabled: false })).status, 200);
    room.post(owner, "@crm gắn nhãn khách");
    await room.tick();
    assert.equal(calls.length, 1);
    assert.equal((await post("/agent-router/crm/enabled", { enabled: true })).status, 200);
    const proposal = room.post(owner, "@crm gắn nhãn khách").task;
    await room.tick();
    assert.equal(calls[1].model, light);
    assert.match(store.db.prepare("SELECT result FROM web_agent_runs WHERE task_id=?").get(proposal.id).result, /Chờ người duyệt/);
    responseChoice = "send_message";
    const rejected = room.post(owner, "@crm thử lựa chọn ngoài quyền").task;
    await room.tick();
    assert.match(store.db.prepare("SELECT result FROM web_agent_runs WHERE task_id=?").get(rejected.id).result, /chưa trả kết quả hợp lệ/);
    const simulated = room.post(owner, "@report tóm tắt").task;
    await mock.tick();
    assert.match(store.db.prepare("SELECT result FROM web_agent_runs WHERE task_id=?").get(simulated.id).result, /giả lập/);
    assert.equal(calls.length, 3);
    responseChoice = undefined;
    store.set("budgetStop", 1);
    const capped = room.post(owner, "@report tóm tắt").task;
    await room.tick();
    assert.match(store.db.prepare("SELECT result FROM web_agent_runs WHERE task_id=?").get(capped.id).result, /ngân sách/);
    assert.equal(calls.length, 3);
    assert.equal(channel.sent.size, 0);
    assert.equal(store.db.prepare("SELECT count(*)::int AS n FROM customer_field").get().n, 0);
  });
