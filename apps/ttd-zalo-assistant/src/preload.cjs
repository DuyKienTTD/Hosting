const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("ttd", {
  status: () => ipcRenderer.invoke("m0:status"),
  stop: (stopped) => ipcRenderer.invoke("m0:stop", stopped),
  consent: (target, retain, respond, send, takeover) =>
    ipcRenderer.invoke("m0:consent", target, retain, respond, send, takeover),
  approve: (target, content, origin) => ipcRenderer.invoke("m0:approve", target, content, origin),
  receive: (target, text) => ipcRenderer.invoke("mvp:receive", target, text),
  conversation: (target) => ipcRenderer.invoke("mvp:conversation", target),
  profile: (target) => ipcRenderer.invoke("mvp:profile", target),
  remember: (target, source, fact) => ipcRenderer.invoke("mvp:remember", target, source, fact),
  invalidate: (target) => ipcRenderer.invoke("mvp:invalidate", target),
  draft: (target, origin) => ipcRenderer.invoke("mvp:draft", target, origin),
  importDoc: (doc) => ipcRenderer.invoke("mvp:import", doc),
  knowledge: (query) => ipcRenderer.invoke("mvp:knowledge", query),
  activity: () => ipcRenderer.invoke("mvp:activity"),
  send: (id, target, content) => ipcRenderer.invoke("m0:send", id, target, content),
});
