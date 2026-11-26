import { oaQuoteBlockLabels, type OaQuoteBlock } from "./oa-quote-policy";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import {
  ArrowRight,
  Check,
  ClipboardList,
  Clock3,
  MessageSquare,
  ShieldCheck,
} from "lucide-react";
import {
  api,
  ApiError,
  can,
  type Action,
  type Channel,
  type Conversation,
  type Operator,
  type Router,
  type Settings as SettingsData,
  type Unit,
  type Workspace,
} from "./api";
import {
  approvedPriceList,
  calculateQuote,
  hasDimensions,
  money,
  number,
  unitLabels,
  validQuoteQuantity,
} from "./quote";

type Props = {
  data: Workspace;
  user: Operator;
  run: (
    work: () => Promise<(current: Workspace) => Workspace>,
    success: string,
  ) => Promise<void>;
  busy: boolean;
  refresh: number;
};

const channelStates = {
  online: "Đang hoạt động",
  offline: "Ngoại tuyến",
  stopped: "Đã dừng",
};
const deliveryLabels = {
  draft: "Chờ duyệt",
  queued: "Trong hàng đợi",
  sent: "Đã gửi",
  blocked: "Bị chặn",
  unknown_delivery: "Chưa rõ đã giao",
};
const optOutLabels = {
  none: "Không có yêu cầu dừng",
  review: "Cần xác minh",
  stop: "Dừng liên hệ",
};
const consentLabels = {
  unknown: "Chưa xác nhận",
  granted: "Đã đồng ý",
  withdrawn: "Đã rút lại",
};
const workLabels = {
  new: "Mới",
  active: "Đang làm",
  review: "Chờ duyệt",
  done: "Xong",
};

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={"badge " + tone}>{children}</span>;
}
export function ChannelStatus({ channel }: { channel: Channel }) {
  return (
    <Badge tone={channel.state}>
      <span className="dot" />
      {channelStates[channel.state]}
    </Badge>
  );
}
function Card({
  title,
  children,
  className = "",
}: {
  title: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={"card " + className}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}
function Can({
  user,
  action,
  children,
}: {
  user: Operator;
  action: Action;
  children: ReactNode;
}) {
  return can(user.role, action) ? (
    children
  ) : (
    <p className="muted">Vai trò hiện tại chỉ có quyền xem mục này.</p>
  );
}

export function Overview({ data }: Props) {
  const drafts = data.conversations.filter(
    ({ delivery }) => delivery === "draft",
  );
  const metrics = [
    {
      label: "Hội thoại",
      value: data.conversations.length,
      icon: MessageSquare,
      href: "#inbox",
      tone: "blue",
    },
    {
      label: "Nháp chờ duyệt",
      value: drafts.length,
      icon: Clock3,
      href: "#inbox",
      tone: "amber",
    },
    {
      label: "Báo giá đã lưu",
      value: data.quotes.length,
      icon: ClipboardList,
      href: "#quotes",
      tone: "purple",
    },
    {
      label: "Kênh hoạt động",
      value: data.channels.filter(({ state }) => state === "online").length,
      icon: ShieldCheck,
      href: "#channels",
      tone: "green",
    },
  ];
  const maximum = Math.max(
    1,
    ...data.activity.flatMap(({ received, answered }) => [received, answered]),
  );
  return (
    <>
      <div className="metrics">
        {metrics.map(({ label, value, icon: Icon, href, tone }) => (
          <a className="card metric" key={label} href={href}>
            <span className={"metric-icon " + tone}>
              <Icon size={20} />
            </span>
            <ArrowRight size={16} className="metric-arrow" />
            <strong>{value}</strong>
            <span>{label}</span>
          </a>
        ))}
      </div>
      <div className="dashboard-grid">
        <Card title="Hoạt động hội thoại">
          <div className="chart-caption">
            <span>7 ngày gần nhất</span>
            <div className="legend">
              <span>Tiếp nhận</span>
              <span>Đã phản hồi</span>
            </div>
          </div>
          <div className="chart">
            {data.activity.map(({ day, received, answered }) => (
              <div
                className="chart-group"
                key={day}
                role="img"
                aria-label={
                  day +
                  ": " +
                  received +
                  " tiếp nhận, " +
                  answered +
                  " đã phản hồi"
                }
              >
                <div
                  className="bars"
                  title={received + " tiếp nhận · " + answered + " đã phản hồi"}
                >
                  <i style={{ height: (received / maximum) * 100 + "%" }} />
                  <i style={{ height: (answered / maximum) * 100 + "%" }} />
                </div>
                <small>{day}</small>
              </div>
            ))}
          </div>
        </Card>
        <Card title="Cần xử lý">
          <div className="rows">
            {drafts.map((item) => (
              <a className="row" key={item.id} href={"#inbox/" + item.id}>
                <div>
                  <strong>{item.subject}</strong>
                  <small>
                    {item.customerId} · {item.time}
                  </small>
                </div>
                <Badge tone="amber">Duyệt nháp</Badge>
              </a>
            ))}
            {data.customers
              .filter((item) => item.optOut === "review")
              .map((item) => (
                <a className="row" key={item.id} href="#customers">
                  <div>
                    <strong>{item.label}</strong>
                    <small>Kiểm tra yêu cầu dừng nhận tin</small>
                  </div>
                  <Badge tone="amber">Xác minh</Badge>
                </a>
              ))}
            {!drafts.length &&
              !data.customers.some((item) => item.optOut === "review") && (
                <p className="muted">Hàng đợi hiện trống.</p>
              )}
          </div>
        </Card>
      </div>
      <Card title="Hội thoại gần đây" className="recent">
        <div className="rows">
          {data.conversations.map((item) => (
            <a key={item.id} href={"#inbox/" + item.id} className="row">
              <span>
                <strong>{item.subject}</strong>
                <small>
                  {item.customerId} · {item.time}
                </small>
              </span>
              <Badge
                tone={
                  item.delivery === "draft" ||
                  item.delivery === "unknown_delivery"
                    ? "amber"
                    : "neutral"
                }
              >
                {deliveryLabels[item.delivery]}
              </Badge>
            </a>
          ))}
        </div>
      </Card>
    </>
  );
}

function Draft({
  item,
  data,
  user,
  run,
  busy,
}: Props & { item: Conversation }) {
  const [text, setText] = useState(item.draft);
  const [confirmed, setConfirmed] = useState(false);
  const customer = data.customers.find(({ id }) => id === item.customerId);
  const channel = data.channels.find(({ id }) => id === item.channel);
  const blocked =
    customer?.optOut !== "none" ||
    customer.consent.support !== "granted" ||
    channel?.state !== "online";
  return (
    <form
      className="form draft"
      onSubmit={(event) => {
        event.preventDefault();
        if (!confirmed || blocked || !text.trim()) return;
        void run(async () => {
          const updated = await api.approve(item.id, item.version, text.trim());
          return (current) => ({
            ...current,
            conversations: current.conversations.map((row) =>
              row.id === updated.id ? updated : row,
            ),
          });
        }, "Đã duyệt nháp và đưa vào hàng đợi.");
      }}
    >
      <label>
        Nháp AI
        <textarea
          required
          maxLength={2000}
          rows={5}
          value={text}
          onChange={(event) => {
            setText(event.target.value);
            setConfirmed(false);
          }}
          readOnly={!can(user.role, "approve")}
        />
      </label>
      <Can user={user} action="approve">
        <label className="checkbox">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(event) => setConfirmed(event.target.checked)}
            disabled={blocked || busy}
          />
          Tôi đã kiểm tra nội dung và người nhận{" "}
          {customer?.label ?? item.customerId}.
        </label>
        {blocked && (
          <p className="muted">
            Chính sách liên hệ hoặc trạng thái kênh đang chặn gửi.
          </p>
        )}
        <button disabled={busy || blocked || !confirmed || !text.trim()}>
          <Check size={16} /> Duyệt và đưa vào hàng đợi
        </button>
      </Can>
    </form>
  );
}

