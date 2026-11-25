import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import type { Foundation, Target } from "./foundation.js";

import type { FieldKind } from "./customer.js";

type Result<T extends keyof Foundation> = Foundation[T] extends (...args: never[]) => infer R ? Awaited<R> : never;
type Bridge = {
  status(): Promise<Result<"status">>;
  stop(flag: boolean): Promise<Result<"status">>;
  consent(target: Target, retain: boolean, respond: boolean, send: boolean, takeover: boolean): Promise<Result<"status">>;
  approve(target: Target, text: string, origin: string): Promise<string>;
  send(id: string, target: Target, text: string): Promise<Result<"send">>;
  receive(target: Target, text: string): Promise<Result<"receive">>;
  conversation(target: Target): Promise<Result<"conversation">>;
  profile(target: Target): Promise<Result<"profile">>;
  remember(target: Target, source: string, fact: string): Promise<Result<"profile">>;
  invalidate(target: Target): Promise<void>;
  draft(target: Target, origin: string): Promise<Result<"draft">>;
  importDoc(text: string): Promise<string>;
  knowledge(query: string): Promise<Result<"knowledge">>;
  importDocument(name: string, text: string): Promise<string>;
  addSource(json: string): Promise<string>;
  fields(target: Target): Promise<Result<"fields">>;
  saveField(target: Target, source: string, kind: FieldKind, value: string): Promise<void>;
  exportCustomer(target: Target): Promise<boolean>;
  deleteCustomer(target: Target): Promise<void>;
  activity(): Promise<Result<"activity">>;
};
declare global { interface Window { ttd: Bridge } }
const labels = { retain: "Cho phép lưu", respond: "Cho phép soạn phản hồi", send: "Cho phép gửi giả lập",
  takeover: "Nhân viên tiếp quản" };
const fieldLabels: Record<FieldKind, string> = { tag: "Thẻ", stage: "Giai đoạn", need: "Nhu cầu", "follow-up": "Việc theo dõi" };
const screens = ["Hội thoại", "Tin nhắn", "Hồ sơ khách", "Tri thức", "Duyệt và gửi", "Quyền và hoạt động"] as const;
const states: Record<string, string> = {
  "stop": "Đã dừng", "resume": "Đã bỏ dừng", "consent": "Đã đổi quyền", "takeover": "Nhân viên tiếp quản",
  "fake-sent": "Đã gửi giả lập", "inbound-denied": "Từ chối tin đến", "inbound-retained": "Đã lưu tin đến",
  "inbound-ephemeral": "Xử lý tin trong phiên", "memory-saved": "Đã lưu ghi nhớ",
  "knowledge-imported": "Đã nhập tri thức", "send-closed": "Lượt gửi đã đóng",
  "reserved": "Kết quả chưa rõ · không gửi lại", "sent": "Đã gửi giả lập", "closed": "Đã đóng · không gửi lại",
};

