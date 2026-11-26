import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  Activity,
  ArrowRight,
  Bot,
  ClipboardList,
  LayoutGrid,
  LogOut,
  Menu,
  MessageSquare,
  Radio,
  RefreshCw,
  ShieldCheck,
  Users,
  Workflow,
  X,
} from "lucide-react";
import {
  api,
  ApiError,
  demoMode,
  roleLabels,
  type Operator,
  type Role,
  type Workspace,
} from "./api";
import {
  Agents,
  Badge,
  Channels,
  ChannelStatus,
  Coordination,
  Customers,
  Inbox,
  Overview,
  Privacy,
  Quotes,
} from "./screens";

const routes = {
  overview: {
    title: "Tổng quan",
    description: "Theo dõi hội thoại, báo giá và các việc cần xử lý.",
    icon: LayoutGrid,
    screen: Overview,
  },
  inbox: {
    title: "Hộp thư khách",
    description: "Xem hội thoại và duyệt nội dung trả lời.",
    icon: MessageSquare,
    screen: Inbox,
  },
  quotes: {
    title: "Báo giá",
    description: "Lập báo giá dựa trên đơn giá và quy cách sản phẩm.",
    icon: ClipboardList,
    screen: Quotes,
  },
  customers: {
    title: "Khách hàng & theo sát",
    description: "Theo dõi khách và yêu cầu dừng liên hệ.",
    icon: Users,
    screen: Customers,
  },
  coordination: {
    title: "Phòng điều phối",
    description: "Giao phiếu việc và theo dõi tiến độ.",
    icon: Workflow,
    screen: Coordination,
  },
  agents: {
    title: "Agent & AI Router",
    description: "Theo dõi agent, mô hình và ngân sách sử dụng.",
    icon: Bot,
    screen: Agents,
  },
  channels: {
    title: "Kênh Zalo",
    description: "Kiểm tra trạng thái kết nối và điều khiển dừng nick phụ.",
    icon: Radio,
    screen: Channels,
  },
  privacy: {
    title: "Dữ liệu & quyền riêng tư",
    description: "Theo dõi consent và gửi yêu cầu xử lý dữ liệu.",
    icon: ShieldCheck,
    screen: Privacy,
  },
};
type Page = keyof typeof routes;
function readRoute(): [Page, string] {
  const [page, selected = ""] = window.location.hash.slice(1).split("/");
  return [Object.hasOwn(routes, page) ? (page as Page) : "overview", selected];
}

function Brand() {
  return (
    <div className="brand">
      <div className="brand-icon">
        <MessageSquare size={22} />
      </div>
      <div>
        <strong>TTD METAL</strong>
        <small>Zalo Assistant</small>
      </div>
    </div>
  );
}