export function Inbox({ selected, ...props }: Props & { selected: string }) {
  const { data } = props;
  const item =
    data.conversations.find(({ id }) => id === selected) ??
    data.conversations[0];
  return (
    <div className="inbox-grid">
      <Card title="Hội thoại">
        <div className="rows">
          {data.conversations.map((row) => (
            <a
              className={"row " + (item?.id === row.id ? "selected" : "")}
              aria-current={item?.id === row.id ? "true" : undefined}
              href={"#inbox/" + row.id}
              key={row.id}
            >
              <div>
                <strong>{row.subject}</strong>
                <small>
                  {
                    data.channels.find((channel) => channel.id === row.channel)
                      ?.label
                  }{" "}
                  · {row.time}
                </small>
              </div>
            </a>
          ))}
        </div>
        {!item && <p className="muted">Chưa có hội thoại.</p>}
      </Card>
      {item && (
        <Card title={item.subject}>
          <div className="conversation-meta">
            <span>
              {item.customerId} ·{" "}
              {data.customers.find(({ id }) => id === item.customerId)?.label}
            </span>
            <Badge>{deliveryLabels[item.delivery]}</Badge>
          </div>
          <blockquote>{item.message}</blockquote>
          {item.delivery === "draft" && (
            <Draft key={item.id + ":" + item.version} {...props} item={item} />
          )}
          {item.delivery === "unknown_delivery" && (
            <p className="callout">
              Chưa xác định tin đã giao. Kiểm tra thủ công trước khi liên hệ
              tiếp.
            </p>
          )}
          {item.reason && <p className="callout">{item.reason}</p>}
          {item.delivery === "queued" && (
            <p className="callout">
              Đang chờ Guard kiểm tra ngay trước khi gửi.
            </p>
          )}
        </Card>
      )}
    </div>
  );
}

