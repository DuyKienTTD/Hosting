import { randomBytes, scrypt } from "node:crypto";
import { promisify } from "node:util";
import type { Store } from "../store.js";

const derive = promisify(scrypt);

export async function createOperator(store: Store, actor: string | null, input: Record<string, unknown>) {
  const { account, label, passphrase, role } = input;
  if (typeof account !== "string" || !/^[a-z0-9_.@-]{1,120}$/i.test(account) ||
      typeof label !== "string" || !label.trim() || label.length > 120 ||
      typeof passphrase !== "string" || passphrase.length < 16 || passphrase.length > 256 ||
      (actor === null ? role !== "owner" : role !== "sales" && role !== "support")) {
    return { status: 400 as const, message: "Kiểm tra tên tài khoản, tên hiển thị, vai trò và mật khẩu tối thiểu 16 ký tự." };
  }
  const salt = randomBytes(16);
  const key = await derive(passphrase, salt, 64) as Buffer;
  const verifier = salt.toString("hex") + ":" + key.toString("hex");
  const row = store.db.prepare("SELECT public.web_create_operator(?::uuid,?,?,?,?) AS id")
    .get(actor, account, label.trim(), String(role), verifier);
  if (!row?.id) return { status: 409 as const, message: "Tài khoản đã tồn tại hoặc không còn quyền tạo." };
  return { status: 201 as const, operator: { id: row.id, label: label.trim(), role } };
}
