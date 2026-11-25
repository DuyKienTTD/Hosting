import type { IncomingMessage, ServerResponse } from "node:http";
import { readFileSync } from "node:fs";
import { ChannelJournal } from "./common.js";
import { SubizAdapter, type SubizConfig } from "./subiz.js";
import { ZaloBotAdapter, type BotConfig } from "./bot.js";
import { SubizUiAdapter, type UiConfig } from "./ui.js";
import { CapabilityRouter, RuntimeChannel, runtimeEvent, type Capability } from "./router.js";
import type { Event } from "../channel.js";
import type { Store } from "../store.js";

export type Routes = { subiz: SubizConfig; bot?: BotConfig; ui?: UiConfig; capabilities: Capability };
export function readRoutes(): Routes {
  const path = process.env.CHANNEL_ROUTES_PATH;
  if (!path) throw Error("CHANNEL_ROUTES_REQUIRED");
  const routes: Routes = JSON.parse(readFileSync(path, "utf8"));
  if (!routes?.subiz || !routes.capabilities || (routes.ui && routes.ui.accountId !== routes.subiz.accountId) ||
    (routes.bot && routes.bot.accountId !== routes.subiz.accountId)) throw Error("INVALID_CHANNEL_ROUTES");
  return routes;
}
export async function setupChannels(store: Store, routes: Routes, smokeOnly = false) {
  if (!process.env.SUBIZ_API_TOKEN || !process.env.SUBIZ_WEBHOOK_SECRET) throw Error("SUBIZ_ENV_REQUIRED");
  const journal = new ChannelJournal(store);
  const subiz = new SubizAdapter(routes.subiz, journal);
  const api = { adapter: subiz, operations: ["receiveMessage", "sendMessage", "getContact"] as const };
  let bot: ZaloBotAdapter | undefined;
  let ui: SubizUiAdapter | undefined;
  if (!smokeOnly && Object.values(routes.capabilities).includes("bot")) {
    if (!routes.bot || !process.env.ZALO_BOT_WEBHOOK_SECRET) throw Error("BOT_CONFIG_REQUIRED");
    bot = new ZaloBotAdapter(routes.bot, journal);
    if (!(await bot.authenticate()).ok) throw Error("BOT_GROUP_ENTITLEMENT_REQUIRED");
  }
  if (!smokeOnly && Object.values(routes.capabilities).includes("ui")) {
    const { SUBIZ_UI_URL, SUBIZ_UI_STATE_PATH, SUBIZ_UI_DIAGNOSTIC_PATH } = process.env;
    if (!routes.ui || !SUBIZ_UI_URL || !SUBIZ_UI_STATE_PATH) throw Error("UI_CONFIG_REQUIRED");
    ui = await SubizUiAdapter.launch(routes.ui, journal, SUBIZ_UI_URL, SUBIZ_UI_STATE_PATH, SUBIZ_UI_DIAGNOSTIC_PATH);
  }
  const router = new CapabilityRouter(smokeOnly ? { receiveMessage: "api", sendMessage: "api", getContact: "api" } : routes.capabilities, {
    api, bot: bot && { adapter: bot, operations: ["readGroupMessages", "postToGroup"] },
    ui: ui && { adapter: ui, operations: ["createGroup", "postToGroup", "sendFriendRequest", "onFriendAccepted"] },
  });
  const groups = router.capabilities.readGroupMessages === "bot" ? routes.bot?.groups ?? [] : [];
  return { subiz, bot, ui, channel: new RuntimeChannel(router, routes.subiz.accountId,
    new Map(routes.subiz.direct.map(r => [r.contactId, r.conversationId])), groups), journal };
}

export function webhookHandler(subiz: SubizAdapter, bot?: ZaloBotAdapter, consume?: (event: Event) => void) {
  return async (req: IncomingMessage, res: ServerResponse) => {
    const endpoint = req.url === "/webhooks/subiz" ? "subiz" : req.url === "/webhooks/zalo-bot" && bot ? "bot" : undefined;
    if (!endpoint) return false;
    if (req.method !== "POST" || req.headers["content-type"]?.split(";")[0]?.trim() !== "application/json") {
      res.writeHead(415).end(); return true;
    }
    const parts: Buffer[] = [];
    let size = 0;
    for await (const part of req) {
      const bytes = Buffer.isBuffer(part) ? part : Buffer.from(part);
      size += bytes.length;
      if (size > 256 * 1024) { res.writeHead(413).end(); return true; }
      parts.push(bytes);
    }
    const raw = Buffer.concat(parts);
    const signature = req.headers[endpoint === "subiz" ? "x-hub-signature-256" : "x-bot-api-secret-token"];
    const header = typeof signature === "string" ? signature : undefined;
    const status = endpoint === "subiz" ? await subiz.webhook(raw, header, consume && (event => consume(runtimeEvent(event)))) : bot!.webhook(raw, header);
    res.writeHead(status).end();
    return true;
  };
}