export function Login({
  onLogin,
  busy,
}: {
  onLogin: (input: Parameters<typeof api.login>[0]) => void;
  busy: boolean;
}) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    onLogin(
      demoMode
        ? { demoRole: String(form.get("demoRole")) as Role }
        : {
            account: String(form.get("account")).trim(),
            passphrase: String(form.get("passphrase")),
          },
    );
  }
  return (
    <section className="card login-card">
      <Brand />
      <h1>Đăng nhập</h1>
      <form className="form" onSubmit={submit}>
        {demoMode ? (
          <label>
            Tài khoản giả lập
            <select name="demoRole">
              {Object.entries(roleLabels).map(([id, label]) => (
                <option value={id} key={id}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        ) : (
          <>
            <label>
              Tài khoản
              <input required autoComplete="username" name="account" />
            </label>
            <label>
              Mật khẩu
              <input
                required
                type="password"
                autoComplete="current-password"
                name="passphrase"
              />
            </label>
          </>
        )}
        <button disabled={busy}>
          Đăng nhập <ArrowRight size={16} />
        </button>
      </form>
    </section>
  );
}

const messageOf = (error: unknown) =>
  error instanceof ApiError
    ? error.message
    : "Không thể kết nối dịch vụ. Vui lòng thử lại.";

export default function App() {
  const [[page, selected], setRoute] = useState(readRoute);
  const [menuOpen, setMenuOpen] = useState(false);
  const [user, setUser] = useState<Operator | null>(null);
  const [data, setData] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const locked = useRef(false);

  useEffect(() => {
    function navigate() {
      setRoute(readRoute());
      setMenuOpen(false);
      setNotice("");
      setError("");
    }
    window.addEventListener("hashchange", navigate);
    return () => window.removeEventListener("hashchange", navigate);
  }, []);

  useEffect(() => {
    let active = true;
    async function restore() {
      try {
        const operator = await api.session();
        if (active) setUser(operator);
        const workspace = await api.workspace();
        if (active) setData(workspace);
      } catch (err) {
        if (!active) return;
        if (err instanceof ApiError && err.status === 401) setUser(null);
        else setError(messageOf(err));
      } finally {
        if (active) setLoading(false);
      }
    }
    void restore();
    return () => {
      active = false;
    };
  }, []);

  async function execute(work: () => Promise<void>) {
    if (locked.current) return;
    locked.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await work();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setUser(null);
        setData(null);
      }
      setError(messageOf(err));
    } finally {
      locked.current = false;
      setBusy(false);
    }
  }

  if (loading)
    return (
      <main className="login-layout">
        <p role="status">Đang tải phiên làm việc…</p>
      </main>
    );
  if (!user)
    return (
      <main className="login-layout">
        <Login
          busy={busy}
          onLogin={(input) =>
            void execute(async () => {
              setUser(await api.login(input));
              setData(await api.workspace());
            })
          }
        />
        {error && (
          <p role="alert" className="notice error">
            {error}
          </p>
        )}
      </main>
    );

  const { title, description, screen: Screen } = routes[page];
  return (
    <div className="shell">
      <aside className="sidebar">
        <Brand />
        <button
          className="menu-button"
          aria-label={menuOpen ? "Đóng điều hướng" : "Mở điều hướng"}
          aria-expanded={menuOpen}
          aria-controls="workspace-nav"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <X /> : <Menu />}
        </button>
        <nav
          id="workspace-nav"
          className={menuOpen ? "open" : ""}
          aria-label="Màn hình làm việc"
        >
          {Object.entries(routes).map(([id, item]) => (
            <a
              key={id}
              href={"#" + id}
              onClick={() => setMenuOpen(false)}
              aria-current={page === id ? "page" : undefined}
            >
              <item.icon size={18} />
              {item.title}
            </a>
          ))}
        </nav>
        <div className="sidebar-footer">
          <ShieldCheck size={16} /> Quảng cáo đang tắt
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div className="topbar-label">
            <Activity size={19} />
            <span>Không gian vận hành</span>
            {demoMode && <Badge tone="blue">Giả lập</Badge>}
          </div>
          <div className="user-bar">
            <span className="avatar">
              {roleLabels[user.role].slice(0, 2).toUpperCase()}
            </span>
            <span>{user.label}</span>
            <button
              className="icon-button"
              aria-label="Đăng xuất"
              title="Đăng xuất"
              disabled={busy}
              onClick={() =>
                void execute(async () => {
                  await api.logout();
                  setUser(null);
                  setData(null);
                  window.location.hash = "";
                })
              }
            >
              <LogOut size={18} />
            </button>
          </div>
        </header>
        <main>
          {data && (
            <div className="channel-strip" aria-label="Trạng thái kênh">
              {data.channels.map((channel) => (
                <a key={channel.id} href="#channels">
                  <span>{channel.label}</span>
                  <ChannelStatus channel={channel} />
                </a>
              ))}
            </div>
          )}
          <div className="page-heading">
            <div>
              <h1>{title}</h1>
              <p>{description}</p>
            </div>
            <button
              className="secondary"
              disabled={busy}
              onClick={() =>
                void execute(async () => {
                  setData(await api.workspace());
                  setNotice("Đã tải trạng thái mới nhất.");
                })
              }
            >
              <RefreshCw size={16} /> Làm mới
            </button>
          </div>
          {error && (
            <p role="alert" className="notice error">
              {error}
            </p>
          )}
          {notice && (
            <p role="status" className="notice success">
              {notice}
            </p>
          )}
          {data ? (
            <Screen
              key={page}
              selected={selected}
              data={data}
              user={user}
              busy={busy}
              run={(work, success) =>
                execute(async () => {
                  const update = await work();
                  setData((current) => current && update(current));
                  setNotice(success);
                })
              }
            />
          ) : (
            <p className="muted">
              {busy
                ? "Đang tải dữ liệu…"
                : "Chưa tải được không gian làm việc."}
            </p>
          )}
        </main>
      </div>
    </div>
  );
}
