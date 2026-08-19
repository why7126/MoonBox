import playwright from "../../../../../src/web/node_modules/@playwright/test/index.js";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const evidenceDir = path.dirname(new URL(import.meta.url).pathname);
await mkdir(evidenceDir, { recursive: true });

const { chromium } = playwright;
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });

await page.addInitScript(() => {
  window.localStorage.setItem(
    "moonbox.session",
    JSON.stringify({
      username: "frontuser",
      started_at: "2026-08-19T00:00:00.000Z",
      access_token: "front-token",
      expires_at: "2026-08-20 00:00:00",
    }),
  );
});

const fixture = {
  issues: [
    {
      id: "REQ-0021",
      type: "requirement",
      title: "Markdown 编辑器 Vditor 增强",
      priority: "P1",
      owner: "产品团队",
      source: "capture",
      stage: "capture",
      documents: ["capture.md", "trace.md"],
      document_entries: [
        { name: "capture.md", type: "markdown", open_mode: "drawer", label: "capture.md", editable: true, url: "/api/v1/requirement-center/issues/REQ-0021/documents/capture.md" },
        { name: "trace.md", type: "markdown", open_mode: "drawer", label: "trace.md", editable: false, url: "/api/v1/requirement-center/issues/REQ-0021/documents/trace.md" },
      ],
      updated_at: "12:30",
    },
  ],
  workspaces: [
    {
      organization_name: "MoonBox Lab",
      workspace_id: "moonbox-platform",
      name: "Platform Operations",
      slug: "platform-ops",
      description: "需求中心视觉验收",
      timezone: "Asia/Shanghai",
      member_count: 12,
      role: "拥有者",
      status: "ACTIVE",
      readonly: false,
    },
  ],
  current_user: { name: "许同学", avatar_initial: "许", can_access_admin: true, permissions: ["requirement:read"] },
  selected_workspace_id: "moonbox-platform",
  stats: { total: 1, requirements: 1, bugs: 0, blocked: 0, drift: 0 },
};

await page.route("**/api/v1/requirement-center/context**", (route) =>
  route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: fixture }) }),
);
await page.route("**/api/v1/requirement-center/issues/REQ-0021/documents/capture.md", (route) =>
  route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({ data: { content: "# capture.md\n\n需要支持图片上传、表格工具、代码高亮、数学公式。" } }),
  }),
);

await page.goto("http://127.0.0.1:4173/requirements", { waitUntil: "networkidle" });
await page.getByRole("button", { name: /capture.md/ }).click();
await page.getByTestId("markdown-drawer").getByRole("button", { name: "编辑" }).click();
await page.getByRole("button", { name: "插入表格" }).click();
await page.getByRole("button", { name: "插入代码块" }).click();
await page.getByRole("button", { name: "插入数学公式" }).click();
await page.screenshot({ path: path.join(evidenceDir, "01-capture-vditor-editor-1440.png"), fullPage: true });

await page.getByRole("button", { name: "插入图片" }).click();
await page.screenshot({ path: path.join(evidenceDir, "02-image-upload-controlled-failure-1440.png"), fullPage: true });

const computed = await page.evaluate(() => {
  const shell = document.querySelector(".rc-vditor-shell");
  const toolbar = document.querySelector(".rc-vditor-toolbar");
  const workspace = document.querySelector(".rc-vditor-workspace");
  const state = document.querySelector(".rc-vditor-upload-state");
  const rect = shell?.getBoundingClientRect();
  const styles = shell ? getComputedStyle(shell) : null;
  return {
    shellExists: Boolean(shell),
    toolbarButtons: toolbar?.querySelectorAll("button").length ?? 0,
    uploadStateText: state?.textContent ?? "",
    workspaceGridTemplateColumns: workspace ? getComputedStyle(workspace).gridTemplateColumns : "",
    shellRect: rect ? { x: rect.x, y: rect.y, width: rect.width, height: rect.height } : null,
    shellDisplay: styles?.display ?? "",
    bodyScrollWidth: document.body.scrollWidth,
    viewportWidth: window.innerWidth,
  };
});

await writeFile(path.join(evidenceDir, "computed-vditor-editor-1440.json"), JSON.stringify(computed, null, 2));
await browser.close();
console.log(JSON.stringify({ evidenceDir, computed }, null, 2));
