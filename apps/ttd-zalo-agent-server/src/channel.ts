export type ChannelError = "rate_limited" | "auth" | "not_supported" | "unknown_delivery";
export type Result<T = void> = { ok: true; value: T } | { ok: false; error: ChannelError };
export type Request = { key: string; target: string; text?: string; message?: string };
export type Contact = { id: string; friend: boolean };
export type Event = { id: string; contact: string; thread: string; at: number } & (
  { kind: "dm" | "group"; text: string } | { kind: "accepted" | "spam" });
export interface ChannelAdapter {
  receiveMessage(req: Request): Promise<Result<Event[]>>;
  sendMessage(req: Request): Promise<Result>;
  listGroups(req: Request): Promise<Result<string[]>>;
  readGroupMessages(req: Request): Promise<Result<Event[]>>;
  postToGroup(req: Request): Promise<Result>;
  createGroup(req: Request): Promise<Result>;
  moderateGroup(req: Request): Promise<Result>;
  sendFriendRequest(req: Request): Promise<Result>;
  onFriendAccepted(req: Request): Promise<Result<Event[]>>;
  getContact(req: Request): Promise<Result<Contact>>;
}
const unsupported = async <T>(): Promise<Result<T>> => ({ ok: false, error: "not_supported" });

export class SubizAdapter implements ChannelAdapter {
  receiveMessage = unsupported<Event[]>;
  sendMessage = unsupported<void>;
  listGroups = unsupported<string[]>;
  readGroupMessages = unsupported<Event[]>;
  postToGroup = unsupported<void>;
  createGroup = unsupported<void>;
  moderateGroup = unsupported<void>;
  sendFriendRequest = unsupported<void>;
  onFriendAccepted = unsupported<Event[]>;
  getContact = unsupported<Contact>;
}

export class MockChannel implements ChannelAdapter {
  readonly events: Event[] = [];
  readonly contacts = new Map<string, Contact>();
  readonly groups = new Set<string>();
  readonly sent = new Map<string, { operation: string; request: Request }>();
  fail: ChannelError | undefined;
  async receiveMessage(_req: Request): Promise<Result<Event[]>> {
    return { ok: true, value: this.events.filter(event => event.kind !== "accepted") };
  }
  async onFriendAccepted(_req: Request): Promise<Result<Event[]>> {
    return { ok: true, value: this.events.filter(event => event.kind === "accepted") };
  }
  async listGroups(_req: Request): Promise<Result<string[]>> { return { ok: true, value: [...this.groups] }; }
  async readGroupMessages(req: Request): Promise<Result<Event[]>> {
    return { ok: true, value: this.events.filter(e => e.kind === "group" && e.thread === req.target) };
  }
  async getContact(req: Request): Promise<Result<Contact>> {
    return { ok: true, value: this.contacts.get(req.target) ?? { id: req.target, friend: false } };
  }
  private async write(operation: string, request: Request): Promise<Result> {
    if (!this.sent.has(request.key)) this.sent.set(request.key, { operation, request });
    return this.fail ? { ok: false, error: this.fail } : { ok: true, value: undefined };
  }
  sendMessage = (req: Request) => this.write("sendMessage", req);
  postToGroup = (req: Request) => this.write("postToGroup", req);
  async createGroup(req: Request) {
    const result = await this.write("createGroup", req);
    if (result.ok) this.groups.add(req.target);
    return result;
  }
  moderateGroup = (req: Request) => this.write("moderateGroup", req);
  sendFriendRequest = (req: Request) => this.write("sendFriendRequest", req);
}
