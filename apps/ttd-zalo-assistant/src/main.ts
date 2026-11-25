import { app, BrowserWindow, dialog, ipcMain, session } from "electron";
import { fileURLToPath, pathToFileURL } from "node:url";
import { join } from "node:path";
import type { Source } from "./knowledge.js";
import { validField } from "./customer.js";
import { Foundation, validTarget } from "./foundation.js";

const dir = fileURLToPath(new URL(".", import.meta.url));
const index = pathToFileURL(join(dir, "index.html")).href;
const smoke = !app.isPackaged && process.argv.includes("--m0-smoke");
app.disableHardwareAcceleration();
app.commandLine.appendSwitch("disable-background-networking");
app.enableSandbox();

async function start() {
  if (!app.requestSingleInstanceLock()) { app.quit(); return; }
  await app.whenReady();
  const db = new Foundation(join(app.getPath("userData"), "foundation.sqlite"));
  app.once("will-quit", () => db.close());
  const ses = session.fromPartition("ttd-offline");
  ses.setPermissionCheckHandler(() => false);
  ses.setPermissionRequestHandler((_contents, _permission, respond) => respond(false));
  ses.on("will-download", (event) => event.preventDefault());
  ses.webRequest.onBeforeRequest((info, respond) => {
    const allow = ["index.html", "style.css", "ui.js"].some((file) => info.url === pathToFileURL(join(dir, file)).href);
    respond({ cancel: !allow });
  });
  const win = new BrowserWindow({
    width: 1000, height: 720, minWidth: 520, minHeight: 560, title: "TTD Zalo Assistant",
    webPreferences: { session: ses, preload: join(dir, "preload.cjs"), nodeIntegration: false,
      contextIsolation: true, sandbox: true, webSecurity: true, devTools: false },
  });
  win.webContents.setWindowOpenHandler(() => ({ action: "deny" }));
  win.webContents.on("will-navigate", (event) => event.preventDefault());
  win.webContents.on("will-attach-webview", (event) => event.preventDefault());
  const handle = (channel: string, count: number, run: (args: unknown[]) => unknown) => {
    ipcMain.handle(channel, async (event, ...args: unknown[]) => {
      if (event.sender !== win.webContents || !event.senderFrame ||
          event.senderFrame !== win.webContents.mainFrame || event.senderFrame.url !== index || args.length !== count) {
        throw new Error("IPC_DENIED");
      }
      try { return await run(args); }
      catch { throw new Error("ACTION_DENIED"); }
    });
  };
  handle("m0:status", 0, () => db.status());
  handle("m0:stop", 1, ([flag]) => {
    if (typeof flag !== "boolean") throw new Error("INVALID_STOP");
    db.setStopped(flag);
    return db.status();
  });
  handle("m0:consent", 5, ([target, retain, respond, send, takeover]) => {
    if (!validTarget(target) || typeof retain !== "boolean" || typeof respond !== "boolean" ||
        typeof send !== "boolean" || typeof takeover !== "boolean") throw new Error("INVALID_CONSENT");
    db.setConsent(target, { retain, respond, send }, Date.now() + 3_600_000, takeover);
    return db.status();
  });
  handle("m0:approve", 3, ([target, content, intent]) => {
    if (!validTarget(target) || typeof content !== "string" || typeof intent !== "string" || !intent) throw new Error("INVALID_APPROVAL");
    return db.approve(target, content, intent);
  });
  handle("m0:send", 3, ([id, target, content]) => {
    if (typeof id !== "string" || !validTarget(target) || typeof content !== "string") throw new Error("INVALID_SEND");
    return db.send(id, target, content);
  });
  handle("mvp:receive", 2, ([target, text]) => {
    if (!validTarget(target) || typeof text !== "string") throw new Error("INVALID_DM");
    return db.receive(target, crypto.randomUUID(), text);
  });
  handle("mvp:conversation", 1, ([target]) => {
    if (!validTarget(target)) throw new Error("INVALID_TARGET");
    return db.conversation(target);
  });
  handle("mvp:profile", 1, ([target]) => {
    if (!validTarget(target)) throw new Error("INVALID_TARGET");
    return db.profile(target);
  });
  handle("mvp:remember", 3, ([target, source, fact]) => {
    if (!validTarget(target) || typeof source !== "string" || typeof fact !== "string") throw new Error("INVALID_FACT");
    db.remember(target, source, fact);
    return db.profile(target);
  });
  handle("mvp:invalidate", 1, ([target]) => {
    if (!validTarget(target)) throw new Error("INVALID_TARGET");
    db.invalidateApprovals(target);
  });
  handle("mvp:draft", 2, ([target, origin]) => {
    if (!validTarget(target) || typeof origin !== "string") throw new Error("INVALID_DRAFT");
    return db.draft(target, origin);
  });
  handle("mvp:import", 1, ([doc]) => {
    if (typeof doc !== "string") throw new Error("INVALID_DOCUMENT");
    return db.importKnowledge(doc);
  });
  handle("mvp:knowledge", 1, ([query]) => {
    if (typeof query !== "string") throw new Error("INVALID_QUERY");
    return db.knowledge(query);
  });
  handle("product:import-document", 2, ([filename, doc]) => {
    if (typeof filename !== "string" || typeof doc !== "string") throw Error("INVALID_DOCUMENT");
    return db.importKnowledge(doc, filename);
  });
  handle("product:add-source", 1, ([json]) => {
    if (typeof json !== "string" || json.length > 12000) throw Error("INVALID_CATALOGUE");
    const row: Partial<Source> | null = JSON.parse(json);
    if (!row || typeof row !== "object" || Array.isArray(row) || row.kind === "document" ||
        Object.keys(row).length !== 11) throw Error("INVALID_CATALOGUE");
    return db.addCatalogueSource(row as Source);
  });
  handle("product:fields", 1, ([target]) => {
    if (!validTarget(target)) throw Error("INVALID_TARGET");
    return db.fields(target);
  });
  handle("product:save-field", 4, ([target, source, kind, value]) => {
    if (!validTarget(target) || typeof source !== "string" || !validField(kind) || typeof value !== "string") {
      throw Error("INVALID_FIELD");
    }
    db.saveField(target, source, kind, value);
  });
  handle("product:export", 1, async ([target]) => {
    if (!validTarget(target) || !db.policy(target).retain) throw Error("EXPORT_DENIED");
    const selection = await dialog.showSaveDialog(win, {
      defaultPath: `${target}.json`, filters: [{ name: "JSON", extensions: ["json"] }],
    });
    if (selection.canceled || !selection.filePath) return false;
    const { writeFileSync } = await import("node:fs");
    writeFileSync(selection.filePath, JSON.stringify(db.exportCustomer(target), null, 2), { mode: 0o600 });
    return true;
  });
  handle("product:delete", 1, ([target]) => {
    if (!validTarget(target)) throw Error("INVALID_TARGET");
    db.deleteCustomer(target);
  });
  handle("mvp:activity", 0, () => db.activity());
  await win.loadURL(index);
  if (smoke) {
    const result: unknown = await win.webContents.executeJavaScript(`(async () => {
      const expect = (ok, label) => { if (!ok) throw Error(label); };
      const until = async (test) => {
        for (let i=0; i<100; i++) { if (test()) return; await new Promise(r=>setTimeout(r,20)); }
        throw Error("UI timeout");
      };
      await until(() => document.querySelector("#stop"));
      expect(typeof require === "undefined" && typeof process === "undefined", "renderer isolation");
      let invalid = false;
      try { await window.ttd.stop("false"); } catch { invalid = true; }
      expect(invalid, "invalid IPC rejected");
      document.querySelector("#stop").click();
      await until(() => document.querySelector("#stop").textContent.includes("Dừng"));
      document.querySelector("#stop").click();
      await until(() => document.querySelector("#stop").textContent.includes("Bỏ"));
      expect(document.querySelectorAll("nav button").length === 6, "six screens");
      document.querySelector("#stop").click();
      await until(() => document.querySelector("#stop").textContent.includes("Dừng"));
      await window.ttd.consent("customer-a", true, true, true, false);
      await window.ttd.importDoc("SKU: MAU-01\\nTên: Mẫu A\\nThông tin: Thép mạ kẽm");
      const inbound = await window.ttd.receive("customer-a", "Hỏi SKU MAU-01");
      expect(inbound.canDraft, "fake inbound");
      await window.ttd.saveField("customer-a", inbound.id, "follow-up", "Kiểm tra mẫu");
      expect((await window.ttd.fields("customer-a")).length === 1, "follow-up attached to inbound");
      expect((await window.ttd.status()).connection.channel === "fake", "fake connection status");
      const note = await window.ttd.importDocument("notes.md", "# Kiểm tra <img src=x onerror=throw(1)>");
      expect((await window.ttd.knowledge("kiểm tra")).some(row => row.id === note), "Markdown is indexed as data");
      let wrongKind = false;
      try { await window.ttd.saveField("customer-a", inbound.id, "execute", "Kiểm tra"); }
      catch { wrongKind = true; }
      expect(wrongKind, "invalid field rejected");
      const draft = await window.ttd.draft("customer-a", inbound.id);
      expect(draft.source.id === "MAU-01", "draft source");
      const grant = await window.ttd.approve("customer-a", draft.text, inbound.id);
      await window.ttd.send(grant, "customer-a", draft.text);
      expect((await window.ttd.status()).fakeSends === 1, "one fake initiation");
      await window.ttd.stop(true);
      return "UI, six screens, IPC rejection, STOP and fake DM bridge PASS";
    })()`);
    console.log(result);
    if (process.env.TTD_SMOKE_PNG) {
      const { writeFile } = await import("node:fs/promises");
      await writeFile(process.env.TTD_SMOKE_PNG, (await win.webContents.capturePage()).toPNG());
    }
    app.quit();
  }
}
app.on("window-all-closed", () => app.quit());
start().catch(() => { console.error("TTD_STARTUP_FAILED"); app.exit(1); });
