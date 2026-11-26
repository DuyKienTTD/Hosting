import type { Event } from "../../channel.js";
import { day, type Config } from "../../config.js";
import { Guard, type Proposal } from "../../guard.js";
import { classifyOptOut } from "../../opt-out.js";
import type { Store } from "../../store.js";
import type { OaRuntimeChannel } from "./adapter.js";
import { accountScope, consultationWindow, oaUid, type OaAccount } from "./webhook.js";

export function consentAnswer(text: string) {
  const answer = text.normalize("NFC").trim().toLocaleLowerCase("vi");
  if (answer === "đồng ý") return "grant";
  if (["không đồng ý", "stop", "hủy", "huỷ"].includes(answer)) return "withdraw";
}

export function readOaConsent(env: NodeJS.ProcessEnv, retentionDays: number) {
  const enabled = env.OA_CONSENT_PROMPT_ENABLED ?? "0";
  if (enabled !== "0" && enabled !== "1") throw Error("INVALID_OA_CONSENT_PROMPT_ENABLED");
  const url = env.OA_CONSENT_POLICY_URL;
  const version = env.OA_CONSENT_POLICY_VERSION;
  if (!url && !version && enabled === "0") return;
  if (!url || url.length > 300 || !version || !/^[\w.-]{1,64}$/.test(version)) throw Error("OA_CONSENT_POLICY_REQUIRED");
  const policy = new URL(url);
  if (policy.protocol !== "https:" || policy.username || policy.password) throw Error("INVALID_OA_CONSENT_POLICY_URL");
  const text = `Thuận Thành Đạt xin phép lưu nội dung trao đổi và mã tài khoản OA để hỗ trợ yêu cầu của bạn, dùng AI soạn nháp cho nhân viên xem xét và gửi phản hồi tư vấn qua Zalo. Tin nhắn được lưu tối đa ${retentionDays} ngày. Đồng ý có hiệu lực ${retentionDays} ngày và không bao gồm quảng cáo.

Bạn có thể từ chối hoặc rút lại bất cứ lúc nào. Chính sách và thông tin thực hiện quyền của bạn: ${policy.href}

Vui lòng trả lời đúng “Đồng ý” hoặc “Không đồng ý”. Để rút lại sau khi đồng ý, nhắn “Hủy”.`;
  return { enabled: enabled === "1", text, version, retentionDays };
}

export class OaConsent {
  private readonly scope: string;
  private readonly guard: Guard;
  constructor(private readonly store: Store, private readonly account: OaAccount, channel: OaRuntimeChannel,
    private readonly config: Config, private readonly policy: ReturnType<typeof readOaConsent>, private readonly clock = Date.now) {
    this.scope = accountScope(account);
    this.guard = new Guard(store, channel, config, clock, undefined, {
      allows: (proposal, target, now) => this.allowsPrompt(proposal, target, now),
      reserve: (target, key, now) => this.reservePrompt(target, key, now),
    });
  }

  private receipt(target: string, id: string) {
    return this.store.db.prepare(`SELECT i.seq FROM oa_inbox i JOIN oa_contacts c USING(scope,target)
      WHERE i.scope=? AND i.event_id=? AND i.target=? AND i.sealed IS NOT NULL
      AND i.expires_at>clock_timestamp() AND NOT c.withdrawn`).get(this.scope, id, target);
  }

  private allowsPrompt(proposal: Proposal, target: string, now: number) {
    if (!this.policy?.enabled || proposal.text !== this.policy.text || proposal.thread !== proposal.target ||
      !oaUid(this.account, proposal.target) || this.store.db.prepare(
        "SELECT event_id FROM oa_inbox WHERE scope=? AND target=? AND sealed IS NOT NULL ORDER BY seq DESC LIMIT 1"
      ).get(this.scope, target)?.event_id !== proposal.origin ||
      !this.receipt(target, proposal.origin ?? "")) return false;
    const policy = this.store.policy(target, "support", now);
    if (policy.takeover || policy.retain || policy.respond || policy.send) return false;
    return !this.store.db.prepare("SELECT 1 FROM oa_consent_prompts WHERE scope=? AND target=? AND at>?")
      .get(this.scope, target, now - consultationWindow);
  }

