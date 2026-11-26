export type Thread =
  | { kind: "direct"; conversationId: string }
  | { kind: "group"; groupId: string };

export interface PageRequest {
  cursor?: string;
  limit?: number;
}

export interface Page<T> {
  items: T[];
  nextCursor?: string;
}

export interface Message {
  messageId: string;
  senderId: string;
  thread: Thread;
  text: string;
}

export interface FriendAcceptance {
  contactId: string;
  evidenceId: string;
}

export interface EventPayloads {
  messageReceived: Message;
  friendAccepted: FriendAcceptance;
}

export type ChannelEvent<K extends keyof EventPayloads = keyof EventPayloads> = {
  [T in K]: {
    version: 1;
    accountId: string;
    eventId: string;
    occurredAt: string;
    type: T;
    payload: EventPayloads[T];
  }
}[K];

export type GroupModeration =
  | { action: "add_member" | "remove_member"; groupId: string; contactId: string }
  | { action: "delete_message"; groupId: string; messageId: string }
  | { action: "rename_group"; groupId: string; name: string };

export interface CommandPayloads {
  receiveMessage: PageRequest;
  sendMessage: { conversationId: string; text: string };
  listGroups: PageRequest;
  readGroupMessages: PageRequest & { groupId: string };
  postToGroup: { groupId: string; text: string };
  createGroup: { name: string; memberIds: string[] };
  moderateGroup: GroupModeration;
  sendFriendRequest: { contactId: string };
  onFriendAccepted: PageRequest;
  getContact: { contactId: string };
}

export type Operation = keyof CommandPayloads;
export type Command<K extends Operation = Operation> = {
  [T in K]: {
    version: 1;
    accountId: string;
    idempotencyKey: string;
    operation: T;
    payload: CommandPayloads[T];
  }
}[K];

export interface DeliveryReceipt {
  providerMessageId: string;
  state: "accepted" | "delivered";
}

export interface Group {
  groupId: string;
  name: string;
}

export interface Contact {
  contactId: string;
  displayName?: string;
  friendship: "unknown" | "pending" | "accepted";
  tags?: string[];
  notes?: string[];
}

export interface Results {
  receiveMessage: Page<ChannelEvent<"messageReceived">>;
  sendMessage: DeliveryReceipt;
  listGroups: Page<Group>;
  readGroupMessages: Page<ChannelEvent<"messageReceived">>;
  postToGroup: DeliveryReceipt;
  createGroup: Group;
  moderateGroup: { applied: true };
  sendFriendRequest: { status: "requested" | "already_friends" };
  onFriendAccepted: Page<ChannelEvent<"friendAccepted">>;
  getContact: Contact;
}

export type ChannelErrorCode = "rate_limited" | "auth" | "not_supported" | "unknown_delivery" | "invalid_input" | "policy_denied" | "temporary_failure";
export interface ChannelError {
  providerCode?: number;
  code: ChannelErrorCode;
  retryAfterSeconds?: number;
}
export type Result<T> = { ok: true; value: T } | { ok: false; error: ChannelError };

export interface ChannelAdapter {
  receiveMessage(command: Command<"receiveMessage">): Promise<Result<Results["receiveMessage"]>>;
  sendMessage(command: Command<"sendMessage">): Promise<Result<Results["sendMessage"]>>;
  listGroups(command: Command<"listGroups">): Promise<Result<Results["listGroups"]>>;
  readGroupMessages(command: Command<"readGroupMessages">): Promise<Result<Results["readGroupMessages"]>>;
  postToGroup(command: Command<"postToGroup">): Promise<Result<Results["postToGroup"]>>;
  createGroup(command: Command<"createGroup">): Promise<Result<Results["createGroup"]>>;
  moderateGroup(command: Command<"moderateGroup">): Promise<Result<Results["moderateGroup"]>>;
  sendFriendRequest(command: Command<"sendFriendRequest">): Promise<Result<Results["sendFriendRequest"]>>;
  onFriendAccepted(command: Command<"onFriendAccepted">): Promise<Result<Results["onFriendAccepted"]>>;
  getContact(command: Command<"getContact">): Promise<Result<Results["getContact"]>>;
}
