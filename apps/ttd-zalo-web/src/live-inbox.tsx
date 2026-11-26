import { useEffect, useRef, useState } from "react";
import {
  api,
  ApiError,
  type InboxDraft,
  type OaThread,
  type OaThreadDetail,
} from "./api";

const localDate = new Intl.DateTimeFormat("vi-VN", {
  timeZone: "Asia/Ho_Chi_Minh",
  dateStyle: "short",
  timeStyle: "short",
});
function describe(error: unknown) {
  return error instanceof ApiError
    ? error.message
    : "Không thể tải hộp thư OA.";
}

export function LiveInbox({
  selected,
  refresh,
}: {
  selected: string;
  refresh: number;
}) {
  const [threads, setThreads] = useState<OaThread[]>();
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    let pending = false;
    async function load() {
      if (pending) return;
      pending = true;
      try {
        const items = await api.inbox();
        if (active) {
          setThreads(items);
          setError("");
        }
      } catch (err) {
        if (active) setError(describe(err));
      } finally {
        pending = false;
      }
    }
    void load();
    const timer = window.setInterval(() => void load(), 6000);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [refresh]);
  const thread = threads?.find((item) => item.id === selected) ?? threads?.[0];

  return (
    <div className="inbox-grid">
      <section className="card">
        <h2>Hội thoại Zalo OA</h2>
        {error && <p role="alert">{error}</p>}
        {!threads && !error && <p role="status">Đang tải hội thoại…</p>}
        {threads?.length === 0 && (
          <p className="muted">Chưa có hội thoại OA.</p>
        )}
        <div className="rows">
          {threads?.map((item) => (
            <a
              key={item.id}
              className={"row" + (item.id === thread?.id ? " selected" : "")}
              href={"#inbox/" + item.id}
              aria-current={item.id === thread?.id ? "true" : undefined}
            >
              <span>
                Khách {item.customerId}
                <small>
                  {localDate.format(new Date(item.lastInteractionAt))}
                </small>
              </span>
            </a>
          ))}
        </div>
      </section>
      {thread && <Thread key={thread.id} id={thread.id} refresh={refresh} />}
    </div>
  );
}

const intentLabel = {
  price: "Hỏi giá",
  technical: "Kỹ thuật",
  complaint: "Khiếu nại",
  other: "Khác",
};
const draftState = {
  pending: "Đang chờ",
  generating: "Đang soạn nháp",
  ready: "Chờ duyệt",
  needs_human: "Cần người",
  approved: "Đã duyệt",
};
const draftReason = {
  mock: "AI đang chạy giả lập.",
  budget: "Đang chạm giới hạn ngân sách.",
  consent: "Chưa đủ quyền xử lý bằng AI.",
  unavailable: "Chưa nhận được kết quả từ AI.",
  no_knowledge: "Chưa đủ nguồn tri thức đã xác minh.",
};

