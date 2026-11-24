// ZALO-POC-02 A2 - offline source contract checks for A1 canonical consumer binding.
// Run in a blocked-egress pinned source tree AFTER applying both A1/A2 author patches.
// ZALO_PATCHED_SOURCE_ROOT=/absolute/checkout node --test experiments/zalo-poc-02/a2/shared-policy-contract.test.mjs
// THESE ASSERT SOURCE STRUCTURE ONLY, NOT SQLite runtime consent or restart safety.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { test } from "node:test";
const root=process.env.ZALO_PATCHED_SOURCE_ROOT;
assert.ok(root && path.isAbsolute(root),"ZALO_PATCHED_SOURCE_ROOT must point to the pinned patched checkout");
const source=(p)=>fs.readFileSync(path.join(root,p),"utf8");
const router=source("src/zalo/incoming-message-router.ts");
const filter=source("src/middleware/allowlist-filter.ts");
const replay=source("src/zalo/offline-replay/tiep-nhan-tin-lay-bu.ts");
const replayMgr=source("src/zalo/offline-replay/lay-bu-cho-account.ts");
const record=source("src/zalo/record-incoming-message.ts");
const media=source("src/conversation/media-store.ts");
const a1=source("src/agent/tools/outbound-guard-runtime.ts");
const authority=source("src/agent/tools/atomic-send-admission.ts");
test("CB-01 A2 reads canonical A1 snapshot, no second policy writer",()=>{
 assert.match(router,/import \{ readCurrentSyntheticPolicy \} from "\.\.\/agent\/tools\/outbound-guard-runtime\.js"/);
 assert.match(a1,/export function readCurrentSyntheticPolicy/);
 assert.match(authority,/export type PolicySnapshot/);
 assert.match(authority,/function readSnapshot/);
 assert.doesNotMatch(router,/CREATE TABLE|mutatePolicy\(|INSERT INTO synthetic_outbound_policy/);
});
test("CB-02 A2 rejects global/account STOP, revoked, expired, takeover and mismatch",()=>{
 for(const token of ["snapshot.globalStopped","snapshot.accountStopped","snapshot.optedOut",
  "snapshot.takeover","snapshot.stopped","!snapshot.running","snapshot.expiresAtMs <= Date.now()",
  "snapshot.accountId !== config.id","snapshot.senderId !== msg.senderId",
  "snapshot.threadId !== msg.threadId","snapshot.threadType !== (msg.isGroup"]) {
   assert.ok(router.includes(token),token);
 }
 assert.match(a1,/snap.globalStopped \|\| snap.accountStopped/);
 assert.match(filter,/consent\.revoked \|\| consent\.humanTakeover \|\| consent\.stopped/);
});
test("CB-03 consent denial is before contact/thread/history persistence",()=>{
 const denied=router.indexOf('if (!decision.respond && !decision.record) return "bo"');
 assert.ok(denied>0 && denied<router.indexOf("recordContactActivity(config.id"));
 assert.ok(denied<router.indexOf("recordThreadActivity({"));
 assert.ok(denied<router.indexOf("ghiTinDenVaoHistory(config.id"));
 assert.match(record,/if \(!current\?\.retain\) return 0/);
});
test("CB-04 replay checks current canonical policy at intake, enqueue and batch",()=>{
 assert.match(replay,/nhanVaGhiTinDen\(ctx.config, ctx.api, msg\)/);
 assert.match(replayMgr,/readInboundConsent\(c, msg\)/);
 assert.match(replayMgr,/batch.every\(\(m\) => readInboundConsent/);
 assert.match(router,/ketQua === "tra-loi" \|\| ketQua === "ghi-thu-dong"/);
});
test("CB-05 delayed media write rechecks retain after download",()=>{
 assert.match(media,/readCurrentSyntheticPolicy\(accountId, msg.threadId, msg.senderId/);
 const downloadAt=media.indexOf("const downloaded = await download(image.url)");
 const guardAt=media.indexOf("if (!readCurrentSyntheticPolicy",downloadAt);
 const writeAt=media.indexOf("fs.writeFileSync(absPath, downloaded.data)");
 assert.ok(downloadAt>=0 && guardAt>downloadAt && writeAt>guardAt);
 assert.match(record,/readCurrentSyntheticPolicy\(accountId, msg.threadId, msg.senderId/);
 assert.match(record,/readCurrentSyntheticPolicy\(msg.accountId, msg.threadId, msg.senderId/);
});
test("CB-06 absent A1 source does not create opt-in",()=>{
 assert.match(a1,/if\(!snap \|\| !snap.verified/);
 assert.doesNotMatch(router,/verified: true, respond: true, retain: true/);
 assert.doesNotMatch(router,/^[ \t]*sendDeliveredReceipt\(api, msg\);/m);
 assert.doesNotMatch(router,/^[ \t]*void resolveGroupName\(config.id, api, msg.threadId\);/m);
});
