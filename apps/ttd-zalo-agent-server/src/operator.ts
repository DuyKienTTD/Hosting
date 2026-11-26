import { createHash, randomUUID, timingSafeEqual } from "node:crypto";
import type { IncomingMessage, ServerResponse } from "node:http";
import { agents } from "./config.js";
import type { Store } from "./store.js";

const digest = (value: string) => createHash("sha256").update(value).digest();
const html = (value: unknown) => String(value).replace(/[&<>"']/gu, char =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]!);

export function operator(store: Store, password: string | undefined) {
  const authorization = digest("Basic " + Buffer.from("owner:" + password).toString("base64"));
  const csrf = randomUUID();
  return async (req: IncomingMessage, res: ServerResponse) => {
    res.setHeader("Cache-Control", "no-store");
    res.setHeader("Content-Security-Policy", "default-src 'none'; form-action 'self'; frame-ancestors 'none'");
    res.setHeader("X-Content-Type-Options", "nosniff");
    if (!password || !["/operator", "/operator/stop", "/operator/ads-review"].includes(req.url ?? "")) { res.writeHead(404).end(); return; }
    if (!timingSafeEqual(authorization, digest(req.headers.authorization ?? ""))) {
      res.writeHead(401, { "WWW-Authenticate": 'Basic realm="TTD METAL"' }).end();
      return;
    }
    const scopes: readonly string[] = ["global", ...agents];
    if (req.method === "POST" && req.url !== "/operator") {
      if (req.headers["content-type"]?.split(";")[0].trim() !== "application/x-www-form-urlencoded") { res.writeHead(415).end(); return; }
      let body = "";
      for await (const chunk of req) {
        body += String(chunk);
        if (body.length > 1024) { res.writeHead(413).end(); return; }
      }
      const fields = new URLSearchParams(body);
      if (fields.get("csrf") !== csrf) { res.writeHead(403).end(); return; }
      if (req.url === "/operator/stop") {
        const scope = fields.get("scope") ?? "";
        if (!scopes.includes(scope)) { res.writeHead(403).end(); return; }
        store.stop(scope, true);
      } else {
        const action = fields.get("action");
        const target = fields.get("target") ?? "";
        const event = fields.get("event") ?? "";
        if ((action !== "active" && action !== "opted_out") ||
          !/^[a-f0-9]{64}$/u.test(target) || !/^[a-f0-9]{64}$/u.test(event)) { res.writeHead(400).end(); return; }
        if (!store.resolveAdsReview(target, event, action)) { res.writeHead(409).end(); return; }
      }
      res.writeHead(303, { Location: "/operator" }).end();
      return;
    }
    if (req.method !== "GET" || req.url !== "/operator") { res.writeHead(405).end(); return; }
    const buttons = scopes.map(scope => `<form action="/operator/stop" method="post">
      <input type="hidden" name="csrf" value="${csrf}">
      <button name="scope" value="${scope}">DỪNG ${scope === "global" ? "toàn hệ thống" : scope}</button>
      <span>${store.setting(scope) ? "Đang dừng" : "Đã bật"}</span></form>`).join("");
    const reviews = store.db.prepare(`SELECT target,ads_paused_review FROM contact
      WHERE ads_paused_review IS NOT NULL AND opted_out=0 LIMIT 50`).all().map(row =>
      `<li><form action="/operator/ads-review" method="post">
      <input type="hidden" name="csrf" value="${csrf}">
      <input type="hidden" name="target" value="${html(row.target)}">
      <input type="hidden" name="event" value="${html(row.ads_paused_review)}">
      <code>${html(row.ads_paused_review)}</code>
      <button name="action" value="active">Xác nhận bỏ tạm dừng</button>
      <button name="action" value="opted_out">Xác nhận ngừng quảng cáo</button></form></li>`).join("");
    const notices = store.db.prepare("SELECT at,body FROM notices ORDER BY at DESC LIMIT 30").all()
      .map(row => `<li><time>${new Date(Number(row.at)).toISOString()}</time> ${html(row.body)}</li>`).join("");
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }).end(`<!doctype html>
      <html lang="vi"><meta charset="utf-8"><title>TTD METAL</title><h1>TTD METAL</h1>
      <h2>Dừng hoạt động</h2>${buttons}<h2>Quảng cáo tạm dừng chờ xem</h2><ul>${reviews}</ul><h2>Báo cáo và cảnh báo</h2><ul>${notices}</ul></html>`);
  };
}
