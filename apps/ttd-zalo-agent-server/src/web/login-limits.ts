import { isIP, SocketAddress } from "node:net";

const windowMs = 15 * 60_000;
const capacity = 10_000;
const clientThreshold = 10;
const accountThreshold = 5;

function ip(value: string | undefined) {
  const family = isIP(value ?? "");
  if (family === 4) return value;
  if (family !== 6 || value!.includes("%")) return;
  const address = new SocketAddress({ address: value, family: "ipv6" }).address;
  const mapped = /^::ffff:([0-9a-f]{1,4}):([0-9a-f]{1,4})$/i.exec(address);
  if (!mapped) return address.replace(/^::ffff:(?=\d+\.)/i, "");
  const upper = Number.parseInt(mapped[1], 16);
  const lower = Number.parseInt(mapped[2], 16);
  return [upper >> 8, upper & 255, lower >> 8, lower & 255].join(".");
}

export function loginClientAddress(proxies = "") {
  const trusted = new Set(["127.0.0.1", "::1"]);
  for (const item of proxies.split(",").map(value => value.trim()).filter(Boolean)) {
    const address = ip(item);
    if (!address) throw Error("INVALID_TRUSTED_PROXY");
    trusted.add(address);
  }
  return (peer: string | undefined, forwarded: string | string[] | undefined) => {
    const socket = ip(peer) ?? "unknown";
    // The ingress proxy overwrites X-Forwarded-For with exactly one address.
    return trusted.has(socket) && typeof forwarded === "string" ? ip(forwarded.trim()) ?? socket : socket;
  };
}

type Counter = { failures: number; pending: number; expires: number; retryAt: number };

export function loginLimits(clock = Date.now) {
  const clients = new Map<string, Counter>();
  const accounts = new Map<string, Counter>();
  let sweepAt = 0;
  let minute = -1;
  let started = 0;
  let pending = 0;
  const counter = (map: Map<string, Counter>, key: string, now: number) => {
    const row = map.get(key);
    return row && (row.expires > now || row.pending > 0) ? row : undefined;
  };
  function finish(row: Counter, limit: number, failed: boolean, now: number) {
    row.pending--;
    if (failed && ++row.failures >= limit) {
      row.retryAt = Math.min(row.expires, now + Math.min(5 * 60_000, 30_000 * 2 ** (row.failures - limit)));
    }
  }

  return (client: string, username: string) => {
    const now = clock();
    if (now >= sweepAt) {
      sweepAt = now + 60_000;
      for (const map of [clients, accounts]) {
        for (const [key, row] of map) {
          if (row.expires <= now && row.pending === 0) map.delete(key);
        }
      }
    }
    const account = username.trim().toLowerCase();
    const clientRow = counter(clients, client, now);
    const accountRow = counter(accounts, account, now);
    const blocked = (row: Counter | undefined, limit: number) =>
      row && (row.retryAt > now || row.pending >= Math.max(1, limit - row.failures));
    if (blocked(clientRow, clientThreshold) || blocked(accountRow, accountThreshold)) return;
    const currentMinute = Math.floor(now / 60_000);
    if (currentMinute !== minute) { minute = currentMinute; started = 0; }
    if (started >= 600 || pending >= 16) return;
    if ((!clientRow && clients.size >= capacity && !clients.has(client)) ||
        (!accountRow && accounts.size >= capacity && !accounts.has(account))) return;

    const fresh = () => ({ failures: 0, pending: 0, expires: now + windowMs, retryAt: 0 });
    const byClient = clientRow ?? fresh();
    const byAccount = accountRow ?? fresh();
    clients.set(client, byClient);
    accounts.set(account, byAccount);
    byClient.pending++;
    byAccount.pending++;
    pending++;
    started++;
    return (failed: boolean) => {
      pending--;
      const completed = clock();
      finish(byClient, clientThreshold, failed, completed);
      finish(byAccount, accountThreshold, failed, completed);
    };
  };
}