function DraftPanel({
  draft,
  busy,
  update,
  report,
}: {
  draft: InboxDraft;
  busy: boolean;
  update: (draft: InboxDraft) => void;
  report: (work: () => Promise<void>) => Promise<void>;
}) {
  const [editing, setEditing] = useState(false);
  const [edited, setEdited] = useState(draft.text);
  const ready =
    draft.state === "ready" ||
    (draft.state === "needs_human" && draft.reason === "no_knowledge");
  const open = draft.delivery === "draft";
  const regenerate = draft.state === "ready" || draft.state === "needs_human";
  return (
    <div className="callout">
      <p>
        <strong>{draftState[draft.state]}</strong>
        {draft.intent && " · " + intentLabel[draft.intent]}
      </p>
      {draft.reason && <p className="muted">{draftReason[draft.reason]}</p>}
      {editing ? (
        <label>
          Nội dung nháp
          <textarea
            rows={4}
            maxLength={1500}
            value={edited}
            onChange={(event) => setEdited(event.target.value)}
            disabled={busy}
          />
        </label>
      ) : (
        draft.text && <p className="message-history">{draft.text}</p>
      )}
      {draft.sourceIds.length > 0 && (
        <div>
          Nguồn tri thức
          <ul>
            {draft.sourceIds.map((source) => (
              <li key={source}>{source}</li>
            ))}
          </ul>
        </div>
      )}
      {open && (ready || regenerate) && (
        <div className="pair">
          {ready && (
            <button
              type="button"
              className="secondary"
              disabled={busy}
              onClick={() => {
                setEdited(draft.text);
                setEditing(!editing);
              }}
            >
              {editing ? "Hủy sửa" : "Sửa"}
            </button>
          )}
          {regenerate && (
            <button
              type="button"
              className="secondary"
              disabled={busy}
              onClick={() =>
                void report(async () =>
                  update(await api.regenerateDraft(draft.id, draft.version)),
                )
              }
            >
              Tạo lại
            </button>
          )}
          {ready && (
            <button
              type="button"
              disabled={busy || (editing && !edited.trim())}
              onClick={() =>
                void report(async () => {
                  const approved = await api.approveDraft(
                    draft.id,
                    draft.version,
                    editing ? edited.trim() : undefined,
                  );
                  update({ ...draft, ...approved, state: "approved" });
                })
              }
            >
              Duyệt
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function Thread({ id, refresh }: { id: string; refresh: number }) {
  const [detail, setDetail] = useState<OaThreadDetail>();
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [sending, setSending] = useState(false);
  const [lockedAfterSend, setLockedAfterSend] = useState(false);
  const [reload, setReload] = useState(0);
  const inFlight = useRef(false);
  const draft = detail?.aiDraft;
  const approved =
    draft?.state === "approved" && draft.delivery === "draft"
      ? draft
      : undefined;
  const replyText = approved?.text ?? text;

  function updateDraft(next: InboxDraft) {
    setDetail((previous) => previous && { ...previous, aiDraft: next });
  }

  async function runDraft(work: () => Promise<void>) {
    if (inFlight.current) return;
    inFlight.current = true;
    setSending(true);
    setError("");
    setNotice("");
    try {
      await work();
    } catch (err) {
      setError(describe(err));
    } finally {
      inFlight.current = false;
      setSending(false);
      setReload((value) => value + 1);
    }
  }

  useEffect(() => {
    let current = true;
    let pending = false;
    async function load() {
      if (pending) return;
      pending = true;
      try {
        const item = await api.oaThread(id);
        if (current)
          setDetail((previous) => {
            const known = previous?.aiDraft;
            const incoming = item.aiDraft;
            return known &&
              incoming &&
              known.id === incoming.id &&
              known.version > incoming.version
              ? { ...item, aiDraft: known }
              : item;
          });
      } catch (err) {
        if (current) {
          setDetail(undefined);
          setError(describe(err));
        }
      } finally {
        pending = false;
      }
    }
    void load();
    const timer = window.setInterval(() => void load(), 6000);
    return () => {
      current = false;
      clearInterval(timer);
    };
  }, [id, refresh, reload]);

  async function send() {
    if (
      inFlight.current ||
      !detail ||
      detail.sendBlock ||
      lockedAfterSend ||
      !replyText.trim()
    )
      return;
    inFlight.current = true;
    setSending(true);
    setError("");
    setNotice("");
    try {
      if (approved) {
        const result = await api.approve(
          approved.id,
          approved.version,
          approved.text,
        );
        updateDraft({
          ...approved,
          delivery: result.delivery,
          version: result.version,
        });
        if (result.delivery !== "sent") {
          setLockedAfterSend(result.delivery === "unknown_delivery");
          setError(
            result.delivery === "unknown_delivery"
              ? "Chưa rõ đã giao. Kiểm tra lịch sử trước khi soạn tin mới."
              : "OA chưa tiếp nhận tin trả lời.",
          );
          return;
        }
      } else await api.replyOa(id, text.trim());
      setText("");
      setNotice("OA đã tiếp nhận tin trả lời.");
    } catch (err) {
      // A missing HTTP result can also mean that the provider received the reply.
      if (
        !(err instanceof ApiError) ||
        err.status >= 500 ||
        err.code === "duplicate"
      ) {
        setLockedAfterSend(true);
        setError(
          "Chưa xác nhận được kết quả gửi. Kiểm tra lịch sử trước khi soạn tin mới.",
        );
      } else setError(describe(err));
    } finally {
      inFlight.current = false;
      setSending(false);
      setReload((value) => value + 1);
    }
  }

  return (
    <section className="card">
      <h2>Chi tiết hội thoại</h2>
      {error && <p role="alert">{error}</p>}
      {notice && <p role="status">{notice}</p>}
      {detail && (
        <>
          <p className="muted">
            {detail.following === null
              ? "Chưa có trạng thái quan tâm"
              : detail.following
                ? "Đang quan tâm OA"
                : "Đã bỏ quan tâm OA"}
          </p>
          <ol className="message-history">
            {detail.messages.map((message) => (
              <li key={message.id} className="callout">
                <small>
                  {message.direction === "incoming" ? "Khách" : "Trả lời"} ·{" "}
                  {localDate.format(new Date(message.at))}
                </small>
                <div>{message.text ?? "Nội dung không khả dụng"}</div>
                {message.delivery === "unknown_delivery" && (
                  <small>Chưa rõ đã giao</small>
                )}
                {message.delivery === "failed" && (
                  <small>Gửi không thành công</small>
                )}
              </li>
            ))}
          </ol>
          {detail.estimatedAiUsdToday !== undefined && (
            <p className="muted">
              Chi phí AI soạn nháp hôm nay (ước tính) ·{" "}
              {new Intl.NumberFormat("vi-VN", {
                style: "currency",
                currency: "USD",
                maximumFractionDigits: 6,
              }).format(detail.estimatedAiUsdToday)}
            </p>
          )}
          <h3>Bản nháp AI</h3>
          {draft ? (
            <DraftPanel
              key={draft.id + ":" + draft.version}
              draft={draft}
              busy={sending}
              update={updateDraft}
              report={runDraft}
            />
          ) : (
            <p className="muted">Chưa có bản nháp.</p>
          )}
          <form
            className="form"
            onSubmit={(event) => {
              event.preventDefault();
              void send();
            }}
          >
            <label>
              Nội dung trả lời
              <textarea
                value={replyText}
                onChange={(event) => setText(event.target.value)}
                rows={4}
                readOnly={Boolean(approved)}
                required
                maxLength={1500}
                disabled={
                  Boolean(detail.sendBlock) || sending || lockedAfterSend
                }
              />
            </label>
            {detail.sendBlock && (
              <p id="oa-inbox-send-block" className="muted">
                {detail.sendBlock.message}
              </p>
            )}
            <button
              disabled={
                sending ||
                Boolean(detail.sendBlock) ||
                lockedAfterSend ||
                !replyText.trim()
              }
              aria-describedby={
                detail.sendBlock ? "oa-inbox-send-block" : undefined
              }
            >
              Gửi trả lời OA
            </button>
          </form>
        </>
      )}
    </section>
  );
}
