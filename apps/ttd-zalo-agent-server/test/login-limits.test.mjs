import assert from "node:assert/strict";
import test from "node:test";
import { loginClientAddress, loginLimits } from "../dist/ttd-zalo-agent-server/src/web/login-limits.js";

test("resolve only a single valid forwarded IP from exact trusted peers", () => {
  const resolve = loginClientAddress("172.20.0.1, 2001:db8::1");
  assert.equal(resolve("::ffff:172.20.0.1", "192.0.2.5"), "192.0.2.5");
  assert.equal(resolve("2001:0db8:0:0:0:0:0:1", "2001:0db8::42"), "2001:db8::42");
  assert.equal(resolve("172.20.0.2", "192.0.2.5"), "172.20.0.2");
  assert.equal(resolve("127.0.0.1", "192.0.2.5, 127.0.0.2"), "127.0.0.1");
  assert.equal(resolve("127.0.0.1", ["192.0.2.5"]), "127.0.0.1");
  assert.throws(() => loginClientAddress("172.20.0.0/16"), /INVALID_TRUSTED_PROXY/);
});

test("IP and normalized account limits are independent, with escalating delay and expiry", () => {
  let now = 0;
  const admit = loginLimits(() => now);
  for (let index = 0; index < 30; index++) {
    const complete = admit("ip-a", "distinct-" + index);
    if (index < 10) complete(true);
    else assert.equal(complete, undefined);
  }
  admit("ip-b", "unrelated")(false);
  for (let i = 0; i < 5; i++) admit("multi-" + i, i % 2 ? " Account " : "account")(true);
  assert.equal(admit("multi-6", "ACCOUNT"), undefined);
  now += 30_000;
  admit("multi-6", "account")(true);
  now += 30_000;
  assert.equal(admit("multi-7", "account"), undefined);
  now += 60_000;
  admit("multi-7", "account")(false);
  now = 15 * 60_000;
  admit("ip-a", "new-account")(false);
  admit("multi-8", "account")(false);
});

test("in-flight checks cannot overshoot the account threshold and flood ceiling expires", () => {
  let now = 0;
  const admit = loginLimits(() => now);
  const outstanding = Array.from({ length: 5 }, (_, index) => admit("ip-" + index, "shared"));
  assert.equal(admit("ip-6", "shared"), undefined);
  for (const finish of outstanding) finish(true);
  assert.equal(admit("ip-7", "shared"), undefined);
  for (let i = 0; i < 595; i++) admit("ip-flood-" + i, "account-" + i)(false);
  assert.equal(admit("ip-after", "independent"), undefined);
  now += 60_000;
  admit("ip-after", "independent")(false);
});
