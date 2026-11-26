import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import type { IncomingMessage, ServerResponse } from "node:http";
import { extname, join } from "node:path";
import { pipeline } from "node:stream/promises";

const types = new Map([
  [".js", "text/javascript; charset=utf-8"], [".css", "text/css; charset=utf-8"],
  [".woff2", "font/woff2"], [".woff", "font/woff"], [".html", "text/html; charset=utf-8"],
]);

export async function serveWebAssets(req: IncomingMessage, res: ServerResponse, directory: string) {
  const path = req.url?.split("?", 1)[0];
  const name = path === "/" ? "index.html" : /^\/assets\/([a-zA-Z0-9_-]+\.(?:js|css|woff2?))$/.exec(path ?? "")?.[1];
  if (!name || (req.method !== "GET" && req.method !== "HEAD")) return false;
  const index = path === "/";
  const file = index ? join(directory, name) : join(directory, "assets", name);
  const info = await stat(file).catch(() => undefined);
  if (!info?.isFile()) { res.writeHead(404).end(); return true; }
  res.writeHead(200, {
    "Content-Type": types.get(extname(name))!,
    "Content-Length": info.size,
    "Cache-Control": index ? "no-cache" : "public, max-age=31536000, immutable",
    "X-Content-Type-Options": "nosniff",
  });
  if (req.method === "HEAD") res.end();
  else await pipeline(createReadStream(file), res);
  return true;
}
