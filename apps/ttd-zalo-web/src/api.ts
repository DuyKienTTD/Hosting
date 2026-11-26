import type { OaQuoteBlock } from "./oa-quote-policy";

export type Role = "owner" | "support" | "sales" | "a0";
export type Operator = { id: string; label: string; role: Role };
export type Purpose = "support" | "quote" | "marketing";
export type Consent = "unknown" | "granted" | "withdrawn";
export type OptOut = "none" | "review" | "stop";
export type Delivery =
  | "draft"
  | "queued"
  | "sent"
  | "blocked"
  | "unknown_delivery";
export type Unit = "metre" | "bar" | "set";

export type Conversation = {
  id: string;
  customerId: string;
  subject: string;
  channel: "oa" | "nick" | "bot";
  message: string;
  time: string;
  draft: string;
  version: number;
  delivery: Delivery;
  reason?: string;
};
export type OaThread = {
  id: string;
  customerId: string;
  lastInteractionAt: string;
  following: boolean | null;
};
export type InboxDraft = {
  id: string;
  version: number;
  text: string;
  state: "pending" | "generating" | "ready" | "needs_human" | "approved";
  intent: "price" | "technical" | "complaint" | "other" | null;
  reason: "mock" | "budget" | "consent" | "unavailable" | "no_knowledge" | null;
  sourceIds: string[];
  delivery: Delivery;
};
export type ApprovedInboxDraft = Pick<InboxDraft, "id" | "version" | "text"> & {
  conversationId: string;
};
export type OaThreadDetail = OaThread & {
  messages: {
    id: string;
    at: string;
    direction: "incoming" | "outgoing";
    text: string | null;
    delivery?: string;
  }[];
  sendBlock: { code: string; message: string } | null;
  aiDraft: InboxDraft | null;
  estimatedAiUsdToday?: number;
};
export type Customer = {
  id: string;
  label: string;
  segment: string;
  followUp: string;
  optOut: OptOut;
  oaQuoteBlock: OaQuoteBlock | null;
  consent: Record<Purpose, Consent>;
};
export type Product = {
  id: string;
  label: string;
  millimetresPerBar: number;
  barsPerSet: number;
  vndPerMetre: number;
  approvedPriceList: string | null;
};
export type QuoteInput = {
  customerId: string;
  productId: string;
  unit: Unit;
  quantity: number;
};
export type ConfirmedQuote = QuoteInput & {
  confirmed: true;
  priceList: string;
};
export type Quote = QuoteInput & {
  delivery?: "queued" | "sent" | "failed" | "unknown_delivery";
  id: string;
  totalMillimetres: number;
  totalVnd: number;
};
export type WorkItem = {
  id: string;
  title: string;
  agent: string;
  status: "new" | "active" | "review" | "done";
  result?: string | null;
  reviewDecision?: "accept" | "dismiss" | null;
};
export type RoomMessage = { id: string; author: string; text: string; task?: WorkItem };
export type Channel = {
  id: Conversation["channel"];
  label: string;
  state: "online" | "offline" | "stopped";
  detail: string;
};
export type DeletionRequest = {
  id: string;
  customerId: string;
  reason: string;
  status: "requested";
};
export type Workspace = {
  adsEnabled: false;
  conversations: Conversation[];
  customers: Customer[];
  products: Product[];
  quotes: Quote[];
  workItems: WorkItem[];
  roomMessages: RoomMessage[];
  channels: Channel[];
  deletionRequests: DeletionRequest[];
  agents: { label: string; role: string; status: string }[];
  activity: { day: string; received: number; answered: number }[];
};
export type Router = { status: "available" | "capped" } | {
  provider: string;
  budgetVnd: number | null;
  usedVnd: number | null;
  model: string;
  unassignedUsd?: number;
  draftsEnabled?: boolean;
  agents?: { id: string; model: string; permission: "read" | "propose"; enabled: boolean; blocked: boolean;
    usedUsd: number; usedVnd: number | null }[];
};
export type Settings = { adsEnabled: false };

