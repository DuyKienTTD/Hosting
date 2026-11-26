import type { RunStep } from "./store.js";

export class RunDeadline {
  private readonly controller = new AbortController();
  private readonly until: number;
  private timer?: ReturnType<typeof setTimeout>;
  step: RunStep = "authorization";

  constructor(timeoutMs: number) {
    this.until = performance.now() + timeoutMs;
    this.limit(timeoutMs);
  }

  get signal() { return this.controller.signal; }

  limit(ms: number) {
    clearTimeout(this.timer);
    const remaining = Math.min(ms, this.until - performance.now());
    if (remaining <= 0) this.expire();
    else this.timer = setTimeout(() => this.expire(), Math.ceil(remaining));
  }

  private expire() { this.controller.abort(Error("timeout")); }

  close() { clearTimeout(this.timer); }

  async during<T>(step: RunStep, operation: (signal: AbortSignal) => Promise<T>): Promise<T> {
    this.step = step;
    this.signal.throwIfAborted();
    let abort!: () => void;
    const expired = new Promise<never>((_resolve, reject) => {
      abort = () => reject(this.signal.reason);
      this.signal.addEventListener("abort", abort, { once: true });
    });
    try {
      return await Promise.race([operation(this.signal), expired]);
    } finally {
      this.signal.removeEventListener("abort", abort);
    }
  }
}
