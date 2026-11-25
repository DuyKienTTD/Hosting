import { chromium, type Page } from "playwright";
import { BaseAdapter, ChannelJournal, fail, id, ok } from "./common.js";
import type { ChannelEvent, Command, Operation, Result, Results } from "./contract.js";

export type UiSelectors = {
  workspace: string; challenge: string; root: string; target: string;
  targetAttribute: string; input: string; member: string; submit: string;
  receipt: string; receiptAttribute: string; memberRows: string;
  acceptanceRows: string; evidenceAttribute: string; timestampAttribute: string;
};
export type UiConfig = {
  accountId: string; workspaceId: string; origin: string; selectors: UiSelectors;
  groups: string[]; contacts: string[]; groupNames: string[];
};
type UiWrite = "createGroup" | "postToGroup" | "sendFriendRequest";
const selectorNames: (keyof UiSelectors)[] = ["workspace", "challenge", "root", "target", "targetAttribute",
  "input", "member", "submit", "receipt", "receiptAttribute", "memberRows", "acceptanceRows", "evidenceAttribute", "timestampAttribute"];

export class SubizUiAdapter extends BaseAdapter {
  private disabled = false;
  private readonly breaker: string;
  private readonly scope: string;
  constructor(readonly config: UiConfig, private page: Page, private journal: ChannelJournal, private screenshotPath?: string) {
    super();
    if (![config.accountId, config.workspaceId].every(id) || !config.selectors ||
      selectorNames.some(key => typeof config.selectors[key] !== "string" || !config.selectors[key].trim()) ||
      !Array.isArray(config.groups) || !config.groups.every(id) || !Array.isArray(config.contacts) || !config.contacts.every(id) ||
      !Array.isArray(config.groupNames) || !config.groupNames.every(x => typeof x === "string" && x.length > 0 && x.length <= 100)) {
      throw Error("INVALID_UI_CONFIG");
    }
    this.scope = "ui:" + config.accountId;
    this.breaker = JSON.stringify([this.scope, config.workspaceId, selectorNames.map(key => config.selectors[key])]);
  }
  static async launch(config: UiConfig, journal: ChannelJournal, url: string, statePath: string, screenshotPath?: string) {
    const origin = new URL(url).origin;
    if (origin !== "https://app.subiz.com.vn" || origin !== config.origin) throw Error("INVALID_UI_ORIGIN");
    const browser = await chromium.launch({ headless: true, chromiumSandbox: true });
    try {
      const page = await browser.newPage({ storageState: statePath });
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 10_000 });
      if (new URL(page.url()).origin !== origin) throw Error("UI_AUTH_REQUIRED");
      return new SubizUiAdapter(config, page, journal, screenshotPath);
    } catch (error) { await browser.close(); throw error; }
  }
  private async disable() {
    this.disabled = true;
    this.journal.pause(this.breaker);
    if (!this.screenshotPath) return;
    // Generate the evidence in a fresh context. No production DOM is captured.
    const clean = await this.page.context().browser()?.newPage();
    if (!clean) return;
    try {
      await clean.setContent("<!doctype html><title>UI paused</title><h1>Subiz UI paused</h1><p>Selector, session, or receipt check failed.</p>");
      await clean.screenshot({ path: this.screenshotPath });
    } finally { await clean.context().close(); }
  }

  private write<K extends UiWrite>(c: Command<K>, target: string, text: string, members: string[],
    map: (receipt: string) => Results[K]): Promise<Result<Results[K]>> {
    if (this.disabled || this.journal.paused(this.breaker)) return Promise.resolve(fail("not_supported"));
    if (c.accountId !== this.config.accountId) return Promise.resolve(fail("policy_denied"));
    const { selectors: s, workspaceId, origin } = this.config;
    return this.journal.write(this.scope, c, async () => {
      let prior: string | null;
      try {
        // No auto-wait or alternate selector. Validate everything before changing the DOM.
        prior = await this.page.evaluate(({ s, workspaceId, origin, operation, target, text, members }) => {
          const one = (scope: ParentNode, css: string) => {
            const items = scope.querySelectorAll<HTMLElement>(css);
            if (items.length !== 1 || !items[0].getClientRects().length) throw Error("UI_DRIFT");
            return items[0];
          };
          if (location.origin !== origin || document.querySelector(s.challenge) ||
            one(document, s.workspace).getAttribute(s.targetAttribute) !== workspaceId) throw Error("UI_SESSION");
          const roots = [...document.querySelectorAll<HTMLElement>(s.root)].filter(el => el.getAttribute(s.targetAttribute) === operation);
          if (roots.length !== 1 || !roots[0].getClientRects().length) throw Error("UI_OPERATION");
          const root = roots[0];
          if (one(root, s.target).getAttribute(s.targetAttribute) !== target) throw Error("UI_TARGET");
          const button = one(root, s.submit);
          const receipt = one(root, s.receipt);
          if (!(button instanceof HTMLButtonElement) || button.disabled) throw Error("UI_SUBMIT");
          const field = text ? one(root, s.input) : undefined;
          if (field && (!(field instanceof HTMLTextAreaElement || field instanceof HTMLInputElement) || field.disabled || field.readOnly)) {
            throw Error("UI_INPUT");
          }
          const memberFields = [...root.querySelectorAll<HTMLInputElement>(s.member)];
          for (const input of memberFields) if (!(input instanceof HTMLInputElement) || input.type !== "checkbox" ||
            input.disabled || !input.getAttribute(s.targetAttribute)) throw Error("UI_MEMBER_SELECTION");
          for (const member of members) if (memberFields.filter(input => input.getAttribute(s.targetAttribute) === member).length !== 1) {
            throw Error("UI_MEMBER_MISSING");
          }
          if (field instanceof HTMLTextAreaElement || field instanceof HTMLInputElement) {
            field.value = text;
            field.dispatchEvent(new window.Event("input", { bubbles: true }));
          }
          for (const input of memberFields) {
            const selected = members.includes(input.getAttribute(s.targetAttribute) ?? "");
            if (input.checked === selected) continue;
            if (!input.isConnected || !root.contains(input)) throw Error("UI_CHANGED");
            input.checked = selected;
            input.dispatchEvent(new window.Event("change", { bubbles: true }));
          }
          if (!button.isConnected || button.disabled || one(root, s.submit) !== button ||
            one(root, s.target).getAttribute(s.targetAttribute) !== target) throw Error("UI_CHANGED");
          const selected = [...root.querySelectorAll<HTMLInputElement>(s.member)].filter(input => input.checked)
            .map(input => input.getAttribute(s.targetAttribute));
          if (selected.length !== members.length || !members.every(member => selected.includes(member))) throw Error("UI_CHANGED");
          const before = receipt.getAttribute(s.receiptAttribute);
          button.click();
          return before;
        }, { s, workspaceId, origin, operation: c.operation, target, text, members });
        const value = await this.page.waitForFunction(({ s, origin, prior, workspaceId, target, operation }) => {
          if (location.origin !== origin || document.querySelector(s.challenge) ||
            document.querySelector(s.workspace)?.getAttribute(s.targetAttribute) !== workspaceId) return false;
          const roots = [...document.querySelectorAll(s.root)].filter(el => el.getAttribute(s.targetAttribute) === operation);
          const root = roots.length === 1 ? roots[0] : undefined;
          if (root?.getAttribute(s.targetAttribute) !== operation ||
            root.querySelector(s.target)?.getAttribute(s.targetAttribute) !== target) return false;
          const items = root.querySelectorAll(s.receipt);
          const value = items.length === 1 && items[0].getAttribute(s.receiptAttribute);
          return value && value !== prior ? value : false;
        }, { s, origin, prior, workspaceId, target, operation: c.operation }, { timeout: 4000 });
        const receipt = await value.jsonValue();
        await value.dispose();
        if (!id(receipt)) throw Error("UI_RECEIPT");
        return ok(map(receipt));
      } catch {
        await this.disable().catch(() => {});
        // A disconnect or selector error after the click cannot prove non-delivery.
        return fail("unknown_delivery");
      }
    });
  }
  override createGroup(c: Command<"createGroup">) {
    if (!this.config.groupNames.includes(c.payload.name) || !Array.isArray(c.payload.memberIds) || !c.payload.memberIds.length ||
      new Set(c.payload.memberIds).size !== c.payload.memberIds.length || c.payload.memberIds.some(i => !this.config.contacts.includes(i))) {
      return Promise.resolve(fail("policy_denied"));
    }
    return this.write(c, "new", c.payload.name, c.payload.memberIds, groupId => ({ groupId, name: c.payload.name }));
  }
  override postToGroup(c: Command<"postToGroup">) {
    if (!this.config.groups.includes(c.payload.groupId)) return Promise.resolve(fail("policy_denied"));
    if (!c.payload.text?.trim() || c.payload.text.length > 2000) return Promise.resolve(fail("invalid_input"));
    return this.write(c, c.payload.groupId, c.payload.text, [], providerMessageId => ({ providerMessageId, state: "accepted" }));
  }
  override sendFriendRequest(c: Command<"sendFriendRequest">) {
    if (!this.config.contacts.includes(c.payload.contactId)) return Promise.resolve(fail("policy_denied"));
    return this.write(c, c.payload.contactId, "", [], () => ({ status: "requested" }));
  }

  private async rows(accountId: string, selector: string, target: string, operation: string) {
    if (this.disabled || this.journal.paused(this.breaker)) return fail("not_supported");
    if (accountId !== this.config.accountId) return fail("policy_denied");
    const { selectors: s, workspaceId, origin } = this.config;
    try {
      return ok(await this.page.evaluate(({ s, workspaceId, origin, selector, target, operation }) => {
        const spaces = document.querySelectorAll(s.workspace);
        if (location.origin !== origin || document.querySelector(s.challenge) || spaces.length !== 1 ||
          spaces[0].getAttribute(s.targetAttribute) !== workspaceId) throw Error("UI_SESSION");
        const roots = [...document.querySelectorAll(s.root)].filter(el => el.getAttribute(s.targetAttribute) === operation);
        if (roots.length !== 1) throw Error("UI_OPERATION");
        const scope = roots[0];
        if (target && scope.querySelector(s.target)?.getAttribute(s.targetAttribute) !== target) throw Error("UI_TARGET");
        return [...scope.querySelectorAll(selector)].slice(0, 500).map(row => ({
          contact: row.getAttribute(s.targetAttribute), evidence: row.getAttribute(s.evidenceAttribute),
          at: Number(row.getAttribute(s.timestampAttribute)),
        }));
      }, { s, workspaceId, origin, selector, target, operation }));
    } catch { await this.disable().catch(() => {}); return fail("not_supported"); }
  }
  async listMembers(accountId: string, groupId: string) {
    if (!this.config.groups.includes(groupId)) return fail("policy_denied");
    const rows = await this.rows(accountId, this.config.selectors.memberRows, groupId, "listMembers");
    return rows.ok ? ok(rows.value.map(r => r.contact).filter(id)) : rows;
  }
  override async onFriendAccepted(c: Command<"onFriendAccepted">) {
    const read = await this.rows(c.accountId, this.config.selectors.acceptanceRows, "", "onFriendAccepted");
    if (!read.ok) return read;
    const events: ChannelEvent<"friendAccepted">[] = [];
    for (const row of read.value) {
      if (!id(row.contact) || !this.config.contacts.includes(row.contact) || !id(row.evidence) ||
        !Number.isSafeInteger(row.at) || row.at <= 0 || row.at > 8.64e15) continue;
      events.push({ version: 1, accountId: c.accountId, eventId: row.evidence, occurredAt: new Date(row.at).toISOString(),
        type: "friendAccepted", payload: { contactId: row.contact, evidenceId: row.evidence } });
    }
    this.journal.append(this.scope, events.map(event => ({ stream: "accepted", event })));
    const page = this.journal.page(this.scope, "accepted", c.payload);
    return page.ok ? ok({ ...page.value, items: page.value.items.filter((e): e is ChannelEvent<"friendAccepted"> => e.type === "friendAccepted") }) : page;
  }
}