export const roleLabels: Record<Role, string> = {
  owner: "Chủ dự án",
  support: "CSKH",
  sales: "Bán hàng",
  a0: "A0",
};
export const permissions = {
  approve: ["owner", "support"],
  quote: ["owner", "sales"],
  task: ["owner"],
  stop: ["owner"],
  restrictedRead: ["owner", "a0"],
  privacy: ["owner"],
} as const satisfies Record<string, readonly Role[]>;
export type Action = keyof typeof permissions;
export function can(role: Role, action: Action) {
  return (permissions[action] as readonly Role[]).includes(role);
}

export const demoMode = import.meta.env.DEV || import.meta.env.MODE === "mock";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string,
  ) {
    super(message);
  }
}
async function request<T>(
  path: string,
  method = "GET",
  body?: object,
): Promise<T> {
  const response = await fetch("/api/v1" + path, {
    method,
    credentials: "same-origin",
    cache: "no-store",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new ApiError(
      response.status,
      error?.message ?? "Không thể kết nối dịch vụ.",
      error?.code,
    );
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export const api = {
  connectOa: () =>
    request<{ authorizationUrl: string }>("/oa/oauth/start", "POST"),
  session: () => request<Operator>("/session"),
  login: (
    credentials: { account: string; passphrase: string } | { demoRole: Role },
  ) => request<Operator>("/session", "POST", credentials),
  logout: () => request<void>("/session", "DELETE"),
  workspace: () => request<Workspace>("/workspace"),
  inbox: () => request<OaThread[]>("/inbox"),
  oaThread: (id: string) =>
    request<OaThreadDetail>("/inbox/" + encodeURIComponent(id)),
  regenerateDraft: (id: string, version: number) =>
    request<InboxDraft>(
      "/drafts/" + encodeURIComponent(id) + "/regenerate",
      "POST",
      { version },
    ),
  approveDraft: (id: string, version: number, text?: string) =>
    request<ApprovedInboxDraft>(
      "/drafts/" + encodeURIComponent(id) + "/approve",
      "POST",
      { version, text },
    ),
  replyOa: (id: string, text: string) =>
    request<{ delivery: "sent" }>(
      "/inbox/" + encodeURIComponent(id) + "/replies",
      "POST",
      { text },
    ),
  approve: (id: string, version: number, text: string) =>
    request<Conversation>(
      "/conversations/" + encodeURIComponent(id) + "/approve",
      "POST",
      { version, text },
    ),
  quote: (input: ConfirmedQuote) => request<Quote>("/quotes", "POST", input),
  sendQuote: (input: ConfirmedQuote) =>
    request<Quote>("/quotes/oa-send", "POST", input),
  router: () => request<Router>("/agent-router"),
  toggleAgent: (id: string, enabled: boolean) =>
    request<{ enabled: boolean }>("/agent-router/" + encodeURIComponent(id) + "/enabled", "POST", { enabled }),
  reviewAgent: (id: string, decision: "accept" | "dismiss") =>
    request<{ status: "done" }>("/work-items/" + encodeURIComponent(id) + "/review", "POST", { decision }),
  settings: () => request<Settings>("/settings"),
  createOperator: (input: {
    account: string;
    label: string;
    passphrase: string;
    role: "sales" | "support";
  }) => request<Operator>("/operators", "POST", input),
  task: (title: string, agent: string) =>
    request<WorkItem>("/work-items", "POST", { title, agent }),
  postRoomMessage: (text: string) =>
    request<RoomMessage>("/room-messages", "POST", { text }),
  pairNick: () => request<{code: string; expiresAt: number}>("/channels/nick/pairing", "POST"),
  revokeNick: () => request<{revoked: boolean}>("/channels/nick/revoke", "POST"),
  stopNick: () => request<Channel>("/channels/nick/stop", "POST"),
  requestDeletion: (customerId: string, reason: string) =>
    request<DeletionRequest>("/deletion-requests", "POST", {
      customerId,
      reason,
    }),
};
