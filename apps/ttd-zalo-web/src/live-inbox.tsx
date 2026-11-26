import { useEffect, useRef, useState } from "react";
import { api, ApiError, type OaThread, type OaThreadDetail } from "./api";

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

function Thread({ id, refresh }: { id: string; refresh: number }) {
  const [detail, setDetail] = useState<OaThreadDetail>();
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [sending, setSending] = useState(false);
  const [lockedAfterSend, setLockedAfterSend] = useState(false);
  const [reload, setReload] = useState(0);
  const inFlight = useRef(false);

  useEffect(() => {
    let current = true;
    let pending = false;
    async function load() {
      if (pending) return;
      pending = true;
      try {
        const item = await api.oaThread(id);
        if (current) setDetail(item);
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
      !text.trim()
    )
      return;
    inFlight.current = true;
    setSending(true);
    setError("");
    setNotice("");
    try {
      await api.replyOa(id, text.trim());
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
          <h3>Bản nháp AI</h3>
          {detail.aiDraft ? (
            <p className="callout">{detail.aiDraft.text}</p>
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
                value={text}
                onChange={(event) => setText(event.target.value)}
                rows={4}
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
                !text.trim()
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
