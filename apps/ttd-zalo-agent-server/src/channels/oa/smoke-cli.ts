import { randomUUID } from "node:crypto";
import { id } from "../../adapters/common.js";
import type { Result, Results } from "../../adapters/contract.js";
import type { Config } from "../../config.js";
import { Guard } from "../../guard.js";
import { classifyOptOut } from "../../opt-out.js";
import type { Store } from "../../store.js";
import type { OaRuntimeChannel } from "./adapter.js";
import { consultationWindow, oaTarget, oaUid, type OaAccount } from "./webhook.js";

type Modes = { oaMode: string; smokeOnly: boolean; smokeAllowlist?: ReadonlySet<string> };
type Oa = { channel: OaRuntimeChannel; account: OaAccount };

export function modeError(modes: Modes, uid?: string) {
  if (modes.oaMode !== "live") return "oa_live_required";
  if (!modes.smokeOnly) return "oa_smoke_only_required";
  if (!modes.smokeAllowlist?.size || (uid !== undefined && (!id(uid) || !modes.smokeAllowlist.has(uid)))) return "oa_uid_not_allowlisted";
}

export function latestSmokeUid(oa: Oa) {
  const event = oa.channel.latestInbound();
  return event && oaUid(oa.account, event.contact);
}

export async function sendOaSmoke(store: Store, config: Config, oa: Oa, modes: Modes,
  uid: string, text: string, approve: boolean, result: () => Result<Results["sendMessage"]> | undefined, clock = Date.now) {
  const mode = modeError(modes, uid);
  if (mode) return { ok: false, error: mode };
  if (!text.trim() || Buffer.byteLength(text) > 8000 || [...text].length > 2000) return { ok: false, error: "invalid_text" };

  const target = oaTarget(oa.account, uid);
  const hashed = store.hash(target);
  const proposalId = "oa-smoke:" + randomUUID();
  const admission = store.atomic(() => {
    const now = clock();
    if (store.stopped("support")) return "stopped";
    const event = oa.channel.latestInbound(target);
    const contact = store.contact(hashed, now);
    if (contact?.opted_out || contact?.ads_paused_review ||
        (event && classifyOptOut(event.text, config.advertising) !== "none")) return "consent";
    const signed = event && Number.isSafeInteger(event.at) && event.at <= now && now - event.at < consultationWindow;
    const prior = !signed && store.db.prepare("SELECT id FROM inbound WHERE target=? AND received>? AND received<=? ORDER BY received DESC LIMIT 1")
      .get(hashed, now - consultationWindow, now);
    const origin = signed ? store.eventKey(event.contact, event.thread, event.id) : prior && String(prior.id);
    if (!origin) return "oa_interaction_missing";
    if (!contact && approve && signed) {
      const label = "smoke_test_owner_approved";
      // The immutable consent history is the audit record. Grant only reply
      // and send for this fixture, until the signed interaction window ends.
      store.consent(hashed, event.at + consultationWindow, false, true, true, false, {
        displayedText: label, policyVersion: label,
        evidence: { source: label, actor: "operator_cli", inbound: origin, proposal: proposalId },
      });
    }
    const policy = store.policy(hashed, "support", now);
    if (!policy.respond || !policy.send) return "consent";
    // Reuse the genuine signed event as Guard evidence. A prior zeroed
    // inbound marker stays zero, including after customer deletion.
    if (signed) store.db.prepare("INSERT OR IGNORE INTO inbound VALUES(?,?,?)").run(origin, hashed, event.at);
    return { origin, revision: policy.revision, epoch: store.setting("epoch") };
  });
  if (typeof admission === "string") return { ok: false, error: admission };
  const outcome = await new Guard(store, oa.channel, config, clock).dispatch({
    ...admission, id: proposalId, kind: "reply", agent: "support", purpose: "oa_smoke",
    target, thread: target, text,
  });
  const receipt = result();
  if (outcome === "sent" && receipt?.ok) return { ok: true, message_id: receipt.value.providerMessageId };
  return { ok: false, error: outcome === "unknown" ? "unknown_delivery" : outcome === "sent" ? "receipt_unavailable" : outcome,
    ...(receipt && !receipt.ok ? { channel_error: receipt.error.code,
      ...(receipt.error.providerCode === undefined ? {} : { zalo_error: receipt.error.providerCode }) } : {}) };
}
