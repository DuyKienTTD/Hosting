import { app, BrowserWindow, ipcMain, session } from "electron";
import { fileURLToPath, pathToFileURL } from "node:url";
import { join } from "node:path";
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
  handle("m0:approve", 2, ([target, content]) => {
    if (!validTarget(target) || typeof content !== "string") throw new Error("INVALID_APPROVAL");
    return db.approve(target, content);
  });
  handle("m0:send", 3, ([id, target, content]) => {
    if (typeof id !== "string" || !validTarget(target) || typeof content !== "string") throw new Error("INVALID_SEND");
    return db.send(id, target, content);
  });
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
      return "UI launch, sandboxed renderer, invalid IPC and STOP control PASS";
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