  private reservePrompt(target: string, key: string, now: number) {
    const { text, version } = this.policy!;
    this.store.db.prepare(`INSERT INTO oa_consent_prompts VALUES(?,?,?,?,?,?)
      ON CONFLICT(scope,target) DO UPDATE SET send_id=excluded.send_id,at=excluded.at,
      displayed_text=excluded.displayed_text,policy_version=excluded.policy_version`)
      .run(this.scope, target, key, now, text, version);
  }

  get attestationText() { return this.policy?.text; }

  attest(rawTarget: string, operator: string, version: string, recordingRef: string) {
    const now = this.clock();
    const policy = this.policy;
    if (!policy || policy.version !== version || !oaUid(this.account, rawTarget)) return false;
    const target = this.store.hash(rawTarget);
    return this.store.atomic(() => {
      const contact = this.store.db.prepare("SELECT withdrawn FROM oa_contacts WHERE scope=? AND target=?").get(this.scope, target);
      if (!contact || contact.withdrawn || this.store.contact(target)?.opted_out) return false;
      this.store.consent(target, now + policy.retentionDays * day, true, true, true, false, {
        displayedText: policy.text, policyVersion: policy.version, evidence: { source: "operator_attested", operator, recordingRef },
      });
      return true;
    });
  }

  get policyVersion() { return this.policy?.version; }

  async handle(event: Event) {
    if (event.kind !== "dm" || event.channel !== "oa" || event.thread !== event.contact ||
      !oaUid(this.account, event.contact)) return false;
    const target = this.store.hash(event.contact);
    const now = this.clock();
    if (!Number.isSafeInteger(event.at) || event.at > now) return false;
    const optOut = classifyOptOut(event.text, this.config.advertising);
    const answer = consentAnswer(event.text) ?? (optOut === "stop" ? "withdraw" : undefined);
    if (!answer) {
      if (this.policy?.enabled && optOut === "none") await this.guard.dispatch({
        agent: "support", kind: "reply", purpose: "oa_consent_prompt", revision: this.store.policy(target, "support", now).revision,
        epoch: this.store.setting("epoch"), id: JSON.stringify(["oa-consent-prompt", this.scope, target, event.id]),
        origin: event.id, target: event.contact, thread: event.thread, text: this.policy.text,
      });
      return false;
    }
    this.store.atomic(() => {
      if (!this.receipt(target, event.id)) return;
      const db = this.store.db;
      const recorded = db.prepare("INSERT INTO oa_consent_decisions(scope,receipt) VALUES(?,?) ON CONFLICT DO NOTHING RETURNING receipt")
        .get(this.scope, this.store.hash(JSON.stringify([target, event.id])));
      if (!recorded) return;
      const prompt = db.prepare(`SELECT p.displayed_text,p.policy_version FROM oa_consent_prompts p
        JOIN send_log s ON s.id=p.send_id WHERE p.scope=? AND p.target=? AND s.state='sent' AND p.at<=? AND p.at>?`)
        .get(this.scope, target, event.at, event.at - consultationWindow);
      const evidence = { source: "signed_oa_event", scope: this.scope, receipt: event.id, occurredAt: event.at, decision: answer };
      if (answer === "withdraw") {
        this.store.consent(target, now, false, false, false, false, {
          displayedText: String(prompt?.displayed_text ?? "Rút lại đồng ý qua OA"),
          policyVersion: String(prompt?.policy_version ?? this.policy?.version ?? "oa-withdrawal-v1"), evidence,
        });
        this.store.optOut(target);
        db.prepare("DELETE FROM jobs WHERE target=?").run(target);
      } else if (prompt && this.policy?.version === prompt.policy_version &&
        this.policy.text === prompt.displayed_text && !this.store.contact(target)?.opted_out) {
        this.store.consent(target, now + this.policy.retentionDays * day, true, true, true, false, {
          displayedText: this.policy.text, policyVersion: this.policy.version, evidence,
        });
      }
    });
    return true;
  }
}
