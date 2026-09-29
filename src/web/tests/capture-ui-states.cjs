const { chromium } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.CAPTURE_BROWSER_BASE || "http://127.0.0.1:5190";
const apiBase = process.env.CAPTURE_BROWSER_API || "http://127.0.0.1:18101";
const username = process.env.CAPTURE_BROWSER_USER;
const password = process.env.CAPTURE_BROWSER_PASSWORD;
const evidenceDir = path.resolve(__dirname, "../../../openspec/changes/add-capture-multimodal-candidate-review/evidence");

async function api(pathname, options = {}) {
  const response = await fetch(`${apiBase}${pathname}`, { ...options, headers: { "content-type": "application/json", ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`${pathname} ${response.status} ${body.message || ""}`);
  return body.data;
}

function ok(data, status = 200) {
  return { status, contentType: "application/json", body: JSON.stringify({ code: 0, message: "OK", data }) };
}
function fail(message, status = 409, kind = "revision_conflict") {
  return { status, contentType: "application/json", body: JSON.stringify({ code: 2606, message, data: { kind } }) };
}

const candidate = { id: "candidate-1", type: "requirement", title: "统一 MD 编辑器", description: "Capture 弹窗只有一个 MD 编辑器，文本文件进入来源块，图片以内嵌材料卡保留。", priority: "P1", severity: null, source_refs: ["text"], parents: [], classification_reason: "合成 UI 状态回归，不调用正式编号器。", clarifications: [] };

async function openScenario(browser, project, session, name, viewport, behavior) {
  const page = await browser.newPage({ viewport });
  const responses = [];
  await page.route("**/api/v1/requirement-center/**", async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const pathname = url.pathname;
    const method = req.method();
    responses.push({ method, pathname });
    if (pathname.endsWith("/projects") && method === "GET") return route.fulfill(ok({ projects: [{ ...project, status: "connected", readonly: false }] }));
    if (pathname.endsWith("/capture-readiness")) return route.fulfill(ok({ ready: true, reason: "" }));
    if (pathname.endsWith("/capture-capabilities")) return route.fulfill(ok({ limits: { max_images: 10, max_image_bytes: 10485760, max_total_image_bytes: 52428800, max_pixels: 20000000, max_text_codepoints: 20000, max_candidates: 50, max_title_codepoints: 60, max_description_codepoints: 10000, max_drafts: 50, max_material_bytes: 1073741824, image_types: ["image/png", "image/jpeg", "image/webp"] }, organize_ready: true, organize_reason: "", write_ready: true, write_reason: "" }));
    if (pathname.endsWith("/capture-drafts") && method === "GET") return route.fulfill(ok({ items: [], total: 0, page: 1, page_size: 20 }));
    if (pathname.endsWith("/capture-drafts") && method === "POST") return route.fulfill(ok({ id: `draft-${name}`, revision: 1, state: "editing", content: { text: "", media_ids: [], candidates: [] }, updated_at: "2026-09-15T00:00:00Z" }));
    if (pathname.includes("/materials") && method === "POST") return route.fulfill(ok({ media_id: `media-${name}`, mime_type: "image/png", size: 88, width: 20, height: 10, state: "ready", preview_url: `/api/v1/requirement-center/capture-materials/media-${name}/content` }));
    if (pathname.includes("/capture-materials/") && method === "GET") return route.fulfill({ status: 200, contentType: "image/png", body: Buffer.from("iVBORw0KGgoAAAANSUhEUgAAABQAAAAKCAIAAAA7N+mxAAAAF0lEQVR4nGP8//8/A7mAiWydo5pHjGYAM38DEWQYrPYAAAAASUVORK5CYII=", "base64") });
    if (behavior === "conflict" && pathname.includes("/capture-drafts/") && method === "PATCH") return route.fulfill(fail("草稿版本已变化，请刷新后重试", 409, "revision_conflict"));
    if (pathname.includes("/capture-drafts/") && method === "PATCH") return route.fulfill(ok({ id: `draft-${name}`, revision: 2, state: "editing", content: { text: "合成材料", media_ids: [], candidates: behavior === "result" ? [candidate] : [] }, updated_at: "2026-09-15T00:00:01Z" }));
    if (behavior === "failure" && pathname.endsWith("/organize") && method === "POST") return route.fulfill(fail("图文整理服务未就绪，材料已保留，请稍后重试", 503, "organize_unavailable"));
    if (pathname.endsWith("/organize") && method === "POST") return route.fulfill(ok({ id: `organize-${name}`, revision: 2, state: "ready", error_code: null, result: { rules_version: "capture-organize-v1", candidates: [candidate] } }, 202));
    if (pathname.includes("/organize-tasks/")) return route.fulfill(ok({ id: `organize-${name}`, revision: 2, state: "ready", error_code: null, result: { rules_version: "capture-organize-v1", candidates: [candidate] } }));
    if (pathname.endsWith("/confirmations") && method === "POST") return route.fulfill(ok({ id: `task-${name}`, revision: 3, state: "completed", phase: "completed", issue_links: [{ candidate_id: "candidate-1", issue_id: "REQ-0999-synthetic-ui-state" }] }, 202));
    return route.fulfill(ok({}));
  });
  await page.addInitScript(({ session, project }) => {
    localStorage.setItem("moonbox.session", JSON.stringify({ username: session.user?.username || "user", access_token: session.access_token, started_at: new Date().toISOString(), user: session.user }));
    localStorage.setItem("moonbox.workspace", JSON.stringify({ workspaceId: project.space_id }));
  }, { session, project });
  await page.goto(`${base}/requirements?space_id=${encodeURIComponent(project.space_id)}&repository_id=${encodeURIComponent(project.repository_id)}`);
  await page.getByRole("button", { name: "新建 Capture" }).click();
  const dialog = page.getByRole("dialog", { name: "新建 Capture" });
  await dialog.locator("#capture-raw-editor").waitFor({ timeout: 30000 });
  await dialog.locator("#capture-raw-editor").fill(`合成 UI 状态回归：${name}`);
  await page.waitForTimeout(1200);
  if (behavior === "conflict") {
    await dialog.getByRole("alert").waitFor({ timeout: 30000 });
  } else {
    await dialog.getByRole("button", { name: "AI 整理候选" }).click();
  }
  if (behavior === "result") {
    await dialog.getByTestId("capture-review-list").waitFor({ timeout: 30000 });
    await dialog.getByRole("button", { name: "确认创建 1 条" }).click();
    await dialog.getByRole("button", { name: "确认创建", exact: true }).click();
    await dialog.getByTestId("capture-result").first().waitFor({ timeout: 30000 });
  } else if (behavior !== "conflict") {
    await dialog.getByRole("alert").waitFor({ timeout: 30000 });
  }
  const styles = await page.evaluate(() => [".capture-workspace", ".capture-actions", ".capture-alert", ".capture-result"].map((selector) => {
    const element = document.querySelector(selector);
    if (!element) return { selector, missing: true };
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return { selector, width: rect.width, height: rect.height, padding: style.padding, font: style.font, color: style.color, background: style.backgroundColor, overflow: style.overflow };
  }));
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  await page.screenshot({ path: path.join(evidenceDir, `capture-ui-${name}.png`), fullPage: true });
  await page.close();
  return { name, viewport, behavior, overflow, responses, styles };
}

(async () => {
  if (!username || !password) throw new Error("CAPTURE_BROWSER_USER and CAPTURE_BROWSER_PASSWORD are required");
  fs.mkdirSync(evidenceDir, { recursive: true });
  const session = await api("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ username, password, remember_me: false }) });
  const projects = await api("/api/v1/requirement-center/projects", { headers: { authorization: `Bearer ${session.access_token}` } });
  const project = projects.projects.find((item) => !item.readonly);
  if (!project) throw new Error("no writable project for capture ui states");
  project.status = "connected";
  project.readonly = false;
  const browser = await chromium.launch({ headless: true });
  const results = [];
  results.push(await openScenario(browser, project, session, "result-1024", { width: 1024, height: 760 }, "result"));
  results.push(await openScenario(browser, project, session, "failure-390", { width: 390, height: 760 }, "failure"));
  results.push(await openScenario(browser, project, session, "conflict-short", { width: 900, height: 520 }, "conflict"));
  await browser.close();
  if (results.some((item) => item.overflow)) throw new Error("horizontal overflow in synthetic UI state");
  fs.writeFileSync(path.join(evidenceDir, "capture-ui-states.json"), JSON.stringify({ boundary: "synthetic Capture API responses; real app shell; no formal issue creation", results }, null, 2));
  console.log("Capture UI states: result/failure/conflict responsive screenshots passed; synthetic API, no formal issue creation.");
})().catch((error) => { console.error(error.message); process.exit(1); });