function CustomerSelect({ data }: { data: Workspace }) {
  return (
    <label>
      Khách hàng
      <select name="customerId" required defaultValue="">
        <option value="" disabled>
          Chọn khách hàng
        </option>
        {data.customers.map(({ id, label }) => (
          <option key={id} value={id}>
            {label} · {id}
          </option>
        ))}
      </select>
    </label>
  );
}
function fields(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();
  return new FormData(event.currentTarget);
}

export function Quotes({ data, user, run, busy, refresh }: Props) {
  const [productId, setProductId] = useState(data.products[0]?.id ?? "");
  const [unit, setUnit] = useState<Unit>("bar");
  const [quantity, setQuantity] = useState("2");
  const product = data.products.find(({ id }) => id === productId);
  const [customerId, setCustomerId] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const customer = data.customers.find(({ id }) => id === customerId);
  const confirmationKey = JSON.stringify([customerId, product, unit, quantity]);
  const confirmed = confirmation === confirmationKey;
  const dimensionsReady = !!product && hasDimensions(product);
  const priceList = approvedPriceList(product);
  const validQuantity = validQuoteQuantity(unit, Number(quantity));
  const preview =
    product && dimensionsReady && priceList && validQuantity
      ? calculateQuote(product, { unit, quantity: Number(quantity) })
      : undefined;
  const reasons = [
    !customer && "Chọn khách hàng.",
    !dimensionsReady && "Thiếu kích thước hoặc quy cách sản phẩm.",
    !validQuantity && "Nhập số lượng hợp lệ.",
    !priceList && "Giá chưa có trong bảng giá đã duyệt.",
    !confirmed && "Tích xác nhận báo giá.",
  ].filter(Boolean);
  const [sendDenial, setSendDenial] = useState<{
    customerId: string;
    refresh: number;
    code: OaQuoteBlock;
  }>();
  const block =
    sendDenial?.customerId === customerId && sendDenial.refresh === refresh
      ? sendDenial.code
      : customer?.oaQuoteBlock;
  const sendBlocked = !!customer && block !== null;
  const blockLabel = oaQuoteBlockLabels[block ?? "oa_interaction_missing"];

  function submit(send: boolean) {
    if (
      busy ||
      reasons.length ||
      !preview ||
      !priceList ||
      (send && sendBlocked) ||
      !can(user.role, "quote")
    )
      return;
    void run(
      async () => {
        const quote = await (send ? api.sendQuote : api.quote)({
          customerId,
          productId,
          unit,
          quantity: Number(quantity),
          priceList,
          confirmed: true,
        }).catch((error) => {
          if (
            send &&
            error instanceof ApiError &&
            error.code &&
            Object.hasOwn(oaQuoteBlockLabels, error.code)
          ) {
            setSendDenial({
              customerId,
              refresh,
              code: error.code as OaQuoteBlock,
            });
          }
          throw error;
        });
        setConfirmation("");
        // A failed refresh must not turn a successful queue admission into a send error.
        const latest = send
          ? await api.workspace().catch(() => undefined)
          : undefined;
        return (current) => ({
          ...current,
          customers: latest?.customers ?? current.customers,
          quotes: [quote, ...current.quotes],
        });
      },
      send ? "Đã duyệt và xếp hàng gửi qua OA." : "Đã lưu báo giá.",
    );
  }
  return (
    <div className="dashboard-grid">
      <Card title="Lập báo giá">
        <Can user={user} action="quote">
          <form
            className="form"
            onSubmit={(event) => {
              event.preventDefault();
              submit(false);
            }}
          >
            <label>
              Khách hàng
              <select
                required
                value={customerId}
                onChange={(event) => {
                  setCustomerId(event.target.value);
                  setConfirmation("");
                }}
              >
                <option value="">Chọn khách hàng</option>
                {data.customers.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label} · {item.id}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Sản phẩm
              <select
                required
                value={productId}
                onChange={(event) => {
                  setProductId(event.target.value);
                  setConfirmation("");
                }}
              >
                {data.products.map((item) => (
                  <option value={item.id} key={item.id}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
            <div className="pair">
              <label>
                Đơn vị
                <select
                  value={unit}
                  onChange={(event) => {
                    setUnit(event.target.value as Unit);
                    setConfirmation("");
                  }}
                >
                  {Object.entries(unitLabels).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Số lượng
                <input
                  type="number"
                  min={unit === "metre" ? "0.001" : "1"}
                  max="10000"
                  step={unit === "metre" ? "0.001" : "1"}
                  required
                  value={quantity}
                  onChange={(event) => {
                    setQuantity(event.target.value);
                    setConfirmation("");
                  }}
                />
              </label>
            </div>
            {product && dimensionsReady && priceList && (
              <div className="callout">
                <small>
                  {number(product.millimetresPerBar / 1000)} m/thanh ·{" "}
                  {product.barsPerSet} thanh/bộ · {money(product.vndPerMetre)}/m
                  · {priceList}
                </small>
                <div className="quote-total">
                  <span>
                    {preview
                      ? number(preview.totalMillimetres / 1000) + " m quy đổi"
                      : "Số lượng chưa hợp lệ"}
                  </span>
                  <strong>{preview ? money(preview.totalVnd) : "—"}</strong>
                </div>
              </div>
            )}
            <label className="checkbox">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(event) =>
                  setConfirmation(event.target.checked ? confirmationKey : "")
                }
              />
              Tôi đã xác nhận khách hàng, quy cách, số lượng và giá.
            </label>
            {reasons.length > 0 && (
              <ul id="quote-locks" className="muted">
                {reasons.map((reason) => (
                  <li key={String(reason)}>{reason}</li>
                ))}
              </ul>
            )}
            {sendBlocked && (
              <p id="oa-lock" className="muted">
                {blockLabel}
              </p>
            )}
            <div className="pair">
              <button
                className="secondary"
                disabled={busy || !!reasons.length}
                aria-describedby={reasons.length ? "quote-locks" : undefined}
              >
                Lưu báo giá
              </button>
              <button
                type="button"
                disabled={busy || !!reasons.length || sendBlocked}
                aria-describedby={
                  [
                    reasons.length ? "quote-locks" : "",
                    sendBlocked ? "oa-lock" : "",
                  ]
                    .filter(Boolean)
                    .join(" ") || undefined
                }
                onClick={() => submit(true)}
              >
                Duyệt &amp; gửi qua OA
              </button>
            </div>
          </form>
        </Can>
      </Card>
      <Card title="Báo giá đã lưu">
        <div className="rows">
          {data.quotes.map((item) => (
            <div className="row" key={item.id}>
              <div>
                <strong>
                  {item.id} · {item.customerId}
                </strong>
                <small>
                  {item.productId} ·{" "}
                  {item.delivery === "queued" && "Chờ gửi OA · "}
                  {number(item.quantity)} {unitLabels[item.unit].toLowerCase()}{" "}
                  · {number(item.totalMillimetres / 1000)} m
                </small>
              </div>
              <strong>{money(item.totalVnd)}</strong>
            </div>
          ))}
        </div>
        {!data.quotes.length && <p className="muted">Chưa có báo giá.</p>}
      </Card>
    </div>
  );
}

export function Customers({ data }: Props) {
  const [search, setSearch] = useState("");
  const customers = data.customers.filter((item) =>
    (item.id + " " + item.label + " " + item.segment)
      .toLocaleLowerCase("vi")
      .includes(search.trim().toLocaleLowerCase("vi")),
  );
  return (
    <Card title="Danh sách theo sát">
      <input
        type="search"
        aria-label="Tìm khách hàng"
        placeholder="Tìm theo mã khách, tên hoặc nhóm"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
      />
      <div className="rows">
        {customers.map((item) => (
          <div key={item.id} className="row">
            <div>
              <strong>
                {item.label} · {item.id}
              </strong>
              <small>
                {item.segment} · {item.followUp}
              </small>
            </div>
            <Badge
              tone={
                item.optOut === "stop"
                  ? "stopped"
                  : item.optOut === "review"
                    ? "amber"
                    : "neutral"
              }
            >
              {optOutLabels[item.optOut]}
            </Badge>
          </div>
        ))}
      </div>
      {!customers.length && <p className="muted">Không tìm thấy khách hàng.</p>}
    </Card>
  );
}

export function Coordination({ data, user, run, busy }: Props) {
  return (
    <>
      <div className="dashboard-grid">
        <Card title="Trao đổi nội bộ">
          <div className="room-log" role="log" aria-label="Trao đổi nội bộ">
            {data.roomMessages.map((item) => (
              <div key={item.id} className="work-item">
                <strong>{item.author}</strong>
                <p>{item.text}</p>
              </div>
            ))}
            {!data.roomMessages.length && (
              <p className="muted">Chưa có trao đổi.</p>
            )}
          </div>
          <Can user={user} action="task">
            <form
              className="form"
              onSubmit={(event) => {
                const formElement = event.currentTarget;
                const form = fields(event);
                const text = String(form.get("text")).trim();
                if (!text) return;
                void run(async () => {
                  const item = await api.postRoomMessage(text);
                  formElement.reset();
                  return (current) => ({
                    ...current,
                    roomMessages: [...current.roomMessages, item],
                  });
                }, "Đã đăng trao đổi nội bộ.");
              }}
            >
              <label>
                Lời nhắn nội bộ
                <textarea
                  name="text"
                  required
                  maxLength={1000}
                  rows={2}
                  placeholder="@agent và nội dung trao đổi"
                />
              </label>
              <button disabled={busy}>Đăng trao đổi</button>
            </form>
          </Can>
        </Card>
        <Card title="Tạo phiếu việc">
          <Can user={user} action="task">
            <form
              className="form"
              onSubmit={(event) => {
                const form = fields(event);
                const title = String(form.get("title")).trim();
                if (!title) return;
                void run(async () => {
                  const item = await api.task(title, String(form.get("agent")));
                  return (current) => ({
                    ...current,
                    workItems: [item, ...current.workItems],
                  });
                }, "Đã tạo phiếu việc.");
              }}
            >
              <label>
                Nội dung
                <input name="title" required maxLength={250} />
              </label>
              <label>
                Giao cho
                <select name="agent" required>
                  {data.agents.map(({ label }) => (
                    <option key={label} value={label}>
                      @{label}
                    </option>
                  ))}
                </select>
              </label>
              <button disabled={busy || !data.agents.length}>Tạo phiếu</button>
            </form>
          </Can>
        </Card>
      </div>
      <div className="board">
        {Object.entries(workLabels).map(([status, label]) => (
          <Card key={status} title={label}>
            {data.workItems
              .filter((item) => item.status === status)
              .map((item) => (
                <div className="work-item" key={item.id}>
                  <small>{item.id}</small>
                  <strong>{item.title}</strong>
                  <small>@{item.agent}</small>
                </div>
              ))}
            {!data.workItems.some((item) => item.status === status) && (
              <p className="muted">Chưa có phiếu.</p>
            )}
          </Card>
        ))}
      </div>
    </>
  );
}

function useRestrictedData<T>(load: () => Promise<T>, refresh: number) {
  const [result, setResult] = useState<{ data?: T; error?: string }>({});
  useEffect(() => {
    let active = true;
    setResult({});
    void load().then(
      (data) => {
        if (active) setResult({ data });
      },
      (error) => {
        if (active)
          setResult({ error: error.message || "Không tải được dữ liệu." });
      },
    );
    return () => {
      active = false;
    };
  }, [load, refresh]);
  return result;
}

export function Settings({ refresh }: Props) {
  const { data, error } = useRestrictedData<SettingsData>(
    api.settings,
    refresh,
  );
  return (
    <Card title="Chính sách vận hành">
      {error ? (
        <p role="alert">{error}</p>
      ) : data ? (
        <p>Quảng cáo đang tắt trong pilot.</p>
      ) : (
        <p role="status">Đang tải cài đặt…</p>
      )}
    </Card>
  );
}

export function Agents({ data, refresh }: Props) {
  const { data: router, error } = useRestrictedData<Router>(
    api.router,
    refresh,
  );
  return (
    <div className="dashboard-grid">
      <Card title="Đội ngũ agent">
        <div className="rows">
          {data.agents.map((item) => (
            <div className="row" key={item.label}>
              <div>
                <strong>{item.label}</strong>
                <small>{item.role}</small>
              </div>
              <Badge>{item.status}</Badge>
            </div>
          ))}
        </div>
      </Card>
      <Card title="Hostinger AI Router">
        {error ? (
          <p role="alert">{error}</p>
        ) : router ? (
          <>
            <dl>
              <dt>Provider</dt>
              <dd>{router.provider}</dd>
              <dt>Mô hình</dt>
              <dd>{router.model}</dd>
              <dt>Chi phí hôm nay</dt>
              <dd>
                {money(router.usedVnd)} / {money(router.budgetVnd)}
              </dd>
            </dl>
            <progress
              aria-label="Mức sử dụng ngân sách"
              max={router.budgetVnd || 1}
              value={router.usedVnd}
            />
          </>
        ) : (
          <p role="status">Đang tải AI Router…</p>
        )}
      </Card>
    </div>
  );
}

export function Channels({ data, user, run, busy }: Props) {
  const [confirm, setConfirm] = useState(false);
  return (
    <div className="channel-grid">
      {data.channels.map((channel) => (
        <Card key={channel.id} title={channel.label}>
          <ChannelStatus channel={channel} />
          <p className="muted">{channel.detail}</p>
          {channel.id === "nick" && channel.state !== "stopped" && (
            <Can user={user} action="stop">
              {confirm ? (
                <div className="form">
                  <p>Dừng mọi lượt gửi tiếp theo qua nick Zalo phụ?</p>
                  <div className="pair">
                    <button
                      className="danger"
                      disabled={busy}
                      onClick={() =>
                        void run(async () => {
                          const updated = await api.stopNick();
                          setConfirm(false);
                          return (current) => ({
                            ...current,
                            channels: current.channels.map((row) =>
                              row.id === updated.id ? updated : row,
                            ),
                          });
                        }, "Đã bật kill switch nick Zalo phụ.")
                      }
                    >
                      Xác nhận dừng nick
                    </button>
                    <button
                      className="secondary"
                      disabled={busy}
                      onClick={() => setConfirm(false)}
                    >
                      Hủy
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  className="danger"
                  disabled={busy}
                  onClick={() => setConfirm(true)}
                >
                  Bật kill switch
                </button>
              )}
            </Can>
          )}
        </Card>
      ))}
    </div>
  );
}

export function Privacy({ data, user, run, busy }: Props) {
  return (
    <div className="dashboard-grid">
      <Card title="Consent theo mục đích">
        <div className="privacy-list">
          {data.customers.map((item) => (
            <section key={item.id}>
              <h3>
                {item.label} · {item.id}
              </h3>
              <small>{optOutLabels[item.optOut]}</small>
              <dl>
                <dt>Chăm sóc khách</dt>
                <dd>{consentLabels[item.consent.support]}</dd>
                <dt>Báo giá</dt>
                <dd>{consentLabels[item.consent.quote]}</dd>
                <dt>Quảng cáo</dt>
                <dd>{consentLabels[item.consent.marketing]}</dd>
              </dl>
            </section>
          ))}
        </div>
      </Card>
      <Card title="Yêu cầu xóa dữ liệu">
        <Can user={user} action="privacy">
          <form
            className="form"
            onSubmit={(event) => {
              const form = fields(event);
              const reason = String(form.get("reason")).trim();
              if (!reason) return;
              void run(async () => {
                const item = await api.requestDeletion(
                  String(form.get("customerId")),
                  reason,
                );
                return (current) => ({
                  ...current,
                  deletionRequests: [item, ...current.deletionRequests],
                });
              }, "Đã ghi nhận yêu cầu xóa để kiểm tra điều kiện lưu giữ.");
            }}
          >
            <CustomerSelect data={data} />
            <label>
              Lý do
              <textarea name="reason" required maxLength={500} rows={3} />
            </label>
            <button disabled={busy}>Yêu cầu xóa</button>
          </form>
        </Can>
        <div className="rows">
          {data.deletionRequests.map((item) => (
            <div key={item.id} className="row">
              <div>
                <strong>
                  {item.id} · {item.customerId}
                </strong>
                <small>{item.reason}</small>
              </div>
              <Badge>Đã yêu cầu</Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
