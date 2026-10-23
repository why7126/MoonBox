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
        <section class="pg-result">BUG-0024-capture <button>查看成果 · 4 个文件</button></section> <!-- // ds-ok: DOM清理回归夹具，刻意使用原生节点 -->
        <section class="chat-message-history"><p>正常对话里提到查看成果不应被删除</p></section>
      </main>
    `;

    expect(removeLegacyGovernancePanels()).toBe(1);
    expect(document.querySelector(".pg-result")).toBeNull();
    expect(document.querySelector(".chat-message-history")?.textContent).toContain("正常对话");
  });

  it.each(["待应用成果", "查看成果", "审阅治理成果", "确认应用", "执行成果保存在独立副本中"])(
    "普通正文提及%s时保留带标签会话和无关对话框", text => {
      document.body.innerHTML = `
        <main aria-label="工作台">
          <section class="chat-main" aria-label="Chat 工作台">
            <section aria-label="会话内容"><p>${text}</p></section>
            <form aria-label="消息输入"><textarea>草稿 ${text}</textarea></form> <!-- // ds-ok: DOM清理回归夹具，刻意使用原生节点 -->
          </section>
          <dialog open aria-label="会话历史"><p>${text}</p></dialog>
          <div role="dialog" aria-label="重命名会话"><p>${text}</p></div>
        </main>`;
      const nodes = Array.from(document.querySelectorAll("main, section, form, textarea, dialog, [role=dialog]"));
      expect(removeLegacyGovernancePanels()).toBe(0);
      expect(nodes.every(node => node.isConnected)).toBe(true);
      expect(document.querySelector("textarea")?.value).toBe(`草稿 ${text}`);
    },
  );

  it("仅删除明确旧入口并保留父容器，重复清理幂等", () => {
    document.body.innerHTML = `
      <main aria-label="工作台"><section class="chat-main" aria-label="Chat 工作台">
        <section class="pg-result">查看成果</section>
        <section data-testid="governance-result-preview">待应用成果</section>
        <section aria-label="会话内容">后端确认应用后，再进入下一阶段。</section>
      </section></main>
      <dialog open aria-label="审阅治理成果"><button>确认应用</button></dialog> <!-- // ds-ok: DOM清理回归夹具，刻意使用原生节点 -->
      <div role="dialog" aria-label="审阅治理成果"><button>确认应用</button></div>`; // ds-ok: DOM清理回归夹具，刻意使用原生节点
    expect(removeLegacyGovernancePanels()).toBe(4);
    expect(document.querySelector(".chat-main")?.textContent).toContain("后端确认应用后");
    expect(document.querySelector("main")?.isConnected).toBe(true);
    expect(document.querySelectorAll(".pg-result, [data-testid=governance-result-preview], dialog, [role=dialog]")).toHaveLength(0);
    expect(removeLegacyGovernancePanels()).toBe(0);
  });
});
