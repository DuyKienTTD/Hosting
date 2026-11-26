import type { Store } from "../store.js";
import type { Envelope } from "../channels/oa/crypto.js";
import { accountScope, inboxContext, oaUid, type OaAccount } from "../channels/oa/webhook.js";
import { classifyOptOut } from "../opt-out.js";
import type { Config } from "../config.js";

export type InboxSource = { account: OaAccount; envelope: Envelope };
type SealedEvent = { event_id: unknown; target: unknown; sealed: unknown };
type Message = { id: string; contact: string; at: number; text: string };

export function inboxProjector(store: Store, { account, envelope }: InboxSource, config: Config) {
  const scope = accountScope(account);
  const db = store.db;

  function decode(item: SealedEvent): Message | undefined {
    if (typeof item.sealed !== "string") return;
    try {
      const data = JSON.parse(envelope.open(Buffer.from(item.sealed, "base64"), inboxContext(scope, String(item.event_id))));
      if (data?.kind !== "dm" || data.channel !== "oa" || data.thread !== data.contact || data.id !== item.event_id ||
          typeof data.contact !== "string" || !oaUid(account, data.contact) || store.hash(data.contact) !== item.target ||
          !Number.isSafeInteger(data.at) || data.at <= 0 || data.at > Date.now() || typeof data.text !== "string") return;
      return { id: data.id, contact: data.contact, at: data.at, text: data.text };
    } catch { return; }
  }

  function project() {
    const batch = db.prepare(`SELECT i.event_id,i.target,encode(i.sealed,'base64') AS sealed
      FROM oa_inbox i WHERE i.scope=? AND i.sealed IS NOT NULL AND i.expires_at>clock_timestamp()
        AND NOT EXISTS(SELECT 1 FROM web_oa_projection p WHERE p.scope=i.scope AND p.event_id=i.event_id)
      ORDER BY i.seq LIMIT 20`).all(scope);
    for (const row of batch) {
      const eventId = String(row.event_id);
      const target = String(row.target);
      const message = decode({ event_id: row.event_id, target: row.target, sealed: row.sealed });
      store.atomic(() => {
        const available = db.prepare(`SELECT 1 FROM oa_inbox i JOIN oa_contacts c USING(scope,target)
          WHERE i.scope=? AND i.event_id=? AND i.sealed IS NOT NULL AND i.expires_at>clock_timestamp()
          AND NOT c.withdrawn AND NOT EXISTS(SELECT 1 FROM web_oa_projection p WHERE p.scope=i.scope AND p.event_id=i.event_id)`)
          .get(scope, eventId);
        if (!available) return;

        const mark = (conversation: string | null, origin: string | null, received: number, retained: boolean) =>
          db.prepare("INSERT INTO web_oa_projection VALUES(?,?,?,?,?,?,?::boolean)")
            .run(scope, eventId, conversation, target, origin, received, String(retained));
        if (!message) { mark(null, null, 0, false); return; }
        const uid = oaUid(account, message.contact)!;
        const known = db.prepare("SELECT customer_id FROM channel_identities WHERE channel='oa' AND account_id=? AND uid=?")
          .get(account.oaId, uid);
        const mapped = db.prepare("SELECT customer_id FROM runtime_customer WHERE target=?").get(target);
        if (known && mapped && known.customer_id !== mapped.customer_id) { mark(null, null, 0, false); return; }
        if (known && !mapped && db.prepare("SELECT 1 FROM runtime_customer WHERE customer_id=?").get(String(known.customer_id))) {
          mark(null, null, 0, false);
          return;
        }
        const customer = String(mapped?.customer_id ?? known?.customer_id ?? db.prepare("INSERT INTO customers DEFAULT VALUES RETURNING id").get()!.id);
        db.prepare("INSERT INTO contact(target) VALUES(?) ON CONFLICT(target) DO NOTHING").run(target);
        if (!mapped) db.prepare("INSERT INTO runtime_customer(target,customer_id) VALUES(?,?)").run(target, customer);
        if (!known) db.prepare("INSERT INTO channel_identities(channel,account_id,uid,customer_id) VALUES('oa',?,?,?)")
          .run(account.oaId, uid, customer);
        const thread = db.prepare(`INSERT INTO conversations(customer_id,channel,runtime_thread) VALUES(?,'oa',?)
          ON CONFLICT(customer_id,channel,runtime_thread) DO UPDATE SET runtime_thread=excluded.runtime_thread RETURNING id`).get(customer, target)!;
        const origin = store.eventKey(message.contact, message.contact, message.id);
        const optOut = classifyOptOut(message.text, config.advertising);
        if (optOut === "stop" && !store.contact(target)?.opted_out) store.optOut(target);
        if (optOut === "review" && !store.contact(target)?.ads_paused_review) store.pauseAdsForReview(target, origin);
        const existing = db.prepare("SELECT 1 FROM messages WHERE conversation_id=? AND event_id=?").get(String(thread.id), origin);
        const erased = db.prepare("SELECT 1 FROM restore_tombstones WHERE conversation_id=? AND event_id=?").get(String(thread.id), origin);
        const retained = !!existing || !!erased || store.contact(target)?.retain === 1;
        if (retained && !existing && !erased) {
          store.retainMessage(target, message.contact, "oa", origin, message.text, message.at);
        }
        // Ingress already advanced interaction_at under the same policy lock.
        mark(String(thread.id), origin, message.at, retained);
      });
    }
  }
  return { scope, project, decode };
}
