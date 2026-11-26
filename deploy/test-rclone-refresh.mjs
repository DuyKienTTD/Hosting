import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { readFileSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { promisify } from "node:util";

const run = promisify(execFile);
const config = process.env.RCLONE_CONFIG;
const source = process.env.RCLONE_CONFIG_SOURCE ?? "/run/rclone-source.conf";
const original = readFileSync(source, "utf8");
assert.equal(statSync(config).mode & 0o777, 0o600);
assert.equal(statSync(config).uid, process.getuid());
assert.match(original, /fixture-expired/);

let refreshes = 0;
const oauth = createServer((req, res) => {
  if (req.method !== "POST" || req.url !== "/token") return res.writeHead(404).end();
  refreshes++;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify({ access_token: "fixture-fresh", token_type: "Bearer", expires_in: 3600 }));
});
await new Promise(resolve => oauth.listen(0, "127.0.0.1", resolve));
try {
  const env = {
    ...process.env,
    RCLONE_DRIVE_TOKEN_URL: `http://127.0.0.1:${oauth.address().port}/token`,
    HTTP_PROXY: "http://127.0.0.1:1",
    HTTPS_PROXY: "http://127.0.0.1:1",
    NO_PROXY: "127.0.0.1",
  };
  for (let attempt = 0; attempt < 2; attempt++) {
    // The fixture supplies OAuth locally. The Drive API request is blocked by the proxy.
    const result = await run("rclone", ["about", "fixture:", "--retries", "1",
      "--low-level-retries", "1", "--contimeout", "1s"], { env, timeout: 5000 })
      .catch(error => error);
    assert.doesNotMatch(result.stderr ?? "", /read-only file system|failed to save config/i);
    assert.match(readFileSync(config, "utf8"), /fixture-fresh/);
    assert.equal(statSync(config).mode & 0o777, 0o600);
  }
  assert.equal(refreshes, 1);
  assert.equal(readFileSync(source, "utf8"), original);
} finally {
  await new Promise(resolve => oauth.close(resolve));
}
