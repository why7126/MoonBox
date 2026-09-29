const { chromium } = require(process.cwd() + "/node_modules/@playwright/test");
const fs = require("node:fs");

const origin = process.argv[2] || "http://127.0.0.1:18112";
const dir = "../../openspec/changes/add-chat-workbench-image-skill-context/evidence/trace-v3";

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.addInitScript(() => localStorage.setItem("moonbox.session", JSON.stringify({ username: "视觉测试", access_token: "synthetic-test-token" })));
    const row = { id: "synthetic", space_id: "space", repository_id: "sandbox", title: "轨迹 v3 验收", archived: false, pinned: false, active_turn_id: null, created_at: "2026-09-18T09:09:11Z", updated_at: "2026-09-18T09:09:11Z" };
    const turn = { id: "turn", conversation_id: row.id, status: "completed", created_at: row.created_at, effective_config: { agent: "codex", model: "gpt-6-astra", reasoning: "high" } };
    const events = [
      { type: "execution.state", payload: { status: "running" } },
      { type: "execution.output", payload: { text: "我先检查轨迹事件和引用快照。", item_id: "a", executor_turn_id: "turn" } },
      { type: "execution.tool", payload: { item_id: "tool", executor_turn_id: "turn", type: "commandExecution", phase: "started", detail_version: 1, arguments: { command: "printf hello" } } },
      { type: "execution.tool", payload: { item_id: "tool", executor_turn_id: "turn", type: "commandExecution", phase: "completed", detail_version: 1, status: "completed", result: "hello", exit_code: 0, duration_ms: 50, timing_source: "executor" } },
      { type: "execution.usage", payload: { total_tokens: 15319 } },
      { type: "execution.state", payload: { status: "completed" } },
    ].map((event, index) => ({ ...event, sequence: index + 1 }));
    await page.route("**/api/v1/requirement-center/**", route => {
      const url = new URL(route.request().url());
      if (url.pathname.endsWith("/context")) return route.fulfill({ json: { code: 0, data: { currentUser: { name: "视觉测试", avatarInitial: "测", canAccessAdmin: false, permissions: [] }, workspaces: [{ workspaceId: "space", name: "验收空间", role: "成员", memberCount: 1 }], selectedWorkspaceId: "space" } } });
      if (url.pathname.endsWith("/projects")) return route.fulfill({ json: { code: 0, data: { projects: [{ space_id: "space", repository_id: "sandbox", status: "connected", readonly: false }] } } });
      return route.fulfill({ json: { code: 0, data: {} } });
    });
    await page.route("**/api/v1/chat/**", async route => {
      const url = new URL(route.request().url());
      let data;
      if (url.pathname.endsWith("/spaces")) data = [{ id: "space", name: "验收空间" }];
      else if (url.pathname.endsWith("/capabilities")) data = { execution_ready: true, reason: "执行服务已就绪", repositories: [{ id: "sandbox", space_id: "space" }] };
      else if (url.pathname.endsWith("/relations")) data = { primary: null, references: [] };
      else if (url.pathname.endsWith("/governance-candidates")) data = { items: [] };
      else if (url.pathname.endsWith("/events")) {
        const after = Number(url.searchParams.get("after") || 0);
        return route.fulfill({ contentType: "text/event-stream", body: events.filter(event => event.sequence > after).map(event => `id: ${event.sequence}\nevent: ${event.type}\ndata: ${JSON.stringify(event.payload)}\n\n`).join("") });
      } else if (url.pathname.endsWith("/diff")) data = { available: true, files: [{ path: "src/components/UserCard.tsx", status: "modified", before_size: 10, after_size: 12 }], cumulative_files: [] };
      else if (url.pathname.endsWith("/context")) data = [{ object_id: "REQ-0039-test", version: "abcdef123456", title: "待澄清：test 的具体意图", content: "只读引用快照", truncated: false }];
      else if (url.pathname.endsWith("/turns/turn")) data = turn;
      else if (url.pathname.endsWith("/turns")) data = { items: [turn] };
      else if (url.pathname.endsWith("/messages")) data = { items: [{ id: "u", turn_id: "turn", role: "user", content: "检查轨迹", created_at: row.created_at }, { id: "a", turn_id: "turn", role: "assistant", content: "已完成检查。", created_at: row.created_at }] };
      else if (url.pathname.endsWith("/synthetic")) data = row;
      else data = { items: [row], total: 1, page: 1, page_size: 20 };
      return route.fulfill({ json: { code: 0, data } });
    });
    fs.mkdirSync(dir, { recursive: true });
    const results = [];
    for (const [width, height] of [[1440, 900], [390, 844]]) {
      await page.setViewportSize({ width, height });
      await page.goto(`${origin}/tests/trajectory-preview.html`);
      await page.getByRole("tab", { name: "轨迹" }).click();
      await page.locator(".trace-card").waitFor();
      await page.getByTestId("chat-raw-events").locator("summary").click();
      await page.screenshot({ path: `${dir}/trace-v3-${width}.png`, fullPage: true });
      const values = await page.evaluate(() => {
        const sample = selector => {
          const element = document.querySelector(selector);
          if (!element) return null;
          const css = getComputedStyle(element);
          return { display: css.display, gridTemplateColumns: css.gridTemplateColumns, gap: css.gap, padding: css.padding, margin: css.margin, border: css.border, borderRadius: css.borderRadius, backgroundColor: css.backgroundColor, fontSize: css.fontSize, lineHeight: css.lineHeight };
        };
        return {
          traceWrap: sample(".trace-wrap"),
          toolbar: sample(".trace-toolbar"),
          status: sample(".trace-status"),
          card: sample(".trace-card"),
          controls: sample(".trace-controls"),
          search: sample(".trace-search"),
          scrub: sample(".scrub"),
          eventRow: sample(".event-row"),
          raw: sample(".raw-events-box"),
          section: sample(".section-block"),
        };
      });
      if (!values.traceWrap || !values.card || !values.eventRow || !values.raw || !values.section) throw Error(`missing trace v3 selectors at ${width}`);
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw Error(`trace page overflow at ${width}`);
      results.push({ width, height, values });
    }
    if (errors.length) throw Error(errors.join(","));
    fs.writeFileSync(`${dir}/trace-v3-computed.json`, JSON.stringify({ boundary: "synthetic Chat API; production Web bundle and real components", screenshots: 2, results }, null, 2));
    console.log(JSON.stringify({ screenshots: 2, computed: true, eventRows: await page.locator(".event-row").count(), boundary: "synthetic API mocks" }));
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
