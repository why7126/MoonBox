import { chromium } from "../../../../../src/web/node_modules/@playwright/test/index.mjs";
import fs from "node:fs";

const out = "openspec/changes/add-chat-agent-model-reasoning-selector/evidence/ui";
const api = (data) => ({ code: 0, message: "success", data });
const now = "2026-09-15T00:00:00+08:00";
const conversation = {
  id: "c1",
  space_id: "space",
  repository_id: "repo",
  title: "配置选择验收会话",
  pinned: false,
  archived: false,
  active_turn_id: null,
  created_at: now,
  updated_at: now,
};
const capabilities = {
  execution_ready: true,
  reason: "仓库执行服务已就绪",
  repositories: [{ id: "repo", space_id: "space" }],
  materials: {
    max_images: 5,
    max_image_bytes: 1000000,
    max_total_image_bytes: 5000000,
    allowed_image_mime_types: ["image/png"],
    max_skills: 5,
    max_skill_summary_chars: 1200,
    max_prompt_chars: 32000,
  },
  execution: {
    policy_version: "chat-execution-config-v1",
    agents: [{ value: "codex", display_name: "Codex", available: true }],
    models: [
      { value: "gpt-5.6-sol", display_name: "GPT-5.6 Sol", available: true },
      { value: "gpt-6-astra", display_name: "GPT-6 Astra", available: true },
      { value: "gpt-5.6-terra", display_name: "GPT-5.6 Terra", available: true },
      { value: "gpt-5.6-luna", display_name: "GPT-5.6 Luna", available: true },
      { value: "gpt-5.5", display_name: "GPT-5.5", available: true },
    ],
    reasoning: [
      { value: "high", display_name: "High", available: true },
      { value: "medium", display_name: "Medium", available: true },
      { value: "xhigh", display_name: "XHigh", available: true },
    ],
    defaults: { agent: "codex", model: "gpt-6-astra", reasoning: "high" },
  },
};

async function fulfill(route) {
  const url = new URL(route.request().url());
  const path = url.pathname;
  if (path.endsWith("/spaces")) return route.fulfill({ contentType: "application/json", body: JSON.stringify(api([{ id: "space", name: "验收空间" }])) });
  if (path.endsWith("/capabilities")) return route.fulfill({ contentType: "application/json", body: JSON.stringify(api(capabilities)) });
  if (path.endsWith("/conversations") && route.request().method() === "GET") {
    return route.fulfill({ contentType: "application/json", body: JSON.stringify(api({ items: [conversation], total: 1, page: 1, page_size: 20 })) });
  }
  if (path.endsWith("/conversations/c1") && route.request().method() === "GET") return route.fulfill({ contentType: "application/json", body: JSON.stringify(api(conversation)) });
  if (path.endsWith("/conversations/c1/turns")) {
    return route.fulfill({ contentType: "application/json", body: JSON.stringify(api({ items: [{
      id: "t1", conversation_id: "c1", client_request_id: "r1", status: "queued", retry_of: null, error_code: null, created_at: now, updated_at: now,
      effective_config: { agent: "codex", model: "gpt-6-astra", reasoning: "high" },
    }], page: 1, page_size: 20 })) });
  }
  if (path.endsWith("/conversations/c1/messages")) {
    return route.fulfill({ contentType: "application/json", body: JSON.stringify(api({ items: [{
      id: "m1", turn_id: "t1", role: "user", content: "验证配置选择", created_at: now,
      effective_config: { agent: "codex", model: "gpt-6-astra", reasoning: "high" },
      materials: [],
    }], page: 1, page_size: 20 })) });
  }
  if (path.endsWith("/turns/t1")) {
    return route.fulfill({ contentType: "application/json", body: JSON.stringify(api({
      id: "t1", conversation_id: "c1", client_request_id: "r1", status: "queued", retry_of: null, error_code: null, created_at: now, updated_at: now,
      effective_config: { agent: "codex", model: "gpt-6-astra", reasoning: "high" },
    })) });
  }
  if (path.endsWith("/turns/t1/events")) return route.fulfill({ contentType: "text/event-stream", body: ": no-events\n\n" });
  if (path.endsWith("/turns/t1/diff")) return route.fulfill({ contentType: "application/json", body: JSON.stringify(api({ available: false, reason: "尚无可信差异快照", files: [], cumulative_files: [] })) });
  if (path.endsWith("/turns/t1/context")) return route.fulfill({ contentType: "application/json", body: JSON.stringify(api([])) });
  if (path.endsWith("/behavior-events")) return route.fulfill({ contentType: "application/json", body: JSON.stringify(api({ recorded: true })) });
  return route.fulfill({ contentType: "application/json", body: JSON.stringify(api({})) });
}

const browser = await chromium.launch({ headless: true });
const result = { screenshots: [], computed: {} };

for (const item of [
  { name: "desktop-light", width: 1440, height: 900, scheme: "light" },
  { name: "tablet-dark", width: 1024, height: 768, scheme: "dark" },
  { name: "mobile-light", width: 390, height: 844, scheme: "light" },
]) {
  const context = await browser.newContext({ viewport: { width: item.width, height: item.height }, colorScheme: item.scheme });
  const page = await context.newPage();
  await page.route("**/api/v1/chat/**", fulfill);
  await page.addInitScript(() => localStorage.setItem("moonbox.session", JSON.stringify({
    access_token: "synthetic",
    user: { id: "alice", username: "alice", role: "前台用户" },
  })));
  await page.goto("http://127.0.0.1:4173/chat");
  await page.getByTestId("chat-composer").waitFor({ timeout: 10000 });
  await page.getByTestId("chat-model-selector").click();
  const path = `${out}/${item.name}-model-menu.png`;
  await page.screenshot({ path, fullPage: true });
  result.screenshots.push(path);
  if (item.name === "desktop-light") {
    result.computed = await page.locator("[data-testid=chat-execution-config-bar]").evaluate((el) => {
      const bar = getComputedStyle(el);
      const chip = getComputedStyle(el.querySelector("[data-testid=chat-model-selector]"));
      const menu = getComputedStyle(document.querySelector("[data-testid=chat-execution-config-menu]"));
      return {
        bar: { display: bar.display, gap: bar.gap, flexWrap: bar.flexWrap },
        chip: { minHeight: chip.minHeight, borderRadius: chip.borderRadius, color: chip.color, backgroundColor: chip.backgroundColor, maxWidth: chip.maxWidth },
        menu: { position: menu.position, borderRadius: menu.borderRadius, maxHeight: menu.maxHeight, zIndex: menu.zIndex },
      };
    });
  }
  await context.close();
}

fs.writeFileSync(`${out}/computed-style.json`, JSON.stringify(result, null, 2));
await browser.close();
