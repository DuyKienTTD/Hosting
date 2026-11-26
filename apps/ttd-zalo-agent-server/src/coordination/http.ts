import type { IncomingMessage, ServerResponse } from "node:http";
import { uuid } from "../data/repository.js";
import type { CoordinationRoom } from "./room.js";

type Authenticate = (request: IncomingMessage) => Promise<object | undefined>;
const statuses: Record<string, number> = { forbidden: 403, invalid: 400, missing: 404, conflict: 409, capacity: 503, timeout: 504 };

function json(response: ServerResponse, status: number, value: unknown) {
  response.writeHead(status, { "Content-Type": "application/json; charset=utf-8" }).end(JSON.stringify(value));
}

async function readJson(request: IncomingMessage) {
  const length = request.headers["content-length"];
  if (request.headers["content-type"]?.split(";")[0].trim() !== "application/json" ||
      (length !== undefined && Number(length) > 8192)) throw Error("invalid");
  const chunks: Buffer[] = [];
  let size = 0;
  for await (const part of request.iterator({ destroyOnReturn: false })) {
    const chunk = Buffer.isBuffer(part) ? part : Buffer.from(part);
    size += chunk.length;
    if (size > 8192) throw Error("invalid");
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8")) as unknown;
  } catch {
    throw Error("invalid");
  }
}

async function events(room: CoordinationRoom, handle: object, response: ServerResponse) {
  const first = await room.list(handle);
  response.writeHead(200, { "Content-Type": "text/event-stream", "X-Accel-Buffering": "no" });
  const publish = (state: typeof first) => response.write(
    "id: " + state.revision + "\nevent: room\ndata: " + JSON.stringify(state) + "\n\n",
  );
  let revision = first.revision;
  let timer: ReturnType<typeof setTimeout> | undefined;
  response.once("close", () => clearTimeout(timer));
  // Full snapshot on connection avoids gaps across replicas or reconnects.
  if (!publish(first)) return response.end();
  const poll = async () => {
    try {
      const state = await room.list(handle);
      if (response.destroyed) return;
      const accepted = state.revision !== revision ? publish(state) : response.write(": heartbeat\n\n");
      revision = state.revision;
      if (accepted) timer = setTimeout(() => void poll(), 1000);
      else response.end();
    } catch {
      response.end();
    }
  };
  timer = setTimeout(() => void poll(), 1000);
}

export function coordinationHttp(room: CoordinationRoom, authenticate: Authenticate, uiOrigin: string) {
  return async (request: IncomingMessage, response: ServerResponse) => {
    response.setHeader("Cache-Control", "no-store");
    response.setHeader("X-Content-Type-Options", "nosniff");
    try {
      const handle = await authenticate(request);
      if (!handle) return json(response, 401, { error: "unauthenticated" });
      const { url, method } = request;
      if (method === "GET" && url === "/coordination") return json(response, 200, await room.list(handle));
      if (method === "GET" && url === "/coordination/events") return await events(room, handle, response);
      if (method !== "POST" && method !== "PATCH") return json(response, 404, { error: "missing" });
      if (request.headers.origin !== undefined && request.headers.origin !== uiOrigin ||
          request.headers["sec-fetch-site"] === "cross-site") throw Error("forbidden");
      if (method === "POST" && url === "/coordination/messages") {
        return json(response, 201, await room.post(handle, await readJson(request)));
      }
      const match = /^\/coordination\/tickets\/([^/]+)(?:\/(run|rename|recover))?$/u.exec(url ?? "");
      if (!match || !uuid(match[1])) throw Error("missing");
      const [, id, operation] = match;
      const body = await readJson(request);
      if (!body || typeof body !== "object" || Array.isArray(body)) throw Error("invalid");
      const fields = body as Record<string, unknown>;
      const count = Object.keys(fields).length;
      if (method === "PATCH" && !operation && count === 1 && typeof fields.version === "number" &&
          Number.isSafeInteger(fields.version)) return json(response, 200, await room.approve(handle, id, fields.version));
      if (method === "POST" && operation === "recover" && count === 1 && typeof fields.version === "number" &&
          Number.isSafeInteger(fields.version)) return json(response, 200, await room.recover(handle, id, fields.version));
      if (method === "POST" && operation === "run" && count === 0) return json(response, 200, await room.run(handle, id));
      if (method === "POST" && operation === "rename" && count === 2 &&
          typeof fields.index === "number" && typeof fields.expectedName === "string") {
        await room.applyRename(handle, id, fields.index, fields.expectedName);
        return response.writeHead(204).end();
      }
      throw Error("invalid");
    } catch (error) {
      if (response.headersSent) return response.end();
      const code = error instanceof Error && Object.hasOwn(statuses, error.message) ? error.message : "internal";
      return json(response, statuses[code] ?? 500, { error: code });
    }
  };
}
