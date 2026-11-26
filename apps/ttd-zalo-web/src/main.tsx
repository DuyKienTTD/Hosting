import { createRoot } from "react-dom/client";
import "@fontsource-variable/inter";
import "./styles.css";
import App from "./App";
import { demoMode } from "./api";

const root = createRoot(document.getElementById("root")!);
async function start() {
  if (demoMode) {
    const { worker } = await import("./mocks/browser");
    await worker.start({ onUnhandledRequest: "error", quiet: true });
  }
  root.render(<App />);
}
void start().catch(() =>
  root.render(
    <main>
      <p role="alert">Không khởi động được ứng dụng giả lập.</p>
    </main>,
  ),
);