function App() {
  const [status, setStatus] = useState<Result<"status">>();
  const [target, setTarget] = useState<Target>("customer-a");
  const [screen, setScreen] = useState(0);
  const [rows, setRows] = useState<Result<"conversation">>([]);
  const [facts, setFacts] = useState<Result<"profile">>([]);
  const [fields, setFields] = useState<Result<"fields">>([]);
  const [fieldKind, setFieldKind] = useState<FieldKind>("need");
  const [fieldSource, setFieldSource] = useState("");
  const [fieldValue, setFieldValue] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [sourceJson, setSourceJson] = useState("");
  const [filename, setFilename] = useState("");
  const [library, setLibrary] = useState<Result<"knowledge">>([]);
  const [activity, setActivity] = useState<Result<"activity">>({ audit: [], attempts: [] });
  const [incoming, setIncoming] = useState("");
  const [origin, setOrigin] = useState("");
  const [inputDoc, setInputDoc] = useState("");
  const [query, setQuery] = useState("");
  const [draft, setDraft] = useState("");
  const [citation, setCitation] = useState<Result<"draft"> | null>(null);
  const [refused, setRefused] = useState(false);
  const [approval, setApproval] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [scopes, setScopes] = useState({ retain: false, respond: false, send: false, takeover: false });
  const [dirty, setDirty] = useState(false);
  const customer = status?.customers.find((row) => row.id === target);
  const displayed = dirty ? scopes : customer?.configured ?? scopes;

  async function refresh(id: Target, q = query) {
    const [s, r, f, k, a, entries] = await Promise.all([
      window.ttd.status(), window.ttd.conversation(id), window.ttd.profile(id),
      window.ttd.knowledge(q), window.ttd.activity(), window.ttd.fields(id),
    ]);
    setFields(entries); setStatus(s); setRows(r); setFacts(f); setLibrary(k); setActivity(a);
  }
  useEffect(() => { void refresh("customer-a", "").catch(() => setNotice("Không đọc được trạng thái.")); }, []);
  function clearDraft() { setOrigin(""); setDraft(""); setRefused(false); setApproval(""); setCitation(null); }
  async function run(action: () => Promise<void>, id = target) {
    setBusy(true); setNotice("");
    try { await action(); }
    catch { setApproval(""); setNotice("Thao tác bị từ chối. Kiểm tra dữ liệu, quyền và trạng thái dừng."); }
    finally {
      try { await refresh(id); }
      catch { setNotice("Không đọc được trạng thái. Thử mở lại ứng dụng."); }
      setBusy(false);
    }
  }
  return <>
    <header><div><h1>TTD Zalo Assistant</h1><p>Ngoại tuyến · Tài khoản và dữ liệu giả lập</p></div>
      {status && <button id="stop" disabled={busy} className="stop" onClick={() => void run(async () => {
        clearDraft(); setStatus(await window.ttd.stop(!status.stopped)); setDirty(false);
      })}>{status.stopped ? "Bỏ dừng giả lập" : "Dừng gửi"}</button>}</header>
    <p aria-live="polite">{status ? (status.stopped ? "Đang dừng" : "Đã bật thử nghiệm") : "Đang tải"}
      {" · "}Kênh giả lập: {status?.connection.state === "offline-ready" ? "Sẵn sàng ngoại tuyến" : "Đang tải"} · Gửi giả lập: {status?.fakeSends ?? 0}{customer ? " · " + customer.thread : ""}</p>
    <nav aria-label="Màn hình">{screens.map((name, i) => <button key={name} disabled={busy} aria-current={screen === i ? "page" : undefined} onClick={() => setScreen(i)}>{name}</button>)}</nav>
    {screen === 0 && <section><h2>Danh sách hội thoại</h2>
      {status?.customers.map((c) => <button key={c.id} className="customer" disabled={busy} onClick={() => {
        setTarget(c.id); setDirty(false); clearDraft(); setIncoming(""); setRows([]); setFacts([]); setFields([]); setFieldSource(""); setFieldValue(""); setConfirmDelete(false); setScreen(1);
        void run(async () => {}, c.id);
      }}>{c.name} · {c.thread}</button>)}
    </section>}
    {screen === 1 && <section><h2>Tin nhắn · {customer?.thread}</h2>
      <label htmlFor="incoming">Nhập tin nhắn của khách mẫu</label>
      <textarea id="incoming" placeholder="Ví dụ: Cho tôi hỏi SKU MAU-01" maxLength={2000} value={incoming} disabled={busy} onChange={e => setIncoming(e.currentTarget.value)} />
      <button disabled={busy || !incoming.trim()} onClick={() => void run(async () => {
        clearDraft();
        const msg = await window.ttd.receive(target, incoming);
        setIncoming("");
        setNotice(msg.state === "denied" ? "Tin bị từ chối." : "Đã nhận tin giả lập.");
        if (msg.canDraft) setOrigin(msg.id);
      })}>Nhận tin giả lập</button>
      <button disabled={busy || !origin} onClick={() => void run(async () => {
        const result = await window.ttd.draft(target, origin);
        setDraft(result.text); setCitation(result); setRefused(result.action === "từ chối"); setApproval(""); setScreen(4);
      })}>Soạn nháp từ tri thức</button>
      <h3>Tin đã lưu</h3>
      {rows.length === 0 && <p>Không có tin được phép hiển thị.</p>}
      <ul>{rows.map(r => <li key={r.id}><time>{new Date(r.received).toLocaleString("vi-VN")}</time> · {r.content} <button disabled={busy} onClick={() => void run(async () => {
        setFacts(await window.ttd.remember(target, r.id, r.content));
        setScreen(2);
      })}>Tạo ghi nhớ</button></li>)}</ul>
    </section>}
    {screen === 2 && <section><h2>Hồ sơ · {customer?.name}</h2><p>Mã khách {target} · {customer?.thread}</p>
      {facts.length === 0 && <p>Chưa có ghi nhớ được phép hiển thị.</p>}
      <ul>{facts.map((f, i) => <li key={i}>{f.fact}<br/><small>Nguồn tin: {f.source}</small></li>)}</ul>
      <h3>Dòng thời gian</h3>
      <ul>{rows.map(row => <li key={row.id}>{new Date(row.received).toLocaleString("vi-VN")} · {row.content}</li>)}</ul>
      <h3>Thẻ, giai đoạn và nhu cầu</h3>
      <ul>{fields.filter(field => field.kind !== "follow-up").map(field =>
        <li key={field.id}>{fieldLabels[field.kind]} · {field.value} <small>Nguồn tin {field.source}</small></li>)}</ul>
      <h3>Việc theo dõi</h3>
      <ul>{fields.filter(field => field.kind === "follow-up").map(field =>
        <li key={field.id}>{field.value} <small>Nguồn tin {field.source}</small></li>)}</ul>
      <fieldset disabled={busy || !customer?.policy.retain || !rows.length}>
        <label>Loại <select value={fieldKind} onChange={e => setFieldKind(e.currentTarget.value as FieldKind)}>
          {Object.entries(fieldLabels).map(([id, label]) => <option key={id} value={id}>{label}</option>)}
        </select></label>
        <label>Tin nhắn nguồn <select value={fieldSource} onChange={e => setFieldSource(e.currentTarget.value)}>
          <option value="">Chọn tin nhắn</option>
          {rows.map(row => <option key={row.id} value={row.id}>{row.content.slice(0, 80)}</option>)}
        </select></label>
        <label>Nội dung <input value={fieldValue} maxLength={250} onChange={e => setFieldValue(e.currentTarget.value)}/></label>
        <button disabled={!fieldSource || !fieldValue.trim()} onClick={() => void run(async () => {
          await window.ttd.saveField(target, fieldSource, fieldKind, fieldValue);
          setFieldValue("");
        })}>Lưu vào hồ sơ</button>
      </fieldset>
      <button disabled={busy || !customer?.policy.retain} onClick={() => void run(async () => {
        if (await window.ttd.exportCustomer(target)) setNotice("Đã xuất hồ sơ khách đang chọn.");
      })}>Xuất hồ sơ</button>
      {confirmDelete ? <div>
        <p>Xóa tin nhắn đã lưu, ghi nhớ và việc theo dõi của {target}, đồng thời thu hồi quyền giả lập?</p>
        <button disabled={busy} onClick={() => void run(async () => {
          await window.ttd.deleteCustomer(target);
          clearDraft(); setFieldSource(""); setFieldValue(""); setConfirmDelete(false); setDirty(false);
          setNotice("Đã xóa hồ sơ khách đang chọn.");
        })}>Xác nhận xóa</button>
        <button disabled={busy} onClick={() => setConfirmDelete(false)}>Hủy</button>
      </div> : <button disabled={busy} onClick={() => setConfirmDelete(true)}>Xóa dữ liệu khách</button>}
    </section>}
    {screen === 3 && <section><h2>Thư viện tri thức</h2>
      <label htmlFor="doc">Tài liệu mẫu TXT hoặc Markdown</label>
      <input type="file" accept=".txt,.md,text/plain,text/markdown" disabled={busy} onChange={e => {
        const file = e.currentTarget.files?.[0];
        if (file) void run(async () => { if (file.size > 48000) throw Error(); setInputDoc(await file.text()); setFilename(file.name); });
      }} />
      <textarea id="doc" maxLength={12000} placeholder={"SKU: MAU-01\nTên: Mẫu lan can A\nThông tin: Thép mạ kẽm"} value={inputDoc} onChange={e => setInputDoc(e.currentTarget.value)} />
      <button disabled={busy || !inputDoc.trim()} onClick={() => void run(async () => {
        const id = filename ? await window.ttd.importDocument(filename, inputDoc) : await window.ttd.importDoc(inputDoc);
        setInputDoc(""); setFilename(""); setApproval(""); setNotice("Đã nhập nguồn " + id);
      })}>Nhập tài liệu</button>
      <details><summary>Thêm bản ghi catalogue có thẩm quyền</summary>
        <p>Dùng JSON gồm id, sku, kind (product, price, policy), title, summary, version, effective, until, origin,
          amount và unit. Ngày theo YYYY-MM-DD. Dùng null cho trường tùy chọn, giá ghi bằng VND.</p>
        <label htmlFor="catalogue-source">Bản ghi catalogue mẫu</label>
        <textarea id="catalogue-source" maxLength={12000} value={sourceJson} onChange={e => setSourceJson(e.currentTarget.value)} />
        <button disabled={busy || !sourceJson.trim()} onClick={() => void run(async () => {
          const id = await window.ttd.addSource(sourceJson);
          setSourceJson(""); clearDraft(); setNotice("Đã lưu bản ghi " + id);
        })}>Thêm bản ghi</button>
      </details>
      <label htmlFor="query">Tìm theo mã hoặc tên</label><input id="query" maxLength={100} value={query} onChange={e => setQuery(e.currentTarget.value)} />
      <button disabled={busy} onClick={() => void run(async () => setLibrary(await window.ttd.knowledge(query)))}>Tìm</button>
      <ul>{library.map(k => <li key={k.id}><strong>{k.id} · {k.title}</strong><br/>{k.summary}<br/><small>{k.origin} · phiên bản {k.version} · từ {k.effective}</small></li>)}</ul>
    </section>}
    {screen === 4 && <section><h2>Duyệt và gửi · {customer?.thread}</h2>
      {citation && <>
        <p>Căn cứ: {citation.confidence === "grounded" ? "Có nguồn phù hợp" : "Cần xác minh"} · {citation.action}</p>
        <p>Nguồn nháp: {citation.sourceIds.join(", ") || "Chưa có nguồn phù hợp"}</p>
        {citation.suggestFollowUp && <button disabled={busy || !customer?.policy.retain || !rows.some(row => row.id === origin)}
          onClick={() => void run(async () => {
            await window.ttd.saveField(target, origin, "follow-up", "Xác minh giá theo đề xuất trong bản nháp");
            setScreen(2);
          })}>Lưu đề xuất theo dõi</button>}
      </>}
      <label htmlFor="draft">Nội dung giả lập</label>
      <textarea id="draft" maxLength={2000} value={draft} disabled={busy || !origin} onChange={(e) => {
        setDraft(e.currentTarget.value); setCitation(null);
        if (approval) void window.ttd.invalidate(target).catch(() => setNotice("Không hủy được duyệt. Hãy dừng gửi."));
        setApproval("");
      }} />
      <div className="actions">
        <button disabled={busy || refused || !origin || dirty || !customer?.policy.send || !draft.trim()} onClick={() => void run(async () => {
          setApproval(await window.ttd.approve(target, draft, origin)); setNotice("Đã duyệt đúng nội dung và đích trong tối đa một phút.");
        })}>Duyệt nội dung</button>
        <button disabled={busy || !approval} onClick={() => void run(async () => {
          await window.ttd.send(approval, target, draft); clearDraft(); setNotice("Đã ghi nhận một lượt gửi giả lập.");
        })}>Gửi giả lập</button>
      </div>
    </section>}
    {screen === 5 && <section><h2>Quyền và hoạt động · {customer?.thread}</h2>
      <fieldset disabled={busy || !status} aria-label="Quyền giả lập">
      {(["retain", "respond", "send", "takeover"] as const).map((key) => <label key={key}>
        <input type="checkbox" checked={displayed[key]} onChange={(e) => {
          setScopes({ ...displayed, [key]: e.currentTarget.checked }); setDirty(true); setApproval("");
        }} />{labels[key]}</label>)}
      </fieldset>
      <button disabled={busy || !dirty} onClick={() => void run(async () => {
        setStatus(await window.ttd.consent(target, scopes.retain, scopes.respond, scopes.send, scopes.takeover));
        setDirty(false); clearDraft(); setNotice("Đã cập nhật quyền giả lập.");
      })}>Lưu quyền thử nghiệm</button>
      <h3>Lịch sử và phục hồi</h3>
      <p>Các lượt chưa rõ kết quả được giữ để đối soát. Ứng dụng không tự gửi lại.</p>
      <ul>{activity.attempts.map(a => <li key={a.id}>{a.target} · {states[a.status] ?? a.status}</li>)}</ul>
      <ul>{activity.audit.map((a, i) => <li key={i}>{new Date(a.at).toLocaleString("vi-VN")} · {states[a.action] ?? a.action}{a.target ? " · " + a.target : ""}</li>)}</ul>
    </section>}
    <p role="status">{notice}</p>
    <p>Nhóm, phát lại và tự động gửi tệp đang tắt.</p>
  </>;
}
createRoot(document.getElementById("root")!).render(<App />);
