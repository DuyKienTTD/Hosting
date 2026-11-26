import type { IncomingMessage, ServerResponse } from "node:http";
import type { Config } from "../config.js";
import { Guard } from "../guard.js";
import type { Store } from "../store.js";
import type { OaRuntimeChannel } from "../channels/oa/adapter.js";
import { oaTarget } from "../channels/oa/webhook.js";
import { json, readJson, type Operator } from "./http.js";
import { inboxProjector, type InboxSource } from "./inbox-projector.js";

type Draft = { id: string; revision: number; text: string };
// Work ROOM can provide an implementation. Drafts stay separate from manual sends.
export interface InboxDraftReader {
  find(conversationId: string, operator: Operator): Promise<Draft | null>;
}

export type OaWebInbox = ReturnType<typeof oaWebInbox>;
export function oaWebInbox(store: Store, config: Config, source: InboxSource, channel: OaRuntimeChannel,
  mode: "active" | "smoke_only" | "oa_unavailable", drafts?: InboxDraftReader) {
  const { project, decode, scope } = inboxProjector(store, source, config);
  const db = store.db;
  const guard = new Guard(store, channel, config, Date.now);
  const threadQuery = `SELECT c.id,c.customer_id,p.target,p.received_ms,p.origin_id,
      t.follow_at,t.following,t.withdrawn
    FROM conversations c
    JOIN LATERAL(SELECT target,received_ms,origin_id FROM web_oa_projection
      WHERE conversation_id=c.id AND scope=? ORDER BY received_ms DESC,event_id DESC LIMIT 1) p ON true
    JOIN oa_contacts t ON t.scope=? AND t.target=p.target
    WHERE c.channel='oa'`;
  const canReadBody = (operator: Operator) => operator.role === "owner" || operator.role === "support";

  const messages = {
    smoke_only: "Chế độ smoke-only đang khóa gửi.",
    oa_unavailable: "Runtime chưa bật gửi qua kênh OA.",
    stopped: "STOP đang bật.",
    oa_window_expired: "Ngoài cửa sổ tư vấn OA.",
    quota_exhausted: "Đã hết quota OA.",
    oa_interaction_missing: "Chưa xác minh được lần tương tác OA cuối.",
    oa_policy_denied: "Consent hoặc chính sách OA đang chặn gửi.",
    forbidden: "Vai trò hiện tại không có quyền gửi trả lời.",
    budget_held: "Đang tạm giữ do giới hạn ngân sách.",
  };
  function block(operator: Operator, target: string | undefined) {
    if (!canReadBody(operator)) return "forbidden";
    if (mode !== "active") return mode;
    if (store.stopped("support")) return "stopped";
    if (!target) return "oa_interaction_missing";
    return channel.quoteBlock(target, Date.now());
  }

  function resolveTarget(customer: string, hash: string) {
    const ids = db.prepare("SELECT uid FROM channel_identities WHERE customer_id=? AND channel='oa' AND account_id=? LIMIT 2")
      .all(customer, source.account.oaId);
    if (ids.length !== 1) return;
    const target = oaTarget(source.account, String(ids[0].uid));
    if (store.hash(target) === hash) return target;
  }

  function summary(row: Record<string, unknown>) {
    return { id: row.id, customerId: row.customer_id, lastInteractionAt: new Date(Number(row.received_ms)).toISOString(),
      following: row.withdrawn ? false : Number(row.follow_at) === 0 ? null : row.following === true };
  }

  async function handle(operator: Operator, req: IncomingMessage, res: ServerResponse) {
    const noInbox = () => json(res, 404, { message: "Không tìm thấy hội thoại." });
    if (req.method === "GET" && req.url === "/api/v1/inbox") {
      return json(res, 200, db.prepare(threadQuery + " AND NOT t.withdrawn ORDER BY p.received_ms DESC,c.id LIMIT 100")
        .all(scope, scope).map(summary));
    }
    const match = /^\/api\/v1\/inbox\/([a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})(\/replies)?$/i.exec(req.url ?? "");
    if (!match) return noInbox();
    const [, id, compose] = match;
    const thread = db.prepare(threadQuery + " AND c.id=? AND NOT t.withdrawn").get(scope, scope, id);
    if (!thread) return noInbox();
    const target = resolveTarget(String(thread.customer_id), String(thread.target));
    const denial = block(operator, target);

    if (req.method === "GET" && !compose) {
      const retain = store.contact(String(thread.target))?.retain === 1;
      const incoming = db.prepare(`SELECT p.event_id AS id,p.event_id,p.target,p.received_ms AS at,
          CASE WHEN ?::boolean THEN m.body ELSE NULL END AS body,
          CASE WHEN ?::boolean AND NOT p.retained AND raw.id IS NULL AND t.record_id IS NULL
            AND i.expires_at>clock_timestamp() THEN encode(i.sealed,'base64') END AS sealed
        FROM web_oa_projection p LEFT JOIN oa_inbox i USING(scope,event_id)
        LEFT JOIN messages raw ON raw.conversation_id=p.conversation_id AND raw.event_id=p.origin_id
        LEFT JOIN visible_messages m ON m.id=raw.id
        LEFT JOIN restore_tombstones t ON t.conversation_id=p.conversation_id AND t.event_id=p.origin_id
        WHERE p.scope=? AND p.conversation_id=? ORDER BY p.received_ms DESC,p.event_id LIMIT 25`)
        .all(String(canReadBody(operator) && retain), String(canReadBody(operator)), scope, id)
        .map(row => ({ id: row.id, at: new Date(Number(row.at)).toISOString(), direction: "incoming",
          text: row.body ?? decode({ event_id: row.event_id, target: row.target, sealed: row.sealed })?.text ?? null }));
      const outgoing = db.prepare(`SELECT s.id,s.at,s.state,CASE WHEN ?::boolean THEN m.body END AS text
        FROM web_oa_replies r JOIN send_log s ON s.id=r.send_id
        LEFT JOIN messages raw ON raw.conversation_id=r.conversation_id AND raw.event_id=s.id
        LEFT JOIN visible_messages m ON m.id=raw.id
        WHERE r.conversation_id=? ORDER BY s.at DESC LIMIT 100`).all(String(canReadBody(operator) && retain), id)
        .map(row => ({ id: row.id, at: new Date(Number(row.at)).toISOString(), direction: "outgoing", text: row.text, delivery: row.state }));
      return json(res, 200, { ...summary(thread),
        sendBlock: denial ? { code: denial, message: messages[denial] } : null,
        messages: [...incoming, ...outgoing].sort((a, b) => a.at.localeCompare(b.at)),
        aiDraft: canReadBody(operator) && drafts ? await drafts.find(id, operator) : null });
    }
    if (req.method !== "POST" || !compose) return json(res, 405, { message: "Phương thức không hợp lệ." });
    if (!canReadBody(operator)) return json(res, 403, { code: "forbidden", message: messages.forbidden });
    if (denial || !target) {
      const code = denial ?? "oa_interaction_missing";
      return json(res, 409, { code, message: messages[code] });
    }
    const input = await readJson(req);
    const text = typeof input?.text === "string" ? input.text.trim() : "";
    if (!text || [...text].length > config.scheduling.maxText) return json(res, 400, { message: "Nội dung trả lời không hợp lệ." });
    const send = "web-oa-inbox:" + store.hash(JSON.stringify([id, thread.origin_id, text]));
    const sendId = store.hash(send);
    const contact = String(thread.target);
    const outcome = await guard.dispatch({ agent: "support", kind: "reply", purpose: "oa_inbox_reply",
      id: send, target, thread: target, origin: String(thread.origin_id), text,
      revision: store.policy(contact, "support", Date.now()).revision, epoch: store.setting("epoch") });
    if (["sent", "failed", "unknown", "duplicate"].includes(outcome)) {
      store.atomic(() => {
        if (outcome === "sent" && store.contact(contact)?.retain === 1) {
          store.retainMessage(contact, target, "oa", sendId, text, Date.now());
        }
        db.prepare(`INSERT INTO web_oa_replies(send_id,conversation_id)
          SELECT id,? FROM send_log WHERE id=? ON CONFLICT DO NOTHING`).run(id, sendId);
      });
      if (outcome === "sent") return json(res, 201, { delivery: "sent" });
      const code = outcome === "unknown" ? "unknown_delivery" : outcome;
      return json(res, outcome === "duplicate" ? 409 : 502,
        { code, message: "Lượt gửi đã được xử lý hoặc chưa rõ đã giao. Kiểm tra lịch sử trước khi gửi lại." });
    }
    const code = outcome === "stopped" || outcome === "quota_exhausted" || outcome === "budget_held"
      ? outcome : block(operator, target) ?? "oa_policy_denied";
    return json(res, 409, { code, message: messages[code] });
  }
  return { handle, project };
}
