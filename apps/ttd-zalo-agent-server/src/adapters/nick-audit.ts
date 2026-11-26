import { timingSafeEqual } from "node:crypto";
import type { Server } from "node:http";
import { WebSocketServer, WebSocket } from "ws";
import type { RuntimeDatabase } from "../sql.js";

const code = "committed_before_revoke";
const identifier = /^[A-Za-z0-9_-]{1,100}$/;

export function attachNickAudit(server: Server, db: RuntimeDatabase, credential: string | ((value: string) => boolean), stopped?: () => boolean) {
  if (typeof credential === "string" && Buffer.byteLength(credential) < 32) throw Error("INVALID_NICK_WORKER_AUTH");
  const expected = typeof credential === "string" ? Buffer.from("Bearer " + credential) : undefined;
  const sockets = new WebSocketServer({ noServer: true, maxPayload: 64 * 1024 });
  // One statement atomically persists the send state and the owner notice.
  const audit = db.prepare(`WITH changed AS (
    UPDATE send_log SET state='committed_before_revoke'
    WHERE id=? AND agent='nick-worker' AND kind='reply'
      AND state IN ('reserved','sent','unknown_delivery','committed_before_revoke')
    RETURNING id
  ), alert AS (
    INSERT INTO notices(key,at,body) SELECT ?,?,? FROM changed
    ON CONFLICT (key) DO NOTHING
  ) SELECT id FROM changed`);
  let active: WebSocket | undefined;
  const stop = () => { if (active?.readyState === WebSocket.OPEN) active.send(JSON.stringify({ type: "stop" })); };
  server.on("upgrade", (req, socket, head) => {
    const header = req.headers.authorization ?? "";
    const received = Buffer.from(header);
    let allowed = false;
    try {
      if (req.url === "/nick-worker/socket" && typeof credential === "function" && header.startsWith("Bearer ")) {
        allowed = credential(header.slice(7));
      } else if (req.url === "/internal/nick-worker" && expected && received.length === expected.length) {
        allowed = timingSafeEqual(received, expected);
      }
    } catch { /* reject if the credential store is unavailable */ }
    if (!allowed) {
      socket.end("HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\n");
      return;
    }
    sockets.handleUpgrade(req, socket, head, worker => {
      active?.terminate();
      active = worker;
      if (stopped?.()) stop();
      worker.on("error", () => worker.terminate());
      worker.on("message", (raw, binary) => {
        if (active !== worker || binary) return;
        try {
          if (typeof credential === "function" && !credential(header.slice(7))) {
            worker.terminate();
            return;
          }
          const msg = JSON.parse(raw.toString());
          if (msg?.type === "heartbeat") {
            worker.send(JSON.stringify({ type: "pong" }));
            return;
          }
          if (msg?.type !== "audit_alert" || typeof msg.id !== "string" || !identifier.test(msg.id) ||
            msg.code !== code || msg.audience !== "owner" || msg.idempotencyKey !== `nick:${code}:${msg.id}`) return;
          const matched = audit.get(msg.id, msg.idempotencyKey, Date.now(),
            `Nick Zalo: lượt gửi ${msg.id} đã cam kết trước khi thu hồi. Không gửi lại.`);
          if (matched) worker.send(JSON.stringify({ type: "audit_ack", id: msg.id, idempotencyKey: msg.idempotencyKey }));
        } catch {
          // The worker retains the event and retries when no durable ACK is received.
        }
      });
    });
  });
  return Object.assign(() => {
    active?.terminate();
    sockets.close();
  }, { stop, disconnect: () => active?.terminate(), connected: () => active?.readyState === WebSocket.OPEN });
}
