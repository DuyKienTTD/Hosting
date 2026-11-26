import type { OaWebInbox } from "./oa-inbox.js";
import { oaOAuth, type OaOAuth } from "./oa-oauth.js";
import type { OaAiDrafts } from "./ai-drafts.js";
import type { WebRoomAgents } from "./room-agents.js";
import { createOperator } from "./accounts.js";
import type { IncomingMessage, ServerResponse } from "node:http";
import { randomUUID } from "node:crypto";
import type { Store } from "../store.js";
import type { Config } from "../config.js";
import { vietnam } from "../config.js";
import { Guard } from "../guard.js";
import type { OaRuntimeChannel } from "../channels/oa/adapter.js";
import { oaTarget, type OaAccount } from "../channels/oa/webhook.js";
import { json, operatorSessions, readJson } from "./http.js";
import { oaQuotes, selection, type Selection } from "./oa-quotes.js";

const agents = ["Claude", "A1", "A2"];
const uuid = (value: unknown): value is string => typeof value === "string" &&
  /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i.test(value);
const clean = (value: unknown, length: number) =>
  typeof value === "string" && value.trim().length <= length && value.trim() || undefined;

export function webApi(store: Store, config: Config, origin: string,
  oa?: { account: OaAccount; channel: OaRuntimeChannel }, usdVnd?: number, nick?: { stop(): void; connected(): boolean; issue?(): { code: string; expiresAt: number }; revoke?(): void }, onboarding?: OaOAuth, inbox?: OaWebInbox, drafts?: OaAiDrafts, botStatus?: () => { state: string; detail: string }, room?: WebRoomAgents) {
  const db = store.db;
  const session = operatorSessions(store, origin);
  const oauth = onboarding && oaOAuth(origin, session, onboarding);
  const guard = oa && new Guard(store, oa.channel, config, Date.now);
  const approvedPrices = `FROM web_approved_prices p JOIN catalogue c ON c.id=p.catalogue_id
    WHERE p.revoked_at IS NULL AND p.approved_at<=clock_timestamp() AND c.effective<=?
    AND (c.until IS NULL OR c.until>=?)`;
  const date = () => vietnam(Date.now()).date;
  const byCustomer = (id: string) => {
    if (!oa) return;
    const ids = db.prepare("SELECT uid FROM channel_identities WHERE customer_id=? AND channel='oa' AND account_id=? LIMIT 2")
      .all(id, oa.account.oaId);
    if (ids.length !== 1) return;
    const target = oaTarget(oa.account, String(ids[0].uid));
    if (!db.prepare("SELECT 1 FROM runtime_customer WHERE customer_id=? AND target=?").get(id, store.hash(target))) return;
    return target;
  };
  function totals(input: Selection) {
    if (!uuid(input.customerId) || !db.prepare("SELECT 1 FROM customers WHERE id=?").get(input.customerId)) return;
    const today = date();
    const rate = db.prepare("SELECT p.millimetres_per_bar,p.bars_per_set,p.vnd_per_metre " + approvedPrices +
      " AND p.catalogue_id=? AND p.price_list=?").get(today, today, input.productId, input.priceList);
    if (!rate) return;
    const bar = Number(rate.millimetres_per_bar);
    const mm = Math.round(input.quantity * (input.unit === "metre" ? 1000 : input.unit === "bar" ? bar : bar * Number(rate.bars_per_set)));
    const vnd = (BigInt(mm) * BigInt(Number(rate.vnd_per_metre)) + 500n) / 1000n;
    if (vnd > BigInt(Number.MAX_SAFE_INTEGER)) return;
    return { totalMillimetres: mm, totalVnd: Number(vnd) };
  }
  function record(id: string, input: Selection, total: NonNullable<ReturnType<typeof totals>>, actor: string, sendKey: string | null) {
    db.prepare(`INSERT INTO web_quotes(id,send_key,operator_id,customer_id,catalogue_id,price_list,unit,quantity,total_mm,total_vnd)
      VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO NOTHING`).run(id, sendKey, actor, input.customerId, input.productId,
      input.priceList, input.unit, input.quantity, total.totalMillimetres, total.totalVnd);
  }
  const quotes = oa && oaQuotes({
    store, channel: oa.channel, config, authenticate: session.authenticate,
    async resolve(input) {
      const target = uuid(input.customerId) && byCustomer(input.customerId);
      const total = totals(input);
      if (!target || !total) return;
      const inbound = db.prepare("SELECT id FROM inbound WHERE target=? AND received>0 ORDER BY received DESC,id DESC LIMIT 1")
        .get(store.hash(target));
      // Guard verifies current send/respond grants, revocation and opt-out during admission.
      return { target, origin: String(inbound?.id ?? ""), ...total };
    },
    record(id, input, total, actor) { record(id, input, total, actor, store.hash(id)); },
  });

  function channels() {
    const stopped = store.stopped("nick");
    const connected = nick?.connected() ?? false;
    return [{ id: "oa", label: "Zalo OA", state: oa ? "online" : "offline", detail: oa ? "OA OpenAPI" : "Chưa cấu hình OA" },
      { id: "nick", label: "Nick Zalo phụ", state: stopped ? "stopped" : connected ? "online" : "offline", detail: stopped ? "Đã ghi STOP" : connected ? "Worker đã kết nối" : "Chưa kết nối worker" },
      { id: "bot", label: "Zalo Bot", ...(botStatus?.() ?? { state: "offline", detail: "Đang ở chế độ mock" }) }];
  }
  const conversationSelect = `SELECT d.id,c.customer_id AS "customerId",c.channel,
      coalesce(m.body,'') AS message,coalesce(to_char(m.received_at AT TIME ZONE 'Asia/Ho_Chi_Minh','HH24:MI'),'') AS time,
      'Hội thoại Zalo' AS subject,d.body AS draft,d.revision AS version,d.delivery
      FROM web_reply_drafts d JOIN conversations c ON c.id=d.conversation_id
      LEFT JOIN LATERAL (SELECT body,received_at FROM visible_messages WHERE conversation_id=c.id
        ORDER BY received_at DESC LIMIT 1) m ON true
      ${drafts ? "WHERE (d.ai_state IS NULL OR EXISTS (SELECT 1 FROM visible_messages src WHERE src.id=d.ai_message_id))" : ""}`;
  function workspace(showMessageBody: boolean) {
    const now = Date.now();
    const today = date();
    return {
      adsEnabled: store.setting("ADS_ENABLED") === 1,
      customers: db.prepare(`SELECT c.id,c.display_name AS label,r.target,s.state FROM customers c
        LEFT JOIN runtime_customer r ON r.customer_id=c.id LEFT JOIN ad_status s ON s.customer_id=c.id
        ORDER BY c.id LIMIT 250`).all().map(row => {
        const contact = typeof row.target === "string" ? store.contact(row.target, now) : undefined;
        const target = byCustomer(String(row.id));
        const consent = (purpose: string) => {
          const latest = db.prepare("SELECT withdrawn,valid_until_ms FROM consents WHERE customer_id=? AND purpose=? ORDER BY occurred_at DESC,id DESC LIMIT 1")
            .get(String(row.id), purpose);
          return !latest ? "unknown" : latest.withdrawn ? "withdrawn" : Number(latest.valid_until_ms) > now ? "granted" : "unknown";
        };
        return { id: row.id, label: row.label || row.id, segment: "", followUp: "",
          optOut: contact?.opted_out ? "stop" : contact?.ads_paused_review ? "review" : "none",
          oaQuoteBlock: target && quotes ? quotes.block(target) : "oa_interaction_missing",
          consent: { support: consent("respond"), quote: consent("send"), marketing: consent("ads") } };
      }),
      products: db.prepare(`SELECT c.id,c.title AS label,p.millimetres_per_bar AS "millimetresPerBar",
        p.bars_per_set AS "barsPerSet",p.vnd_per_metre AS "vndPerMetre",p.price_list AS "approvedPriceList" ` +
        approvedPrices + " ORDER BY c.id LIMIT 250").all(today, today),
      quotes: db.prepare(`SELECT q.id,q.customer_id AS "customerId",q.catalogue_id AS "productId",q.unit,
        q.quantity::float8 AS quantity,q.total_mm::float8 AS "totalMillimetres",q.total_vnd::float8 AS "totalVnd",
        CASE WHEN s.state IN ('sent','unknown_delivery','failed') THEN s.state END AS delivery
        FROM web_quotes q LEFT JOIN send_log s ON s.id=q.send_key ORDER BY q.created_at DESC LIMIT 100`).all()
        .map(({ delivery, ...row }) => delivery ? { ...row, delivery } : row),
      conversations: [
        ...db.prepare(conversationSelect + " ORDER BY d.id LIMIT 100").all()
          .map(row => showMessageBody ? row : { ...row, message: "", draft: "" }),
        ...(botStatus && showMessageBody ? db.prepare(`SELECT c.id,c.customer_id AS "customerId",
          c.channel,m.body AS message,to_char(m.received_at AT TIME ZONE 'Asia/Ho_Chi_Minh','HH24:MI') AS time,
          'Hội thoại Zalo Bot' AS subject,'' AS draft,0 AS version,'blocked' AS delivery,
          'Pilot Bot gửi qua lệnh đã qua Guard.' AS reason
          FROM conversations c JOIN LATERAL (SELECT body,received_at FROM visible_messages WHERE conversation_id=c.id
            ORDER BY received_at DESC,id DESC LIMIT 1) m ON true
          WHERE c.channel='bot' AND NOT EXISTS (SELECT 1 FROM web_reply_drafts d WHERE d.conversation_id=c.id)
          ORDER BY m.received_at DESC LIMIT 100`).all() : []),
      ],
      workItems: db.prepare(`SELECT t.id,t.title,a.agent,CASE t.state WHEN 'in_progress' THEN 'active' ELSE t.state END AS status
        ${room ? ",r.result,r.review_decision AS \"reviewDecision\"" : ""}
        FROM tasks t JOIN web_task_agents a ON a.task_id=t.id
        ${room ? "LEFT JOIN web_agent_runs r ON r.task_id=t.id" : ""} ORDER BY t.created_at DESC LIMIT 100`).all(),
      roomMessages: db.prepare(`SELECT m.id,o.label AS author,m.body AS text FROM web_room_messages m
        JOIN web_operators o ON o.id=m.operator_id ORDER BY m.created_at DESC LIMIT 100`).all(),
      deletionRequests: db.prepare(`SELECT id,customer_id AS "customerId",reason,'requested' AS status
        FROM web_deletion_requests ORDER BY created_at DESC LIMIT 100`).all(),
      channels: channels(),
      agents: room?.roster() ?? agents.map(label => ({ label, role: label === "Claude" ? "Điều phối" : "Thực thi", status: "Có thể giao việc" })),
      activity: [],
    };
  }

  async function approve(id: string, request: IncomingMessage, response: ServerResponse) {
    if (!guard) return json(response, 503, { message: "Chưa cấu hình kênh OA." });
    const input = await readJson(request);
    const text = clean(input?.text, config.scheduling.maxText);
    if (!text || !Number.isInteger(input?.version)) return json(response, 400, { message: "Bản nháp không hợp lệ." });
    const draft = db.prepare(`SELECT c.customer_id,c.channel,d.inbound_id,d.revision,d.delivery${drafts ? ",d.ai_state,d.ai_message_id,d.body" : ""}
      FROM web_reply_drafts d JOIN conversations c ON c.id=d.conversation_id WHERE d.id=?`).get(id);
    if (!draft) return json(response, 404, { message: "Không tìm thấy bản nháp." });
    const target = draft.channel === "oa" && byCustomer(String(draft.customer_id));
    if (draft.ai_state && (draft.ai_state !== "approved" || draft.body !== text ||
      !db.prepare("SELECT 1 FROM visible_messages WHERE id=?").get(String(draft.ai_message_id)))) {
      return json(response, 409, { message: "Cần duyệt đúng nội dung bản nháp AI trước khi gửi." });
    }
    if (!target || draft.delivery !== "draft" || draft.revision !== input?.version) {
      return json(response, 409, { message: "Bản nháp đã thay đổi hoặc kênh chưa sẵn sàng." });
    }
    const now = Date.now();
    const outcome = await guard.dispatch({ agent: "support", kind: "reply", id: "web-reply:" + id,
      target, thread: target, text, origin: String(draft.inbound_id), epoch: store.setting("epoch"),
      revision: store.policy(store.hash(target), "support", now).revision });
    if (outcome === "duplicate") return json(response, 409, { message: "Bản nháp đã được xử lý. Kiểm tra send_log." });
    if (outcome === "sent" || outcome === "unknown" || outcome === "failed") {
      const delivery = outcome === "sent" ? "sent" : outcome === "unknown" ? "unknown_delivery" : "blocked";
      db.prepare("UPDATE web_reply_drafts SET revision=revision+1,delivery=?,body=? WHERE id=? AND revision=?").run(delivery, text, id, Number(draft.revision));
      return json(response, 200, db.prepare(conversationSelect + (drafts ? " AND d.id=?" : " WHERE d.id=?")).get(id));
    }
    return json(response, 409, { message: "Guard đang chặn lượt gửi." });
  }

  return async (request: IncomingMessage, response: ServerResponse) => {
    if (oauth && await oauth(request, response)) return true;
    const path = request.url;
    if (!path?.startsWith("/api/v1/")) return false;
    if (request.method !== "GET" && !session.allowWrite(request)) return json(response, 403, { message: "Nguồn yêu cầu không hợp lệ." });
    if (path === "/api/v1/session") return session.handle(request, response);
    const principal = await session.authenticate(request);
    if (!principal) return json(response, 401, { message: "Cần đăng nhập." });
    const { role } = principal;
    if (path === "/api/v1/inbox" || path.startsWith("/api/v1/inbox/")) {
      if (inbox) return inbox.handle(principal, request, response);
      return path === "/api/v1/inbox" && request.method === "GET" ? json(response, 200, [])
        : json(response, 503, { code: "oa_unavailable", message: "Kênh OA chưa sẵn sàng." });
    }
    const deny = () => json(response, 403, { message: "Vai trò hiện tại không có quyền thao tác." });
    const draftList = /^\/api\/v1\/conversations\/([^/]+)\/drafts$/.exec(path);
    const draftAction = /^\/api\/v1\/drafts\/([^/]+)\/(regenerate|approve)$/.exec(path);
    if (drafts && request.method === "GET" && draftList && uuid(draftList[1])) {
      if (role !== "owner" && role !== "support") return deny();
      return json(response, 200, { drafts: drafts.list(draftList[1]) });
    }
    if (drafts && request.method === "POST" && draftAction && uuid(draftAction[1])) {
      if (role !== "owner" && role !== "support") return deny();
      const input = await readJson(request);
      if (!input || Object.keys(input).length !== 1 || !Number.isSafeInteger(input.version) || Number(input.version) < 1) {
        return json(response, 400, { message: "Phiên bản nháp không hợp lệ." });
      }
      const [, id, action] = draftAction;
      if (!drafts.get(id)) return json(response, 404, { message: "Không tìm thấy bản nháp." });
      const version = Number(input.version);
      const result = action === "approve" ? drafts.approve(id, version, principal.id) : await drafts.regenerate(id, version);
      return result ? json(response, 200, result) : json(response, 409, { message: "Bản nháp đã đổi hoặc chưa sẵn sàng." });
    }
    if (request.method === "GET") {
      if (path === "/api/v1/workspace") return json(response, 200, workspace(role === "owner" || role === "support"));
      if (path === "/api/v1/agent-router" || path === "/api/v1/settings") {
        if (role !== "owner" && role !== "a0") return deny();
        if (path.endsWith("/settings")) return json(response, 200, { adsEnabled: store.setting("ADS_ENABLED") === 1 });
        const { budget } = config;
        const cap = budget.provider === "anthropic-compatible" ? budget.compatibleDailyUsd : budget.stopUsd;
        const used = Number(db.prepare("SELECT coalesce(sum(amount),0) AS total FROM ledger WHERE date=? AND provider=?").get(date(), budget.provider)?.total);
        return json(response, 200, { provider: budget.provider, model: budget.byAgent.router,
          ...room?.ownerView(principal, usdVnd ?? 0),
          budgetVnd: usdVnd ? Math.round(cap * usdVnd) : null, usedVnd: usdVnd ? Math.round(used * usdVnd / 1e9) : null });
      }
    }
    if (request.method === "POST") {
      if (path === "/api/v1/channels/nick/pairing" || path === "/api/v1/channels/nick/revoke") {
        if (role !== "owner") return deny();
        response.setHeader("Cache-Control", "no-store");
        if (path.endsWith("/pairing") && nick?.issue) return json(response, 201, nick.issue());
        if (path.endsWith("/revoke") && nick?.revoke) {
          nick.revoke();
          return json(response, 200, { revoked: true });
        }
        return json(response, 503, { message: "Chưa cấu hình ghép cặp nick phụ." });
      }
      const toggle = /^\/api\/v1\/agent-router\/([^/]+)\/enabled$/.exec(path);
      const review = /^\/api\/v1\/work-items\/([^/]+)\/review$/.exec(path);
      if (room && (toggle || review)) {
        if (role !== "owner") return deny();
        const input = await readJson(request);
        if (input && Object.keys(input).length === 1) {
          if (toggle && typeof input.enabled === "boolean" && room.toggle(principal, toggle[1], input.enabled)) {
            return json(response, 200, { enabled: input.enabled });
          }
          if (review && uuid(review[1]) && (input.decision === "accept" || input.decision === "dismiss")) {
            return room.review(principal, review[1], input.decision)
              ? json(response, 200, { status: "done" })
              : json(response, 409, { message: "Phiếu không còn chờ duyệt." });
          }
        }
        return json(response, 400, { message: "Dữ liệu không hợp lệ." });
      }
      if (path === "/api/v1/operators") {
        if (role !== "owner") return deny();
        const input = await readJson(request);
        if (!input) return json(response, 400, { message: "Dữ liệu tài khoản không hợp lệ." });
        const result = await createOperator(store, principal.id, input);
        return result.status === 201 ? json(response, 201, result.operator) : json(response, result.status, { message: result.message });
      }
      if (path === "/api/v1/quotes/oa-send" || path === "/api/v1/quotes") {
        if (role !== "owner" && role !== "sales") return deny();
        if (path.endsWith("/oa-send")) return quotes ? quotes.handle(request, response) : json(response, 503, { message: "Chưa cấu hình kênh OA." });
        const input = await selection(request);
        const total = input && totals(input);
        if (!input || !total) return json(response, 409, { message: "Khách hoặc bảng giá đã duyệt không hợp lệ." });
        const id = randomUUID();
        record(id, input, total, principal.id, null);
        const { priceList: _priceList, ...display } = input;
        return json(response, 201, { id, ...display, ...total });
      }
      const approval = /^\/api\/v1\/conversations\/([^/]+)\/approve$/.exec(path);
      if (approval && uuid(approval[1])) return role === "owner" || role === "support"
        ? approve(approval[1], request, response) : deny();
      if (["/api/v1/channels/nick/stop", "/api/v1/room-messages", "/api/v1/work-items", "/api/v1/deletion-requests"].includes(path)) {
        if (role !== "owner") return deny();
        if (path.endsWith("/nick/stop")) { store.stop("nick", true); nick?.stop(); return json(response, 200, channels()[1]); }
        const input = await readJson(request);
        const text = clean(input?.text, 1000);
        const title = clean(input?.title, 250);
        const reason = clean(input?.reason, 500);
        if (room && path.endsWith("/room-messages") && text) return json(response, 201, room.post(principal, text));
        if (room && path.endsWith("/work-items") && title && typeof input?.agent === "string") {
          const item = room.assign(principal, title, input.agent);
          return item ? json(response, 201, item) : json(response, 400, { message: "Agent không hợp lệ." });
        }
        if (path.endsWith("/room-messages") && text) {
          const row = db.prepare("INSERT INTO web_room_messages(operator_id,body) VALUES(?,?) RETURNING id").get(principal.id, text);
          return json(response, 201, { id: row?.id, author: principal.label, text });
        }
        if (path.endsWith("/work-items") && title && typeof input?.agent === "string" && agents.includes(input.agent)) {
          const agent = input.agent;
          const id = store.atomic(() => {
            const row = db.prepare("INSERT INTO tasks(created_by,title) VALUES(?,?) RETURNING id").get(principal.id, title)!;
            db.prepare("INSERT INTO web_task_agents VALUES(?,?)").run(String(row.id), agent);
            return row.id;
          });
          return json(response, 201, { id, title, agent, status: "new" });
        }
        if (path.endsWith("/deletion-requests") && reason && uuid(input?.customerId)) {
          const customerId = input.customerId;
          const row = db.prepare(`INSERT INTO web_deletion_requests(customer_id,operator_id,reason)
            SELECT id,?,? FROM customers WHERE id=? RETURNING id`).get(principal.id, reason, customerId);
          if (row) return json(response, 201, { id: row.id, customerId, reason, status: "requested" });
        }
        return json(response, 400, { message: "Dữ liệu không hợp lệ." });
      }
    }
    return json(response, 404, { message: "Không tìm thấy API." });
  };
}
