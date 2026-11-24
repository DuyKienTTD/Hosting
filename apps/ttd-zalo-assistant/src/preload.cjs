const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("ttd", {
  status: () => ipcRenderer.invoke("m0:status"),
  stop: (stopped) => ipcRenderer.invoke("m0:stop", stopped),
  consent: (target, retain, respond, send, takeover) =>
    ipcRenderer.invoke("m0:consent", target, retain, respond, send, takeover),
  approve: (target, content) => ipcRenderer.invoke("m0:approve", target, content),
  send: (id, target, content) => ipcRenderer.invoke("m0:send", id, target, content),
});
