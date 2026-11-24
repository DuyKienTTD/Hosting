// ZALO-POC-02 / A2 — source-aligned shared policy contract tests.
// Run only in a verified offline isolated patched checkout.
// ZALO_PATCHED_SOURCE_ROOT=/absolute/pinned/check-out node --test experiments/zalo-poc-02/a2/shared-policy-contract.test.mjs
// Source structure assertions are NOT integrated SQLite or security runtime PASS.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { test } from "node:test";
const root=process.env.ZALO_PATCHED_SOURCE_ROOT;
assert.ok(root && path.isAbsolute(root),"Require absolute ZALO_PATCHED_SOURCE_ROOT (pinned patched checkout)");
function source(p){return fs.readFileSync(path.join(root,p),"utf8")}
const router=source("src/zalo/incoming-message-router.ts");
const replay=source("src/zalo/offline-replay/tiep-nhan-tin-lay-bu.ts");
const replayMgr=source("src/zalo/offline-replay/lay-bu-cho-account.ts");
const filter=source("src/middleware/allowlist-filter.ts");
test("SP-01 A2 references only canonical A1 policy type, no second policy writer",()=>{
 assert.match(router,/import type \{ PolicyMutation \} from "\.\.\/agent\/tools\/atomic-send-admission\.js"/);
 assert.match(router,/export type InboundPolicyReader/);
 assert.doesNotMatch(router,/CREATE TABLE|mutatePolicy\(|INSERT INTO synthetic_outbound_policy/);
});
test("SP-02 absent policy reader denies before inbound contact/history persistence",()=>{
 assert.match(router,/if \(!readPolicy \|\| !config\.id/);
 const gate=router.indexOf('if (!decision.respond && !decision.record) return "bo"');
 assert.ok(gate>=0 && gate<router.indexOf("recordContactActivity(config.id"));
 assert.ok(gate<router.indexOf("ghiTinDenVaoHistory(config.id"));
});
test("SP-03 mismatched, expired, revoked and takeover snapshots fail closed",()=>{
 for(const token of ["snapshot.accountId !== config.id","snapshot.senderId !== msg.senderId",
   "snapshot.threadId !== msg.threadId","snapshot.optedOut","snapshot.takeover",
   "snapshot.stopped","!snapshot.running","snapshot.expiresAtMs <= Date.now()"]) {
   assert.ok(router.includes(token),token);
 }
 assert.match(filter,/consent\.revision/);
});
test("SP-04 replay uses same injected reader and avoids denied cursor advance",()=>{
 assert.match(replay,/nhanVaGhiTinDen\(ctx\.config, ctx\.api, msg, ctx\.readPolicy\)/);
 assert.match(replayMgr,/readInboundConsent\(c, msg, tiem\.readPolicy\)/);
 assert.match(router,/ketQua === "tra-loi" \|\| ketQua === "ghi-thu-dong"/);
 assert.match(replayMgr,/batch\.every\(\(m\) => readInboundConsent/);
});
test("SP-05 inbound does not unconditionally send receipts or group lookups",()=>{
 assert.doesNotMatch(router,/^[ \t]*sendDeliveredReceipt\(api, msg\);/m);
 assert.doesNotMatch(router,/^[ \t]*void resolveGroupName\(config.id, api, msg.threadId\);/m);
});
