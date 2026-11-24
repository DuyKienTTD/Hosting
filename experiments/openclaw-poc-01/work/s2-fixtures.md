# OpenClaw S2 test-only fixtures

Copy each block to its named path in the pinned scratch checkout. Use the existing sandbox runner environment (unshare -Urn, clean environment, temporary state and TCP negative probe). Run Vitest extension-zalo config for work-s2-send.test.ts and the schema case; for the raw-payload case use work-s2.config.ts and -t "records raw payload". Fixtures are not upstream business code.

## extensions/zalouser/src/work-s2.test.ts

```ts
import { expect, it, vi } from "vitest";
import { ZalouserAccountSchema } from "./config-schema.js";
import { createZalouserIngressMonitor } from "./ingress.js";
import { createRawZalouserMessage, observeZalouserIngressVerdict, withZalouserIngressTestQueue } from "./ingress.test-support.js";

it("stock configuration keeps reply controls but strips independent retention and response consent fields", () => {
  const parsed = ZalouserAccountSchema.parse({
    dmPolicy: "allowlist", allowFrom: ["sender-1"], historyLimit: 0,
    retentionConsent: false, responseConsent: true,
  });
  expect(parsed).toMatchObject({ dmPolicy: "allowlist", allowFrom: ["sender-1"], historyLimit: 0 });
  expect(parsed).not.toHaveProperty("retentionConsent");
  expect(parsed).not.toHaveProperty("responseConsent");
});

it("records raw payload upstream of the downstream decision seam", async () => {
  await withZalouserIngressTestQueue(async (queue) => {
    const rows = new Map<string, string>();
    const enqueue: typeof queue.enqueue = async (...args) => {
      const result = await queue.enqueue(...args);
      rows.set(args[0], args[1].rawMessage);
      return result;
    };
    const decisionIds: string[] = [];
    const monitor = createZalouserIngressMonitor({
      accountId: "default", ownUserId: "owner-1",
      queue: { ...queue, enqueue },
      runtime: { error: vi.fn(), log: vi.fn() },
      dispatch: async (msg, lifecycle) => {
        decisionIds.push(String(msg.msgId));
        expect(rows.size).toBeGreaterThan(0);
        await lifecycle.onAdopted();
      },
    });
    try {
      const msgId = "work-s2-raw";
      await monitor.receive(createRawZalouserMessage({ msgId }));
      expect([...rows.values()].some((raw) => raw.includes(msgId))).toBe(true);
    } finally {
      await monitor.stop();
    }
  });
});
```

## extensions/zalouser/src/work-s2-send.test.ts

```ts
import { loadOutboundMediaFromUrl } from "openclaw/plugin-sdk/outbound-media";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { waitForEffectPreparation } from "../../test-support/effect-preparation.test-support.js";
import {
  createSendHarness,
  encryptResponse,
  imageUrl,
  serviceUrl,
  useAudioFixture,
  type SendHarness,
} from "./send.handoff.test-support.js";
import { createZalouserTool } from "./tool.js";

const effectGate = await vi.hoisted(async () =>
  (
    await import("../../test-support/effect-preparation.test-support.js")
  ).createEffectPreparationGate(),
);
// mock-isolation: Share the export-preserving factory, but keep the preparation gate suite-local.
vi.mock("openclaw/plugin-sdk/fetch-runtime", effectGate.mockRuntime);

vi.mock("./session-state.js", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./session-state.js")>()),
  clearStoredZaloCredentials: vi.fn(),
  loadStoredZaloCredentials: vi.fn(),
  refreshStoredZaloCredentials: vi.fn(),
  saveStoredZaloCredentials: vi.fn(async () => {}),
}));

vi.mock("openclaw/plugin-sdk/outbound-media", () => ({
  loadOutboundMediaFromUrl: vi.fn(),
}));

let harness: SendHarness;

beforeEach(() => {
  harness = createSendHarness();
});

afterEach(async () => {
  await harness.close();
});


it("canceled DM and allowed group with the same target ID stay separated at fake transport", async () => {
  await harness.send("message.text", {text:"warm"});
  harness.requests.length=0;
  const cookie=harness.holdCookie();
  const caller=new AbortController();
  const pending=harness.send("message.text",{to:"user:201",text:"denied DM",signal:caller.signal}).catch(e=>e);
  try {
    await cookie.entered.promise;
    caller.abort(new Error("synthetic STOP"));
    const allowed=await harness.send("sendText",{to:"group:201",text:"allowed group"});
    expect(allowed.messageId).toBeTruthy();
  } finally {cookie.release.resolve();}
  expect(await pending).toMatchObject({message:"synthetic STOP"});
  expect(harness.requests).toHaveLength(1);
  expect(harness.requests[0]?.path).toContain("/group/");
  expect(harness.requests[0]?.params).toMatchObject({grid:"201",message:"allowed group"});
  console.log("fake transport: stopped DM=0, allowed group=1");
});
```

## test/vitest/work-s2.config.ts

```ts
import config from "./vitest.extension-database-workers.config.ts";
export default {...config,test:{...config.test,include:["zalouser/src/work-s2.test.ts"],passWithNoTests:false}};
```
