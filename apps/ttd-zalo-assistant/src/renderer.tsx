import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import type { Foundation, Target } from "./foundation.js";

type Snapshot = ReturnType<Foundation["status"]>;
declare global {
  interface Window {
    ttd: {
      status(): Promise<Snapshot>;
      stop(flag: boolean): Promise<Snapshot>;
      consent(target: Target, retain: boolean, respond: boolean, send: boolean, takeover: boolean): Promise<Snapshot>;
      approve(target: Target, content: string): Promise<string>;
      send(id: string, target: Target, content: string): Promise<{ status: string }>;
    };
  }
}

function App() {
  const [status, setStatus] = useState<Snapshot>();
  const [target, setTarget] = useState<Target>("customer-a");
  const [draft, setDraft] = useState("");
  const [approval, setApproval] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [scopes, setScopes] = useState({ retain: false, respond: false, send: false, takeover: false });
  const [dirty, setDirty] = useState(false);
  useEffect(() => { window.ttd.status().then(setStatus).catch(() => setNotice("Không đọc được trạng thái.")); }, []);
  const policy = status?.customers.find((row) => row.id === target)?.policy;
  const displayed = dirty ? scopes : policy ?? scopes;
  const labels = { retain: "Cho phép lưu", respond: "Cho phép soạn phản hồi", send: "Cho phép gửi giả lập",
    takeover: "Nhân viên tiếp quản" };
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setNotice("");
    try { await action(); }
    catch { setApproval(""); setNotice("Thao tác bị từ chối. Kiểm tra quyền và trạng thái dừng."); }
    finally { setBusy(false); }
  }
  return <>
    <header><div><h1>TTD Zalo Assistant</h1><p>Chế độ ngoại tuyến · Dữ liệu giả lập</p></div>
      {status && <button id="stop" disabled={busy} className="stop" onClick={() => void run(async () => {
        setApproval(""); setStatus(await window.ttd.stop(!status.stopped)); setDirty(false);
      })}>{status.stopped ? "Bỏ dừng giả lập" : "Dừng gửi"}</button>}</header>
    <p aria-live="polite">{status ? (status.stopped ? "Đang dừng" : "Đã bật thử nghiệm") : "Đang tải"} · Đã gửi giả lập: {status?.fakeSends ?? 0}</p>
    <section><h2>Quyền theo hội thoại</h2>
      <label>Khách hàng <select value={target} disabled={busy} onChange={(e) => {
        setTarget(e.currentTarget.value as Target); setDirty(false); setApproval(""); setDraft("");
      }}>{status?.customers.map((c) => <option key={c.id} value={c.id}>{c.name} · {c.thread}</option>)}</select></label>
      <fieldset disabled={busy || !status} aria-label="Quyền giả lập">
      {(["retain", "respond", "send", "takeover"] as const).map((key) => <label key={key}>
        <input type="checkbox" checked={displayed[key]} onChange={(e) => {
          setScopes({ ...displayed, [key]: e.currentTarget.checked }); setDirty(true); setApproval("");
        }} />{labels[key]}</label>)}
      </fieldset>
      <button disabled={busy || !dirty} onClick={() => void run(async () => {
        setStatus(await window.ttd.consent(target, scopes.retain, scopes.respond, scopes.send, scopes.takeover));
        setDirty(false); setNotice("Đã cập nhật quyền giả lập.");
      })}>Lưu quyền thử nghiệm</button>
    </section>
    <section><h2>Gửi thử</h2>
      <label htmlFor="draft">Nội dung giả lập</label>
      <textarea id="draft" maxLength={2000} value={draft} disabled={busy} onChange={(e) => {
        setDraft(e.currentTarget.value); setApproval("");
      }} />
      <div className="actions">
        <button disabled={busy || dirty || !policy?.send || !draft.trim()} onClick={() => void run(async () => {
          setApproval(await window.ttd.approve(target, draft)); setNotice("Đã duyệt đúng nội dung và đích trong một phút.");
        })}>Duyệt nội dung</button>
        <button disabled={busy || !approval} onClick={() => void run(async () => {
          await window.ttd.send(approval, target, draft); setApproval("");
          setStatus(await window.ttd.status()); setNotice("Đã ghi nhận một lượt gửi giả lập.");
        })}>Gửi giả lập</button>
      </div>
      <p role="status">{notice}</p>
    </section>
    <p>Nhóm, phát lại và tự động gửi tệp đang tắt.</p>
  </>;
}
createRoot(document.getElementById("root")!).render(<App />);
