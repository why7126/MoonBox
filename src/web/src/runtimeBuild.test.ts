import { afterEach, describe, expect, it, vi } from "vitest";
import { ensureCurrentRuntimeBundle, removeLegacyGovernancePanels } from "./runtimeBuild";

afterEach(() => {
  document.head.innerHTML = "";
  document.body.innerHTML = "";
  document.documentElement.removeAttribute("data-moonbox-build-id");
  sessionStorage.clear();
  vi.restoreAllMocks();
});

describe("运行态前端构建防回退", () => {
  it("发现 HTML 已切到新 bundle 时只刷新一次", async () => {
    document.head.innerHTML = '<script type="module" src="/assets/index-old.js"></script>';
    const reload = vi.fn();
    const fetcher = vi.fn(async () => new Response('<script type="module" src="/assets/index-new.js"></script>', { status: 200 }));
    const location = { href: "http://localhost:39002/chat?conversation_id=c", reload };

    await expect(ensureCurrentRuntimeBundle({ location, fetcher, force: true })).resolves.toBe(true);
    expect(fetcher).toHaveBeenCalledWith("http://localhost:39002/chat?conversation_id=c", { cache: "no-store" });
    expect(reload).toHaveBeenCalledTimes(1);

    await expect(ensureCurrentRuntimeBundle({ location, fetcher, force: true })).resolves.toBe(false);
    expect(reload).toHaveBeenCalledTimes(1);
    expect(document.documentElement.dataset.moonboxBuildId).toBeTruthy();
  });

  it("运行 bundle 已匹配当前 HTML 时不刷新", async () => {
    document.head.innerHTML = '<script type="module" src="/assets/index-current.js"></script>';
    const reload = vi.fn();
    const fetcher = vi.fn(async () => new Response('<script type="module" src="/assets/index-current.js"></script>', { status: 200 }));

    await expect(ensureCurrentRuntimeBundle({ location: { href: "http://localhost:39002/chat", reload }, fetcher, force: true })).resolves.toBe(false);
    expect(reload).not.toHaveBeenCalled();
  });

  it("清理历史入口残留的旧治理成果面板", () => {
    document.body.innerHTML = `
      <main class="chat-main">
        <section class="pg-result">BUG-0024-capture <button>查看成果 · 4 个文件</button></section>
        <section class="chat-message-history"><p>正常对话里提到查看成果不应被删除</p></section>
      </main>
    `;

    expect(removeLegacyGovernancePanels()).toBe(1);
    expect(document.querySelector(".pg-result")).toBeNull();
    expect(document.querySelector(".chat-message-history")?.textContent).toContain("正常对话");
  });
});
