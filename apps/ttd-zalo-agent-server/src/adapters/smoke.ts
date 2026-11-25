import { setTimeout as wait } from "node:timers/promises";
import type { Config } from "../config.js";
import { Guard } from "../guard.js";
import type { Store } from "../store.js";
import type { setupChannels, Routes } from "./setup.js";
import { command } from "./router.js";

export async function smoke(store: Store, config: Config, routes: Routes, active: Awaited<ReturnType<typeof setupChannels>>,
  contactId: string | undefined, nonce: string | undefined, clock = Date.now, sleep = wait) {
  const route = routes.subiz.direct.find(r => r.contactId === contactId);
  if (!route || !nonce || !/^TTD-SMOKE-[A-Za-z0-9_-]{12,80}$/.test(nonce)) return { status: "FAIL", step: "pilot_configuration" };
  const target = store.hash(route.contactId);
  const policy = store.policy(target, "support", clock());
  if (!policy.respond || !policy.send || !route.friendUntil || route.friendUntil <= clock()) return { status: "FAIL", step: "policy" };
  if (!(await active.subiz.authenticate()).ok) return { status: "FAIL", step: "auth" };
  if (!(await active.subiz.verifyConversation(route)).ok) return { status: "FAIL", step: "route" };
  const started = clock();
  let cursor: string | undefined;
  for (let tries = 0; tries < 90; tries++) {
    const page = await active.subiz.receiveMessage(command(routes.subiz.accountId, store.hash(nonce), "receiveMessage", { cursor }));
    if (!page.ok) return { status: "FAIL", step: "receive" };
    cursor = page.value.nextCursor;
    const received = page.value.items.find(e => e.payload.senderId === route.contactId && e.payload.thread.kind === "direct" &&
      e.payload.thread.conversationId === route.conversationId && e.payload.text === nonce && Date.parse(e.occurredAt) >= started - 300_000);
    if (!received) { if (tries < 89 && page.value.items.length < 100) await sleep(1000); continue; }
    const history = await active.subiz.history(route.conversationId);
    if (!history.ok || !history.value.some((e: { id?: string }) => e?.id === received.eventId)) return { status: "FAIL", step: "history" };
    const id = store.eventKey(route.contactId, route.conversationId, received.eventId);
    store.db.prepare("INSERT OR IGNORE INTO inbound VALUES(?,?,?)").run(id, target, Date.parse(received.occurredAt));
    const guard = new Guard(store, active.channel, config, clock);
    const text = "TTD smoke ACK " + nonce;
    const result = await guard.dispatch({ id: "smoke:" + store.hash(route.contactId + ":" + nonce), origin: id,
      agent: "support", kind: "reply", target: route.contactId, thread: route.conversationId, text,
      revision: policy.revision, epoch: store.setting("epoch") });
    if (!["sent", "duplicate"].includes(result)) return { status: "FAIL", step: result };
    for (let check = 0; check < 5; check++) {
      const after = await active.subiz.history(route.conversationId);
      if (!after.ok) return { status: "FAIL", step: "send_history" };
      const matched = after.value.filter((e: any) => e?.account_id === routes.subiz.accountId &&
        e?.type === "message_sent" && e?.by?.type === "agent" && e.by.id === routes.subiz.agentId &&
        e?.data?.message?.conversation_id === route.conversationId && e?.data?.message?.text === text);
      if (matched.length > 1) return { status: "FAIL", step: "duplicate_history" };
      if (matched.length === 1) return { status: "PASS", auth: "PASS", receive: "PASS", send: "accepted_in_history", delivery: "confirm_on_recipient" };
      if (check < 4) await sleep(1000);
    }
    return { status: "FAIL", step: "send_history" };
  }
  return { status: "FAIL", step: "nonce_timeout" };
}
