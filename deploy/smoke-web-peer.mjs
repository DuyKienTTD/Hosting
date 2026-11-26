import assert from "node:assert/strict";

try {
  for (let i = 0; i < 11; i++) {
    const response = await fetch("http://runtime:8080/api/v1/session", {
      method: "POST",
      headers: {
        Origin: "https://cskh.thuanthanhdat.com.vn",
        "Content-Type": "application/json",
        "X-Forwarded-For": "198.51.100." + (i + 1),
      },
      body: JSON.stringify({ account: "peer-fixture-" + i, passphrase: "invalid" }),
    });
    assert.equal(response.status, i < 10 ? 401 : 429);
    await response.body?.cancel();
  }
  console.log("PASS 04c untrusted peer could not bypass socket IP limit using X-Forwarded-For");
} catch (error) {
  console.error("FAIL 04c untrusted peer X-Forwarded-For enforcement");
  throw error;
}
