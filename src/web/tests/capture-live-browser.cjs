const { chromium } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.CAPTURE_BROWSER_BASE || "http://127.0.0.1:5190";
const apiBase = process.env.CAPTURE_BROWSER_API || "http://127.0.0.1:18101";
const username = process.env.CAPTURE_BROWSER_USER;
const password = process.env.CAPTURE_BROWSER_PASSWORD;
const evidenceDir = path.resolve(__dirname, "../../../openspec/changes/add-capture-multimodal-candidate-review/evidence");

const png = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAABQAAAAKCAIAAAA7N+mxAAAAF0lEQVR4nGP8//8/A7mAiWydo5pHjGYAM38DEWQYrPYAAAAASUVORK5CYII=",
  "base64",
);

async function api(pathname, options = {}) {
  const response = await fetch(`${apiBase}${pathname}`, {
    ...options,
    headers: { "content-type": "application/json", ...(options.headers || {}) },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`${pathname} ${response.status} ${body.message || ""}`);
  return body.data;
}

(async () => {
  if (!username || !password) throw new Error("CAPTURE_BROWSER_USER and CAPTURE_BROWSER_PASSWORD are required");
  fs.mkdirSync(evidenceDir, { recursive: true });
  const session = await api("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password, remember_me: false }),
  });
  const projects = await api("/api/v1/requirement-center/projects", {
    headers: { authorization: `Bearer ${session.access_token}` },
  });
  const project = projects.projects.find((item) => item.status === "connected" && !item.readonly);
  if (!project) throw new Error("no writable project for capture browser test");
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  const responses = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("response", async (response) => {
    const url = response.url();
    if (!url.includes("/api/v1/requirement-center/capture")) return;
    const item = { url, status: response.status(), body: "" };
    if (response.status() >= 400) item.body = await response.text().catch(() => "");
    responses.push(item);
  });
  await page.addInitScript(({ session, project }) => {
    localStorage.setItem("moonbox.session", JSON.stringify({
      username: session.user?.username || "req29browser",
      access_token: session.access_token,
      started_at: new Date().toISOString(),
      user: session.user,
    }));
    localStorage.setItem("moonbox.workspace", JSON.stringify({ workspaceId: project.space_id }));
  }, { session, project });

  await page.goto(`${base}/requirements?space_id=${encodeURIComponent(project.space_id)}&repository_id=${encodeURIComponent(project.repository_id)}`);
  await page.getByRole("button", { name: "新建 Capture" }).waitFor({ timeout: 30000 });
  await page.waitForFunction(() => !document.body.textContent?.includes("需求中心暂时无法加载"), null, { timeout: 30000 });
  await page.getByRole("button", { name: "新建 Capture" }).click();
  const dialog = page.getByRole("dialog", { name: "新建 Capture" });
  await dialog.getByText("草稿已保存").waitFor({ timeout: 30000 });
  await page.waitForFunction(() => Boolean(
    document.querySelector("#capture-raw-editor") || document.querySelector('[data-testid="capture-review-list"]')
  ), null, { timeout: 30000 });
  if (await dialog.getByTestId("capture-review-list").isVisible().catch(() => false)) {
    await dialog.getByRole("button", { name: "返回编辑材料" }).click();
  }
  const editor = dialog.locator("#capture-raw-editor");
  await editor.waitFor({ timeout: 30000 });
  await editor.fill("希望 Capture 弹窗只有一个 MD 编辑器，能直接放多张图片和多个文本文件。\n列表刷新后回到顶部像是问题，也请拆成候选。");
  await dialog.getByTestId("capture-file-input").setInputFiles([
    { name: "notes.md", mimeType: "text/markdown", buffer: Buffer.from("补充材料：图片和文本文件都应在同一个编辑器材料流里。") },
    { name: "screen.png", mimeType: "image/png", buffer: png },
  ]);
  await dialog.getByTestId("capture-image-card").first().waitFor({ timeout: 30000 });
  await page.screenshot({ path: path.join(evidenceDir, "capture-live-input-1440.png"), fullPage: true });
  const inputStyles = await page.evaluate(() => [".capture-workspace", ".capture-editor-panel textarea", ".capture-material-chip", ".capture-input-submit"].map((selector) => {
    const element = document.querySelector(selector);
    if (!element) return { selector, missing: true };
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return { selector, width: rect.width, height: rect.height, padding: style.padding, font: style.font, color: style.color, background: style.backgroundColor, overflow: style.overflow };
  }));
  await page.waitForTimeout(1200);
  await dialog.getByRole("button", { name: "AI 整理候选" }).click();
  try {
    await dialog.getByTestId("capture-review-list").waitFor({ timeout: 120000 });
  } catch (error) {
    await page.screenshot({ path: path.join(evidenceDir, "capture-live-failure.png"), fullPage: true }).catch(() => {});
    fs.writeFileSync(path.join(evidenceDir, "capture-live-failure.json"), JSON.stringify({
      message: error.message,
      text: await dialog.textContent().catch(() => ""),
      responses,
      errors,
    }, null, 2));
    throw error;
  }
  await page.screenshot({ path: path.join(evidenceDir, "capture-live-review-1440.png"), fullPage: true });

  const reviewStyles = await page.evaluate(() => [".capture-workspace", ".capture-candidate", ".capture-actions"].map((selector) => {
    const element = document.querySelector(selector);
    if (!element) return { selector, missing: true };
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return { selector, width: rect.width, height: rect.height, padding: style.padding, font: style.font, color: style.color, background: style.backgroundColor, overflow: style.overflow };
  }));
  const styles = { input: inputStyles, review: reviewStyles };
  if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error("horizontal overflow");
  fs.writeFileSync(path.join(evidenceDir, "capture-live-browser.json"), JSON.stringify({ project: { space_id: project.space_id, repository_id: project.repository_id }, errors, responses, styles }, null, 2));
  await browser.close();
  if (errors.length) throw new Error(errors.join("\n"));
  console.log("Capture live browser: input/upload/preview/model review passed; no confirmation created.");
})().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
